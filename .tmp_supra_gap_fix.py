from pathlib import Path

path = Path("app/supra_single_grid.py")
text = path.read_text(encoding="utf-8")

old = '''        [class*="st-key-eccitabilita_sopraciliare_grid"] > [data-testid="stVerticalBlock"] {\n            gap: 0 !important;\n        }\n'''
new = '''        [class*="st-key-eccitabilita_sopraciliare_grid"] [data-testid="stVerticalBlock"] {\n            gap: 0 !important;\n            row-gap: 0 !important;\n        }\n\n        @media (max-width: 768px) {\n            [class*="st-key-eccitabilita_sopraciliare_grid"] {\n                position: relative !important;\n                top: -0.80rem !important;\n                margin-bottom: -0.80rem !important;\n            }\n        }\n'''
if text.count(old) != 1:
    raise SystemExit(f"vertical block selector mismatch: {text.count(old)}")
text = text.replace(old, new, 1)

old = '''        [class*="st-key-eccitabilita_sopraciliare_segment_"] {\n            width: 100% !important;\n            margin-top: 0 !important;\n            margin-bottom: -0.18rem !important;\n            padding: 0 !important;\n        }\n'''
new = '''        [class*="st-key-eccitabilita_sopraciliare_segment_"] {\n            width: 100% !important;\n            margin-top: 0 !important;\n            margin-bottom: 0.22rem !important;\n            padding: 0 !important;\n        }\n'''
if text.count(old) != 1:
    raise SystemExit(f"segment spacing mismatch: {text.count(old)}")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")

updated = path.read_text(encoding="utf-8")
checks = [
    '[class*="st-key-eccitabilita_sopraciliare_grid"] [data-testid="stVerticalBlock"]',
    'row-gap: 0 !important;',
    'top: -0.80rem !important;',
    'margin-bottom: 0.22rem !important;',
]
missing = [item for item in checks if item not in updated]
if missing:
    raise SystemExit(f"Missing expected CSS changes: {missing}")
