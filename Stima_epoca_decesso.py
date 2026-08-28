# -*- coding: utf-8 -*-

from app import i18n
from app.parameters import dati_parametri_aggiuntivi
from app.full_tanatology import (
    FULL_LIVOR_STATE_BY_LABEL,
    FULL_RIGOR_STATE_BY_LABEL,
    FULL_SPECIAL_PARAM_BY_LABEL,
    full_livor_legacy_value,
    full_rigor_legacy_value,
    full_special_parameter_label,
    full_special_parameter_legacy_value,
    full_special_option_labels,
    full_special_option_id,
    full_special_option_legacy_value,
)
from app.special_tanatology_states import (
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_ELECTRICAL_PERIORAL,
    OPTION_NOT_ASSESSED,
)
from app.native_time_picker import native_time_picker
from app.full_factor_panel import pannello_suggerisci_fc
from app.device_mode import full_device_is_mobile
from app.mobile_navigation import render_mobile_page_switch
from app.graphing import aggiorna_grafico

import streamlit as st
import datetime

def _is_num(x):
    try:
        return x is not None and float(x) == float(x)
    except Exception:
        return False

def _build_ta_values_from_ui():
    vals = []
    if st.session_state.get("stima_cautelativa_beta", False) and st.session_state.get("range_unico_beta", False):
        vals.extend([st.session_state.get("Ta_min_beta"), st.session_state.get("Ta_max_beta")])
    else:
        vals.append(st.session_state.get("ta_base_val"))
    vals = [float(v) for v in vals if _is_num(v)]
    return sorted(set(vals))

def _prudente_any_combination_possible(Tr_val, ta_vals):
    """True se esiste almeno una combinazione fisicamente calcolabile (Tr > Ta)."""
    if not _is_num(Tr_val):
        return False
    tv = [float(t) for t in ta_vals if _is_num(t)]
    if not tv:
        return False
    tr = float(Tr_val)
    return any(tr > ta for ta in tv)

# ---------------------------
# Palette / UI helpers
# ---------------------------
def _warn_palette():
    base = st.get_option("theme.base") or "light"
    if base.lower() == "dark":
        return dict(bg="#3b2a00", text="#ffe08a", border="#8a6d1a")
    else:
        return dict(bg="#fff3cd", text="#664d03", border="#ffda6a")

def _warn_box(msg: str):
    pal = _warn_palette()
    st.markdown(
        f'<div style="background:{pal["bg"]};color:{pal["text"]};'
        f'border:1px solid {pal["border"]};border-radius:6px;'
        f'padding:8px 10px;margin:4px 0;font-size:0.92rem;">'
        f'⚠️ {msg}'
        f'</div>',
        unsafe_allow_html=True
    )


