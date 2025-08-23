# app/data_sources.py
import pandas as pd
import streamlit as st

@st.cache_data
def load_tabelle_correzione():
    t1 = pd.read_excel("data/tabella_rielaborata.xlsx", engine="openpyxl")
    t2 = pd.read_excel("data/tabella_secondaria.xlsx", engine="openpyxl")
    t1['Fattore'] = pd.to_numeric(t1['Fattore'], errors='coerce')
    for col in ["Ambiente", "Vestiti", "Coperte", "Superficie d'appoggio", "Correnti"]:
        t1[col] = t1[col].astype(str).str.strip()
    return t1, t2
