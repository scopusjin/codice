# -*- coding: utf-8 -*-

from app.factor_calc import (
    DressCounts, compute_factor, build_cf_description,
    SURF_DISPLAY_ORDER, fattore_vestiti_coperte,
)

from app.henssge import (
    calcola_raffreddamento,
    ranges_in_disaccordo_completa,
    INF_HOURS as INF_HOURS_HENSSGE,
)
from app.utils_time import (
    arrotonda_quarto_dora,
    split_hours_minutes as _split_hours_minutes,
    round_quarter_hour,
)

from app.parameters import (
    INF_HOURS,
    opzioni_macchie, macchie_medi, testi_macchie,
    opzioni_rigidita, rigidita_medi, rigidita_descrizioni,
    dati_parametri_aggiuntivi, nomi_brevi,
)

from app.data_sources import load_tabelle_correzione
from app.plotting import compute_plot_data, render_ranges_plot
from app.textgen import (
    build_final_sentence,
    paragrafo_raffreddamento_dettaglio,
    paragrafo_potente,
    paragrafo_raffreddamento_input,
    paragrafi_descrizioni_base,
    paragrafi_parametri_aggiuntivi,
    paragrafo_putrefattive,
    frase_riepilogo_parametri_usati,
    avvisi_raffreddamento_henssge,
    frase_qd,
    build_simple_sentence, 
    build_final_sentence_simple,        
    build_simple_sentence_no_dt,        
)

from app.cautelativa import compute_raffreddamento_cautelativo
from app.graphing import aggiorna_grafico  # in cima al file

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd
import math

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

