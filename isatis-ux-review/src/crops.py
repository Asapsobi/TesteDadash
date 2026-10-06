"""Crop screenshots, irreversibly blur personal data, export WebP + JSON metadata."""
import json, sys
from pathlib import Path
from PIL import Image, ImageFilter

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

# name: (source, crop box, [blur boxes in source coords])
CROPS = {
    "f03_chart":    ("10.webp", (545, 500, 1150, 1040), []),
    "f05_chips":    ("14.png",  (0, 0, 952, 114), []),
    "f06_label":    ("9.png",   (0, 0, 490, 214), []),
    "f08_sheet":    ("2.jpg",   (0, 330, 863, 905), []),
    "f10_info":     ("4.jpg",   (30, 870, 850, 1020), []),
    "f11_error":    ("5.jpg",   (20, 165, 850, 505), [(650, 388, 822, 446)]),
    "f12_profile":  ("12.png",  (200, 20, 730, 352), [(372, 236, 560, 290), (418, 292, 558, 332)]),
    "f13_select":   ("2.jpg",   (0, 555, 850, 1030), []),
    "f14_min":      ("13.png",  (0, 205, 952, 675), []),
    "f15_invoice":  ("1.jpg",   (0, 0, 1140, 890), []),
    "f16_pdp_head": ("10.webp", (540, 198, 1152, 266), []),
    "f16_trade_head": ("7.png", (0, 0, 946, 112), []),
    "f16_nav":      ("7.png",   (0, 1612, 946, 1748), []),
    "f18_card":     ("6.png",   (0, 0, 952, 390), [(662, 240, 822, 294)]),
    "f23_receipt":  ("3.jpg",   (0, 110, 1280, 1045), []),
}

def blur(im, box):
    region = im.crop(box)
    w, h = region.size
    region = region.resize((max(1, w // 14), max(1, h // 14)), Image.BILINEAR).resize((w, h), Image.BILINEAR)
    region = region.filter(ImageFilter.GaussianBlur(6))
    im.paste(region, box[:2])

meta = {}
for name, (src, box, blurs) in CROPS.items():
    im = Image.open(SRC / src).convert("RGB")
    for b in blurs:
        blur(im, b)
    im = im.crop(box)
    im.save(OUT / f"{name}.webp", "WEBP", quality=90, method=6)
    meta[name] = {"w": im.width, "h": im.height, "x0": box[0], "y0": box[1]}
    print(name, im.size, (OUT / f"{name}.webp").stat().st_size // 1024, "KB")
(OUT / "meta.json").write_text(json.dumps(meta, indent=1))
