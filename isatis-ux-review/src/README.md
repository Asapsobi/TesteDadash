# Isatis UX review — sources

`../index.html` is the finished, self-contained report (font and screenshots are embedded).

- `template.html` — report content and styles; `{{FIG:key}}` tokens mark where screenshots go.
- `build.py` — figure definitions (image, caption, highlight boxes) and the build: `python3 build.py`.
- `crops.py` — crops the original screenshots and blurs personal data into `assets/`
  (`python3 crops.py <screenshots-dir> assets`). The original, unmasked screenshots are not stored in the repo.
- `assets/` — masked WebP crops, `meta.json` (crop origins), and the Vazirmatn font (SIL OFL, see `Vazirmatn-OFL.txt`).
