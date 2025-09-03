

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

# ---------------------------
# Palette / UI helpers
# ---------------------------
def _fc_palette():
    base = st.get_option("theme.base") or "light"
    if base.lower() == "dark":
        return dict(
            bg="#0e3c2f", text="#d7fbe8", border="#2ea043", note="#abeacb"
        )
    else:
        return dict(
            bg="#e6f4ea", text="#0f5132", border="#2ea043", note="#5b7f6b"
        )

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
            f'Valore per 70 kg: {f_base:.2f} • Adattato per {peso_corrente:.1f} kg'
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

if "fattore_correzione" not in st.session_state:
    st.session_state["fattore_correzione"] = 1.0

if "show_img_sopraciliare" not in st.session_state:
    st.session_state["show_img_sopraciliare"] = False
if "show_img_peribuccale" not in st.session_state:
    st.session_state["show_img_peribuccale"] = False

if "show_results" not in st.session_state:
    st.session_state["show_results"] = False

# --- INIT per cautelativa: intervallo FC proposto dal pannello "Suggerisci FC"
if "fc_suggested_vals" not in st.session_state:
    st.session_state["fc_suggested_vals"] = [] 

def _sync_fc_range_from_suggestions():
    vals = st.session_state.get("fc_suggested_vals", [])
    vals = sorted({round(float(v), 2) for v in vals})

    if not vals:
        st.session_state.pop("FC_min_beta", None)
        st.session_state.pop("FC_max_beta", None)
        st.session_state["fc_manual_range_beta"] = False
        return

    # con 1 solo valore: applica ±0.10 di default
    if len(vals) == 1:
        lo, hi = vals[0] - 0.10, vals[0] + 0.10
    else:
        lo, hi = vals[0], vals[-1]

    # scrivi range e media come "base" per coerenza con i moduli che leggono un singolo valore
    st.session_state["FC_min_beta"] = round(lo, 2)
    st.session_state["FC_max_beta"] = round(hi, 2)
    st.session_state["fattore_correzione"] = round((lo + hi) / 2.0, 2)
    st.session_state["fc_manual_range_beta"] = True


def add_fc_suggestion_global(val: float) -> None:
    v = round(float(val), 2)
    vals = st.session_state.get("fc_suggested_vals", [])
    vals = sorted({*vals, v})
    # se >2 valori, mantieni solo gli estremi
    if len(vals) >= 3:
        vals = [vals[0], vals[-1]]
    st.session_state["fc_suggested_vals"] = vals
    _sync_fc_range_from_suggestions()

    

def clear_fc_suggestions_global() -> None:
    st.session_state["fc_suggested_vals"] = []
    _sync_fc_range_from_suggestions()
    
    



# Titolo
st.markdown("<h5 style='margin-top:0; margin-bottom:10px;'>STIMA EPOCA DECESSO</h5>", unsafe_allow_html=True)

# --- Definizione Widget (Streamlit) ---

# --- Data/Ora ispezione legale ---
with st.container(border=True):
    usa_orario_custom = st.toggle(
        "Aggiungi data/ora rilievi tanatologici",
        value=st.session_state.get("usa_orario_custom", False),
        key="usa_orario_custom",
    )

    if usa_orario_custom:
        col1, col2 = st.columns(2, gap="small")
        with col1:
            input_data_rilievo = st.date_input(
                "Data ispezione legale:",
                value=st.session_state.get("input_data_rilievo") or datetime.date.today(),
                label_visibility="collapsed",
                key="input_data_rilievo_widget",
            )
            st.session_state["input_data_rilievo"] = input_data_rilievo
        with col2:
            input_ora_rilievo = st.text_input(
                "Ora ispezione legale (HH:MM):",
                value=st.session_state.get("input_ora_rilievo") or "00:00",
                label_visibility="collapsed",
                key="input_ora_rilievo_widget",
            )
            st.session_state["input_ora_rilievo"] = input_ora_rilievo
    else:
        st.session_state["input_data_rilievo"] = None
        st.session_state["input_ora_rilievo"] = None
