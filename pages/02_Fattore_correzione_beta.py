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

# =========================
# Help (stile esempio)
# =========================
HELP_CONDIZIONE = (
    "Se il corpo è **immerso in acqua**, abbigliamento e coperte non sono rilevanti: "
    "verranno mostrati solo i parametri pertinenti (acqua stagnante/corrente)."
)
HELP_CORRENTI_ARIA = (
    "Seleziona *Eposto a corrente d’aria* quando il corpo è in prossimità di finestre aperte, ventole, "
    "correnti d’aria naturali o artificiali. Altrimenti scegli *Nessuna corrente*."
)
HELP_SUPERFICIE = (
    "Scegli il supporto su cui è adagiato il corpo. *Isolante* riduce lo scambio termico, "
    "*Conduttivo* lo aumenta. Le **foglie** compaiono solo in condizioni particolari."
)
HELP_COPERTE = (
    "Tenerne conto solo se coprono addome/torace inferiore. "
    "Lenzuolo + = telo sottile; Lenzuolo ++ = invernale/copriletto; "
    "Coperta medie/pesanti = mezza stagione/pesanti."
)

# =========================
# Peso su riga isolata
# =========================
peso = st.number_input(
    "Peso (kg)",
    min_value=10.0,
    max_value=200.0,
    value=70.0,
    step=0.5,
)

# =========================
# Condizioni iniziali (radio orizzontali, con titoletti e help)
# =========================
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("**Condizioni del corpo**")
    stato = st.radio(
        "",
        ["asciutto", "bagnato", "in acqua"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        help=HELP_CONDIZIONE,
    )

with col2:
    st.markdown("**Vestizione**")
    scelta_vestizione = st.radio(
        "",
        ["nudo e scoperto", "vestito e/o coperto"],
        index=1,
        horizontal=True,
        label_visibility="collapsed",
    )

# Caso: corpo immerso -> UI minima
if stato == "in acqua":
    st.markdown("**Condizioni dell’acqua**")
    acqua_tipo = st.radio(
        "",
        ["acqua stagnante", "acqua corrente"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )
    fattore_finale = 0.35 if acqua_tipo == "acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# =========================
# Correnti + Appoggio (con titoletti e help)
# =========================
colA, colB = st.columns([1, 2])

with colA:
    st.markdown("**Correnti d’aria?**")
    correnti_aria = st.radio(
        "",
        ["senza correnti", "con correnti d'aria"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        help=HELP_CORRENTI_ARIA,
    )

with colB:
    st.markdown("**Appoggio**")
    superficie = st.radio(
        "",
        [
            "Pavimento/terreno/prato/asfalto",
            "Materasso o tappeto spesso",
            "Imbottitura pesante",
            "Foglie umide (>= 2 cm)",
            "Foglie secche (>= 2 cm)",
        ],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        help=HELP_SUPERFICIE,
    )

# =========================
# Abbigliamento e coperte (compatti)
# =========================
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

# =========================
# Correzione peso (Tabella 2 - compatta)
# =========================
def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    if f_base >= 1.4:
        return f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return f_base

fattore_finale = correzione_peso_tabella2(float(fattore_preliminare), float(peso))

# =========================
# Output compatto
# =========================
st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
