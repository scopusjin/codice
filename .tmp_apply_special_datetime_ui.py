from pathlib import Path

stima_path = Path("Stima_epoca_decesso.py")
stima = stima_path.read_text(encoding="utf-8")

old_datetime = '''                with coly1:
                    measurement_date = i18n.ui_text("full.measurement_date")
                    st.markdown(f"<div style='font-size: 0.88rem; padding-top: 0.4rem;'>{measurement_date}</div>", unsafe_allow_html=True)
                    data_picker = st.date_input(measurement_date, value=input_data_rilievo,
                                                key=f"{nome_parametro_legacy}_data", label_visibility="collapsed")
                with coly2:
                    measurement_time = i18n.ui_text("full.measurement_time")
                    st.markdown(f"<div style='font-size: 0.88rem; padding-top: 0.4rem;'>{measurement_time}</div>", unsafe_allow_html=True)
                    ora_input = st.text_input(i18n.ui_text("full.measurement_time_input"), value=input_ora_rilievo,
                                              key=f"{nome_parametro_legacy}_ora", label_visibility="collapsed")
'''
new_datetime = '''                with coly1:
                    measurement_date = i18n.ui_text("full.measurement_date")
                    st.markdown(f"<div style='font-size: 0.88rem; padding-top: 0.4rem;'>{measurement_date}</div>", unsafe_allow_html=True)
                    data_picker = st.date_input(
                        measurement_date,
                        value=input_data_rilievo,
                        format="DD/MM/YYYY",
                        key=f"{nome_parametro_legacy}_data",
                        label_visibility="collapsed",
                    )
                with coly2:
                    measurement_time = i18n.ui_text("full.measurement_time")
                    st.markdown(f"<div style='font-size: 0.88rem; padding-top: 0.4rem;'>{measurement_time}</div>", unsafe_allow_html=True)
                    ora_key = f"{nome_parametro_legacy}_ora"
                    ora_value = st.session_state.get(ora_key) or input_ora_rilievo or "00:00"
                    ora_input = native_time_picker(
                        ora_value,
                        key=f"{ora_key}_native",
                    )
                    st.session_state[ora_key] = ora_input
'''
if stima.count(old_datetime) != 1:
    raise SystemExit("Special datetime block mismatch")
stima = stima.replace(old_datetime, new_datetime, 1)
stima_path.write_text(stima, encoding="utf-8")

heading_path = Path("app/special_heading_ui.py")
heading = heading_path.read_text(encoding="utf-8")
old_heading = '''            body = (
                "<div style='font-size:0.94rem; font-weight:800; "
                "letter-spacing:0.025em; line-height:1.05; "
                "padding-top:0; padding-bottom:0; "
                "margin-top:0; margin-bottom:-1.45rem;'>"
                f"{html.escape(nome_parametro.upper())}:"
                "</div>"
            )
            kwargs["unsafe_allow_html"] = True
'''
new_heading = '''            body = (
                "<div class='mortem-section-title'>"
                f"{html.escape(nome_parametro)}"
                "</div>"
            )
            kwargs["unsafe_allow_html"] = True
'''
if heading.count(old_heading) != 1:
    raise SystemExit("Special heading block mismatch")
heading = heading.replace(old_heading, new_heading, 1)
heading_path.write_text(heading, encoding="utf-8")

special_dt_path = Path("app/special_datetime_ui.py")
special_dt = special_dt_path.read_text(encoding="utf-8")
old_doc = '''La vecchia conferma "valutato a un'ora diversa" viene resa implicita.
Data e ora restano i widget originali, ma vengono mostrati direttamente
su una sola riga compatta anche su schermi stretti.
'''
new_doc = '''La vecchia conferma "valutato a un'ora diversa" viene resa implicita.
Data e ora vengono mostrati direttamente su una sola riga compatta anche
su schermi stretti; i widget effettivi sono definiti dalla pagina Full.
'''
if special_dt.count(old_doc) != 1:
    raise SystemExit("Special datetime docstring mismatch")
special_dt = special_dt.replace(old_doc, new_doc, 1)

old_css = '''        [class*="st-key-special_datetime_row_"] div[data-baseweb="input"],
        [class*="st-key-special_datetime_row_"] input {
            width: 100% !important;
            min-width: 0 !important;
        }
        </style>
'''
new_css = '''        [class*="st-key-special_datetime_row_"] div[data-baseweb="input"],
        [class*="st-key-special_datetime_row_"] input,
        [class*="st-key-special_datetime_time_"] iframe {
            width: 100% !important;
            min-width: 0 !important;
        }

        [class*="st-key-special_datetime_time_"] iframe {
            display: block !important;
        }
        </style>
'''
if special_dt.count(old_css) != 1:
    raise SystemExit("Special datetime CSS block mismatch")
special_dt = special_dt.replace(old_css, new_css, 1)
special_dt_path.write_text(special_dt, encoding="utf-8")

# Controlli finali mirati
checks = {
    stima_path: [
        'format="DD/MM/YYYY"',
        'key=f"{ora_key}_native"',
        'st.session_state[ora_key] = ora_input',
    ],
    heading_path: [
        "<div class='mortem-section-title'>",
        'html.escape(nome_parametro)',
    ],
    special_dt_path: [
        'st-key-special_datetime_time_']
}
for path, needles in checks.items():
    content = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in content]
    if missing:
        raise SystemExit(f"Missing in {path}: {missing}")

if 'st.text_input(i18n.ui_text("full.measurement_time_input")' in stima:
    raise SystemExit("Legacy special time text_input still present")
