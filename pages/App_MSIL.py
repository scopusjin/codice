# pages/app_mobile.py
# -*- coding: utf-8 -*-
import datetime
import pandas as pd
import streamlit as st

from app.graphing import aggiorna_grafico
from app.data_sources import load_tabelle_correzione
from app.factor_calc import (
    DressCounts, compute_factor, SURF_DISPLAY_ORDER, fattore_vestiti_coperte
)

st.set_page_config(page_title="STIMA EPOCA DECESSO - MSIL", layout="centered")

st.markdown("""
<style>
header[data-testid="stHeader"]{display:none!important;}
section.main, div.block-container{padding-top:0!important;margin-top:0!important}
div[data-testid="stContainer"], .element-container{padding:0!important;margin:0!important}
div[data-testid="stVerticalBlock"]{margin:0!important}
div[data-testid="stVerticalBlock"] > div{margin:2px 0!important}
div[data-testid="stHorizontalBlock"]{display:flex;flex-wrap:wrap;gap:.22rem!important;margin:0!important}
div[data-testid="column"]{padding:0!important;margin:0!important;flex:1 1 220px!important;min-width:220px!important}
div[data-testid="stSelectbox"],
div[data-testid="stNumberInput"],
div[data-testid="stToggle"],
div[data-testid="stRadio"],
div[data-testid="stDateInput"],
div[data-testid="stTextInput"]{margin-top:2px!important;margin-bottom:2px!important;padding:0!important}
div[data-testid="stNumberInput"] > label,
div[data-testid="stSelectbox"] > label,
div[data-testid="stToggle"] > label,
div[data-testid="stRadio"] > label,
div[data-testid="stDateInput"] > label,
div[data-testid="stTextInput"] > label{margin:0 0 2px 0!important;line-height:1.05!important;font-size:.84rem}
div[data-testid="stNumberInput"] input{height:30px!important;padding:3px 6px!important}
div[data-baseweb="select"] > div{min-height:30px!important}
div[data-testid="stSelectbox"] svg{margin-top:-3px!important}
/* --- RADIO SUPER-COMPATTI --- */
div[data-testid="stRadio"]{
  margin:0!important;
  padding:0!important;
}
div[data-testid="stRadio"] > label{
  display:none!important;   /* elimina spazio riservato alla label */
  height:0!important;
  margin:0!important;
  padding:0!important;
}
div[data-testid="stRadio"] div[role="radiogroup"]{
  gap:.20rem!important;     /* distanza orizzontale minima tra le opzioni */
  margin:0!important;
  padding:0!important;
}
div[data-testid="stRadio"] div[role="radiogroup"] > label{
  margin:0!important;       /* rimuove margini di ciascuna opzione */
  padding:.05rem .2rem!important;
  line-height:1!important;
}

/* pannello FC senza cuscinetti */
.fcpanel{margin:0!important;padding:0!important}
.fcpanel > div{margin:0!important}

div[data-testid="stDataEditor"] thead,
div[data-testid="stDataEditor"] [role="columnheader"],
div[data-testid="stDataEditor"] .column-header{display:none!important}
[data-testid="stElementToolbar"]{display:none!important}
.tight-label{margin:0!important;padding:0!important;line-height:1.05}
.tight-label p{margin:0!important}
.hint{font-size:.72rem;opacity:.75;margin-left:.25rem}
div.stButton{margin:0!important}
div.stButton>button{min-height:34px;height:34px;margin:0!important}
div.stButton>button:hover{filter:brightness(1.06)}
#stDecoration,[data-testid="stDecoration"],[data-testid="viewerBadge"],a[data-testid="viewerBadge"],
[class^="viewerBadge_"],[class*=" viewerBadge_"],a[href^="https://streamlit.io/cloud"],
a[href^="https://share.streamlit.io"]{display:none!important;}
#MainMenu{visibility:hidden;} footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

_defaults = {
    "run_stima_mobile": False,
    "show_avvisi": True,
    "rt_val": 35.0,
    "ta_base_val": 20.0,
    "peso": 70.0,
    "fattore_correzione": 1.0,
    "usa_orario_custom": False,
    "input_data_rilievo": None,
    "input_ora_rilievo": None,
    "toggle_fattore_inline_mobile": False,
    "fc_riassunto_contatori": None,
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

def _safe_int(x):
    try: return int(x)
    except Exception: return 0

def _label(text, hint=None):
    if hint:
        st.markdown(f"<div class='tight-label'>{text} <span class='hint'>{hint}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='tight-label'>{text}</div>", unsafe_allow_html=True)

# ---------------------- Data/Ora ispezione --------------------
st.toggle("Aggiungi data/ora rilievi tanatologici", key="usa_orario_custom")
if st.session_state["usa_orario_custom"]:
    if st.session_state.get("input_data_rilievo") is None:
        st.session_state["input_data_rilievo"] = datetime.date.today()
    if not st.session_state.get("input_ora_rilievo"):
        st.session_state["input_ora_rilievo"] = datetime.datetime.now().strftime("%H:%M")
    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.date_input("Data ispezione legale", value=st.session_state["input_data_rilievo"],
                      label_visibility="collapsed", key="input_data_rilievo")
    with c2:
        st.text_input("Ora ispezione legale (HH:MM)", value=st.session_state["input_ora_rilievo"],
                      label_visibility="collapsed", key="input_ora_rilievo")
else:
    st.session_state["input_data_rilievo"] = None
    st.session_state["input_ora_rilievo"] = None

# --------------------- Ipostasi e rigidità --------------------
_IPOSTASI_MOBILE = {
    "Ipostasi assenti": "Non ancora comparse",
    "Ipostasi almeno in parte migrabili": "Migrabili perlomeno parzialmente",
    "Ipostasi non migrabili": "Fisse",
    "Ipostasi?": "Non valutate",
}
_RIGIDITA_MOBILE = {
    "Rigor assente": "Non ancora apprezzabile",
    "Rigor presente e in aumento": "Presente e in via di intensificazione e generalizzazione",
    "Rigor ubiquitario e massimo": "Presente, intensa e generalizzata",
    "Rigor in risoluzione": "In via di risoluzione",
    "Rigor risolto": "Risolta",
    "Rigor mortis?": "Non valutata",
}
c_ip, c_rg = st.columns(2, gap="small")
with c_ip:
    ip_keys = list(_IPOSTASI_MOBILE.keys())
    scelta_ipostasi_lbl = st.selectbox(
        "Macchie ipostatiche", ip_keys,
        index=(ip_keys.index("Ipostasi?") if "Ipostasi?" in ip_keys else 0),
        key="selettore_macchie_mobile", label_visibility="collapsed",
    )
    selettore_macchie = _IPOSTASI_MOBILE[scelta_ipostasi_lbl]
with c_rg:
    rg_keys = list(_RIGIDITA_MOBILE.keys())
    scelta_rigidita_lbl = st.selectbox(
        "Rigidità cadaverica", rg_keys,
        index=(rg_keys.index("Rigor mortis?") if "Rigor mortis?" in rg_keys else 0),
        key="selettore_rigidita_mobile", label_visibility="collapsed",
    )
    selettore_rigidita = _RIGIDITA_MOBILE[scelta_rigidita_lbl]

# ------------------ 1) Campi di input (FC placeholder) --------
c_rt, c_ta, c_w, c_fc = st.columns(4, gap="small")

with c_rt:
    _label("T. rettale (°C)")
    input_rt = st.number_input("", value=st.session_state.get("rt_val", 35.0),
                               step=0.1, format="%.1f", key="rt_val", label_visibility="collapsed")

with c_ta:
    _label("T. ambientale media (°C)", " incertezza ±1 °C")
    input_ta = st.number_input("", value=st.session_state.get("ta_base_val", 20.0),
                               step=0.1, format="%.1f", key="ta_base_val", label_visibility="collapsed")

with c_w:
    _label("Peso (kg)", "incertezza ±3 kg")
    input_w = st.number_input("", value=st.session_state.get("peso", 70.0),
                              step=1.0, format="%.1f", key="peso", label_visibility="collapsed")

with c_fc:
    _label("Fattore di correzione (FC)", "incertezza ±0.10")
    fc_placeholder = st.empty()   # il widget FC verrà creato DOPO il pannello

# ------------------ 2) Toggle “Suggerisci FC” -----------------
st.toggle("Suggerisci FC",
          value=st.session_state.get("toggle_fattore_inline_mobile", False),
          key="toggle_fattore_inline_mobile")
st.session_state["toggle_fattore"] = st.session_state["toggle_fattore_inline_mobile"]

# -------- Pannello “Suggerisci FC” (calcola __next_fc) --------
def pannello_suggerisci_fc_mobile(peso_default: float = 70.0, key_prefix: str = "fcpanel_m"):
    def k(name: str) -> str: return f"{key_prefix}_{name}"

    st.markdown("<div class='fcpanel'>", unsafe_allow_html=True)

    stato_label = st.radio("", ["Corpo asciutto", "Bagnato", "Immerso"],
                           index=0, horizontal=True, key=k("radio_stato_corpo"),
                           label_visibility="collapsed")
    stato_corpo = "Asciutto" if stato_label == "Corpo asciutto" else stato_label

    try:
        tabella2 = load_tabelle_correzione()
    except Exception:
        tabella2 = None

    if stato_corpo == "Immerso":
        acqua_label = st.radio("", ["In acqua stagnante", "In acqua corrente"],
                               index=0, horizontal=True, key=k("radio_acqua"),
                               label_visibility="collapsed")
        acqua_mode = "stagnante" if acqua_label == "In acqua stagnante" else "corrente"

        result = compute_factor(
            stato="Immerso", acqua=acqua_mode, counts=DressCounts(),
            superficie_display=None, correnti_aria=False,
            peso=float(st.session_state.get("peso", peso_default)),
            tabella2_df=tabella2
        )
        st.session_state["__next_fc"] = round(float(result.fattore_finale), 2)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    col_corr, col_vest = st.columns([1.0, 1.3], gap="small")
    with col_corr:
        corr_placeholder = st.empty()
    with col_vest:
        toggle_vestito = st.toggle("Vestiti/coperte su addome/bacino?",
                                   value=st.session_state.get(k("toggle_vestito"), False),
                                   key=k("toggle_vestito"))

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
        df = pd.DataFrame([{"Voce": nome, "Numero?": v} for nome, v in defaults.items()])
        edited = st.data_editor(
            df, hide_index=True, use_container_width=True,
            column_config={
                "Voce": st.column_config.TextColumn(disabled=True, width="medium"),
                "Numero?": st.column_config.NumberColumn(min_value=0, max_value=8, step=1, width="small"),
            },
        )
        vals = {r["Voce"]: _safe_int(r["Numero?"]) for _, r in edited.iterrows()}
        n_sottili     = vals.get("Strati leggeri (indumenti o teli sottili)", 0)
        n_spessi      = vals.get("Strati pesanti (indumenti o teli spessi)", 0)
        n_cop_medie   = vals.get("Coperte di medio spessore", 0) if stato_corpo == "Asciutto" else 0
        n_cop_pesanti = vals.get("Coperte pesanti", 0)           if stato_corpo == "Asciutto" else 0

    counts = DressCounts(
        sottili=n_sottili, spessi=n_spessi,
        coperte_medie=n_cop_medie, coperte_pesanti=n_cop_pesanti
    )

    superficie_display_selected = None
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
            "Superficie di appoggio", options_display,
            index=options_display.index(prev_display),
            key=k("superficie_display_sel"), label_visibility="visible"
        )

    correnti_presenti = False
    with corr_placeholder.container():
        mostra_correnti = True
        if stato_corpo == "Asciutto":
            f_vc = fattore_vestiti_coperte(counts)
            if f_vc >= 1.2:
                mostra_correnti = False
        if mostra_correnti:
            correnti_presenti = st.toggle(
                "Correnti d'aria presenti?",
                value=st.session_state.get(k("toggle_correnti_fc"), False),
                key=k("toggle_correnti_fc"), disabled=False
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
    st.session_state["__next_fc"] = round(float(result.fattore_finale), 2)
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.get("toggle_fattore_inline_mobile", False):
    pannello_suggerisci_fc_mobile(
        peso_default=st.session_state.get("peso", 70.0),
        key_prefix="fcpanel_mobile"
    )

# ---- Applica l'eventuale FC calcolato PRIMA di creare il widget FC ----
if "__next_fc" in st.session_state:
    st.session_state["fattore_correzione"] = st.session_state.pop("__next_fc")

# Crea ORA il widget FC nel placeholder (ultima posizione della riga input)
with c_fc:
    fc_placeholder.number_input(
        "", value=st.session_state.get("fattore_correzione", 1.0),
        step=0.1, format="%.2f", key="fattore_correzione", label_visibility="collapsed"
    )

# ------------------ 3) Pulsante finale ------------------------
clicked = st.button("STIMA EPOCA DECESSO", key="btn_stima_mobile", use_container_width=True, type="primary")

# ----------------- Firma input e range fissi mobile -----------
def _inputs_signature_mobile(selettore_macchie: str, selettore_rigidita: str):
    return (
        bool(st.session_state.get("usa_orario_custom", False)),
        str(st.session_state.get("input_data_rilievo")),
        str(st.session_state.get("input_ora_rilievo")),
        selettore_macchie,
        selettore_rigidita,
        float(st.session_state.get("rt_val", 0.0)),
        float(st.session_state.get("ta_base_val", 0.0)),
        float(st.session_state.get("peso", 0.0)),
        float(st.session_state.get("fattore_correzione", 0.0)),
    )

st.session_state["stima_cautelativa_beta"] = True
st.session_state["range_unico_beta"] = True
st.session_state["ta_range_toggle_beta"] = True
st.session_state["fc_manual_range_beta"] = True
st.session_state.setdefault("fc_suggested_vals", [])

ta_center = float(st.session_state.get("ta_base_val", 20.0))
fc_center = float(st.session_state.get("fattore_correzione", 1.0))
st.session_state["Ta_min_beta"] = round(ta_center - 1.0, 2)
st.session_state["Ta_max_beta"] = round(ta_center + 1.0, 2)
st.session_state["FC_min_beta"] = round(fc_center - 0.10, 2)
st.session_state["FC_max_beta"] = round(fc_center + 0.10, 2)
st.session_state["peso_stimato_beta"] = True

curr_sig = _inputs_signature_mobile(selettore_macchie, selettore_rigidita)
if "last_run_sig_mobile" not in st.session_state:
    st.session_state["last_run_sig_mobile"] = curr_sig

if clicked:
    st.session_state["run_stima_mobile"] = True
    st.session_state["last_run_sig_mobile"] = curr_sig

if st.session_state.get("run_stima_mobile") and st.session_state.get("last_run_sig_mobile") != curr_sig:
    st.session_state["run_stima_mobile"] = False

# -------------------------- Output ---------------------------
if st.session_state.get("run_stima_mobile"):
    aggiorna_grafico(
        selettore_macchie=selettore_macchie,
        selettore_rigidita=selettore_rigidita,
        input_rt=input_rt,
        input_ta=input_ta,
        input_tm=37.2,
        input_w=input_w,
        fattore_correzione=st.session_state["fattore_correzione"],
        widgets_parametri_aggiuntivi={},
        usa_orario_custom=st.session_state["usa_orario_custom"],
        input_data_rilievo=st.session_state["input_data_rilievo"],
        input_ora_rilievo=st.session_state["input_ora_rilievo"],
        alterazioni_putrefattive=False,
    )
