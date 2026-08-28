from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected 1 occurrence, found {count}"
    return text.replace(old, new, 1)


def replace_between(text, start, end, new_body, label):
    i = text.find(start)
    assert i >= 0, f"{label}: start marker not found"
    j = text.find(end, i + len(start))
    assert j >= 0, f"{label}: end marker not found"
    return text[:i] + new_body + text[j:]


# 1) V2 usato dalla Full sia mobile sia desktop.
p = Path("app/decimal_number_input.py")
text = p.read_text(encoding="utf-8")
text = replace_once(
    text,
    "from app.device_mode import full_device_is_mobile\n",
    "",
    "decimal import device mode",
)
text = replace_once(
    text,
    '''    # ``compact_mobile`` indica che il chiamante supporta la resa compatta\n    # della schermata Full. La scelta effettiva mobile/desktop viene risolta\n    # una sola volta per sessione sul server, prima di inviare il componente.\n    compact_mobile = bool(compact_mobile and full_device_is_mobile())\n''',
    '''    # ``compact_mobile`` è il flag storico della resa compatta della Full.\n    # La stessa UI V2 viene ora usata sia su mobile sia su desktop; la MSIL non\n    # passa questo flag per le proprie chiavi e conserva quindi il renderer V1.\n    compact_mobile = bool(compact_mobile)\n''',
    "decimal full V2 gate",
)
p.write_text(text, encoding="utf-8")


# 2) Etichette interne: compatte su mobile, estese su desktop.
p = Path("app/__init__.py")
text = p.read_text(encoding="utf-8")
text = replace_once(
    text,
    "from app.decimal_number_input import decimal_number_input\n",
    "from app.decimal_number_input import decimal_number_input\nfrom app.device_mode import full_device_is_mobile\n",
    "init import device mode",
)
start = "def _compact_mobile_label(label, key) -> str:\n"
end = "\n\ndef _number_input_with_decimal_point(label, *args, **kwargs):\n"
new_func = '''def _compact_mobile_label(label, key) -> str:
    prudent_mode = bool(st.session_state.get("stima_cautelativa_beta", False))
    range_mode = bool(st.session_state.get("range_unico_beta", False))

    if not full_device_is_mobile():
        if key == "fattore_correzione":
            return "Fattore di correzione (FC)"
        if key == "fc_min_val":
            return "Fattore di correzione minimo"
        if key == "fc_other_val":
            return "Fattore di correzione massimo"
        if key == "ta_base_val":
            return "T. ambientale media 1" if prudent_mode and range_mode else "T. ambientale media"
        if key == "ta_other_val":
            return "T. ambientale media 2"
        if key == "rt_val":
            return "T. rettale"
        if key == "tm_val":
            return "T. ante-mortem stimata"
        if key == "peso":
            return "Peso"

        text = str(label or key).strip().rstrip(":")
        for suffix in (" (°C)", " (kg)"):
            if text.endswith(suffix):
                text = text[:-len(suffix)]
                break
        return text

    if key == "fattore_correzione":
        return "FC"
    if key == "fc_min_val":
        return "FC min"
    if key == "fc_other_val":
        return "FC max"
    if key == "ta_base_val":
        return "T. amb. 1" if prudent_mode and range_mode else "T. amb. media"
    if key == "ta_other_val":
        return "T. amb. 2"

    text = str(label or key).strip().rstrip(":")
    if key == "tm_val":
        text = text.replace(" stimata", "")
    for suffix in (" (°C)", " (kg)"):
        if text.endswith(suffix):
            text = text[:-len(suffix)]
            break
    return text
'''
text = replace_between(text, start, end, new_func, "compact label function")
p.write_text(text, encoding="utf-8")


# 3) Full principale: Henssge e V2 desktop.
p = Path("Stima_epoca_decesso.py")
text = p.read_text(encoding="utf-8")

