from pathlib import Path
from textwrap import indent


# 1) Full: costruzione mobile strutturale della modalità con intervalli.
stima_path = Path("Stima_epoca_decesso.py")
stima = stima_path.read_text(encoding="utf-8")
start_marker = "            # Riga 1: T. rettale, T. ante-mortem, Peso + switch ±3 kg\n"
end_marker = '            st.session_state["toggle_fattore"] = st.session_state.get("toggle_fattore_inline", False)\n'
assert stima.count(start_marker) == 1
start = stima.index(start_marker)
end = stima.index(end_marker, start) + len(end_marker)
desktop_block = stima[start:end]

mobile_block = '''            if full_mobile:
                with st.container(gap="xsmall", key="cooling_prudent_v2_stack_mobile"):
                    rectal_label = i18n.ui_text("full.rectal_temp_label")
                    st.number_input(
                        rectal_label,
                        value=sget("rt_val", 35.0), step=0.1, format="%.1f",
                        key="rt_val", label_visibility="collapsed"
                    )
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
                        key="prudent_weight_row_mobile",
                    ):
                        with st.container(width="stretch", key="prudent_weight_value_mobile"):
                            st.number_input(
                                i18n.ui_text("full.weight_label"),
                                value=sget("peso", 70.0), step=1.0, format="%.1f",
                                key="peso", label_visibility="collapsed"
                            )
                        with st.container(width="content", key="prudent_weight_uncertainty_mobile"):
                            st.toggle(i18n.ui_text("full.weight_uncertainty"), key="peso_stimato_beta")

                    ta_base_val = st.number_input(
                        i18n.ui_text("full.ta_base_input"),
                        value=sget("ta_base_val", 20.0),
                        step=0.1, format="%.1f",
                        key="ta_base_val",
                        label_visibility="collapsed"
                    )
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

                    # In mobile il solo V2 "FC max" ospita il comando Consiglia.
                    # Il pannello suggerisce l'intero intervallo, non un estremo specifico.
                    st.session_state["toggle_fattore"] = bool(
                        st.session_state.get("toggle_fattore_inline", False)
                    )
            else:
'''
stima = stima[:start] + mobile_block + indent(desktop_block, "    ") + stima[end:]
stima_path.write_text(stima, encoding="utf-8")


# 2) V2: un solo Consiglia in modalità con intervalli, sul controllo FC max.
init_path = Path("app/__init__.py")
init = init_path.read_text(encoding="utf-8")
old_targets = '''        suggest_target = None
        if compact_mobile:
            if key == "fattore_correzione" and (not prudent_mode or not range_mode):
                suggest_target = "single"
            elif prudent_mode and range_mode and key == "fc_min_val":
                suggest_target = "min"
            elif prudent_mode and range_mode and key == "fc_other_val":
                suggest_target = "max"
'''
new_targets = '''        suggest_target = None
        if compact_mobile:
            if key == "fattore_correzione" and (not prudent_mode or not range_mode):
                suggest_target = "single"
            elif prudent_mode and range_mode and key == "fc_other_val":
                suggest_target = "range"
'''
assert init.count(old_targets) == 1
init = init.replace(old_targets, new_targets, 1)
init_path.write_text(init, encoding="utf-8")


# 3) V2: helper temperatura immediatamente dopo l'etichetta.
v2_path = Path("app/decimal_number_input_v2.py")
v2 = v2_path.read_text(encoding="utf-8")
label_rule_end = '''  line-height: 1.1;
}
.number-input {
'''
label_rule_new = '''  line-height: 1.1;
}
.number-control.has-help .mobile-label {
  flex: 0 1 auto;
}
.number-control.has-help .number-input {
  margin-left: auto;
}
.number-input {
'''
assert v2.count(label_rule_end) == 1
v2 = v2.replace(label_rule_end, label_rule_new, 1)
js_help = '''  const showHelp = Boolean(data?.help_enabled);
  const showSuggest = Boolean(data?.suggest_enabled);
'''
js_help_new = '''  const showHelp = Boolean(data?.help_enabled);
  const showSuggest = Boolean(data?.suggest_enabled);
  control.classList.toggle('has-help', showHelp);
'''
assert v2.count(js_help) == 1
v2 = v2.replace(js_help, js_help_new, 1)
v2_path.write_text(v2, encoding="utf-8")


