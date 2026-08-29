from pathlib import Path

path = Path("app/supra_single_grid.py")
text = path.read_text(encoding="utf-8")

old = '''        [class*="st-key-eccitabilita_sopraciliare_grid"] {
            position: relative !important;
            top: -0.80rem !important;
            margin-bottom: -0.80rem !important;
        }
'''
new = '''        [class*="st-key-eccitabilita_sopraciliare_grid"] {
            position: relative !important;
            top: -0.80rem !important;
            margin-bottom: -0.80rem !important;
        }

        @media (max-width: 768px) {
            [class*="st-key-eccitabilita_sopraciliare_grid"] {
                top: -2.40rem !important;
                margin-bottom: -2.40rem !important;
            }
        }
'''

count = text.count(old)
if count != 1:
    raise SystemExit(f"Expected one desktop grid position block, found {count}")

text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

updated = path.read_text(encoding="utf-8")
for expected in (
    'top: -0.80rem !important;',
    '@media (max-width: 768px)',
    'top: -2.40rem !important;',
    'margin-bottom: -2.40rem !important;',
):
    if expected not in updated:
        raise SystemExit(f"Missing expected CSS: {expected}")
