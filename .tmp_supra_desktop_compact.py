from pathlib import Path

supra_path = Path("app/supra_single_grid.py")
supra = supra_path.read_text(encoding="utf-8")
old = '''        @media (max-width: 768px) {\n            [class*=\"st-key-eccitabilita_sopraciliare_grid\"] {\n                position: relative !important;\n                top: -0.80rem !important;\n                margin-bottom: -0.80rem !important;\n            }\n        }\n'''
new = '''        [class*=\"st-key-eccitabilita_sopraciliare_grid\"] {\n            position: relative !important;\n            top: -0.80rem !important;\n            margin-bottom: -0.80rem !important;\n        }\n'''
if supra.count(old) != 1:
    raise SystemExit(f"supra media rule mismatch: {supra.count(old)}")
supra = supra.replace(old, new, 1)
supra_path.write_text(supra, encoding="utf-8")

heading_path = Path("app/special_heading_ui.py")
heading = heading_path.read_text(encoding="utf-8")
anchor = '''          body:has([class*=\"st-key-mostra_parametri_aggiuntivi\"])\n          [data-testid=\"stVerticalBlockBorderWrapper\"]:has([class*=\"st-key-electrical_pair_layout\"])\n          [data-testid=\"stElementContainer\"]:has(.mortem-section-title--supra) {\n            margin-bottom: -1.18rem !important;\n          }\n'''
if heading.count(anchor) != 1:
    raise SystemExit(f"heading supra rule mismatch: {heading.count(anchor)}")
# La stessa regola deve valere anche fuori dal media query per desktop.
insert = '''\n        body:has([class*=\"st-key-mostra_parametri_aggiuntivi\"])\n        [data-testid=\"stVerticalBlockBorderWrapper\"]:has([class*=\"st-key-electrical_pair_layout\"])\n        [data-testid=\"stElementContainer\"]:has(.mortem-section-title--supra) {\n          margin-bottom: -1.18rem !important;\n        }\n'''
marker = '''        </style>\n'''
if heading.count(marker) != 1:
    raise SystemExit(f"style marker mismatch: {heading.count(marker)}")
heading = heading.replace(marker, insert + marker, 1)
heading_path.write_text(heading, encoding="utf-8")

# Verifiche mirate.
updated_supra = supra_path.read_text(encoding="utf-8")
if '@media (max-width: 768px) {\n            [class*=\"st-key-eccitabilita_sopraciliare_grid\"]' in updated_supra:
    raise SystemExit("mobile-only supra position rule still present")
if updated_supra.count('top: -0.80rem !important;') != 1:
    raise SystemExit("unexpected supra top rule count")
updated_heading = heading_path.read_text(encoding="utf-8")
if updated_heading.count('margin-bottom: -1.18rem !important;') != 2:
    raise SystemExit("desktop heading rule not added exactly once")
