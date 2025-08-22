# pages/03_Fattore_correzione_delta.py
# -*- coding: utf-8 -*-
import math
import streamlit as st

# =========================
# Config pagina
# =========================
st.set_page_config(
    page_title="Fattore di correzione (delta)",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Fattore di correzione — delta")

# =========================
# Help compatti
# =========================
HELP_CONDIZIONE = "Se il corpo è immerso in acqua, abbigliamento e coperte non sono rilevanti."
HELP_CORRENTI_ARIA = "Se ci sono finestre aperte, ventole o correnti naturali, seleziona 'con correnti d'aria'."
HELP_SUPERFICIE = (
    "**Indifferente**: pavimento domestico/terreno asciutto/prato asciutto/asfalto · "
    "**Isolante**: materasso/tappeto spesso · "
    "**Molto isolante**: sacco a pelo tecnico, polistirolo, divano imbottito · "
    "**Conduttivo**: cemento/pietra/pavimento in PVC/pavimentazione esterna · "
    "**Molto conduttivo**: adagiato su superficie metallica spessa all'esterno · "
    "**Foglie**: adagiato su strato spesso di foglie"
)

# =========================
# Utility
# =========================
def clamp(x, lo=0.35, hi=3.0):
    return max(lo, min(hi, x))

def calcola_fattore_vestiti_coperte(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti):
    """
    Regole VOLUTE (come da tua scelta):
    - Base 2.0 se >=1 coperta pesante (+0.3 per ciascuna pesante extra, +0.2 per ciascuna media)
    - Altrimenti base 1.8 se >=1 coperta media (+0.2 per ciascuna media extra)
    - Altrimenti base 1.0
    - Poi: +0.075 per ogni strato sottile (indumento o lenzuolo sottile)
           +0.15  per ogni strato spesso  (indumento pesante o lenzuolo spesso)
    """
    if n_cop_pesanti > 0:
        fatt = 2.0 + max(0, n_cop_pesanti - 1) * 0.3 + n_cop_medie * 0.2
    elif n_cop_medie > 0:
        fatt = 1.8 + max(0, n_cop_medie - 1) * 0.2
    else:
        fatt = 1.0

    fatt += n_sottili_eq * 0.075
    fatt += n_spessi_eq * 0.15
    return float(fatt)  # niente cap locale; clamp solo a fine pipeline

def applica_regole_superficie(
    fatt, superficie_short, stato, correnti_aria, vestizione,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
):
    """Regole di appoggio (con ‘Molto conduttivo’ a precedenza assoluta)."""
    tot_items = n_sottili_eq + n_spessi_eq + n_cop_medie + n_cop_pesanti

    def only_thin_1():   return (n_sottili_eq == 1 and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)
    def only_thin_1_2(): return (n_sottili_eq in (1, 2) and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)

    # 0) Indifferente → nessuna modifica
    if superficie_short == "Indifferente":
        return fatt

    # 1) Isolante (corretto: nudo=1.10; 1 sottile=1.20; altrimenti +0.10)
    if superficie_short == "Isolante":
        if tot_items == 0:              # nudo
            return 1.10
        elif only_thin_1():             # solo 1 sottile (indumento o lenzuolo)
            return 1.20
        else:
            return fatt + 0.10

    # 2) Molto isolante
    if superficie_short == "Molto isolante":
        if tot_items == 0:              # nudo
            return 1.30
        if only_thin_1_2():             # solo 1–2 sottili
            return fatt + 0.30
        else:
            return fatt + 0.10

    # 3) Conduttivo
    if superficie_short == "Conduttivo":
        if tot_items == 0:              # nudo
            return 0.75
        elif only_thin_1():             # solo 1 sottile
            return fatt - 0.20
        else:
            return fatt - 0.10

    # 4) Molto conduttivo (solo nudo + asciutto): override con correnti (precedenza assoluta)
    if superficie_short == "Molto conduttivo":
        if not (stato == "asciutto" and vestizione == "nudo e scoperto"):
            return fatt  # guard-rail
        return 0.50 if correnti_aria == "con correnti d'aria" else 0.55

    # 5) Foglie umide (>= 2 cm)
    if superficie_short == "Foglie umide (>= 2 cm)":
        if tot_items == 0:
            return 1.20
        if only_thin_1_2():
            return fatt + 0.20
        else:
            return fatt + 0.10

    # 6) Foglie secche (>= 2 cm)
    if superficie_short == "Foglie secche (>= 2 cm)":
        if tot_items == 0:
            return 1.50
        if only_thin_1_2():
            return fatt + 0.30
        else:
            return fatt + 0.20

    return fatt

def applica_correnti(
    fatt, stato, vestizione, superficie_short, correnti_aria,
    n_sottili_eq, n_spessi_eq, fattore_vestiti_coperte
):
    """
    Precedenze correnti:
    - Visibilità: se fattore_vestiti_coperte >= 1.2 → correnti irrilevanti ("/").
    - Molto conduttivo: gestito in superficie (precedenza assoluta).
    - Bagnato + correnti: override a 0.7/0.8/0.9 secondo gli strati.
    - Nudo + asciutto: SOLO se superficie = Indifferente → 1.00 / 0.75.
    - Vestizione minima + correnti: fatt - 0.10.
    """
    # Correnti nascoste o irrilevanti
    if correnti_aria == "/":
        return fatt, False

    # Molto conduttivo già trattato a monte
    if superficie_short == "Molto conduttivo":
        return fatt, True

    # 2) Corpo bagnato + correnti → override diretto
    if stato == "bagnato" and correnti_aria == "con correnti d'aria":
        # nudo o 1 sottile -> 0.7
        if (vestizione == "nudo e scoperto") or (n_sottili_eq == 1 and n_spessi_eq == 0):
            return 0.70, True
        # 2 sottili oppure 1 spesso -> 0.8
        if (n_sottili_eq == 2 and n_spessi_eq == 0) or (n_spessi_eq == 1 and n_sottili_eq == 0):
            return 0.80, True
        # 2 spessi -> 0.9 (o più)
        if n_spessi_eq >= 2:
            return 0.90, True
        return fatt, False

    # 3) Nudo + asciutto → SOLO su superficie Indifferente
    if stato == "asciutto" and vestizione == "nudo e scoperto" and superficie_short == "Indifferente":
        return (0.75, True) if correnti_aria == "con correnti d'aria" else (1.00, True)

    # 4) Vestizione minima + correnti: -0.10
    # condizioni: 1-2 sottili (e 0 spessi) OPPURE 1 spesso (e 0 sottili)
    vestizione_minima = (
        (n_sottili_eq in (1, 2) and n_spessi_eq == 0) or
        (n_spessi_eq == 1 and n_sottili_eq == 0)
    )
    if vestizione_minima and correnti_aria == "con correnti d'aria":
        return fatt - 0.10, False

    return fatt, False

def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    """Stub Tabella 2: sostituisci con lookup reale quando pronto."""
    if f_base < 1.4:
        return f_base
    approx = f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return clamp(approx)

# =========================
# UI reattiva (senza form): si aggiorna ad ogni modifica
# =========================
st.subheader("Input")

# Peso
peso = st.number_input("Peso corporeo (kg)", min_value=10.0, max_value=200.0, value=70.0, step=0.5)

# ---- Condizione del corpo (UI compatta, senza titolo) ----
# Manteniamo valori interni invariati tramite mappatura
_stato_options = [("asciutto", "corpo asciutto"),
                  ("bagnato", "corpo bagnato"),
                  ("in acqua", "corpo immerso")]
stato = st.selectbox(
    "",
    _stato_options,
    index=0,
    format_func=lambda x: x[1],
    label_visibility="collapsed",
    
)[0]  # prendi il valore interno ("asciutto"/"bagnato"/"in acqua")

# Vestizione
vestizione = st.selectbox("Vestizione", ["nudo e scoperto", "vestito e/o coperto"], index=0)

# Caso: in acqua → UI minima e stop
if stato == "in acqua":
    acqua_tipo = st.selectbox("Condizioni dell'acqua", ["acqua stagnante", "acqua corrente"], index=0)
    fattore_finale = 0.35 if acqua_tipo == "acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# Se vestito/coperto → campi ACCORPATI
n_sottili_eq = n_spessi_eq = 0
n_cop_medie = n_cop_pesanti = 0
if vestizione == "vestito e/o coperto":
    n_sottili_eq = st.slider("Strati SOTTILI (indumenti o lenzuola sottili)", 0, 8, 0)
    n_spessi_eq  = st.slider("Strati SPESSI (indumenti o lenzuola spesse)", 0, 6, 0)
    n_cop_medie  = st.slider("Coperte MEDIE", 0, 5, 0)
    n_cop_pesanti= st.slider("Coperte PESANTI", 0, 5, 0)

# Fattore solo da vestiti/lenzuola (serve anche per visibilità correnti)
fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
)

