# app/data_sources.py
import pandas as pd
import streamlit as st
from pathlib import Path

from app import i18n


@st.cache_data
def load_tabelle_correzione():
    """
    Ritorna la tabella correttiva del peso (DataFrame) letta da Excel.
    Richiede 'openpyxl'. Se il file non esiste o non è leggibile,
    ritorna None (l'app continua senza correzione peso).
    """
    xlsx_path = Path("data/tabella_secondaria.xlsx")  # ← adatta il percorso se diverso
    if not xlsx_path.exists():
        st.info(i18n.ui_text("data.weight_table_missing"))
        return None
    try:
        # usa esplicitamente openpyxl per .xlsx
        return pd.read_excel(xlsx_path, engine="openpyxl")
    except ImportError:
        st.error(i18n.ui_text("data.openpyxl_missing"))
        return None
    except Exception as e:
        st.warning(i18n.ui_text("data.weight_table_read_error", error=e))
        return None