# Assicurati che le variabili esistano sempre
if "input_data_rilievo" not in st.session_state:
    st.session_state["input_data_rilievo"] = None
if "input_ora_rilievo" not in st.session_state:
    st.session_state["input_ora_rilievo"] = None

# Alias locali dai valori salvati in sessione
input_data_rilievo = st.session_state["input_data_rilievo"]
input_ora_rilievo  = st.session_state["input_ora_rilievo"]

# 📌 2. Ipostasi e rigidità — RIQUADRO (INVARIATO)
with st.container(border=True):
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>Ipostasi:</div>", unsafe_allow_html=True)
        selettore_macchie = st.selectbox("Macchie ipostatiche:", options=list(opzioni_macchie.keys()), label_visibility="collapsed")
    with col2:
        st.markdown("<div style='font-size: 0.88rem;'>Rigidità cadaverica:</div>", unsafe_allow_html=True)
        selettore_rigidita = st.selectbox("Rigidità cadaverica:", options=list(opzioni_rigidita.keys()), label_visibility="collapsed")

# === Switch generale Cautelativa ===
st.toggle(
    "Stima prudente",
    value=st.session_state.get("stima_cautelativa_beta", False),
    key="stima_cautelativa_beta"
)
stima_cautelativa_beta = st.session_state["stima_cautelativa_beta"]