# 4) Range suggerito: con una sola proposta usa il valore suggerito e conserva
#    l'estremo corrente più lontano; nessuna generazione artificiale ±0.10.
panel_path = Path("app/full_factor_panel.py")
panel = panel_path.read_text(encoding="utf-8")
old_sync = '''def _sync_fc_range_from_suggestions():
    vals = st.session_state.get("fc_suggested_vals", [])
    vals = sorted({round(float(v), 2) for v in vals if v is not None})
    if not vals:
        return
    lo, hi = (vals[0]-0.10, vals[0]+0.10) if len(vals) == 1 else (vals[0], vals[-1])
    lo, hi = round(lo, 2), round(hi, 2)
    st.session_state["fc_min_val"] = lo
    st.session_state["fc_other_val"] = hi
    st.session_state["FC_min_beta"] = lo
    st.session_state["FC_max_beta"] = hi
    st.session_state["range_unico_beta"] = True
'''
new_sync = '''def _sync_fc_range_from_suggestions():
    vals = st.session_state.get("fc_suggested_vals", [])
    vals = sorted({round(float(v), 2) for v in vals if v is not None})
    if not vals:
        return

    if len(vals) == 1:
        suggested = vals[0]
        current_bounds = []
        for key in ("fc_min_val", "fc_other_val"):
            try:
                current_bounds.append(round(float(st.session_state.get(key)), 2))
            except (TypeError, ValueError):
                pass
        if current_bounds:
            anchor = max(current_bounds, key=lambda value: abs(value - suggested))
        else:
            try:
                anchor = round(float(st.session_state.get("fattore_correzione", suggested)), 2)
            except (TypeError, ValueError):
                anchor = suggested
        lo, hi = sorted((suggested, anchor))
    else:
        lo, hi = vals[0], vals[-1]

    lo, hi = round(lo, 2), round(hi, 2)
    st.session_state["fc_min_val"] = lo
    st.session_state["fc_other_val"] = hi
    st.session_state["FC_min_beta"] = lo
    st.session_state["FC_max_beta"] = hi
    st.session_state["range_unico_beta"] = True
'''
assert panel.count(old_sync) == 1
panel = panel.replace(old_sync, new_sync, 1)

# 5) Risultato FC standard mobile: nota peso dentro lo stesso blocco.
block_start = '    if full_mobile and not range_mode:\n'
block_end = '    else:\n        _fc_box(result.fattore_finale, result.fattore_base, peso_eff)\n'
assert panel.count(block_start) == 1
p_start = panel.index(block_start)
p_end = panel.index(block_end, p_start)
new_panel_block = '''    if full_mobile and not range_mode:
        side_text = ""
        if (
            result.fattore_base is not None
            and peso_eff is not None
            and abs(result.fattore_finale - result.fattore_base) > 1e-9
        ):
            side_text = i18n.ui_text(
                "full.fc_adjusted_for_weight", weight=peso_eff, base=result.fattore_base
            )

        with st.container(border=False, key=f"{key_prefix}_fc_apply_block_mobile"):
            with st.container(
                horizontal=True,
                wrap=False,
                horizontal_alignment="distribute",
                vertical_alignment="center",
                gap=None,
                key=f"{key_prefix}_fc_apply_row_mobile",
            ):
                with st.container(width="stretch", key=f"{key_prefix}_fc_apply_value_mobile"):
                    st.markdown(
                        f'<div class="mortem-fc-inline-result">FC suggerito:&nbsp;<strong>{result.fattore_finale:.2f}</strong></div>',
                        unsafe_allow_html=True,
                    )
                with st.container(width="content", key=f"{key_prefix}_fc_apply_action_mobile"):
                    st.button(
                        "→ Usa",
                        type="secondary",
                        on_click=_apply_fc, args=(result.fattore_finale, result.riassunto),
                        key=f"{key_prefix}_btn_usa_fc{suffix}",
                    )
            if side_text:
                st.markdown(
                    f'<div class="mortem-fc-weight-note-mobile">{side_text}</div>',
                    unsafe_allow_html=True,
                )
'''
panel = panel[:p_start] + new_panel_block + panel[p_end:]
panel_path.write_text(panel, encoding="utf-8")


