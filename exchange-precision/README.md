# دقت اعشار مقدار دارایی در صرافی‌های ایرانی

موضوع این صفحه **تعداد رقم اعشار مقدار دارایی** است، نه قیمت. دو عدد جدا وجود دارد:

- **دقت سفارش (step):** کوچک‌ترین گامی که می‌شود خرید یا فروخت. مثلاً ETH با ۵ رقم یعنی ۰٫۰۰۰۰۱.
- **دقت موجودی:** تعداد رقمی که کیف پول نگه می‌دارد و نشان می‌دهد. معمولاً بیشتر از دقت سفارش است، چون کارمزد که از خود کوین کم می‌شود ارقام ریزتری می‌سازد.

## آنچه تأیید شد (تا ۲۰ مهر ۱۴۰۵)

سایت‌ها و APIهای صرافی‌های ایرانی از محیط این تحقیق در دسترس نبودند. اعداد زیر از نمونه‌پاسخ‌های واقعی API در کتابخانه‌های متن‌باز آمده‌اند.

| دارایی | نوبیتکس (سفارش) | والکس (سفارش) | منبع دیگر |
|---|---|---|---|
| BTC | **۶** (۰٫۰۰۰۰۰۱) در BTCIRT و BTCUSDT | **۸** در BTCUSDT (بازار تومانی دیده نشد) | — |
| ETH | **۵** (۰٫۰۰۰۰۱) در ETHIRT | **۵** در ETHUSDT | — |
| USDT | **۲** (۰٫۰۱) در USDTIRT | **۲** در USDTTMN | — |
| TON | ؟ | ؟ | رمزینکس: `base_precision = 2` (نمونه‌پاسخ قدیمی‌تر SDK) |
| BNB، SOL | ؟ | ؟ | — |
| XAU (طلا) | به شکل PAXG و XAUT معامله می‌شود (هر توکن یک اونس). خودِ XAU معامله نمی‌شود | XAUT | — |
| XAG، XPT، XPD، XCU، UKOIL | ندارد | ندارد | فقط صرافی راستین درباره این‌ها محتوا منتشر می‌کند؛ دقتشان پیدا نشد |

**دقت موجودی:**
- **نوبیتکس:** موجودی کیف پول را با **۱۰ رقم اعشار** برمی‌گرداند، مثل `"balance": "0.6000000000"`.
- **والکس:** برای همه بازارهای دیده‌شده `baseAssetPrecision = 8` است، یعنی ۸ رقم ذخیره می‌کند. اینکه در اپ ۷ رقم نشان می‌دهد تصمیم رابط کاربری است.
- **بیت‌پین:** در نمونه SDK غیررسمی، `precision = 8` برای BTC.

**نکته مهم:** نوبیتکس سفارشی را که ارقام اضافه دارد رد نمی‌کند. بی‌صدا آن را به گام مجاز کوتاه می‌کند، مثلاً ۰٫۰۰۰۰۴۵۰۴ را به ۰٫۰۰۰۰۴۵.

## گرفتن جدول کامل

از جایی که به صرافی‌های ایرانی دسترسی دارد (مثلاً داخل ایران) اجرا کنید:

```
python3 fetch_precisions.py               # فقط بازارهای تومانی
python3 fetch_precisions.py --all-quotes  # بازارهای تتری هم
python3 fetch_precisions.py --raw out     # ذخیره ردیف‌ها به JSON
```

این اسکریپت فقط از کتابخانه استاندارد پایتون استفاده می‌کند. منابعی که می‌خواند:

| صرافی | آدرس | فیلدی که دقت سفارش را می‌دهد |
|---|---|---|
| نوبیتکس | `apiv2.nobitex.ir/v2/options` | `amountPrecisions` (مقدار گام، مثل "0.00001") |
| والکس | `api.wallex.ir/v1/markets` | `stepSize`، که **تعداد رقم** است و نه گام. `baseAssetPrecision` دقت موجودی است |
| بیت‌پین | `api.bitpin.ir/api/v1/mkt/markets/` | `base_amount_precision` |
| رمزینکس | `publicapi.ramzinex.com/exchange/api/v1.0/exchange/pairs` | `base_precision` |
| تبدیل | `api1.tabdeal.org/r/api/v1/exchangeInfo` | فیلتر `LOT_SIZE.stepSize` |

شکل پاسخ بیت‌پین، رمزینکس و تبدیل از SDKهای غیررسمی برداشته شده و روی API زنده آزمایش نشده است. اگر اسکریپت برای یکی از این‌ها خطا داد، آن صرافی را جدا گزارش می‌کند و بقیه را ادامه می‌دهد.

## منابع

- نوبیتکس: [laminorr/griding – docs/market-precision.md](https://github.com/laminorr/griding/blob/main/docs/market-precision.md) (مقادیر «verified on the host»)، [MehrdadMiri/nobitex-sdk](https://github.com/MehrdadMiri/nobitex-sdk)، [ccxt PR #30603](https://github.com/ccxt/ccxt/pull/30603)
- والکس: فایل نمونه `markets/wallex.json` در [hasanparasteh/ccxt PR #1](https://github.com/hasanparasteh/ccxt/pull/1)، و [ccxt PR #30647](https://github.com/ccxt/ccxt/pull/30647)
- رمزینکس: [ramzinex/php-sdk README](https://github.com/ramzinex/php-sdk)
- بیت‌پین: [amiwrpremium/go-bitpin](https://github.com/amiwrpremium/go-bitpin)
- تبدیل: [darhelm/go-tabdeal](https://github.com/darhelm/go-tabdeal)
- طلا در نوبیتکس: [nobitex.ir/mag/coins/xau](https://nobitex.ir/mag/coins/xau/)
