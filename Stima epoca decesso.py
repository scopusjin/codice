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
    "Migrab
