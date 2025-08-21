# pages/02_Fattore_correzione_beta.py
# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

# =========================
# Config pagina
# =========================
st.set_page_config(
    page_title="Fattore di correzione (beta)",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Fattore di correzione — beta")

# =========================
# Help compatti
# =========================
HELP_CONDIZIONE = "Se il corpo è immerso in acqua, abbigliamento e coperte non sono rilevanti."
HELP_CORRENTI_ARIA = "Se ci sono finestre aperte, ventole o correnti naturali, seleziona 'con correnti d'aria'."
HELP_COPERTE = "Considera solo se coprono la parte inferiore del tronco"
HELP_SUPERFICIE = (
    "Indifferente = Pavimento/terreno/prato asciutto/asfalto · "
    "Isolante = Materasso/tappeto spesso · "
    "Molto isolante = Imbottitura pesante (sacco a pelo, polistirolo, divano imbottito) · "
    "Conduttivo = Cemento/pietra/PVC/esterno · "
    "Molto conduttivo = Superficie metallica spessa all'esterno (solo nudo asciutto) · "
    "Foglie = strato ≥ 2 cm"
)

# Etichette brevi -> descrizioni estese
APP_APPOGGIO_MAP = {
    "Indifferente": "Pavimento di casa, terreno o prato asciutto, asfalto",
    "Isolante": "Materasso o tappeto spesso",
    "Molto isolante": "sacco a pelo tecnico, polistirolo, divano imbottito)",
    "Conduttivo": "Cemento, pietra, pavimentazione esterna, pavimento in PVC.",
    "Molto conduttivo": "Superficie metallica spessa, in ambiente esterno.",
    "Foglie (>= 2 cm)": "adagiato su uno spesso strato di foglie",
}

# =========================
# 1) Peso su riga isolata
# =========================
peso = st.number_input(
    "Peso corporeo (kg)",
    min_value=10.0, max_value=200.0, value=70.0, step=0.5,
)

# =========================
# 2) Condizioni iniziali (no colonne, opzioni orizzontali)
# =========================
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

# Caso: immerso -> UI minima e stop (niente tabella vestiti)
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

# =========================
# 3) Tabella VESTITI/COPERTE subito sotto la riga “Vestizione”
# =========================
# Contatori di default (anche se nudo restano 0)
n_sottili = n_spessi = n_lenz_plus = n_cop_medie = n_cop_pesanti = 0
has_lenz_pp = False

fattore_preliminare = 1.0

if scelta_vestizione == "vestito e/o coperto":
    # DataFrame a 1 riga con dtype espliciti
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
        key="editor_vestiti",  # evita conflitti di stato fra rerun
        column_config={
            "Sottili": st.column_config.NumberColumn(min_value=0, step=1),
            "Spessi": st.column_config.NumberColumn(min_value=0, step=1),
            "Lenz.+": st.column_config.NumberColumn(min_value=0, step=1),
            "Cop. medie": st.column_config.NumberColumn(min_value=0, step=1),
            "Cop. pesanti": st.column_config.NumberColumn(min_value=0, step=1),
            "Lenz.++": st.column_config.CheckboxColumn(),
        },
    )

    r = edited.iloc[0]
    # Valori dai contatori
    n_sottili     = int(r["Sottili"])
    n_spessi      = int(r["Spessi"])
    n_lenz_plus   = int(r["Lenz.+"])
    has_lenz_pp   = bool(r["Lenz.++"])
    n_cop_medie   = int(r["Cop. medie"])
    n_cop_pesanti = int(r["Cop. pesanti"])

    # -----------------------------
    # Calcolo base con regole corrette per le coperte:
    # - Se presente >=1 coperta pesante: BASE = 1.8
    # - altrimenti se presente >=1 coperta media: BASE = 1.5
    # - altrimenti: BASE = 1.0
    # Extra coperte:
    #   * pesante aggiuntiva: +0.3 ciascuna
    #   * media aggiuntiva (o medie quando base è pesante): +0.2 ciascuna
    # Strati:
    #   * sottile: +0.075 ciascuno
    #   * spesso: +0.15 ciascuno
    #   * lenzuolo+: +0.075 ciascuno
    #   * lenzuolo++: +0.15 (checkbox)
    # -----------------------------

    if n_cop_pesanti > 0:
        # Base 1.8, +0.3 per ogni pesante extra, +0.2 per ogni media
        fattore_preliminare = 1.8 + max(0, n_cop_pesanti - 1) * 0.3 + n_cop_medie * 0.2
    elif n_cop_medie > 0:
        # Base 1.5, +0.2 per ogni media extra
        fattore_preliminare = 1.5 + max(0, n_cop_medie - 1) * 0.2
    else:
        fattore_preliminare = 1.0

    # Incrementi vestiti/lenzuola
    fattore_preliminare += n_sottili * 0.075
    fattore_preliminare += n_spessi * 0.15
    fattore_preliminare += n_lenz_plus * 0.075
    if has_lenz_pp:
        fattore_preliminare += 0.15

    # Cap massimo
    fattore_preliminare = min(fattore_preliminare, 3.0)

# =========================
# 4) Correnti d’aria + Appoggio (senza colonne, orizzontali)
# =========================
correnti_aria = st.radio(
    "**Correnti d'aria?**",
    ["senza correnti", "con correnti d'aria"],
    index=0,
    horizontal=True,
    help=HELP_CORRENTI_ARIA,
)

