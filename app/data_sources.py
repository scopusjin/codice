# app/data_sources.py
import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_tabelle_correzione():
    """
    Ritorna la tabella correttiva del peso (DataFrame) letta da Excel.
    Richiede 'openpyxl'. Se il file non esiste o non è leggibile,
    ritorna None (l'app continua senza correzione peso).
    """
    xlsx_path = Path("data/tabella_secondaria.xlsx")  # ← adatta il percorso se diverso
    if not xlsx_path.exists():
        st.info("Tabella correttiva del peso non trovata: continuo senza.")
        return None
    try:
        # usa esplicitamente openpyxl per .xlsx
        return pd.read_excel(xlsx_path, engine="openpyxl")
    except ImportError:
        st.error("Per leggere il file .xlsx serve 'openpyxl'. Installa con: pip install openpyxl")
        return None
    except Exception as e:
        st.warning(f"Impossibile leggere l'Excel della tabella peso: {e}")
        return None