def _build_fc_values_from_ui():
    vals = []
    if st.session_state.get("stima_cautelativa_beta", False) and st.session_state.get("range_unico_beta", False):
        vals.extend([st.session_state.get("FC_min_beta"), st.session_state.get("FC_max_beta")])
    else:
        vals.append(st.session_state.get("fattore_correzione", 1.0))
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
        f'Fattore di correzione suggerito: {f_finale:.2f}'
        f'</div>'
    )
    side = ""
    if f_base is not None and peso_corrente is not None and abs(f_finale - f_base) > 1e-9:
        side = (
            f'<div style="color:{pal["note"]};padding:10px 2px 0 2px;font-size:0.92em;">'
            f'Adattato per {peso_corrente:.1f} kg (valore per 70 kg: {f_base:.2f})'
            f'</div>'
        )
    st.markdown(main + side, unsafe_allow_html=True)

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
</style>
""", unsafe_allow_html=True)

def _wrap_final(s: str | None) -> str | None:
    return f'<div class="final-text">{s}</div>' if s else s

# Helper: default stabile per ogni widget
def sget(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]

# Defaults iniziali una sola volta
_defaults = {
    "rt_val": None,
    "tm_val": 37.2,
    "ta_base_val": 20.0,
    "peso": 70.0,
    "fattore_correzione": 1.0,
    "usa_orario_custom": False,
    "input_data_rilievo": None,
    "input_ora_rilievo": None,
    "stima_cautelativa_beta": True,
    "range_unico_beta": False,
    "peso_stimato_beta": False,
    "toggle_fattore_inline": False,
    "toggle_fattore_inline_std": False,
    "fc_suggested_vals": [],
    # range widgets
    "fc_min_val": 0.90,
    "fc_other_val": 1.10,
    "ta_other_val": 21.0,
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

if "show_results" not in st.session_state:
    st.session_state["show_results"] = False
if "show_img_sopraciliare" not in st.session_state:
    st.session_state["show_img_sopraciliare"] = False
if "show_img_peribuccale" not in st.session_state:
    st.session_state["show_img_peribuccale"] = False

# --- INIT per cautelativa: intervallo FC proposto dal pannello "Suggerisci FC"
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

# Titolo
st.markdown("<h5 style='margin-top:0; margin-bottom:10px;'>STIMA EPOCA DECESSO</h5>", unsafe_allow_html=True)

# --- Definizione Widget (Streamlit) ---

# --- Data/Ora ispezione legale ---
with st.container(border=True):
    usa_orario_custom = st.toggle(
        "Aggiungi data/ora rilievi tanatologici",
        key="usa_orario_custom",
    )

    if st.session_state["usa_orario_custom"]:
        if st.session_state.get("input_data_rilievo") is None:
            st.session_state["input_data_rilievo"] = datetime.date.today()
        if not st.session_state.get("input_ora_rilievo"):
            st.session_state["input_ora_rilievo"] = "00:00"

        col1, col2 = st.columns(2, gap="small")
        with col1:
            st.date_input(
                "Data ispezione legale:",
                value=st.session_state["input_data_rilievo"],
                label_visibility="collapsed",
                key="input_data_rilievo",
            )
        with col2:
            st.text_input(
                "Ora ispezione legale (HH:MM):",
                value=st.session_state["input_ora_rilievo"],
                label_visibility="collapsed",
                key="input_ora_rilievo",
            )
    else:
        st.session_state["input_data_rilievo"] = None
        st.session_state["input_ora_rilievo"] = None

# Alias locali
input_data_rilievo = st.session_state.get("input_data_rilievo")
input_ora_rilievo  = st.session_state.get("input_ora_rilievo")

# 📌 2. Ipostasi e rigidità — RIQUADRO
with st.container(border=True):
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>Ipostasi:</div>", unsafe_allow_html=True)
        selettore_macchie = st.selectbox(
            "Macchie ipostatiche:",
            options=list(opzioni_macchie.keys()),
            index=list(opzioni_macchie.keys()).index(sget("selettore_macchie", list(opzioni_macchie.keys())[0])) if "selettore_macchie" in st.session_state else 0,
            key="selettore_macchie",
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("<div style='font-size: 0.88rem;'>Rigidità cadaverica:</div>", unsafe_allow_html=True)
        selettore_rigidita = st.selectbox(
            "Rigidità cadaverica:",
            options=list(opzioni_rigidita.keys()),
            index=list(opzioni_rigidita.keys()).index(sget("selettore_rigidita", list(opzioni_rigidita.keys())[0])) if "selettore_rigidita" in st.session_state else 0,
            key="selettore_rigidita",
            label_visibility="collapsed"
        )

# Toggle principale
st.toggle("Stima prudente", key="stima_cautelativa_beta")
stima_cautelativa_beta = st.session_state["stima_cautelativa_beta"]

# ================================
# 📌 Riquadro raffreddamento (STANDARD o CAUTELATIVA)
# ================================
with st.container(border=True):

    if stima_cautelativa_beta:
        # -------------------------
        # 🔶 MASCHERA CAUTELATIVA
        # -------------------------
        rg1, rg2 = st.columns([3, 1], gap="small")
        with rg1:
            st.markdown(
                "<div style='font-size:0.9rem; color:#444; padding:6px 8px; "
                "border-left:4px solid #bbb; background:#f7f7f7; margin-bottom:8px;'>"
                "Se non diversamente specificato, si considererà "
                "un range di incertezza di ±1.0 °C per la T. ambientale media "
                "e di ±0.10 per il fattore di correzione."
                "</div>",
                unsafe_allow_html=True
            )

        with rg2:
            range_unico = st.toggle("Specifica range", key="range_unico_beta")

        # Etichette dinamiche
        label_ta = "T. ambientale media (°C):"
        label_fc = "Fattore di correzione (FC):"
        if st.session_state.get("range_unico_beta", False):
            label_ta = "Range di T. ambientale media (°C):"
            label_fc = "Range del fattore di correzione (FC):"

        # Riga 1: T. rettale, T. ante-mortem, Peso + switch ±3 kg
        c1, c2, c3 = st.columns([1, 1, 1.6], gap="small")
        with c1:
            st.markdown("<div style='font-size: 0.88rem;'>T. rettale (°C):</div>", unsafe_allow_html=True)
            st.number_input("T. rettale (°C):",
                            value=sget("rt_val", 35.0), step=0.1, format="%.1f",
                            key="rt_val", label_visibility="collapsed")
        with c2:
            st.markdown("<div style='font-size: 0.88rem;'>T. ante-mortem (°C):</div>", unsafe_allow_html=True)
            st.number_input("T. ante-mortem stimata (°C):",
                            value=sget("tm_val", 37.2), step=0.1, format="%.1f",
                            key="tm_val", label_visibility="collapsed")
        with c3:
            st.markdown("<div style='font-size: 0.88rem;'>Peso (kg):</div>", unsafe_allow_html=True)
            pc1, pc2 = st.columns([1, 0.8], gap="small")
            with pc1:
                st.number_input("Peso (kg):",
                                value=sget("peso", 70.0), step=1.0, format="%.1f",
                                key="peso", label_visibility="collapsed")
            with pc2:
                st.toggle("±3 kg", key="peso_stimato_beta")

        # Riga 2: T. ambientale media + range unico
        st.markdown(f"<div style='font-size: 0.88rem;'>{label_ta}</div>", unsafe_allow_html=True)
        ta_c1, ta_c2, ta_c3 = st.columns([1, 1, 1.6], gap="small")
        with ta_c1:
            ta_base_val = st.number_input(
                "TA base",
                value=sget("ta_base_val", 20.0),
                step=0.1, format="%.1f",
                key="ta_base_val",
                label_visibility="collapsed"
            )
        with ta_c2:
            if st.session_state.get("range_unico_beta", False):
                ta_other_val = st.number_input(
                    "TA altro estremo",
                    value=sget("ta_other_val", ta_base_val + 1.0),
                    step=0.1, format="%.1f",
                    key="ta_other_val",
                    label_visibility="collapsed"
                )
                lo_ta, hi_ta = sorted([float(st.session_state["ta_base_val"]), float(st.session_state["ta_other_val"])])
                st.session_state["Ta_min_beta"], st.session_state["Ta_max_beta"] = lo_ta, hi_ta
            else:
                st.empty()
        with ta_c3:
            st.empty()

        # Riga 3: Fattore di correzione
        st.markdown(f"<div style='font-size: 0.88rem;'>{label_fc}</div>", unsafe_allow_html=True)
        fc_c1, fc_c2, fc_c3 = st.columns([1, 1, 1.6], gap="small")

        with fc_c1:
            if st.session_state.get("range_unico_beta", False):
                fc_min_val = st.number_input(
                    "FC min",
                    value=sget("fc_min_val", round(sget("fattore_correzione", 1.0) - 0.10, 2)),
                    step=0.1, format="%.2f",
                    key="fc_min_val",
                    label_visibility="collapsed"
                )
            else:
                st.number_input(
                    "FC",
                    value=sget("fattore_correzione", 1.0),
                    step=0.1, format="%.2f",
                    key="fattore_correzione",
                    label_visibility="collapsed"
                )
                if not st.session_state.get("fc_suggested_vals"):
                    st.session_state.pop("FC_min_beta", None)
                    st.session_state.pop("FC_max_beta", None)

        with fc_c2:
            if st.session_state.get("range_unico_beta", False):
                fc_other_val = st.number_input(
                    "FC max",
                    value=sget("fc_other_val", round(sget("fattore_correzione", 1.0) + 0.10, 2)),
                    step=0.1, format="%.2f",
                    key="fc_other_val",
                    label_visibility="collapsed"
                )
                lo_fc, hi_fc = sorted([float(st.session_state["fc_min_val"]), float(st.session_state["fc_other_val"])])
                st.session_state["FC_min_beta"], st.session_state["FC_max_beta"] = lo_fc, hi_fc
            else:
                st.empty()

        with fc_c3:
            st.toggle("Suggerisci FC", key="toggle_fattore_inline")
        st.session_state["toggle_fattore"] = st.session_state.get("toggle_fattore_inline", False)

    else:
        # -------------------------
        # 🔷 MASCHERA STANDARD
        # -------------------------
        col1, col2, col3 = st.columns([1, 1, 1], gap="small")
        with col1:
            st.markdown("<div style='font-size: 0.88rem;'>T. rettale (°C):</div>", unsafe_allow_html=True)
            st.number_input("T. rettale (°C):",
                            value=sget("rt_val", 35.0), step=0.1, format="%.1f",
                            key="rt_val", label_visibility="collapsed")
        with col2:
            st.markdown("<div style='font-size: 0.88rem;'>T. ante-mortem (°C):</div>", unsafe_allow_html=True)
            st.number_input("T. ante-mortem stimata (°C):",
                            value=sget("tm_val", 37.2), step=0.1, format="%.1f",
                            key="tm_val", label_visibility="collapsed")
        with col3:
            st.markdown("<div style='font-size: 0.88rem;'>Peso  (kg):</div>", unsafe_allow_html=True)
            st.number_input("Peso (kg):",
                            value=sget("peso", 70.0), step=1.0, format="%.1f",
                            key="peso", label_visibility="collapsed")

        col1, col2, col3 = st.columns([1, 1, 1], gap="small")
        with col1:
            st.markdown("<div style='font-size: 0.88rem;'>T. ambientale media (°C):</div>", unsafe_allow_html=True)
            st.number_input("T. ambientale (°C):",
                            value=sget("ta_base_val", 20.0), step=0.1, format="%.1f",
                            key="ta_base_val", label_visibility="collapsed")

        with col2:
            st.markdown("<div style='font-size: 0.88rem;'>Fattore di correzione (FC):</div>", unsafe_allow_html=True)
            st.number_input("Fattore di correzione:",
                            value=sget("fattore_correzione", 1.0), step=0.1, format="%.2f",
                            key="fattore_correzione", label_visibility="collapsed")
        with col3:
            st.toggle("Suggerisci FC", key="toggle_fattore_inline_std")
            st.session_state["toggle_fattore"] = st.session_state.get("toggle_fattore_inline_std", False)
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
    stato_label = st.radio("dummy", ["Corpo asciutto", "Bagnato", "Immerso"], index=0, horizontal=True, key=k("radio_stato_corpo"))
    stato_corpo = "Asciutto" if stato_label == "Corpo asciutto" else ("Bagnato" if stato_label == "Bagnato" else "Immerso")

    # ============== Immerso ==============
    if stato_corpo == "Immerso":
        acqua_label = st.radio("dummy", ["In acqua stagnante", "In acqua corrente"], index=0, horizontal=True, key=k("radio_acqua"))
        acqua_mode = "stagnante" if acqua_label == "In acqua stagnante" else "corrente"

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
            st.button("✅ Usa questo fattore", on_click=_apply_fc, args=(result.fattore_finale, result.riassunto),
                      use_container_width=True, key=k("btn_usa_fc_imm"))

        if st.session_state.get("stima_cautelativa_beta", False):
            st.button("➕ Aggiungi a range FC", use_container_width=True, on_click=add_fc_suggestion_global,
                      args=(result.fattore_finale,), key=k("btn_add_fc_imm"))
        return

    # ============== Asciutto / Bagnato ==============
    col_corr, col_vest = st.columns([1.0, 1.3])
    with col_corr:
        corr_placeholder = st.empty()
    with col_vest:
        toggle_vestito = st.toggle("Vestito/coperto?", key=k("toggle_vestito"), value=False)

    n_sottili = n_spessi = n_cop_medie = n_cop_pesanti = 0
    if toggle_vestito:
        defaults = {
            "Strati leggeri (indumenti o teli sottili)": st.session_state.get(k("strati_sottili"), 0),
            "Strati pesanti (indumenti o teli spessi)":  st.session_state.get(k("strati_spessi"), 0),
        }
        if stato_corpo == "Asciutto":
            defaults.update({
                "Coperte di medio spessore": st.session_state.get(k("coperte_medie"), 0),
                "Coperte pesanti":           st.session_state.get(k("coperte_pesanti"), 0),
            })

        rows = [{"--": nome, "Numero?": val} for nome, val in defaults.items()]
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
                "Numero?": st.column_config.NumberColumn(min_value=0, max_value=8, step=1, width="small"),
            },
        )

        vals = {r["--"]: int(r["Numero?"] or 0) for _, r in edited.iterrows()}

        n_sottili = vals.get("Strati leggeri (indumenti o teli sottili)", 0)
        n_spessi = vals.get("Strati pesanti (indumenti o teli spessi)", 0)
        n_cop_medie = vals.get("Coperte di medio spessore", 0) if stato_corpo == "Asciutto" else 0
        n_cop_pesanti = vals.get("Coperte pesanti", 0) if stato_corpo == "Asciutto" else 0

    counts = DressCounts(sottili=n_sottili, spessi=n_spessi, coperte_medie=n_cop_medie, coperte_pesanti=n_cop_pesanti)

    superficie_display_selected = "/"
    if stato_corpo == "Asciutto":
        nudo_eff = ((not toggle_vestito) or (counts.sottili == counts.spessi == counts.coperte_medie == counts.coperte_pesanti == 0))
        options_display = SURF_DISPLAY_ORDER.copy()
        if not nudo_eff:
            options_display = [o for o in options_display if o != "Superficie metallica spessa (all’aperto)"]
        prev_display = st.session_state.get(k("superficie_display_sel"))
        if prev_display not in options_display:
            prev_display = options_display[0]
        superficie_display_selected = st.selectbox("Superficie di appoggio", options_display,
                                                   index=options_display.index(prev_display), key=k("superficie_display_sel"))

    correnti_presenti = False
    with corr_placeholder.container():
        mostra_correnti = True
        if stato_corpo == "Asciutto":
            from app.factor_calc import fattore_vestiti_coperte
            f_vc = fattore_vestiti_coperte(counts)
            if f_vc >= 1.2:
                mostra_correnti = False
        if mostra_correnti:
            correnti_presenti = st.toggle("Correnti d'aria presenti?", key=k("toggle_correnti_fc"), disabled=False)

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
        st.button("✅ Usa questo fattore", on_click=_apply_fc, args=(result.fattore_finale, result.riassunto),
                  use_container_width=True, key=k("btn_usa_fc"))

    if st.session_state.get("stima_cautelativa_beta", False):
        st.button("➕ Aggiungi a range FC", use_container_width=True, on_click=add_fc_suggestion_global,
                  args=(result.fattore_finale,), key=k("btn_add_fc"))

# --- Toggle pannello suggeritore in fondo al riquadro ---
_togg_val = st.session_state.get("toggle_fattore", False)
st.session_state["toggle_fattore"] = st.session_state.get("toggle_fattore_bottom", _togg_val)

# --- Pannello "Suggerisci FC" ---
if st.session_state.get("toggle_fattore", False):
    with st.container(border=True):
        pannello_suggerisci_fc(
            peso_default=st.session_state.get("peso", 70.0),
            key_prefix="fcpanel_caut" if st.session_state.get("stima_cautelativa_beta", False) else "fcpanel_std"
        )

# Parametri aggiuntivi
mostra_parametri_aggiuntivi = st.checkbox("Aggiungi dati tanatologici speciali")
widgets_parametri_aggiuntivi = {}

if mostra_parametri_aggiuntivi:
    with st.container(border=True):
        usa_orario_custom_globale = st.session_state.get("usa_orario_custom", False)

        if not usa_orario_custom_globale:
            st.markdown(
                "<div style='font-size:0.9rem; color:#666; padding:6px 8px; "
                "border-left:4px solid #bbb; background:#f7f7f7; margin-bottom:8px;'>"
                "Per specificare orari dei rilievi, attiva in alto "
                "<b>“Aggiungi data/ora rilievi”</b>."
                "</div>",
                unsafe_allow_html=True
            )

        for nome_parametro, dati_parametro in dati_parametri_aggiuntivi.items():
            col1, col2 = st.columns([1, 2], gap="small")

            with col1:
                subcol1, subcol2 = st.columns([1, 0.5])
                with subcol1:
                    st.markdown(
                        f"<div style='font-size: 0.88rem; padding-top: 0.4rem;'>{nome_parametro}:</div>",
                        unsafe_allow_html=True
                    )
                with subcol2:
                    if nome_parametro in ["Eccitabilità elettrica sopraciliare", "Eccitabilità elettrica peribuccale"]:
                        with st.popover(" "):
                            if nome_parametro == "Eccitabilità elettrica sopraciliare":
                                st.image(
                                    "https://raw.githubusercontent.com/scopusjin/codice/main/immagini/eccitabilit%C3%A0.PNG",
                                    width=400
                                )
                            elif nome_parametro == "Eccitabilità elettrica peribuccale":
                                st.image(
                                    "https://raw.githubusercontent.com/scopusjin/codice/main/immagini/peribuccale.PNG",
                                    width=300
                                )

            with col2:
                selettore = st.selectbox(
                    label=nome_parametro,
                    options=dati_parametro["opzioni"],
                    key=f"{nome_parametro}_selector",
                    label_visibility="collapsed"
                )

            data_picker = None
            ora_input = None
            usa_orario_personalizzato = False

            if selettore != "Non valutata" and usa_orario_custom_globale:
                chiave_checkbox = f"{nome_parametro}_diversa"
                colx1, colx2 = st.columns([0.75, 0.25], gap="small")
                with colx1:
                    st.markdown(
                        "<div style='font-size: 0.8em; color: orange; margin-bottom: 3px;'>"
                        "Valutato ad un'ora diversa?"
                        "</div>",
                        unsafe_allow_html=True
                    )
                with colx2:
                    usa_orario_personalizzato = st.checkbox(label="", key=chiave_checkbox)

            if usa_orario_custom_globale and usa_orario_personalizzato:
                coly1, coly2 = st.columns(2)
                with coly1:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Data rilievo:</div>", unsafe_allow_html=True)
                    data_picker = st.date_input("Data rilievo:", value=input_data_rilievo,
                                                key=f"{nome_parametro}_data", label_visibility="collapsed")
                with coly2:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Ora rilievo:</div>", unsafe_allow_html=True)
                    ora_input = st.text_input("Ora rilievo (HH:MM):", value=input_ora_rilievo,
                                              key=f"{nome_parametro}_ora", label_visibility="collapsed")

            widgets_parametri_aggiuntivi[nome_parametro] = {
                "selettore": selettore,
                "data_rilievo": data_picker,
                "ora_rilievo": ora_input
            }

        chk_putrefattive = st.checkbox("Alterazioni putrefattive?", value=st.session_state.get("alterazioni_putrefattive", False))
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

# --- Helper: applica range prudente di default quando "Specifica range" è OFF ---
def _apply_default_prudent_ranges():
    if not st.session_state.get("stima_cautelativa_beta", False):
        return
    if not st.session_state.get("range_unico_beta", False):
        ta = st.session_state.get("ta_base_val")
        if _is_num(ta):
            st.session_state["Ta_min_beta"] = round(float(ta) - 1.0, 2)
            st.session_state["Ta_max_beta"] = round(float(ta) + 1.0, 2)
        else:
            st.session_state.pop("Ta_min_beta", None)
            st.session_state.pop("Ta_max_beta", None)

        if not st.session_state.get("fc_suggested_vals"):
            fc = st.session_state.get("fattore_correzione", 1.0)
            st.session_state["FC_min_beta"] = round(float(fc) - 0.10, 2)
            st.session_state["FC_max_beta"] = round(float(fc) + 0.10, 2)

# --- Pulizia chiavi dei widget di range quando si torna OFF ---
if not st.session_state.get("range_unico_beta", False):
    for _tmpk in ("ta_
