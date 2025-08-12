# -*- coding: utf-8 -*-
# Streamlit app: Stima epoca decesso
# Revisione: UI compatta (form, time_input, selectbox), expander parametri, CSS, descrizioni su richiesta.
# Il testo complessivo resta fuori dall’expander come richiesto.

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import root_scalar
import datetime
import pandas as pd

# =========================
# Stato e costanti globali
# =========================

if "fattore_correzione" not in st.session_state:
    st.session_state["fattore_correzione"] = 1.0

if "mostra_modulo_fattore" not in st.session_state:
    st.session_state["mostra_modulo_fattore"] = False

INF_HOURS = 200  # range aperti

# =========================
# Utility cache per Excel
# =========================

@st.cache_data
def load_tabelle_correzione():
    """Carica e normalizza le tabelle usate da calcola_fattore."""
    try:
        t1 = pd.read_excel("tabella rielaborata.xlsx", engine="openpyxl")
        t2 = pd.read_excel("tabella secondaria.xlsx", engine="openpyxl")
    except FileNotFoundError:
        raise
    except ImportError as e:
        raise RuntimeError("Il pacchetto 'openpyxl' è richiesto per leggere i file Excel.") from e

    t1['Fattore'] = pd.to_numeric(t1['Fattore'], errors='coerce')
    for col in ["Ambiente", "Vestiti", "Coperte", "Superficie d'appoggio", "Correnti"]:
        t1[col] = t1[col].astype(str).str.strip()
    return t1, t2

# =========================
# Calcolo fattore (UI compattata)
# =========================

def calcola_fattore(peso):
    try:
        tabella1, tabella2 = load_tabelle_correzione()
    except FileNotFoundError:
        st.error("Impossibile caricare i file Excel per il calcolo del fattore di correzione. "
                 "Verifica che 'tabella rielaborata.xlsx' e 'tabella secondaria.xlsx' siano presenti.")
        return
    except Exception as e:
        st.error(f"Errore nel caricamento delle tabelle: {e}")
        return

    st.markdown("""<style>
    .fattore-correzione-section .stRadio, 
    .fattore-correzione-section .stSelectbox { margin-bottom: 0.25rem; }
    </style>""", unsafe_allow_html=True)
    st.markdown('<div class="fattore-correzione-section">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # --- COLONNA 1: CONDIZIONE CORPO ---
    with col1:
        st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Condizioni del corpo</p>", unsafe_allow_html=True)
        stato_corpo = st.radio("", ["Asciutto", "Bagnato", "Immerso"], label_visibility="collapsed", key="radio_stato_corpo")
        corpo_immerso = (stato_corpo == "Immerso")
        corpo_bagnato = (stato_corpo == "Bagnato")
        corpo_asciutto = (stato_corpo == "Asciutto")

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
            if st.session_state.get("radio_vestiti") == "Moltissimi strati":
                opzioni_coperte = ["Molte coperte pesanti"]

            scelta_coperte = st.selectbox("", opzioni_coperte, index=0, label_visibility="collapsed", key="scelta_coperte_radio")
        else:
            scelta_coperte = "/"

    copertura_speciale = scelta_coperte in ["Strato di foglie di medio spessore", "Spesso strato di foglie"]

    # --- COLONNA 1: ABBIGLIAMENTO ---
    if (corpo_asciutto or corpo_bagnato) and not corpo_immerso and not copertura_speciale:
        with col1:
            st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Abbigliamento</p>", unsafe_allow_html=True)
            scelta_vestiti = st.selectbox(
                "", [
                    "Nudo",
                    "1-2 strati sottili",
                    "2-3 strati sottili",
                    "3-4 strati sottili",
                    "1-2 strati spessi",
                    "˃4 strati sottili o ˃2 spessi",
                    "Moltissimi strati"
                ],
                index=0, label_visibility="collapsed", key="radio_vestiti"
            )
    else:
        scelta_vestiti = "/"

    # --- COLONNA 2: CORRENTI ---
    with col2:
        if not copertura_speciale:
            mostra_corrente = False
            if corpo_bagnato:
                mostra_corrente = True
            elif corpo_asciutto and scelta_vestiti in ["Nudo", "1-2 strati sottili"] and scelta_coperte == "Nessuna coperta":
                mostra_corrente = True

            if scelta_vestiti == "Moltissimi strati":
                mostra_corrente = False

            if mostra_corrente:
                st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Presenza di correnti</p>", unsafe_allow_html=True)
                corrente = st.selectbox("", ["Esposto a corrente d'aria", "Nessuna corrente"], index=1, label_visibility="collapsed", key="radio_corrente")
            elif corpo_immerso:
                st.markdown("<p style='font-weight:bold; margin-bottom:4px;'>Presenza di correnti</p>", unsafe_allow_html=True)
                corrente = st.selectbox("", ["In acqua corrente", "In acqua stagnante"], index=1, label_visibility="collapsed", key="radio_acqua")
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
            if mostra_foglie:
                opzioni_superficie += ["Superficie metallica spessa, all'esterno.", "Foglie umide (≥2 cm)", "Foglie secche (≥2 cm)"]
            superficie = st.selectbox("", opzioni_superficie, label_visibility="collapsed", key="radio_superficie")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- CALCOLO TABELLA ---
    valori = {
        "Ambiente": stato_corpo,
        "Vestiti": scelta_vestiti,
        "Coperte": scelta_coperte,
        "Superficie d'appoggio": superficie,
        "Correnti": corrente
    }
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
        st.info("Più combinazioni valide trovate: verrà usata la prima.")

    try:
        fattore_base = float(riga["Fattore"].values[0])
    except Exception:
        st.warning("Il valore di 'Fattore' in tabella non è numerico.")
        return

    fattore_finale = fattore_base
    if fattore_base >= 1.4 and peso != 70:
        try:
            t2 = tabella2.copy()

            def parse_peso(col):
                s = str(col).strip().lower().replace('kg', '').replace('w', '')
                num = ''.join(ch for ch in s if (ch.isdigit() or ch in '.,')).replace(',', '.')
                return float(num) if num not in ("", ".", ",") else None

            pesi_col = {col: parse_peso(col) for col in t2.columns}
            pesi_col = {col: w for col, w in pesi_col.items() if w is not None}
            if not pesi_col:
                raise ValueError("Nessuna colonna peso valida in Tabella 2.")

            col_70 = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - 70.0))
            serie70 = pd.to_numeric(t2[col_70], errors='coerce')
            idx_match = (serie70 - fattore_base).abs().idxmin()
            col_user = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - float(peso)))
            val_user = pd.to_numeric(t2.loc[idx_match, col_user], errors='coerce')
            if pd.notna(val_user):
                fattore_finale = float(val_user)
        except Exception as e:
            st.warning(f"Impossibile adattare per il peso (uso Tabella 1): {e}")

    if abs(fattore_finale - fattore_base) > 1e-9:
        st.success(f"Fattore di correzione (adattato per peso): {fattore_finale:.2f}")
        st.caption(f"Tabella 1: {fattore_base:.2f} – peso: {peso:.1f} kg")
    else:
        st.success(f"Fattore di correzione calcolato: {fattore_finale:.2f}")

    def _apply_fattore(val):
        st.session_state["fattore_correzione"] = round(float(val), 2)
        st.session_state["mostra_modulo_fattore"] = False

    st.button("✅ Usa questo fattore", key="usa_fattore_btn", on_click=_apply_fattore, args=(fattore_finale,))

