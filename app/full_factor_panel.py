# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st

from app import i18n
from app.data_sources import load_tabelle_correzione
from app.device_mode import full_device_is_mobile
from app.factor_calc import DressCounts, compute_factor, fattore_vestiti_coperte
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


def _fc_palette():
    base = st.get_option("theme.base") or "light"
    if base.lower() == "dark":
        return dict(bg="#0d2a47", text="#d6e9ff", border="#1976d2", note="#a7c7ff")
    else:
        return dict(bg="#e8f0fe", text="#0d47a1", border="#1976d2", note="#3f6fb5")
            

def _fc_box(f_finale: float, f_base: float | None, peso_corrente: float | None):
    pal = _fc_palette()
    main = (
        f'<div style="background:{pal["bg"]};color:{pal["text"]};'
        f'border:1px solid {pal["border"]};border-radius:8px;'
        f'padding:10px;font-weight:600;">'
        f'{i18n.ui_text("full.fc_suggested", value=f_finale)}'
        f'</div>'
    )
    side = ""
    if f_base is not None and peso_corrente is not None and abs(f_finale - f_base) > 1e-9:
        side = (
            f'<div style="color:{pal["note"]};padding:10px 2px 0 2px;font-size:0.92em;">'
            f'{i18n.ui_text("full.fc_adjusted_for_weight", weight=peso_corrente, base=f_base)}'
            f'</div>'
        )
    st.markdown(main + side, unsafe_allow_html=True)


def _sync_fc_range_from_suggestions():
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


def clear_fc_suggestions_global() -> None:
    st.session_state["fc_suggested_vals"] = []


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


_FULL_MOBILE_SURFACE_PLACEHOLDER = "Superficie di appoggio"


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
    stato_label = st.radio("" if mobile else "dummy", list(body_labels()), **radio_kwargs)
    stato_corpo = body_legacy_value(stato_label)

    tabella2_mobile = _load_factor_table() if mobile else None
    peso_eff = _panel_weight(peso_default, True) if mobile else None

    if stato_corpo == "Immerso":
        acqua_kwargs = dict(index=0, horizontal=True, key=k("radio_acqua"))
        if mobile:
            acqua_kwargs["label_visibility"] = "collapsed"
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

    if full_mobile:
        # Streamlit 1.62 permette una vera riga orizzontale non spezzabile.
        # Le stesse chiavi di stato restano usate anche su desktop.
        st.markdown(
            f"""
            <style>
            @media (max-width: 768px) {{
              [class*="st-key-{key_prefix}_switch_row"][data-testid="stHorizontalBlock"],
              [class*="st-key-{key_prefix}_switch_row"] [data-testid="stHorizontalBlock"] {{
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                align-items: center !important;
                gap: 0.5rem !important;
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
            gap="xsmall",
            key=k("switch_row"),
        ):
            with st.container(width="content", key=k("vest_slot")):
                toggle_vestito = st.toggle(
                    "Vestiti/coperte",
                    key=k("toggle_vestito"), value=False
                )
            with st.container(width="content", key=k("corr_slot")):
                corr_placeholder = st.empty()
    elif mobile:
        col_corr, col_vest = st.columns([1.0, 1.3], gap="small")
        with col_corr:
            corr_placeholder = st.empty()
        with col_vest:
            toggle_vestito = st.toggle(
                i18n.ui_text("msil.clothed_covered"),
                value=st.session_state.get(k("toggle_vestito"), False),
                key=k("toggle_vestito")
            )
    else:
        col_corr, col_vest = st.columns([1.0, 1.3])
        with col_corr:
            corr_placeholder = st.empty()
        with col_vest:
            toggle_vestito = st.toggle(
                i18n.ui_text("full.clothed_covered"),
                key=k("toggle_vestito"), value=False
            )

    n_sottili = n_spessi = n_cop_medie = n_cop_pesanti = 0
    if toggle_vestito:
        label_sottili = clothing_label(LAYER_THIN)
        label_spessi = clothing_label(LAYER_THICK)
        label_coperte_medie = clothing_label(BLANKET_MEDIUM)
        label_coperte_pesanti = clothing_label(BLANKET_HEAVY)

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

        select_options = options_display
        if full_mobile:
            select_options = [_FULL_MOBILE_SURFACE_PLACEHOLDER, *options_display]

        prev_display = st.session_state.get(k("superficie_display_sel"))
        if prev_display not in select_options:
            prev_display = _FULL_MOBILE_SURFACE_PLACEHOLDER if full_mobile else options_display[0]

        select_kwargs = dict(
            index=select_options.index(prev_display),
            key=k("superficie_display_sel")
        )
        if mobile:
            select_kwargs["label_visibility"] = "visible"
        elif full_mobile:
            select_kwargs["label_visibility"] = "collapsed"
            select_kwargs["format_func"] = _full_mobile_surface_caption

        superficie_display_label = st.selectbox(
            i18n.ui_text(f"{scope}.support_surface"),
            select_options,
            **select_kwargs
        )
        if full_mobile and superficie_display_label == _FULL_MOBILE_SURFACE_PLACEHOLDER:
            # Placeholder neutro: nessun effetto proprio della superficie.
            # Per le correnti mantiene la stessa classe INDIFFERENTE del
            # precedente default (prima superficie dell'elenco).
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
                "Correnti d'aria" if full_mobile else i18n.ui_text(f"{scope}.air_currents"),
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
    if full_mobile and surface_placeholder_selected:
        result.riassunto["superficie"] = "/"
    return result, peso_eff, False


# --- Pannello “Suggerisci FC”
def pannello_suggerisci_fc(peso_default: float = 70.0, key_prefix: str = "fcpanel"):
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
        full_mobile=full_device_is_mobile(),
    )

    _fc_box(result.fattore_finale, result.fattore_base, peso_eff)

    def _apply_fc(val: float, riass: str | None) -> None:
        st.session_state["fattore_correzione"] = round(float(val), 2)
        st.session_state["fattori_condizioni_parentetica"] = None
        st.session_state["fattori_condizioni_testo"] = None
        st.session_state["toggle_fattore"] = False
        st.session_state["fc_riassunto_contatori"] = riass

    suffix = "_imm" if immersed else ""
    if not st.session_state.get("range_unico_beta", False):
        st.button(
            i18n.ui_text("full.use_this_factor"),
            on_click=_apply_fc, args=(result.fattore_finale, result.riassunto),
            use_container_width=True, key=f"{key_prefix}_btn_usa_fc{suffix}"
        )

    if st.session_state.get("stima_cautelativa_beta", False):
        st.button(
            i18n.ui_text("full.add_to_fc_range"),
            use_container_width=True, on_click=add_fc_suggestion_global,
            args=(result.fattore_finale,), key=f"{key_prefix}_btn_add_fc{suffix}"
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
