# pages/02_Fattore_correzione_beta.py
# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from datetime import datetime

# =========================
# Config pagina
# =========================
st.set_page_config(
    page_title="Fattore di correzione (beta)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Fattore di correzione — beta")

# =========================
# Helper per label "senza titolo"
# =========================
RADIO_NO_LABEL = ""

# =========================
# SEZIONE 0 — Scelta rapida (senza titolo): nudo/scoperto vs vestito/coperto
# =========================
scelta_vestizione = st.radio(
    RADIO_NO_LABEL,
    ("nudo e scoperto", "vestito e/o coperto"),
    horizontal=True,
    index=1,
    label_visibility="collapsed",
    help="Scegli se il corpo è completamente nudo e non coperto, oppure se presenta abiti e/o coperte."
)

st.divider()

# =========================
# SEZIONE 1 — Condizioni del corpo (PRIMA della tabella)
# =========================
st.subheader("Condizioni del corpo")
cond_col1 = st.columns([1])[0]
with cond_col1:
    stato = st.selectbox(
        "Stato del corpo",
        ["asciutto", "bagnato", "in acqua"],
        index=0,
        help="Se il corpo è immerso *in acqua*, verranno mostrati solo i parametri pertinenti (acqua stagnante/corrente)."
    )

# Branch 1: Corpo immerso — UI ridotta e fattori fissi
if stato == "in acqua":
    st.subheader("Parametri acqua")
    acqua_tipo = st.selectbox(
        "Acqua",
        ["acqua stagnante", "acqua corrente"],
        index=0,
        help="Seleziona il tipo di acqua."
    )

    # Valori fissi (override totale)
    if acqua_tipo == "acqua corrente":
        fattore_finale = 0.35
    else:
        fattore_finale = 0.50

    st.info("Tabella abbigliamento/coperte nascosta: non rilevante per corpo immerso.")
    st.success(f"FATTORE DI CORREZIONE FINALE (in acqua): **{fattore_finale:.2f}**")
    st.stop()

# Branch 2: Corpo non immerso — mostra correnti d'aria, superficie, peso
cond_col2, cond_col3, cond_col4 = st.columns([1.2, 1.6, 1.2])
with cond_col2:
    correnti_aria = st.selectbox(
        "Correnti d'aria",
        ["senza correnti", "con correnti d'aria"],
        index=0,
        help="Rilevante solo se il corpo non è immerso."
    )
with cond_col3:
    superficie = st.selectbox(
        "Superficie d'appoggio",
        [
            "Pavimento di casa, terreno o prato asciutto, asfalto",
            "Materasso o tappeto spesso",
            "Imbottitura pesante (es sacco a pelo isolante)",
            "Foglie umide (almeno 2 cm)",
            "Foglie secche (almeno 2 cm)",
        ],
        index=0,
    )
with cond_col4:
    peso = st.number_input(
        "Peso corporeo (kg)",
        min_value=10.0, max_value=200.0, value=70.0, step=0.5,
        help="Usato per la correzione di Tabella 2 quando necessario."
    )

st.divider()

# =========================
# SEZIONE 2 — Tabella abbigliamento/coperture (solo se vestito/coperto)
# =========================
mostra_tabella = (scelta_vestizione == "vestito e/o coperto")

fattore_preliminare = 1.0

if mostra_tabella:
    st.subheader("Abbigliamento e coperte — Tabella")

    # Tabella a singola riga con contatori
    schema = {
        "n. strati sottili": 0,
        "n. strati spessi": 0,
        "n. lenzuolo +": 0,
        "n. coperte medie": 0,
        "n. coperte pesanti": 0,
        "lenzuolo ++": False,  # flag dedicato
    }
    df = pd.DataFrame([schema])

    edited = st.data_editor(
        df,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "n. strati sottili": st.column_config.NumberColumn(min_value=0, step=1, help="Strati leggeri"),
            "n. strati spessi": st.column_config.NumberColumn(min_value=0, step=1, help="Strati pesanti"),
            "n. lenzuolo +": st.column_config.NumberColumn(min_value=0, step=1, help="Lenzuola sottili"),
            "n. coperte medie": st.column_config.NumberColumn(min_value=0, step=1, help="Coperte mezza stagione"),
            "n. coperte pesanti": st.column_config.NumberColumn(min_value=0, step=1, help="Coperte spesse"),
            "lenzuolo ++": st.column_config.CheckboxColumn(help="Lenzuolo invernale/copriletto leggero"),
        },
        use_container_width=True,
    )

    r = edited.iloc[0]

    # Valore iniziale
    fattore_preliminare = 1.0

    # Regole incrementali
    if r["n. strati sottili"] > 0:
        fattore_preliminare += min(r["n. strati sottili"] * 0.075, 1.8)
    if r["n. strati spessi"] > 0:
        fattore_preliminare += min(r["n. strati spessi"] * 0.15, 1.8)
    if r["n. lenzuolo +"] > 0:
        fattore_preliminare += min(r["n. lenzuolo +"] * 0.075, 1.8)
    if bool(r["lenzuolo ++"]):
        fattore_preliminare += 1.0
    if r["n. coperte medie"] > 0:
        fattore_preliminare += 1.5 + max(0, r["n. coperte medie"] - 1) * 0.2
    if r["n. coperte pesanti"] > 0:
        fattore_preliminare += 1.5 + max(0, r["n. coperte pesanti"] - 1) * 0.3

    st.info(f"Fattore preliminare (prima di correzioni): **{fattore_preliminare:.2f}**")
else:
    st.subheader("Abbigliamento e coperte — Tabella (nascosta per corpo nudo e scoperto)")

# =========================
# SEZIONE 3 — Adattamenti e correzione peso (solo corpo non immerso)
# =========================
fattore = float(fattore_preliminare)

def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    if f_base >= 1.4:
        return f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return f_base

fattore_finale = correzione_peso_tabella2(fattore, float(peso))

st.success(f"FATTORE DI CORREZIONE FINALE: **{fattore_finale:.2f}**")
