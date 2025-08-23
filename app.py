from app.factor_calc import (
    DressCounts, compute_factor, build_cf_description,
    SURF_DISPLAY_ORDER, fattore_vestiti_coperte,
)

from app.henssge import (
    round_quarter_hour,
    calcola_raffreddamento,
    ranges_in_disaccordo_completa,
    INF_HOURS as INF_HOURS_HENSSGE  # opzionale, se ti serve
)

from app.utils_time import arrotonda_quarto_dora, split_hours_minutes as _split_hours_minutes

# se la funzione Excel è in questo stesso file, non serve importarla;
# altrimenti, se l’hai spostata in data_sources.py, usa:
# from data_sources import load_tabelle_correzione

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit.components.v1 as components
import numpy as np
from scipy.optimize import root_scalar
import datetime
import pandas as pd


# =========================
# Stato e costanti globali
# =========================
st.set_page_config(page_title="MStima Epoca della Morte", layout="centered")

if "fattore_correzione" not in st.session_state:
    st.session_state["fattore_correzione"] = 1.0


if "show_img_sopraciliare" not in st.session_state:
    st.session_state["show_img_sopraciliare"] = False
if "show_img_peribuccale" not in st.session_state:
    st.session_state["show_img_peribuccale"] = False
# Definiamo un valore che rappresenta "infinito" o un limite superiore molto elevato per i range aperti
INF_HOURS = 200  # Un valore sufficientemente grande per la scala del grafico e i calcoli



# =========================
# Utility cache per Excel
# =========================

@st.cache_data
def load_tabelle_correzione():
    """
    Carica e normalizza le tabelle usate da calcola_fattore.
    """
    try:
        t1 = pd.read_excel("data/tabella_rielaborata.xlsx", engine="openpyxl")
        t2 = pd.read_excel("data/tabella_secondaria.xlsx", engine="openpyxl")
    except FileNotFoundError:
        raise
    except ImportError as e:
        raise RuntimeError("Il pacchetto 'openpyxl' è richiesto per leggere i file Excel.") from e

    t1['Fattore'] = pd.to_numeric(t1['Fattore'], errors='coerce')
    for col in ["Ambiente", "Vestiti", "Coperte", "Superficie d'appoggio", "Correnti"]:
        t1[col] = t1[col].astype(str).str.strip()
    return t1, t2

# =========================
# Funzioni esistenti (con fix robustezza)
# =========================







# Titolo più piccolo e con peso medio
st.markdown("<h5 style='margin-top:0; margin-bottom:10px;'>Stima epoca decesso</h5>", unsafe_allow_html=True)



# --- Dati per Macchie Ipostatiche e Rigidità Cadaverica (Esistenti) ---


