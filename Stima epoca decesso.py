# -*- coding: utf-8 -*-
# Streamlit app: Stima epoca decesso
# Revisione con correzioni di robustezza e piccoli fix senza variare la logica di calcolo/UX.

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

if "fattore_correzione" not in st.session_state:
    st.session_state["fattore_correzione"] = 1.0

# Definiamo un valore che rappresenta "infinito" o un limite superiore molto elevato per i range aperti
INF_HOURS = 200  # Un valore sufficientemente grande per la scala del grafico e i calcoli

# =========================
# Utility cache per Excel
# =========================

@st.cache_data
def load_tabelle_correzione():
    """
    Carica e normalizza le tabelle usate da calcola_fattore.
    Restituisce (tabella1, tabella2) o solleva eccezione con messaggio chiaro.
    """
    t1 = pd.read_excel("tabella rielaborata.xlsx")
    t1['Fattore'] = pd.to_numeric(t1['Fattore'], errors='coerce')
    for col in ["Ambiente", "Vestiti", "Coperte", "Superficie d'appoggio", "Correnti"]:
        t1[col] = t1[col].astype(str).str.strip()
    t2 = pd.read_excel("tabella secondaria.xlsx")
    return t1, t2

# =========================
# Funzioni esistenti (con fix robustezza)
# =========================

def calcola_fattore(peso):
    import streamlit as st

    # Caricamento tabelle con cache + gestione errori
    try:
        tabella1, tabella2 = load_tabelle_correzione()
    except FileNotFoundError as e:
        st.error("Impossibile caricare i file Excel per il calcolo del fattore di correzione. "
                 "Verifica che 'tabella rielaborata.xlsx' e 'tabella secondaria.xlsx' siano presenti.")
        return
    except Exception as e:
        st.error(f"Errore nel caricamento delle tabelle: {e}")
        return

    st.markdown("""<style> /* ... (stile invariato) ... */ </style>""", unsafe_allow_html=True)
    st.markdown('<div class="fattore-correzione-section">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # --- COLONNA 1: CONDIZIONE CORPO ---
    with col1:
        st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Condizioni del corpo</p>", unsafe_allow_html=True)
        stato_corpo = st.radio("", ["Asciutto", "Bagnato", "Immerso"], label_visibility="collapsed")
        corpo_immerso = (stato_corpo == "Immerso")
        corpo_bagnato = (stato_corpo == "Bagnato")
        corpo_asciutto = (stato_corpo == "Asciutto")

    # inizializzazione variabili
    copertura_speciale = False
    scelta_vestiti = "/"
    superficie = "/"
    corrente = "/"

    # --- COLONNA 2: COPERTURA ---
    with col2:
        if not (corpo_immerso or corpo_bagnato):
            st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Copertura</p>", unsafe_allow_html=True)
            opzioni_coperte = [
                "Nessuna coperta",
                "Coperta spessa (es copriletto)",
                "Coperte più spesse (es coperte di lana)",
                "Coperta pesante (es piumino imbottito)",
                "Molte coperte pesanti"
            ]
            if corpo_asciutto:
                opzioni_coperte += ["Strato di foglie di medio spessore", "Spesso strato di foglie"]

            scelta_coperte = st.radio("", opzioni_coperte, label_visibility="collapsed", key="scelta_coperte_radio")
        else:
            scelta_coperte = "/"

    copertura_speciale = scelta_coperte in ["Strato di foglie di medio spessore", "Spesso strato di foglie"]

    # --- COLONNA 1: ABBIGLIAMENTO (dopo copertura) ---
    # Mostriamo l'abbigliamento sia per Asciutto che per Bagnato (non per Immerso o copertura speciale)
    if (corpo_asciutto or corpo_bagnato) and not corpo_immerso and not copertura_speciale:
        with col1:
            st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Abbigliamento</p>", unsafe_allow_html=True)
            scelta_vestiti = st.radio("", [
                "Nudo",
                "1-2 strati sottili",
                "2-3 strati sottili",
                "3-4 strati sottili",
                "1-2 strati spessi",
                "˃4 strati sottili o ˃2 spessi",
                "Moltissimi strati"
            ], label_visibility="collapsed")
    elif corpo_immerso or copertura_speciale:
        scelta_vestiti = "/"

    # --- COLONNA 2: CORRENTI ---
    with col2:
        if not copertura_speciale:
            mostra_corrente = False
            if corpo_bagnato:
                # per Bagnato mostra sempre la scelta correnti (in tabella non ci sono coperte/superficie)
                mostra_corrente = True
            elif corpo_asciutto:
                if scelta_vestiti in ["Nudo", "1-2 strati sottili"] and scelta_coperte == "Nessuna coperta":
                    mostra_corrente = True

            if mostra_corrente:
                st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Presenza di correnti</p>", unsafe_allow_html=True)
                corrente = st.radio(
                    "",
                    ["Esposto a corrente d'aria", "Nessuna corrente"],
                    index=1,
                    label_visibility="collapsed",
                    key="radio_corrente"
                )
            elif corpo_immerso:
                st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Presenza di correnti</p>", unsafe_allow_html=True)
                corrente = st.radio(
                    "",
                    ["In acqua corrente", "In acqua stagnante"],
                    index=1,
                    label_visibility="collapsed",
                    key="radio_acqua"
                )
            else:
                corrente = "/"

    # --- COLONNA 3: SUPERFICIE ---
    with col3:
        if not (corpo_immerso or corpo_bagnato or copertura_speciale):
            st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Superficie di appoggio</p>", unsafe_allow_html=True)
            mostra_foglie = scelta_vestiti == "Nudo" and scelta_coperte == "Nessuna coperta"

            opzioni_superficie = [
                "Pavimento di casa, terreno o prato asciutto, asfalto",
                "Imbottitura pesante (es sacco a pelo isolante, polistirolo, divano imbottito)",
                "Materasso o tappeto spesso",
                "Cemento, pietra, pavimento in PVC, pavimentazione esterna"
            ]
            if scelta_vestiti == "Nudo":
                opzioni_superficie.append("Superficie metallica spessa, all'esterno.")
            if mostra_foglie:
                opzioni_superficie += ["Foglie umide (≥2 cm)", "Foglie secche (≥2 cm)"]

            superficie = st.radio("", opzioni_superficie, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- CALCOLO TABELLA E DESCRIZIONE ---
    valori = {
        "Ambiente": stato_corpo,
        "Vestiti": scelta_vestiti,
        "Coperte": scelta_coperte,
        "Superficie d'appoggio": superficie,
        "Correnti": corrente
    }
    # strip sui valori scelti dall'utente per evitare mismatch da spazi
    valori = {k: (str(v).strip() if v is not None else v) for k, v in valori.items()}

    riga = tabella1[
        (tabella1["Ambiente"] == valori["Ambiente"]) &
        (tabella1["Vestiti"] == valori["Vestiti"]) &
        (tabella1["Coperte"] == valori["Coperte"]) &
        (tabella1["Superficie d'appoggio"] == valori["Superficie d'appoggio"]) &
        (tabella1["Correnti"] == valori["Correnti"])
    ]

    if riga.empty:
        st.warning("Nessuna combinazione valida trovata nella tabella.")
        return
    if len(riga) > 1:
        st.info("Più combinazioni valide trovate nella tabella: viene utilizzata la prima corrispondenza.")

    fattore = riga["Fattore"].values[0]
    try:
        fattore_base = float(fattore)
    except Exception:
        st.warning("Il valore di 'Fattore' nella tabella non è numerico. Impossibile proseguire.")
        return

    fattore_finale = fattore_base

    # Applica Tabella 2 solo quando serve (
    if fattore_base >= 1.4 and abs(peso - 70.0) > 0.01:
        try:
            t2 = tabella2.copy()

            # Provo a interpretare le intestazioni di colonna come pesi (es. "70", "70 kg", "W70")
            def parse_peso(col):
                s = str(col).strip().lower().replace('kg', '').replace('w', '')
                num = ''.join(ch for ch in s if (ch.isdigit() or ch in '.,'))
                num = num.replace(',', '.')
                return float(num) if num not in ("", ".", ",") else None

            pesi_col = {col: parse_peso(col) for col in t2.columns}
            pesi_col = {col: w for col, w in pesi_col.items() if w is not None}
            if not pesi_col:
                raise ValueError("Nessuna colonna peso valida in Tabella 2.")

            # Colonna ~70 kg (se manca 70 preciso, prendo la più vicina)
            col_70 = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - 70.0))
            serie70 = pd.to_numeric(t2[col_70], errors='coerce')

            # Riga della Tabella 2 che più si avvicina al fattore base nella colonna 70 kg
            idx_match = (serie70 - fattore_base).abs().idxmin()

            # Colonna del peso utente (o la più vicina)
            col_user = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - float(peso)))

            val_user = pd.to_numeric(t2.loc[idx_match, col_user], errors='coerce')
            if pd.notna(val_user):
                fattore_finale = float(val_user)

        except Exception as e:
            st.warning(f"Impossibile applicare la correzione per il peso (uso Tabella 1): {e}")

    # Output
    if abs(fattore_finale - fattore_base) > 1e-9:
        st.success(f"Fattore di correzione (Tabella 1 → adattato per il peso): {fattore_finale:.2f}")
        st.caption(f"Valore Tabella 1: {fattore_base:.2f} – peso considerato: {peso:.1f} kg")
    else:
        st.success(f"Fattore di correzione calcolato: {fattore_finale:.2f}")

    # Pulsante per applicare il fattore calcolato al campo principale (senza aggiornamenti automatici)
    def _apply_fattore(val):
        st.session_state["fattore_correzione"] = round(float(val), 2)
        st.session_state["mostra_modulo_fattore"] = False  # opzionale: richiude l’expander

    st.button(
        "✅ Usa questo fattore",
        key="usa_fattore_btn",
        on_click=_apply_fattore,
        args=(fattore_finale,)
    )


