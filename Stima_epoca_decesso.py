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
from app.native_time_picker import EMPTY_TIME_SENTINEL, native_time_picker
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
  text-align: justify !important;
  text-justify: inter-word !important;
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
    st.markdown(
        "<div class='mortem-section-title'>Data e ora rilievi tanatologici</div>",
        unsafe_allow_html=True,
    )
    # I campi restano sempre visibili. Finché l'ora è vuota, data e ora sono
    # soltanto informative e non vengono applicate alla stima.
    st.session_state["__full_datetime_always_visible"] = True
    st.session_state["usa_orario_custom"] = True
    if st.session_state.get("input_data_rilievo") is None:
        st.session_state["input_data_rilievo"] = datetime.date.today()
    if not st.session_state.get("input_ora_rilievo"):
        st.session_state["input_ora_rilievo"] = EMPTY_TIME_SENTINEL

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
                format="DD/MM/YYYY",
                label_visibility="collapsed",
                key="input_data_rilievo",
            )
        with st.container(width="stretch", key="inspection_datetime_time"):
            selected_time = native_time_picker(
                st.session_state["input_ora_rilievo"],
                key="input_ora_rilievo_native",
            )
            st.session_state["input_ora_rilievo"] = selected_time

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
            label_visibility="collapsed",
            filter_mode=full_select_filter_mode,
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
            label_visibility="collapsed",
            filter_mode=full_select_filter_mode,
        )
        st.session_state["selettore_rigidita_id"] = FULL_RIGOR_STATE_BY_LABEL[scelta_rigidita_lbl]
        selettore_rigidita = full_rigor_legacy_value(scelta_rigidita_lbl)
        st.session_state["selettore_rigidita"] = selettore_rigidita

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
                    f"<div class='mortem-section-title'>{i18n.ui_text('full.cooling_heading')}</div>",
                    unsafe_allow_html=True,
                )
            with st.container(width="content", key="cooling_heading_actions_mobile"):
                henssge_non_app = st.checkbox(
                    i18n.ui_text("full.henssge_not_applicable"),
                    key="henssge_non_applicabile",
                    help=i18n.ui_text("full.henssge_not_applicable_help"),
                )
    else:
        cooling_title_col, cooling_actions_col = st.columns([1, 1], gap="small")
        with cooling_title_col:
            st.markdown(
                f"<div class='mortem-section-title'>{i18n.ui_text('full.cooling_heading')}</div>",
                unsafe_allow_html=True,
            )
        with cooling_actions_col:
            henssge_non_app = st.checkbox(
                i18n.ui_text("full.henssge_not_applicable"),
                key="henssge_non_applicabile",
                help=i18n.ui_text("full.henssge_not_applicable_help"),
            )

    st.toggle(i18n.ui_text("full.prudent_toggle"), key="stima_cautelativa_beta")
    stima_cautelativa_beta = st.session_state["stima_cautelativa_beta"]

    # La modalità con intervalli usa sempre range espliciti. Alla prima attivazione
    # i due estremi coincidono con i valori correnti; nei rerun successivi si
    # conservano invece i valori già inseriti dall'utente.
    if stima_cautelativa_beta:
        if not st.session_state.get("__prudent_explicit_ranges_initialized", False):
            ta_seed = st.session_state.get("ta_base_val", 20.0)
            fc_seed = st.session_state.get("fattore_correzione", 1.0)
            if _is_num(ta_seed):
                st.session_state["ta_other_val"] = float(ta_seed)
            if _is_num(fc_seed):
                st.session_state["fc_min_val"] = float(fc_seed)
                st.session_state["fc_other_val"] = float(fc_seed)
            st.session_state["__prudent_explicit_ranges_initialized"] = True
        st.session_state["range_unico_beta"] = True
    else:
        st.session_state["range_unico_beta"] = False

    if henssge_non_app:
        # Metodo di Henssge escluso: non mostrare la maschera di input del raffreddamento
        pass

    else:

        # -------------------------
        # 🔶 MASCHERA CAUTELATIVA
        # -------------------------
        if stima_cautelativa_beta:
            with st.container(key="prudent_explicit_ranges"):
                st.markdown(
                    i18n.ui_text("full.prudent_default_note"),
                    unsafe_allow_html=True
                )

            label_ta = i18n.ui_text("full.ta_range_label")
            label_fc = i18n.ui_text("full.fc_range_label")

            if full_mobile:
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

        else:
            # -------------------------
            # 🔷 MASCHERA STANDARD
            # -------------------------
            if full_mobile:
                # Su mobile i V2 sono renderizzati direttamente nella pila:
                # nessun vecchio st.columns limita la larghezza disponibile.
                with st.container(gap="xsmall", key="cooling_standard_v2_stack_mobile"):
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
                    st.number_input(
                        i18n.ui_text("full.weight_label"),
                        value=sget("peso", 70.0), step=1.0, format="%.1f",
                        key="peso", label_visibility="collapsed"
                    )
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
                    # Resta montato per conservare lo stesso stato; il CSS mobile
                    # lo nasconde perché il comando Consiglia è integrato nel V2.
                    st.toggle(i18n.ui_text("full.suggest_fc"), key="toggle_fattore_inline_std")
                    st.session_state["toggle_fattore"] = st.session_state.get("toggle_fattore_inline_std", False)
            else:
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

    # --- Pannello "Suggerisci FC" interno al riquadro raffreddamento ---
    if st.session_state.get("toggle_fattore", False):
        with st.container(
            border=False,
            key="full_fc_panel_mobile" if full_mobile else "full_fc_panel_desktop",
        ):
            pannello_suggerisci_fc(
                peso_default=st.session_state.get("peso", 70.0),
                key_prefix="fcpanel_caut" if st.session_state.get("stima_cautelativa_beta", False) else "fcpanel_std"
            )

