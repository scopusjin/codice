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
st.caption("Modalità Tabella (originale) + Modalità Formula (senza tabella). Condizioni del corpo spostate **prima** della tabella. Selezione iniziale senza titolo: 
*nudo e scoperto* vs *vestito e/o coperto*. La tabella compare solo se selezioni *vestito e/o coperto*. Se *in acqua*, resta solo la scelta stagnante/corrente con valori fissi (0.35 / 0.50).") + Modalità Formula (senza tabella). Condizioni del corpo spostate **prima** della tabella. Selezione iniziale senza titolo: \n*nudo e scoperto* vs *vestito e/o coperto*. La tabella compare solo se selezioni *vestito e/o coperto*. Se *in acqua*, resta solo la scelta stagnante/corrente con valori fissi.")

# =========================
# Helper per label "senza titolo"
# =========================
RADIO_NO_LABEL = ""

# =========================
# SEZIONE 0 — Scelta rapida (senza titolo): nudo/scoperto vs vestito/coperto
# =========================
colA, colB = st.columns([1, 3])
with colA:
    scelta_vestizione = st.radio(
        RADIO_NO_LABEL,
        ("nudo e scoperto", "vestito e/o coperto"),
        horizontal=True,
        index=1,
        label_visibility="collapsed",
        help="Scegli rapidamente se il corpo è completamente nudo e non coperto, oppure se presenta abiti e/o coperte."
    )
with colB:
    st.write("")

# =========================
# SEZIONE 1 — Condizioni del corpo (PRIMA della tabella)
# =========================
st.subheader("Condizioni del corpo")

cond_col1, cond_col2 = st.columns([1.2, 1.2])
with cond_col1:
    stato = st.selectbox(
        "Stato del corpo",
        ["asciutto", "bagnato", "in acqua"],
        index=0,
        help="Se il corpo è immerso *in acqua*, vengono nascosti tutti gli altri parametri tranne la scelta stagnante/corrente."
    )

correnti_aria = None
correnti_acqua = None
superficie = None
peso = None

if stato == "in acqua":
    with cond_col2:
        correnti_acqua = st.selectbox(
            "Acqua",
            ["acqua stagnante", "acqua corrente"],
            index=0,
            help="Specificare se l'acqua è stagnante o corrente."
        )

else:
    # Gestione comune per corpi non immersi (asciutto o bagnato)
    cond_col2, cond_col3, cond_col4 = st.columns([1.2, 1.2, 1.2])
    with cond_col2:
        correnti_aria = st.selectbox(
            "Correnti d'aria",
            ["senza correnti", "con correnti d'aria"],
            index=0,
            help="Rilevante solo se corpo non immerso."
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

    cond_col2, cond_col3, cond_col4 = st.columns([1.2, 1.2, 1.2])
    with cond_col2:
        correnti_aria = st.selectbox(
            "Correnti d'aria",
            ["senza correnti", "con correnti d'aria"],
            index=0,
            help="Rilevante solo se corpo non immerso."
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
# SEZIONE 2 — Tabella abbigliamento/coperture (solo se vestito/coperto e non in acqua)
# =========================
mostra_tabella = (scelta_vestizione == "vestito e/o coperto") and (stato != "in acqua")

if stato == "in acqua":
    st.subheader("Condizione idrica")
    if correnti_acqua == "acqua corrente":
        fattore_finale = 0.35
    else:
        fattore_finale = 0.50
    st.success(f"FATTORE DI CORREZIONE FINALE: **{fattore_finale:.2f}** (condizione idrica fissa)")

elif mostra_tabella:
    st.subheader("Abbigliamento e coperte — Tabella")
    st.caption("Usa i contatori su una sola riga. Valori base e incrementi come da specifiche. La correzione peso (Tabella 2) è applicata dopo il calcolo preliminare.")

    schema = {
        "n. strati sottili": 0,
        "n. strati spessi": 0,
        "n. lenzuolo +": 0,
        "n. coperte medie": 0,
        "n. coperte pesanti": 0,
        "lenzuolo ++": False,
    }
    df = pd.DataFrame([schema])

    edited = st.data_editor(
        df,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "n. strati sottili": st.column_config.NumberColumn(min_value=0, step=1),
            "n. strati spessi": st.column_config.NumberColumn(min_value=0, step=1),
            "n. lenzuolo +": st.column_config.NumberColumn(min_value=0, step=1),
            "n. coperte medie": st.column_config.NumberColumn(min_value=0, step=1),
            "n. coperte pesanti": st.column_config.NumberColumn(min_value=0, step=1),
            "lenzuolo ++": st.column_config.CheckboxColumn(help="Se selezionato, applica il valore base dedicato + incrementi."),
        },
        use_container_width=True,
    )

    r = edited.iloc[0]
    fattore = 1.0

    if r["n. strati sottili"] > 0:
        fattore += min(r["n. strati sottili"] * 0.075, 1.8)
    if r["n. strati spessi"] > 0:
        fattore += min(r["n. strati spessi"] * 0.15, 1.8)
    if r["n. lenzuolo +"] > 0:
        fattore += min(r["n. lenzuolo +"] * 0.075, 1.8)
    if bool(r["lenzuolo ++"]):
        fattore += 1.0
    if r["n. coperte medie"] > 0:
        fattore += 1.5 + (r["n. coperte medie"] - 1) * 0.2
    if r["n. coperte pesanti"] > 0:
        fattore += 1.5 + (r["n. coperte pesanti"] - 1) * 0.3

    st.info(f"Fattore preliminare (prima di correzioni stato/superficie/peso): **{fattore:.2f}**")

    if correnti_aria is not None and correnti_aria == "con correnti d'aria":
        fattore *= 1.05
    if superficie and "Imbottitura pesante" in superficie:
        fattore *= 0.95

    def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
        if f_base >= 1.4:
            return f_base * (0.98 + (peso_kg / 70.0) * 0.02)
        return f_base

    fattore_finale = correzione_peso_tabella2(fattore, float(peso)) if peso else fattore

    st.success(f"FATTORE DI CORREZIONE FINALE: **{fattore_finale:.2f}**")

else:
    st.subheader("Abbigliamento e coperte — Tabella")
    st.caption("La tabella è nascosta perché hai selezionato **nudo e scoperto**. I parametri di abbigliamento/copertura non si applicano.")

st.caption(f"Ultimo aggiornamento UI: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
