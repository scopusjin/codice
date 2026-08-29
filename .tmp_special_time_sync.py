from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label} anchor mismatch: {count}")
    return text.replace(old, new, 1)


# ------------------------------------------------------------
# Python wrapper del picker: flag inherited + colore dedicato
# ------------------------------------------------------------
path = Path("app/native_time_picker.py")
text = path.read_text(encoding="utf-8")

old = '''def _theme_value(option, fallback):\n    try:\n        value = st.get_option(option)\n    except Exception:\n        value = None\n    return value or fallback\n\n\ndef native_time_picker(value="00:00", *, key=None):\n'''
new = '''def _theme_value(option, fallback):\n    try:\n        value = st.get_option(option)\n    except Exception:\n        value = None\n    return value or fallback\n\n\ndef _inherited_background_color():\n    base = str(_theme_value("theme.base", "light")).lower()\n    return "#3b2a00" if base == "dark" else "#fff3cd"\n\n\ndef native_time_picker(value="00:00", *, key=None, inherited=False):\n'''
text = replace_once(text, old, new, "native helper")

old = '''        background_color=_theme_value("theme.secondaryBackgroundColor", "#F0F2F6"),\n        text_color=_theme_value("theme.textColor", "#31333F"),\n        key=key,\n'''
new = '''        background_color=_theme_value("theme.secondaryBackgroundColor", "#F0F2F6"),\n        text_color=_theme_value("theme.textColor", "#31333F"),\n        inherited=bool(inherited),\n        inherited_background_color=_inherited_background_color(),\n        key=key,\n'''
text = replace_once(text, old, new, "native args")
path.write_text(text, encoding="utf-8")


# ------------------------------------------------------------
# Frontend picker: evidenzia stato ereditato e lo rimuove al commit utente
# ------------------------------------------------------------
path = Path("app/native_time_picker_frontend/main.js")
text = path.read_text(encoding="utf-8")

old = '''const timeInput = document.getElementById("time-input");\nconst pickerToggle = document.getElementById("picker-toggle");\n'''
new = '''const timeInput = document.getElementById("time-input");\nconst timeControl = document.getElementById("time-control");\nconst pickerToggle = document.getElementById("picker-toggle");\n'''
text = replace_once(text, old, new, "js control")

old = '''function setTheme(args) {\n  document.documentElement.style.setProperty("--primary", args.primary_color || "#168AC1");\n  document.documentElement.style.setProperty("--field-bg", args.background_color || "#F0F2F6");\n  document.documentElement.style.setProperty("--text", args.text_color || "#31333F");\n}\n\nfunction parseTime(value) {\n'''
new = '''function setTheme(args) {\n  document.documentElement.style.setProperty("--primary", args.primary_color || "#168AC1");\n  document.documentElement.style.setProperty("--field-bg", args.background_color || "#F0F2F6");\n  document.documentElement.style.setProperty("--text", args.text_color || "#31333F");\n  document.documentElement.style.setProperty("--inherited-bg", args.inherited_background_color || "#fff3cd");\n}\n\nfunction setInheritedState(active) {\n  timeControl.classList.toggle("inherited", Boolean(active));\n}\n\nfunction parseTime(value) {\n'''
text = replace_once(text, old, new, "js theme")

old = '''function commitNormalizedValue(value) {\n  committedValue = value;\n  pendingCommittedValue = value;\n  timeInput.value = value;\n  Streamlit.setComponentValue(value);\n}\n'''
new = '''function commitNormalizedValue(value) {\n  committedValue = value;\n  pendingCommittedValue = value;\n  timeInput.value = value;\n  setInheritedState(false);\n  Streamlit.setComponentValue(value);\n}\n'''
text = replace_once(text, old, new, "js commit")

old = '''function onRender(event) {\n  const args = event.detail.args || {};\n  setTheme(args);\n\n  isMobile = Boolean(args.mobile);\n'''
new = '''function onRender(event) {\n  const args = event.detail.args || {};\n  setTheme(args);\n  setInheritedState(args.inherited);\n\n  isMobile = Boolean(args.mobile);\n'''
text = replace_once(text, old, new, "js render")
path.write_text(text, encoding="utf-8")


