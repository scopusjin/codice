# app/data_sources.py
# -*- coding: utf-8 -*-
"""
Gestione dei file Excel per i fattori di correzione.

"""

import pandas as pd
import streamlit as st


@st.cache_data
def load_tabelle_correzione() -> pd.DataFrame:
    """
    Carica la Tabella 2 (Excel) per l'adattamento del fattore di correzione al peso.
    Restituisce un DataFrame pandas.
    """
    try:
        tabella2 = pd.read_excel("data/tabella_secondaria.xlsx", engine="openpyxl")
    except Exception as e:
        st.error(f"Errore nel caricamento della Tabella correttiva del peso: {e}")
        return None
    return tabella2