# Parametri aggiuntivi
mostra_parametri_aggiuntivi = st.checkbox(i18n.ui_text("full.add_special_data"), key="mostra_parametri_aggiuntivi")
widgets_parametri_aggiuntivi = {}

if mostra_parametri_aggiuntivi:
    with st.container(border=True):
        usa_orario_custom_globale = st.session_state.get("usa_orario_custom", False)

        if not usa_orario_custom_globale:
            st.markdown(
                i18n.ui_text("full.special_datetime_hint"),
                unsafe_allow_html=True
            )

        for parametro_id in FULL_SPECIAL_PARAM_BY_LABEL.values():
            nome_parametro = full_special_parameter_label(parametro_id)
            nome_parametro_legacy = full_special_parameter_legacy_value(parametro_id)
            dati_parametro = dati_parametri_aggiuntivi[nome_parametro_legacy]
            col1, col2 = st.columns([1, 2], gap="small")

            with col1:
                subcol1, subcol2 = st.columns([1, 0.5])
                with subcol1:
                    st.markdown(
                        f"<div style='font-size: 0.88rem; padding-top: 0.4rem;'>{nome_parametro}:</div>",
                        unsafe_allow_html=True
                    )
                with subcol2:
                    if parametro_id in {PARAM_ELECTRICAL_SUPRACILIARY, PARAM_ELECTRICAL_PERIORAL}:
                        with st.popover(" "):
                            if parametro_id == PARAM_ELECTRICAL_SUPRACILIARY:
                                st.image(
                                    "https://raw.githubusercontent.com/scopusjin/codice/main/immagini/eccitabilit%C3%A0.PNG",
                                    width=400
                                )
                            elif parametro_id == PARAM_ELECTRICAL_PERIORAL:
                                st.image(
                                    "https://raw.githubusercontent.com/scopusjin/codice/main/immagini/peribuccale.PNG",
                                    width=300
                                )

            with col2:
                selettore = st.selectbox(
                    label=nome_parametro,
                    options=list(full_special_option_labels(parametro_id)),
                    key=f"{nome_parametro_legacy}_selector",
                    label_visibility="collapsed"
                )
                selettore_id = full_special_option_id(parametro_id, selettore)
                selettore_legacy = full_special_option_legacy_value(parametro_id, selettore)
                st.session_state[f"special_{parametro_id}_id"] = selettore_id

            data_picker = None
            ora_input = None
            usa_orario_personalizzato = False

            if selettore_id != OPTION_NOT_ASSESSED and usa_orario_custom_globale:
                chiave_checkbox = f"{nome_parametro_legacy}_diversa"
                colx1, colx2 = st.columns([0.75, 0.25], gap="small")
                with colx1:
                    st.markdown(
                        "<div style='font-size: 0.8em; color: orange; margin-bottom: 3px;'>"
                        f"{i18n.ui_text('full.assessed_different_time')}"
                        "</div>",
                        unsafe_allow_html=True
                    )
                with colx2:
                    usa_orario_personalizzato = st.checkbox(label="", key=chiave_checkbox)

            ora_key = f"{nome_parametro_legacy}_ora"
            ora_manual_key = f"{ora_key}__manual"
            ora_last_main_key = f"{ora_key}__last_main"
            if not usa_orario_personalizzato:
                st.session_state.pop(ora_manual_key, None)
                st.session_state.pop(ora_last_main_key, None)

            if usa_orario_custom_globale and usa_orario_personalizzato:
                coly1, coly2 = st.columns(2)
                with coly1:
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
                    ora_main = input_ora_rilievo or "00:00"
                    ora_manual = bool(st.session_state.get(ora_manual_key, False))
                    ora_value = (
                        (st.session_state.get(ora_key) or ora_main)
                        if ora_manual
                        else ora_main
                    )
                    ora_picker = native_time_picker(
                        ora_value,
                        key=f"{ora_key}_native",
                        inherited=not ora_manual,
                    )

                    if ora_manual:
                        ora_input = ora_picker
                    else:
                        ora_last_main = st.session_state.get(ora_last_main_key)
                        if ora_last_main is None:
                            # Primo render (o riattivazione): ignora un eventuale
                            # valore residuo del componente e parti dall'orario principale.
                            ora_input = ora_main
                        elif ora_main != ora_last_main and ora_picker == ora_last_main:
                            # Dopo un cambio programmatico del principale il componente
                            # può restituire per un singolo rerun il vecchio valore.
                            ora_input = ora_main
                        elif ora_picker != ora_main:
                            # Da questo momento il valore è stato modificato localmente
                            # e non deve più seguire l'orario principale.
                            st.session_state[ora_manual_key] = True
                            ora_input = ora_picker
                        else:
                            ora_input = ora_main
                        st.session_state[ora_last_main_key] = ora_main

                    st.session_state[ora_key] = ora_input

            widgets_parametri_aggiuntivi[nome_parametro_legacy] = {
                "selettore": selettore_legacy,
                "data_rilievo": data_picker,
                "ora_rilievo": ora_input
            }

        chk_putrefattive = st.checkbox(i18n.ui_text("full.putrefactive_changes"), value=st.session_state.get("alterazioni_putrefattive", False))
        st.session_state["alterazioni_putrefattive"] = chk_putrefattive
