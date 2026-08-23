# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st

from app import i18n
from app.data_sources import load_tabelle_correzione
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
    vals = st.session_state.get("fc_suggested_vals", [])
    vals = sorted({*vals, v})
    if len(vals) >= 3:
        vals = [vals[0], vals[-1]]
    st.session_state["fc_suggested_vals"] = vals
    _sync_fc_range_from_suggestions()


def clear_fc_suggestions_global() -> None:
    st.session_state["fc_suggested_vals"] = []


# --- Pannello “Suggerisci FC”
def pannello_suggerisci_fc(peso_default: float = 70.0, key_prefix: str = "fcpanel"):
    import streamlit as st

    def k(name: str) -> str:
        return f"{key_prefix}_{name}"

    def _apply_fc(val: float, riass: str | None) -> None:
        st.session_state["fattore_correzione"] = round(float(val), 2)
        st.session_state["fattori_condizioni_parentetica"] = None
        st.session_state["fattori_condizioni_testo"] = None
        st.session_state["toggle_fattore"] = False
        st.session_state["fc_riassunto_contatori"] = riass

    # --- CSS compatto ---
    st.markdown("""
        <style>
          div[data-testid="stRadio"] > label {display:none !important;}
          div[data-testid="stRadio"] {margin-top:-14px; margin-bottom:-10px;}
          div[data-testid="stRadio"] div[role="radiogroup"] {gap:0.4rem;}
          div[data-testid="stToggle"] {margin-top:-6px; margin-bottom:-6px;}
          div[data-testid="stSlider"] {margin-top:-4px; margin-bottom:-2px;}
        </style>
    """, unsafe_allow_html=True)
    # --- Stato corpo ---
    stato_label = st.radio("dummy", list(full_body_labels()), index=0, horizontal=True, key=k("radio_stato_corpo"))
    stato_corpo = full_body_legacy_value(stato_label)

    # ============== Immerso ==============
    if stato_corpo == "Immerso":
        acqua_label = st.radio("dummy", list(full_water_labels()), index=0, horizontal=True, key=k("radio_acqua"))
        acqua_mode = full_water_legacy_value(acqua_label)

        try:
            tabella2 = load_tabelle_correzione()
        except Exception:
            tabella2 = None

        result = compute_factor(
            stato="Immerso", acqua=acqua_mode, counts=DressCounts(),
            superficie_display=None, correnti_aria=False,
            peso=float(st.session_state.get("peso", peso_default)),
            tabella2_df=tabella2
        )
        _fc_box(result.fattore_finale, result.fattore_base, float(st.session_state.get("peso", peso_default)))

        if not st.session_state.get("range_unico_beta", False):
            st.button(i18n.ui_text("full.use_this_factor"), on_click=_apply_fc, args=(result.fattore_finale, result.riassunto),
                      use_container_width=True, key=k("btn_usa_fc_imm"))

        if st.session_state.get("stima_cautelativa_beta", False):
            st.button(i18n.ui_text("full.add_to_fc_range"), use_container_width=True, on_click=add_fc_suggestion_global,
                      args=(result.fattore_finale,), key=k("btn_add_fc_imm"))
        return

    # ============== Asciutto / Bagnato ==============
    col_corr, col_vest = st.columns([1.0, 1.3])
    with col_corr:
        corr_placeholder = st.empty()
    with col_vest:
        toggle_vestito = st.toggle(i18n.ui_text("full.clothed_covered"), key=k("toggle_vestito"), value=False)

    n_sottili = n_spessi = n_cop_medie = n_cop_pesanti = 0
    if toggle_vestito:
        label_sottili = full_clothing_label(LAYER_THIN)
        label_spessi = full_clothing_label(LAYER_THICK)
        label_coperte_medie = full_clothing_label(BLANKET_MEDIUM)
        label_coperte_pesanti = full_clothing_label(BLANKET_HEAVY)

        count_col = i18n.ui_text("full.count_column")
        defaults = {
            label_sottili: st.session_state.get(k("strati_sottili"), 0),
            label_spessi: st.session_state.get(k("strati_spessi"), 0),
        }
        if stato_corpo == "Asciutto":
            defaults.update({
                label_coperte_medie: st.session_state.get(k("coperte_medie"), 0),
                label_coperte_pesanti: st.session_state.get(k("coperte_pesanti"), 0),
            })

        rows = [{"--": nome, count_col: val} for nome, val in defaults.items()]
        df = pd.DataFrame(rows)
        st.markdown("""
        <style>
        [data-testid="stDataFrameContainer"] thead {display: none;}
        [data-testid="stElementToolbar"] {display: none;}
        [data-testid="stDataFrameContainer"] tbody th {display: none;}
        </style>
        """, unsafe_allow_html=True)
        
        edited = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "--": st.column_config.TextColumn(disabled=True, width="medium"),
                count_col: st.column_config.NumberColumn(min_value=0, max_value=8, step=1, width="small"),
            },
        )

        vals = {r["--"]: int(r[count_col] or 0) for _, r in edited.iterrows()}

        n_sottili = vals.get(label_sottili, 0)
        n_spessi = vals.get(label_spessi, 0)
        n_cop_medie = vals.get(label_coperte_medie, 0) if stato_corpo == "Asciutto" else 0
        n_cop_pesanti = vals.get(label_coperte_pesanti, 0) if stato_corpo == "Asciutto" else 0

    counts = DressCounts(sottili=n_sottili, spessi=n_spessi, coperte_medie=n_cop_medie, coperte_pesanti=n_cop_pesanti)

    superficie_display_selected = "/"
    if stato_corpo == "Asciutto":
        nudo_eff = ((not toggle_vestito) or (counts.sottili == counts.spessi == counts.coperte_medie == counts.coperte_pesanti == 0))
        options_display = list(full_surface_labels())
        if not nudo_eff:
            excluded_surface = full_surface_label(SURFACE_THICK_METAL_OUTDOOR)
            options_display = [o for o in options_display if o != excluded_surface]
        prev_display = st.session_state.get(k("superficie_display_sel"))
        if prev_display not in options_display:
            prev_display = options_display[0]
        superficie_display_label = st.selectbox(i18n.ui_text("full.support_surface"), options_display,
                                                 index=options_display.index(prev_display), key=k("superficie_display_sel"))
        superficie_display_selected = full_surface_legacy_value(superficie_display_label)

    correnti_presenti = False
    with corr_placeholder.container():
        mostra_correnti = True
        if stato_corpo == "Asciutto":
            from app.factor_calc import fattore_vestiti_coperte
            f_vc = fattore_vestiti_coperte(counts)
            if f_vc >= 1.2:
                mostra_correnti = False
        if mostra_correnti:
            correnti_presenti = st.toggle(i18n.ui_text("full.air_currents"), key=k("toggle_correnti_fc"), disabled=False)

    try:
        tabella2 = load_tabelle_correzione()
    except Exception:
        tabella2 = None

    result = compute_factor(
        stato=stato_corpo, acqua=None, counts=counts,
        superficie_display=superficie_display_selected if stato_corpo == "Asciutto" else None,
        correnti_aria=correnti_presenti,
        peso=float(st.session_state.get("peso", peso_default)),
        tabella2_df=tabella2
    )
    _fc_box(result.fattore_finale, result.fattore_base, float(st.session_state.get("peso", peso_default)))

    if not st.session_state.get("range_unico_beta", False):
        st.button(i18n.ui_text("full.use_this_factor"), on_click=_apply_fc, args=(result.fattore_finale, result.riassunto),
                  use_container_width=True, key=k("btn_usa_fc"))

    if st.session_state.get("stima_cautelativa_beta", False):
        st.button(i18n.ui_text("full.add_to_fc_range"), use_container_width=True, on_click=add_fc_suggestion_global,
                  args=(result.fattore_finale,), key=k("btn_add_fc"))
