# app/data_sources.py
import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_tabelle_correzione():
    """
    Ritorna la tabella correttiva del peso come DataFrame, se trovata.
    Prova prima CSV, poi Excel solo se 'openpyxl' è presente.
    Se nulla è leggibile, ritorna None (l'app continua senza tabella).
    """
    csv_path = Path("data/tabella_secondaria.csv")
    if csv_path.exists():
        try:
            return pd.read_csv(csv_path)
        except Exception as e:
            st.warning(f"Tabella peso CSV trovata ma non leggibile: {e}")

    xlsx_path = Path("data/tabella_secondaria.xlsx")
    if xlsx_path.exists():
        try:
            import openpyxl  # lazy import, evita crash se manca
            return pd.read_excel(xlsx_path, engine="openpyxl")
        except ImportError:
            st.info("`openpyxl` non installato: salto l'Excel e continuo senza tabella peso.")
        except Exception as e:
            st.warning(f"Impossibile leggere l'Excel della tabella peso: {e}")

    st.info("Tabella correttiva del peso non trovata: continuo senza (FC per peso disabilitato).")
    return None