# --- Funzioni di Utilità e Calcolo Henssge (Esistenti) ---




    
# --- Definizione Widget (Streamlit) ---
with st.container(border=True):
    
    # 📌 1. Data e ora ispezione legale
    st.markdown("<div style='font-size: 0.88rem;'>Data e ora dei rilievi tanatologici:</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="small")
    with col1:
        input_data_rilievo = st.date_input("Data ispezione legale:", value=datetime.date.today(), label_visibility="collapsed")

    with col2:
        input_ora_rilievo = st.text_input(
            "Ora ispezione legale (HH:MM):",
            value="00:00",
            label_visibility="collapsed"
        )

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
    stato_corpo = "Asciutto" if stato_label == "Corpo asciutto" else ("Bagnato" if stato_label == "Bagnato" else "Immerso")

    # ——— Se Immerso: acqua stagnante/corrente, calcolo immediato e ritorno ———
    if stato_corpo == "Immerso":
        acqua_label = st.radio("dummy", ["In acqua stagnante", "In acqua corrente"], index=0, horizontal=True, key="radio_acqua")
        acqua_mode = "stagnante" if acqua_label == "In acqua stagnante" else "corrente"
        # tabelle Excel (solo Tabella 2 serve per peso)
        try:
            _, tabella2 = load_tabelle_correzione()
        except Exception:
            tabella2 = None

        result = compute_factor(
            stato="Immerso",
            acqua=acqua_mode,
            counts=DressCounts(),                 # zero strati nel caso Immerso
            superficie_display=None,
            correnti_aria=False,
            peso=float(st.session_state.get("peso", peso_default)),
            tabella2_df=tabella2
        )

        st.markdown(
            f"<div style='background-color:#e6f4ea; padding:10px; border-radius:5px;'>"
            f"Fattore di correzione suggerito: {result.fattore_finale:.2f}"
            f"</div>",
            unsafe_allow_html=True
        )

        def _apply(val, riass):
            st.session_state["fattore_correzione"] = round(float(val), 2)
            st.session_state["fattori_condizioni_parentetica"] = None
            st.session_state["fattori_condizioni_testo"] = None
            st.session_state["toggle_fattore"] = False
            st.session_state["fc_riassunto_contatori"] = riass

        st.button("✅ Usa questo fattore", on_click=_apply, args=(result.fattore_finale, result.riassunto), use_container_width=True)
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
            n_sottili = st.slider("Strati leggeri (indumenti o teli sottili)", 0, 8, st.session_state.get("strati_sottili", 0), key="strati_sottili")
            n_spessi  = st.slider("Strati pesanti (indumenti o teli spessi)",  0, 6, st.session_state.get("strati_spessi", 0),  key="strati_spessi")
        with col_blankets:
            if stato_corpo == "Asciutto":
                n_cop_medie   = st.slider("Coperte di medio spessore", 0, 5, st.session_state.get("coperte_medie", 0), key="coperte_medie")
                n_cop_pesanti = st.slider("Coperte pesanti",          0, 5, st.session_state.get("coperte_pesanti", 0), key="coperte_pesanti")

    counts = DressCounts(sottili=n_sottili, spessi=n_spessi, coperte_medie=n_cop_medie, coperte_pesanti=n_cop_pesanti)

    # ——— Superficie (solo Asciutto) ———
    superficie_display_selected = "/"
    if stato_corpo == "Asciutto":
        # se nudo effettivo, includi opzione “Superficie metallica spessa (all’aperto)”
        nudo_eff = (not toggle_vestito) or (counts.sottili == counts.spessi == counts.coperte_medie == counts.coperte_pesanti == 0)
        options_display = SURF_DISPLAY_ORDER.copy()
        if not nudo_eff:
            options_display = [o for o in options_display if o != "Superficie metallica spessa (all’aperto)"]

        # mantieni selezione precedente se valida
        prev_display = st.session_state.get("superficie_display_sel")
        if prev_display not in options_display:
            prev_display = options_display[0]

        superficie_display_selected = st.selectbox(
            "Superficie di appoggio",
            options_display,
            index=options_display.index(prev_display),
            key="superficie_display_sel"
        )

    # ——— Correnti d’aria (visibilità simile alla tua logica) ———
    correnti_presenti = False
    with corr_placeholder.container():
        mostra_correnti = True
        if stato_corpo == "Asciutto":
            f_vc = fattore_vestiti_coperte(counts)
            if f_vc >= 1.2:   # come la tua regola: se molto vestito, nascondi toggle
                mostra_correnti = False
        if mostra_correnti:
            correnti_presenti = st.toggle(
                "Correnti d'aria presenti?",
                value=st.session_state.get("toggle_correnti_fc", False),
                key="toggle_correnti_fc",
                disabled=False
            )

    # ——— Carica Tabella 2 (se disponibile) ———
    try:
        _, tabella2 = load_tabelle_correzione()
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

    # ——— UI risultato ———
    st.markdown(
        f'<div style="background-color:#e6f4ea; padding:10px; border-radius:5px;">'
        f'Fattore di correzione suggerito: {result.fattore_finale:.2f}'
        f'</div>',
        unsafe_allow_html=True
    )

    def _apply(val, riass):
        st.session_state["fattore_correzione"] = round(float(val), 2)
        st.session_state["fattori_condizioni_parentetica"] = None
        st.session_state["fattori_condizioni_testo"] = None
        st.session_state["toggle_fattore"] = False
        st.session_state["fc_riassunto_contatori"] = riass

    st.button("✅ Usa questo fattore", on_click=_apply, args=(result.fattore_finale, result.riassunto), use_container_width=True)

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
    pulsante_genera_stima = st.button("STIMA EPOCA DECESSO")


def aggiorna_grafico():
        # --- Raccolta messaggi per nuova UI compatta ---
    avvisi = []              # tutti gli avvisi arancioni
    dettagli = []            # testi lunghi/descrittivi per l’expander
    frase_finale_html = None # “La valutazione complessiva…”
    frase_secondaria_html = None  # eventuale variante “Senza considerare Potente…”

    # --- Validazione Input Data/Ora Ispezione Legale ---
    if not input_data_rilievo or not input_ora_rilievo:
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Inserisci data e ora dell'ispezione legale.</p>", unsafe_allow_html=True)
        return

    try:
        ora_isp_obj = datetime.datetime.strptime(input_ora_rilievo, '%H:%M')
        minuti_isp = ora_isp_obj.minute
    except ValueError:
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Errore: Formato ora ispezione legale non valido. Utilizzare il formato HH:MM (es. 14:30).</p>", unsafe_allow_html=True)
        return

    data_ora_ispezione_originale = datetime.datetime.combine(input_data_rilievo, ora_isp_obj.time())
    data_ora_ispezione = arrotonda_quarto_dora(data_ora_ispezione_originale)

    # --- Recupero Valori Input per Calcoli (Esistenti) ---
    Tr_val = input_rt
    Ta_val = input_ta
    T0_val = input_tm
    W_val = input_w
    CF_val = st.session_state.get("fattore_correzione", 1.0)

    # Validazioni extra (robustezza)
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

    t_med_raff_hensge_rounded, t_min_raff_hensge, t_max_raff_hensge, t_med_raff_hensge_rounded_raw, Qd_val_check = calcola_raffreddamento(
        Tr_val, Ta_val, T0_val, W_val, CF_val
    )
    qd_threshold = 0.2 if Ta_val <= 23 else 0.5
    raffreddamento_calcolabile = not np.isnan(t_med_raff_hensge_rounded) and t_med_raff_hensge_rounded >= 0

    temp_difference_small = False
    if Tr_val is not None and Ta_val is not None and (Tr_val - Ta_val) is not None and (Tr_val - Ta_val) < 2.0 and (Tr_val - Ta_val) >= 0:
        temp_difference_small = True

    macchie_range_valido = macchie_selezionata != "Non valutabili/Non attendibili"
    macchie_range = opzioni_macchie.get(macchie_selezionata) if macchie_range_valido else (np.nan, np.nan)
    macchie_medi_range = macchie_medi.get(macchie_selezionata) if macchie_range_valido else None

    rigidita_range_valido = rigidita_selezionata != "Non valutabile/Non attendibile"
    rigidita_range = opzioni_rigidita.get(rigidita_selezionata) if rigidita_range_valido else (np.nan, np.nan)
    rigidita_medi_range = rigidita_medi.get(rigidita_selezionata) if rigidita_range_valido else None

    parametri_aggiuntivi_da_considerare = []
    nota_globale_range_adattato = False

    for nome_parametro, widgets_param in widgets_parametri_aggiuntivi.items():
        stato_selezionato = widgets_param["selettore"]
        data_rilievo_param = widgets_param["data_rilievo"]
        ora_rilievo_param_str = widgets_param["ora_rilievo"]

        if stato_selezionato == "Non valutata":
            continue

        chiave_descrizione = stato_selezionato.split(':')[0].strip()

        # Ora param: normalizza a datetime.time e controlla mezz'ora
        if not ora_rilievo_param_str or ora_rilievo_param_str.strip() == "":
            ora_rilievo_time = data_ora_ispezione.time()
        else:
            try:
                ora_rilievo_time = datetime.datetime.strptime(ora_rilievo_param_str, '%H:%M').time()
                
            except ValueError:
                avvisi.append(f"⚠️ {nome_parametro}: formato ora di rilievo '{ora_rilievo_param_str}' non valido (usa HH:MM, es. 14:30) → parametro escluso dalla stima.")
                continue

        # Se data personalizzata assente, usa quella dell’ispezione
        if data_rilievo_param is None:
            data_rilievo_param = data_ora_ispezione.date()

        # Determina la chiave corretta da usare per cercare nel dizionario dei range
        if nome_parametro == "Eccitabilità elettrica peribuccale":
            chiave_descrizione = stato_selezionato.split(':')[0].strip()
        else:
            chiave_descrizione = stato_selezionato.strip()

        # Forza il recupero esatto della chiave anche se ci sono spazi invisibili
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

    # --- Determinazione Range Raffreddamento per Visualizzazione nel Grafico ---
    # Il range visualizzato per Henssge > 30h sarà un range ±20% attorno a t_med_raw
    t_min_raff_visualizzato = np.nan
    t_max_raff_visualizzato = np.nan

    # --- Definisce i range USATI per l'intersezione (stima complessiva) ---
    ranges_per_intersezione_inizio = []
    ranges_per_intersezione_fine = []
    # Lista per tenere traccia dei nomi dei parametri USATI per l'intersezione
    nomi_parametri_usati_per_intersezione = []

    # Determina se visualizzare il range Henssge sul grafico
    visualizza_hensge_grafico = raffreddamento_calcolabile

    if visualizza_hensge_grafico:
        # Usa i limiti calcolati da calcola_raffreddamento per la visualizzazione
        t_min_raff_visualizzato = t_min_raff_hensge
        t_max_raff_visualizzato = t_max_raff_hensge
    else:
        # Se non visualizzabile, imposta NaN
        t_min_raff_visualizzato = np.nan
        t_max_raff_visualizzato = np.nan

    # --- Fine Determinazione Range Raffreddamento Visualizzazione ---

    # Aggiunge range macchie se valido e presente
    if macchie_range_valido and macchie_range is not None:
        ranges_per_intersezione_inizio.append(macchie_range[0])
        ranges_per_intersezione_fine.append(macchie_range[1])
        nomi_parametri_usati_per_intersezione.append("macchie ipostatiche")

    # Aggiunge range rigidità se valido e presente
    if rigidita_range_valido and rigidita_range is not None:
        ranges_per_intersezione_inizio.append(rigidita_range[0])
        ranges_per_intersezione_fine.append(rigidita_range[1])
        nomi_parametri_usati_per_intersezione.append("rigidità cadaverica")

    # --- Stima minima post mortem secondo Potente et al. ---
    mt_ore = None
    mt_giorni = None
    usa_potente_per_intersezione = False

    if not any(np.isnan(val) for val in [Tr_val, Ta_val, CF_val, W_val]):
        if Tr_val <= Ta_val + 1e-6:
            mt_ore = None
            mt_giorni = None
        else:
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

    # Aggiunge range dei parametri aggiuntivi, considerando sempre il limite inferiore
    for p in parametri_aggiuntivi_da_considerare:
        if not np.isnan(p["range_traslato"][0]):
            ranges_per_intersezione_inizio.append(p["range_traslato"][0])
            if np.isnan(p["range_traslato"][1]) or p["range_traslato"][1] >= INF_HOURS:
                ranges_per_intersezione_fine.append(np.nan)
            else:
                ranges_per_intersezione_fine.append(p["range_traslato"][1])
            nomi_parametri_usati_per_intersezione.append(p["nome"])

    # --- Logica Henssge/Potente per intersezione ---
    if raffreddamento_calcolabile:
        # Se deve essere usato solo il limite inferiore
        usa_solo_limite_inferiore_henssge = False
        if not np.isnan(Qd_val_check) and Qd_val_check < 0.2:
            usa_solo_limite_inferiore_henssge = True

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
            # Usa solo Potente, senza aggiungere Henssge
            ranges_per_intersezione_inizio.append(mt_ore)
            ranges_per_intersezione_fine.append(np.nan)
            nome_raffreddamento_intersezione = "raffreddamento cadaverico (intervallo minimo secondo Potente et al.)"
            nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)

        elif usa_solo_limite_inferiore_henssge:
            if mt_ore is not None and not np.isnan(mt_ore):
                ranges_per_intersezione_inizio.append(mt_ore)
                ranges_per_intersezione_fine.append(np.nan)
                nome_raffreddamento_intersezione = "raffreddamento cadaverico (intervallo minimo secondo Potente et al.)"
                nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
            else:
                ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                ranges_per_intersezione_fine.append(np.nan)
                nome_raffreddamento_intersezione = (
                    "raffreddamento cadaverico (è stato considerato solo il limite inferiore, "
                    "vista la limitata affidabilità del calcolo per i motivi sopraesposti)"
                )
                nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)

        else:
            if t_med_raff_hensge_rounded_raw > 48:
                if altri_parametri_con_range:
                    if t_min_raff_hensge > 48:
                        ranges_per_intersezione_inizio.append(48.0)
                        ranges_per_intersezione_fine.append(np.nan)
                        nome_raffreddamento_intersezione = (
                            "raffreddamento cadaverico (che è stato considerato genericamente > 48h, "
                            "vista la limitata affidabilità del calcolo per i motivi sopraesposti)"
                        )
                        nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
                    else:
                        ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                        ranges_per_intersezione_fine.append(t_max_raff_hensge)
                        nome_raffreddamento_intersezione = "raffreddamento cadaverico"
                        nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
            else:
                ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                ranges_per_intersezione_fine.append(t_max_raff_hensge)
                nome_raffreddamento_intersezione = "raffreddamento cadaverico"
                nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)

    # Se Potente non è stato usato per intersezione, ma è disponibile, lo aggiunge come parametro separato
    if (not usa_potente_per_intersezione) and ('mt_ore' in locals()) and (mt_ore is not None) and (not np.isnan(mt_ore)):
        ranges_per_intersezione_inizio.append(mt_ore)
        ranges_per_intersezione_fine.append(np.nan)

    # Calcolo intersezione finale
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

        if np.isnan(comune_fine):
            overlap = True
        else:
            overlap = comune_inizio <= comune_fine
    else:
        comune_inizio, comune_fine = np.nan, np.nan
        overlap = False

    # --- Sezione dedicata alla generazione del grafico ---

    # Determina il numero totale di parametri da mostrare nel grafico
    num_params_grafico = 0
    if macchie_range_valido: num_params_grafico += 1
    if rigidita_range_valido: num_params_grafico += 1
    if visualizza_hensge_grafico: num_params_grafico += 1
    num_params_grafico += len([p for p in parametri_aggiuntivi_da_considerare if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1])])

    if num_params_grafico > 0:
        fig, ax = plt.subplots(figsize=(10, max(2, 1.5 + 0.5 * num_params_grafico)))