# # ================================
# 📌 Riquadro raffreddamento (STANDARD o CAUTELATIVA)
# ================================
with st.container(border=True):

    if st.session_state.get("stima_cautelativa_beta", False):
        # -------------------------
        # 🔶 MASCHERA CAUTELATIVA
        # -------------------------

        # --- Toggle unico per i range TA e FC + messaggio generale ---
        rg1, rg2 = st.columns([0.6, 1.4], gap="small")
        with rg1:
            range_unico = st.toggle(
                "Specifica range",
                value=st.session_state.get("range_unico_beta", False),
                key="range_unico_beta"
            )
        # mantieni in sync le vecchie chiavi per compatibilità
        st.session_state["ta_range_toggle_beta"] = range_unico
    

        with rg2:
            st.caption("se non specificato, verrà considerato un range di ± 1 °C per la di T. amb e di ± 0.1 per FC.")

        # Riga 1: T. rettale, T. ante-mortem, Peso + switch ±3 kg
        c1, c2, c3, c4 = st.columns([1, 1, 1, 0.7], gap="small")
        with c1:
            st.markdown("<div style='font-size: 0.88rem;'>T. rettale (°C):</div>", unsafe_allow_html=True)
            input_rt = st.number_input(
                "T. rettale (°C):",
                value=st.session_state.get("rt_val", 35.0),
                step=0.1, format="%.1f",
                label_visibility="collapsed",
                key="rt_val"
            )
        with c2:
            st.markdown("<div style='font-size: 0.88rem;'>T. ante-mortem (°C):</div>", unsafe_allow_html=True)
            input_tm = st.number_input(
                "T. ante-mortem stimata (°C):",
                value=st.session_state.get("tm_val", 37.2),
                step=0.1, format="%.1f",
                label_visibility="collapsed",
                key="tm_val"
            )
        with c3:
            st.markdown("<div style='font-size: 0.88rem;'>Peso (kg):</div>", unsafe_allow_html=True)
            input_w = st.number_input(
                "Peso (kg):",
                value=st.session_state.get("peso", 70.0),
                step=1.0, format="%.1f",
                label_visibility="collapsed"
            )
            st.session_state["peso"] = input_w
        with c4:
            st.toggle("±3 kg", value=st.session_state.get("peso_stimato_beta", False), key="peso_stimato_beta")

        # Riga 2: T. ambientale media + range unico
        st.markdown("<div style='font-size: 0.88rem;'>T. ambientale media (°C):</div>", unsafe_allow_html=True)
        r2c1, r2c2, r2c3 = st.columns([1, 1, 1.2], gap="small")
        with r2c1:
            input_ta = st.number_input(
                "TA base",
                value=st.session_state.get("ta_base_val", 20.0),
                step=0.1, format="%.1f",
                label_visibility="collapsed",
                key="ta_base_val"
            )
        if range_unico:
            with r2c2:
                ta_other = st.number_input(
                    "TA altro estremo",
                    value=st.session_state.get("ta_other_val", input_ta + 1.0),
                    step=0.1, format="%.1f",
                    label_visibility="collapsed",
                    key="ta_other_val"
                )
            lo_ta, hi_ta = sorted([input_ta, ta_other])
            st.session_state["Ta_min_beta"], st.session_state["Ta_max_beta"] = lo_ta, hi_ta
        else:
            with r2c2:
                st.empty()
            with r2c3:
                st.caption("Verrà considerato un range ±1.0 °C.")
            st.session_state.pop("Ta_min_beta", None)
            st.session_state.pop("Ta_max_beta", None)

        # Riga 3: FC — label e toggle sulla stessa riga, campi input sulla stessa riga
        fc_head1, fc_head2 = st.columns([1.2, 0.8], gap="small")
        with fc_head1:
            st.markdown("<div style='font-size: 0.88rem;'>Fattore di correzione (FC):</div>", unsafe_allow_html=True)
        with fc_head2:
        

        if range_unico:
            r3c1, r3c2 = st.columns([1, 1], gap="small")
            fc_min_default = st.session_state.get("FC_min_beta", float(st.session_state.get("fattore_correzione", 1.0)))
            fc_max_default = st.session_state.get(
                "FC_max_beta",
                st.session_state.get("fc_other_val", float(st.session_state.get("fattore_correzione", 1.0)) + 0.10)
            )
            with r3c1:
                fc_min = st.number_input(
                    "FC min",
                    value=fc_min_default,
                    step=0.01, format="%.2f",
                    label_visibility="collapsed",
                    key="fc_min_val"
                )
            with r3c2:
                fc_max = st.number_input(
                    "FC max",
                    value=fc_max_default,
                    step=0.01, format="%.2f",
                    label_visibility="collapsed",
                    key="fc_other_val"
                )
            lo_fc, hi_fc = sorted([float(fc_min), float(fc_max)])
            st.session_state["FC_min_beta"], st.session_state["FC_max_beta"] = lo_fc, hi_fc
            st.session_state["fattore_correzione"] = round((lo_fc + hi_fc) / 2.0, 2)
        else:
            r3c1, _ = st.columns([1, 1], gap="small")
            with r3c1:
                fattore_correzione = st.number_input(
                    "FC",
                    value=st.session_state.get("fattore_correzione", 1.0),
                    step=0.01, format="%.2f",
                    label_visibility="collapsed",
                    key="fattore_correzione"
                )
            if not st.session_state.get("fc_manual_range_beta", False) and not st.session_state.get("fc_suggested_vals"):
                st.session_state.pop("FC_min_beta", None)
                st.session_state.pop("FC_max_beta", None)

        # --- Toggle pannello suggeritore in fondo al riquadro ---
        st.toggle("Suggerisci FC", value=st.session_state.get("toggle_fattore", False), key="toggle_fattore")
        

    
    else:
        # -------------------------
        # 🔷 MASCHERA STANDARD
        # -------------------------
        # 3. Temperature
        col1, col2, col3 = st.columns(3, gap="small")
        with col1:
            st.markdown("<div style='font-size: 0.88rem;'>T. rettale (°C):</div>", unsafe_allow_html=True)
            input_rt = st.number_input(
                "T. rettale (°C):",
                value=st.session_state.get("rt_val", 35.0),
                step=0.1, format="%.1f",
                label_visibility="collapsed",
                key="rt_val"
            )
        with col2:
            st.markdown("<div style='font-size: 0.88rem;'>T. ante-mortem (°C):</div>", unsafe_allow_html=True)
            input_tm = st.number_input(
                "T. ante-mortem stimata (°C):",
                value=st.session_state.get("tm_val", 37.2),
                step=0.1, format="%.1f",
                label_visibility="collapsed",
                key="tm_val"
            )
        with col3:
            st.markdown("<div style='font-size: 0.88rem;'>T. ambientale media (°C):</div>", unsafe_allow_html=True)
            input_ta = st.number_input(
                "T. ambientale (°C):",
                value=st.session_state.get("ta_base_val", 20.0),
                step=0.1, format="%.1f",
                label_visibility="collapsed",
                key="ta_base_val"
            )

        # 4. Peso + FC + Suggerisci
        col1, col2 = st.columns([1, 3], gap="small")
        with col1:
            st.markdown("<div style='font-size: 0.88rem;'>Peso corporeo (kg):</div>", unsafe_allow_html=True)
            input_w = st.number_input(
                "Peso (kg):",
                value=st.session_state.get("peso", 70.0),
                step=1.0, format="%.1f",
                label_visibility="collapsed"
            )
            st.session_state["peso"] = input_w
        with col2:
            subcol1, subcol2 = st.columns([1.5, 1], gap="small")
            with subcol1:
                st.markdown("<div style='font-size: 0.88rem;'>Fattore di correzione (FC):</div>", unsafe_allow_html=True)
                fattore_correzione = st.number_input(
                    "Fattore di correzione:",
                    value=st.session_state.get("fattore_correzione", 1.0),
                    step=0.01, format="%.2f",
                    label_visibility="collapsed",
                    key="fattore_correzione"
                )
            with subcol2:



# --- Pannello “Suggerisci FC” (identico alla app principale) ---
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
    stato_label = st.radio(
        "dummy",
        ["Corpo asciutto", "Bagnato", "Immerso"],
        index=0, horizontal=True, key=k("radio_stato_corpo")
    )
    stato_corpo = "Asciutto" if stato_label == "Corpo asciutto" else ("Bagnato" if stato_label == "Bagnato" else "Immerso")

    # ============== Immerso ==============
    if stato_corpo == "Immerso":
        acqua_label = st.radio(
            "dummy", ["In acqua stagnante", "In acqua corrente"],
            index=0, horizontal=True, key=k("radio_acqua")
        )
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

        st.button("✅ Usa questo fattore", on_click=_apply_fc,
                  args=(result.fattore_finale, result.riassunto),
                  use_container_width=True, key=k("btn_usa_fc_imm"))

        if st.session_state.get("stima_cautelativa_beta", False):
                st.button("➕ Aggiungi a range FC",
                          use_container_width=True, on_click=add_fc_suggestion_global,
                          args=(result.fattore_finale,), key=k("btn_add_fc_imm"))
            
        return

    # ============== Asciutto / Bagnato ==============
    col_corr, col_vest = st.columns([1.0, 1.3])
    with col_corr:
        corr_placeholder = st.empty()
    with col_vest:
        toggle_vestito = st.toggle(
            "Vestito/coperto?",
            value=st.session_state.get(k("toggle_vestito"), False),
            key=k("toggle_vestito")
        )

    n_sottili = n_spessi = n_cop_medie = n_cop_pesanti = 0
    if toggle_vestito:
        col_layers, col_blankets = st.columns(2)
        with col_layers:
            n_sottili = st.slider("Strati leggeri (indumenti o teli sottili)", 0, 8,
                                  st.session_state.get(k("strati_sottili"), 0), key=k("strati_sottili"))
            n_spessi = st.slider("Strati pesanti (indumenti o teli spessi)", 0, 6,
                                 st.session_state.get(k("strati_spessi"), 0), key=k("strati_spessi"))
        with col_blankets:
            if stato_corpo == "Asciutto":
                n_cop_medie = st.slider("Coperte di medio spessore", 0, 5,
                                        st.session_state.get(k("coperte_medie"), 0), key=k("coperte_medie"))
                n_cop_pesanti = st.slider("Coperte pesanti", 0, 5,
                                          st.session_state.get(k("coperte_pesanti"), 0), key=k("coperte_pesanti"))

    counts = DressCounts(sottili=n_sottili, spessi=n_spessi, coperte_medie=n_cop_medie, coperte_pesanti=n_cop_pesanti)

    superficie_display_selected = "/"
    if stato_corpo == "Asciutto":
        nudo_eff = ((not toggle_vestito)
                    or (counts.sottili == counts.spessi == counts.coperte_medie == counts.coperte_pesanti == 0))
        options_display = SURF_DISPLAY_ORDER.copy()
        if not nudo_eff:
            options_display = [o for o in options_display if o != "Superficie metallica spessa (all’aperto)"]
        prev_display = st.session_state.get(k("superficie_display_sel"))
        if prev_display not in options_display:
            prev_display = options_display[0]
        superficie_display_selected = st.selectbox(
            "Superficie di appoggio",
            options_display,
            index=options_display.index(prev_display),
            key=k("superficie_display_sel")
        )

    correnti_presenti = False
    with corr_placeholder.container():
        mostra_correnti = True
        if stato_corpo == "Asciutto":
            from app.factor_calc import fattore_vestiti_coperte
            f_vc = fattore_vestiti_coperte(counts)
            if f_vc >= 1.2:
                mostra_correnti = False
        if mostra_correnti:
            correnti_presenti = st.toggle(
                "Correnti d'aria presenti?",
                value=st.session_state.get(k("toggle_correnti_fc"), False),
                key=k("toggle_correnti_fc"),
                disabled=False
            )

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

    st.button("✅ Usa questo fattore", on_click=_apply_fc,
              args=(result.fattore_finale, result.riassunto),
              use_container_width=True, key=k("btn_usa_fc"))

    if st.session_state.get("stima_cautelativa_beta", False):
            st.button("➕ Aggiungi a range FC",
                      use_container_width=True, on_click=add_fc_suggestion_global,
                      args=(result.fattore_finale,), key=k("btn_add_fc"))
