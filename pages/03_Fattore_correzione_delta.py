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
    Regole VOLUTE:
    - Base 2.0 se >=1 coperta pesante (+0.3 per ciascuna pesante extra, +0.2 per ciascuna media)
    - Altrimenti base 1.8 se >=1 coperta media (+0.2 per ciascuna media extra)
    - Altrimenti base 1.0
    - +0.075 per ogni strato sottile (indumento o lenzuolo sottile)
    - +0.15  per ogni strato spesso  (indumento pesante o lenzuolo spesso)
    - CAP: se non ci sono coperte, valore massimo = 1.8
    """
    if n_cop_pesanti > 0:
        fatt = 2.0 + max(0, n_cop_pesanti - 1) * 0.3 + n_cop_medie * 0.2
        fatt += n_sottili_eq * 0.075
        fatt += n_spessi_eq * 0.15
    elif n_cop_medie > 0:
        fatt = 1.8 + max(0, n_cop_medie - 1) * 0.2
        fatt += n_sottili_eq * 0.075
        fatt += n_spessi_eq * 0.15
    else:
        fatt = 1.0 + n_sottili_eq * 0.075 + n_spessi_eq * 0.15
        if fatt > 1.8:
     #   if fatt > 1.8:
     #       fatt = 1.8  # cap se solo indumenti/lenzuola

    return float(fatt)


def is_vestizione_minima(n_sottili_eq: int, n_spessi_eq: int) -> bool:
    # 1–2 sottili (0 spessi) oppure 1 spesso (0 sottili)
    return ((n_sottili_eq in (1, 2) and n_spessi_eq == 0) or
            (n_spessi_eq == 1 and n_sottili_eq == 0))

def is_poco_vestito(fattore_vestiti_coperte: float) -> bool:
    # come da richiesta: >1 e <1.2
    return (fattore_vestiti_coperte > 1.0 and fattore_vestiti_coperte < 1.2)

def applica_regole_superficie(
    fatt, superficie_short, stato, vestizione,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
):
    """Regole di appoggio (senza gestire qui le correnti)."""
    tot_items = n_sottili_eq + n_spessi_eq + n_cop_medie + n_cop_pesanti

    def only_thin_1():   return (n_sottili_eq == 1 and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)
    def only_thin_1_2(): return (n_sottili_eq in (1, 2) and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)

    # 0) Indifferente → nessuna modifica
    if superficie_short == "Indifferente":
        return fatt

    # 1) Isolante
    if superficie_short == "Isolante":
        if tot_items == 0:              # nudo
            return 1.10
        elif only_thin_1():             # 1 sottile
            return 1.20
        else:
            return fatt + 0.10

    # 2) Molto isolante
    if superficie_short == "Molto isolante":
        if tot_items == 0:              # nudo
            return 1.30
        if only_thin_1_2():             # 1–2 sottili
            return fatt + 0.30
        else:
            return fatt + 0.10

    # 3) Conduttivo
    if superficie_short == "Conduttivo":
        if tot_items == 0:              # nudo
            return 0.75
        elif only_thin_1():
            return fatt - 0.20
        else:
            return fatt - 0.10

    # 4) Molto conduttivo (solo nudo + asciutto)
    if superficie_short == "Molto conduttivo":
        if not (stato == "asciutto" and vestizione == "nudo e scoperto"):
            return fatt  # guard-rail
        return 0.55  # le correnti si applicano DOPO (−25% richiesto)

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
    fatt, stato, vestizione, superficie_short, correnti_presenti: bool,
    n_sottili_eq, n_spessi_eq, fattore_vestiti_coperte
):
    """
    Correnti d'aria:
    - BAGNATO + correnti: override a 0.7/0.8/0.9 secondo gli strati (come prima).
    - ASCIUTTO + correnti: riduzioni per superficie come da specifica:
        * Indifferente:   nudo −25% ; poco vestito −20%
        * Isolante:       nudo −20% ; poco vestito −15%
        * Molto isolante: nudo/poco vestito −10%
        * Conduttivo:     nudo/poco vestito −25%
        * Molto conduttivo: nudo −25%  (partendo da 0.55)
    - Altrimenti: invariato.
    """
    if not correnti_presenti:
        return fatt, False

    # 1) Corpo bagnato: override forte
    if stato == "bagnato":
        # nudo o 1 sottile -> 0.7
        if (vestizione == "nudo e scoperto") or (n_sottili_eq == 1 and n_spessi_eq == 0):
            return 0.70, True
        # 2 sottili oppure 1 spesso -> 0.8
        if (n_sottili_eq == 2 and n_spessi_eq == 0) or (n_spessi_eq == 1 and n_sottili_eq == 0):
            return 0.80, True
        # >=2 spessi -> 0.9
        if n_spessi_eq >= 2:
            return 0.90, True
        return fatt, False

    # 2) Corpo asciutto: applica riduzioni percentuali
    nudo_asciutto = (stato == "asciutto" and vestizione == "nudo e scoperto")
    poco_vestito  = (stato == "asciutto" and is_poco_vestito(fattore_vestiti_coperte))

    if stato == "asciutto":
        if superficie_short == "Indifferente":
            if nudo_asciutto:
                return fatt * 0.75, True
            if poco_vestito:
                return fatt * 0.80, True

        elif superficie_short == "Isolante":
            if nudo_asciutto:
                return fatt * 0.80, True
            if poco_vestito:
                return fatt * 0.85, True

        elif superficie_short == "Molto isolante":
            if nudo_asciutto or poco_vestito:
                return fatt * 0.90, True

        elif superficie_short == "Conduttivo":
            if nudo_asciutto or poco_vestito:
                return fatt * 0.75, True

        elif superficie_short == "Molto conduttivo":
            # solo nudo è ammesso da UI; −25% richiesto
            return fatt * 0.75, True

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

# ---- Condizione del corpo (etichette “corpo …”) ----
_stato_options = [("asciutto", "corpo asciutto"),
                  ("bagnato", "corpo bagnato"),
                  ("in acqua", "corpo immerso")]
stato = st.selectbox(
    "Condizione del corpo",
    _stato_options,
    index=0,
    format_func=lambda x: x[1],
)[0]  # valore interno

# ---- Switch affiancati ----
c1, c2 = st.columns(2)
with c1:
    toggle_vestito = st.toggle("Vestito/coperto?", value=False)  # <— fix sintassi
with c2:
    toggle_correnti = st.toggle("Correnti d'aria presenti?", value=False, disabled=(stato == "in acqua"))
correnti_presenti = bool(toggle_correnti)

vestizione = "vestito e/o coperto" if toggle_vestito else "nudo e scoperto"

# ---- Expander (senza titolo leggibile) per strati/coperte ----
n_sottili_eq = n_spessi_eq = 0
n_cop_medie = n_cop_pesanti = 0
if toggle_vestito:
    with st.expander(" ", expanded=True):  # U+2003 em-space: appare senza testo
        c1e, c2e = st.columns(2)
        with c1e:
            n_sottili_eq = st.slider("Strati leggeri (indumenti o lenzuola sottili)", 0, 8, 0)
            n_cop_medie  = st.slider("Coperte di medio spessore", 0, 5, 0)
        with c2e:
            n_spessi_eq  = st.slider("Strati pesanti (indumenti o lenzuola spesse)", 0, 6, 0)
            n_cop_pesanti= st.slider("Coperte pesanti", 0, 5, 0)

# Caso: in acqua → UI minima e stop
if stato == "in acqua":
    acqua_tipo = st.selectbox("Condizioni dell'acqua", ["acqua stagnante", "acqua corrente"], index=0)
    fattore_finale = 0.35 if acqua_tipo == "acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# Fattore solo da vestiti/lenzuola (serve anche per regole 'poco vestito')
fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
)

# Superficie (opzioni condizionali)
opts_appoggio = ["Indifferente", "Isolante", "Molto isolante", "Conduttivo"]
if stato == "asciutto" and vestizione == "nudo e scoperto":
    opts_appoggio.append("Molto conduttivo")
if stato == "asciutto":
    opts_appoggio += ["Foglie umide (>= 2 cm)", "Foglie secche (>= 2 cm)"]
superficie_short = st.selectbox("Superficie di appoggio", opts_appoggio, index=0, help=HELP_SUPERFICIE)

# =========================
# Pipeline di calcolo (reattiva)
# =========================
# 1) Base: fattore da vestiti/coperte
fattore = float(fattore_vestiti_coperte)

# 2) Regole superficie (Molto conduttivo restituisce 0.55 per nudo asciutto)
fattore = applica_regole_superficie(
    fattore, superficie_short, stato, vestizione,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
)

# 3) Correnti d’aria (bagnato = override; asciutto = percentuali richieste)
fattore, correnti_override = applica_correnti(
    fatt=fattore, stato=stato, vestizione=vestizione, superficie_short=superficie_short,
    correnti_presenti=correnti_presenti,
    n_sottili_eq=n_sottili_eq, n_spessi_eq=n_spessi_eq,
    fattore_vestiti_coperte=fattore_vestiti_coperte
)

# 4) Regola generale bagnato: se poco vestito (<1.2) e NON c'è override forte → -0.3
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
