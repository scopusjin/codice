# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st

from app import i18n
from app.data_sources import load_tabelle_correzione
from app.device_mode import full_device_is_mobile
from app.factor_calc import DressCounts, compute_factor, fattore_vestiti_coperte, floor_to_step
from app.factor_ui_states import (
    LAYER_THIN,
    LAYER_THICK,
    BLANKET_MEDIUM,
    BLANKET_HEAVY,
)
from app.full_factor_ui import (
    full_body_labels,
    full_body_legacy_value,
    full_water_labels,
    full_water_legacy_value,
    full_clothing_label,
    full_surface_labels,
    full_surface_label,
    full_surface_legacy_value,
)
from app.surface_ui_states import SURFACE_THICK_METAL_OUTDOOR


def _sync_fc_range_from_suggestions():
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


def add_fc_suggestion_global(val: float) -> None:
    v = round(float(val), 2)
    target = st.session_state.get("__full_fc_suggest_target")
    if target in {"min", "max"}:
        other_key = "fc_other_val" if target == "min" else "fc_min_val"
        try:
            other = round(float(st.session_state.get(other_key)), 2)
        except (TypeError, ValueError):
            other = v
        lo, hi = sorted([v, other])
        st.session_state["fc_min_val"] = lo
        st.session_state["fc_other_val"] = hi
        st.session_state["FC_min_beta"] = lo
        st.session_state["FC_max_beta"] = hi
        st.session_state["range_unico_beta"] = True
        st.session_state["toggle_fattore_inline"] = False
        st.session_state["toggle_fattore"] = False
        st.session_state.pop("__full_fc_suggest_target", None)
        return

    vals = st.session_state.get("fc_suggested_vals", [])
    vals = sorted({*vals, v})
    if len(vals) >= 3:
        vals = [vals[0], vals[-1]]
    st.session_state["fc_suggested_vals"] = vals
    _sync_fc_range_from_suggestions()


def _load_factor_table():
    try:
        return load_tabelle_correzione()
    except Exception:
        return None


def _safe_int(x):
    try:
        return int(x)
    except Exception:
        return 0


_FULL_MOBILE_SURFACE_PLACEHOLDER = "Superficie di appoggio ?"
_FULL_DESKTOP_SURFACE_PLACEHOLDER = "Seleziona la superficie"


def _full_mobile_surface_caption(value: str) -> str:
    if value == _FULL_MOBILE_SURFACE_PLACEHOLDER:
        return value
    text = str(value).rstrip(".")
    if not text:
        return text
    return f"Su {text[:1].lower()}{text[1:]}"


def _panel_weight(peso_default: float, mobile: bool) -> float:
    if not mobile:
        return float(st.session_state.get("peso", peso_default))

    if st.session_state.get("peso") in (None, 0) or (st.session_state.get("peso") or 0) <= 0:
        st.session_state["peso"] = 70.0
    peso_eff = st.session_state.get("peso") or peso_default
    try:
        peso_eff = float(peso_eff)
        return peso_eff if peso_eff > 0 else float(peso_default)
    except Exception:
        return float(peso_default)