old_henssge_desktop = '''    else:
        st.markdown(
            f"<div class='mortem-section-title'>{i18n.ui_text('full.cooling_heading')}</div>",
            unsafe_allow_html=True,
        )
        henssge_non_app = st.checkbox(
            i18n.ui_text("full.henssge_not_applicable"),
            key="henssge_non_applicabile",
            help=i18n.ui_text("full.henssge_not_applicable_help"),
        )
'''
new_henssge_desktop = '''    else:
        with st.container(
            horizontal=True,
            wrap=False,
            horizontal_alignment="distribute",
            vertical_alignment="center",
            gap="small",
            key="cooling_heading_row_desktop",
        ):
            with st.container(width="stretch", key="cooling_heading_title_desktop"):
                st.markdown(
                    f"<div class='mortem-section-title'>{i18n.ui_text('full.cooling_heading')}</div>",
                    unsafe_allow_html=True,
                )
            with st.container(width="content", key="cooling_heading_actions_desktop"):
                henssge_non_app = st.checkbox(
                    i18n.ui_text("full.henssge_not_applicable"),
                    key="henssge_non_applicabile",
                    help=i18n.ui_text("full.henssge_not_applicable_help"),
                )
'''
text = replace_once(text, old_henssge_desktop, new_henssge_desktop, "desktop Henssge header")

cautious_start = '''            else:
                # Riga 1: T. rettale, T. ante-mortem, Peso + switch ±3 kg
'''
cautious_end = '''
        else:
            # -------------------------
            # 🔷 MASCHERA STANDARD
'''
cautious_new = '''            else:
                with st.container(gap="small", key="cooling_prudent_v2_grid_desktop"):
                    c1, c2 = st.columns(2, gap="small")
                    with c1:
                        rectal_label = i18n.ui_text("full.rectal_temp_label")
                        st.number_input(
                            rectal_label,
                            value=sget("rt_val", 35.0), step=0.1, format="%.1f",
                            key="rt_val", label_visibility="collapsed"
                        )
                    with c2:
                        st.number_input(
                            i18n.ui_text("full.antemortem_temp_estimated_label"),
                            value=sget("tm_val", 37.2), step=0.1, format="%.1f",
                            key="tm_val", label_visibility="collapsed"
                        )

                    with st.container(
                        horizontal=True,
                        wrap=False,
                        horizontal_alignment="distribute",
                        vertical_alignment="center",
                        gap="small",
                        key="prudent_weight_row_desktop",
                    ):
                        with st.container(width="stretch", key="prudent_weight_value_desktop"):
                            st.number_input(
                                i18n.ui_text("full.weight_label"),
                                value=sget("peso", 70.0), step=1.0, format="%.1f",
                                key="peso", label_visibility="collapsed"
                            )
                        with st.container(width="content", key="prudent_weight_uncertainty_desktop"):
                            st.toggle(i18n.ui_text("full.weight_uncertainty"), key="peso_stimato_beta")

                    ta_c1, ta_c2 = st.columns(2, gap="small")
                    with ta_c1:
                        ta_base_val = st.number_input(
                            i18n.ui_text("full.ta_base_input"),
                            value=sget("ta_base_val", 20.0),
                            step=0.1, format="%.1f",
                            key="ta_base_val",
                            label_visibility="collapsed"
                        )
                    with ta_c2:
                        ta_other_val = st.number_input(
                            i18n.ui_text("full.ta_other_input"),
                            value=sget("ta_other_val", ta_base_val),
                            step=0.1, format="%.1f",
                            key="ta_other_val",
                            label_visibility="collapsed"
                        )
                    ta_values = [
                        st.session_state.get("ta_base_val"),
                        st.session_state.get("ta_other_val"),
                    ]
                    if all(_is_num(v) for v in ta_values):
                        lo_ta, hi_ta = sorted(float(v) for v in ta_values)
                        st.session_state["Ta_min_beta"], st.session_state["Ta_max_beta"] = lo_ta, hi_ta
                    else:
                        st.session_state.pop("Ta_min_beta", None)
                        st.session_state.pop("Ta_max_beta", None)

                    fc_min_val = st.number_input(
                        i18n.ui_text("full.fc_min_input"),
                        value=sget("fc_min_val", sget("fattore_correzione", 1.0)),
                        step=0.1, format="%.2f",
                        key="fc_min_val",
                        label_visibility="collapsed"
                    )
                    fc_other_val = st.number_input(
                        i18n.ui_text("full.fc_max_input"),
                        value=sget("fc_other_val", sget("fattore_correzione", 1.0)),
                        step=0.1, format="%.2f",
                        key="fc_other_val",
                        label_visibility="collapsed"
                    )
                    fc_values = [
                        st.session_state.get("fc_min_val"),
                        st.session_state.get("fc_other_val"),
                    ]
                    if all(_is_num(v) for v in fc_values):
                        lo_fc, hi_fc = sorted(float(v) for v in fc_values)
                        st.session_state["FC_min_beta"], st.session_state["FC_max_beta"] = lo_fc, hi_fc
                    else:
                        st.session_state.pop("FC_min_beta", None)
                        st.session_state.pop("FC_max_beta", None)

                    st.session_state["toggle_fattore"] = bool(
                        st.session_state.get("toggle_fattore_inline", False)
                    )
'''
text = replace_between(text, cautious_start, cautious_end, cautious_new, "desktop cautious V2 block")