# Opzioni Appoggio: "Molto conduttivo" solo se nudo + asciutto
opts_appoggio = ["Indifferente", "Isolante", "Molto isolante", "Conduttivo"]
if stato == "asciutto" and scelta_vestizione == "nudo e scoperto":
    opts_appoggio.append("Molto conduttivo")
opts_appoggio += ["Foglie umide (>= 2 cm)", "Foglie secche (>= 2 cm)"]

superficie_short = st.radio(
    "**Appoggio**",
    opts_appoggio,
    index=0,  # default: Indifferente
    horizontal=True,
    help=HELP_SUPERFICIE,
)
superficie_full = APP_APPOGGIO_MAP.get(superficie_short, superficie_short)

# =========================
# 5) Regole Appoggio (dopo vestiti/coperte, prima correzione peso)
# =========================
def applica_regole_superficie(
    fatt, superficie_short, stato, correnti_aria, vestizione,
    n_sottili, n_spessi, n_lenz_plus, has_lenz_pp, n_cop_medie, n_cop_pesanti
):
    """Applica le regole dell'appoggio al fattore preliminare."""
    tot_items = (
        n_sottili + n_spessi + n_lenz_plus
        + (1 if has_lenz_pp else 0) + n_cop_medie + n_cop_pesanti
    )

    def only_thin_1():
        return (n_sottili == 1 and tot_items == 1)

    def only_sheet_1():
        return (n_lenz_plus == 1 and tot_items == 1)

    def only_thin_1_2():
        return (
            n_sottili in (1, 2)
            and n_spessi == 0 and n_lenz_plus == 0 and not has_lenz_pp
            and n_cop_medie == 0 and n_cop_pesanti == 0
            and tot_items == n_sottili
        )

    def only_sheet_1_2():
        return (
            n_lenz_plus in (1, 2)
            and n_sottili == 0 and n_spessi == 0 and not has_lenz_pp
            and n_cop_medie == 0 and n_cop_pesanti == 0
            and tot_items == n_lenz_plus
        )

    # 0) Indifferente → nessuna modifica
    if superficie_short == "Indifferente":
        return fatt

    # 1) Isolante
    # - nudo → override 1.20
    # - solo 1 sottile OPPURE solo 1 lenzuolo+ → override 1.10
    # - altrimenti (più vestiti o qualsiasi coperta/lenzuolo++) → +0.10
    if superficie_short == "Isolante":
        if tot_items == 0:
            return 1.20
        elif only_thin_1() or only_sheet_1():
            return 1.10
        else:
            return fatt + 0.10

    # 2) Molto isolante
    # - nudo → override 1.30
    # - solo 1–2 sottili OPPURE solo 1–2 lenzuola+ → +0.30
    # - altrimenti → +0.10
    if superficie_short == "Molto isolante":
        if tot_items == 0:
            return 1.30
        if only_thin_1_2() or only_sheet_1_2():
            return fatt + 0.30
        else:
            return fatt + 0.10

    # 3) Conduttivo
    # - nudo → override 0.75
    # - solo 1 sottile OPPURE solo 1 lenzuolo+ → fatt - 0.20
    # - altrimenti → fatt - 0.10
    if superficie_short == "Conduttivo":
        if tot_items == 0:
            return 0.75
        elif only_thin_1() or only_sheet_1():
            return fatt - 0.20
        else:
            return fatt - 0.10

    # 4) Molto conduttivo (solo nudo + asciutto): override con correnti
    if superficie_short == "Molto conduttivo":
        return 0.55 if correnti_aria == "senza correnti" else 0.50

    # 5) Foglie umide (>= 2 cm)
    # - nudo → override 1.20
    # - solo 1–2 sottili OPPURE solo 1–2 lenzuola+ → +0.20
    # - altrimenti → +0.10
    if superficie_short == "Foglie umide (>= 2 cm)":
        if tot_items == 0:
            return 1.20
        if only_thin_1_2() or only_sheet_1_2():
            return fatt + 0.20
        else:
            return fatt + 0.10

    # 6) Foglie secche (>= 2 cm)
    # - nudo → override 1.50
    # - solo 1–2 sottili OPPURE solo 1–2 lenzuola+ → +0.30
    # - altrimenti → +0.20
    if superficie_short == "Foglie secche (>= 2 cm)":
        if tot_items == 0:
            return 1.50
        if only_thin_1_2() or only_sheet_1_2():
            return fatt + 0.30
        else:
            return fatt + 0.20

    return fatt

# Applica regole Appoggio
fattore_preliminare = applica_regole_superficie(
    fattore_preliminare,
    superficie_short=superficie_short,
    stato=stato,
    correnti_aria=correnti_aria,
    vestizione=scelta_vestizione,
    n_sottili=n_sottili,
    n_spessi=n_spessi,
    n_lenz_plus=n_lenz_plus,
    has_lenz_pp=has_lenz_pp,
    n_cop_medie=n_cop_medie,
    n_cop_pesanti=n_cop_pesanti,
)

# =========================
# 6) Correzione peso (Tabella 2 - compatta / placeholder)
# =========================
def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    # Semplificata; sostituisci con Tabella 2 completa se necessario.
    if f_base >= 1.4:
        return f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return f_base

fattore_finale = correzione_peso_tabella2(float(fattore_preliminare), float(peso))

# =========================
# 7) Output
# =========================
st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