# --- Toggle pannello suggeritore in fondo al riquadro ---
_togg_val = st.session_state.get("toggle_fattore", False)
st.toggle("Suggerisci FC", value=_togg_val, key="toggle_fattore_bottom")
st.session_state["toggle_fattore"] = st.session_state.get("toggle_fattore_bottom", _togg_val)


# --- Pannello "Suggerisci FC" ---
if st.session_state.get("toggle_fattore", False):
    with st.container(border=True):
        pannello_suggerisci_fc(
            peso_default=st.session_state.get("peso", 70.0),
            key_prefix="fcpanel_caut" if st.session_state.get("stima_cautelativa_beta", False) else "fcpanel_std"
        )
        


# Parametri aggiuntivi (identico alla app principale)
mostra_parametri_aggiuntivi = st.checkbox("Aggiungi dati tanatologici speciali")
widgets_parametri_aggiuntivi = {}

if mostra_parametri_aggiuntivi:
    with st.container(border=True):
        usa_orario_custom_globale = st.session_state.get("usa_orario_custom", False)

        # Messaggio generale (mostrato una volta sola) se la data/ora iniziale NON è attiva
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

            # ---- Colonna etichetta + eventuale immagine di aiuto ----
            with col1:
                subcol1, subcol2 = st.columns([1, 0.5])
                with subcol1:
                    st.markdown(
                        f"<div style='font-size: 0.88rem; padding-top: 0.4rem;'>{nome_parametro}:</div>",
                        unsafe_allow_html=True
                    )
                with subcol2:
                    if nome_parametro in ["Eccitabilità elettrica sopraciliare", "Eccitabilità elettrica peribuccale"]:
                        with st.popover(" "):  # pulsante minimale
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

            # ---- Colonna selettore stato ----
            with col2:
                selettore = st.selectbox(
                    label=nome_parametro,
                    options=dati_parametro["opzioni"],
                    key=f"{nome_parametro}_selector",
                    label_visibility="collapsed"
                )

            # ---- Campi "orario diverso" (visibili solo se globale attivo) ----
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

            # ---- Campi data/ora SOLO se: globale attivo + checkbox attiva ----
            if usa_orario_custom_globale and usa_orario_personalizzato:
                coly1, coly2 = st.columns(2)
                with coly1:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Data rilievo:</div>", unsafe_allow_html=True)
                    data_picker = st.date_input(
                        "Data rilievo:",
                        value=input_data_rilievo,
                        key=f"{nome_parametro}_data",
                        label_visibility="collapsed"
                    )
                with coly2:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Ora rilievo:</div>", unsafe_allow_html=True)
                    ora_input = st.text_input(
                        "Ora rilievo (HH:MM):",
                        value=input_ora_rilievo,
                        key=f"{nome_parametro}_ora",
                        label_visibility="collapsed"
                    )

            # ---- Persisti valori widget ----
            widgets_parametri_aggiuntivi[nome_parametro] = {
                "selettore": selettore,
                "data_rilievo": data_picker,
                "ora_rilievo": ora_input
            }

        # ---- Checkbox putrefattive ----
        chk_putrefattive = st.checkbox(
            "Alterazioni putrefattive?",
            value=st.session_state.get("alterazioni_putrefattive", False),
        )
        st.session_state["alterazioni_putrefattive"] = chk_putrefattive