def arrotonda_quarto_dora(dt: datetime.datetime) -> datetime.datetime:
    """Arrotonda un datetime al quarto d’ora più vicino."""
    minuti = (dt.minute + 7) // 15 * 15
    if minuti == 60:
        dt += datetime.timedelta(hours=1)
        minuti = 0
    return dt.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=minuti)

st.set_page_config(page_title="Stima Epoca della Morte", layout="centered")
st.title("Stima epoca decesso")

# --- BOX STILE PER IPOSTASI & RIGOR ---
st.markdown("""
<style>
.box-tanatologia {
    border: 1.5px solid #e0e0e0;
    border-radius: 10px;
    padding: 12px 12px 6px;
    background: #fafafa;
    margin-top: 6px;
}
.box-tanatologia .box-title {
    font-weight: 600;
    font-size: 0.95rem;
    margin: 0 0 8px 2px;
    color: #444;
}
@media (max-width: 600px){
    .box-tanatologia { padding: 10px; }
    .box-tanatologia .box-title { font-size: 0.92rem; }
}
</style>
""", unsafe_allow_html=True)

# --- Dati per Macchie Ipostatiche e Rigidità Cadaverica (Esistenti) ---
opzioni_macchie = {
    "Non ancora comparse": (0, 3),
    "Migrabilità totale": (0, 6),
    "Migrabilità parziale": (4, 24),
    "Migrabilità perlomeno parziale": (0, 24),
    "Fissità assoluta": (10, INF_HOURS),
    "Non valutabili/Non attendibili": None
}
macchie_medi = {
    "Non ancora comparse": (0, 0.33),
    "Migrabilità totale": (0.33, 6),
    "Migrabilità parziale": (6, 12),
    "Migrabilità perlomeno parziale": None,
    "Fissità assoluta": (12, INF_HOURS),
    "Non valutabili/Non attendibili": None
}
testi_macchie = {
    "Non ancora comparse": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, non fossero ancora comparse. Secondo le comuni nozioni della medicina legale, le ipostasi compaiono entro 3 ore dal decesso (generalmente entro 15-20 minuti).",
    "Migrabilità totale": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero in una fase di migrabilità totale. Secondo le comuni nozioni della medicina legale, tale fase indica che fossero trascorse meno di 6 ore dal decesso. Generalmente le ipostasi compaiono dopo 20 minuti dal decesso",
    "Migrabilità parziale": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero in una fase di migrabilità parziale. Secondo le comuni nozioni della medicina legale, tale fase indica che fossero trascorse tra le 4 ore e le 24 ore dal decesso.",
    "Migrabilità perlomeno parziale": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero in una fase di migrabilità perlomeno parziale (modificando la posizione del cadavere si sono modificate le macchie ipostatiche, ma, per le modalità e le tempistiche di esecuzione dell’ispezione legale, non è stato possibile dettagliare l’entità del fenomeno). Secondo le comuni nozioni della medicina legale, tale fase indica che fossero trascorse meno di 24 ore dal decesso.",
    "Fissità assoluta": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero in una fase di fissità assoluta. Secondo le comuni nozioni della medicina legale, tale fase indica che fossero trascorse più di 10 ore dal decesso (fino a 30 ore le macchie possono non modificare la loro posizione alla movimentazione del corpo, ma la loro intensità può affievolirsi).",
    "Non valutabili/Non attendibili": "Le macchie ipostatiche non sono state valutate o i rilievi non sono considerati attendibili per la stima dell'epoca della morte."
}