# =========================
# Dati fenomeni tanatologici
# =========================

st.set_page_config(page_title="Stima Epoca della Morte", layout="centered")
st.markdown("<h5 style='margin-top:0; margin-bottom:10px;'>Stima epoca decesso</h5>", unsafe_allow_html=True)

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
    "Non ancora comparse": "È da ritenersi che le macchie ipostatiche ... entro 3 ore ...",
    "Migrabilità totale": "È da ritenersi che ... meno di 6 ore ...",
    "Migrabilità parziale": "È da ritenersi che ... tra 4 e 24 ore ...",
    "Migrabilità perlomeno parziale": "È da ritenersi che ... meno di 24 ore ...",
    "Fissità assoluta": "È da ritenersi che ... più di 10 ore ...",
    "Non valutabili/Non attendibili": "Le macchie ipostatiche non sono state valutate ..."
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
    "Non ancora comparsa": "È possibile valutare che la rigidità ... meno di 7 ore ...",
    "In via di formazione, intensificazione e generalizzazione": "È possibile valutare che ... 0.5–20 ore ...",
    "Presente e generalizzata": "È possibile valutare che ... 2–96 ore ...",
    "In via di risoluzione": "È possibile valutare che ... 24–192 ore ...",
    "Ormai risolta": "È possibile valutare che ... ≥ 24 ore ...",
    "Non valutabile/Non attendibile": "La rigidità cadaverica non è stata valutata ..."
}

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
            "Fase VI": "L’applicazione ... 1–6 ore ...",
            "Fase V": "L’applicazione ... 2–7 ore ...",
            "Fase IV": "L’applicazione ... 3–8 ore ...",
            "Fase III": "L’applicazione ... 3h30–13h ...",
            "Fase II": "L’applicazione ... 5–16 ore ...",
            "Fase I": "L’applicazione ... 5–22 ore ...",
            "Non valutabile/non attendibile": "Non è stato possibile valutare ...",
            "Nessuna reazione": "L’applicazione ... > 5 ore ..."
        }
    },
    "Eccitabilità elettrica peribuccale": {
        "opzioni": ["Non valutata", "Marcata ed estesa (+++)", "Discreta (++)", "Accennata (+)", "Nessuna reazione", "Non valutabile/non attendibile"],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (6, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Marcata ed estesa (+++)": (0, 2.5),
            "Discreta (++)": (1, 5),
            "Accennata (+)": (2, 6)
        },
        "descrizioni": {
            "Marcata ed estesa (+++)": "L’applicazione ... < 2h30 ...",
            "Discreta (++)": "L’applicazione ... 1–5 ore ...",
            "Accennata (+)": "L’applicazione ... 2–6 ore ...",
            "Non valutata/non attendibile": "Non è stato possibile valutare ...",
            "Nessuna reazione": "L’applicazione ... > 6 ore ..."
        }
    },
    "Eccitabilità muscolare meccanica": {
        "opzioni": ["Non valutata", "Contrazione reversibile dell’intero muscolo", "Formazione di una tumefazione reversibile", "Formazione di una piccola tumefazione persistente", "Nessuna reazione", "Non valutabile/non attendibile"],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (1.5, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Formazione di una piccola tumefazione persistente": (0, 12),
            "Formazione di una tumefazione reversibile": (2, 5),
            "Contrazione reversibile dell’intero muscolo": (0, 2)
        },
        "descrizioni": {
            "Formazione di una piccola tumefazione persistente": "L’eccitabilità ... < 12 ore ...",
            "Formazione di una tumefazione reversibile": "L’eccitabilità ... 2–5 ore ...",
            "Contrazione reversibile dell’intero muscolo": "L’eccitabilità ... < 2 ore ...",
            "Non valutabile/non attendibile": "Non è stato possibile valutare ...",
            "Nessuna reazione": "L’applicazione ... > 1h30 ..."
        }
    },
    "Eccitabilità chimica pupillare": {
        "opzioni": ["Non valutata", "Non valutabile/non attendibile", "Positiva", "Negativa"],
        "range": {
            "Non valutata": None,
            "Non valutabile/non attendibile": None,
            "Positiva": (0, 30),
            "Negativa": (5, INF_HOURS)
        },
        "descrizioni": {
            "Positiva": "L’eccitabilità ... < 30 ore ...",
            "Negativa": "L’eccitabilità ... > 5 ore ...",
            "Non valutabile/non attendibile": "L'eccitabilità ... non valutabile ..."
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

# =========================
# Utilità calcolo raffreddamento
# =========================

def round_quarter_hour(x):
    if np.isnan(x):
        return np.nan
    return np.round(x * 2) / 2

def calcola_raffreddamento(Tr, Ta, T0, W, CF):
    if Tr is None or Ta is None or T0 is None or W is None or CF is None:
        return np.nan, np.nan, np.nan, np.nan, np.nan
    temp_tolerance = 1e-6
    if Tr <= Ta + temp_tolerance:
        return np.nan, np.nan, np.nan, np.nan, np.nan
    if abs(T0 - Ta) < temp_tolerance:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    Qd = (Tr - Ta) / (T0 - Ta)
    if np.isnan(Qd) or Qd <= 0 or Qd > 1:
        return np.nan, np.nan, np.nan, np.nan, np.nan

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
        except Exception:
            return np.nan

    t_med_raw = np.nan
    try:
        sol = root_scalar(lambda t: Qp(t) - Qd, bracket=[0, 160], method='bisect')
        t_med_raw = sol.root
    except Exception:
        t_med_raw = np.nan

    Dt_raw = 0
    if not np.isnan(t_med_raw) and not np.isnan(Qd):
        if Qd <= 0.2:
            Dt_raw = t_med_raw * 0.20
        elif CF == 1:
            Dt_raw = 2.8 if Qd > 0.5 else 3.2 if Qd > 0.3 else 4.5
        else:
            Dt_raw = 2.8 if Qd > 0.5 else 4.5 if Qd > 0.3 else 7

    t_med = round_quarter_hour(t_med_raw) if not np.isnan(t_med_raw) else np.nan
    t_min = round_quarter_hour(t_med_raw - Dt_raw) if not np.isnan(t_med_raw) else np.nan
    t_max = round_quarter_hour(t_med_raw + Dt_raw) if not np.isnan(t_med_raw) else np.nan
    t_min = max(0.0, t_min) if not np.isnan(t_min) else np.nan
    return t_med, t_min, t_max, t_med_raw, Qd

def arrotonda_quarto_dora(dt: datetime.datetime) -> datetime.datetime:
    minuti = (dt.minute + 7) // 15 * 15
    if minuti == 60:
        dt += datetime.timedelta(hours=1)
        minuti = 0
    return dt.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=minuti)

def _split_hours_minutes(h: float):
    if h is None or (isinstance(h, float) and np.isnan(h)):
        return None
    total_minutes = int(round(h * 60))
    hours, minutes = divmod(total_minutes, 60)
    return hours, minutes

def ranges_in_disaccordo_completa(r_inizio, r_fine):
    intervalli = []
    for start, end in zip(r_inizio, r_fine):
        s = start if not np.isnan(start) else -np.inf
        e = end if not np.isnan(end) else np.inf
        intervalli.append((s, e))
    for i, (s1, e1) in enumerate(intervalli):
        if not any(i == j or not (s1 > e2 or s2 > e1) for j, (s2, e2) in enumerate(intervalli)):
            return True
    return False

# =========================
# CSS compatto
# =========================
st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-bottom: 1rem; }
div[data-testid="stVerticalBlock"] { gap: 0.4rem; }
label, .stSelectbox label, .stRadio label { font-size: 0.92rem; margin-bottom: 0.25rem; }
.stSelectbox div[data-baseweb="select"] { min-height: 36px; }
div.stButton > button {
    border: 2px solid #2196F3 !important;
    color: black !important;
    background-color: white !important;
    font-weight: bold;
    border-radius: 8px !important;
    padding: 0.5rem 1.4rem !important;
}
div.stButton > button:hover { background-color: #E3F2FD !important; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

# =========================
# FORM COMPATTO
# =========================
with st.form("stima_form", clear_on_submit=False):
    # 1) Data / Ora
    st.markdown("<div style='font-size: 0.88rem;'>Data e ora dei rilievi tanatologici:</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="small")
    with col1:
        input_data_rilievo = st.date_input("Data ispezione legale:", value=datetime.date.today(), label_visibility="collapsed")
    with col2:
        input_ora_rilievo = st.time_input("Ora ispezione legale:", value=datetime.time(0, 0), step=datetime.timedelta(minutes=15), label_visibility="collapsed")

    # 2) Ipostasi / Rigidità
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>Ipostasi:</div>", unsafe_allow_html=True)
        selettore_macchie = st.selectbox("Macchie ipostatiche:", list(opzioni_macchie.keys()), label_visibility="collapsed")
    with col2:
        st.markdown("<div style='font-size: 0.88rem;'>Rigidità cadaverica:</div>", unsafe_allow_html=True)
        selettore_rigidita = st.selectbox("Rigidità cadaverica:", list(opzioni_rigidita.keys()), label_visibility="collapsed")

    # 3) Temperature
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

    # 4) Peso + FC
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>Peso corporeo (kg):</div>", unsafe_allow_html=True)
        input_w = st.number_input("Peso (kg):", value=70.0, step=1.0, format="%.1f", label_visibility="collapsed")
        st.session_state["peso"] = input_w
    with col2:
        st.markdown("<div style='font-size: 0.88rem;'>Fattore di correzione (FC):</div>", unsafe_allow_html=True)
        st.number_input("Fattore di correzione:", step=0.1, format="%.2f", label_visibility="collapsed", key="fattore_correzione")

    # 5) Modulo fattore (expander)
    if not st.session_state["mostra_modulo_fattore"]:
        st.button("Stima fattore di correzione", key="open_fattore_btn", on_click=lambda: st.session_state.update(mostra_modulo_fattore=True))
    else:
        with st.expander("Stima fattore di correzione", expanded=True):
            st.markdown('<div style="background-color:#f0f0f5; padding:10px; border-radius:5px;">', unsafe_allow_html=True)
            calcola_fattore(peso=st.session_state.get("peso", 70))
            st.markdown('</div>', unsafe_allow_html=True)

    # 6) Parametri aggiuntivi (expander per ciascuno)
    mostra_parametri_aggiuntivi = st.checkbox("Inserisci dati tanatologici aggiuntivi")
    widgets_parametri_aggiuntivi = {}
    if mostra_parametri_aggiuntivi:
        for nome_parametro, dati_parametro in dati_parametri_aggiuntivi.items():
            with st.expander(nome_parametro, expanded=False):
                col1p, col2p = st.columns([1, 2], gap="small")
                with col1p:
                    st.markdown(f"<div style='font-size: 0.88rem; padding-top: 0.4rem;'>{nome_parametro}:</div>", unsafe_allow_html=True)
                with col2p:
                    selettore = st.selectbox(label=nome_parametro, options=dati_parametro["opzioni"], key=f"{nome_parametro}_selector", label_visibility="collapsed")

                data_picker = None
                ora_input = None
                usa_orario_personalizzato = False

                if selettore != "Non valutata":
                    col1c, col2c = st.columns([0.7, 0.3], gap="small")
                    with col1c:
                        st.markdown("<div style='font-size: 0.8em; color: orange; margin-bottom: 3px;'>Il dato è stato valutato a un'orario diverso?</div>", unsafe_allow_html=True)
                    with col2c:
                        usa_orario_personalizzato = st.checkbox(label="", key=f"{nome_parametro}_diversa")

                if usa_orario_personalizzato:
                    col1d, col2d = st.columns(2)
                    with col1d:
                        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Data rilievo:</div>", unsafe_allow_html=True)
                        data_picker = st.date_input("Data rilievo:", value=input_data_rilievo, key=f"{nome_parametro}_data", label_visibility="collapsed")
                    with col2d:
                        st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Ora rilievo:</div>", unsafe_allow_html=True)
                        ora_input = st.time_input("Ora rilievo (HH:MM):", value=input_ora_rilievo, key=f"{nome_parametro}_ora", step=datetime.timedelta(minutes=30), label_visibility="collapsed")

                if nome_parametro == "Eccitabilità elettrica sopraciliare":
                    st.image("https://raw.githubusercontent.com/scopusjin/codice/main/immagini/eccitabilit%C3%A0.PNG", width=320)
                if nome_parametro == "Eccitabilità elettrica peribuccale":
                    st.image("https://raw.githubusercontent.com/scopusjin/codice/main/immagini/peribuccale.PNG", width=300)

                widgets_parametri_aggiuntivi[nome_parametro] = {
                    "selettore": selettore,
                    "data_rilievo": data_picker,
                    "ora_rilievo": ora_input
                }

    submitted = st.form_submit_button("STIMA EPOCA DECESSO")

# =========
# LOGICA post-submit
# =========

def aggiorna_grafico():
    # Validazione Data/Ora
    if not input_data_rilievo or not input_ora_rilievo:
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Inserisci data e ora dell'ispezione legale.</p>", unsafe_allow_html=True)
        return

    minuti_isp = input_ora_rilievo.minute
    data_ora_ispezione_originale = datetime.datetime.combine(input_data_rilievo, input_ora_rilievo)
    data_ora_ispezione = arrotonda_quarto_dora(data_ora_ispezione_originale)

    # Valori per Henssge
    Tr_val = input_rt
    Ta_val = input_ta
    T0_val = input_tm
    W_val = input_w
    CF_val = st.session_state.get("fattore_correzione", 1.0)

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

    t_med_h, t_min_h, t_max_h, t_med_raw, Qd_val = calcola_raffreddamento(Tr_val, Ta_val, T0_val, W_val, CF_val)
    qd_threshold = 0.2 if Ta_val <= 23 else 0.5
    raffreddamento_calcolabile = not np.isnan(t_med_h) and t_med_h >= 0

    temp_difference_small = (Tr_val is not None and Ta_val is not None and (Tr_val - Ta_val) is not None and (Tr_val - Ta_val) < 2.0 and (Tr_val - Ta_val) >= 0)

    macchie_range_valido = macchie_selezionata != "Non valutabili/Non attendibili"
    macchie_range = opzioni_macchie.get(macchie_selezionata) if macchie_range_valido else (np.nan, np.nan)
    macchie_medi_range = macchie_medi.get(macchie_selezionata) if macchie_range_valido else None

    rigidita_range_valido = rigidita_selezionata != "Non valutabile/Non attendibile"
    rigidita_range = opzioni_rigidita.get(rigidita_selezionata) if rigidita_range_valido else (np.nan, np.nan)
    rigidita_medi_range = rigidita_medi.get(rigidita_selezionata) if rigidita_range_valido else None

    # Parametri aggiuntivi raccolti nel form
    parametri_aggiuntivi_da_considerare = []
    nota_globale_range_adattato = False

    if 'widgets_parametri_aggiuntivi' in locals():
        for nome_parametro, widgets_param in widgets_parametri_aggiuntivi.items():
            stato_selezionato = widgets_param["selettore"]
            data_rilievo_param = widgets_param["data_rilievo"]
            ora_rilievo_param_time = widgets_param["ora_rilievo"]

            if stato_selezionato == "Non valutata":
                continue

            chiave_descrizione = stato_selezionato.split(':')[0].strip() if nome_parametro == "Eccitabilità elettrica peribuccale" else stato_selezionato.strip()

            if ora_rilievo_param_time is None:
                ora_rilievo_time = data_ora_ispezione.time()
            else:
                ora_rilievo_time = ora_rilievo_param_time
                if ora_rilievo_time.minute not in (0, 30):
                    st.markdown(f"<p style='color:orange;font-weight:bold;'>⚠️ Orario '{nome_parametro}' non arrotondato (:00/:30). Parametro escluso.</p>", unsafe_allow_html=True)
                    continue

            if data_rilievo_param is None:
                data_rilievo_param = data_ora_ispezione.date()

            chiave_esatta = None
            for k in dati_parametri_aggiuntivi[nome_parametro]["range"].keys():
                if k.strip() == chiave_descrizione:
                    chiave_esatta = k
                    break

            range_valori = dati_parametri_aggiuntivi[nome_parametro]["range"].get(chiave_esatta)
            range_originale = range_valori

            if range_valori:
                descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(chiave_descrizione, f"Descrizione non trovata per '{stato_selezionato}'.")
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
            else:
                descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(chiave_descrizione, f"{nome_parametro} ({stato_selezionato}) senza range definito.")
                parametri_aggiuntivi_da_considerare.append({
                    "nome": nome_parametro,
                    "stato": stato_selezionato,
                    "range_traslato": (np.nan, np.nan),
                    "descrizione": descrizione
                })

    # Range raffreddamento da visualizzare
    t_min_raff_visualizzato = t_min_h if raffreddamento_calcolabile else np.nan
    t_max_raff_visualizzato = t_max_h if raffreddamento_calcolabile else np.nan

    # Intersezione globale
    ranges_per_intersezione_inizio = []
    ranges_per_intersezione_fine = []
    nomi_parametri_usati_per_intersezione = []

    if macchie_range_valido and macchie_range is not None:
        ranges_per_intersezione_inizio.append(macchie_range[0])
        ranges_per_intersezione_fine.append(macchie_range[1])
        nomi_parametri_usati_per_intersezione.append("macchie ipostatiche")

    if rigidita_range_valido and rigidita_range is not None:
        ranges_per_intersezione_inizio.append(rigidita_range[0])
        ranges_per_intersezione_fine.append(rigidita_range[1])
        nomi_parametri_usati_per_intersezione.append("rigidità cadaverica")

    # Potente et al. (minimo)
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
            (not np.isnan(Qd_val)) and
            (Qd_val < qd_threshold) and
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

    if raffreddamento_calcolabile:
        usa_solo_limite_inferiore_henssge = (not np.isnan(Qd_val)) and Qd_val < 0.2
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
            nomi_parametri_usati_per_intersezione.append("raffreddamento cadaverico (intervallo minimo secondo Potente et al.)")
        elif usa_solo_limite_inferiore_henssge:
            if mt_ore is not None and not np.isnan(mt_ore):
                ranges_per_intersezione_inizio.append(mt_ore)
                ranges_per_intersezione_fine.append(np.nan)
                nomi_parametri_usati_per_intersezione.append("raffreddamento cadaverico (intervallo minimo secondo Potente et al.)")
            else:
                ranges_per_intersezione_inizio.append(t_min_h)
                ranges_per_intersezione_fine.append(np.nan)
                nomi_parametri_usati_per_intersezione.append("raffreddamento cadaverico (limite inferiore)")
        else:
            if t_med_raw > 48 and altri_parametri_con_range:
                if t_min_h > 48:
                    ranges_per_intersezione_inizio.append(48.0)
                    ranges_per_intersezione_fine.append(np.nan)
                    nomi_parametri_usati_per_intersezione.append("raffreddamento cadaverico (>48h, affidabilità ridotta)")
                else:
                    ranges_per_intersezione_inizio.append(t_min_h)
                    ranges_per_intersezione_fine.append(t_max_h)
                    nomi_parametri_usati_per_intersezione.append("raffreddamento cadaverico")
            else:
                ranges_per_intersezione_inizio.append(t_min_h)
                ranges_per_intersezione_fine.append(t_max_h)
                nomi_parametri_usati_per_intersezione.append("raffreddamento cadaverico")

    if (not usa_potente_per_intersezione) and (mt_ore is not None) and (not np.isnan(mt_ore)):
        ranges_per_intersezione_inizio.append(mt_ore)
        ranges_per_intersezione_fine.append(np.nan)

    # Calcolo intersezione finale
    if len(ranges_per_intersezione_inizio) > 0:
        comune_inizio = max(ranges_per_intersezione_inizio)
        superiori_finiti = [v for v in ranges_per_intersezione_fine if not np.isnan(v) and v < INF_HOURS]
        comune_fine = min(superiori_finiti) if superiori_finiti else np.nan
        overlap = np.isnan(comune_fine) or (comune_inizio <= comune_fine)
    else:
        comune_inizio = np.nan
        comune_fine = np.nan
        overlap = False

    # ====== GRAFICO ======
    num_params_grafico = 0
    if macchie_range_valido: num_params_grafico += 1
    if rigidita_range_valido: num_params_grafico += 1
    if raffreddamento_calcolabile: num_params_grafico += 1
    num_params_grafico += len([p for p in parametri_aggiuntivi_da_considerare if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1])])

    if num_params_grafico > 0:
        fig, ax = plt.subplots(figsize=(10, max(2, 1.5 + 0.5 * num_params_grafico)))
        parametri_grafico, ranges_to_plot_inizio, ranges_to_plot_fine = [], [], []

        if macchie_range_valido and macchie_range is not None:
            label_macchie = f"Ipostasi\n({macchie_range[0]:.1f}–{macchie_range[1]:.1f} h)" if macchie_range[1] < INF_HOURS else f"Ipostasi\n(≥ {macchie_range[0]:.1f} h)"
            parametri_grafico.append(label_macchie); ranges_to_plot_inizio.append(macchie_range[0]); ranges_to_plot_fine.append(macchie_range[1] if macchie_range[1] < INF_HOURS else INF_HOURS)

        if rigidita_range_valido and rigidita_range is not None:
            label_rigidita = f"Rigor\n({rigidita_range[0]:.1f}–{rigidita_range[1]:.1f} h)" if rigidita_range[1] < INF_HOURS else f"Rigor\n(≥ {rigidita_range[0]:.1f} h)"
            parametri_grafico.append(label_rigidita); ranges_to_plot_inizio.append(rigidita_range[0]); ranges_to_plot_fine.append(rigidita_range[1] if rigidita_range[1] < INF_HOURS else INF_HOURS)

        label_hensge = None
        if raffreddamento_calcolabile:
            if (not np.isnan(Qd_val)) and Qd_val < 0.2:
                label_hensge = f"Raffreddamento\n(> {t_min_h:.1f} h)\n({t_min_h:.1f}–{t_max_h:.1f} h)"
            elif t_med_raw is not None and t_med_raw > 30:
                label_hensge = f"Raffreddamento\n(> {30.0:.1f} h)\n({t_min_h:.1f}–{t_max_h:.1f} h)"
            else:
                label_hensge = f"Raffreddamento\n({t_min_h:.1f}–{t_max_h:.1f} h)"
            parametri_grafico.append(label_hensge); ranges_to_plot_inizio.append(t_min_h); ranges_to_plot_fine.append(t_max_h)

        for p in parametri_aggiuntivi_da_considerare:
            if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1]):
                nome_breve = nomi_brevi.get(p['nome'], p['nome'])
                label = f"{nome_breve}\n({p['range_traslato'][0]:.1f}–{p['range_traslato'][1]:.1f} h)" if p['range_traslato'][1] != INF_HOURS else f"{nome_breve}\n(≥ {p['range_traslato'][0]:.1f} h)"
                if p.get('adattato', False):
                    label += " *"
                parametri_grafico.append(label)
                ranges_to_plot_inizio.append(p["range_traslato"][0])
                ranges_to_plot_fine.append(p["range_traslato"][1] if p["range_traslato"][1] < INF_HOURS else INF_HOURS)

        for i, (s, e) in enumerate(zip(ranges_to_plot_inizio, ranges_to_plot_fine)):
            if not np.isnan(s) and not np.isnan(e):
                ax.hlines(i, s, e, linewidth=6)

        # Mediane/medie per ipostasi/rigidità
        y_indices_mapping, current_y_index = {}, 0
        if macchie_range_valido and macchie_range is not None:
            y_indices_mapping["Macchie ipostatiche"] = current_y_index; current_y_index += 1
        if rigidita_range_valido and rigidita_range is not None:
            y_indices_mapping["Rigidità cadaverica"] = current_y_index; current_y_index += 1
        if raffreddamento_calcolabile:
            y_indices_mapping["Raffreddamento cadaverico"] = current_y_index; current_y_index += 1

        if macchie_range_valido and macchie_medi_range is not None and "Macchie ipostatiche" in y_indices_mapping:
            ax.hlines(y_indices_mapping["Macchie ipostatiche"], macchie_medi_range[0], macchie_medi_range[1], linewidth=6, alpha=0.6)
        if rigidita_range_valido and rigidita_medi_range is not None and "Rigidità cadaverica" in y_indices_mapping:
            ax.hlines(y_indices_mapping["Rigidità cadaverica"], rigidita_medi_range[0], rigidita_medi_range[1], linewidth=6, alpha=0.6)
        if raffreddamento_calcolabile and "Raffreddamento cadaverico" in y_indices_mapping:
            y_pos = y_indices_mapping["Raffreddamento cadaverico"]
            punto_medio = (t_min_raff_visualizzato + t_max_raff_visualizzato) / 2
            ax.hlines(y_pos, punto_medio - 0.1, punto_medio + 0.1, linewidth=6, alpha=0.8)

        ax.set_yticks(range(len(parametri_grafico)))
        ax.set_yticklabels(parametri_grafico, fontsize=9)
        ax.set_xlabel("Ore dal decesso")
        max_x_value = 10
        valid_limits = [lim for lim in (ranges_to_plot_fine + ranges_to_plot_inizio) if not np.isnan(lim) and lim < INF_HOURS]
        if valid_limits:
            max_x_value = max(max_x_value, max(valid_limits) * 1.1, 10)
        ax.set_xlim(0, max_x_value)
        ax.grid(True, axis='x', linestyle=':', alpha=0.6)

        if overlap and not np.isnan(comune_inizio) and comune_inizio < max_x_value:
            ax.axvline(max(0, comune_inizio), linestyle='--')
            if not np.isnan(comune_fine):
                ax.axvline(min(max_x_value, comune_fine), linestyle='--')

        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.markdown("<p style='color:orange;font-weight:bold;'>⚠️ Nessun parametro tanatologico con un range valido da visualizzare nel grafico.</p>", unsafe_allow_html=True)

    # NOTE/AVVISI HENSSGE
    if minuti_isp not in [0, 15, 30, 45]:
        st.markdown("<p style='color:darkorange;font-size:small;'>NB: l’orario dei rilievi è stato arrotondato al quarto d’ora più vicino.</p>", unsafe_allow_html=True)

    if (input_rt is not None and input_ta is not None and input_tm is not None and input_w is not None and st.session_state.get("fattore_correzione", None) is not None):
        if input_ta > 25:
            st.markdown("<p style='color:darkorange;font-size:small;'>T. ambiente > 25 °C: un FC ≠ 1 può influenzare molto i risultati.</p>", unsafe_allow_html=True)
        if input_ta < 18:
            st.markdown("<p style='color:darkorange;font-size:small;'>T. ambiente < 18 °C: un FC ≠ 1 può influenzare molto i risultati.</p>", unsafe_allow_html=True)
        if temp_difference_small:
            st.markdown("<p style='color:darkorange;font-size:small;'>Differenza T rettale-ambiente minima: possibile equilibrio termico. Interpretare con cautela.</p>", unsafe_allow_html=True)

    # ====== TESTO COMPLESSIVO (sempre FUORI dall’expander) ======
    summary_text = None
    if overlap:
        isp = data_ora_ispezione
        limite_superiore_infinito = np.isnan(comune_fine) or comune_fine == INF_HOURS
        if limite_superiore_infinito and not np.isnan(comune_inizio):
            hm = _split_hours_minutes(comune_inizio)
            comune_inizio_hours, comune_inizio_minutes = hm if hm else (0, 0)
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 and comune_inizio_minutes == 0 else "ore"
            da = isp - datetime.timedelta(hours=comune_inizio)
            summary_text = (
                f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
            )
        elif not np.isnan(comune_inizio) and not np.isnan(comune_fine):
            hm = _split_hours_minutes(comune_inizio); in_h, in_m = hm if hm else (0, 0)
            hm = _split_hours_minutes(comune_fine); fi_h, fi_m = hm if hm else (0, 0)
            in_tx = "ora" if in_h == 1 else "ore"; fi_tx = "ora" if fi_h == 1 else "ore"
            da = isp - datetime.timedelta(hours=comune_fine)
            aa = isp - datetime.timedelta(hours=comune_inizio)
            if da.date() == aa.date():
                summary_text = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{in_h} {in_tx}{'' if in_m == 0 else f' {in_m} minuti'} e "
                    f"{fi_h} {fi_tx}{'' if fi_m == 0 else f' {fi_m} minuti'} "
                    f"prima dei rilievi, ovvero circa tra le ore {da.strftime('%H:%M')} e le ore {aa.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
                )
            else:
                summary_text = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{in_h} {in_tx}{'' if in_m == 0 else f' {in_m} minuti'} e "
                    f"{fi_h} {fi_tx}{'' if fi_m == 0 else f' {fi_m} minuti'} "
                    f"prima dei rilievi, ovvero tra le ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')} "
                    f"e le ore {aa.strftime('%H:%M')} del {aa.strftime('%d.%m.%Y')}."
                )
    else:
        # discordanza evidente
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>", unsafe_allow_html=True)

    # ====== EXPANDER: descrizioni su richiesta ======
    with st.expander("Dettaglio interpretazione (facoltativo)"):
        if raffreddamento_calcolabile and (not np.isnan(t_min_raff_visualizzato)) and (not np.isnan(t_max_raff_visualizzato)):
            hm = _split_hours_minutes(t_min_raff_visualizzato); h1, m1 = hm if hm else (0, 0)
            hm = _split_hours_minutes(t_max_raff_visualizzato); h2, m2 = hm if hm else (0, 0)
            st.markdown(
                f"- Henssge: tra circa {h1} {'ora' if h1==1 and m1==0 else 'ore'}"
                f"{'' if m1==0 else f' {m1} minuti'} e {h2} {'ora' if h2==1 and m2==0 else 'ore'}"
                f"{'' if m2==0 else f' {m2} minuti'} prima dei rilievi.",
                unsafe_allow_html=True
            )
            if (not np.isnan(Qd_val)) and Qd_val < 0.2:
                st.markdown(f"  - Qd={Qd_val:.4f} (&lt;0.2): intervallo indicativo (±20% della media).", unsafe_allow_html=True)
            if (not np.isnan(Qd_val)) and Qd_val > 0.2 and t_med_raw > 30:
                st.markdown("  - Stima media > 30h: affidabilità ridotta.", unsafe_allow_html=True)

        st.markdown(f"- {testi_macchie[macchie_selezionata]}", unsafe_allow_html=True)
        st.markdown(f"- {rigidita_descrizioni[rigidita_selezionata]}", unsafe_allow_html=True)
        for p in parametri_aggiuntivi_da_considerare:
            if p["stato"] not in ("Non valutata", "Non valutabile/non attendibile"):
                st.markdown(f"- {p['descrizione']}", unsafe_allow_html=True)

    # >>> Stampa del TESTO COMPLESSIVO FUORI dall’expander <<<
    if summary_text:
        st.markdown(f"<b>{summary_text}</b>", unsafe_allow_html=True)

# Esegui su submit
if 'submitted' in locals() and submitted:
    aggiorna_grafico()
