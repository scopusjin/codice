# pages/app_mobile.py
# -*- coding: utf-8 -*-
import datetime
import textwrap
import pandas as pd
import streamlit as st
from app import i18n
from app.theme import apply_theme, warn_box
from app.theme import fc_panel_start
from app.full_factor_panel import pannello_suggerisci_fc_mobile
from app.mobile_shell import install_minimal_mobile_shell


from app.graphing import aggiorna_grafico
from app.data_sources import load_tabelle_correzione
from app.factor_calc import (DressCounts, compute_factor, SURF_DISPLAY_ORDER, fattore_vestiti_coperte, floor_to_step)
from app.msil_tanatology import (
    MSIL_LIVOR_STATE_BY_LABEL,
    MSIL_RIGOR_STATE_BY_LABEL,
    msil_livor_legacy_value,
    msil_rigor_legacy_value,
)
from app.factor_ui_states import (
    LAYER_THIN,
    LAYER_THICK,
    BLANKET_MEDIUM,
    BLANKET_HEAVY,
)
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
from app.surface_ui_states import SURFACE_THICK_METAL_OUTDOOR

# ------------------------------------------------------------
# Config pagina
# ------------------------------------------------------------
st.set_page_config(
    page_title=i18n.ui_text("msil.page_title"),
    layout="centered",
    initial_sidebar_state="collapsed",
)
apply_theme()
install_minimal_mobile_shell()
# ------------------------------------------------------------
# CSS compatto + nascondi header/footer/badge
# ------------------------------------------------------------
st.markdown("""
<style>
/* Padding pagina: la cornice mobile condivisa conserva soltanto il comando
   nativo della sidebar nell'angolo superiore sinistro. */
section.main, div.block-container{margin-top:0!important}

/* Titolo reale della modalità sopralluogo */
.mortem-msil-page-title{
  margin:0 0 .12rem 0!important;
  padding:0!important;
  font-size:1.05rem!important;
  font-weight:650!important;
  line-height:1.05!important;
}
[data-testid="stElementContainer"]:has(.mortem-msil-page-title){
  margin:0!important;
  padding:0!important;
}

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

/* Etichette compatte */
.tight-label{margin:0!important;padding:0!important;line-height:1.05}
.tight-label p{margin:0!important}
.hint{font-size:.72rem;opacity:.75;margin-left:.25rem}

/* Pulsanti */
div.stButton{margin:0!important}
div.stButton>button{min-height:34px;height:34px;margin:0!important}

/* Nascondi footer/badge Streamlit */
#stDecoration,[data-testid="stDecoration"],
[data-testid="viewerBadge"],a[data-testid="viewerBadge"],
[class^="viewerBadge_"],[class*=" viewerBadge_"],
a[href^="https://streamlit.io/cloud"], a[href^="https://share.streamlit.io"]{display:none!important;}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="mortem-msil-page-title">Stima epoca decesso durante ispezione legale</div>',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Raccomandazioni helper + stile popover
# ------------------------------------------------------------

def _raccomandazioni_html() -> str:
    return i18n.ui_text("msil.recommendations_html")

st.markdown(
    textwrap.dedent("""
    <style>
    /* link popover blu tipo link */
    div[data-testid="stPopover"] button {
        background:none!important;
        border:none!important;
        color: #1976d2 !important;
        font-size:0.9rem!important;
        padding:0!important;
        margin:6px 0!important;
        text-decoration:none!important;
        cursor:pointer;
    }
    /* niente limite di altezza al contenuto del popover */
    div[data-testid="stPopoverContent"] { max-height:none!important; }
    </style>
    """),
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
st.session_state["__desc_dettagliate_html"] = ""
# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


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

def _number_or_text(label, state_key, widget_key, text_key, hint=None, step=0.1, fmt="%.1f",
                    min_value=None, max_value=None):
    _label(label, hint)
    try:
        val = st.number_input(
            "", value=st.session_state.get(state_key, None),
            step=step, format=fmt, key=widget_key, label_visibility="collapsed",
            min_value=min_value, max_value=max_value
        )
        if val is None:
            return None
        return float(val)
    except Exception:
        raw = st.text_input(
            "", value="" if st.session_state.get(text_key) in (None, "") else str(st.session_state.get(text_key)),
            key=text_key, label_visibility="collapsed", placeholder=""
        )
        v = _to_float_or_none(raw)
        if v is None:
            return None
        if min_value is not None and v < min_value: v = float(min_value)
        if max_value is not None and v > max_value: v = float(max_value)
        return v


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

st.toggle(i18n.ui_text("msil.add_datetime"), key="usa_orario_custom")

if not st.session_state["usa_orario_custom"]:
    # rimuovi le chiavi per avere default freschi al prossimo ON
    st.session_state.pop("input_data_rilievo", None)
    st.session_state.pop("input_ora_rilievo", None)

if st.session_state["usa_orario_custom"]:
    # inizializza se mancanti o falsy
    if not st.session_state.get("input_data_rilievo"):
        st.session_state["input_data_rilievo"] = now_ch.date()
    if not st.session_state.get("input_ora_rilievo"):
        st.session_state["input_ora_rilievo"] = now_ch.strftime("%H:%M")

    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.date_input(
            i18n.ui_text("msil.inspection_date"),
            key="input_data_rilievo",
            label_visibility="collapsed"
        )
    with c2:
        st.text_input(
            i18n.ui_text("msil.inspection_time"),
            key="input_ora_rilievo",
            label_visibility="collapsed"
        )

# ------------------------------------------------------------
# Ipostasi e rigidità
# ------------------------------------------------------------
_IPOSTASI_MOBILE = MSIL_LIVOR_STATE_BY_LABEL
_RIGIDITA_MOBILE = MSIL_RIGOR_STATE_BY_LABEL

c_ip, c_rg = st.columns(2, gap="small")
with c_ip:
    ip_keys = list(_IPOSTASI_MOBILE.keys())
    scelta_ipostasi_lbl = st.selectbox(
        i18n.ui_text("msil.livor_select_label"), ip_keys,
        index=(ip_keys.index("🩸 IPOSTASI?") if "🩸 IPOSTASI?" in ip_keys else 0),
        key="selettore_macchie_mobile", label_visibility="collapsed",
    )
    selettore_macchie = msil_livor_legacy_value(scelta_ipostasi_lbl)
with c_rg:
    rg_keys = list(_RIGIDITA_MOBILE.keys())
    scelta_rigidita_lbl = st.selectbox(
        i18n.ui_text("msil.rigor_select_label"), rg_keys,
        index=(rg_keys.index("💪🏻 RIGOR MORTIS?") if "💪🏻 RIGOR MORTIS?" in rg_keys else 0),
        key="selettore_rigidita_mobile", label_visibility="collapsed",
    )
    selettore_rigidita = msil_rigor_legacy_value(scelta_rigidita_lbl)

# ------------------------------------------------------------
# 1) Campi di input: RT / TA / Peso con chiavi widget dedicate
# ------------------------------------------------------------
c_rt, c_ta, c_w, c_fc = st.columns(4, gap="small")

with c_rt:
    rt_val_parsed = _number_or_text(
        i18n.ui_text("msil.rectal_temp"),
        state_key="rt_val",
        widget_key="rt_val_widget",
        text_key="rt_val_str",
        step=0.1, fmt="%.1f",
        min_value=5.0, max_value=42.0
    )

with c_ta:
    ta_val_parsed = _number_or_text(
        i18n.ui_text("msil.ta_mean"),
        state_key="ta_base_val",
        widget_key="ta_base_val_widget",
        text_key="ta_base_val_str",
        step=0.1, fmt="%.1f",
        min_value=-5.0, max_value=40.0
    )

with c_w:
    peso_parsed = _number_or_text(
        i18n.ui_text("msil.weight"),
        state_key="peso",
        widget_key="peso_widget",
        text_key="peso_str",
        step=1.0, fmt="%.1f",
        min_value=3.0, max_value=160.0
    )

with c_fc:
    _label(i18n.ui_text("msil.fc_label"))
    fc_placeholder = st.empty()

# Persisti valori parsati su chiavi logiche
st.session_state["rt_val"] = rt_val_parsed
st.session_state["ta_base_val"] = ta_val_parsed
st.session_state["peso"] = peso_parsed

# ------------------------------------------------------------
# 2) Toggle “Suggerisci FC”
# ------------------------------------------------------------
st.toggle(i18n.ui_text("msil.suggest_fc"),
          value=st.session_state.get("toggle_fattore_inline_mobile", False),
          key="toggle_fattore_inline_mobile")
st.session_state["toggle_fattore"] = st.session_state["toggle_fattore_inline_mobile"]

# ------------------------------------------------------------
# Pannello “Suggerisci FC”
# ------------------------------------------------------------
if st.session_state.get("toggle_fattore_inline_mobile", False):
    with fc_panel_start():
        pannello_suggerisci_fc_mobile(
            peso_default=70.0 if st.session_state.get("peso") in (None, 0) else st.session_state.get("peso"),
            key_prefix="fcpanel_mobile"
        )

# ------------------------------------------------------------
# Applica eventuale FC calcolato PRIMA di creare il widget FC
# ------------------------------------------------------------
if "__next_fc" in st.session_state:
    v = float(st.session_state.pop("__next_fc"))
    st.session_state["fattore_correzione"] = floor_to_step(v)

# Callback per normalizzare l'input FC su step 0,05 e chiudere il pannello "Suggerisci FC"
def _normalize_fc_callback():
    try:
        v = float(st.session_state.get("fattore_correzione", 1.0))
        st.session_state["fattore_correzione"] = floor_to_step(v)  # arrotonda per difetto a 0,05
    except Exception:
        return
    # chiudi eventuali pannelli "Suggerisci FC" aperti
    st.session_state["toggle_fattore_inline_mobile"] = False  # toggle del pannello mobile
    st.session_state["toggle_fattore"] = False                # flag usato per mostrare il pannello
    st.session_state["toggle_fattore_inline"] = False         # compatibilità con altre viste
    st.session_state["toggle_fattore_inline_std"] = False     # compatibilità con vista standard


# Crea ORA il widget FC senza passare "value" per evitare conflitti
with c_fc:
    fc_placeholder.number_input(
        "", step=0.05, format="%.2f",
        min_value=0.30, max_value=3.00,
        key="fattore_correzione", label_visibility="collapsed",
        on_change=_normalize_fc_callback
    )

# ------------------------------------------------------------
# 3) Pulsante finale
# ------------------------------------------------------------
clicked = st.button(i18n.ui_text("msil.estimate_button"), key="btn_stima_mobile", use_container_width=True, type="primary")

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

st.session_state["selettore_macchie"] = selettore_macchie
st.session_state["selettore_rigidita"] = selettore_rigidita

with st.popover(i18n.ui_text("msil.recommendations_button")):
    st.markdown(_raccomandazioni_html(), unsafe_allow_html=True)
