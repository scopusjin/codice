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

# ------------------------------------------------------------
# Config + stato persistente
# ------------------------------------------------------------
st.set_page_config(page_title="STIMA EPOCA DECESSO - MSIL", layout="centered")

# --- CSS bottone evidenziato + sticky bar
st.markdown("""
<style>
.sticky-cta{position:sticky;bottom:0;z-index:999;background:rgba(255,255,255,.95);padding:10px 8px 14px 8px;border-top:1px solid #e0e0e0;}
div.stButton>button{width:100%!important;height:56px!important;font-size:1.05rem!important;font-weight:700!important;letter-spacing:.3px!important;border-radius:10px!important;box-shadow:0 4px 12px rgba(0,0,0,.12)!important;}
html[data-theme="light"] div.stButton>button{background:#1976d2!important;color:#fff!important;border:0!important;}
html[data-theme="dark"] div.stButton>button{background:#2196f3!important;color:#0b1020!important;border:0!important;}
div.stButton>button:hover{filter:brightness(1.06);}
</style>
""", unsafe_allow_html=True)

# defaults una sola volta
_defaults = {
    "run_stima_mobile": False,
    "show_avvisi": True,
    "rt_val": 35.0,
    "ta_base_val": 20.0,
    "peso": 70.0,
    "fattore_correzione": 1.0,   # step 0.1
    "usa_orario_custom": False,
    "input_data_rilievo": None,
    "input_ora_rilievo": None,
    "toggle_fattore_inline_mobile": False,
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

# ------------------------------------------------------------
# Helpers UI
# ------------------------------------------------------------
def _fc_palette():
    base = (st.get_option("theme.base") or "light").lower()
    return dict(
        bg=("#0d2a47" if base == "dark" else "#e8f0fe"),
        text=("#d6e9ff" if base == "dark" else "#0d47a1"),
        border="#1976d2",
        note=("#a7c7ff" if base == "dark" else "#3f6fb5"),
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
            f'<div style="color:{pal["note"]};padding:8px 2px 0 2px;font-size:0.92em;">'
            f'Adattato per {peso_corrente:.1f} kg (valore per 70 kg: {f_base:.2f})'
            f'</div>'
        )
    st.markdown(main + side, unsafe_allow_html=True)

# ------------------------------------------------------------
# Data/Ora ispezione
# ------------------------------------------------------------
with st.container(border=True):
    st.toggle(
        "Aggiungi data/ora rilievi tanatologici",
        key="usa_orario_custom",
    )

    if st.session_state["usa_orario_custom"]:
        # auto-default se erano None/empty
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

# ------------------------------------------------------------
# Ipostasi e rigidità (versione mobile semplificata)
# ------------------------------------------------------------
_IPOSTASI_MOBILE = {
    "Assenti": "Non ancora comparse",
    "Almeno parzialmente migrabili": "Migrabili perlomeno parzialmente",
    "Fisse": "Fisse",
    "/": "Non valutate",
}

_RIGIDITA_MOBILE = {
    "Assente": "Non ancora apprezzabile",
    "Presente e in aumento": "Presente e in via di intensificazione e generalizzazione",
    "Completa e massima": "Presente, intensa e generalizzata",
    "In risoluzione": "In via di risoluzione",
    "Risolta": "Risolta",
    "/": "Non valutata",
}

with st.container(border=True):
    c1, c2 = st.columns(2, gap="small")
    with c1:
        ipostasi_options = list(_IPOSTASI_MOBILE.keys())
        ip_default_idx = ipostasi_options.index("/") if "/" in ipostasi_options else 0
        scelta_ipostasi_lbl = st.selectbox(
            "Macchie ipostatiche:",
            options=ipostasi_options,
            index=ip_default_idx,
            key="selettore_macchie_mobile",
        )
        selettore_macchie = _IPOSTASI_MOBILE[scelta_ipostasi_lbl]
    with c2:
        rigidita_options = list(_RIGIDITA_MOBILE.keys())
        rg_default_idx = rigidita_options.index("/") if "/" in rigidita_options else 0
        scelta_rigidita_lbl = st.selectbox(
            "Rigidità cadaverica:",
            options=rigidita_options,
            index=rg_default_idx,
            key="selettore_rigidita_mobile",
        )
        selettore_rigidita = _RIGIDITA_MOBILE[scelta_rigidita_lbl]

# ------------------------------------------------------------
# Temperature e parametri principali
# ------------------------------------------------------------
with st.container(border=True):
    # T. rettale
    st.markdown("<div style='font-size: 0.88rem;'>T. rettale (°C):</div>", unsafe_allow_html=True)
    input_rt = st.number_input(
        "T. rettale (°C):",
        value=st.session_state.get("rt_val", 35.0),
        step=0.1, format="%.1f",
        key="rt_val",
        label_visibility="collapsed",
    )

    st.markdown("""
    <style>
    .lbl{font-size:0.88rem;}
    .lbl .unc{font-size:0.78rem; color:#555; white-space:nowrap;}
    </style>
    """, unsafe_allow_html=True)

    # RIGA 1: Peso + T. ambientale
    c1, c2 = st.columns([1, 1], gap="small")
    with c1:
        st.markdown("<div class='lbl'>Peso (kg) <span class='unc'>— default ±3</span></div>", unsafe_allow_html=True)
        input_w = st.number_input(
            "Peso (kg):",
            value=st.session_state.get("peso", 70.0),
            step=1.0, format="%.1f",
            label_visibility="collapsed",
            key="peso"
        )
    with c2:
        st.markdown("<div class='lbl'>T. ambientale media (°C) <span class='unc'>— default ±1</span></div>", unsafe_allow_html=True)
        input_ta = st.number_input(
            "T. ambientale media (°C):",
            value=st.session_state.get("ta_base_val", 20.0),
            step=0.1, format="%.1f",
            label_visibility="collapsed",
            key="ta_base_val"
        )

    # RIGA 2: Fattore di correzione + switch suggerimento
    c3, c4 = st.columns([1, 1], gap="small")
    with c3:
        st.markdown("<div class='lbl'>Fattore di correzione <span class='unc'>— default ±0.10</span></div>", unsafe_allow_html=True)
        fattore_correzione = st.number_input(
            "Fattore di correzione (FC):",
            value=st.session_state.get("fattore_correzione", 1.0),
            step=0.1, format="%.2f",
            label_visibility="collapsed",
            key="fattore_correzione"
        )
    with c4:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        st.toggle(
            "Suggerisci fattore di correzione",
            value=st.session_state.get("toggle_fattore_inline_mobile", False),
            key="toggle_fattore_inline_mobile",
        )
        st.session_state["toggle_fattore"] = st.session_state["toggle_fattore_inline_mobile"]

# ------------------------------------------------------------
# Pannello “Suggerisci FC”
# ------------------------------------------------------------
def pannello_suggerisci_fc_mobile(peso_default: float = 70.0, key_prefix: str = "fcpanel_m"):
    def k(name: str) -> str:
        return f"{key_prefix}_{name}"

    def _apply_fc(val: float, riass: str | None) -> None:
        st.session_state["fattore_correzione"] = round(float(val), 2)
        st.session_state["fattori_condizioni_parentetica"] = None
        st.session_state["fattori_condizioni_testo"] = None
        st.session_state["fc_riassunto_contatori"] = riass
        st.session_state["toggle_fattore"] = False
        st.session_state["toggle_fattore_inline_mobile"] = False

    def _safe_int(x):
        try:
            return int(x)
        except Exception:
            return 0

    st.markdown("""
        <style>
          div[data-testid="stRadio"] > label {display:none !important;}
          div[data-testid="stRadio"] {margin-top:-6px; margin-bottom:-6px;}
          div[data-testid="stRadio"] div[role="radiogroup"] {gap:0.4rem;}
          div[data-testid="stToggle"] {margin-top:-6px; margin-bottom:-6px;}
          div[data-testid="stSlider"] {margin-top:-4px; margin-bottom:-2px;}
        </style>
    """, unsafe_allow_html=True)

    stato_label = st.radio(
        "Stato del corpo", ["Asciutto", "Bagnato", "Immerso"],
        index=0, horizontal=True, key=k("radio_stato_corpo")
    )
    stato_corpo = stato_label

    if stato_corpo == "Immerso":
        acqua_label = st.radio(
            "Condizione in acqua", ["In acqua stagnante", "In acqua corrente"],
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
        return

    col_corr, col_vest = st.columns([1.0, 1.3])
    with col_corr:
        corr_placeholder = st.empty()
    with col_vest:
        toggle_vestito = st.toggle(
            "Vestiti/coperte su addome/bacino?",
            value=st.session_state.get(k("toggle_vestito"), False),
            key=k("toggle_vestito")
        )

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

        rows = [{"Voce": nome, "Numero?": val} for nome, val in defaults.items()]
        df = pd.DataFrame(rows)

        st.markdown(
            """
            <style>
            div[data-testid="stDataEditor"] thead {display:none !important;}
            div[data-testid="stDataEditor"] [role="columnheader"] {display:none !important;}
            div[data-testid="stDataEditor"] .column-header {display:none !important;}
            [data-testid="stElementToolbar"] {display:none !important;}
            </style>
            """,
            unsafe_allow_html=True
        )

        edited = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
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
        nudo_eff = (
            (not toggle_vestito)
            or (counts.sottili == counts.spessi == counts.coperte_medie == counts.coperte_pesanti == 0)
        )
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

# Toggle pannello Suggerisci FC
if st.session_state.get("toggle_fattore", False):
    with st.container(border=True):
        pannello_suggerisci_fc_mobile(
            peso_default=st.session_state.get("peso", 70.0),
            key_prefix="fcpanel_mobile"
        )

# --- Firma degli input (mobile) ---
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

# ------------------------------------------------------------
# Delta range fissi lato mobile
# ------------------------------------------------------------
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

# --- Calcolo firma corrente ---
curr_sig = _inputs_signature_mobile(selettore_macchie, selettore_rigidita)
if "last_run_sig_mobile" not in st.session_state:
    st.session_state["last_run_sig_mobile"] = curr_sig

# ------------------------------------------------------------
# Bottone e invalidazione output
# ------------------------------------------------------------

with st.container():
    st.markdown('<div class="sticky-cta">', unsafe_allow_html=True)
    clicked = st.button(
        "STIMA EPOCA DECESSO",
        key="btn_stima_mobile",
        use_container_width=True,
        type="primary",
    )
    st.markdown('</div>', unsafe_allow_html=True)

if clicked:
    st.session_state["run_stima_mobile"] = True
    st.session_state["last_run_sig_mobile"] = curr_sig

if st.session_state.get("run_stima_mobile") and st.session_state.get("last_run_sig_mobile") != curr_sig:
    st.session_state["run_stima_mobile"] = False


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