# 6) CSS mobile: stack prudente a piena larghezza + risultato realmente unico.
compact_path = Path("app/full_mobile_compact.py")
compact = compact_path.read_text(encoding="utf-8")
css_start = "/* Risultato FC standard mobile: valore e azione su una sola riga. */\n"
css_end = "/* Il selettore della superficie deve distinguersi chiaramente dagli stepper. */\n"
assert compact.count(css_start) == 1
c_start = compact.index(css_start)
c_end = compact.index(css_end, c_start)
css_new = r'''/* Modalità Condizioni variabili: V2 a piena larghezza. */
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-cooling_prudent_v2_stack_mobile"] {
  width: 100% !important;
  min-width: 0 !important;
  gap: 0.18rem !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_row_mobile"] {
  width: 100% !important;
  min-width: 0 !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  gap: 0.28rem !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_value_mobile"] {
  flex: 1 1 auto !important;
  width: auto !important;
  min-width: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_uncertainty_mobile"] {
  flex: 0 0 auto !important;
  width: max-content !important;
  min-width: max-content !important;
}

/* Risultato FC standard mobile: valore, azione e nota peso in un solo blocco. */
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_block_mobile"] {
  box-sizing: border-box !important;
  width: 100% !important;
  min-width: 0 !important;
  margin: 0 !important;
  padding: 0.08rem 0.10rem 0.10rem !important;
  border: 1px solid color-mix(in srgb, var(--st-primary-color) 70%, transparent) !important;
  border-radius: 0.58rem !important;
  background: color-mix(in srgb, var(--st-secondary-background-color) 82%, var(--st-primary-color) 18%) !important;
  overflow: hidden !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_block_mobile"] > [data-testid="stVerticalBlock"] {
  gap: 0.02rem !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_row_mobile"] {
  box-sizing: border-box !important;
  width: 100% !important;
  min-width: 0 !important;
  height: 2.15rem !important;
  min-height: 2.15rem !important;
  max-height: 2.15rem !important;
  gap: 0 !important;
  align-items: center !important;
  overflow: hidden !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_value_mobile"] {
  flex: 1 1 auto !important;
  min-width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

.mortem-fc-inline-result {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  height: 2.15rem;
  min-height: 2.15rem;
  max-height: 2.15rem;
  padding: 0 0.48rem;
  font-size: 0.88rem;
  line-height: 1.1;
  font-weight: 600;
  color: var(--st-text-color);
  white-space: nowrap;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] {
  flex: 0 0 auto !important;
  width: max-content !important;
  min-width: max-content !important;
  margin: 0 !important;
  padding: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] button {
  height: 1.86rem !important;
  min-height: 1.86rem !important;
  max-height: 1.86rem !important;
  margin: 0 0.12rem 0 0 !important;
  padding: 0 0.58rem !important;
  border: 1px solid var(--st-primary-color) !important;
  border-radius: 0.44rem !important;
  background: color-mix(in srgb, var(--st-primary-color) 13%, var(--st-secondary-background-color)) !important;
  color: var(--st-text-color) !important;
  font-weight: 650 !important;
  white-space: nowrap !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] button p,
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] button span {
  color: var(--st-text-color) !important;
  font-weight: 650 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] > [data-testid="stVerticalBlock"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] [data-testid="stElementContainer"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] [data-testid="stButton"] {
  height: 2.15rem !important;
  min-height: 2.15rem !important;
  max-height: 2.15rem !important;
  margin: 0 !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: flex-end !important;
}

.mortem-fc-weight-note-mobile {
  box-sizing: border-box;
  width: 100%;
  margin: 0 !important;
  padding: 0 0.48rem 0.12rem !important;
  font-size: 0.76rem;
  line-height: 1.20;
  white-space: normal;
  overflow: visible;
  color: var(--st-text-color);
}

body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stElementContainer"]:has(.mortem-fc-weight-note-mobile) {
  width: 100% !important;
  overflow: visible !important;
  margin: 0 !important;
  padding: 0 !important;
}

'''
compact = compact[:c_start] + css_new + compact[c_end:]
compact_path.write_text(compact, encoding="utf-8")