else:
    st.session_state["alterazioni_putrefattive"] = False

def _inputs_signature():
    import numpy as np
    import datetime as _dt
    import streamlit as st

    def _freeze(v):
        if v is None or isinstance(v, bool):
            return v
        if isinstance(v, (np.floating,)):
            return float(v)
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, (_dt.date, _dt.datetime, _dt.time)):
            try:
                return v.isoformat()
            except Exception:
                return str(v)
        if isinstance(v, (list, tuple)):
            return tuple(_freeze(x) for x in v)
        if isinstance(v, dict):
            return tuple(sorted((k, _freeze(val)) for k, val in v.items()))
        return str(v)

    base = [
        bool(st.session_state.get("usa_orario_custom", False)),
        bool(st.session_state.get("mostra_parametri_aggiuntivi", False)),
        bool(st.session_state.get("henssge_non_applicabile", False)),
        _freeze(st.session_state.get("input_data_rilievo")),
        _freeze(st.session_state.get("input_ora_rilievo")),
        _freeze(st.session_state.get("selettore_macchie") if "selettore_macchie" in st.session_state else None),
        _freeze(st.session_state.get("selettore_rigidita") if "selettore_rigidita" in st.session_state else None),
        _freeze(st.session_state.get("rt_val")),
        _freeze(st.session_state.get("ta_base_val") if "ta_base_val" in st.session_state else None),
        _freeze(st.session_state.get("tm_val")),
        _freeze(st.session_state.get("peso")),
        _freeze(st.session_state.get("fattore_correzione", 1.0)),
        bool(st.session_state.get("alterazioni_putrefattive", False)),
        bool(st.session_state.get("stima_cautelativa_beta", False)),
    ]

    try:
        from app.parameters import dati_parametri_aggiuntivi
        extra = []
        for nome_parametro, _ in dati_parametri_aggiuntivi.items():
            extra.append(_freeze(st.session_state.get(f"{nome_parametro}_selector")))
            extra.append(_freeze(st.session_state.get(f"{nome_parametro}_diversa")))
            extra.append(_freeze(st.session_state.get(f"{nome_parametro}_data")))
            extra.append(_freeze(st.session_state.get(f"{nome_parametro}_ora")))
    except Exception:
        extra = []

    caut = [
        _freeze(st.session_state.get("Ta_min_beta")),
        _freeze(st.session_state.get("Ta_max_beta")),
        _freeze(st.session_state.get("FC_min_beta")),
        _freeze(st.session_state.get("FC_max_beta")),
        bool(st.session_state.get("peso_stimato_beta", False)),
        bool(st.session_state.get("range_unico_beta", False)),
        _freeze(st.session_state.get("ta_other_val")),
        _freeze(st.session_state.get("fc_other_val")),
        tuple(sorted(_freeze(st.session_state.get("fc_suggested_vals", [])))),
    ]

    return tuple(_freeze(base + extra + caut))