standard_start = '''            else:
                col1, col2, col3 = st.columns([1, 1, 1], gap="small")
'''
standard_end = '''
    # --- Pannello "Suggerisci FC" interno al riquadro raffreddamento ---
'''
standard_new = '''            else:
                with st.container(gap="small", key="cooling_standard_v2_grid_desktop"):
                    c1, c2 = st.columns(2, gap="small")
                    with c1:
                        rectal_label = i18n.ui_text("full.rectal_temp_label")
                        st.number_input(
                            rectal_label,
                            value=sget("rt_val", 35.0), step=0.1, format="%.1f",
                            key="rt_val", label_visibility="collapsed"
                        )
                    with c2:
                        st.number_input(
                            i18n.ui_text("full.antemortem_temp_estimated_label"),
                            value=sget("tm_val", 37.2), step=0.1, format="%.1f",
                            key="tm_val", label_visibility="collapsed"
                        )

                    c1, c2 = st.columns(2, gap="small")
                    with c1:
                        st.number_input(
                            i18n.ui_text("full.weight_label"),
                            value=sget("peso", 70.0), step=1.0, format="%.1f",
                            key="peso", label_visibility="collapsed"
                        )
                    with c2:
                        st.number_input(
                            i18n.ui_text("full.ta_input_label"),
                            value=sget("ta_base_val", 20.0), step=0.1, format="%.1f",
                            key="ta_base_val", label_visibility="collapsed"
                        )

                    st.number_input(
                        i18n.ui_text("full.fc_input_label"),
                        value=sget("fattore_correzione", 1.0), step=0.1, format="%.2f",
                        key="fattore_correzione", label_visibility="collapsed"
                    )
                    st.session_state["toggle_fattore"] = bool(
                        st.session_state.get("toggle_fattore_inline_std", False)
                    )
'''
text = replace_between(text, standard_start, standard_end, standard_new, "desktop standard V2 block")
p.write_text(text, encoding="utf-8")


# 4) Pannello FC Full: stepper, superficie neutra, riga risultato comune.
p = Path("app/full_factor_panel.py")
text = p.read_text(encoding="utf-8")
text = replace_once(
    text,
    '_FULL_MOBILE_SURFACE_PLACEHOLDER = "Superficie di appoggio ?"\n',
    '_FULL_MOBILE_SURFACE_PLACEHOLDER = "Superficie di appoggio ?"\n_FULL_DESKTOP_SURFACE_PLACEHOLDER = "Seleziona la superficie"\n',
    "desktop surface placeholder constant",
)