# ------------------------------------------------------------
# CSS: giallo soltanto sul campo chiuso, non sul pannello rotella
# ------------------------------------------------------------
path = Path("app/native_time_picker_frontend/style.css")
text = path.read_text(encoding="utf-8")
old = '''.time-control:hover,\n.time-control:focus-within {\n'''
new = '''.time-control.inherited {\n  background: var(--inherited-bg, #fff3cd);\n}\n\n.time-control:hover,\n.time-control:focus-within {\n'''
text = replace_once(text, old, new, "css inherited")
path.write_text(text, encoding="utf-8")


# ------------------------------------------------------------
# Full: sincronizzazione dell'orario aggiuntivo con quello principale
# ------------------------------------------------------------
path = Path("Stima_epoca_decesso.py")
text = path.read_text(encoding="utf-8")

old = '''            if usa_orario_custom_globale and usa_orario_personalizzato:\n                coly1, coly2 = st.columns(2)\n'''
new = '''            ora_key = f"{nome_parametro_legacy}_ora"\n            ora_manual_key = f"{ora_key}__manual"\n            ora_last_main_key = f"{ora_key}__last_main"\n            if not usa_orario_personalizzato:\n                st.session_state.pop(ora_manual_key, None)\n                st.session_state.pop(ora_last_main_key, None)\n\n            if usa_orario_custom_globale and usa_orario_personalizzato:\n                coly1, coly2 = st.columns(2)\n'''
text = replace_once(text, old, new, "stima state keys")

old = '''                    ora_key = f"{nome_parametro_legacy}_ora"\n                    ora_value = st.session_state.get(ora_key) or input_ora_rilievo or "00:00"\n                    ora_input = native_time_picker(\n                        ora_value,\n                        key=f"{ora_key}_native",\n                    )\n                    st.session_state[ora_key] = ora_input\n'''
new = '''                    ora_main = input_ora_rilievo or "00:00"\n                    ora_manual = bool(st.session_state.get(ora_manual_key, False))\n                    ora_value = (\n                        (st.session_state.get(ora_key) or ora_main)\n                        if ora_manual\n                        else ora_main\n                    )\n                    ora_picker = native_time_picker(\n                        ora_value,\n                        key=f"{ora_key}_native",\n                        inherited=not ora_manual,\n                    )\n\n                    if ora_manual:\n                        ora_input = ora_picker\n                    else:\n                        ora_last_main = st.session_state.get(ora_last_main_key)\n                        if ora_last_main is None:\n                            # Primo render (o riattivazione): ignora un eventuale\n                            # valore residuo del componente e parti dall'orario principale.\n                            ora_input = ora_main\n                        elif ora_main != ora_last_main and ora_picker == ora_last_main:\n                            # Dopo un cambio programmatico del principale il componente\n                            # può restituire per un singolo rerun il vecchio valore.\n                            ora_input = ora_main\n                        elif ora_picker != ora_main:\n                            # Da questo momento il valore è stato modificato localmente\n                            # e non deve più seguire l'orario principale.\n                            st.session_state[ora_manual_key] = True\n                            ora_input = ora_picker\n                        else:\n                            ora_input = ora_main\n                        st.session_state[ora_last_main_key] = ora_main\n\n                    st.session_state[ora_key] = ora_input\n'''
text = replace_once(text, old, new, "stima picker sync")
path.write_text(text, encoding="utf-8")


# Verifiche minime sugli output
checks = {
    "app/native_time_picker.py": [
        'def native_time_picker(value="00:00", *, key=None, inherited=False):',
        "inherited=bool(inherited)",
    ],
    "app/native_time_picker_frontend/main.js": [
        'const timeControl = document.getElementById("time-control");',
        "setInheritedState(args.inherited);",
        "setInheritedState(false);",
    ],
    "app/native_time_picker_frontend/style.css": [
        ".time-control.inherited",
    ],
    "Stima_epoca_decesso.py": [
        'ora_manual_key = f"{ora_key}__manual"',
        "inherited=not ora_manual",
        "ora_last_main is None",
    ],
}
for filename, required in checks.items():
    current = Path(filename).read_text(encoding="utf-8")
    missing = [item for item in required if item not in current]
    if missing:
        raise SystemExit(f"{filename}: missing {missing}")