# --- Firma degli input che influenzano la stima ---
curr_sig = _inputs_signature()

# Stato iniziale sicuro
if "last_run_sig" not in st.session_state:
    st.session_state["last_run_sig"] = None
if "show_results" not in st.session_state:
    st.session_state["show_results"] = False

# Stile bottone
st.markdown("""
    <style>
    div.stButton > button {
        border: 2px solid #2196F3 !important;
        color: black !important;
        background-color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
        padding: 0.6em 2em !important;
    }
    div.stButton > button:hover { background-color: #E3F2FD !important; cursor: pointer; }
    </style>
""", unsafe_allow_html=True)

# --- Bottone: esegue il calcolo SOLO su click ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(i18n.ui_text("full.estimate_button"), key="btn_stima"):
        st.session_state["last_run_sig"] = curr_sig
        st.session_state["show_results"] = True

# --- Se QUALSIASI input cambia: nascondi risultati (NON ricalcolare) ---
if st.session_state["show_results"] and st.session_state["last_run_sig"] != curr_sig:
    st.session_state["show_results"] = False

# --- Mostra risultati SOLO se richiesti e firma invariata ---
if st.session_state["show_results"]:
    input_rt = st.session_state.get("rt_val")
    input_ta = st.session_state.get("ta_base_val")
    input_tm = st.session_state.get("tm_val")
    input_w  = st.session_state.get("peso")

    no_rt = (input_rt is None) or (isinstance(input_rt, (int, float)) and input_rt <= 0)
    no_macchie = str(selettore_macchie).strip() in {"Non valutata", "Non valutate", "/"}
    no_rigidita = str(selettore_rigidita).strip() in {"Non valutata", "Non valutate", "/"}
    ha_parametro_aggiuntivo_stimabile = any(
        isinstance(
            dati_parametri_aggiuntivi.get(nome_parametro, {})
            .get("range", {})
            .get((widgets or {}).get("selettore")),
            tuple,
        )
        for nome_parametro, widgets in widgets_parametri_aggiuntivi.items()
    )

    if no_rt and no_macchie and no_rigidita and not ha_parametro_aggiuntivo_stimabile:
        with st.container(key="mortem_no_data_box"):
            st.warning(i18n.ui_text("full.no_data_warning"))
        st.stop()

    base_ok = (
        not st.session_state.get("henssge_non_applicabile", False) and
        not no_rt and
        input_ta is not None and
        input_tm is not None and
        input_w  is not None and input_w > 0
    )

    prudente_ok = True
    if base_ok and st.session_state.get("stima_cautelativa_beta", False):
        ta_vals = _build_ta_values_from_ui()
        if not ta_vals and _is_num(input_ta):
            ta_vals = [float(input_ta)]
        prudente_ok = _prudente_any_combination_possible(input_rt, ta_vals)
        if not prudente_ok:
            _warn_box(i18n.ui_text("full.henssge_incoherent_warning"))

    considera_raffreddamento = base_ok and (
        not st.session_state.get("stima_cautelativa_beta", False) or prudente_ok
    )

    aggiorna_grafico(
        selettore_macchie=selettore_macchie,
        selettore_rigidita=selettore_rigidita,
        input_rt=(input_rt if considera_raffreddamento else None),
        input_ta=(input_ta if considera_raffreddamento else None),
        input_tm=(input_tm if considera_raffreddamento else None),
        input_w=(input_w if considera_raffreddamento else None),
        fattore_correzione=st.session_state.get("fattore_correzione", 1.0),
        widgets_parametri_aggiuntivi=widgets_parametri_aggiuntivi,
        usa_orario_custom=st.session_state.get("usa_orario_custom", False),
        input_data_rilievo=st.session_state.get("input_data_rilievo"),
        input_ora_rilievo=st.session_state.get("input_ora_rilievo"),
        alterazioni_putrefattive=st.session_state.get("alterazioni_putrefattive", False),
        skip_warnings=True,
    )

render_mobile_page_switch(
    "Modalità sopralluogo",
    "pages/App_MSIL.py",
    "mobile_nav_footer_to_msil",
)