switch_start = '''    if full_mobile:
        # Streamlit 1.62 permette una vera riga orizzontale non spezzabile.
'''
switch_end = '''
    n_sottili = n_spessi = n_cop_medie = n_cop_pesanti = 0
'''
switch_new = '''    if not mobile:
        if full_mobile:
            st.markdown(
                f"""
                <style>
                @media (max-width: 768px) {{
                  [class*="st-key-{key_prefix}_switch_row"][data-testid="stHorizontalBlock"],
                  [class*="st-key-{key_prefix}_switch_row"] [data-testid="stHorizontalBlock"] {{
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                    align-items: center !important;
                    gap: 0.30rem !important;
                  }}
                  [class*="st-key-{key_prefix}_switch_row"] [data-testid="stToggle"] {{
                    width: max-content !important;
                    max-width: max-content !important;
                    min-width: max-content !important;
                  }}
                  [class*="st-key-{key_prefix}_switch_row"] label,
                  [class*="st-key-{key_prefix}_switch_row"] label p {{
                    white-space: nowrap !important;
                  }}
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )
        with st.container(
            horizontal=True,
            wrap=False,
            horizontal_alignment="distribute",
            vertical_alignment="center",
            gap="small",
            key=k("switch_row"),
        ):
            with st.container(
                horizontal=True,
                wrap=False,
                vertical_alignment="center",
                gap="xsmall",
                width="content",
                key=k("vest_group"),
            ):
                with st.container(width="content", key=k("vest_slot")):
                    toggle_vestito = st.toggle(
                        "Vestiti/coperte" if full_mobile else i18n.ui_text("full.clothed_covered"),
                        key=k("toggle_vestito"), value=False
                    )
                with st.container(width="content", key=k("vest_help_slot")):
                    with st.popover("?"):
                        st.markdown(
                            """
                            <div class="mortem-help-copy">
                              <div class="mortem-help-copy-intro">Esempi orientativi per classificare vestiti, teli e coperte:</div>
                              <div class="mortem-help-copy-bullet">• Vestiti/teli leggeri: T-shirt, camicia, lenzuolo o telo sottile.</div>
                              <div class="mortem-help-copy-bullet">• Vestiti/teli pesanti: maglione, felpa pesante, giacca o telo spesso.</div>
                              <div class="mortem-help-copy-bullet">• Coperte medie: coperta di normale spessore.</div>
                              <div class="mortem-help-copy-bullet">• Coperte pesanti/termiche: piumone pesante o mantellina/coperta termica.</div>
                              <div class="mortem-help-copy-intro">Conta separatamente ogni strato effettivamente presente sul corpo.</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            with st.container(width="content", key=k("corr_slot")):
                corr_placeholder = st.empty()
    else:
        col_corr, col_vest = st.columns([1.0, 1.3], gap="small")
        with col_corr:
            corr_placeholder = st.empty()
        with col_vest:
            toggle_vestito = st.toggle(
                i18n.ui_text("msil.clothed_covered"),
                value=st.session_state.get(k("toggle_vestito"), False),
                key=k("toggle_vestito")
            )
'''
text = replace_between(text, switch_start, switch_end, switch_new, "factor Full switch row")

clothes_start = '''        if full_mobile:
            n_sottili = _safe_int(st.number_input(
'''
clothes_end = '''        else:
            item_col = i18n.ui_text("msil.item_column") if mobile else "--"
'''
clothes_new = '''        if not mobile:
            thin_input_label = "Vestiti/teli leggeri" if full_mobile else label_sottili
            thick_input_label = "Vestiti/teli pesanti" if full_mobile else label_spessi
            medium_blanket_input_label = "Coperte medie" if full_mobile else label_coperte_medie
            heavy_blanket_input_label = "Coperte pesanti/termiche" if full_mobile else label_coperte_pesanti

            n_sottili = _safe_int(st.number_input(
                thin_input_label,
                value=st.session_state.get(k("strati_sottili"), 0),
                min_value=0, max_value=8, step=1, format="%.0f",
                key=k("strati_sottili"), label_visibility="collapsed",
            ))
            n_spessi = _safe_int(st.number_input(
                thick_input_label,
                value=st.session_state.get(k("strati_spessi"), 0),
                min_value=0, max_value=8, step=1, format="%.0f",
                key=k("strati_spessi"), label_visibility="collapsed",
            ))
            if stato_corpo == "Asciutto":
                n_cop_medie = _safe_int(st.number_input(
                    medium_blanket_input_label,
                    value=st.session_state.get(k("coperte_medie"), 0),
                    min_value=0, max_value=8, step=1, format="%.0f",
                    key=k("coperte_medie"), label_visibility="collapsed",
                ))
                n_cop_pesanti = _safe_int(st.number_input(
                    heavy_blanket_input_label,
                    value=st.session_state.get(k("coperte_pesanti"), 0),
                    min_value=0, max_value=8, step=1, format="%.0f",
                    key=k("coperte_pesanti"), label_visibility="collapsed",
                ))
'''
text = replace_between(text, clothes_start, clothes_end, clothes_new, "factor Full clothing steppers")