# =========================
# Stato e costanti globali
# =========================
st.set_page_config(page_title="Mor-tem", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
.final-text{
  font-family: Arial, sans-serif !important;
  font-size: 10pt !important;
  line-height: 14pt !important;
}
.mortem-section-title {
  margin: 0 0 0.28rem 0 !important;
  padding: 0 !important;
  font-size: 0.86rem !important;
  font-weight: 600 !important;
  line-height: 1.15 !important;
  opacity: 0.82;
}
@media (max-width: 768px) {
  div.block-container { padding-top: 3rem !important; }
  .mortem-full-title {
    margin: 0 !important;
    padding: 0 !important;
    font-size: 1.05rem !important;
    font-weight: 650 !important;
    line-height: 1.05 !important;
  }
  [data-testid="stElementContainer"]:has(.mortem-full-title) {
    margin: 0 0 -0.35rem 0 !important;
    padding: 0 !important;
  }
}
</style>
""", unsafe_allow_html=True)

# Helper: default stabile per ogni widget
def sget(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]

# Defaults iniziali una sola volta
_defaults = {
    "rt_val": None,
    "ta_base_val": 20.0,
    "peso": 70.0,
    "fattore_correzione": 1.0,
    "usa_orario_custom": False,
    "input_data_rilievo": None,
    "input_ora_rilievo": None,
    "stima_cautelativa_beta": False,
    "range_unico_beta": False,
    "peso_stimato_beta": False,
    "toggle_fattore_inline": False,
    "toggle_fattore_inline_std": False,
    "fc_suggested_vals": [],
    # range widgets
    "fc_min_val": 1.00,
    "fc_other_val": 1.00,
    "ta_other_val": 20.0,
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

if "show_results" not in st.session_state:
    st.session_state["show_results"] = False
if "show_img_sopraciliare" not in st.session_state:
    st.session_state["show_img_sopraciliare"] = False
if "show_img_peribuccale" not in st.session_state:
    st.session_state["show_img_peribuccale"] = False

# Titolo
st.markdown(
    f"<h5 class='mortem-full-title' style='margin-top:0; margin-bottom:0;'>{i18n.ui_text('full.title')}</h5>",
    unsafe_allow_html=True,
)

# --- Definizione Widget (Streamlit) ---

# --- Data/Ora ispezione legale ---
with st.container(border=True):
    usa_orario_custom = st.toggle(
        i18n.ui_text("full.add_datetime"),
        key="usa_orario_custom",
    )

    if st.session_state["usa_orario_custom"]:
        if st.session_state.get("input_data_rilievo") is None:
            st.session_state["input_data_rilievo"] = datetime.date.today()
        if not st.session_state.get("input_ora_rilievo"):
            st.session_state["input_ora_rilievo"] = "00:00"

        with st.container(
            horizontal=True,
            horizontal_alignment="left",
            gap="small",
            key="inspection_datetime_row",
        ):
            with st.container(width="stretch", key="inspection_datetime_date"):
                st.date_input(
                    i18n.ui_text("full.inspection_date"),
                    value=st.session_state["input_data_rilievo"],
                    label_visibility="collapsed",
                    key="input_data_rilievo",
                )
            with st.container(width="stretch", key="inspection_datetime_time"):
                selected_time = native_time_picker(
                    st.session_state["input_ora_rilievo"],
                    key="input_ora_rilievo_native",
                    mobile=full_device_is_mobile(),
                )
                st.session_state["input_ora_rilievo"] = selected_time
    else:
        st.session_state["input_data_rilievo"] = None
        st.session_state["input_ora_rilievo"] = None

# Alias locali
input_data_rilievo = st.session_state.get("input_data_rilievo")
input_ora_rilievo  = st.session_state.get("input_ora_rilievo")

# 📌 2. Ipostasi e rigidità — RIQUADRO
full_select_filter_mode = None if full_device_is_mobile() else "fuzzy"
with st.container(border=True):
    col1, col2 = st.columns(2, gap="small")

    livor_labels = list(FULL_LIVOR_STATE_BY_LABEL.keys())
    rigor_labels = list(FULL_RIGOR_STATE_BY_LABEL.keys())

    with col1:
        livor_heading = i18n.ui_text("full.livor_heading")
        st.markdown(f"<div class='mortem-section-title'>{livor_heading}</div>", unsafe_allow_html=True)
        prev_livor = st.session_state.get("selettore_macchie", livor_labels[0])
        if prev_livor not in livor_labels:
            prev_livor = livor_labels[0]
        scelta_macchie_lbl = st.selectbox(
            i18n.ui_text("full.livor_select_label"),
            options=livor_labels,
            index=livor_labels.index(prev_livor),
            key="selettore_macchie_ui",
            label_visibility="collapsed"
        )
        st.session_state["selettore_macchie_id"] = FULL_LIVOR_STATE_BY_LABEL[scelta_macchie_lbl]
        selettore_macchie = full_livor_legacy_value(scelta_macchie_lbl)
        st.session_state["selettore_macchie"] = selettore_macchie

    with col2:
        rigor_heading = i18n.ui_text("full.rigor_heading")
        st.markdown(f"<div class='mortem-section-title'>{rigor_heading}</div>", unsafe_allow_html=True)
        prev_rigor = st.session_state.get("selettore_rigidita", rigor_labels[0])
        if prev_rigor not in rigor_labels:
            prev_rigor = rigor_labels[0]
        scelta_rigidita_lbl = st.selectbox(
            i18n.ui_text("full.rigor_select_label"),
            options=rigor_labels,
            index=rigor_labels.index(prev_rigor),
            key="selettore_rigidita_ui",
            label_visibility="collapsed"
        )
        st.session_state["selettore_rigidita_id"] = FULL_RIGOR_STATE_BY_LABEL[scelta_rigidita_lbl]
        selettore_rigidita = full_rigor_legacy_value(scelta_rigidita_lbl)
        st.session_state["selettore_rigidita"] = selettore_rigidita

# Toggle principale
st.toggle(i18n.ui_text("full.prudent_toggle"), key="stima_cautelativa_beta")
stima_cautelativa_beta = st.session_state["stima_cautelativa_beta"]

# ================================
# 📌 Riquadro raffreddamento (STANDARD o CAUTELATIVA)
# ================================
full_mobile = full_device_is_mobile()
with st.container(border=True):
    if full_mobile:
        with st.container(
            horizontal=True,
            wrap=False,
            horizontal_alignment="distribute",
            vertical_alignment="center",
            gap="small",
            key="cooling_heading_row_mobile",
        ):
            with st.container(width="stretch", key="cooling_heading_title_mobile"):
                st.markdown(
                    f"<div class='mortem-section-title'>{i18n.ui_text('full.henssge_heading')}</div>",
                    unsafe_allow_html=True,
                )
            with st.container(width="content", key="cooling_heading_actions_mobile"):
                henssge_non_app = st.checkbox(
                    i18n.ui_text("full.henssge_not_applicable"),
                    key="henssge_non_applicabile",
                    help=i18n.ui_text("full.henssge_not_applicable_help"),
                )
    else:
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
                    f"<div class='mortem-section-title'>{i18n.ui_text('full.henssge_heading')}</div>",
                    unsafe_allow_html=True,
                )
            with st.container(width="content", key="cooling_heading_actions_desktop"):
                henssge_non_app = st.checkbox(
                    i18n.ui_text("full.henssge_not_applicable"),
                    key="henssge_non_applicabile",
                    help=i18n.ui_text("full.henssge_not_applicable_help"),
                )

    if henssge_non_app:
        # Metodo di Henssge escluso: non mostrare la maschera di input del raffreddamento
        pass

    else:

        # -------------------------
        # 🔶 MASCHERA CAUTELATIVA
        # -------------------------
        if stima_cautelativa_beta:
            rg1, rg2 = st.columns([3, 1], gap="small") if not full_mobile else (None, None)
            if full_mobile:
                st.markdown(
                    i18n.ui_text("full.prudent_default_note"),
                    unsafe_allow_html=True
                )
                range_unico = st.toggle(i18n.ui_text("full.specify_range"), key="range_unico_beta")
            else:
                with rg1:
                    st.markdown(
                        i18n.ui_text("full.prudent_default_note"),
                        unsafe_allow_html=True
                    )
                with rg2:
                    range_unico = st.toggle(i18n.ui_text("full.specify_range"), key="range_unico_beta")

            # Etichette dinamiche
            label_ta = i18n.ui_text("full.ta_mean_label")
            label_fc = i18n.ui_text("full.fc_label")
            if st.session_state.get("range_unico_beta", False):
                label_ta = i18n.ui_text("full.ta_range_label")
                label_fc = i18n.ui_text("full.fc_range_label")

            if full_mobile:
                with st.container(gap="xsmall", key="cooling_prudent_v2_stack_mobile"):
                    st.number_input(
                        "Temperatura rettale",
                        min_value=0.0, max_value=45.0, step=0.1, value=None,
                        placeholder="es. 32.0", key="rt_val", format="%.1f"
                    )
                    st.number_input(
                        "Temperatura ante-mortem",
                        min_value=35.0, max_value=42.0, step=0.1,
                        value=sget("tm_val", 37.2), key="tm_val", format="%.1f"
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
                                "Peso corporeo",
                                min_value=1.0, max_value=250.0, step=0.5,
                                value=float(sget("peso", 70.0)), key="peso", format="%.1f"
                            )
                        with st.container(width="content", key="prudent_weight_toggle_mobile"):
                            st.toggle(
                                i18n.ui_text("full.weight_estimated_toggle"),
                                key="peso_stimato_beta",
                            )

                    ta_base_val = st.number_input(
                        "Temperatura ambientale 1",
                        min_value=-10.0, max_value=50.0, step=0.1,
                        value=float(sget("ta_base_val", 20.0)), key="ta_base_val", format="%.1f"
                    )
                    ta_other_val = st.number_input(
                        "Temperatura ambientale 2",
                        min_value=-10.0, max_value=50.0, step=0.1,
                        value=float(sget("ta_other_val", ta_base_val)), key="ta_other_val", format="%.1f"
                    )

                    fc_min_val = st.number_input(
                        "Fattore di correzione minimo",
                        min_value=0.5, max_value=3.0, step=0.01,
                        value=float(sget("fc_min_val", 1.00)), key="fc_min_val", format="%.2f"
                    )
                    fc_other_val = st.number_input(
                        "Fattore di correzione massimo",
                        min_value=0.5, max_value=3.0, step=0.01,
                        value=float(sget("fc_other_val", fc_min_val)), key="fc_other_val", format="%.2f"
                    )
                    st.toggle(
                        i18n.ui_text("full.suggest_fc"),
                        key="toggle_fattore_inline",
                    )
                    st.session_state["toggle_fattore"] = bool(
                        st.session_state.get("toggle_fattore_inline", False)
                    )

            else:
                # Desktop: stessi controlli V2 della Full mobile, con etichette estese.
                with st.container(gap="xsmall", key="cooling_prudent_v2_stack_desktop"):
                    st.number_input(
                        i18n.ui_text("full.rectal_temp_label"),
                        min_value=0.0, max_value=45.0, step=0.1, value=None,
                        placeholder="es. 32.0", key="rt_val", format="%.1f"
                    )
                    st.number_input(
                        i18n.ui_text("full.ante_mortem_temp_label"),
                        min_value=35.0, max_value=42.0, step=0.1,
                        value=sget("tm_val", 37.2), key="tm_val", format="%.1f"
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
                                min_value=1.0, max_value=250.0, step=0.5,
                                value=float(sget("peso", 70.0)), key="peso", format="%.1f"
                            )
                        with st.container(width="content", key="prudent_weight_toggle_desktop"):
                            st.toggle(
                                i18n.ui_text("full.weight_estimated_toggle"),
                                key="peso_stimato_beta",
                            )

                    ta_base_val = st.number_input(
                        i18n.ui_text("full.ambient_temp_1_label"),
                        min_value=-10.0, max_value=50.0, step=0.1,
                        value=float(sget("ta_base_val", 20.0)), key="ta_base_val", format="%.1f"
                    )
                    ta_other_val = st.number_input(
                        i18n.ui_text("full.ambient_temp_2_label"),
                        min_value=-10.0, max_value=50.0, step=0.1,
                        value=float(sget("ta_other_val", ta_base_val)), key="ta_other_val", format="%.1f"
                    )

                    fc_min_val = st.number_input(
                        i18n.ui_text("full.fc_min_label"),
                        min_value=0.5, max_value=3.0, step=0.01,
                        value=float(sget("fc_min_val", 1.00)), key="fc_min_val", format="%.2f"
                    )
                    fc_other_val = st.number_input(
                        i18n.ui_text("full.fc_max_label"),
                        min_value=0.5, max_value=3.0, step=0.01,
                        value=float(sget("fc_other_val", fc_min_val)), key="fc_other_val", format="%.2f"
                    )
                    st.toggle(
                        i18n.ui_text("full.suggest_fc"),
                        key="toggle_fattore_inline",
                    )
                    st.session_state["toggle_fattore"] = bool(
                        st.session_state.get("toggle_fattore_inline", False)
                    )

            # Sincronizza i range globali
            tmin, tmax = sorted([ta_base_val, ta_other_val])
            fmin, fmax = sorted([fc_min_val, fc_other_val])
            st.session_state["Ta_min_beta"] = tmin
            st.session_state["Ta_max_beta"] = tmax
            st.session_state["FC_min_beta"] = fmin
            st.session_state["FC_max_beta"] = fmax

        # -------------------------
        # 🔹 MASCHERA STANDARD
        # -------------------------
        else:
            if full_mobile:
                with st.container(gap="xsmall", key="cooling_standard_v2_stack_mobile"):
                    st.number_input(
                        "Temperatura rettale",
                        min_value=0.0, max_value=45.0, step=0.1, value=None,
                        placeholder="es. 32.0", key="rt_val", format="%.1f"
                    )
                    st.number_input(
                        "Temperatura ante-mortem",
                        min_value=35.0, max_value=42.0, step=0.1,
                        value=sget("tm_val", 37.2), key="tm_val", format="%.1f"
                    )
                    st.number_input(
                        "Peso corporeo",
                        min_value=1.0, max_value=250.0, step=0.5,
                        value=float(sget("peso", 70.0)), key="peso", format="%.1f"
                    )
                    st.number_input(
                        "Temperatura ambientale",
                        min_value=-10.0, max_value=50.0, step=0.1,
                        value=float(sget("ta_base_val", 20.0)), key="ta_base_val", format="%.1f"
                    )
                    st.number_input(
                        "Fattore di correzione",
                        min_value=0.5, max_value=3.0, step=0.01,
                        value=float(sget("fattore_correzione", 1.0)), key="fattore_correzione", format="%.2f"
                    )
                    st.toggle(i18n.ui_text("full.suggest_fc"), key="toggle_fattore_inline_std")
                    st.session_state["toggle_fattore"] = bool(
                        st.session_state.get("toggle_fattore_inline_std", False)
                    )
            else:
                with st.container(gap="xsmall", key="cooling_standard_v2_stack_desktop"):
                    st.number_input(
                        i18n.ui_text("full.rectal_temp_label"),
                        min_value=0.0, max_value=45.0, step=0.1, value=None,
                        placeholder="es. 32.0", key="rt_val", format="%.1f"
                    )
                    st.number_input(
                        i18n.ui_text("full.ante_mortem_temp_label"),
                        min_value=35.0, max_value=42.0, step=0.1,
                        value=sget("tm_val", 37.2), key="tm_val", format="%.1f"
                    )
                    st.number_input(
                        i18n.ui_text("full.weight_label"),
                        min_value=1.0, max_value=250.0, step=0.5,
                        value=float(sget("peso", 70.0)), key="peso", format="%.1f"
                    )
                    st.number_input(
                        i18n.ui_text("full.ambient_temp_label"),
                        min_value=-10.0, max_value=50.0, step=0.1,
                        value=float(sget("ta_base_val", 20.0)), key="ta_base_val", format="%.1f"
                    )
                    st.number_input(
                        i18n.ui_text("full.fc_label"),
                        min_value=0.5, max_value=3.0, step=0.01,
                        value=float(sget("fattore_correzione", 1.0)), key="fattore_correzione", format="%.2f"
                    )
                    st.toggle(i18n.ui_text("full.suggest_fc"), key="toggle_fattore_inline_std")
                    st.session_state["toggle_fattore"] = bool(
                        st.session_state.get("toggle_fattore_inline_std", False)
                    )

        # Pannello FC (dentro lo stesso riquadro del raffreddamento)
        if st.session_state.get("toggle_fattore", False):
            if full_mobile:
                with st.container(border=False, key="full_fc_panel_mobile"):
                    pannello_suggerisci_fc(
                        peso_default=st.session_state.get("peso", 70.0),
                        key_prefix="fcpanel_caut" if stima_cautelativa_beta else "fcpanel_std",
                    )
            else:
                with st.container(border=True, key="full_fc_panel_desktop"):
                    pannello_suggerisci_fc(
                        peso_default=st.session_state.get("peso", 70.0),
                        key_prefix="fcpanel_caut" if stima_cautelativa_beta else "fcpanel_std",
                    )

# --- Parametri aggiuntivi ---
with st.container(border=True):
    st.markdown(
        f"<div class='mortem-section-title'>{i18n.ui_text('full.additional_parameters_heading')}</div>",
        unsafe_allow_html=True,
    )
    for param_id, opts in dati_parametri_aggiuntivi.items():
        label = full_special_parameter_label(param_id)
        option_labels = full_special_option_labels(param_id)
        current_legacy = st.session_state.get(param_id)
        current_id = st.session_state.get(f"{param_id}_id")
        if current_id is None:
            current_id = OPTION_NOT_ASSESSED
        current_label = next(
            (lbl for lbl in option_labels if full_special_option_id(param_id, lbl) == current_id),
            option_labels[0],
        )
        selected_label = st.selectbox(
            label,
            options=option_labels,
            index=option_labels.index(current_label),
            key=f"{param_id}_ui",
            label_visibility="visible",
            filter_mode=full_select_filter_mode,
        )
        st.session_state[f"{param_id}_id"] = full_special_option_id(param_id, selected_label)
        st.session_state[param_id] = full_special_option_legacy_value(param_id, selected_label)

# --- Calcola / Risultati ---
if st.button(i18n.ui_text("full.calculate"), type="primary", use_container_width=True):
    st.session_state["show_results"] = True

if st.session_state.get("show_results", False):
    aggiorna_grafico()

render_mobile_page_switch(target="msil")
