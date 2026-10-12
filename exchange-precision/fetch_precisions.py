#!/usr/bin/env python3
"""
Fetch quantity precision (decimal places of the asset amount, not the price)
from the public APIs of Iranian exchanges, for the assets in the app list.

Run from a network that can reach Iranian exchanges (e.g. inside Iran):
    python3 fetch_precisions.py            # table to stdout
    python3 fetch_precisions.py --raw out  # also save each raw response to out/

Stdlib only. Each exchange is fetched independently; a failure is reported
and the rest still run.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from decimal import Decimal

# Asset in the app -> symbols it may be listed under on an exchange.
ASSETS = {
    "BTC": ["BTC"],
    "ETH": ["ETH"],
    "USDT": ["USDT"],
    "BNB": ["BNB"],
    "TON": ["TON"],
    "SOL": ["SOL"],
    "XAU": ["XAU", "PAXG", "XAUT", "GOLD"],
    "XAG": ["XAG", "SILVER"],
    "XPT": ["XPT", "PLATINUM"],
    "XPD": ["XPD", "PALLADIUM"],
    "XCU": ["XCU", "COPPER"],
    "UKOIL": ["UKOIL", "BRENT", "OIL"],
}
TOMAN = ("IRT", "TMN", "RLS", "IRR")

UA = "Mozilla/5.0 (precision-research)"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def step_to_decimals(step):
    """'0.00001' -> 5, '1' -> 0, '10' -> 0. None if not a power-of-ten step."""
    try:
        d = Decimal(str(step)).normalize()
    except Exception:
        return None
    if d <= 0:
        return None
    exp = d.as_tuple().exponent
    return max(0, -exp) if d.as_tuple().digits == (1,) else None


def match_asset(base):
    base = (base or "").upper()
    for asset, aliases in ASSETS.items():
        if base in aliases:
            return asset, base
    return None, None


# Each parser yields dicts: market, asset, listed_as, quote, amount_decimals, note
def nobitex():
    data = get_json("https://apiv2.nobitex.ir/v2/options")
    nb = data.get("nobitex", {})
    amounts = nb.get("amountPrecisions", {})
    mins = nb.get("minOrders", {})
    for market, step in amounts.items():
        m = re.match(r"^(.*?)(IRT|USDT)$", market.upper())
        if not m:
            continue
        asset, listed = match_asset(m.group(1))
        if asset:
            quote_key = "rls" if m.group(2) == "IRT" else "usdt"  # minOrders is keyed by quote
            yield dict(market=market, asset=asset, listed_as=listed, quote=m.group(2),
                       amount_decimals=step_to_decimals(step),
                       note=f"step={step} minOrder={mins.get(quote_key, '')}")


def wallex():
    data = get_json("https://api.wallex.ir/v1/markets")
    symbols = data.get("result", {}).get("symbols", {})
    for sym, m in symbols.items():
        asset, listed = match_asset(m.get("baseAsset"))
        if asset:
            # stepSize is a decimal COUNT on Wallex, not a step value.
            yield dict(market=sym, asset=asset, listed_as=listed, quote=m.get("quoteAsset"),
                       amount_decimals=m.get("stepSize"),
                       note=f"baseAssetPrecision={m.get('baseAssetPrecision')} minQty={m.get('minQty')}")


def bitpin():
    data = None
    for url in ("https://api.bitpin.ir/api/v1/mkt/markets/", "https://api.bitpin.market/api/v1/mkt/markets/"):
        try:
            data = get_json(url)
            break
        except Exception:
            continue
    if data is None:
        raise RuntimeError("both Bitpin hosts failed")
    rows = data if isinstance(data, list) else data.get("results", data.get("data", []))
    for m in rows:
        sym = m.get("symbol") or m.get("code") or ""
        base = sym.split("_")[0] if "_" in sym else (m.get("base") or m.get("currency1", {}).get("code"))
        quote = sym.split("_")[1] if "_" in sym else (m.get("quote") or m.get("currency2", {}).get("code"))
        asset, listed = match_asset(base)
        if asset:
            yield dict(market=sym, asset=asset, listed_as=listed, quote=quote,
                       amount_decimals=m.get("base_amount_precision", m.get("amount_precision")),
                       note=f"quote_amount_precision={m.get('quote_amount_precision')}")


def ramzinex():
    data = get_json("https://publicapi.ramzinex.com/exchange/api/v1.0/exchange/pairs")
    rows = data.get("data", [])
    if isinstance(rows, dict):
        rows = rows.get("pairs", list(rows.values()))
    for m in rows:
        base = m.get("base_currency_symbol")
        if isinstance(base, dict):
            base = base.get("en") or base.get("fa")
        base = base or (m.get("url_name") or "").split("-")[-1]
        asset, listed = match_asset(base)
        if asset:
            yield dict(market=f"pair_id={m.get('pair_id')}", asset=asset, listed_as=listed,
                       quote=m.get("quote_currency_id"),
                       amount_decimals=m.get("base_precision"),
                       note=f"amount_step={m.get('amount_step')}")


def tabdeal():
    data = get_json("https://api1.tabdeal.org/r/api/v1/exchangeInfo")
    rows = data if isinstance(data, list) else data.get("symbols", [])
    for m in rows:
        asset, listed = match_asset(m.get("baseAsset"))
        if not asset:
            continue
        lot = next((f for f in m.get("filters", []) if f.get("filterType") == "LOT_SIZE"), {})
        yield dict(market=m.get("symbol"), asset=asset, listed_as=listed, quote=m.get("quoteAsset"),
                   amount_decimals=step_to_decimals(lot.get("stepSize")) if lot else None,
                   note=f"stepSize={lot.get('stepSize')} minQty={lot.get('minQty')} "
                        f"baseAssetPrecision={m.get('baseAssetPrecision')}")


EXCHANGES = {"nobitex": nobitex, "wallex": wallex, "bitpin": bitpin,
             "ramzinex": ramzinex, "tabdeal": tabdeal}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", help="directory to save each exchange's parsed rows as JSON")
    ap.add_argument("--all-quotes", action="store_true", help="include USDT-quoted markets too")
    args = ap.parse_args()

    results = {}
    for name, fn in EXCHANGES.items():
        try:
            rows = list(fn())
            if not args.all_quotes:
                toman = [r for r in rows if str(r["quote"]).upper() in TOMAN or str(r["quote"]) == "2"]
                rows = toman or rows
            results[name] = rows
        except Exception as e:  # keep going on any single failure
            print(f"[{name}] failed: {e}", file=sys.stderr)
            results[name] = []

    print(f"{'asset':6} {'exchange':9} {'market':14} {'listed':6} {'decimals':>8}  note")
    for asset in ASSETS:
        for name, rows in results.items():
            for r in (x for x in rows if x["asset"] == asset):
                print(f"{asset:6} {name:9} {str(r['market']):14} {r['listed_as']:6} "
                      f"{str(r['amount_decimals']):>8}  {r['note']}")

    if args.raw:
        os.makedirs(args.raw, exist_ok=True)
        for name, rows in results.items():
            with open(os.path.join(args.raw, f"{name}.json"), "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