surface_start = '''        select_options = options_display
        if full_mobile:
            select_options = [_FULL_MOBILE_SURFACE_PLACEHOLDER, *options_display]
'''
surface_end = '''        else:
            superficie_display_selected = surface_legacy_value(superficie_display_label)
'''
surface_new = '''        full_surface_placeholder = None
        select_options = options_display
        if not mobile:
            full_surface_placeholder = (
                _FULL_MOBILE_SURFACE_PLACEHOLDER
                if full_mobile
                else _FULL_DESKTOP_SURFACE_PLACEHOLDER
            )
            select_options = [full_surface_placeholder, *options_display]

        prev_display = st.session_state.get(k("superficie_display_sel"))
        if prev_display not in select_options:
            prev_display = full_surface_placeholder if full_surface_placeholder else options_display[0]

        select_kwargs = dict(
            index=select_options.index(prev_display),
            key=k("superficie_display_sel")
        )
        if mobile:
            select_kwargs["label_visibility"] = "visible"
        elif full_mobile:
            select_kwargs["label_visibility"] = "collapsed"
            select_kwargs["format_func"] = _full_mobile_surface_caption
            select_kwargs["filter_mode"] = None
        else:
            select_kwargs["label_visibility"] = "visible"

        if full_mobile:
            with st.container(key=k("surface_select_mobile")):
                superficie_display_label = st.selectbox(
                    i18n.ui_text(f"{scope}.support_surface"),
                    select_options,
                    **select_kwargs
                )
        elif not mobile:
            with st.container(key=k("surface_select_desktop")):
                superficie_display_label = st.selectbox(
                    i18n.ui_text(f"{scope}.support_surface"),
                    select_options,
                    **select_kwargs
                )
        else:
            superficie_display_label = st.selectbox(
                i18n.ui_text(f"{scope}.support_surface"),
                select_options,
                **select_kwargs
            )
        if full_surface_placeholder and superficie_display_label == full_surface_placeholder:
            # Placeholder neutro: non attribuisce un fattore proprio alla superficie.
            # Per le correnti usa la stessa classe INDIFFERENTE del default storico.
            surface_placeholder_selected = True
            superficie_display_selected = surface_legacy_value(options_display[0])
'''
text = replace_between(text, surface_start, surface_end, surface_new, "factor Full surface selector")

text = replace_once(
    text,
    '    if full_mobile and surface_placeholder_selected:\n        result.riassunto["superficie"] = "/"\n',
    '    if not mobile and surface_placeholder_selected:\n        result.riassunto["superficie"] = "/"\n',
    "factor placeholder summary",
)

