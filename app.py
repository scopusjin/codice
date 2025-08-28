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
# se la funzione Excel è in questo stesso file, non serve importarla;
# altrimenti:
# from app.data_sources import load_tabelle_correzione

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

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd

def _fc_palette():
    base = st.get_option("theme.base") or "light"
    if base.lower() == "dark":
        return dict(
            bg="#0e3c2f",      # verde scuro leggibile su dark
            text="#d7fbe8",    # testo chiaro
            border="#2ea043",  # bordo/accessorio
            note="#abeacb"     # testo secondario
        )
    else:
        return dict(
            bg="#e6f4ea",      # verde chiaro per light
            text="#0f5132",    # testo scuro
            border="#2ea043",
            note="#5b7f6b"
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


# Titolo più piccolo e con peso medio
st.markdown("<h5 style='margin-top:0; margin-bottom:10px;'>Stima epoca decesso</h5>", unsafe_allow_html=True)







    
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
        # segnaposto per evitare NameError nel resto del codice
        input_data_rilievo = None
        input_ora_rilievo = None

# 📌 2. Ipostasi e rigidità (2 colonne stessa riga) — RIQUADRO
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

    # 📌 3. Temperature (3 colonne gap small)
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

    # 📌 4. Peso + Fattore di correzione + pulsante "Suggerisci" (mini-link)
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



def pannello_suggerisci_fc(peso_default: float = 70.0):
    import streamlit as st

    # ——— CSS compatto (opzionale) ———
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

    # ——— Stato corpo ———
    stato_label = st.radio(
        "dummy",
        ["Corpo asciutto", "Bagnato", "Immerso"],
        index=0, horizontal=True, key="radio_stato_corpo"
    )
    stato_corpo = (
        "Asciutto" if stato_label == "Corpo asciutto"
        else ("Bagnato" if stato_label == "Bagnato" else "Immerso")
    )

    # ——— Se Immerso: acqua stagnante/corrente, calcolo immediato e ritorno ———
    if stato_corpo == "Immerso":
        acqua_label = st.radio(
            "dummy",
            ["In acqua stagnante", "In acqua corrente"],
            index=0, horizontal=True, key="radio_acqua"
        )
        acqua_mode = "stagnante" if acqua_label == "In acqua stagnante" else "corrente"

        try:
            tabella2 = load_tabelle_correzione()
        except Exception:
            tabella2 = None

        result = compute_factor(
            stato="Immerso",
            acqua=acqua_mode,
            counts=DressCounts(),  # zero strati nel caso Immerso
            superficie_display=None,
            correnti_aria=False,
            peso=float(st.session_state.get("peso", peso_default)),
            tabella2_df=tabella2
        )

        # UI risultato adattiva
        peso_corrente = float(st.session_state.get("peso", peso_default))
        _fbase = result.fattore_base
        _ffin  = result.fattore_finale
        _fc_box(_ffin, _fbase, peso_corrente)


        def _apply(val, riass):
            st.session_state["fattore_correzione"] = round(float(val), 2)
            st.session_state["fattori_condizioni_parentetica"] = None
            st.session_state["fattori_condizioni_testo"] = None
            st.session_state["toggle_fattore"] = False
            st.session_state["fc_riassunto_contatori"] = riass

        st.button(
            "✅ Usa questo fattore",
            on_click=_apply,
            args=(result.fattore_finale, result.riassunto),
            use_container_width=True
        )
        return

    # ——— Non Immerso: vestizione/coperte ———
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
                                  st.session_state.get("strati_sottili", 0),
                                  key="strati_sottili")
            n_spessi = st.slider("Strati pesanti (indumenti o teli spessi)", 0, 6,
                                 st.session_state.get("strati_spessi", 0),
                                 key="strati_spessi")
        with col_blankets:
            if stato_corpo == "Asciutto":
                n_cop_medie = st.slider("Coperte di medio spessore", 0, 5,
                                        st.session_state.get("coperte_medie", 0),
                                        key="coperte_medie")
                n_cop_pesanti = st.slider("Coperte pesanti", 0, 5,
                                          st.session_state.get("coperte_pesanti", 0),
                                          key="coperte_pesanti")

    counts = DressCounts(
        sottili=n_sottili, spessi=n_spessi,
        coperte_medie=n_cop_medie, coperte_pesanti=n_cop_pesanti
    )

    # ——— Superficie (solo Asciutto) ———
    superficie_display_selected = "/"
    if stato_corpo == "Asciutto":
        nudo_eff = (
            (not toggle_vestito)
            or (counts.sottili == counts.spessi == counts.coperte_medie == counts.coperte_pesanti == 0)
        )
        options_display = SURF_DISPLAY_ORDER.copy()
        if not nudo_eff:
            options_display = [
                o for o in options_display
                if o != "Superficie metallica spessa (all’aperto)"
            ]

        prev_display = st.session_state.get("superficie_display_sel")
        if prev_display not in options_display:
            prev_display = options_display[0]

        superficie_display_selected = st.selectbox(
            "Superficie di appoggio",
            options_display,
            index=options_display.index(prev_display),
            key="superficie_display_sel"
        )

    # ——— Correnti d’aria ———
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

    # ——— Carica Tabella 2 ———
    try:
        tabella2 = load_tabelle_correzione()
    except Exception:
        tabella2 = None

    # ——— Calcolo finale ———
    result = compute_factor(
        stato=stato_corpo,
        acqua=None,
        counts=counts,
        superficie_display=superficie_display_selected if stato_corpo == "Asciutto" else None,
        correnti_aria=correnti_presenti,
        peso=float(st.session_state.get("peso", peso_default)),
        tabella2_df=tabella2
    )

    # ——— UI risultato adattiva ———
    peso_corrente = float(st.session_state.get("peso", peso_default))
    _fbase = result.fattore_base
    _ffin  = result.fattore_finale
    _fc_box(_ffin, _fbase, peso_corrente)


    def _apply(val, riass):
        st.session_state["fattore_correzione"] = round(float(val), 2)
        st.session_state["fattori_condizioni_parentetica"] = None
        st.session_state["fattori_condizioni_testo"] = None
        st.session_state["toggle_fattore"] = False
        st.session_state["fc_riassunto_contatori"] = riass

    st.button(
        "✅ Usa questo fattore",
        on_click=_apply,
        args=(result.fattore_finale, result.riassunto),
        use_container_width=True
    )
    