opzioni_rigidita = {
    "Non ancora comparsa": (0, 7),
    "In via di formazione, intensificazione e generalizzazione": (0.5, 20),
    "Presente e generalizzata": (2, 96),
    "In via di risoluzione": (24, 192),
    "Ormai risolta": (24, INF_HOURS),
    "Non valutabile/Non attendibile": None
}
rigidita_medi = {
    "Non ancora comparsa": (0, 3),
    "In via di formazione, intensificazione e generalizzazione": (2, 10),
    "Presente e generalizzata": (10, 85),
    "In via di risoluzione": (29, 140),
    "Ormai risolta": (76, INF_HOURS)
}
rigidita_descrizioni = {
    "Non ancora comparsa": "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, non fosse ancora comparsa. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorse meno di 7 ore dal decesso (in genere la rigidità compare entro 2 - 3 ore dal decesso).",
    "In via di formazione, intensificazione e generalizzazione": "È possibile valutare che la rigidità cadaverica fosse in via di formazione, intensificazione e generalizzazione. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorsi almeno 30 minuti dal decesso ma meno di 20 ore da esso (generalmente la formazione della rigidità si completa in 6-10 ore).",
    "Presente e generalizzata": "È possibile valutare che la rigidità cadaverica fosse presente e generalizzata. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorse almeno 2 ore dal decesso ma meno di 96 ore da esso, cioè meno di 4 giorni (in genere la rigidità persiste sino a 29 – 85 ore).",
    "In via di risoluzione": "È possibile valutare che la rigidità cadaverica fosse in via di risoluzione. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorse almeno 24 ore dal decesso ma meno di 192 ore da esso, cioè meno di 8 giorni (in genere la rigidità cadaverica inizia a risolversi dopo 57 ore, cioè dopo 2 giorni e mezzo dal decesso).",
    "Ormai risolta": "È possibile valutare che la rigidità cadaverica fosse ormai risolta. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorse almeno 24 ore dal decesso (in genere la rigidità scompare entro 76 ore dal decesso, cioè dopo poco più  di 3 giorni).",
    "Non valutabile/Non attendibile": "La rigidità cadaverica non è stata valutata o i rilievi non sono considerati attendibili per la stima dell'epoca della morte."
}

# --- Dati per i Nuovi Parametri Aggiuntivi ---
dati_parametri_aggiuntivi = {
    "Eccitabilità elettrica sopraciliare": {
        "opzioni": ["Non valutata", "Fase I", "Fase II", "Fase III", "Fase IV", "Fase V", "Fase VI", "Nessuna reazione", "Non valutabile/non attendibile"],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (5, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Fase VI": (1, 6),
            "Fase V": (2, 7),
            "Fase IV": (3, 8),
            "Fase III": (3.5, 13),
            "Fase II": (5, 16),
            "Fase I": (5, 22),
                    },
         "descrizioni": {
             "Fase VI": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata dei muscoli della fronte, dell’orbita, della guancia. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra 1 e 6 ore prima delle valutazioni del dato tanatologico.",
             "Fase V": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata dei muscoli della fronte e dell’orbita. Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il decesso fosse avvenuto tra le 2 e le 7 ore prima delle valutazioni del dato tanatologico.",
             "Fase IV": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata dei muscoli orbicolari (superiori e inferiori). Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il decesso fosse avvenuto tra le 3 e le 8 ore prima delle valutazioni del dato tanatologico.",
             "Fase III": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione dei muscoli dell’intera palpebra superiore. Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il decesso fosse avvenuto tra le 3 ore e 30 minuti e le 13 ore prima delle valutazioni del dato tanatologico.",
             "Fase II": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione dei muscoli di meno di 2/3 della palpebra superiore. Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il decesso fosse avvenuto tra le 5 e le 16 ore prima delle valutazioni del dato tanatologico.",
             "Fase I": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione accennata di una minima porzione della palpebra superiore (meno di 1/3). Tale reazione di eccitabilità muscolare elettrica residua e suggerisce che il decesso fosse avvenuto tra le 5 e le 22 ore prima delle valutazioni del dato tanatologico.",
             "Non valutabile/non attendibile": "Non è stato possibile valutare l'eccitabilità muscolare elettrica residua sopraciliare o il suo rilievo non è da considerarsi attendibile.",
             "Nessuna reazione": "L’applicazione di uno stimolo elettrico in regione sopraciliare non ha prodotto contrazioni muscolari. Tale risultato permette solamente di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse più di 5 ore dal decesso"
         }
    },
    "Eccitabilità elettrica peribuccale": {
        "opzioni": ["Non valutata", "Marcata ed estesa (+++)", "Discreta (++)", "Accennata (+)", "Nessuna reazione", "Non valutabile/non attendibile"],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (6, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Marcata ed estesa (+++)": (0, 2.5), # 2 ore 30 minuti = 2.5 ore
            "Discreta (++)": (1, 5),
            "Accennata (+)": (2, 6)
        },
        "descrizioni": {
            "Marcata ed estesa (+++)": "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione marcata ai muscoli peribuccali estesasi anche ai muscoli facciali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto meno di 2 ore e mezzo prima delle valutazioni del dato tanatologico.",
            "Discreta (++)": "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione discreta ai muscoli peribuccali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra le 2 e le 6 ore prima delle valutazioni del dato tanatologico.",
            "Accennata (+)": "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione solo accennata dei muscoli peribuccali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra  1 e  5 ore prima delle valutazioni del dato tanatologico.",
            "Non valutata/non attendibile": "Non è stato possibile valutare l'eccitabilità muscolare elettrica residua peribuccale o i rilievi non sono  attendibili per la stima dell'epoca della morte.",
            "Nessuna reazione": "L’applicazione di uno stimolo elettrico in regione peribuccale non ha prodotto contrazioni muscolari. Tale risultato permette solamente di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse più di 6 ore dal decesso."
        }
    },
    "Eccitabilità muscolare meccanica": {
        "opzioni": ["Non valutata", "Contrazione reversibile dell’intero muscolo", "Formazione di una tumefazione reversibile", "Formazione di una piccola tumefazione persistente", "Nessuna reazione", "Non valutabile/non attendibile"],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (1.5, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Formazione di una piccola tumefazione persistente": (0, 12), # Meno di 12 ore = 0-12 (Henssge dice 13)
            "Formazione di una tumefazione reversibile": (2, 5),
            "Contrazione reversibile dell’intero muscolo": (0, 2)   # Meno di 2 ore = 0-2
        },
         "descrizioni": {
             "Formazione di una piccola tumefazione persistente": "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione di una piccola tumefazione persistente del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce che il decesso fosse avvenuto meno di 12 ore prima delle valutazioni del dato tanatologico.",
             "Formazione di una tumefazione reversibile": "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione di una tumefazione reversibile del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce che il decesso fosse avvenuto tra le 2 e le 5 ore prima delle valutazioni del dato tanatologico.",
             "Contrazione reversibile dell’intero muscolo": "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla contrazione reversibile dell’intero muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce che il decesso fosse avvenuto meno di 2 ore prima delle valutazioni del dato tanatologico.",
             "Non valutabile/non attendibile": "Non è stato possibile valutare l'eccitabilità muscolare meccanica o i rilievi non sono  attendibili per la stima dell'epoca della morte.",
             "Nessuna reazione": "L’applicazione di uno stimolo meccanico al muscolo del braccio non ha prodotto contrazioni muscolari evidenti. Tale risultato permette solamente di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse piû di 1 ora e 30 minuti dal decesso."
         }
    },
    "Eccitabilità chimica pupillare": {
        "opzioni": ["Non valutata", "Non valutabile/non attendibile","Positiva", "Negativa"],
        "range": {
            "Non valutata": None,
            "Non valutabile/non attendibile": None,
            "Positiva": (0, 30), # Meno di 30 ore = 0-30
            "Negativa": (5, INF_HOURS) # Più di 5 ore. Usiamo un limite superiore elevato (200h) per il grafico e i calcoli, coerente con gli altri range massimi.(con arropina hansegee dice 3- 10
        },
         "descrizioni": {
             "Positiva": "L’eccitabilità pupillare chimica residua, nel momento dell’ispezione legale, era caratterizzata da una risposta dei muscoli pupillari dell’occhio (con aumento del diametro della pupilla) all’instillazione intraoculare di atropina. Tale reazione suggerisce che il decesso fosse avvenuto meno di 30 ore prima delle valutazioni medico legali.",
             "Negativa": "L’eccitabilità pupillare chimica residua, nel momento dell’ispezione legale, era caratterizzata da una assenza di risposta dei muscoli pupillari dell’occhio (con aumento del diametro della pupilla) all’instillazione intraoculare di atropina. Tale reazione suggerisce che il decesso fosse avvenuto più di 5 ore prima delle valutazioni medico legali.",
             "Non valutabile/non attendibile": "L'eccitabilità chimica pupillare non era valutabile o i rilievi non sono considerati attendibili per la stima dell'epoca della morte."
         }
    }
}
nomi_brevi = {
    "Macchie ipostatiche": "Ipostasi",
    "Rigidità cadaverica": "Rigor",
    "Raffreddamento cadaverico": "Raffreddamento",
    "Eccitabilità elettrica peribuccale": "Ecc. elettrica peribuccale",
    "Eccitabilità elettrica sopraciliare": "Ecc. elettrica sopraciliare",
    "Eccitabilità chimica pupillare": "Ecc. pupillare",
    "Eccitabilità muscolare meccanica": "Ecc. meccanica"
}

