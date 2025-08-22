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
    - +0.075 per ogni strato sottile (indumento o telo sottile)
    - +0.15  per ogni strato spesso  (indumento pesante o telo spesso)
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
    return float(fatt)

def is_poco_vestito(fattore_vestiti_coperte: float) -> bool:
    # come da richiesta: >1 e <1.2
    return (fattore_vestiti_coperte > 1.0 and fattore_vestiti_coperte < 1.2)

def applica_correnti(fatt, stato, vestizione, superficie_short, correnti_presenti: bool,
                     n_sottili_eq, n_spessi_eq, fattore_vestiti_coperte):
    """Regole correnti d'aria."""
    if not correnti_presenti:
        return fatt, False

    # Corpo bagnato
    if stato == "Bagnato":
        # 🌊 regole bagnato con correnti
        if vestizione == "nudo e scoperto":
            return 0.7, True
        if n_sottili_eq == 1:
            return 0.8, True
        if (n_spessi_eq == 1 and n_sottili_eq == 0) or (n_sottili_eq == 2 and n_spessi_eq == 0):
            return 0.9, True
        if (n_spessi_eq == 2) or (3 <= n_sottili_eq <= 4):
            return 1.0, True
        if (n_spessi_eq > 2) or (n_sottili_eq > 4):
            return 1.1, True
        return fatt, False

    # Corpo asciutto
    if stato == "Corpo asciutto":
        if superficie_short == "Pavimento di casa, terreno o prato asciutti, asfalto, legno":
            if vestizione == "nudo e scoperto":
                return fatt * 0.75, True
            if is_poco_vestito(fattore_vestiti_coperte):
                return fatt * 0.80, True
        elif superficie_short == "Materasso o tappeto spesso":
            if vestizione == "nudo e scoperto":
                return fatt * 0.80, True
            if is_poco_vestito(fattore_vestiti_coperte):
                return fatt * 0.85, True
        elif superficie_short == "Divano imbottito, sacco a pelo tecnico, polistirolo":
            if vestizione == "nudo e scoperto" or is_poco_vestito(fattore_vestiti_coperte):
                return fatt * 0.90, True
        elif superficie_short == "Cemento, pietra, PVC, pavimento esterno/cantina, piano metallico (al chiuso)":
            if vestizione == "nudo e scoperto" or is_poco_vestito(fattore_vestiti_coperte):
                return fatt * 0.75, True
        elif superficie_short == "Superficie metallica spessa (all’aperto)":
            return fatt * 0.75, True
    return fatt, False

def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    """Stub Tabella 2: sostituisci con lookup reale quando pronto."""
    if f_base < 1.4:
        return f_base
    approx = f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return clamp(approx)

# =========================
# UI
# =========================
st.subheader("Input")

# Peso
peso = st.number_input("Peso corporeo (kg)", min_value=10.0, max_value=200.0, value=70.0, step=0.5)

# Condizione corpo
stato_label = st.radio(
    "\u200B",
    options=["Corpo asciutto", "Bagnato", "Immerso"],
    index=0,
    horizontal=True,
)

# Se Immerso
if stato_label == "Immerso":
    acqua_tipo = st.radio(
        "\u200B",
        options=["In acqua stagnante", "In acqua corrente"],
        index=0,
        horizontal=True,
    )
    fattore_finale = 0.35 if acqua_tipo == "In acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# Selezione correnti (solo se non Immerso)
toggle_correnti = st.toggle("Correnti d'aria presenti?", value=False)
correnti_presenti = bool(toggle_correnti)

# Selezione superficie (solo se asciutto)
superficie_short = None
if stato_label == "Corpo asciutto":
    superficie_short = st.selectbox(
        "Superficie di appoggio",
        [
            "Pavimento di casa, terreno o prato asciutti, asfalto, legno",
            "Materasso o tappeto spesso",
            "Divano imbottito, sacco a pelo tecnico, polistirolo",
            "Cemento, pietra, PVC, pavimento esterno/cantina, piano metallico (al chiuso)",
            "Superficie metallica spessa (all’aperto)",
            "Strato di foglie umide (≥2 cm)",
            "Strato di foglie secche (≥2 cm)",
        ],
        index=0,
    )

# Vestizione/coperte (no se Immerso; ridotta se Bagnato)
vestizione = "nudo e scoperto"
n_sottili_eq = n_spessi_eq = 0
n_cop_medie = n_cop_pesanti = 0

toggle_vestito = st.toggle("Vestito/coperto?", value=False, disabled=(stato_label == "Immerso"))
if toggle_vestito:
    vestizione = "vestito e/o coperto"
    with st.expander(" ", expanded=True):
        st.caption("Indicare il numero di strati sul corpo. Hanno influenza solo quelli che coprono la parte bassa del tronco.")
        c1e, c2e = st.columns(2)
        with c1e:
            n_sottili_eq = st.slider("Strati leggeri (indumenti o teli sottili)", 0, 8, 0)
            if stato_label == "Corpo asciutto":
                n_cop_medie = st.slider("Coperte di medio spessore", 0, 5, 0)
        with c2e:
            n_spessi_eq = st.slider("Strati pesanti (indumenti o teli spessi)", 0, 6, 0)
            if stato_label == "Corpo asciutto":
                n_cop_pesanti = st.slider("Coperte pesanti", 0, 5, 0)

# =========================
# Calcolo fattore
# =========================
fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
)

fattore = float(fattore_vestiti_coperte)

# Correnti
fattore, _ = applica_correnti(
    fatt=fattore, stato=stato_label, vestizione=vestizione, superficie_short=superficie_short,
    correnti_presenti=correnti_presenti,
    n_sottili_eq=n_sottili_eq, n_spessi_eq=n_spessi_eq,
    fattore_vestiti_coperte=fattore_vestiti_coperte
)

# Cap per bagnato
if stato_label == "Bagnato" and fattore > 1.2:
    fattore = 1.2

# Clamp sicurezza
if math.isnan(fattore):
    fattore = 1.0
fattore = clamp(fattore)

# Correzione peso
fattore_finale = correzione_peso_tabella2(fattore, float(peso))

# =========================
# Output
# =========================
st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