if st.session_state.get("toggle_fattore", False):
    with st.container(border=True):
        pannello_suggerisci_fc(peso_default=st.session_state.get("peso", 70.0))
        

# Pulsante per mostrare/nascondere i parametri aggiuntivi
mostra_parametri_aggiuntivi = st.checkbox("Aggiungi dati tanatologici speciali")

widgets_parametri_aggiuntivi = {}

if mostra_parametri_aggiuntivi:
    with st.container(border=True):  # bordo come per "Suggerisci fattore di correzione"
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
                        with st.popover(" "):  # trigger invisibile ma associato alla posizione del testo
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

            if selettore != "Non valutata":
                chiave_checkbox = f"{nome_parametro}_diversa"
                col1, col2 = st.columns([0.2, 0.2], gap="small")
                with col1:
                    st.markdown(
                        "<div style='font-size: 0.8em; color: orange; margin-bottom: 3px;'>"
                        "Il dato è stato valutato a un orario diverso rispetto a quello precedentemente indicato?"
                        "</div>",
                        unsafe_allow_html=True
                    )
                with col2:
                    usa_orario_personalizzato = st.checkbox(
                        label="",
                        key=chiave_checkbox
                    )

            if usa_orario_personalizzato:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Data rilievo:</div>", unsafe_allow_html=True)
                    data_picker = st.date_input(
                        "Data rilievo:",
                        value=input_data_rilievo,
                        key=f"{nome_parametro}_data",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Ora rilievo:</div>", unsafe_allow_html=True)
                    ora_input = st.text_input(
                        "Ora rilievo (HH:MM):",
                        value=input_ora_rilievo,
                        key=f"{nome_parametro}_ora",
                        label_visibility="collapsed"
                    )

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
        extra.ap