# --- Funzioni di Utilità e Calcolo Henssge (Esistenti) ---
def round_quarter_hour(x):
    if np.isnan(x):
        return np.nan
    return np.round(x * 2) / 2

def calcola_raffreddamento(Tr, Ta, T0, W, CF):
    # Controllo per temperature non valide per il calcolo di Henssge
    if Tr is None or Ta is None or T0 is None or W is None or CF is None:
         return np.nan, np.nan, np.nan, np.nan, np.nan # Restituisce 5 NaN
    #
    # Considera non valido se Tr è "molto vicino" o inferiore a Ta
    temp_tolerance = 1e-6
    if Tr <= Ta + temp_tolerance:
        return np.nan, np.nan, np.nan, np.nan, np.nan # Restituisce 5 NaN
    # Controllo esplicito per evitare divisione per zero nel calcolo di Qd
    if abs(T0 - Ta) < temp_tolerance: # Controlla se il denominatore è molto vicino a zero
         return np.nan, np.nan, np.nan, np.nan, np.nan # Restituisce 5 NaN

    # Ora calcola Qd solo se i controlli iniziali sono passati
    Qd = (Tr - Ta) / (T0 - Ta)

    # Assicurati che Qd sia un valore valido e rientri in un range plausibile (es. > 0 e <= 1)
    if np.isnan(Qd) or Qd <= 0 or Qd > 1:
         return np.nan, np.nan, np.nan, np.nan, np.nan # Restituisce 5 NaN

    A = 1.25 if Ta <= 23 else 10/9
    B = -1.2815 * (CF * W)**(-5/8) + 0.0284

    def Qp(t):
        try:
            if t < 0:
                return np.inf
            val = A * np.exp(B * t) + (1 - A) * np.exp((A / (A - 1)) * B * t)
            if np.isinf(val) or abs(val) > 1e10:
                 return np.nan
            return val
        except OverflowError:
             return np.nan
        except Exception:
             return np.nan

    t_med_raw = np.nan

    qp_at_0 = Qp(0)
    qp_at_48 = Qp(480)

    eps = 1e-9
    if np.isnan(qp_at_0) or np.isnan(qp_at_48) or not (min(qp_at_48, qp_at_0) - eps <= Qd <= max(qp_at_48, qp_at_0) + eps):
        t_med_raw = np.nan
    else:
         try:
             sol = root_scalar(lambda t: Qp(t) - Qd, bracket=[0, 160], method='bisect')
             t_med_raw = sol.root
         except ValueError:
             t_med_raw = np.nan
         except Exception:
             t_med_raw = np.nan

    Dt_raw = 0

    if not np.isnan(t_med_raw) and not np.isnan(Qd):
         if Qd <= 0.2:
              Dt_raw = t_med_raw * 0.20
         elif CF == 1:
              Dt_raw = 2.8 if Qd > 0.5 else 3.2 if Qd > 0.3 else 4.5
         else: # CF != 1
              Dt_raw = 2.8 if Qd > 0.5 else 4.5 if Qd > 0.3 else 7

    t_med = round_quarter_hour(t_med_raw) if not np.isnan(t_med_raw) else np.nan
    t_min = round_quarter_hour(t_med_raw - Dt_raw) if not np.isnan(t_med_raw) else np.nan
    t_max = round_quarter_hour(t_med_raw + Dt_raw) if not np.isnan(t_med_raw) else np.nan

    t_min = max(0.0, t_min) if not np.isnan(t_min) else np.nan

    return t_med, t_min, t_max, t_med_raw, Qd