def _render_factor_panel(
    peso_default: float,
    key_prefix: str,
    *,
    body_labels,
    body_legacy_value,
    water_labels,
    water_legacy_value,
    clothing_label,
    surface_labels,
    surface_label,
    surface_legacy_value,
    mobile: bool,
    full_mobile: bool = False,
    compact_full: bool = False,
    extended_clothing_labels: bool = False,
):
    def k(name: str) -> str:
        return f"{key_prefix}_{name}"

    scope = "msil" if mobile else "full"

    if not mobile:
        st.markdown("""
            <style>
              div[data-testid="stRadio"] > label {display:none !important;}
              div[data-testid="stRadio"] {margin-top:-14px; margin-bottom:-10px;}
              div[data-testid="stRadio"] div[role="radiogroup"] {gap:0.4rem;}
              div[data-testid="stToggle"] {margin-top:-6px; margin-bottom:-6px;}
              div[data-testid="stSlider"] {margin-top:-4px; margin-bottom:-2px;}
            </style>
        """, unsafe_allow_html=True)

    radio_kwargs = dict(index=0, horizontal=True, key=k("radio_stato_corpo"))
    if mobile:
        radio_kwargs["label_visibility"] = "collapsed"

    corr_placeholder = None
    body_aux_placeholder = None
    full_compact_row = compact_full and not mobile
    if full_compact_row:
        row_key = "body_row_mobile" if full_mobile else "body_row_desktop"
        body_slot_key = "body_radio_slot_mobile" if full_mobile else "body_radio_slot_desktop"
        corr_slot_key = "corr_slot_mobile" if full_mobile else "corr_slot_desktop"
        with st.container(key=k(row_key)):
            body_col, right_col = st.columns([1.15, 1.0], gap="small")
            with body_col:
                with st.container(key=k(body_slot_key)):
                    stato_label = st.radio("dummy", list(body_labels()), **radio_kwargs)
            with right_col:
                with st.container(key=k(corr_slot_key)):
                    if full_mobile:
                        body_aux_placeholder = st.empty()
                    else:
                        corr_placeholder = st.empty()
    else:
        stato_label = st.radio("" if mobile else "dummy", list(body_labels()), **radio_kwargs)

    stato_corpo = body_legacy_value(stato_label)

    tabella2_mobile = _load_factor_table() if mobile else None
    peso_eff = _panel_weight(peso_default, True) if mobile else None

    if stato_corpo == "Immerso":
        acqua_kwargs = dict(index=0, horizontal=True, key=k("radio_acqua"))
        if mobile:
            acqua_kwargs["label_visibility"] = "collapsed"
        water_placeholder = body_aux_placeholder if body_aux_placeholder is not None else corr_placeholder
        if water_placeholder is not None:
            with water_placeholder.container():
                acqua_label = st.radio("dummy", list(water_labels()), **acqua_kwargs)
        else:
            acqua_label = st.radio("" if mobile else "dummy", list(water_labels()), **acqua_kwargs)
        acqua_mode = water_legacy_value(acqua_label)

        tabella2 = tabella2_mobile if mobile else _load_factor_table()
        if not mobile:
            peso_eff = _panel_weight(peso_default, False)
        result = compute_factor(
            stato="Immerso", acqua=acqua_mode, counts=DressCounts(),
            superficie_display=None, correnti_aria=False,
            peso=peso_eff,
            tabella2_df=tabella2
        )
        return result, peso_eff, True

    if not mobile:
        if compact_full:
            st.markdown(
                f"""
                <style>
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
                  @media (min-width: 769px) {{
                    [class*="st-key-{key_prefix}_body_row_desktop"],
                    [class*="st-key-{key_prefix}_body_row_desktop"] [data-testid="stHorizontalBlock"] {{
                      width: 100% !important;
                      min-width: 0 !important;
                      align-items: center !important;
                      overflow: visible !important;
                    }}
                    [class*="st-key-{key_prefix}_body_radio_slot_desktop"] {{
                      flex: 0 1 auto !important;
                      width: auto !important;
                      min-width: 0 !important;
                      overflow: visible !important;
                    }}
                    [class*="st-key-{key_prefix}_corr_slot_desktop"] {{
                      flex: 0 0 auto !important;
                      width: max-content !important;
                      min-width: max-content !important;
                      max-width: none !important;
                      margin-left: auto !important;
                      overflow: visible !important;
                    }}
                    [class*="st-key-{key_prefix}_switch_row"],
                    [class*="st-key-{key_prefix}_switch_row"] [data-testid="stHorizontalBlock"],
                    [class*="st-key-{key_prefix}_vest_group"],
                    [class*="st-key-{key_prefix}_vest_group"] [data-testid="stHorizontalBlock"] {{
                      min-height: 2.55rem !important;
                      height: auto !important;
                      max-height: none !important;
                      overflow: visible !important;
                      scrollbar-width: none !important;
                    }}
                    [class*="st-key-{key_prefix}_switch_row"]::-webkit-scrollbar,
                    [class*="st-key-{key_prefix}_switch_row"] [data-testid="stHorizontalBlock"]::-webkit-scrollbar,
                    [class*="st-key-{key_prefix}_vest_group"]::-webkit-scrollbar,
                    [class*="st-key-{key_prefix}_vest_group"] [data-testid="stHorizontalBlock"]::-webkit-scrollbar {{
                      display: none !important;
                      width: 0 !important;
                      height: 0 !important;
                    }}
                  }}
                </style>
                """,
                unsafe_allow_html=True,
            )
        switch_alignment = "left" if corr_placeholder is not None else "distribute"
        with st.container(
            horizontal=True,
            wrap=False,
            horizontal_alignment=switch_alignment,
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
                        "Vestiti/coperte" if compact_full else i18n.ui_text("full.clothed_covered"),
                        key=k("toggle_vestito"), value=False
                    )
                with st.container(width="content", key=k("vest_help_slot")):
                    with st.popover("?"):
                        st.markdown(
                            """
                            <div class="mortem-help-copy">
                              <div class="mortem-help-copy-intro"><b>Le categorie sono orientative e non corrispondono a valori di FC rigidi.</b> Il sistema combina gli effetti dei diversi strati per suggerire un fattore di correzione plausibile. Considera soprattutto gli strati che coprono addome e bacino.</div>
                              <div class="mortem-help-copy-bullet">• Vestiti/teli leggeri: biancheria, T-shirt, camicia, pigiama leggero, lenzuolo o telo sottile.</div>
                              <div class="mortem-help-copy-bullet">• Vestiti/teli pesanti: maglione, felpa pesante, giacca o cappotto che raggiunge il bacino, pantaloni molto spessi o imbottiti, telo spesso.</div>
                              <div class="mortem-help-copy-bullet">• Coperta / copriletto spesso: coperta o copriletto con apprezzabile effetto isolante, ma non assimilabile a un piumone o a una coperta molto spessa. Lenzuoli, teli, copriletti leggeri e plaid sottili vanno considerati tra gli strati di vestiti/teli in base allo spessore.</div>
                              <div class="mortem-help-copy-bullet">• Piumone / coperta molto spessa: piumone, trapunta molto imbottita o coperta particolarmente spessa e isolante.</div>
                              <div class="mortem-help-copy-intro">Conta separatamente gli strati effettivamente sovrapposti nella regione addomino-pelvica. Prova le combinazioni plausibili; se più valori di FC restano ragionevoli, usa <b>Condizioni variabili</b> e considera un intervallo di FC.</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            if corr_placeholder is None:
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

    n_sottili = n_spessi = n_cop_medie = n_cop_pesanti = 0
    if toggle_vestito:
        label_sottili = clothing_label(LAYER_THIN)
        label_spessi = clothing_label(LAYER_THICK)
        label_coperte_medie = clothing_label(BLANKET_MEDIUM)
        label_coperte_pesanti = clothing_label(BLANKET_HEAVY)

        if not mobile:
            if compact_full and not extended_clothing_labels:
                thin_input_label = "Vestiti/teli leggeri"
                thick_input_label = "Vestiti/teli pesanti"
                medium_blanket_input_label = "Coperta / copriletto spesso"
                heavy_blanket_input_label = "Piumone / coperta molto spessa"
            else:
                thin_input_label = label_sottili
                thick_input_label = label_spessi
                medium_blanket_input_label = label_coperte_medie
                heavy_blanket_input_label = label_coperte_pesanti

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
        else:
            item_col = i18n.ui_text("msil.item_column") if mobile else "--"
            count_col = i18n.ui_text(f"{scope}.count_column")
            defaults = {
                label_sottili: st.session_state.get(k("strati_sottili"), 0),
                label_spessi: st.session_state.get(k("strati_spessi"), 0),
            }
            if stato_corpo == "Asciutto":
                defaults.update({
                    label_coperte_medie: st.session_state.get(k("coperte_medie"), 0),
                    label_coperte_pesanti: st.session_state.get(k("coperte_pesanti"), 0),
                })

            df = pd.DataFrame([{item_col: nome, count_col: val} for nome, val in defaults.items()])
            if not mobile:
                st.markdown("""
                <style>
                [data-testid="stDataFrameContainer"] thead {display: none;}
                [data-testid="stElementToolbar"] {display: none;}
                [data-testid="stDataFrameContainer"] tbody th {display: none;}
                </style>
                """, unsafe_allow_html=True)

            edited = st.data_editor(
                df, hide_index=True, use_container_width=True,
                column_config={
                    item_col: st.column_config.TextColumn(disabled=True, width="medium"),
                    count_col: st.column_config.NumberColumn(min_value=0, max_value=8, step=1, width="small"),
                },
            )
            if mobile:
                vals = {r[item_col]: _safe_int(r[count_col]) for _, r in edited.iterrows()}
            else:
                vals = {r[item_col]: int(r[count_col] or 0) for _, r in edited.iterrows()}

            n_sottili = vals.get(label_sottili, 0)
            n_spessi = vals.get(label_spessi, 0)
            n_cop_medie = vals.get(label_coperte_medie, 0) if stato_corpo == "Asciutto" else 0
            n_cop_pesanti = vals.get(label_coperte_pesanti, 0) if stato_corpo == "Asciutto" else 0

    counts = DressCounts(
        sottili=n_sottili, spessi=n_spessi,
        coperte_medie=n_cop_medie, coperte_pesanti=n_cop_pesanti
    )

    surface_placeholder_selected = False
    superficie_display_selected = None if mobile else "/"
    if stato_corpo == "Asciutto":
        nudo_eff = ((not toggle_vestito)
                    or (counts.sottili == counts.spessi == counts.coperte_medie == counts.coperte_pesanti == 0))
        options_display = list(surface_labels())
        if not nudo_eff:
            excluded_surface = surface_label(SURFACE_THICK_METAL_OUTDOOR)
            options_display = [o for o in options_display if o != excluded_surface]

        full_surface_placeholder = None
        select_options = options_display
        if not mobile:
            full_surface_placeholder = (
                _FULL_MOBILE_SURFACE_PLACEHOLDER
                if compact_full
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
        elif compact_full:
            select_kwargs["label_visibility"] = "collapsed"
            select_kwargs["format_func"] = _full_mobile_surface_caption
            select_kwargs["filter_mode"] = None
        else:
            select_kwargs["label_visibility"] = "visible"

        if compact_full:
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
        else:
            superficie_display_selected = surface_legacy_value(superficie_display_label)

    correnti_presenti = False
    with corr_placeholder.container():
        mostra_correnti = True
        if stato_corpo == "Asciutto" and fattore_vestiti_coperte(counts) >= 1.2:
            mostra_correnti = False
        if mostra_correnti:
            toggle_kwargs = dict(key=k("toggle_correnti_fc"), disabled=False)
            if mobile:
                toggle_kwargs["value"] = st.session_state.get(k("toggle_correnti_fc"), False)
            correnti_presenti = st.toggle(
                "Correnti d'aria" if compact_full else i18n.ui_text(f"{scope}.air_currents"),
                **toggle_kwargs
            )

    tabella2 = _load_factor_table()
    if not mobile:
        peso_eff = _panel_weight(peso_default, False)
    result = compute_factor(
        stato=stato_corpo, acqua=None, counts=counts,
        superficie_display=superficie_display_selected if stato_corpo == "Asciutto" else None,
        correnti_aria=correnti_presenti,
        peso=peso_eff,
        tabella2_df=tabella2
    )
    if not mobile and surface_placeholder_selected:
        result.riassunto["superficie"] = "/"
    return result, peso_eff, False


# --- Pannello “Suggerisci FC”
def pannello_suggerisci_fc(peso_default: float = 70.0, key_prefix: str = "fcpanel"):
    full_mobile = full_device_is_mobile()
    result, peso_eff, immersed = _render_factor_panel(
        peso_default, key_prefix,
        body_labels=full_body_labels,
        body_legacy_value=full_body_legacy_value,
        water_labels=full_water_labels,
        water_legacy_value=full_water_legacy_value,
        clothing_label=full_clothing_label,
        surface_labels=full_surface_labels,
        surface_label=full_surface_label,
        surface_legacy_value=full_surface_legacy_value,
        mobile=False,
        full_mobile=full_mobile,
        compact_full=True,
        extended_clothing_labels=not full_mobile,
    )

    def _apply_fc(val: float, riass: str | None) -> None:
        st.session_state["fattore_correzione"] = round(float(val), 2)
        st.session_state["fattori_condizioni_parentetica"] = None
        st.session_state["fattori_condizioni_testo"] = None
        st.session_state["toggle_fattore"] = False
        st.session_state["fc_riassunto_contatori"] = riass

    def _apply_fc_range(val: float) -> None:
        add_fc_suggestion_global(val)
        st.session_state["toggle_fattore_inline"] = False
        st.session_state["toggle_fattore"] = False
        st.session_state.pop("__full_fc_suggest_target", None)

    suffix = "_imm" if immersed else ""
    range_mode = st.session_state.get("range_unico_beta", False)

    side_text = ""
    peso_adattato = bool(result.riassunto.get("peso_adattato", False))
    if not peso_adattato and peso_eff is not None and result.fattore_base is not None:
        try:
            base_senza_peso = floor_to_step(round(float(result.fattore_base), 2))
            peso_adattato = (
                abs(float(peso_eff) - 70.0) > 1e-9
                and float(result.fattore_base) >= 1.4
                and abs(float(result.fattore_finale) - base_senza_peso) > 1e-9
            )
        except (TypeError, ValueError):
            peso_adattato = False
    if peso_adattato and peso_eff is not None:
        side_text = i18n.ui_text(
            "full.fc_adjusted_for_weight", weight=peso_eff, base=result.fattore_base
        )

    apply_callback = _apply_fc_range if range_mode else _apply_fc
    apply_args = (result.fattore_finale,) if range_mode else (result.fattore_finale, result.riassunto)

    st.markdown(
        f'''<style>
        [class*="st-key-{key_prefix}_fc_apply_row_mobile"] {{
          display:flex!important;
          align-items:center!important;
          gap:0.34rem!important;
          margin:0.04rem 0 0 0!important;
          padding:0!important;
        }}
        [class*="st-key-{key_prefix}_fc_apply_value_mobile"] [data-testid="stMarkdownContainer"],
        [class*="st-key-{key_prefix}_fc_apply_value_mobile"] .mortem-fc-inline-result {{
          display:flex!important;
          align-items:center!important;
          min-height:2.5rem!important;
          margin:0!important;
          padding:0!important;
          line-height:1!important;
        }}
        [class*="st-key-{key_prefix}_fc_apply_action_mobile"] [data-testid="stButton"] {{
          display:flex!important;
          align-items:center!important;
          margin:0!important;
          padding:0!important;
        }}
        [class*="st-key-{key_prefix}_fc_apply_action_mobile"] button {{
          display:flex!important;
          align-items:center!important;
          justify-content:center!important;
          min-height:2.5rem!important;
          height:2.5rem!important;
          margin:0!important;
          padding:0 0.85rem!important;
        }}
        [class*="st-key-{key_prefix}_fc_apply_action_mobile"] button p {{
          margin:0!important;
          line-height:1!important;
        }}
        [class*="st-key-{key_prefix}_fc_apply_value_mobile"] .mortem-fc-result-stack {{
          display:flex!important;
          flex-direction:column!important;
          justify-content:center!important;
          margin:0!important;
          padding:0!important;
        }}
        [class*="st-key-{key_prefix}_fc_apply_value_mobile"] .mortem-fc-result-stack .mortem-fc-inline-result {{
          min-height:0!important;
        }}
        [class*="st-key-{key_prefix}_fc_apply_value_mobile"] .mortem-fc-weight-note-mobile {{
          font-size:0.74rem!important;
          line-height:1.15!important;
          margin:0.12rem 0 0 0!important;
          padding:0!important;
          opacity:0.78!important;
          white-space:normal!important;
        }}
        @media (min-width:769px) {{
          [class*="st-key-full_fc_panel_desktop"] {{
            box-sizing:border-box!important;
            width:min(100%,46rem)!important;
            max-width:46rem!important;
            min-width:0!important;
            align-self:flex-start!important;
            margin:0.18rem 0 0 0!important;
            padding:0.34rem 0.24rem!important;
            border:0!important;
            border-radius:0.55rem!important;
            box-shadow:none!important;
            background:color-mix(in srgb, var(--st-primary-color,#168AC1) 14%, transparent)!important;
          }}
          [class*="st-key-full_fc_panel_desktop"][data-testid="stVerticalBlock"],
          [class*="st-key-full_fc_panel_desktop"] > [data-testid="stVerticalBlock"] {{
            gap:0.16rem!important;
          }}
          [class*="st-key-full_fc_panel_desktop"] [class*="st-key-{key_prefix}_switch_row"] {{
            margin-top:0.12rem!important;
            margin-bottom:-0.08rem!important;
            padding-top:0!important;
            padding-bottom:0!important;
          }}
          [class*="st-key-full_fc_panel_desktop"] [class*="st-key-{key_prefix}_corr_slot"] {{
            flex:0 0 auto!important;
            width:max-content!important;
            min-width:max-content!important;
            max-width:none!important;
            margin-left:auto!important;
            overflow:visible!important;
          }}
          [class*="st-key-full_fc_panel_desktop"] [class*="st-key-{key_prefix}_vest_group"] {{
            flex:0 0 auto!important;
            width:max-content!important;
            min-width:max-content!important;
            max-width:none!important;
            overflow:visible!important;
          }}
          [class*="st-key-full_fc_panel_desktop"] [class*="st-key-mortem_decimal_{key_prefix}_"] {{
            height:34px!important;
            min-height:34px!important;
          }}
          [class*="st-key-full_fc_panel_desktop"] [class*="st-key-mortem_decimal_{key_prefix}_"] iframe {{
            display:block!important;
            height:34px!important;
            min-height:34px!important;
            max-height:34px!important;
          }}
          [class*="st-key-full_fc_panel_desktop"] [class*="st-key-{key_prefix}_surface_select_mobile"] [data-testid="stSelectbox"] {{
            margin-top:0.04rem!important;
            margin-bottom:0!important;
          }}
        }}
        </style>''',
        unsafe_allow_html=True,
    )

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
                weight_note_html = (
                    f'<div class="mortem-fc-weight-note-mobile">{side_text}</div>'
                    if side_text else ""
                )
                st.markdown(
                    f'<div class="mortem-fc-result-stack">'
                    f'<div class="mortem-fc-inline-result">FC suggerito:&nbsp;<strong>{result.fattore_finale:.2f}</strong></div>'
                    f'{weight_note_html}</div>',
                    unsafe_allow_html=True,
                )
            with st.container(width="content", key=f"{key_prefix}_fc_apply_action_mobile"):
                st.button(
                    "→ Usalo",
                    type="secondary",
                    on_click=apply_callback, args=apply_args,
                    key=f"{key_prefix}_btn_usa_fc{suffix}",
                )


def pannello_suggerisci_fc_mobile(peso_default: float = 70.0, key_prefix: str = "fcpanel_m"):
    from app.msil_factor_ui import (
        msil_body_labels,
        msil_body_legacy_value,
        msil_water_labels,
        msil_water_legacy_value,
        msil_clothing_label,
        msil_surface_labels,
        msil_surface_label,
        msil_surface_legacy_value,
    )

    result, _, _ = _render_factor_panel(
        peso_default, key_prefix,
        body_labels=msil_body_labels,
        body_legacy_value=msil_body_legacy_value,
        water_labels=msil_water_labels,
        water_legacy_value=msil_water_legacy_value,
        clothing_label=msil_clothing_label,
        surface_labels=msil_surface_labels,
        surface_label=msil_surface_label,
        surface_legacy_value=msil_surface_legacy_value,
        mobile=True,
    )
    st.session_state["__next_fc"] = round(float(result.fattore_finale), 2)