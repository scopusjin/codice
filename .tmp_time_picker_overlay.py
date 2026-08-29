from pathlib import Path

path = Path("app/native_time_picker.py")
text = path.read_text(encoding="utf-8")

old = '''_TIME_RE = re.compile(r"^(?:[01]\\d|2[0-3]):[0-5]\\d$")\n\n\ndef _theme_value(option, fallback):\n'''
new = '''_TIME_RE = re.compile(r"^(?:[01]\\d|2[0-3]):[0-5]\\d$")\n\n\ndef _install_mobile_overlay_css():\n    """Fa aprire la rotella sopra il layout senza rialzare la riga Streamlit."""\n    if getattr(st, "_native_time_picker_overlay_css_installed", False):\n        return\n\n    st.markdown(\n        """\n        <style>\n        @media (max-width: 768px) {\n          [data-testid="stElementContainer"]:has(iframe[title*="mortem_native_time_picker"]),\n          [data-testid="stCustomComponentV1"]:has(iframe[title*="mortem_native_time_picker"]) {\n            position: relative !important;\n            height: 40px !important;\n            min-height: 40px !important;\n            overflow: visible !important;\n            z-index: 50 !important;\n          }\n\n          [data-testid="stColumn"]:has(iframe[title*="mortem_native_time_picker"]) {\n            overflow: visible !important;\n            position: relative !important;\n            z-index: 50 !important;\n          }\n\n          iframe[title*="mortem_native_time_picker"] {\n            position: absolute !important;\n            top: 0 !important;\n            left: 0 !important;\n            z-index: 1000 !important;\n          }\n        }\n        </style>\n        """,\n        unsafe_allow_html=True,\n    )\n    st._native_time_picker_overlay_css_installed = True\n\n\ndef _theme_value(option, fallback):\n'''

if text.count(old) != 1:
    raise SystemExit(f"Anchor 1 mismatch: {text.count(old)}")
text = text.replace(old, new, 1)

old2 = '''def native_time_picker(value="00:00", *, key=None):\n    """Restituisce un orario HH:MM; ruote touch solo sulla Full mobile."""\n    if not isinstance(value, str) or not _TIME_RE.fullmatch(value.strip()):\n'''
new2 = '''def native_time_picker(value="00:00", *, key=None):\n    """Restituisce un orario HH:MM; ruote touch solo sulla Full mobile."""\n    _install_mobile_overlay_css()\n\n    if not isinstance(value, str) or not _TIME_RE.fullmatch(value.strip()):\n'''

if text.count(old2) != 1:
    raise SystemExit(f"Anchor 2 mismatch: {text.count(old2)}")
text = text.replace(old2, new2, 1)

path.write_text(text, encoding="utf-8")

updated = path.read_text(encoding="utf-8")
checks = [
    "def _install_mobile_overlay_css():",
    'iframe[title*="mortem_native_time_picker"]',
    "height: 40px !important;",
    "position: absolute !important;",
    "_install_mobile_overlay_css()",
]
missing = [item for item in checks if item not in updated]
if missing:
    raise SystemExit(f"Missing expected changes: {missing}")