apply_start = '''    full_mobile = full_device_is_mobile()

    if full_mobile:
'''
apply_end = '''

def pannello_suggerisci_fc_mobile(peso_default: float = 70.0, key_prefix: str = "fcpanel_m"):
'''
apply_new = '''    full_mobile = full_device_is_mobile()

    side_text = ""
    if (
        result.fattore_base is not None
        and peso_eff is not None
        and abs(result.fattore_finale - result.fattore_base) > 1e-9
    ):
        side_text = i18n.ui_text(
            "full.fc_adjusted_for_weight", weight=peso_eff, base=result.fattore_base
        )

    apply_callback = _apply_fc_range if range_mode else _apply_fc
    apply_args = (result.fattore_finale,) if range_mode else (result.fattore_finale, result.riassunto)

    with st.container(border=False, key=f"{key_prefix}_fc_apply_block_mobile"):
        with st.container(
            horizontal=True,
            wrap=False,
            horizontal_alignment="left",
            vertical_alignment="center",
            gap="small",
            key=f"{key_prefix}_fc_apply_row_mobile",
        ):
            with st.container(width="content", key=f"{key_prefix}_fc_apply_value_mobile"):
                st.markdown(
                    f'<div class="mortem-fc-inline-result">FC suggerito:&nbsp;<strong>{result.fattore_finale:.2f}</strong></div>',
                    unsafe_allow_html=True,
                )
            with st.container(width="content", key=f"{key_prefix}_fc_apply_action_mobile"):
                st.button(
                    "→ Usalo",
                    type="secondary",
                    on_click=apply_callback, args=apply_args,
                    key=f"{key_prefix}_btn_usa_fc{suffix}",
                )
        if side_text:
            st.markdown(
                f'<div class="mortem-fc-weight-note-mobile">{side_text}</div>',
                unsafe_allow_html=True,
            )
'''
text = replace_between(text, apply_start, apply_end, apply_new, "factor Full apply result")
p.write_text(text, encoding="utf-8")


