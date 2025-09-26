# pages/app_mobile.py
# -*- coding: utf-8 -*-
import datetime
import pandas as pd
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

from app.graphing import aggiorna_grafico
from app.data_sources import load_tabelle_correzione
from app.factor_calc import (
    DressCounts, compute_factor, SURF_DISPLAY_ORDER, fattore_vestiti_coperte
)

# ------------------------------------------------------------
# Config pagina
# ------------------------------------------------------------
st.set_page_config(page_title="STIMA EPOCA DECESSO - MSIL", layout="centered")

# ------------------------------------------------------------
# CSS compatto + nascondi header/footer/badge
# ------------------------------------------------------------
st.markdown("""
<style>
/* Header e padding pagina */
header[data-testid="stHeader"]{display:none!important;}
section.main, div.block-container{padding-top:0!important;margin-top:0!important}

/* Layout base */
div[data-testid="stContainer"], .element-container{padding:0!important;margin:0!important}
div[data-testid="stVerticalBlock"]{margin:0!important}
div[data-testid="stVerticalBlock"] > div{margin:0!important}
div[data-testid="stHorizontalBlock"]{display:flex;flex-wrap:wrap;gap:.22rem!important;margin:0!important}
div[data-testid="column"]{padding:0!important;margin:0!important;flex:1 1 220px!important;min-width:220px!important}

/* Widget uniformi */
div[data-testid="stSelectbox"],
div[data-testid="stNumberInput"],
div[data-testid="stToggle"],
div[data-testid="stRadio"],
div[data-testid="stDateInput"],
div[data-testid="stTextInput"]{margin:2px 0!important;padding:0!important}
div[data-testid="stNumberInput"] > label,
div[data-testid="stSelectbox"] > label,
div[data-testid="stToggle"] > label,
div[data-testid="stRadio"] > label,
div[data-testid="stDateInput"] > label,
div[data-testid="stTextInput"] > label{margin:0 0 2px 0!important;line-height:1.05!important;font-size:.84rem}
div[data-testid="stNumberInput"] input{height:30px!important;padding:3px 6px!important}
div[data-baseweb="select"] > div{min-height:30px!important}
div[data-testid="stSelectbox"] svg{margin-top:-3px!important}

/* Radio compatti */
div[data-testid="stRadio"]{margin:0!important;padding:0!important}
div[data-testid="stRadio"] > label{display:none!important;height:0!important;margin:0!important;padding:0!important}
div[data-testid="stRadio"] div[role="radiogroup"]{gap:.20rem!important;margin:0!important;padding:0!important}
div[data-testid="stRadio"] div[role="radiogroup"] > label{margin:0!important;padding:.05rem .2rem!important;line-height:1!important}

/* Toggle compatti */
div[data-testid="stToggle"]{margin:0!important;padding:0!important}

/* Data editor asciutto */
div[data-testid="stDataEditor"] thead,
div[data-testid="stDataEditor"] [role="columnheader"],
div[data-testid="stDataEditor"] .column-header{display:none!important}
[data-testid="stElementToolbar"]{display:none!important}

/* Etichette custom compatte */
.tight-label{margin:0!important;padding:0!important;line-height:1.05}
.tight-label p{margin:0!important}
.hint{font-size:.72rem;opacity:.75;margin-left:.25rem}

/* Pulsanti */
div.stButton{margin:0!important}
div.stButton>button{min-height:34px;height:34px;margin:0!important}
div.stButton>button:hover{filter:brightness(1.06)}

/* Pannello Suggerisci FC: classe applicata via JS */
.fcwrap-bg{
  background:#f0f6ff!important;
  border-radius:4px!important;
  padding:8px!important;
}
@media (prefers-color-scheme: dark){
  .fcwrap-bg{ background:#0f2036!important; }
}


/* Nascondi footer/badge Streamlit */
#stDecoration,[data-testid="stDecoration"],
[data-testid="viewerBadge"],a[data-testid="viewerBadge"],
[class^="viewerBadge_"],[class*=" viewerBadge_"],
a[href^="https://streamlit.io/cloud"], a[href^="https://share.streamlit.io"]{display:none!important;}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Raccomandazioni helper + stile popover
# ------------------------------------------------------------
def _raccomandazioni_html() -> str:  
    return """
    <div style="font-size:0.9rem; line-height:1.45; color:#444;">
      <b>LA VALUTAZIONE DEL RAFFREDDAMENTO CADAVERICO NON è APPLICABILE SE:</b><br><br>
      • Luogo di ispezione/rinvenimento ≠ luogo del decesso.<br>
      • Fonte di calore nelle vicinanze del corpo.<br>
      • Riscaldamento a pavimento sotto il corpo.<br>
      • Ipotermia certa/sospetta (T iniziale < 35 °C).<br>
      • Temperatura ambientale media non determinabile.<br>
      • Fattore di correzione di Henssge non stimabile<br>
      • Temperatura ambientale aumentata molto dopo il decesso.<br><br>
      <b>DA RICORDARE:</b><br><br>
      • Non usare direttamente la temperatura ambientale misurata, ma ragionare su come è cambiata la temperatura tra decesso e ispezione (è aumentata durante il giorno? vi era più freddo nella notte?). Stimare la temperatura media in cui potrebbe essersi trovato il corpo. Valutare eventuali dati meteorologici.<br>
      • Migrabilità ≠ improntabilità (quest'ultimo dato non serve per questa app). Cambiare posizione al cadavere e valutare se si modificano le ipostasi in 20 minuti.<br>
      • Per il fattore di correzione, tenere conto solo degli indumenti e delle coperture a livello delle porzioni caudali del tronco del cadavere. Il sistema che suggerisce il fattore di correzione è da considerarsi indicativo. Si consiglia di utilizzare varie combinazioni e un range di fattori.<br>
      • L'applicazione considera, prudentemente, possibili variazioni di ±1 °C per la temperatura ambientale inserita, di ± 0.1 per il fattore di correzione, di ±3 kg per il peso stimato.<br><br> 
    </div>
    """

st.markdown(
    """
    <style>
    /* link popover blu tipo link */
    div[data-testid="stPopover"] button {
        background:none!important;
        border:none!important;
        color:#1976d2!important;
        font-size:0.9rem!important;
        padding:0!important;
        margin:6px 0!important;
        text-decoration:underline;
        cursor:pointer;
    }
    /* niente limite di altezza al contenuto del popover */
    div[data-testid="stPopoverContent"] { max-height:none!important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# Stato iniziale
# ------------------------------------------------------------
_defaults = {
    "run_stima_mobile": False,
    "show_avvisi": True,

    # Termici/peso SENZA default: opzionali
    "rt_val": None,
    "ta_base_val": None,
    "peso": None,

    # TM fisso e non editabile
    "tm_val": 37.2,

    "fattore_correzione": 1.0,
    "usa_orario_custom": False,
    "input_data_rilievo": None,
    "input_ora_rilievo": None,
    "toggle_fattore_inline_mobile": False,
    "fc_riassunto_contatori": None,

    # Flag stima su range
    "stima_cautelativa_beta": True,
    "range_unico_beta": True,
    "ta_range_toggle_beta": True,
    "fc_manual_range_beta": True,
    "fc_suggested_vals": [],
    "peso_stimato_beta": True,
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

# Garantisce TM fisso
st.session_state["tm_val"] = 37.2

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _safe_int(x):
    try:
        return int(x)
    except Exception:
        return 0

def _label(text, hint=None):
    if hint:
        st.markdown(f"<div class='tight-label'>{text} <span class='hint'>{hint}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='tight-label'>{text}</div>", unsafe_allow_html=True)

def _to_float_or_none(s):
    try:
        if s is None:
            return None
        s = str(s).strip().replace(",", ".")
        return float(s) if s != "" else None
    except Exception:
        return None

def _sig_val(x):
    return "∅" if x is None else x

# number_input che non collide con Session State logico
def _number_or_text(label, state_key, widget_key, text_key, hint=None, step=0.1, fmt="%.1f"):
    _label(label, hint)
    try:
        val = st.number_input(
            "", value=st.session_state.get(state_key, None),
            step=step, format=fmt, key=widget_key, label_visibility="collapsed"
        )
        if val is None:
            return None
        return float(val)
    except Exception:
        raw = st.text_input(
            "", value="" if st.session_state.get(text_key) in (None, "") else str(st.session_state.get(text_key)),
            key=text_key, label_visibility="collapsed", placeholder=""
        )
        return _to_float_or_none(raw)

# ------------------------------------------------------------
# Data/Ora ispezione (Europe/Zurich)
# ------------------------------------------------------------
try:
    from zoneinfo import ZoneInfo
    _TZ_CH = ZoneInfo("Europe/Zurich")
except Exception:
    try:
        import pytz
        _TZ_CH = pytz.timezone("Europe/Zurich")
    except Exception:
        _TZ_CH = None

now_ch = datetime.datetime.now(_TZ_CH) if _TZ_CH else datetime.datetime.utcnow()

st.toggle("Aggiungi data/ora rilievi tanatologici", key="usa_orario_custom")

if st.session_state["usa_orario_custom"]:
    if st.session_state.get("input_data_rilievo") is None:
        st.session_state["input_data_rilievo"] = now_ch.date()
    if not st.session_state.get("input_ora_rilievo"):
        st.session_state["input_ora_rilievo"] = now_ch.strftime("%H:%M")

    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.date_input(
            "Data ispezione legale",
            value=st.session_state["input_data_rilievo"],
            label_visibility="collapsed",
            key="input_data_rilievo",
        )
    with c2:
        st.text_input(
            "Ora ispezione legale (HH:MM)",
            value=st.session_state["input_ora_rilievo"],
            label_visibility="collapsed",
            key="input_ora_rilievo",
        )
else:
    st.session_state["input_data_rilievo"] = None
    st.session_state["input_ora_rilievo"] = None

# ------------------------------------------------------------
# Ipostasi e rigidità
# ------------------------------------------------------------
_IPOSTASI_MOBILE = {
    "Ipostasi assenti": "Non ancora comparse",
    "Ipostasi almeno in parte migrabili": "Migrabili perlomeno parzialmente",
    "Ipostasi non migrabili": "Fisse",
    "IPOSTASI?": "Non valutate",
}
_RIGIDITA_MOBILE = {
    "Rigor assente": "Non ancora apprezzabile",
    "Rigor presente e in aumento": "Presente e in via di intensificazione e generalizzazione",
    "Rigor ubiquitario e massimo": "Presente, intensa e generalizzata",
    "Rigor in risoluzione": "In via di risoluzione",
    "Rigor risolto": "Risolta",
    "RIGOR MORTIS?": "Non valutata",
}
c_ip, c_rg = st.columns(2, gap="small")
with c_ip:
    ip_keys = list(_IPOSTASI_MOBILE.keys())
    scelta_ipostasi_lbl = st.selectbox(
        "Macchie ipostatiche", ip_keys,
        index=(ip_keys.index("IPOSTASI?") if "IPOSTASI?" in ip_keys else 0),
        key="selettore_macchie_mobile", label_visibility="collapsed",
    )
    selettore_macchie = _IPOSTASI_MOBILE[scelta_ipostasi_lbl]
with c_rg:
    rg_keys = list(_RIGIDITA_MOBILE.keys())
    scelta_rigidita_lbl = st.selectbox(
        "Rigidità cadaverica", rg_keys,
        index=(rg_keys.index("RIGOR MORTIS?") if "RIGOR MORTIS?" in rg_keys else 0),
        key="selettore_rigidita_mobile", label_visibility="collapsed",
    )
    selettore_rigidita = _RIGIDITA_MOBILE[scelta_rigidita_lbl]

# ------------------------------------------------------------
# 1) Campi di input: RT / TA / Peso con chiavi widget dedicate
# ------------------------------------------------------------
c_rt, c_ta, c_w, c_fc = st.columns(4, gap="small")

with c_rt:
    rt_val_parsed = _number_or_text(
        "T. rettale (°C)",
        state_key="rt_val",
        widget_key="rt_val_widget",
        text_key="rt_val_str",
        step=0.1, fmt="%.1f"
    )

with c_ta:
    ta_val_parsed = _number_or_text(
        "T. ambientale media (°C)",
        state_key="ta_base_val",
        widget_key="ta_base_val_widget",
        text_key="ta_base_val_str",
        step=0.1, fmt="%.1f"
    )

with c_w:
    peso_parsed = _number_or_text(
        "Peso (kg)",
        state_key="peso",
        widget_key="peso_widget",
        text_key="peso_str",
        step=1.0, fmt="%.1f"
    )

with c_fc:
    _label("Fattore di correzione (FC)")
    fc_placeholder = st.empty()

# Persisti valori parsati su chiavi logiche
st.session_state["rt_val"] = rt_val_parsed
st.session_state["ta_base_val"] = ta_val_parsed
st.session_state["peso"] = peso_parsed

# ------------------------------------------------------------
# 2) Toggle “Suggerisci FC”
# ------------------------------------------------------------
st.toggle("Suggerisci FC",
          value=st.session_state.get("toggle_fattore_inline_mobile", False),
          key="toggle_fattore_inline_mobile")
st.session_state["toggle_fattore"] = st.session_state["toggle_fattore_inline_mobile"]

# ------------------------------------------------------------
# Pannello “Suggerisci FC”
# ------------------------------------------------------------
def pannello_suggerisci_fc_mobile(peso_default: float = 70.0, key_prefix: str = "fcpanel_m"):
    def k(name: str) -> str: return f"{key_prefix}_{name}"

    stato_label = st.radio("", ["Corpo asciutto", "Bagnato", "Immerso"],
                           index=0, horizontal=True, key=k("radio_stato_corpo"),
                           label_visibility="collapsed")
    stato_corpo = "Asciutto" if stato_label == "Corpo asciutto" else stato_label

    try:
        tabella2 = load_tabelle_correzione()
    except Exception:
        tabella2 = None

    # Peso robusto per FC
    if st.session_state.get("peso") in (None, 0) or (st.session_state.get("peso") or 0) <= 0:
        st.session_state["peso"] = 70.0

    peso_eff = st.session_state.get("peso") or peso_default
    try:
        peso_eff = float(peso_eff)
        if peso_eff <= 0:
            peso_eff = float(peso_default)
    except Exception:
        peso_eff = float(peso_default)

    if stato_corpo == "Immerso":
        acqua_label = st.radio("", ["In acqua stagnante", "In acqua corrente"],
                               index=0, horizontal=True, key=k("radio_acqua"),
                               label_visibility="collapsed")
        acqua_mode = "stagnante" if acqua_label == "In acqua stagnante" else "corrente"

        result = compute_factor(
            stato="Immerso", acqua=acqua_mode, counts=DressCounts(),
            superficie_display=None, correnti_aria=False,
            peso=peso_eff, tabella2_df=tabella2
        )
        st.session_state["__next_fc"] = round(float(result.fattore_finale), 2)
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
        peso=peso_eff, tabella2_df=tabella2
    )
    st.session_state["__next_fc"] = round(float(result.fattore_finale), 2)

if st.session_state.get("toggle_fattore_inline_mobile", False):
    with stylable_container(
        key="fcwrap_mobile",
        css_styles="""
        {
          background: #f0f6ff;
          border-radius: 4px;
          padding: 8px;
          margin: 4px 0;
        }
        @media (prefers-color-scheme: dark){
          [data-stylable-key="fcwrap_mobile"] {
            background: #0f2036;
          }
        }
        /* compattazione SOLO dentro il pannello */
        [data-stylable-key="fcwrap_mobile"] div[data-testid="stVerticalBlock"]{margin:0!important}
        [data-stylable-key="fcwrap_mobile"] div[data-testid="stVerticalBlock"]>div{margin:2px 0!important}
        """
    ):
        pannello_suggerisci_fc_mobile(
            peso_default=70.0 if st.session_state.get("peso") in (None, 0) else st.session_state.get("peso"),
            key_prefix="fcpanel_mobile"
        )


# ------------------------------------------------------------
# Applica eventuale FC calcolato PRIMA di creare il widget FC
# ------------------------------------------------------------
if "__next_fc" in st.session_state:
    st.session_state["fattore_correzione"] = st.session_state.pop("__next_fc")

# Crea ORA il widget FC senza passare "value" per evitare conflitti
with c_fc:
    fc_placeholder.number_input(
        "", step=0.1, format="%.2f",
        key="fattore_correzione", label_visibility="collapsed"
    )

# ------------------------------------------------------------
# 3) Pulsante finale
# ------------------------------------------------------------
clicked = st.button("STIMA EPOCA DECESSO", key="btn_stima_mobile", use_container_width=True, type="primary")

# Link “Raccomandazioni” cliccabile (popover)
with st.popover("Raccomandazioni", use_container_width=False):
    st.markdown(_raccomandazioni_html(), unsafe_allow_html=True)

# ------------------------------------------------------------
# Firma input e range fissi mobile
# ------------------------------------------------------------
def _inputs_signature_mobile(selettore_macchie: str, selettore_rigidita: str):
    return (
        bool(st.session_state.get("usa_orario_custom", False)),
        str(st.session_state.get("input_data_rilievo")),
        str(st.session_state.get("input_ora_rilievo")),
        selettore_macchie,
        selettore_rigidita,
        _sig_val(st.session_state.get("rt_val")),
        _sig_val(st.session_state.get("ta_base_val")),
        _sig_val(st.session_state.get("peso")),
        _sig_val(st.session_state.get("fattore_correzione")),
        37.2,
    )

# Range TA e FC
ta_center = st.session_state.get("ta_base_val")
fc_center = float(st.session_state.get("fattore_correzione", 1.0))

if ta_center is not None:
    try:
        ta_center = float(ta_center)
        st.session_state["Ta_min_beta"] = round(ta_center - 1.0, 2)
        st.session_state["Ta_max_beta"] = round(ta_center + 1.0, 2)
    except Exception:
        st.session_state.pop("Ta_min_beta", None)
        st.session_state.pop("Ta_max_beta", None)
else:
    st.session_state.pop("Ta_min_beta", None)
    st.session_state.pop("Ta_max_beta", None)

st.session_state["FC_min_beta"] = round(fc_center - 0.10, 2)
st.session_state["FC_max_beta"] = round(fc_center + 0.10, 2)

curr_sig = _inputs_signature_mobile(selettore_macchie, selettore_rigidita)
if "last_run_sig_mobile" not in st.session_state:
    st.session_state["last_run_sig_mobile"] = curr_sig

if clicked:
    st.session_state["run_stima_mobile"] = True
    st.session_state["last_run_sig_mobile"] = curr_sig

if st.session_state.get("run_stima_mobile") and st.session_state.get("last_run_sig_mobile") != curr_sig:
    st.session_state["run_stima_mobile"] = False

# ------------------------------------------------------------
# Output
# ------------------------------------------------------------
if st.session_state.get("run_stima_mobile"):
    input_rt = st.session_state.get("rt_val")
    input_ta = st.session_state.get("ta_base_val")
    input_w  = st.session_state.get("peso")

    no_rt = (input_rt is None) or (float(input_rt) <= 0)
    no_macchie = str(selettore_macchie).strip() in {"Non valutata", "Non valutate", "/"}
    no_rigidita = str(selettore_rigidita).strip() in {"Non valutata", "Non valutate", "/"}

    if no_rt and no_macchie and no_rigidita:
        st.warning("Nessun dato inserito per la stima")
        st.stop()

    considera_raffreddamento = (
        input_rt is not None and
        input_ta is not None and
        input_w is not None and input_w > 0
    )

    aggiorna_grafico(
        selettore_macchie=selettore_macchie,
        selettore_rigidita=selettore_rigidita,
        input_rt=(input_rt if considera_raffreddamento else None),
        input_ta=(input_ta if considera_raffreddamento else None),
        input_tm=(37.2 if considera_raffreddamento else None),
        input_w=(input_w if considera_raffreddamento else None),
        fattore_correzione=st.session_state.get("fattore_correzione", 1.0),
        widgets_parametri_aggiuntivi={},
        usa_orario_custom=st.session_state.get("usa_orario_custom"),
        input_data_rilievo=st.session_state.get("input_data_rilievo"),
        input_ora_rilievo=st.session_state.get("input_ora_rilievo"),
        alterazioni_putrefattive=False,
        skip_warnings=True,
    )