# ---- Correnti d'aria (UI compatta, senza titolo) ----
correnti_aria = "/"
if fattore_vestiti_coperte < 1.2:
    correnti_aria = st.selectbox(
        "",
        ["senza correnti d'aria", "con correnti d'aria"],
        index=0,
        label_visibility="collapsed",
        
    )

# Superficie (opzioni condizionali)
opts_appoggio = ["Indifferente", "Isolante", "Molto isolante", "Conduttivo"]
if stato == "asciutto" and vestizione == "nudo e scoperto":
    opts_appoggio.append("Molto conduttivo")
if stato == "asciutto":
    opts_appoggio += ["Foglie umide (>= 2 cm)", "Foglie secche (>= 2 cm)"]
superficie_short = st.selectbox("Superficie di appoggio", opts_appoggio, index=0, label_visibility="collapsed", help=HELP_SUPERFICIE)

# =========================
# Pipeline di calcolo (reattiva)
# =========================
# 1) Parto dal fattore vestiti/coperte
fattore = float(fattore_vestiti_coperte)

# 2) Regole superficie (Molto conduttivo ha precedenza e usa correnti)
fattore = applica_regole_superficie(
    fattore, superficie_short, stato, correnti_aria, vestizione,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
)

# 3) Correnti d’aria (fuori dal caso ‘Molto conduttivo’)
fattore, correnti_override = applica_correnti(
    fatt=fattore, stato=stato, vestizione=vestizione, superficie_short=superficie_short,
    correnti_aria=correnti_aria, n_sottili_eq=n_sottili_eq, n_spessi_eq=n_spessi_eq,
    fattore_vestiti_coperte=fattore_vestiti_coperte
)

# 4) Regola generale bagnato: se fattore_vestiti_coperte < 1.2 e NON c'è override forte 0.7/0.8/0.9 → -0.3
if stato == "bagnato" and fattore_vestiti_coperte < 1.2 and not correnti_override:
    fattore -= 0.30

# 5) Clamp sicurezza
if math.isnan(fattore):
    fattore = 1.0
fattore = clamp(fattore)

# 6) Correzione peso (Tabella 2 - stub)
fattore_finale = correzione_peso_tabella2(fattore, float(peso))

# =========================
# Output
# =========================
st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