# 5) Stili desktop corrispondenti, lasciando intatti i riquadri.
p = Path("app/full_mobile_compact.py")
text = p.read_text(encoding="utf-8")
close_marker = '\n}\n</style>\n"""\n\n\ndef install_full_mobile_compact_css()'
assert text.count(close_marker) == 1, "compact CSS closing marker not unique"
desktop_css = r'''
}

@media (min-width: 769px) {
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_row_desktop"] {
    width: 100% !important;
    min-width: 0 !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_title_desktop"] {
    flex: 1 1 auto !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_actions_desktop"] {
    flex: 0 0 auto !important;
    width: max-content !important;
    min-width: max-content !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] {
    width: max-content !important;
    min-width: max-content !important;
    gap: 0.12rem !important;
    margin: 0 !important;
    padding: 0 !important;
    justify-content: flex-end !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] {
    width: 1.55rem !important;
    min-width: 1.55rem !important;
    max-width: 1.55rem !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label {
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 1.55rem !important;
    min-width: 1.55rem !important;
    height: 1.55rem !important;
    min-height: 1.55rem !important;
    margin: 0 !important;
    padding: 0 !important;
    cursor: pointer !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label > * {
    position: absolute !important;
    opacity: 0 !important;
    pointer-events: none !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label::after {
    content: "⦸";
    position: static !important;
    display: block !important;
    font-size: 1.22rem !important;
    line-height: 1 !important;
    font-weight: 500 !important;
    opacity: 0.58;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label:has(input:checked)::after {
    opacity: 1 !important;
    color: #c62828 !important;
    font-weight: 700 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-prudent_weight_row_desktop"] {
    width: 100% !important;
    min-width: 0 !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 0.45rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-prudent_weight_value_desktop"] {
    flex: 1 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-prudent_weight_uncertainty_desktop"] {
    flex: 0 0 auto !important;
    width: max-content !important;
    min-width: max-content !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_switch_row"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_switch_row"] {
    width: 100% !important;
    min-width: 0 !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_corr_slot"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_corr_slot"] {
    flex: 0 0 auto !important;
    width: max-content !important;
    min-width: max-content !important;
    margin-left: auto !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_vest_group"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_vest_group"] {
    flex: 0 0 auto !important;
    width: max-content !important;
    min-width: max-content !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_vest_help_slot"] button,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_vest_help_slot"] button {
    width: 1.45rem !important;
    min-width: 1.45rem !important;
    height: 1.45rem !important;
    min-height: 1.45rem !important;
    padding: 0 !important;
    border-radius: 50% !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_surface_select_desktop"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_surface_select_desktop"] {
    padding: 0.10rem !important;
    border: 1px solid color-mix(in srgb, #d79a00 58%, transparent) !important;
    border-radius: 0.58rem !important;
    background: color-mix(in srgb, var(--st-secondary-background-color) 86%, #ffc107 14%) !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_surface_select_desktop"] [data-testid="stSelectbox"] [data-baseweb="select"] > div,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_surface_select_desktop"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: color-mix(in srgb, var(--st-secondary-background-color) 90%, #ffc107 10%) !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_block_mobile"] {
    box-sizing: border-box !important;
    width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0.10rem 0.12rem !important;
    border: 1px solid color-mix(in srgb, var(--st-primary-color, #168AC1) 62%, transparent) !important;
    border-radius: 0.58rem !important;
    background: color-mix(in srgb, var(--st-secondary-background-color, #F0F2F6) 86%, var(--st-primary-color, #168AC1) 14%) !important;
    overflow: hidden !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_block_mobile"] > [data-testid="stVerticalBlock"] {
    gap: 0.03rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_row_mobile"] {
    width: 100% !important;
    min-width: 0 !important;
    height: 2.05rem !important;
    min-height: 2.05rem !important;
    max-height: 2.05rem !important;
    gap: 0.28rem !important;
    align-items: center !important;
    justify-content: flex-start !important;
    overflow: hidden !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_value_mobile"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_action_mobile"] {
    flex: 0 0 auto !important;
    width: max-content !important;
    min-width: max-content !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  .mortem-fc-inline-result {
    box-sizing: border-box;
    display: flex;
    align-items: center;
    height: 2.05rem;
    min-height: 2.05rem;
    max-height: 2.05rem;
    padding: 0 0.55rem;
    font-size: 0.92rem;
    line-height: 1.1;
    font-weight: 600;
    color: var(--st-text-color, #31333F);
    white-space: nowrap;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_action_mobile"] button {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 2.05rem !important;
    min-height: 2.05rem !important;
    max-height: 2.05rem !important;
    margin: 0 !important;
    padding: 0 0.72rem !important;
    border: 1.5px solid var(--st-primary-color, #168AC1) !important;
    border-radius: 0.46rem !important;
    background: color-mix(in srgb, var(--st-primary-color, #168AC1) 10%, #ffffff) !important;
    color: var(--st-text-color, #31333F) !important;
    box-shadow: none !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_action_mobile"] button p,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_action_mobile"] button span {
    color: var(--st-text-color, #31333F) !important;
    font-weight: 700 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_action_mobile"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_action_mobile"] > [data-testid="stVerticalBlock"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_action_mobile"] [data-testid="stElementContainer"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="fc_apply_action_mobile"] [data-testid="stButton"] {
    height: 2.05rem !important;
    min-height: 2.05rem !important;
    max-height: 2.05rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  .mortem-fc-weight-note-mobile {
    box-sizing: border-box;
    width: 100%;
    margin: 0 !important;
    padding: 0 0.55rem 0.18rem !important;
    font-size: 0.80rem;
    line-height: 1.22;
    white-space: normal;
    color: var(--st-text-color, #31333F);
  }
}
'''
text = text.replace(
    close_marker,
    "\n" + desktop_css + '</style>\n"""\n\n\ndef install_full_mobile_compact_css()',
    1,
)
p.write_text(text, encoding="utf-8")


# Static checks.
stima = Path("Stima_epoca_decesso.py").read_text(encoding="utf-8")
panel = Path("app/full_factor_panel.py").read_text(encoding="utf-8")
dec = Path("app/decimal_number_input.py").read_text(encoding="utf-8")
init = Path("app/__init__.py").read_text(encoding="utf-8")
css = Path("app/full_mobile_compact.py").read_text(encoding="utf-8")

assert "cooling_heading_row_desktop" in stima
assert "cooling_standard_v2_grid_desktop" in stima
assert "cooling_prudent_v2_grid_desktop" in stima
assert 'st.toggle(i18n.ui_text("full.suggest_fc"), key="toggle_fattore_inline_std")' in stima
assert 'st.toggle(i18n.ui_text("full.suggest_fc"), key="toggle_fattore_inline")' not in stima
assert "_FULL_DESKTOP_SURFACE_PLACEHOLDER" in panel
assert "surface_select_desktop" in panel
assert '"→ Usalo"' in panel
assert "full.add_to_fc_range" not in panel
assert "compact_mobile = bool(compact_mobile)" in dec
assert "full_device_is_mobile" in init
assert "Fattore di correzione massimo" in init
assert "@media (min-width: 769px)" in css
