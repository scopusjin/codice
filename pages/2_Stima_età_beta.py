# pages/2_Stima_età_beta.py

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

# NEW (beta)
from app.cautelativa import compute_raffreddamento_cautelativo



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
st.set_page_config(page_title="Mor-tem — BETA", layout="centered", initial_sidebar_state="expanded")

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

# Titolo
st.markdown("<h5 style='margin-top:0; margin-bottom:10px;'>Stima epoca decesso — BETA</h5>", unsafe_allow_html=True)

# --- Definizione Widget (Streamlit) ---
with st.container(border=True):
    # 📌 1. Data e ora ispezione legale (nascosti di default)
    usa_orario_custom = st.toggle("Aggiungi data/ora rilievo dei dati tanatologici", value=False, key="usa_orario_custom")

    if usa_orario_custom:
        col1, col2 = st.columns(2, gap="small")
        with col1:
            input_data_rilievo = st.date_input(
                "Data ispezione legale:",
                value=datetime.date.today(),
                label_visibility="collapsed"
            )
        with col2:
            input_ora_rilievo = st.text_input(
                "Ora ispezione legale (HH:MM):",
                value="00:00",
                label_visibility="collapsed"
            )
    else:
        input_data_rilievo = None
        input_ora_rilievo = None

# 📌 2. Ipostasi e rigidità — RIQUADRO
with st.container(border=True):
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>Ipostasi:</div>", unsafe_allow_html=True)
        selettore_macchie = st.selectbox("Macchie ipostatiche:", options=list(opzioni_macchie.keys()), label_visibility="collapsed")
    with col2:
        st.markdown("<div style='font-size: 0.88rem;'>Rigidità cadaverica:</div>", unsafe_allow_html=True)
        selettore_rigidita = st.selectbox("Rigidità cadaverica:", options=list(opzioni_rigidita.keys()), label_visibility="collapsed")

# 📌 3–4. Temperature + Peso/Fattore — RIQUADRO
with st.container(border=True):
    # 📌 3. Temperature
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>T. rettale (°C):</div>", unsafe_allow_html=True)
        input_rt = st.number_input("T. rettale (°C):", value=35.0, step=0.1, format="%.1f", label_visibility="collapsed")
    with col2:
        st.markdown("<div style='font-size: 0.88rem;'>T. ambientale media (°C):</div>", unsafe_allow_html=True)
        input_ta = st.number_input("T. ambientale (°C):", value=20.0, step=0.1, format="%.1f", label_visibility="collapsed")
    with col3:
        st.markdown("<div style='font-size: 0.88rem;'>T. ante-mortem stimata (°C):</div>", unsafe_allow_html=True)
        input_tm = st.number_input("T. ante-mortem stimata (°C):", value=37.2, step=0.1, format="%.1f", label_visibility="collapsed")

    # 📌 4. Peso + FC + "Suggerisci" + (NEW) Stima cautelativa (beta)
    col1, col2 = st.columns([1, 3], gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>Peso corporeo (kg):</div>", unsafe_allow_html=True)
        input_w = st.number_input("Peso (kg):", value=70.0, step=1.0, format="%.1f", label_visibility="collapsed")
        st.session_state["peso"] = input_w

    with col2:
        subcol1, subcol2 = st.columns([1.5, 1], gap="small")
        with subcol1:
            st.markdown("<div style='font-size: 0.88rem;'>Fattore di correzione (FC):</div>", unsafe_allow_html=True)
            fattore_correzione = st.number_input(
                "Fattore di correzione:",
                step=0.1,
                format="%.2f",
                label_visibility="collapsed",
                key="fattore_correzione"
            )
        with subcol2:
            mostra_fattore = st.toggle(
                "Suggerisci FC",
                value=st.session_state.get("toggle_fattore", False),
                key="toggle_fattore"
            )

# === NEW: Pannello “Stima cautelativa (beta)” ===
st.toggle(
    "Stima cautelativa (beta)",
    value=st.session_state.get("stima_cautelativa_beta", False),
    key="stima_cautelativa_beta"
)
stima_cautelativa_beta = st.session_state["stima_cautelativa_beta"]

if stima_cautelativa_beta:
    cc1, cc2 = st.columns(2, gap="small")
    with cc1:
        Ta_min = st.number_input("Ta minima (°C)", value=st.session_state.get("Ta_min_beta", max(input_ta - 1.0, -50.0)), step=0.1, format="%.1f")
        st.session_state["Ta_min_beta"] = Ta_min
    with cc2:
        Ta_max = st.number_input("Ta massima (°C)", value=st.session_state.get("Ta_max_beta", input_ta + 1.0), step=0.1, format="%.1f")
        st.session_state["Ta_max_beta"] = Ta_max

    cc3, cc4 = st.columns(2, gap="small")
    with cc3:
        FC_min = st.number_input("FC minimo", value=st.session_state.get("FC_min_beta", max(st.session_state.get("fattore_correzione", 1.0) - 0.1, 0.01)), step=0.01, format="%.2f")
        st.session_state["FC_min_beta"] = FC_min
    with cc4:
        FC_max = st.number_input("FC massimo", value=st.session_state.get("FC_max_beta", st.session_state.get("fattore_correzione", 1.0) + 0.1), step=0.01, format="%.2f")
        st.session_state["FC_max_beta"] = FC_max

    st.toggle(
        "Peso corporeo stimato ±3 kg",
        value=st.session_state.get("peso_stimato_beta", False),
        key="peso_stimato_beta"
    )
else:
    for k in ("Ta_min_beta","Ta_max_beta","FC_min_beta","FC_max_beta","peso_stimato_beta"):
        st.session_state.pop(k, None)

# --- Pannello “Suggerisci FC” (identico alla app principale) ---
def pannello_suggerisci_fc(peso_default: float = 70.0):
    import streamlit as st
    st.markdown(
        """
        <style>
          div[data-testid="stRadio"] > label {display:none !important;}
          div[data-testid="stRadio"] {margin-top:-14px; margin-bottom:-10px;}
          div[data-testid="stRadio"] div[role="radiogroup"] {gap:0.4rem;}
          div[data-testid="stToggle"] {margin-top:-6px; margin-bottom:-6px;}
          div[data-testid="stSlider"] {margin-top:-4px; margin-bottom:-2px;}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Stato corpo
    stato_label = st.radio("dummy", ["Corpo asciutto", "Bagnato", "Immerso"],
                           index=0, horizontal=True, key="radio_stato_corpo")
    stato_corpo = ("Asciutto" if stato_label == "Corpo asciutto"
                   else ("Bagnato" if stato_label == "Bagnato" else "Immerso"))

    # Se Immerso: calcolo diretto
    if stato_corpo == "Immerso":
        acqua_label = st.radio("dummy", ["In acqua stagnante", "In acqua corrente"],
                               index=0, horizontal=True, key="radio_acqua")
        acqua_mode = "stagnante" if acqua_label == "In acqua stagnante" else "corrente"

        try:
            tabella2 = load_tabelle_correzione()
        except Exception:
            tabella2 = None

        result = compute_factor(
            stato="Immerso",
            acqua=acqua_mode,
            counts=DressCounts(),
            superficie_display=None,
            correnti_aria=False,
            peso=float(st.session_state.get("peso", peso_default)),
            tabella2_df=tabella2
        )
        peso_corrente = float(st.session_state.get("peso", peso_default))
        _fc_box(result.fattore_finale, result.fattore_base, peso_corrente)

        def _apply(val, riass):
            st.session_state["fattore_correzione"] = round(float(val), 2)
            st.session_state["fattori_condizioni_parentetica"] = None
            st.session_state["fattori_condizioni_testo"] = None
            st.session_state["toggle_fattore"] = False
            st.session_state["fc_riassunto_contatori"] = riass
        st.button("✅ Usa questo fattore", on_click=_apply,
                  args=(result.fattore_finale, result.riassunto),
                  use_container_width=True)
        return

    # Non Immerso
    col_corr, col_vest = st.columns([1.0, 1.3])
    with col_corr:
        corr_placeholder = st.empty()
    with col_vest:
        toggle_vestito = st.toggle(
            "Vestito/coperto?",
            value=st.session_state.get("toggle_vestito", False),
            key="toggle_vestito"
        )

    n_sottili = n_spessi = n_cop_medie = n_cop_pesanti = 0
    if toggle_vestito:
        col_layers, col_blankets = st.columns(2)
        with col_layers:
            n_sottili = st.slider("Strati leggeri (indumenti o teli sottili)", 0, 8,
                                  st.session_state.get("strati_sottili", 0), key="strati_sottili")
            n_spessi = st.slider("Strati pesanti (indumenti o teli spessi)", 0, 6,
                                 st.session_state.get("strati_spessi", 0), key="strati_spessi")
        with col_blankets:
            if stato_corpo == "Asciutto":
                n_cop_medie = st.slider("Coperte di medio spessore", 0, 5,
                                        st.session_state.get("coperte_medie", 0), key="coperte_medie")
                n_cop_pesanti = st.slider("Coperte pesanti", 0, 5,
                                          st.session_state.get("coperte_pesanti", 0), key="coperte_pesanti")

    counts = DressCounts(
        sottili=n_sottili, spessi=n_spessi,
        coperte_medie=n_cop_medie, coperte_pesanti=n_cop_pesanti
    )

    superficie_display_selected = "/"
    if stato_corpo == "Asciutto":
        nudo_eff = ((not toggle_vestito)
                    or (counts.sottili == counts.spessi == counts.coperte_medie == counts.coperte_pesanti == 0))
        options_display = SURF_DISPLAY_ORDER.copy()
        if not nudo_eff:
            options_display = [o for o in options_display if o != "Superficie metallica spessa (all’aperto)"]
        prev_display = st.session_state.get("superficie_display_sel")
        if prev_display not in options_display:
            prev_display = options_display[0]
        superficie_display_selected = st.selectbox(
            "Superficie di appoggio",
            options_display,
            index=options_display.index(prev_display),
            key="superficie_display_sel"
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
                value=st.session_state.get("toggle_correnti_fc", False),
                key="toggle_correnti_fc",
                disabled=False
            )

    try:
        tabella2 = load_tabelle_correzione()
    except Exception:
        tabella2 = None

    result = compute_factor(
        stato=stato_corpo,
        acqua=None,
        counts=counts,
        superficie_display=superficie_display_selected if stato_corpo == "Asciutto" else None,
        correnti_aria=correnti_presenti,
        peso=float(st.session_state.get("peso", peso_default)),
        tabella2_df=tabella2
    )
    peso_corrente = float(st.session_state.get("peso", peso_default))
    _fc_box(result.fattore_finale, result.fattore_base, peso_corrente)

    def _apply(val, riass):
        st.session_state["fattore_correzione"] = round(float(val), 2)
        st.session_state["fattori_condizioni_parentetica"] = None
        st.session_state["fattori_condizioni_testo"] = None
        st.session_state["toggle_fattore"] = False
        st.session_state["fc_riassunto_contatori"] = riass
    st.button("✅ Usa questo fattore", on_click=_apply,
              args=(result.fattore_finale, result.riassunto),
              use_container_width=True)

if st.session_state.get("toggle_fattore", False):
    with st.container(border=True):
        pannello_suggerisci_fc(peso_default=st.session_state.get("peso", 70.0))

# Parametri aggiuntivi (identico alla app principale)
mostra_parametri_aggiuntivi = st.checkbox("Aggiungi dati tanatologici speciali")
widgets_parametri_aggiuntivi = {}

if mostra_parametri_aggiuntivi:
    with st.container(border=True):
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
                                st.image("https://raw.githubusercontent.com/scopusjin/codice/main/immagini/eccitabilit%C3%A0.PNG", width=400)
                            elif nome_parametro == "Eccitabilità elettrica peribuccale":
                                st.image("https://raw.githubusercontent.com/scopusjin/codice/main/immagini/peribuccale.PNG", width=300)
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

            if selettore != "Non valutata":
                chiave_checkbox = f"{nome_parametro}_diversa"
                colx1, colx2 = st.columns([0.2, 0.2], gap="small")
                with colx1:
                    st.markdown(
                        "<div style='font-size: 0.8em; color: orange; margin-bottom: 3px;'>"
                        "Il dato è stato valutato a un orario diverso rispetto a quello precedentemente indicato?"
                        "</div>",
                        unsafe_allow_html=True
                    )
                with colx2:
                    usa_orario_personalizzato = st.checkbox(label="", key=chiave_checkbox)

            if usa_orario_personalizzato:
                coly1, coly2 = st.columns(2)
                with coly1:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Data rilievo:</div>", unsafe_allow_html=True)
                    data_picker = st.date_input("Data rilievo:", value=input_data_rilievo, key=f"{nome_parametro}_data", label_visibility="collapsed")
                with coly2:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Ora rilievo:</div>", unsafe_allow_html=True)
                    ora_input = st.text_input("Ora rilievo (HH:MM):", value=input_ora_rilievo, key=f"{nome_parametro}_ora", label_visibility="collapsed")

            widgets_parametri_aggiuntivi[nome_parametro] = {
                "selettore": selettore,
                "data_rilievo": data_picker,
                "ora_rilievo": ora_input
            }

        chk_putrefattive = st.checkbox(
            "Alterazioni putrefattive?",
            value=st.session_state.get("alterazioni_putrefattive", False),
        )
        st.session_state["alterazioni_putrefattive"] = chk_putrefattive
else:
    st.session_state["alterazioni_putrefattive"] = False

# --- Firma degli input che influenzano la stima ---
def _inputs_signature():
    base = [
        st.session_state.get("usa_orario_custom", False),
        str(input_data_rilievo) if input_data_rilievo else None,
        str(input_ora_rilievo) if input_ora_rilievo else None,
        selettore_macchie,
        selettore_rigidita,
        float(input_rt) if input_rt is not None else None,
        float(input_ta) if input_ta is not None else None,
        float(input_tm) if input_tm is not None else None,
        float(input_w) if input_w is not None else None,
        float(st.session_state.get("fattore_correzione", 1.0)),
        bool(mostra_parametri_aggiuntivi),
        bool(st.session_state.get("alterazioni_putrefattive", False)),
    ]
    extra = []
    for nome_parametro, _ in dati_parametri_aggiuntivi.items():
        extra.append(st.session_state.get(f"{nome_parametro}_selector"))
        extra.append(st.session_state.get(f"{nome_parametro}_diversa"))
        extra.append(str(st.session_state.get(f"{nome_parametro}_data")) if st.session_state.get(f"{nome_parametro}_data") else None)
        extra.append(st.session_state.get(f"{nome_parametro}_ora"))

    # NEW: firma campi beta
    base.extend([
        bool(st.session_state.get("stima_cautelativa_beta", False)),
        st.session_state.get("Ta_min_beta"),
        st.session_state.get("Ta_max_beta"),
        st.session_state.get("FC_min_beta"),
        st.session_state.get("FC_max_beta"),
        bool(st.session_state.get("peso_stimato_beta", False)),
    ])
    return tuple(base + extra)

curr_sig = _inputs_signature()

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
    div.stButton > button:hover {
        background-color: #E3F2FD !important;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    clicked = st.button("STIMA EPOCA DECESSO", key="btn_stima")
    if clicked:
        st.session_state["show_results"] = True
        st.session_state["last_run_sig"] = curr_sig

prev_sig = st.session_state.get("last_run_sig")
if st.session_state.get("show_results", False) and prev_sig is not None and curr_sig != prev_sig:
    st.session_state["show_results"] = False

# ===== LOGICA PRINCIPALE =====
def aggiorna_grafico():
    # --- Raccolta messaggi per nuova UI compatta ---
    avvisi = []
    dettagli = []
    frase_finale_html = None
    frase_secondaria_html = None

    # --- Validazione Input Data/Ora Ispezione Legale ---
    usa_orario_custom = st.session_state.get("usa_orario_custom", False)

    if usa_orario_custom:
        if not input_data_rilievo or not input_ora_rilievo:
            st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Inserisci data e ora dell'ispezione legale.</p>", unsafe_allow_html=True)
            return
        try:
            ora_isp_obj = datetime.datetime.strptime(input_ora_rilievo, '%H:%M')
            minuti_isp = ora_isp_obj.minute
        except ValueError:
            st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Errore: formato ora ispezione legale non valido. Usa HH:MM (es. 14:30).</p>", unsafe_allow_html=True)
            return
        data_ora_ispezione_originale = datetime.datetime.combine(input_data_rilievo, ora_isp_obj.time())
        data_ora_ispezione = arrotonda_quarto_dora(data_ora_ispezione_originale)
    else:
        minuti_isp = 0
        data_ora_ispezione = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))

    # --- Recupero Valori Input per Calcoli ---
    Tr_val = input_rt
    Ta_val = input_ta
    T0_val = input_tm
    W_val = input_w
    CF_val = st.session_state.get("fattore_correzione", 1.0)

    # Validazioni base
    if W_val is None or W_val <= 0:
        st.error("⚠️ Peso non valido. Inserire un valore > 0 kg.")
        return
    if CF_val is None or CF_val <= 0:
        st.error("⚠️ Fattore di correzione non valido. Inserire un valore > 0.")
        return
    if any(v is None for v in [Tr_val, Ta_val, T0_val]):
        st.error("⚠️ Temperature mancanti.")
        return

    macchie_selezionata = selettore_macchie
    rigidita_selezionata = selettore_rigidita

    # ======= SWITCH: Henssge standard vs Stima cautelativa (beta) =======
    qd_threshold = 0.2 if Ta_val <= 23 else 0.5

    if st.session_state.get("stima_cautelativa_beta", False):
        # ---- CAUTELATIVA (beta) ----
        Ta_range = None
        CF_range = None
        if "Ta_min_beta" in st.session_state and "Ta_max_beta" in st.session_state:
            a, b = float(st.session_state["Ta_min_beta"]), float(st.session_state["Ta_max_beta"])
            if a > b: a, b = b, a
            Ta_range = (a, b)
        if "FC_min_beta" in st.session_state and "FC_max_beta" in st.session_state:
            a, b = float(st.session_state["FC_min_beta"]), float(st.session_state["FC_max_beta"])
            if a > b: a, b = b, a
            CF_range = (a, b)

        res = compute_raffreddamento_cautelativo(
            dt_ispezione=data_ora_ispezione,
            Ta_value=float(Ta_val),
            CF_value=float(CF_val),
            peso_kg=float(W_val),
            Ta_range=Ta_range,
            CF_range=CF_range,
            peso_stimato=bool(st.session_state.get("peso_stimato_beta", False)),
            mostra_tabella=False,
            applica_regola_48_inf=True,
            solver_kwargs={
                "Tr": float(Tr_val),
                "T0": float(T0_val),
                "round_minutes": int(st.session_state.get("henssge_round_minutes", 30)),
            },
        )
        # --- Usa il risultato cautelativo come "raffreddamento" per grafico/testi ---
        t_min_raff_hensge = float(res.ore_min)
        # Limite superiore: se è INF_HOURS -> consideralo "aperto"
        t_max_raff_hensge = np.nan if (not np.isfinite(res.ore_max) or res.ore_max >= INF_HOURS-1e-9) else float(res.ore_max)
        _tmed_raw = t_min_raff_hensge if np.isnan(t_max_raff_hensge) else 0.5*(t_min_raff_hensge + t_max_raff_hensge)
        t_med_raff_hensge_rounded_raw = float(_tmed_raw)
        t_med_raff_hensge_rounded = round_quarter_hour(_tmed_raw)
        Qd_val_check = res.qd_min if (res.qd_min is not None) else np.nan
        raffreddamento_calcolabile = True

        # Aggiungi il riepilogo testuale già pronto
        dettagli.append(res.summary_html)
        st.session_state["parentetica_extra"] = res.parentetica
        
       
    else:
        # ---- HENSSGE standard ----
        round_minutes = int(st.session_state.get("henssge_round_minutes", 30))
        t_med_raff_hensge_rounded, t_min_raff_hensge, t_max_raff_hensge, \
        t_med_raff_hensge_rounded_raw, Qd_val_check = calcola_raffreddamento(
            Tr_val, Ta_val, T0_val, W_val, CF_val,
            round_minutes=round_minutes
        )
        raffreddamento_calcolabile = not np.isnan(t_med_raff_hensge_rounded) and t_med_raff_hensge_rounded >= 0
        st.session_state["parentetica_extra"] = ""

    # --- Altri calcoli condivisi ---
    temp_difference_small = (Tr_val is not None and Ta_val is not None and (Tr_val - Ta_val) is not None and 0 <= (Tr_val - Ta_val) < 2.0)

    macchie_range_valido = macchie_selezionata != "Non valutabili/Non attendibili"
    macchie_range = opzioni_macchie.get(macchie_selezionata) if macchie_range_valido else (np.nan, np.nan)
    macchie_medi_range = macchie_medi.get(macchie_selezionata) if macchie_range_valido else None

    rigidita_range_valido = rigidita_selezionata != "Non valutabile/Non attendibile"
    rigidita_range = opzioni_rigidita.get(rigidita_selezionata) if rigidita_range_valido else (np.nan, np.nan)
    rigidita_medi_range = rigidita_medi.get(selettore_rigidita) if rigidita_range_valido else None

    parametri_aggiuntivi_da_considerare = []
    nota_globale_range_adattato = False

    for nome_parametro, widgets_param in widgets_parametri_aggiuntivi.items():
        stato_selezionato = widgets_param["selettore"]
        data_rilievo_param = widgets_param["data_rilievo"]
        ora_rilievo_param_str = widgets_param["ora_rilievo"]

        if stato_selezionato == "Non valutata":
            continue

        chiave_descrizione = stato_selezionato.split(':')[0].strip()

        if not ora_rilievo_param_str or ora_rilievo_param_str.strip() == "":
            ora_rilievo_time = data_ora_ispezione.time()
        else:
            try:
                ora_rilievo_time = datetime.datetime.strptime(ora_rilievo_param_str, '%H:%M').time()
            except ValueError:
                avvisi.append(f"⚠️ {nome_parametro}: formato ora di rilievo '{ora_rilievo_param_str}' non valido (usa HH:MM, es. 14:30) → parametro escluso dalla stima.")
                continue

        if data_rilievo_param is None:
            data_rilievo_param = data_ora_ispezione.date()

        if nome_parametro == "Eccitabilità elettrica peribuccale":
            chiave_descrizione = stato_selezionato.split(':')[0].strip()
        else:
            chiave_descrizione = stato_selezionato.strip()

        chiave_esatta = None
        for k in dati_parametri_aggiuntivi[nome_parametro]["range"].keys():
            if k.strip() == chiave_descrizione:
                chiave_esatta = k
                break

        range_valori = dati_parametri_aggiuntivi[nome_parametro]["range"].get(chiave_esatta)
        range_originale = range_valori

        if range_valori:
            descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(chiave_descrizione, f"Descrizione non trovata per lo stato '{stato_selezionato}'.")
            data_ora_param_raw = datetime.datetime.combine(data_rilievo_param, ora_rilievo_time)
            data_ora_param = arrotonda_quarto_dora(data_ora_param_raw)
            differenza_ore = (data_ora_param - data_ora_ispezione).total_seconds() / 3600.0

            if range_originale[1] >= INF_HOURS:
                range_traslato = (range_originale[0] - differenza_ore, INF_HOURS)
            else:
                range_traslato = (range_originale[0] - differenza_ore, range_originale[1] - differenza_ore)

            range_traslato_rounded = (round_quarter_hour(range_traslato[0]), round_quarter_hour(range_traslato[1]))
            range_traslato_rounded = (max(0, range_traslato_rounded[0]), range_traslato_rounded[1])

            parametri_aggiuntivi_da_considerare.append({
                "nome": nome_parametro,
                "stato": stato_selezionato,
                "range_traslato": range_traslato_rounded,
                "descrizione": descrizione,
                "differenza_ore": differenza_ore,
                "adattato": differenza_ore != 0
            })

            differenze_ore_set = set(
                p["differenza_ore"]
                for p in parametri_aggiuntivi_da_considerare
                if p.get("adattato")
            )
            nota_globale_range_adattato = len(differenze_ore_set) == 1 and len(differenze_ore_set) > 0

        elif dati_parametri_aggiuntivi[nome_parametro]["range"].get(stato_selezionato) is None:
            descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(chiave_descrizione, f"Il parametro {nome_parametro} ({stato_selezionato}) non ha un range temporale definito o descrizione specifica.")
            parametri_aggiuntivi_da_considerare.append({
                "nome": nome_parametro,
                "stato": stato_selezionato,
                "range_traslato": (np.nan, np.nan),
                "descrizione": descrizione
            })

    # --- Range raffreddamento per il grafico ---
    t_min_raff_visualizzato = np.nan
    t_max_raff_visualizzato = np.nan

    ranges_per_intersezione_inizio = []
    ranges_per_intersezione_fine = []
    nomi_parametri_usati_per_intersezione = []

    visualizza_hensge_grafico = raffreddamento_calcolabile
    if visualizza_hensge_grafico:
        t_min_raff_visualizzato = t_min_raff_hensge
        t_max_raff_visualizzato = t_max_raff_hensge

    if macchie_range_valido and macchie_range is not None:
        ranges_per_intersezione_inizio.append(macchie_range[0])
        ranges_per_intersezione_fine.append(macchie_range[1])
        nomi_parametri_usati_per_intersezione.append("macchie ipostatiche")

    if rigidita_range_valido and rigidita_range is not None:
        ranges_per_intersezione_inizio.append(rigidita_range[0])
        ranges_per_intersezione_fine.append(rigidita_range[1])
        nomi_parametri_usati_per_intersezione.append("rigidità cadaverica")

    # --- Potente et al. (minimo) ---
    mt_ore = None
    mt_giorni = None
    usa_potente_per_intersezione = False
    if not any(np.isnan(val) for val in [Tr_val, Ta_val, CF_val, W_val]):
        if Tr_val > Ta_val + 1e-6:
            Qd_potente = (Tr_val - Ta_val) / (37.2 - Ta_val)
            if Qd_potente < qd_threshold:
                B_potente = -1.2815 * (CF_val * W_val) ** (-5 / 8) + 0.0284
                ln_term = np.log(0.16) if Ta_val <= 23 else np.log(0.45)
                mt_ore = round(ln_term / B_potente, 1)
                mt_giorni = round(mt_ore / 24, 1)
        usa_potente_per_intersezione = (
            (not np.isnan(Qd_val_check)) and
            (Qd_val_check < qd_threshold) and
            (mt_ore is not None) and (not np.isnan(mt_ore))
        )

    for p in parametri_aggiuntivi_da_considerare:
        if not np.isnan(p["range_traslato"][0]):
            ranges_per_intersezione_inizio.append(p["range_traslato"][0])
            if np.isnan(p["range_traslato"][1]) or p["range_traslato"][1] >= INF_HOURS:
                ranges_per_intersezione_fine.append(np.nan)
            else:
                ranges_per_intersezione_fine.append(p["range_traslato"][1])
            nomi_parametri_usati_per_intersezione.append(p["nome"])

       # Logica Henssge/Potente per intersezione
    if raffreddamento_calcolabile:
        if np.isnan(t_max_raff_hensge):
            # Stima cautelativa: solo limite inferiore
            ranges_per_intersezione_inizio.append(t_min_raff_hensge)
            ranges_per_intersezione_fine.append(np.nan)
            nomi_parametri_usati_per_intersezione.append(
                "raffreddamento cadaverico (cautelativo: limite superiore aperto)"
            )
        else:
            usa_solo_limite_inferiore_henssge = (not np.isnan(Qd_val_check) and Qd_val_check < 0.2)

            altri_parametri_con_range = any([
                macchie_range_valido and macchie_range[1] < INF_HOURS,
                rigidita_range_valido and rigidita_range[1] < INF_HOURS,
                any(
                    not np.isnan(p["range_traslato"][0]) and
                    not np.isnan(p["range_traslato"][1]) and
                    p["range_traslato"][1] < INF_HOURS
                    for p in parametri_aggiuntivi_da_considerare
                )
            ])

            if usa_potente_per_intersezione:
                ranges_per_intersezione_inizio.append(mt_ore)
                ranges_per_intersezione_fine.append(np.nan)
                nomi_parametri_usati_per_intersezione.append(
                    "raffreddamento cadaverico (intervallo minimo secondo Potente et al.)"
                )

            elif usa_solo_limite_inferiore_henssge:
                if mt_ore is not None and not np.isnan(mt_ore):
                    ranges_per_intersezione_inizio.append(mt_ore)
                    ranges_per_intersezione_fine.append(np.nan)
                    nomi_parametri_usati_per_intersezione.append(
                        "raffreddamento cadaverico (intervallo minimo secondo Potente et al.)"
                    )
                else:
                    ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                    ranges_per_intersezione_fine.append(np.nan)
                    nomi_parametri_usati_per_intersezione.append(
                        "raffreddamento cadaverico (è stato considerato solo il limite inferiore, "
                        "vista la limitata affidabilità del calcolo per i motivi sopraesposti)"
                    )
            else:
                if t_med_raff_hensge_rounded_raw > 48:
                    if altri_parametri_con_range:
                        if t_min_raff_hensge > 48:
                            ranges_per_intersezione_inizio.append(48.0)
                            ranges_per_intersezione_fine.append(np.nan)
                            nomi_parametri_usati_per_intersezione.append(
                                "raffreddamento cadaverico (considerato genericamente > 48h per limitata affidabilità)"
                            )
                        else:
                            ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                            ranges_per_intersezione_fine.append(t_max_raff_hensge)
                            nomi_parametri_usati_per_intersezione.append("raffreddamento cadaverico")
                else:
                    ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                    ranges_per_intersezione_fine.append(t_max_raff_hensge)
                    nomi_parametri_usati_per_intersezione.append("raffreddamento cadaverico")

    if (not usa_potente_per_intersezione) and (mt_ore is not None) and (not np.isnan(mt_ore)):
        ranges_per_intersezione_inizio.append(mt_ore)
        ranges_per_intersezione_fine.append(np.nan)

    if len(ranges_per_intersezione_inizio) > 0:
        comune_inizio = max(ranges_per_intersezione_inizio)

        if mt_ore is not None and not np.isnan(mt_ore):
            altri_limiti_inferiori = [
                v for v, n in zip(ranges_per_intersezione_inizio, nomi_parametri_usati_per_intersezione)
                if "raffreddamento cadaverico" not in n.lower() or "potente" in n.lower()
            ]
            if len(altri_limiti_inferiori) > 0:
                limite_minimo_altri = max(altri_limiti_inferiori)
                if mt_ore >= limite_minimo_altri:
                    comune_inizio = round(mt_ore)

        superiori_finiti = [v for v in ranges_per_intersezione_fine if not np.isnan(v) and v < INF_HOURS]
        if len(superiori_finiti) > 0:
            comune_fine = min(superiori_finiti)
        else:
            comune_fine = np.nan

        # Se cautelativa e nessun parametro chiude l’intervallo → mantieni aperto
        if np.isnan(t_max_raff_hensge) and (len(superiori_finiti) == 0):
            comune_fine = np.nan

        overlap = True if np.isnan(comune_fine) else (comune_inizio <= comune_fine)
    else:
        comune_inizio, comune_fine = np.nan, np.nan
        overlap = False


    # --- Grafico ---
    num_params_grafico = 0
    if macchie_range_valido: num_params_grafico += 1
    if rigidita_range_valido: num_params_grafico += 1
    if raffreddamento_calcolabile: num_params_grafico += 1
    num_params_grafico += len([
        p for p in parametri_aggiuntivi_da_considerare
        if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1])
    ])

    if num_params_grafico > 0:
        plot_data = compute_plot_data(
            macchie_range=macchie_range if macchie_range_valido else (np.nan, np.nan),
            macchie_medi_range=macchie_medi_range if macchie_range_valido else None,
            rigidita_range=rigidita_range if rigidita_range_valido else (np.nan, np.nan),
            rigidita_medi_range=rigidita_medi_range if rigidita_range_valido else None,
            raffreddamento_calcolabile=raffreddamento_calcolabile,
            t_min_raff_hensge=t_min_raff_hensge if raffreddamento_calcolabile else np.nan,
            t_max_raff_hensge=t_max_raff_hensge if raffreddamento_calcolabile else np.nan,
            t_med_raff_hensge_rounded_raw=t_med_raff_hensge_rounded_raw if raffreddamento_calcolabile else np.nan,
            Qd_val_check=Qd_val_check if raffreddamento_calcolabile else np.nan,
            mt_ore=mt_ore,
            INF_HOURS=INF_HOURS,
            qd_threshold=qd_threshold,
        )

        fig = render_ranges_plot(plot_data)

        # Linee rosse dell’intersezione
        if overlap and (np.isnan(comune_fine) or comune_fine > 0):
            ax = fig.axes[0]
            if comune_inizio < plot_data["tail_end"]:
                ax.axvline(max(0, comune_inizio), color='red', linestyle='--')
            if not np.isnan(comune_fine) and comune_fine > 0:
                ax.axvline(min(plot_data["tail_end"], comune_fine), color='red', linestyle='--')
        st.pyplot(fig)

        # Frase sotto al grafico
        if overlap and (not st.session_state.get("stima_cautelativa_beta", False)):
            if usa_orario_custom:
                frase_semplice = build_simple_sentence(
                    comune_inizio=comune_inizio,
                    comune_fine=comune_fine,
                    isp_dt=data_ora_ispezione,
                    inf_hours=INF_HOURS
                )
                if frase_semplice:
                    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                    st.markdown(_wrap_final(frase_semplice), unsafe_allow_html=True)
            else:
                frase_semplice_no_dt = build_simple_sentence_no_dt(
                    comune_inizio=comune_inizio,
                    comune_fine=comune_fine,
                    inf_hours=INF_HOURS
                )
                if frase_semplice_no_dt:
                    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                    st.markdown(_wrap_final(frase_semplice_no_dt), unsafe_allow_html=True)

    # --- NOTE/AVVISI ---
    if nota_globale_range_adattato:
        dettagli.append("<p style='color:gray;font-size:small;'>* alcuni parametri sono stati valutati a orari diversi; i range sono stati traslati per renderli confrontabili.</p>")
    if usa_orario_custom and minuti_isp not in [0, 15, 30, 45]:
        avvisi.append("NB: l’orario dei rilievi è stato arrotondato al quarto d’ora più vicino.")

    hensge_input_forniti = (
        input_rt is not None and
        input_ta is not None and
        input_tm is not None and
        input_w is not None and
        st.session_state.get('fattore_correzione', None) is not None
    )

    if hensge_input_forniti:
        if Ta_val > 25:
            avvisi.append("Per temperature ambientali &gt; 25 °C, variazioni del fattore di correzione possono influenzare notevolmente i risultati.")
        if Ta_val < 18:
            avvisi.append("Per temperature ambientali &lt; 18 °C, la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati.")
        if temp_difference_small:
            avvisi.append("Essendo minima la differenza tra temperatura rettale e ambientale, è possibile che il cadavere fosse ormai in equilibrio termico con l'ambiente. La stima ottenuta dal raffreddamento cadaverico va interpretata con attenzione.")
        if abs(Tr_val - T0_val) <= 1.0:
            avvisi.append(
                "Considerato che la temperatura rettale è molto simile alla temperatura ante-mortem stimata, "
                "è possibile che il raffreddamento si trovi ancora nella fase di plateau o non sia ancora iniziato; "
                "in tale fase la precisione del metodo è ridotta."
            )
        if not raffreddamento_calcolabile:
            avvisi.append("Non è stato possibile applicare il metodo di Henssge (temperature incoerenti o fuori range dell'equazione).")

        avvisi.extend(avvisi_raffreddamento_henssge(
             t_med_round=t_med_raff_hensge_rounded,
             qd_val=Qd_val_check
        ))

    # --- Paragrafi descrittivi ---
    if not st.session_state.get("stima_cautelativa_beta", False):
        # SOLO in modalità standard aggiungi i paragrafi classici
        cf_descr = build_cf_description(
            cf_value=st.session_state.get("fattore_correzione", 1.0),
            riassunto=st.session_state.get("fc_riassunto_contatori"),
            fallback_text=st.session_state.get("fattori_condizioni_testo")
        )
        dettagli.append(paragrafo_raffreddamento_input(
            isp_dt=data_ora_ispezione if usa_orario_custom else None,
            ta_val=Ta_val, tr_val=Tr_val, w_val=W_val, t0_val=T0_val,
            cf_descr=cf_descr
        ))

        par_h = paragrafo_raffreddamento_dettaglio(
            t_min_visual=t_min_raff_visualizzato,
            t_max_visual=t_max_raff_visualizzato,
            t_med_round=t_med_raff_hensge_rounded,
            qd_val=Qd_val_check,
            ta_val=Ta_val,
        )
        if par_h:
            dettagli.append(par_h)

    # Sempre: Potente + altri paragrafi
    par_p = paragrafo_potente(
        mt_ore=mt_ore, mt_giorni=mt_giorni,
        qd_val=Qd_val_check, ta_val=Ta_val,
        qd_threshold=qd_threshold,
    )
    if par_p:
        dettagli.append(par_p)

    dettagli.extend(paragrafi_descrizioni_base(
        testo_macchie=testi_macchie[macchie_selezionata],
        testo_rigidita=rigidita_descrizioni[selettore_rigidita],
    ))
    dettagli.extend(paragrafi_parametri_aggiuntivi(
        parametri=parametri_aggiuntivi_da_considerare
    ))
    par_putr = paragrafo_putrefattive(st.session_state.get("alterazioni_putrefattive", False))
    if par_putr:
        dettagli.append(par_putr)

    # --- Frase finale principale ---
    frase_finale_html = None
    if not st.session_state.get("stima_cautelativa_beta", False):
        frase_finale_html = build_final_sentence(
            comune_inizio, comune_fine, data_ora_ispezione,
            qd_val=Qd_val_check, mt_ore=mt_ore, ta_val=Ta_val, inf_hours=INF_HOURS
        )

    # NEW: aggiungi parentetica extra se presente (cautelativa)
    _par_extra = st.session_state.get("parentetica_extra", "")
    if _par_extra:
        frase_finale_html = (frase_finale_html or "") + " " + _par_extra

    # --- Avvisi toggle ---
    if avvisi:
        mostra_avvisi = st.toggle(f"⚠️ Mostra avvisi ({len(avvisi)})", key="mostra_avvisi")
        if mostra_avvisi:
            for msg in avvisi:
                _warn_box(msg)

    # --- Discordanze ---
    num_potential_ranges_used = sum(
        1 for start, end in zip(ranges_per_intersezione_inizio, ranges_per_intersezione_fine)
        if start is not None and end is not None
    )
    discordanti = (
        (not overlap and num_potential_ranges_used >= 2)
        or ranges_in_disaccordo_completa(ranges_per_intersezione_inizio, ranges_per_intersezione_fine)
    )
    if discordanti:
        st.markdown(
            "<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    with st.expander("Descrizioni dettagliate"):
        for blocco in dettagli:
            st.markdown(_wrap_final(blocco), unsafe_allow_html=True)

        if discordanti:
            st.markdown(
                _wrap_final("<ul><li><b>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</b></li></ul>"),
                unsafe_allow_html=True
            )
        elif overlap and (not st.session_state.get("stima_cautelativa_beta", False)):
            if usa_orario_custom:
                frase_finale_html2 = build_final_sentence(
                    comune_inizio, comune_fine, data_ora_ispezione,
                    qd_val=Qd_val_check, mt_ore=mt_ore, ta_val=Ta_val, inf_hours=INF_HOURS
                )
                # Aggiungi comunque la parentetica extra se presente
                _par_extra = st.session_state.get("parentetica_extra", "")
                if _par_extra:
                    frase_finale_html2 = (frase_finale_html2 or "") + " " + _par_extra

                if frase_finale_html2:
                    st.markdown(_wrap_final(f"<ul><li>{frase_finale_html2}</li></ul>"), unsafe_allow_html=True)
            else:
                frase_finale_html_simpl = build_final_sentence_simple(
                    comune_inizio=comune_inizio,
                    comune_fine=comune_fine,
                    inf_hours=INF_HOURS
                )
                if frase_finale_html_simpl:
                    st.markdown(_wrap_final(f"<ul><li>{frase_finale_html_simpl}</li></ul>"), unsafe_allow_html=True)

        if overlap and len(nomi_parametri_usati_per_intersezione) > 0:
            nomi_parametri_finali_per_riepilogo = []
            for nome in nomi_parametri_usati_per_intersezione:
                if ("raffreddamento cadaverico" in nome.lower()
                    and "potente" not in nome.lower()
                    and mt_ore is not None and not np.isnan(mt_ore)
                    and abs(comune_inizio - mt_ore) < 0.25):
                    continue
                nomi_parametri_finali_per_riepilogo.append(nome)

            small_html = frase_riepilogo_parametri_usati(nomi_parametri_finali_per_riepilogo)
            if small_html:
                st.markdown(_wrap_final(small_html), unsafe_allow_html=True)

        frase_qd_html = frase_qd(Qd_val_check, Ta_val)
        if frase_qd_html:
            st.markdown(_wrap_final(frase_qd_html), unsafe_allow_html=True)


# ---- Trigger run ----
if st.session_state.get("show_results", False):
    aggiorna_grafico()
