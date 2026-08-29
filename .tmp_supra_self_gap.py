from pathlib import Path

path = Path("app/supra_single_grid.py")
text = path.read_text(encoding="utf-8")

old = '''        [class*="st-key-eccitabilita_sopraciliare_grid"] [data-testid="stVerticalBlock"] {
            gap: 0 !important;
            row-gap: 0 !important;
        }
'''
new = '''        [class*="st-key-eccitabilita_sopraciliare_grid"][data-testid="stVerticalBlock"],
        [class*="st-key-eccitabilita_sopraciliare_grid"] [data-testid="stVerticalBlock"] {
            gap: 0 !important;
            row-gap: 0 !important;
        }
'''

count = text.count(old)
if count != 1:
    raise SystemExit(f"Expected exactly one target block, found {count}")

text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

updated = path.read_text(encoding="utf-8")
expected = '[class*="st-key-eccitabilita_sopraciliare_grid"][data-testid="stVerticalBlock"],'
if expected not in updated:
    raise SystemExit("Self selector not applied")
