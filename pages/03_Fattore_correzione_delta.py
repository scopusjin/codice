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
    return float(fatt)

def is_poco_vestito(fattore_vestiti_coperte: float) -> bool:
    return (fattore_vestiti_coperte > 1.0 and fattore_vestiti_coperte < 1.2)

# =========================
# Regole superficie
# =========================
def applica_regole_superficie(
    fatt, superficie, stato, vestizione,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
):
    tot_items = n_sottili_eq + n_spessi_eq + n_cop_medie + n_cop_pesanti
    def only_thin_1():   return (n_sottili_eq == 1 and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)
    def only_thin_1_2(): return (n_sottili_eq in (1, 2) and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)

    if superficie == "Pavimento di casa, terreno o prato asciutti, asfalto, legno":
        return fatt

    if superficie == "Materasso o tappeto spesso":
        if tot_items == 0:
            return 1.10
        elif only_thin_1():
            return 1.20
        else:
            return fatt + 0.10

    if superficie == "Divano imbottito, sacco a pelo tecnico, polistirolo":
        if tot_items == 0:
            return 1.30
        if only_thin_1_2():
            return fatt + 0.30
        else:
            return fatt + 0.10

    if superficie == "Cemento, pietra, PVC, pavimento esterno/cantina, piano metallico (al chiuso)":
        if tot_items == 0:
            return 0.75
        elif only_thin_1():
            return fatt - 0.20
        else:
            return fatt - 0.10

    if superficie == "Superficie metallica spessa (all’aperto)":
        if not (stato == "asciutto" and vestizione == "nudo e scoperto"):
            return fatt
        return 0.55

    if superficie == "Strato di foglie umide (≥2 cm)":
        if tot_items == 0:
            return 1.20
        if only_thin_1_2():
            return fatt + 0.20
        else:
            return fatt + 0.10

    if superficie == "Strato di foglie secche (≥2 cm)":
        if tot_items == 0:
            return 1.50
        if only_thin_1_2():
            return fatt + 0.30
        else:
            return fatt + 0.20

    return fatt

# =========================
# Correnti d'aria
# =========================
def applica_correnti(
    fatt, stato, vestizione, superficie, correnti_presenti: bool,
    n_sottili_eq, n_spessi_eq, fattore_vestiti_coperte
):
    if not correnti_presenti:
        return fatt, False

    if stato == "bagnato":
        if vestizione == "nudo e scoperto":
            return 0.7, True
        if n_sottili_eq == 1:
            return 0.8, True
        if (n_sottili_eq == 2) or (n_spessi_eq == 1):
            return 0.9, True
        if (n_spessi_eq == 2) or (n_sottili_eq in (3,4)):
            return 1.0, True
        if n_spessi_eq > 2 or n_sottili_eq > 4 or n_cop_medie>0 or n_cop_pesanti>0:
            return 1.1, True
        return fatt, False

    if stato == "asciutto":
        nudo_asciutto = (vestizione == "nudo e scoperto")
        poco_vestito  = is_poco_vestito(fattore_vestiti_coperte)

        if superficie == "Pavimento di casa, terreno o prato asciutti, asfalto, legno":
            if nudo_asciutto: return fatt * 0.75, True
            if poco_vestito:  return fatt * 0.80, True

        elif superficie == "Materasso o tappeto spesso":
            if nudo_asciutto: return fatt * 0.80, True
            if poco_vestito:  return fatt * 0.85, True

        elif superficie == "Divano imbottito, sacco a pelo tecnico, polistirolo":
            if nudo_asciutto or poco_vestito: return fatt * 0.90, True

        elif superficie == "Cemento, pietra, PVC, pavimento esterno/cantina, piano metallico (al chiuso)":
            if nudo_asciutto or poco_vestito: return fatt * 0.75, True

        elif superficie == "Superficie metallica spessa (all’aperto)":
            return fatt * 0.75, True

    return fatt, False

# =========================
# Correzione peso (stub Tabella 2)
# =========================
def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    if f_base < 1.4:
        return f_base
    approx = f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return clamp(approx)

# =========================
# UI reattiva
# =========================
st.subheader("Input")

peso = st.number_input("Peso corporeo (kg)", min_value=10.0, max_value=200.0, value=70.0, step=0.5)

stato_label = st.segmented_control(
    options=["Corpo asciutto", "Bagnato", "Immerso"],
    default="Corpo asciutto",
)
stato = "asciutto" if stato_label == "Corpo asciutto" else ("bagnato" if stato_label == "Bagnato" else "in acqua")

# caso in acqua → UI minima
if stato == "in acqua":
    acqua_tipo = st.segmented_control(
        options=["in acqua stagnante", "in acqua corrente"],
        default="in acqua stagnante",
    )
    fattore_finale = 0.35 if acqua_tipo == "in acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# switch
c1, c2 = st.columns(2)
with c1:
    toggle_vestito = st.toggle("Vestito/coperto?", value=False)
with c2:
    toggle_correnti = st.toggle("Correnti d'aria presenti?", value=False)
correnti_presenti = bool(toggle_correnti)
vestizione = "vestito e/o coperto" if toggle_vestito else "nudo e scoperto"

# superficie
opts_appoggio = [
    "Pavimento di casa, terreno o prato asciutti, asfalto, legno",
    "Materasso o tappeto spesso",
    "Divano imbottito, sacco a pelo tecnico, polistirolo",
    "Cemento, pietra, PVC, pavimento esterno/cantina, piano metallico (al chiuso)",
]
if stato == "asciutto" and vestizione == "nudo e scoperto":
    opts_appoggio.append("Superficie metallica spessa (all’aperto)")
if stato == "asciutto":
    opts_appoggio += ["Strato di foglie umide (≥2 cm)", "Strato di foglie secche (≥2 cm)"]

superficie = st.selectbox("Superficie di appoggio", opts_appoggio, index=0)

# vestiti/coperte
n_sottili_eq = n_spessi_eq = n_cop_medie = n_cop_pesanti = 0
if toggle_vestito:
    with st.expander(" ", expanded=True):
        st.caption("Indicare il numero di strati sul corpo. Contano solo quelli che coprono la parte bassa del tronco.")
        c1e, c2e = st.columns(2)
        with c1e:
            n_sottili_eq = st.slider("Strati leggeri (indumenti o teli sottili)", 0, 8, 0)
            n_cop_medie  = st.slider("Coperte di medio spessore", 0, 5, 0)
        with c2e:
            n_spessi_eq  = st.slider("Strati pesanti (indumenti o teli spessi)", 0, 6, 0)
            n_cop_pesanti= st.slider("Coperte pesanti", 0, 5, 0)

# =========================
# Pipeline calcolo
# =========================
fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)
fattore = applica_regole_superficie(fattore_vestiti_coperte, superficie, stato, vestizione, n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)
fattore, correnti_override = applica_correnti(fattore, stato, vestizione, superficie, correnti_presenti, n_sottili_eq, n_spessi_eq, fattore_vestiti_coperte)

if stato == "bagnato" and fattore > 1.2:
    fattore = 1.2

if math.isnan(fattore):
    fattore = 1.0
fattore = clamp(fattore)

fattore_finale = correzione_peso_tabella2(fattore, float(peso))

# =========================
# Output
# =========================
st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