# --- STILI LINEE (pieni e tratteggiati) ---
        LINE_W  = 6              # stesso spessore per pieno e tratteggio
        DASH_LS = (0, (2, 1))    # tratteggio corto: 4 on, 3 off
        CAP     = 'butt'         # terminali piatti (coerenti)
        parametri_grafico = []
        ranges_to_plot_inizio = []
        ranges_to_plot_fine = []

        # --- Etichette e range: IPOSTASI ---
        if macchie_range_valido and macchie_range is not None:
            nome_breve_macchie = "Ipostasi"
            if macchie_range[1] < INF_HOURS:
                label_macchie = f"{nome_breve_macchie}\n({macchie_range[0]:.1f}–{macchie_range[1]:.1f} h)"
            else:
                label_macchie = f"{nome_breve_macchie}\n(≥ {macchie_range[0]:.1f} h)"
            parametri_grafico.append(label_macchie)
            ranges_to_plot_inizio.append(macchie_range[0])
            ranges_to_plot_fine.append(macchie_range[1] if macchie_range[1] < INF_HOURS else INF_HOURS)

        # --- Etichette e range: RIGIDITÀ ---
        if rigidita_range_valido and rigidita_range is not None:
            nome_breve_rigidita = "Rigor"
            if rigidita_range[1] < INF_HOURS:
                label_rigidita = f"{nome_breve_rigidita}\n({rigidita_range[0]:.1f}–{rigidita_range[1]:.1f} h)"
            else:
                label_rigidita = f"{nome_breve_rigidita}\n(≥ {rigidita_range[0]:.1f} h)"
            parametri_grafico.append(label_rigidita)
            ranges_to_plot_inizio.append(rigidita_range[0])
            ranges_to_plot_fine.append(rigidita_range[1] if rigidita_range[1] < INF_HOURS else INF_HOURS)

        # --- Etichette e range: RAFFREDDAMENTO ---
        label_hensge = None
        if raffreddamento_calcolabile:
            nome_breve_hensge = "Raffreddamento"
            usa_solo_limite_inferiore_henssge = not np.isnan(Qd_val_check) and Qd_val_check < 0.2

            if usa_solo_limite_inferiore_henssge:
                maggiore_di_valore = t_min_raff_hensge
                usa_potente = False
                if mt_ore is not None and not np.isnan(mt_ore):
                    maggiore_di_valore = round(mt_ore)
                    usa_potente = True

                if usa_potente:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore} h)"
                else:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore:.1f} h)\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"

                ranges_to_plot_inizio.append(t_min_raff_hensge)
                ranges_to_plot_fine.append(t_max_raff_hensge)

            elif t_med_raff_hensge_rounded_raw is not None and t_med_raff_hensge_rounded_raw > 30:
                maggiore_di_valore = 30.0
                usa_potente = False
                if mt_ore is not None and not np.isnan(mt_ore):
                    maggiore_di_valore = round(mt_ore)
                    usa_potente = True

                if usa_potente:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore} h)"
                else:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore:.1f} h)\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"

                ranges_to_plot_inizio.append(t_min_raff_hensge)
                ranges_to_plot_fine.append(t_max_raff_hensge)

            else:
                label_hensge = f"{nome_breve_hensge}\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"
                ranges_to_plot_inizio.append(t_min_raff_hensge)
                ranges_to_plot_fine.append(t_max_raff_hensge)

            parametri_grafico.append(label_hensge)

        # --- Etichette e range: PARAMETRI AGGIUNTIVI ---
        for param in parametri_aggiuntivi_da_considerare:
            if not np.isnan(param["range_traslato"][0]) and not np.isnan(param["range_traslato"][1]):
                nome_breve = nomi_brevi.get(param['nome'], param['nome'])
                if param['range_traslato'][1] == INF_HOURS:
                    label_param_aggiuntivo = f"{nome_breve}\n(≥ {param['range_traslato'][0]:.1f} h)"
                else:
                    label_param_aggiuntivo = f"{nome_breve}\n({param['range_traslato'][0]:.1f}–{param['range_traslato'][1]:.1f} h)"
                if param.get('adattato', False):
                    label_param_aggiuntivo += " *"
                parametri_grafico.append(label_param_aggiuntivo)
                ranges_to_plot_inizio.append(param["range_traslato"][0])
                ranges_to_plot_fine.append(param["range_traslato"][1] if param["range_traslato"][1] < INF_HOURS else INF_HOURS)

        
        # ==============================
        # 1) RAFFREDDAMENTO verde (SOTTO)
        #    - Disegnato PRIMA delle linee blu
        #    - Cap dinamico e tratteggio fino al 20% in più
        # ==============================

        TAIL_FACTOR = 1.20
        DEFAULT_CAP_IF_NO_FINITE = 72.0  # 3 giorni se non esistono massimi finiti

        # Estremo superiore finito più grande (cap "finito")
        finite_ends_all = [e for e in ranges_to_plot_fine if not np.isnan(e) and e < INF_HOURS]
        cap_base = max(finite_ends_all) if finite_ends_all else DEFAULT_CAP_IF_NO_FINITE

        # Inizi dei segmenti "infiniti" blu (per stimare una base della coda)
        infinite_starts_blue = [
            s for s, e in zip(ranges_to_plot_inizio, ranges_to_plot_fine)
            if not np.isnan(s) and (np.isnan(e) or e >= INF_HOURS)
        ]

        # Inizi dei segmenti verdi speciali (Potente, soglia >30h)
        special_inf_starts_green = []
        if raffreddamento_calcolabile and label_hensge is not None and label_hensge in parametri_grafico:
            if mt_ore is not None and not np.isnan(mt_ore):
                special_inf_starts_green.append(mt_ore)
            if (not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and
                t_med_raff_hensge_rounded_raw is not None and t_med_raff_hensge_rounded_raw > 30):
                special_inf_starts_green.append(30.0)

        # Base della coda = max tra cap finito, inizi infiniti blu e verdi
        if infinite_starts_blue or special_inf_starts_green:
            tail_base = max([cap_base] + infinite_starts_blue + special_inf_starts_green)
        else:
            tail_base = cap_base

        TAIL_END = tail_base * TAIL_FACTOR  # fine tratteggio + fine grafico

        if raffreddamento_calcolabile and label_hensge is not None and label_hensge in parametri_grafico:
            idx_raff = parametri_grafico.index(label_hensge)

            # Segmento Potente (da mt_ore a ∞): solido fino a cap finito, poi tratteggiato fino a TAIL_END
            if mt_ore is not None and not np.isnan(mt_ore):
                solid_from = float(mt_ore)
                solid_to   = max(solid_from, cap_base)

                # parte piena
                if solid_from < TAIL_END and solid_to > solid_from:
                    ax.hlines(
                        y=idx_raff,
                        xmin=solid_from, xmax=min(solid_to, TAIL_END),
                        color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1
                    )

                # tratteggio
                dash_start = max(solid_to, solid_from)
                if TAIL_END > dash_start:
                    ax.hlines(
                        y=idx_raff,
                        xmin=dash_start, xmax=TAIL_END,
                        color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1,
                        linestyle=DASH_LS
                    )

            # Segmento >30h (Qd>0.2 e t_med_raw>30): solido fino a cap finito, poi tratteggiato fino a TAIL_END
            if (not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and
                t_med_raff_hensge_rounded_raw is not None and t_med_raff_hensge_rounded_raw > 30):
                solid_from = 30.0
                solid_to   = max(solid_from, cap_base)

                # parte piena
                if solid_from < TAIL_END and solid_to > solid_from:
                    ax.hlines(
                        y=idx_raff,
                        xmin=solid_from, xmax=min(solid_to, TAIL_END),
                        color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1
                    )

                # tratteggio
                dash_start = max(solid_to, solid_from)
                if TAIL_END > dash_start:
                    ax.hlines(
                        y=idx_raff,
                        xmin=dash_start, xmax=TAIL_END,
                        color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1,
                        linestyle=DASH_LS
                    )
                    
        
        # 2) LINEE BLU DI BASE (tutti i range)
        #    - Finite: come prima
        #    - Infinite: solido fino a cap finito, poi tratteggiato fino a TAIL_END
        # ==============================
        for i, (s, e) in enumerate(zip(ranges_to_plot_inizio, ranges_to_plot_fine)):
            if np.isnan(s):
                continue

            is_infinite = (np.isnan(e) or e >= INF_HOURS)

            if not is_infinite:
                ax.hlines(i, s, e, color='steelblue', linewidth=6, zorder=2)
            else:
                solid_to = max(s, cap_base)
                if solid_to > s and s < TAIL_END:
                    ax.hlines(i, s, min(solid_to, TAIL_END), color='steelblue', linewidth=6, zorder=2)
                dash_start = max(solid_to, s)
                if TAIL_END > dash_start:
                    ax.hlines(i, dash_start, TAIL_END,
                              color='steelblue', linewidth=LINE_W, zorder=2, linestyle=DASH_LS)
                    

        # --- Asse X: termina esattamente a TAIL_END (niente 10% extra) ---
        ax.set_xlim(0, TAIL_END)
        ax.margins(x=0)       # rimuove margine automatico
        max_x_value = TAIL_END  # per la logica delle linee rosse sotto

        # ==============================
        # 3) IPOSTASI/RIGOR Verdi (SOPRA)
        #    - Mediane verdi opache; se la mediana è "infinita": solido fino a cap_base + tratteggio fino a TAIL_END
        # ==============================
        # Mapping asse Y statico per righe principali
        y_indices_mapping = {}
        current_y_index = 0
        if macchie_range_valido and macchie_range is not None:
            y_indices_mapping["Macchie ipostatiche"] = current_y_index
            current_y_index += 1
        if rigidita_range_valido and rigidita_range is not None:
            y_indices_mapping["Rigidità cadaverica"] = current_y_index
            current_y_index += 1
        if raffreddamento_calcolabile:
            y_indices_mapping["Raffreddamento cadaverico"] = current_y_index
            current_y_index += 1

        # --- Mediana IPOSTASI (solido + tratteggio se infinita) ---
        if macchie_range_valido and macchie_medi_range is not None and "Macchie ipostatiche" in y_indices_mapping:
            y = y_indices_mapping["Macchie ipostatiche"]
            m_s, m_e = macchie_medi_range
            is_infinite_m = (m_e is None) or (np.isnan(m_e)) or (m_e >= INF_HOURS)

            if not is_infinite_m:
                ax.hlines(y, m_s, m_e, color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
            else:
                solid_to = max(m_s, cap_base)
                if solid_to > m_s and m_s < TAIL_END:
                    ax.hlines(y, m_s, min(solid_to, TAIL_END), color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
                dash_start = max(solid_to, m_s)
                if TAIL_END > dash_start:
                    # uso plot per avere tratteggio sicuro sopra le blu
                    ax.plot([dash_start, TAIL_END], [y, y],
                            color='mediumseagreen', linewidth=LINE_W, alpha=1.0,
                            linestyle=DASH_LS, zorder=3)
                              
                    

        # --- Mediana RIGIDITÀ (solido + tratteggio se infinita) ---
        if rigidita_range_valido and rigidita_medi_range is not None and "Rigidità cadaverica" in y_indices_mapping:
            y = y_indices_mapping["Rigidità cadaverica"]
            r_s, r_e = rigidita_medi_range
            is_infinite_r = (r_e is None) or (np.isnan(r_e)) or (r_e >= INF_HOURS)

            if not is_infinite_r:
                ax.hlines(y, r_s, r_e, color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
            else:
                solid_to = max(r_s, cap_base)
                if solid_to > r_s and r_s < TAIL_END:
                    ax.hlines(y, r_s, min(solid_to, TAIL_END), color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
                dash_start = max(solid_to, r_s)
                if TAIL_END > dash_start:
                    # uso plot per avere tratteggio sicuro sopra le blu
                    ax.plot([dash_start, TAIL_END], [y, y],
                            color='mediumseagreen', linewidth=LINE_W, alpha=1.0,
                            linestyle=DASH_LS, zorder=3)

        # --- Marker corto verde sul punto medio del raffreddamento ---
        if raffreddamento_calcolabile:
            if "Raffreddamento cadaverico" in y_indices_mapping and not (np.isnan(t_min_raff_visualizzato) or np.isnan(t_max_raff_visualizzato)):
                y_pos_raffreddamento = y_indices_mapping["Raffreddamento cadaverico"]
                punto_medio_raffreddamento = (t_min_raff_visualizzato + t_max_raff_visualizzato) / 2.0
                offset = 0.1
                if (punto_medio_raffreddamento - offset) < TAIL_END:
                    ax.hlines(y_pos_raffreddamento,
                              max(0, punto_medio_raffreddamento - offset),
                              min(TAIL_END, punto_medio_raffreddamento + offset),
                              color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
        
         # --- Asse Y, etichette e limiti ---
        ax.set_yticks(range(len(parametri_grafico)))
        ax.set_yticklabels(parametri_grafico, fontsize=15)
        ax.set_xlabel("Ore dal decesso")
        ax.grid(True, axis='x', linestyle=':', alpha=0.6)

        # Intervallo finale in rosso (clippato a TAIL_END)
        if overlap and (np.isnan(comune_fine) or comune_fine > 0):
            if comune_inizio < TAIL_END:
                ax.axvline(max(0, comune_inizio), color='red', linestyle='--')
            if not np.isnan(comune_fine) and comune_fine > 0:
                ax.axvline(min(TAIL_END, comune_fine), color='red', linestyle='--')

        plt.tight_layout()
        st.pyplot(fig)
                             


    # --- NOTE/AVVISI: raccogli in 'avvisi' (niente stampa diretta) ---
    if nota_globale_range_adattato:
        dettagli.append(
            "<p style='color:gray;font-size:small;'>* alcuni parametri sono stati valutati a orari diversi; i range sono stati traslati per renderli confrontabili.</p>"
        )

    if minuti_isp not in [0, 15, 30, 45]:
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
            avvisi.append("Per temperature ambientali &gt; 25 °C, variazioni del fattore di correzione possono influenzare notevolmente i risultati.")
        if Ta_val < 18:
            avvisi.append("Per temperature ambientali &lt; 18 °C, la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati.")
        if temp_difference_small:
            avvisi.append("Essendo minima la differenza tra temperatura rettale e ambientale, è possibile che il cadavere fosse ormai in equilibrio termico con l'ambiente. La stima ottenuta dal raffreddamento cadaverico va interpretata con attenzione.")
        if abs(Tr_val - T0_val) <= 1.0:
            avvisi.append(
                "Considerato che la temperatura rettale è molto simile alla temperatura ante-mortem stimata, "
                "è possibile che il raffreddamento si trovi ancora nella fase di plateau o non sia ancora iniziato; "
                "in tale fase la precisione del metodo è ridotta."
            )
            
        if not raffreddamento_calcolabile:
            avvisi.append("Non è stato possibile applicare il metodo di Henssge (temperature incoerenti o fuori range del nomogramma).")

    # --- Dettaglio del raffreddamento cadaverico con dati di input (da mostrare prima del testo Henssge) ---
    try:
        orario_isp = data_ora_ispezione.strftime('%H:%M')
        data_isp = data_ora_ispezione.strftime('%d.%m.%Y')
    except Exception:
        orario_isp = input_ora_rilievo or "—"
        data_isp = input_data_rilievo.strftime('%d.%m.%Y') if input_data_rilievo else "—"

    ta_txt = f"{Ta_val:.1f}" if Ta_val is not None else "—"
    tr_txt = f"{Tr_val:.1f}" if Tr_val is not None else "—"
    w_txt  = f"{W_val:.1f}"  if W_val  is not None else "—"
    t0_txt = f"{T0_val:.1f}" if T0_val is not None else "—"
    cf_val = st.session_state.get('fattore_correzione', CF_val if CF_val is not None else None)
    cf_txt = f"{cf_val:.2f}" if cf_val is not None else "—"


    cf_descr = build_cf_description(
        cf_value=st.session_state.get("fattore_correzione", 1.0),
        riassunto=st.session_state.get("fc_riassunto_contatori"),
        fallback_text=st.session_state.get("fattori_condizioni_testo")  # opzionale
)



    dettagli.append(
        "<ul><li>Per quanto attiene la valutazione del raffreddamento cadaverico, sono stati considerati gli elementi di seguito indicati."
        "<ul>"
        f"<li>Temperature misurate nel corso dell’ispezione legale verso le ore {orario_isp} del {data_isp}:"
        "<ul>"
        f"<li>Temperatura ambientale: {ta_txt} °C.</li>"
        f"<li>Temperatura rettale: {tr_txt} °C.</li>"
        "</ul>"
        "</li>"
        f"<li>Peso del cadavere misurato in sala autoptica: {w_txt} kg.</li>"
        f"<li>Temperatura corporea ipotizzata al momento della morte: {t0_txt} °C.</li>"
        f"<li>Fattore di correzione ipotizzato dagli scriventi in base alle condizioni ambientali (per quanto noto): {cf_descr}</li>"
        "</ul>"
        "</li></ul>"
    )


    # --- Testo Henssge dettagliato (va nell’expander) ---
    if raffreddamento_calcolabile:
        if 't_min_raff_visualizzato' in locals() and not (np.isnan(t_min_raff_visualizzato) or np.isnan(t_max_raff_visualizzato)):
            hm = _split_hours_minutes(t_min_raff_visualizzato); min_raff_hours, min_raff_minutes = hm if hm else (0, 0)
            hm = _split_hours_minutes(t_max_raff_visualizzato); max_raff_hours, max_raff_minutes = hm if hm else (0, 0)
            min_raff_hour_text = "ora" if min_raff_hours == 1 and min_raff_minutes == 0 else "ore"
            max_raff_hour_text = "ora" if max_raff_hours == 1 and max_raff_minutes == 0 else "ore"

            # Frase Henssge base originale
            testo_raff_base = (
                f"Applicando il nomogramma di Henssge, è possibile stimare che il decesso sia avvenuto tra circa "
                f"{min_raff_hours} {min_raff_hour_text}{'' if min_raff_minutes == 0 else f' {min_raff_minutes} minuti'} e "
                f"{max_raff_hours} {max_raff_hour_text}{'' if max_raff_minutes == 0 else f' {max_raff_minutes} minuti'} "
                f"prima dei rilievi effettuati al momento dell’ispezione legale."
            )

            elenco_extra = []

            # Qd basso (<0.2)
            if not np.isnan(Qd_val_check) and Qd_val_check < 0.2:
                elenco_extra.append(
                    f"<li>"
                    f"I valori ottenuti, tuttavia, sono in parte o totalmente fuori dai range ottimali delle equazioni applicabili "
                    f"(Valore di Qd ottenuto: <b>{Qd_val_check:.5f}</b>, &lt; 0.2) "
                    f"(il range temporale indicato è stato calcolato, grossolanamente, come pari al ±20% del valore medio ottenuto dalla stima del raffreddamento cadaverico - {t_med_raff_hensge_rounded:.1f} ore -, ma tale range è privo di una solida base statistica). "
                    f"In mancanza di ulteriori dati o interpretazioni, si può presumere che il raffreddamento cadaverico fosse ormai concluso. "
                    f"Per tale motivo, il range ottenuto è da ritenersi del tutto indicativo e per la stima dell'epoca del decesso è consigliabile far riferimento principalmente ad altri dati tanatologici."
                    f"</li>"
                )

            # Qd alto e durata > 30h
            if not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and t_med_raff_hensge_rounded_raw > 30:
                elenco_extra.append(
                    f"<li>"
                    f"<span style='color:orange; font-weight:bold;'>"
                    f"La stima media ottenuta dal raffreddamento cadaverico ({t_med_raff_hensge_rounded:.1f} h) è superiore alle 30 ore. "
                    f"L'affidabilità del metodo di Henssge diminuisce significativamente oltre questo intervallo."
                    f"</span>"
                    f"</li>"
                )

            paragrafo = f"<ul><li>{testo_raff_base}"
            if elenco_extra:
                paragrafo += "<ul>" + "".join(elenco_extra) + "</ul>"
            paragrafo += "</li></ul>"
            dettagli.append(paragrafo)

        # Metodo Potente: solo come punto elenco nei dettagli
        if (mt_ore is not None) and (not np.isnan(mt_ore)) and (Qd_val_check is not None) and (Qd_val_check < qd_threshold):
            condizione_temp = "T. amb ≤ 23 °C" if Ta_val <= 23 else "T. amb > 23 °C"
            dettagli.append(
                f"<ul><li>Lo studio di Potente et al. permette di stimare grossolanamente l’intervallo minimo post-mortem quando i dati non consentono di ottenere risultati attendibili con il metodo di Henssge "
                f"(Qd &lt; {qd_threshold} e {condizione_temp}). "
                f"Applicandolo al caso specifico, si può ipotizzare che, al momento dell’ispezione legale, fossero trascorse almeno <b>{mt_ore:.0f}</b> ore (≈ {mt_giorni:.1f} giorni) dal decesso.</li></ul>"
            )


    # --- Descrizioni macchie/rigidità/parametri: tutte nei dettagli ---
    dettagli.append(f"<ul><li>{testi_macchie[macchie_selezionata]}</li></ul>")
    dettagli.append(f"<ul><li>{rigidita_descrizioni[rigidita_selezionata]}</li></ul>")
    for param in parametri_aggiuntivi_da_considerare:
        if param['stato'] not in ('Non valutata', 'Non valutabile/non attendibile'):
            dettagli.append(f"<ul><li>{param['descrizione']}</li></ul>")
    # Punto elenco extra (solo descrizione dettagliata) se sono state osservate alterazioni putrefattive
    if st.session_state.get("alterazioni_putrefattive", False):
        dettagli.append(
            "<ul><li>Per quanto riguarda i processi trasformativi post-mortali (compresi quelli putrefattivi), "
            "la loro insorgenza è influenzata da numerosi fattori, esogeni (ad esempio temperatura ambientale, "
            "esposizione ai fenomeni metereologici…) ed endogeni (temperatura corporea, infezioni prima del decesso, "
            "presenza di ferite…). Poiché tali processi possono manifestarsi in un intervallo temporale estremamente "
            "variabile, da poche ore a diverse settimane dopo il decesso, la loro valutazione non permette di formulare "
            "ulteriori precisazioni sull’epoca della morte.</li></ul>"
        )

    # --- Frase finale: identica alla tua logica, ma salvata in 'frase_finale_html' ---
    if overlap:
        try:
            isp = data_ora_ispezione
        except Exception:
            return

        limite_superiore_infinito = np.isnan(comune_fine) or comune_fine == INF_HOURS

        if (not np.isnan(Qd_val_check) and Qd_val_check < 0.3
            and comune_inizio > 30
            and (np.isnan(comune_fine) or comune_fine == INF_HOURS)):
            hm = _split_hours_minutes(comune_inizio); comune_inizio_hours, comune_inizio_minutes = hm if hm else (0, 0)
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 and comune_inizio_minutes == 0 else "ore"
            da = isp - datetime.timedelta(hours=comune_inizio)
            if not np.isnan(Qd_val_check) and Qd_val_check <= 0.2 and not np.isnan(mt_ore) and mt_ore > 30:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                    f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                    f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
                )
            else:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                    f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                    f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}. "
                    f"Occorre tener conto che l'affidabilità del metodo di Henssge diminuisce significativamente quando sono trascorse più di 30 ore dal decesso, e tale dato è da considerarsi del tutto indicativo."
                )
        elif limite_superiore_infinito:
            if mt_ore is not None and not np.isnan(mt_ore):
                if abs(comune_inizio - mt_ore) < 0.25:
                    comune_inizio = round(mt_ore)
            hm = _split_hours_minutes(comune_inizio); comune_inizio_hours, comune_inizio_minutes = hm if hm else (0, 0)
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 and comune_inizio_minutes == 0 else "ore"
            da = isp - datetime.timedelta(hours=comune_inizio)
            testo = (
                f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
            )
        elif comune_inizio == 0:
            hm = _split_hours_minutes(comune_fine); comune_fine_hours, comune_fine_minutes = hm if hm else (0, 0)
            fine_hour_text = "ora" if comune_fine_hours == 1 else "ore"
            da = isp - datetime.timedelta(hours=comune_fine)
            testo = (
                f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                f"consente di stimare che la morte sia avvenuta <b>non oltre</b> "
                f"{comune_fine_hours} {fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero successivamente alle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
            )
        else:
            hm = _split_hours_minutes(comune_inizio); comune_inizio_hours, comune_inizio_minutes = hm if hm else (0, 0)
            hm = _split_hours_minutes(comune_fine); comune_fine_hours, comune_fine_minutes = hm if hm else (0, 0)
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 else "ore"
            comune_fine_hour_text = "ora" if comune_fine_hours == 1 else "ore"
            da = isp - datetime.timedelta(hours=comune_fine)
            aa = isp - datetime.timedelta(hours=comune_inizio)
            if da.date() == aa.date():
                testo = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{comune_inizio_hours} {comune_inizio_hour_text}{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} e "
                    f"{comune_fine_hours} {comune_fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {da.strftime('%H:%M')} e le ore {aa.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
                )
            else:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{comune_inizio_hours} {comune_inizio_hour_text}{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} e "
                    f"{comune_fine_hours} {comune_fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')} e le ore {aa.strftime('%H:%M')} del {aa.strftime('%d.%m.%Y')}."
                )
        frase_finale_html = f"<b>{testo}</b>"

    # --- Variante “Senza considerare Potente” (se applicabile) → mostrata sotto la frase finale, non in expander
    if any("potente" in nome.lower() for nome in nomi_parametri_usati_per_intersezione):
        range_inizio_senza_potente = []
        range_fine_senza_potente = []

        if macchie_range_valido and macchie_range is not None:
            range_inizio_senza_potente.append(macchie_range[0]); range_fine_senza_potente.append(macchie_range[1])
        if rigidita_range_valido and rigidita_range is not None:
            range_inizio_senza_potente.append(rigidita_range[0]); range_fine_senza_potente.append(rigidita_range[1])
        for p in parametri_aggiuntivi_da_considerare:
            if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1]):
                range_inizio_senza_potente.append(p["range_traslato"][0]); range_fine_senza_potente.append(p["range_traslato"][1])
        if raffreddamento_calcolabile:
            range_inizio_senza_potente.append(t_min_raff_hensge); range_fine_senza_potente.append(t_max_raff_hensge)

        if len(range_inizio_senza_potente) >= 2:
            inizio_senza_potente = max(range_inizio_senza_potente)
            fine_senza_potente = min(range_fine_senza_potente)
            if inizio_senza_potente <= fine_senza_potente:
                hm = _split_hours_minutes(inizio_senza_potente); inizio_h, inizio_m = hm if hm else (0, 0)
                hm = _split_hours_minutes(fine_senza_potente); fine_h, fine_m = hm if hm else (0, 0)
                inizio_text = "ora" if inizio_h == 1 and inizio_m == 0 else "ore"
                fine_text = "ora" if fine_h == 1 and fine_m == 0 else "ore"
                dt_inizio = data_ora_ispezione - datetime.timedelta(hours=fine_senza_potente)
                dt_fine = data_ora_ispezione - datetime.timedelta(hours=inizio_senza_potente)
                frase_secondaria_html = (
                    f"<b>Senza considerare lo studio di Potente</b>, la valutazione complessiva consente di stimare che la morte sia avvenuta tra circa "
                    f"{inizio_h} {inizio_text}{'' if inizio_m == 0 else f' {inizio_m} minuti'} e "
                    f"{fine_h} {fine_text}{'' if fine_m == 0 else f' {fine_m} minuti'} "
                    f"prima dei rilievi, ovvero tra le ore {dt_inizio.strftime('%H:%M')} del {dt_inizio.strftime('%d.%m.%Y')} "
                    f"e le ore {dt_fine.strftime('%H:%M')} del {dt_fine.strftime('%d.%m.%Y')}."
                )

    # --- Riepilogo parametri usati (era arancione piccolo) → dettagli
    if overlap and len(nomi_parametri_usati_per_intersezione) > 0:
        nomi_parametri_finali_per_riepilogo = []
        for nome in nomi_parametri_usati_per_intersezione:
            if ("raffreddamento cadaverico" in nome.lower()
                and "potente" not in nome.lower()
                and mt_ore is not None
                and not np.isnan(mt_ore)
                and abs(comune_inizio - mt_ore) < 0.25):
                continue
            nomi_parametri_finali_per_riepilogo.append(nome)
        if len(nomi_parametri_finali_per_riepilogo) == 1:
            p = nomi_parametri_finali_per_riepilogo[0]
            dettagli.append(f"<p style='color:orange;font-size:small;'>La stima complessiva si basa sul seguente parametro: {p[0].lower() + p[1:]}.</p>")
        elif len(nomi_parametri_finali_per_riepilogo) > 1:
            parametri_usati_str = ', '.join(p[0].lower() + p[1:] for p in nomi_parametri_finali_per_riepilogo[:-1])
            parametri_usati_str += f" e {nomi_parametri_finali_per_riepilogo[-1][0].lower() + nomi_parametri_finali_per_riepilogo[-1][1:]}"
            dettagli.append(f"<p style='color:orange;font-size:small;'>La stima complessiva si basa sui seguenti parametri: {parametri_usati_str}.</p>")


    # --- Messaggi di discordanza (rossi) → dettagli
    num_potential_ranges_used = sum(
        1
        for start, end in zip(ranges_per_intersezione_inizio, ranges_per_intersezione_fine)
        if start is not None and end is not None
    )


    # === RENDER COMPATTO ===
    if avvisi:
        with st.expander(f"⚠️ Avvertenze ({len(avvisi)})"):
            st.warning("\n".join(f"- {msg}" for msg in avvisi))

    if frase_finale_html:
        st.markdown(frase_finale_html, unsafe_allow_html=True)
    with st.expander("Descrizioni dettagliate"):
        if frase_secondaria_html:
            st.markdown(
                f"<div style='border:1px solid #ccc; padding:10px; color:gray; font-size:small;'>{frase_secondaria_html}</div>",
                unsafe_allow_html=True
            )
        for blocco in dettagli:
            st.markdown(blocco, unsafe_allow_html=True)



 
    if overlap and len(nomi_parametri_usati_per_intersezione) > 0:
        # Filtra la lista dei nomi da mostrare nel riepilogo finale
        nomi_parametri_finali_per_riepilogo = []
        for nome in nomi_parametri_usati_per_intersezione:
            # Escludi il raffreddamento Henssge generico se non usato
            if (
                "raffreddamento cadaverico" in nome.lower()
                and "potente" not in nome.lower()
                and mt_ore is not None
                and not np.isnan(mt_ore)
                and abs(comune_inizio - mt_ore) < 0.25
            ):
                continue
            nomi_parametri_finali_per_riepilogo.append(nome)

        num_parametri_usati_intersezione = len(nomi_parametri_finali_per_riepilogo)
        if num_parametri_usati_intersezione == 1:
            p = nomi_parametri_finali_per_riepilogo[0]
            messaggio_parametri = f"La stima complessiva si basa sul seguente parametro: {p[0].lower() + p[1:]}."
        elif num_parametri_usati_intersezione > 1:
            parametri_usati_str = ', '.join(p[0].lower() + p[1:] for p in nomi_parametri_finali_per_riepilogo[:-1])
            parametri_usati_str += f" e {nomi_parametri_finali_per_riepilogo[-1][0].lower() + nomi_parametri_finali_per_riepilogo[-1][1:]}"
            messaggio_parametri = f"La stima complessiva si basa sui seguenti parametri: {parametri_usati_str}."
        else:
            messaggio_parametri = None

        if messaggio_parametri:
            st.markdown(
                f"<p style='color:orange;font-size:small;'>{messaggio_parametri}</p>",
                unsafe_allow_html=True
            )

    elif not overlap and num_potential_ranges_used >= 2:
        st.markdown(
            "<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>",
            unsafe_allow_html=True
        )
    elif ranges_in_disaccordo_completa(ranges_per_intersezione_inizio, ranges_per_intersezione_fine):
        st.markdown(
            "<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>",
            unsafe_allow_html=True
        )


# Al click del pulsante, esegui la funzione principale
if pulsante_genera_stima:
    aggiorna_grafico()