#
def ranges_in_disaccordo_completa(r_inizio, r_fine):
    intervalli = []
    for start, end in zip(r_inizio, r_fine):
        s = start if not np.isnan(start) else -np.inf
        e = end if not np.isnan(end) else np.inf
        intervalli.append((s, e))

    for i, (s1, e1) in enumerate(intervalli):
        si_sovrappone = False
        for j, (s2, e2) in enumerate(intervalli):
            if i == j:
                continue
            if s1 <= e2 and s2 <= e1:
                si_sovrappone = True
                break
        if not si_sovrappone:
            return True  # almeno uno è completamente isolato
    return False

# --- Definizione Stile e Widget ---
style = {'description_width': 'initial'}

with st.container():

    # 📌 1. Data e ora ispezione legale
    st.markdown("<div style='font-size: 0.88rem;'>Data e ora dei rilievi:</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="small")
    with col1:
        input_data_rilievo = st.date_input(
            "Data ispezione legale:",
            value=datetime.date.today(),
            label_visibility="collapsed",
            key="data_ispezione_legale_main"
        )
    with col2:
        input_ora_rilievo = st.text_input(
            "Ora ispezione legale (HH:MM):",
            value="00:00",
            label_visibility="collapsed",
            key="ora_ispezione_legale_main"
        )

    # 🔹 Ancoraggio per stilare il container successivo come riquadro
    st.markdown('<div id="box-tanatologia"></div>', unsafe_allow_html=True)

    # 🔹 Container che conterrà Ipostasi e Rigidità (verrà stilato come riquadro)
    with st.container():
        st.markdown('<div class="box-title">Segni cadaverici principali</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="small")
        with col1:
            st.markdown("<div style='font-size: 0.88rem;'>Ipostasi:</div>", unsafe_allow_html=True)
            selettore_macchie = st.selectbox(
                "Macchie ipostatiche:",
                options=list(opzioni_macchie.keys()),
                label_visibility="collapsed",
                key="macchie_ipostatiche_main"
            )
        with col2:
            st.markdown("<div style='font-size: 0.88rem;'>Rigidità cadaverica:</div>", unsafe_allow_html=True)
            selettore_rigidita = st.selectbox(
                "Rigidità cadaverica:",
                options=list(opzioni_rigidita.keys()),
                label_visibility="collapsed",
                key="rigidita_cadaverica_main"
            )

    # 🔹 Stile del riquadro applicato al container subito dopo l’ancora
    st.markdown("""
    <style>
    #box-tanatologia + div {
        border: 1.5px solid #e0e0e0;
        border-radius: 10px;
        padding: 12px 12px 6px;
        background: #fafafa;
        margin-top: 6px;
    }
    #box-tanatologia + div .box-title {
        font-weight: 600;
        font-size: 0.95rem;
        margin: 0 0 8px 2px;
        color: #444;
    }
    @media (max-width: 600px){
        #box-tanatologia + div { padding: 10px; }
        #box-tanatologia + div .box-title { font-size: 0.92rem; }
    }
    </style>
    """, unsafe_allow_html=True)

    # 📌 3. Temperature
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>T. rettale (°C):</div>", unsafe_allow_html=True)
        input_rt = st.number_input(
            "T. rettale (°C):",
            value=35.0, step=0.1, format="%.1f",
            label_visibility="collapsed",
            key="t_rettale_main"
        )
    with col2:
        st.markdown("<div style='font-size: 0.88rem;'>T. ambientale (°C):</div>", unsafe_allow_html=True)
        input_ta = st.number_input(
            "T. ambientale (°C):",
            value=20.0, step=0.1, format="%.1f",
            label_visibility="collapsed",
            key="t_ambientale_main"
        )
    with col3:
        st.markdown("<div style='font-size: 0.88rem;'>T. ante-mortem stimata (°C):</div>", unsafe_allow_html=True)
        input_tm = st.number_input(
            "T. ante-mortem stimata (°C):",
            value=37.2, step=0.1, format="%.1f",
            label_visibility="collapsed",
            key="t_antemortem_main"
        )

    # 📌 4. Peso + Fattore di correzione
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>Peso corporeo (kg):</div>", unsafe_allow_html=True)
        input_w = st.number_input(
            "Peso (kg):",
            value=70.0, step=1.0, format="%.1f",
            label_visibility="collapsed",
            key="peso_main"
        )
        st.session_state["peso"] = input_w
    with col2:
        subcol1, subcol2 = st.columns([2, 1], gap="small")
        with subcol1:
            st.markdown("<div style='font-size: 0.88rem;'>Fattore di correzione:</div>", unsafe_allow_html=True)
            fattore_correzione = st.number_input(
                "Fattore di correzione:",
                step=0.1, format="%.2f",
                label_visibility="collapsed",
                key="fattore_correzione"
            )
        with subcol2:
            if st.button("⚙️ Stima il fattore di correzione", key="btn_suggerisci_fattore"):
                st.session_state["mostra_modulo_fattore"] = not st.session_state.get("mostra_modulo_fattore", False)
# Pulsante centrale per generare/aggiornare la stima
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    pulsante_genera_stima = st.button("Stima epoca decesso", key="btn_genera_stima")

if pulsante_genera_stima:
    aggiorna_grafico()


def aggiorna_grafico():
    # --- Validazione Input Data/Ora Ispezione Legale ---
    if not input_data_rilievo or not input_ora_rilievo:
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Completare data e ora dell'ispezione legale.</p>", unsafe_allow_html=True)
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

        # Usa ora ispezione legale se non presente valore personalizzato
        if not ora_rilievo_param_str or ora_rilievo_param_str.strip() == "":
            ora_rilievo_param_obj = data_ora_ispezione
        else:
            try:
                ora_rilievo_param_obj = datetime.datetime.strptime(ora_rilievo_param_str, '%H:%M')
                minuti_param = ora_rilievo_param_obj.minute
                if minuti_param not in [0, 30]:
                    st.markdown(f"<p style='color:orange;font-weight:bold;'>⚠️ Avviso: L'ora di rilievo per '{nome_parametro}' ({ora_rilievo_param_str}) non è arrotondata alla mezzora. Questo parametro non sarà considerato nella stima.</p>", unsafe_allow_html=True)
                    continue
            except ValueError:
                st.markdown(f"<p style='color:orange;font-weight:bold;'>⚠️ Avviso: Formato ora di rilievo non valido per '{nome_parametro}' ({ora_rilievo_param_str}). Utilizzare il formato HH:MM (es. 14:30). Questo parametro non sarà considerato nella stima.</p>", unsafe_allow_html=True)
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

            # Calcolo data e ora param
            if isinstance(ora_rilievo_param_obj, datetime.datetime):
                ora_rilievo_time = ora_rilievo_param_obj.time()
            else:
                ora_rilievo_time = ora_rilievo_param_obj

            data_ora_param = datetime.datetime.combine(data_rilievo_param, ora_rilievo_time)
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

    # --- Stima minima post mortem secondo Potente et al. (calcolato prima di costruire i range) ---
    mt_ore = None
    mt_giorni = None
    usa_potente_per_intersezione = False

    if not any(np.isnan(val) for val in [Tr_val, Ta_val, CF_val, W_val]):
        if Tr_val <= Ta_val + 1e-6:
            mt_ore = None
            mt_giorni = None
        else:
            Qd_potente = (Tr_val - Ta_val) / (37.2 - Ta_val)
            soglia_qd = 0.2 if Ta_val <= 23 else 0.5
            if Qd_potente < soglia_qd:
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

        y_indices_mapping = {}
        current_y_index = 0

        parametri_grafico = []
        ranges_to_plot_inizio = []
        ranges_to_plot_fine = []

        if macchie_range_valido and macchie_range is not None:
            nome_breve_macchie = "Ipostasi"
            if macchie_range[1] < INF_HOURS:
                label_macchie = f"{nome_breve_macchie}\n({macchie_range[0]:.1f}–{macchie_range[1]:.1f} h)"
            else:
                label_macchie = f"{nome_breve_macchie}\n(≥ {macchie_range[0]:.1f} h)"
            parametri_grafico.append(label_macchie)
            ranges_to_plot_inizio.append(macchie_range[0])
            ranges_to_plot_fine.append(macchie_range[1] if macchie_range[1] < INF_HOURS else INF_HOURS)

        if rigidita_range_valido and rigidita_range is not None:
            nome_breve_rigidita = "Rigor"
            if rigidita_range[1] < INF_HOURS:
                label_rigidita = f"{nome_breve_rigidita}\n({rigidita_range[0]:.1f}–{rigidita_range[1]:.1f} h)"
            else:
                label_rigidita = f"{nome_breve_rigidita}\n(≥ {rigidita_range[0]:.1f} h)"
            parametri_grafico.append(label_rigidita)
            ranges_to_plot_inizio.append(rigidita_range[0])
            ranges_to_plot_fine.append(rigidita_range[1] if rigidita_range[1] < INF_HOURS else INF_HOURS)


        if raffreddamento_calcolabile:
            nome_breve_hensge = "Hensge"
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

            elif t_med_raff_hensge_rounded_raw > 30:
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

                y_indices_mapping[label_param_aggiuntivo] = current_y_index
                current_y_index += 1

        for i, (s, e) in enumerate(zip(ranges_to_plot_inizio, ranges_to_plot_fine)):
            if not np.isnan(s) and not np.isnan(e):
                ax.hlines(i, s, e, color='steelblue', linewidth=6)

        if visualizza_hensge_grafico:
            idx = parametri_grafico.index(label_hensge) if 'label_hensge' in locals() and label_hensge in parametri_grafico else None

            if idx is not None:
                if mt_ore is not None and not np.isnan(mt_ore):
                    ax.hlines(y=idx, xmin=mt_ore, xmax=INF_HOURS, color='orange', linewidth=6, alpha=0.6, zorder=1)
                if (not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and
                    t_med_raff_hensge_rounded_raw is not None and t_med_raff_hensge_rounded_raw > 30):
                    ax.hlines(y=idx, xmin=30.0, xmax=INF_HOURS, color='orange', linewidth=6, alpha=0.6, zorder=1)

        # Mapping asse Y statico per righe principali
        y_indices_mapping = {}
        current_y_index = 0
        if macchie_range_valido and macchie_range is not None:
            y_indices_mapping["Macchie ipostatiche"] = current_y_index
            current_y_index += 1
        if rigidita_range_valido and rigidita_range is not None:
            y_indices_mapping["Rigidità cadaverica"] = current_y_index
            current_y_index += 1
        if visualizza_hensge_grafico:
            y_indices_mapping["Raffreddamento cadaverico"] = current_y_index
            current_y_index += 1

        if macchie_range_valido and macchie_medi_range is not None:
            if "Macchie ipostatiche" in y_indices_mapping:
                ax.hlines(y_indices_mapping["Macchie ipostatiche"], macchie_medi_range[0], macchie_medi_range[1], color='orange', linewidth=6, alpha=0.6)

        if rigidita_range_valido and rigidita_medi_range is not None:
            if "Rigidità cadaverica" in y_indices_mapping:
                ax.hlines(y_indices_mapping["Rigidità cadaverica"], rigidita_medi_range[0], rigidita_medi_range[1], color='orange', linewidth=6, alpha=0.6)

        if visualizza_hensge_grafico:
            if "Raffreddamento cadaverico" in y_indices_mapping:
                y_pos_raffreddamento = y_indices_mapping["Raffreddamento cadaverico"]
                punto_medio_raffreddamento = (t_min_raff_visualizzato + t_max_raff_visualizzato) / 2
                offset = 0.1
                ax.hlines(y_pos_raffreddamento, punto_medio_raffreddamento - offset, punto_medio_raffreddamento + offset, color='orange', linewidth=6, alpha=0.8)

        ax.set_yticks(range(len(parametri_grafico)))
        ax.set_yticklabels(parametri_grafico, fontsize=9)
        ax.set_xlabel("Ore dal decesso")

        max_x_value = 10
        all_limits = ranges_to_plot_fine + ranges_to_plot_inizio
        valid_limits = [lim for lim in all_limits if not np.isnan(lim) and lim < INF_HOURS]
        if valid_limits:
            max_x_value = max(max_x_value, max(valid_limits) * 1.1)
            max_x_value = max(max_x_value, 10)

        ax.set_xlim(0, max_x_value)
        ax.grid(True, axis='x', linestyle=':', alpha=0.6)

        if overlap and comune_inizio < max_x_value and (np.isnan(comune_fine) or comune_fine > 0):
            ax.axvline(max(0, comune_inizio), color='red', linestyle='--')
            if not np.isnan(comune_fine):
                ax.axvline(min(max_x_value, comune_fine), color='red', linestyle='--')

        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.markdown((
            "<p style='color:orange;font-weight:bold;'>⚠️ Nessun parametro tanatologico con un range valido da visualizzare nel grafico.</p>"
        ), unsafe_allow_html=True)

    # --- Visualizza note/avvisi e testo descrittivo Henssge (fix variabili non definite) ---

    if nota_globale_range_adattato:
        st.markdown((
            "<p style='color:gray;font-size:small;'>"
            "* alcuni parametri sono stati valutati a orari diversi, ma il range indicato sul grafico e nelle eventuali stime è stato adattato di conseguenza, rendendo confrontabili tra loro gli intervalli."
            "</p>"
        ), unsafe_allow_html=True)

    if minuti_isp not in [0, 15, 30, 45]:
        st.markdown(
            "<p style='color:darkorange;font-size:small;'>NB: Considerati i limiti intrinseci dei metodi utilizzati, l’orario dei rilievi tanatologici è stato automaticamente arrotondato al quarto d’ora più vicino.</p>",
            unsafe_allow_html=True
        )

    hensge_input_forniti = (
        input_rt is not None and
        input_ta is not None and
        input_tm is not None and
        input_w is not None and
        st.session_state.get("fattore_correzione", None) is not None
    )

    if hensge_input_forniti:

        if Ta_val > 25:
            st.markdown((
                "<p style='color:darkorange;font-size:small;'>"
                "Per la temperatura selezionata (&gt; 25 °C), la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati. Scegliere il fattore con cura."
                "</p>"
            ), unsafe_allow_html=True)

        if Ta_val < 18:
            st.markdown((
                "<p style='color:darkorange;font-size:small;'>"
                "Per la temperatura selezionata (&lt; 18 °C), la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati. Scegliere il fattore con cura."
                "</p>"
            ), unsafe_allow_html=True)

        if temp_difference_small:
            st.markdown((
                "<p style='color:darkorange;font-size:small;'>"
                "Essendo minima la differenza tra temperatura rettale e ambientale, "
                "è possibile che il cadavere fosse ormai in equilibrio termico con l'ambiente. "
                "La stima ottenuta dal raffreddamento cadaverico va interpretata con attenzione."
                "</p>"
            ), unsafe_allow_html=True)

        if not raffreddamento_calcolabile:
            st.markdown((
                "<p style='color:orange;font-size:normal;'>⚠️ Non è stato possibile ricavare stime applicando il metodo di Henssge con i valori inseriti "
                "(possibile causa: temperature incoerenti o valori fuori range per il nomogramma).</p>"
            ), unsafe_allow_html=True)
        else:
            # Calcolo e stampa del testo riassuntivo solo se i limiti sono definiti (fix variabili non definite)
            if visualizza_hensge_grafico:
                limite_inferiore_testo = t_min_raff_visualizzato
                limite_superiore_testo = t_max_raff_visualizzato
            else:
                limite_inferiore_testo = t_min_raff_hensge
                limite_superiore_testo = t_max_raff_hensge

            if (not np.isnan(limite_inferiore_testo)) and (not np.isnan(limite_superiore_testo)):
                min_raff_hours = int(limite_inferiore_testo)
                min_raff_minutes = int(round((limite_inferiore_testo % 1) * 60))
                max_raff_hours = int(limite_superiore_testo)
                max_raff_minutes = int(round((limite_superiore_testo % 1) * 60))

                min_raff_hour_text = "ora" if min_raff_hours == 1 and min_raff_minutes == 0 else "ore"
                max_raff_hour_text = "ora" if max_raff_hours == 1 and max_raff_minutes == 0 else "ore"

                # Testo base sempre incluso (solo qui, quando abbiamo i valori)
                testo_raff_base = (
                    f"Applicando il nomogramma di Henssge, è possibile stimare che il decesso sia avvenuto tra circa "
                    f"{min_raff_hours} {min_raff_hour_text}{'' if min_raff_minutes == 0 else f' {min_raff_minutes} minuti'} e "
                    f"{max_raff_hours} {max_raff_hour_text}{'' if max_raff_minutes == 0 else f' {max_raff_minutes} minuti'} "
                    f"prima dei rilievi effettuati al momento dell’ispezione legale."
                )

                # Avvio struttura HTML
                testo_raff_completo = f"<ul><li>{testo_raff_base}"

                # Lista dinamica
                elenco_extra = []

                # Qd troppo basso
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

                # Qd alto e durata > 30 ore
                if not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and t_med_raff_hensge_rounded_raw > 30:
                    elenco_extra.append(
                        f"<li>"
                        f"<span style='color:orange; font-weight:bold;'>"
                        f"La stima media ottenuta dal raffreddamento cadaverico ({t_med_raff_hensge_rounded:.1f} h) è superiore alle 30 ore. "
                        f"L'affidabilità del metodo di Henssge diminuisce significativamente oltre questo intervallo."
                        f"</span>"
                        f"</li>"
                    )

                # Metodo Potente et al.
                soglia_qd = 0.2 if Ta_val <= 23 else 0.5
                condizione_temp = "T. amb ≤ 23 °C" if Ta_val <= 23 else "T. amb > 23 °C"
                if mt_ore is not None and not np.isnan(mt_ore) and Qd_val_check is not None and Qd_val_check < soglia_qd:
                    elenco_extra.append(
                        f"<li>"
                        f"Lo studio di Potente et al. permette di stimare grossolanamente l’intervallo minimo post-mortem quando i dati non consentono di ottenere risultati attendibili con il metodo di Henssge "
                        f"(Qd &lt; {soglia_qd} e {condizione_temp}). "
                        f"Applicandolo al caso specifico, si può ipotizzare che, al momento dell’ispezione legale, fossero trascorse almeno <b>{mt_ore:.0f}</b> ore (≈ {mt_giorni:.1f} giorni) dal decesso."
                        f"<ul><li><span style='font-size:smaller;'>"
                        f"Potente S, Kettner M, Verhoff MA, Ishikawa T. Minimum time since death when the body has either reached or closely approximated equilibrium with ambient temperature. "
                        f"<i>Forensic Sci Int.</i> 2017;281:63–66. doi: 10.1016/j.forsciint.2017.09.012."
                        f"</span></li></ul>"
                        f"</li>"
                    )

                # Se ci sono elementi extra, aggiungili
                if elenco_extra:
                    testo_raff_completo += "<ul>" + "".join(elenco_extra) + "</ul>"

                # Chiudi blocco principale
                testo_raff_completo += "</li></ul>"

                # Visualizza
                st.markdown(testo_raff_completo, unsafe_allow_html=True)

    # --- Visualizza i testi descrittivi per macchie ipostatiche e rigidità cadaverica ---
    st.markdown((f"<ul><li>{testi_macchie[macchie_selezionata]}</li></ul>"), unsafe_allow_html=True)
    st.markdown((f"<ul><li>{rigidita_descrizioni[rigidita_selezionata]}</li></ul>"), unsafe_allow_html=True)
    for param in parametri_aggiuntivi_da_considerare:
       if param["stato"] != "Non valutata" and param["stato"] != "Non valutabile/non attendibile":
           st.markdown(f"<ul><li>{param['descrizione']}</li></ul>", unsafe_allow_html=True)

    # --- Visualizza Stima Complessiva e Messaggi di Incoerenza ---

    # Conta quanti range *potenzialmente* sono stati usati per l'intersezione (quelli con limite superiore < INF_HOURS)
    num_potential_ranges_used = int(macchie_range_valido and macchie_range is not None and macchie_range[1] < INF_HOURS) + \
                                int(rigidita_range_valido and rigidita_range is not None and rigidita_range[1] < INF_HOURS) + \
                                int(raffreddamento_calcolabile and not temp_difference_small and t_med_raff_hensge_rounded <= 30) + \
                                sum(1 for param in parametri_aggiuntivi_da_considerare if not np.isnan(param["range_traslato"][0]) and not np.isnan(param["range_traslato"][1]) and param["range_traslato"][1] < INF_HOURS)

    # Se invece overlap è True, stampiamo SEMPRE la frase di stima complessiva (anche con range aperti sopra)
    if overlap:
        try:
            isp = data_ora_ispezione
        except Exception:
            return

        limite_superiore_infinito = np.isnan(comune_fine) or comune_fine == INF_HOURS

        if (not np.isnan(Qd_val_check) and Qd_val_check < 0.3
            and comune_inizio > 30
            and (np.isnan(comune_fine) or comune_fine == INF_HOURS)):

            comune_inizio_hours = int(comune_inizio)
            comune_inizio_minutes = int(round((comune_inizio % 1) * 60))
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
            # Arrotonda Potente se usato come limite minimo
            if mt_ore is not None and not np.isnan(mt_ore):
                if abs(comune_inizio - mt_ore) < 0.25:
                    comune_inizio = round(mt_ore)

            comune_inizio_hours = int(comune_inizio)
            comune_inizio_minutes = int(round((comune_inizio % 1) * 60))
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 and comune_inizio_minutes == 0 else "ore"
            da = isp - datetime.timedelta(hours=comune_inizio)
            testo = (
                f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
            )

        elif comune_inizio == 0:
            comune_fine_hours = int(comune_fine)
            comune_fine_minutes = int(round((comune_fine % 1) * 60))
            fine_hour_text = "ora" if comune_fine_hours == 1 else "ore"
            da = isp - datetime.timedelta(hours=comune_fine)
            testo = (
                f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                f"consente di stimare che la morte sia avvenuta <b>non oltre</b> "
                f"{comune_fine_hours} {fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero successivamente alle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
            )

        else:
            comune_inizio_hours = int(comune_inizio)
            comune_inizio_minutes = int(round((comune_inizio % 1) * 60))
            comune_fine_hours = int(comune_fine)
            comune_fine_minutes = int(round((comune_fine % 1) * 60))
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 else "ore"
            comune_fine_hour_text = "ora" if comune_fine_hours == 1 else "ore"
            da = isp - datetime.timedelta(hours=comune_fine)
            aa = isp - datetime.timedelta(hours=comune_inizio)

            if da.date() == aa.date():
                testo = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{comune_inizio_hours} {comune_inizio_hour_text}{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} e "
                    f"{comune_fine_hours} {comune_fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {da.strftime('%H:%M')} e le ore {aa.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
                )
            else:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{comune_inizio_hours} {comune_inizio_hour_text}{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} e "
                    f"{comune_fine_hours} {comune_fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')} e le ore {aa.strftime('%H:%M')} del {aa.strftime('%d.%m.%Y')}."
                )

        st.markdown(f"<b>{testo}</b>", unsafe_allow_html=True)

    # --- Frase aggiuntiva SENZA considerare lo studio di Potente (in grigio) ---
    if any("potente" in nome.lower() for nome in nomi_parametri_usati_per_intersezione):
        range_inizio_senza_potente = []
        range_fine_senza_potente = []

        if macchie_range_valido and macchie_range is not None:
            range_inizio_senza_potente.append(macchie_range[0])
            range_fine_senza_potente.append(macchie_range[1])

        if rigidita_range_valido and rigidita_range is not None:
            range_inizio_senza_potente.append(rigidita_range[0])
            range_fine_senza_potente.append(rigidita_range[1])

        for p in parametri_aggiuntivi_da_considerare:
            if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1]):
                range_inizio_senza_potente.append(p["range_traslato"][0])
                range_fine_senza_potente.append(p["range_traslato"][1])

        if raffreddamento_calcolabile:
            range_inizio_senza_potente.append(t_min_raff_hensge)
            range_fine_senza_potente.append(t_max_raff_hensge)

        if len(range_inizio_senza_potente) >= 2:
            inizio_senza_potente = max(range_inizio_senza_potente)
            fine_senza_potente = min(range_fine_senza_potente)
            if inizio_senza_potente <= fine_senza_potente:
                inizio_h = int(inizio_senza_potente)
                inizio_m = int(round((inizio_senza_potente % 1) * 60))
                fine_h = int(fine_senza_potente)
                fine_m = int(round((fine_senza_potente % 1) * 60))

                inizio_text = "ora" if inizio_h == 1 and inizio_m == 0 else "ore"
                fine_text = "ora" if fine_h == 1 and fine_m == 0 else "ore"

                dt_inizio = data_ora_ispezione - datetime.timedelta(hours=fine_senza_potente)
                dt_fine = data_ora_ispezione - datetime.timedelta(hours=inizio_senza_potente)

                frase_secondaria = (
                    f"<b>Senza considerare lo studio di Potente</b>, la valutazione complessiva dei dati tanatologici, "
                    f"integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                    f"consente di stimare che la morte  sia avvenuta tra circa "
                    f"{inizio_h} {inizio_text}{'' if inizio_m == 0 else f' {inizio_m} minuti'} e "
                    f"{fine_h} {fine_text}{'' if fine_m == 0 else f' {fine_m} minuti'} "
                    f"prima dei rilievi effettuati al momento dell’ispezione legale, "
                    f"ovvero tra le ore {dt_inizio.strftime('%H:%M')} del {dt_inizio.strftime('%d.%m.%Y')} "
                    f"e le ore {dt_fine.strftime('%H:%M')} del {dt_fine.strftime('%d.%m.%Y')}."
                )

                st.markdown(
                    f"<div style='border:1px solid #ccc; padding:10px; color:gray; font-size:small;'>{frase_secondaria}</div>",
                    unsafe_allow_html=True
                )

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



