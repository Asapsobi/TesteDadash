"""Build the self-contained report: python3 build.py  ->  ../index.html

Inlines the font and the (already cropped and masked) screenshots as base64,
and expands {{FIG:key}} tokens in template.html into <figure> markup with
highlight marks positioned in percentages of the cropped image.
"""
import base64
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
ASSETS = HERE / "assets"
META = json.loads((ASSETS / "meta.json").read_text())

# key: image, alt, caption, max display height (px or None), marks
# mark: (x0, y0, x1, y1) in ORIGINAL screenshot coordinates, pin label, variant
FIGS = {
    "f03": ("f03_chart", "نمودار یک‌هفته‌ای اتریوم در PDP",
            "نمودار یک‌هفته‌ای PDP اتریوم؛ Tooltip فقط تاریخ و قیمت را نشان می‌دهد.", 360,
            [((880, 722, 1035, 810), "", ""), ((755, 992, 937, 1034), "", "")]),
    "f05": ("f05_chips", "چیپ‌های صفحه بازارها", "چیپ‌های صفحه بازارها", None,
            [((660, 20, 798, 94), "", "")]),
    "f06": ("f06_label", "عنوان قیمت در PDP بیت‌کوین", "عنوان قیمت در PDP", 150,
            [((222, 22, 468, 58), "", "")]),
    "f08": ("f08_sheet", "انتخاب ارز در معامله آسان", "", 300,
            [((522, 618, 756, 656), "۱", ""), ((505, 734, 756, 772), "۲", ""), ((436, 851, 756, 889), "", "")]),
    "f10": ("f10_info", "متن راهنمای شارژ حساب", "متن راهنمای فلوی شارژ حساب", None,
            [((96, 906, 132, 944), "", ""), ((604, 944, 764, 982), "", "")]),
    "f11": ("f11_error", "پیام خطای مرحله تاریخ تولد",
            "مرحله ورود تاریخ تولد در ثبت‌نام (تاریخ واردشده محو شده است)", 230,
            [((524, 462, 600, 504), "", "")]),
    "f12": ("f12_profile", "شماره موبایل در پروفایل",
            "بخش پروفایل (نام و ارقام شماره محو شده‌اند)", 210,
            [((372, 292, 421, 330), "", "")]),
    "f13": ("f13_select", "انتخاب بایننس کوین به‌عنوان ارز پرداخت‌کننده",
            "انتخاب بایننس کوین به‌عنوان ارز پرداخت‌کننده", 280,
            [((14, 908, 840, 1024), "", "")]),
    "f14": ("f14_min", "پیام حداقل مقدار سفارش اتریوم",
            "خرید اتریوم با ۷۱,۰۰۰ تومان", 200,
            [((268, 224, 922, 322), "", ""), ((540, 624, 926, 664), "", "")]),
    "f15": ("f15_invoice", "پیش‌فاکتور خرید سولانا و ماشین‌حساب",
            "صفحه تایید خرید سولانا با ۱,۰۰۰,۰۰۰ تومان، کنار محاسبه همان مقدار", 470,
            [((104, 440, 432, 540), "۱", ""), ((488, 572, 668, 616), "۲", "")]),
    "f16a": ("f16_pdp_head", "هدر صفحه PDP", "", None,
             [((1098, 206, 1146, 258), "", "")]),
    "f16b": ("f16_trade_head", "هدر صفحه معامله آسان", "", None,
             [((836, 22, 920, 100), "", "missing")]),
    "f16c": ("f16_nav", "Navigation Bar", "", None,
             [((765, 1626, 875, 1742), "", "")]),
    "f18": ("f18_card", "پیام خطای افزودن کارت بانکی",
            "افزودن کارت بانکی (ارقام میانی شماره کارت محو شده است)", 190,
            [((590, 330, 926, 370), "", "")]),
    "f23": ("f23_receipt", "رسید شارژ حساب",
            "رسید شارژ حساب؛ از شماره کارت مبدا تنها چهار رقم دیده می‌شود.", 470,
            [((38, 660, 135, 704), "", ""), ((505, 885, 676, 955), "", "")]),
}


def b64(path):
    return base64.b64encode(path.read_bytes()).decode("ascii")


def pct(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") + "%"


def figure(key):
    img, alt, cap, mh, marks = FIGS[key]
    m = META[img]
    spans = []
    for (x0, y0, x1, y1), pin, variant in marks:
        style = (f"left:{pct((x0 - m['x0']) / m['w'] * 100)};top:{pct((y0 - m['y0']) / m['h'] * 100)};"
                 f"width:{pct((x1 - x0) / m['w'] * 100)};height:{pct((y1 - y0) / m['h'] * 100)}")
        cls = "mark" + (f" {variant}" if variant else "")
        spans.append(f'<span class="{cls}" style="{style}">' + (f"<i>{pin}</i>" if pin else "") + "</span>")
    style = f' style="--mh:{mh}px"' if mh else ""
    caption = f"<figcaption>{cap}</figcaption>" if cap else ""
    return (f'<figure class="shot"{style}><div class="shot-frame">'
            f'<img src="data:image/webp;base64,{b64(ASSETS / (img + ".webp"))}" width="{m["w"]}" height="{m["h"]}" alt="{alt}" decoding="async">'
            + "".join(spans) + f"</div>{caption}</figure>")


def main():
    html = (HERE / "template.html").read_text()
    html = re.sub(r"\{\{FIG:(\w+)\}\}", lambda mo: figure(mo.group(1)), html)
    html = html.replace("{{FONT}}", b64(ASSETS / "Vazirmatn-wght.woff2"))
    total = html.count('<section class="slide')
    html = html.replace("{{TOTAL}}", str(total).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")))
    leftover = re.findall(r"\{\{[^}]+\}\}", html)
    if leftover:
        raise SystemExit(f"unresolved tokens: {leftover}")
    out = HERE.parent / "index.html"
    out.write_text(html)
    print(f"{out} — {total} slides, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