else:
    st.session_state["alterazioni_putrefattive"] = False
    
    
            

def _inputs_signature():
    import numpy as np
    import datetime as _dt
    import streamlit as st

    def _freeze(v):
        # None / bool
        if v is None or isinstance(v, bool):
            return v
        # numpy numerici -> python
        if isinstance(v, (np.floating,)):
            return float(v)
        if isinstance(v, (np.integer,)):
            return int(v)
        # numeri python
        if isinstance(v, (int, float)):
            return v
        # date/time/datetime -> ISO
        if isinstance(v, (_dt.date, _dt.datetime, _dt.time)):
            try:
                return v.isoformat()
            except Exception:
                return str(v)
        # sequenze -> tupla
        if isinstance(v, (list, tuple)):
            return tuple(_freeze(x) for x in v)
        # dict -> tupla ordinata di coppie (chiave,valore)
        if isinstance(v, dict):
            return tuple(sorted((k, _freeze(val)) for k, val in v.items()))
        # fallback
        return str(v)

    # Valori base (come prima)
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

    # Parametri aggiuntivi (se presenti in app)
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

    # Campi CAUTELATIVA (nuovi trigger di ricalcolo)
    caut = [
        _freeze(st.session_state.get("Ta_min_beta")),
        _freeze(st.session_state.get("Ta_max_beta")),
        _freeze(st.session_state.get("FC_min_beta")),
        _freeze(st.session_state.get("FC_max_beta")),
        bool(st.session_state.get("peso_stimato_beta", False)),
        bool(st.session_state.get("range_unico_beta", False)),  # nuovo toggle unico
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

# (opzionale) stile bottone
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
    if st.button("STIMA EPOCA DECESSO", key="btn_stima"):
        st.session_state["last_run_sig"] = curr_sig
        st.session_state["show_results"] = True

# --- Se QUALSIASI input cambia: nascondi risultati (NON ricalcolare) ---
if st.session_state["show_results"] and st.session_state["last_run_sig"] != curr_sig:
    st.session_state["show_results"] = False

# --- Mostra risultati SOLO se richiesti e firma invariata ---
if st.session_state["show_results"]:
    aggiorna_grafico(
        selettore_macchie=selettore_macchie,
        selettore_rigidita=selettore_rigidita,
        input_rt=input_rt, input_ta=input_ta, input_tm=input_tm, input_w=input_w,
        fattore_correzione=st.session_state.get("fattore_correzione", 1.0),
        widgets_parametri_aggiuntivi=widgets_parametri_aggiuntivi,
        usa_orario_custom=st.session_state.get("usa_orario_custom", False),
        input_data_rilievo=st.session_state.get("input_data_rilievo"),
        input_ora_rilievo=st.session_state.get("input_ora_rilievo"),
        alterazioni_putrefattive=st.session_state.get("alterazioni_putrefattive", False),
)
    
