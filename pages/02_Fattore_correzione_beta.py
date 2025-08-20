# pages/02_Fattore_correzione_beta.py
# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Fattore di correzione (beta)",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Fattore di correzione — beta")

# --- Help compatti ---
HELP_CONDIZIONE = "Se il corpo è immerso in acqua, abbigliamento e coperte non sono rilevanti."
HELP_CORRENTI_ARIA = "Se ci sono finestre aperte, ventole o correnti naturali, seleziona 'con correnti d'aria'."
HELP_COPERTE = "Considera solo se coprono addome/torace inferiore."

# Dizionario etichette brevi -> descrizioni estese per Appoggio
APP_APPOGGIO_MAP = {
    "Indifferente": "Pavimento di casa, terreno o prato asciutto, asfalto",
    "Isolante": "Materasso o tappeto spesso",
    "Molto isolante": "Imbottitura pesante (es sacco a pelo isolante, polistirolo, divano imbottito)",
    "Conduttivo": "Cemento, pietra, pavimento in PVC, pavimentazione esterna",
    "Molto conduttivo": "Superficie metallica spessa, all'esterno.",
    "Foglie umide (>= 2 cm)": "Foglie umide (>= 2 cm)",
    "Foglie secche (>= 2 cm)": "Foglie secche (>= 2 cm)",
}

HELP_SUPERFICIE = (
    "Significato delle opzioni:\n"
    "- Indifferente = Pavimento di casa / terreno / prato asciutto / asfalto\n"
    "- Isolante = Materasso o tappeto spesso\n"
    "- Molto isolante = Imbottitura pesante (es. sacco a pelo isolante, polistirolo, divano imbottito)\n"
    "- Conduttivo = Cemento, pietra, pavimento in PVC, pavimentazione esterna\n"
    "- Molto conduttivo = Superficie metallica spessa, all'esterno\n"
    "- Foglie umide/secche = strato di foglie di almeno 2 cm"
)

# 1) Peso su riga isolata
peso = st.number_input(
    "Peso corporeo (kg)",
    min_value=10.0, max_value=200.0, value=70.0, step=0.5,
)

# 2) Condizioni iniziali (radio orizzontali, no colonne)
stato = st.radio(
    "**Condizioni del corpo**",
    ["asciutto", "bagnato", "in acqua"],
    index=0,
    horizontal=True,
    help=HELP_CONDIZIONE,
)

scelta_vestizione = st.radio(
    "**Vestizione**",
    ["nudo e scoperto", "vestito e/o coperto"],
    index=0,  # default richiesto
    horizontal=True,
)

# Caso: immerso -> UI minima e stop
if stato == "in acqua":
    acqua_tipo = st.radio(
        "**Condizioni dell'acqua**",
        ["acqua stagnante", "acqua corrente"],
        index=0,
        horizontal=True,
    )
    fattore_finale = 0.35 if acqua_tipo == "acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# 3) Correnti d’aria + Appoggio (senza colonne, orizzontali)
correnti_aria = st.radio(
    "**Correnti d'aria?**",
    ["senza correnti", "con correnti d'aria"],
    index=0,
    horizontal=True,
    help=HELP_CORRENTI_ARIA,
)

superficie_short = st.radio(
    "**Appoggio**",
    list(APP_APPOGGIO_MAP.keys()),
    index=0,  # default: Indifferente
    horizontal=True,
    help=HELP_SUPERFICIE,
)
superficie_full = APP_APPOGGIO_MAP[superficie_short]  # mappatura alla descrizione estesa (se serve più avanti)

# 4) Abbigliamento e coperte (tabella compatta a 1 riga)
fattore_preliminare = 1.0
if scelta_vestizione == "vestito e/o coperto":
    df = pd.DataFrame(
        {
            "Sottili": pd.Series([0], dtype="int"),
            "Spessi": pd.Series([0], dtype="int"),
            "Lenz.+": pd.Series([0], dtype="int"),
            "Cop. medie": pd.Series([0], dtype="int"),
            "Cop. pesanti": pd.Series([0], dtype="int"),
            "Lenz.++": pd.Series([False], dtype="bool"),
        }
    )

    edited = st.data_editor(
        df,
        hide_index=True,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "Sottili": st.column_config.NumberColumn(min_value=0, step=1, help="Strati leggeri"),
            "Spessi": st.column_config.NumberColumn(min_value=0, step=1, help="Strati pesanti"),
            "Lenz.+": st.column_config.NumberColumn(min_value=0, step=1, help="Lenzuola sottili"),
            "Cop. medie": st.column_config.NumberColumn(min_value=0, step=1, help="Coperte mezza stagione"),
            "Cop. pesanti": st.column_config.NumberColumn(min_value=0, step=1, help="Coperte spesse"),
            "Lenz.++": st.column_config.CheckboxColumn(help=HELP_COPERTE),
        },
    )

    r = edited.iloc[0]
    fattore_preliminare = 1.0
    if r["Sottili"] > 0:
        fattore_preliminare += min(int(r["Sottili"]) * 0.075, 1.8)
    if r["Spessi"] > 0:
        fattore_preliminare += min(int(r["Spessi"]) * 0.15, 1.8)
    if r["Lenz.+"] > 0:
        fattore_preliminare += min(int(r["Lenz.+"]) * 0.075, 1.8)
    if bool(r["Lenz.++"]):
        fattore_preliminare += 1.0
    if r["Cop. medie"] > 0:
        fattore_preliminare += 1.5 + max(0, int(r["Cop. medie"]) - 1) * 0.2
    if r["Cop. pesanti"] > 0:
        fattore_preliminare += 1.5 + max(0, int(r["Cop. pesanti"]) - 1) * 0.3

# 5) Correzione peso (Tabella 2 - compatta)
def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    if f_base >= 1.4:
        return f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return f_base

fattore_finale = correzione_peso_tabella2(float(fattore_preliminare), float(peso))

# 6) Output
st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
