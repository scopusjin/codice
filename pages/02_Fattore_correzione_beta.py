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
# Scelta rapida
# =========================
scelta_vestizione = st.radio(
    "",
    ("nudo e scoperto", "vestito e/o coperto"),
    horizontal=True,
    index=1,
    label_visibility="collapsed",
)

# =========================
# Condizioni del corpo
# =========================
colA, colB, colC, colD = st.columns([1, 1, 1, 1])

with colA:
    stato = st.selectbox(
        "Stato",
        ["asciutto", "bagnato", "in acqua"],
        index=0,
    )

# Caso: corpo immerso → UI minima
if stato == "in acqua":
    with colB:
        acqua_tipo = st.selectbox("Acqua", ["acqua stagnante", "acqua corrente"], index=0)
    fattore_finale = 0.35 if acqua_tipo == "acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# Caso: non immerso → opzioni compatte
with colB:
    correnti_aria = st.selectbox("Correnti", ["senza correnti", "con correnti d'aria"], index=0)

with colC:
    superficie = st.selectbox(
        "Superficie",
        [
            "Pavimento/terreno/prato/asfalto",
            "Materasso o tappeto spesso",
            "Imbottitura pesante",
            "Foglie umide (≥2 cm)",
            "Foglie secche (≥2 cm)",
        ],
        index=0,
    )

with colD:
    peso = st.number_input("Peso (kg)", min_value=10.0, max_value=200.0, value=70.0, step=0.5)

st.divider()

# =========================
# Abbigliamento e coperte (compatti)
# =========================
mostra_tabella = (scelta_vestizione == "vestito e/o coperto")
fattore_preliminare = 1.0

if mostra_tabella:
    schema = {
        "n. strati sottili": pd.Series([0], dtype="int"),
        "n. strati spessi": pd.Series([0], dtype="int"),
        "n. lenzuolo +": pd.Series([0], dtype="int"),
        "n. coperte medie": pd.Series([0], dtype="int"),
        "n. coperte pesanti": pd.Series([0], dtype="int"),
        "lenzuolo ++": pd.Series([False], dtype="bool"),
    }
    df = pd.DataFrame(schema)

    edited = st.data_editor(
        df,
        hide_index=True,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "n. strati sottili": st.column_config.NumberColumn(label="Sottili", min_value=0, step=1),
            "n. strati spessi": st.column_config.NumberColumn(label="Spessi", min_value=0, step=1),
            "n. lenzuolo +": st.column_config.NumberColumn(label="Lenz.+", min_value=0, step=1),
            "n. coperte medie": st.column_config.NumberColumn(label="Cop. medie", min_value=0, step=1),
            "n. coperte pesanti": st.column_config.NumberColumn(label="Cop. pesanti", min_value=0, step=1),
            "lenzuolo ++": st.column_config.CheckboxColumn(label="Lenz.++"),
        },
    )

    r = edited.iloc[0]
    fattore_preliminare = 1.0
    if r["n. strati sottili"] > 0:
        fattore_preliminare += min(r["n. strati sottili"] * 0.075, 1.8)
    if r["n. strati spessi"] > 0:
        fattore_preliminare += min(r["n. strati spessi"] * 0.15, 1.8)
    if r["n. lenzuolo +"] > 0:
        fattore_preliminare += min(r["n. lenzuolo +"] * 0.075, 1.8)
    if r["lenzuolo ++"]:
        fattore_preliminare += 1.0
    if r["n. coperte medie"] > 0:
