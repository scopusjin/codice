# pages/03_Fattore_correzione_delta.py
# -*- coding: utf-8 -*-
import math
import pandas as pd
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
    "Indifferente = Pavimento/terreno/prato asciutto/asfalto · "
    "Isolante = Materasso/tappeto spesso · "
    "Molto isolante = Imbottitura pesante (sacco a pelo, polistirolo, divano imbottito) · "
    "Conduttivo = Cemento/pietra/PVC/esterno · "
    "Molto conduttivo = Superficie metallica spessa all'esterno (solo nudo asciutto) · "
    "Foglie umide/secche = strato ≥ 2 cm (solo se corpo asciutto)"
)

APP_APPOGGIO_MAP = {
    "Indifferente": "Pavimento di casa, terreno o prato asciutto, asfalto",
    "Isolante": "Materasso o tappeto spesso",
    "Molto isolante": "Imbottitura pesante (sacco a pelo tecnico, polistirolo, divano imbottito)",
    "Conduttivo": "Cemento, pietra, pavimentazione esterna, pavimento in PVC.",
    "Molto conduttivo": "Superficie metallica spessa, in ambiente esterno.",
    "Foglie umide (>= 2 cm)": "Adagiato su strato di foglie umide ≥ 2 cm",
    "Foglie secche (>= 2 cm)": "Adagiato su strato di foglie secche ≥ 2 cm",
}

# =========================
# Utility
# =========================
def clamp(x, lo=0.35, hi=3.0):
    return max(lo, min(hi, x))

def calcola_fattore_vestiti_coperte(n_sottili, n_spessi, n_lenz_plus, has_lenz_pp, n_cop_medie, n_cop_pesanti):
    if n_cop_pesanti > 0:
        fatt = 2.0 + max(0, n_cop_pesanti - 1) * 0.3 + n_cop_medie * 0.2
    elif n_cop_medie > 0:
        fatt = 1.8 + max(0, n_cop_medie - 1) * 0.2
    else:
        fatt = 1.0
    fatt += n_sottili * 0.075
    fatt += n_spessi * 0.15
    fatt += n_lenz_plus * 0.075
    if has_lenz_pp:
        fatt += 0.15
    return float(fatt)

def applica_regole_superficie(fatt, superficie_short, stato, correnti_aria, vestizione,
                              n_sottili, n_spessi, n_lenz_plus, has_lenz_pp, n_cop_medie, n_cop_pesanti):
    tot_items = n_sottili + n_spessi + n_lenz_plus + (1 if has_lenz_pp else 0) + n_cop_medie + n_cop_pesanti

    def only_thin_1():  return (n_sottili == 1 and tot_items == 1)
    def only_sheet_1(): return (n_lenz_plus == 1 and tot_items == 1)
    def only_thin_1_2(): return (n_sottili in (1, 2) and tot_items == n_sottili)
    def only_sheet_1_2(): return (n_lenz_plus in (1, 2) and tot_items == n_lenz_plus)

    if superficie_short == "Indifferente":
        return fatt
    if superficie_short == "Isolante":
        if tot_items == 0:
            return 1.10
        elif only_thin_1() or only_sheet_1():
            return 1.20
        else:
            return fatt + 0.10
    if superficie_short == "Molto isolante":
        if tot_items == 0:
            return 1.30
        if only_thin_1_2() or only_sheet_1_2():
            return fatt + 0.30
        else:
            return fatt + 0.10
    if superficie_short == "Conduttivo":
        if tot_items == 0:
            return 0.75
        elif only_thin_1() or only_sheet_1():
            return fatt - 0.20
        else:
            return fatt - 0.10
    if superficie_short == "Molto conduttivo":
        if not (stato == "asciutto" and vestizione == "nudo e scoperto"):
            return fatt
        return 0.50 if correnti_aria == "con correnti d'aria" else 0.55
    if superficie_short == "Foglie umide (>= 2 cm)":
        if tot_items == 0:
            return 1.20
        if only_thin_1_2() or only_sheet_1_2():
            return fatt + 0.20
        else:
            return fatt + 0.10
    if superficie_short == "Foglie secche (>= 2 cm)":
        if tot_items == 0:
            return 1.50
        if only_thin_1_2() or only_sheet_1_2():
            return fatt + 0.30
        else:
            return fatt + 0.20
    return fatt

def applica_correnti(fatt, stato, vestizione, superficie_short, correnti_aria,
                     n_sottili, n_spessi, n_lenz_plus, has_lenz_pp, fattore_vestiti_coperte):
    if correnti_aria == "/":
        return fatt, False
    if superficie_short == "Molto conduttivo":
        return fatt, True
    spessi_equiv = n_spessi + (1 if has_lenz_pp else 0)
    if stato == "bagnato" and correnti_aria == "con correnti d'aria":
        if vestizione == "nudo e scoperto" or (n_sottili == 1 and spessi_equiv == 0 and n_lenz_plus == 0):
            return 0.70, True
        if (n_sottili == 2 and spessi_equiv == 0) or (spessi_equiv == 1 and n_sottili == 0):
            return 0.80, True
        if spessi_equiv >= 2:
            return 0.90, True
        return fatt, False
    if stato == "asciutto" and vestizione == "nudo e scoperto" and superficie_short == "Indifferente":
        return (0.75, True) if correnti_aria == "con correnti d'aria" else (1.00, True)
    vestizione_minima = (
        (n_sottili in (1, 2) and n_spessi == 0 and not has_lenz_pp and n_lenz_plus == 0) or
        (n_lenz_plus in (1, 2) and n_sottili == 0 and n_spessi == 0 and not has_lenz_pp) or
        (n_spessi == 1 and n_sottili == 0 and n_lenz_plus == 0 and not has_lenz_pp) or
        (has_lenz_pp and n_sottili == 0 and n_spessi == 0 and n_lenz_plus == 0)
    )
    if vestizione_minima and correnti_aria == "con correnti d'aria":
        return fatt - 0.10, False
    return fatt, False

def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    if f_base < 1.4:
        return f_base
    approx = f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return clamp(approx)

# =========================
# MASCHERA UNICA (st.form)
# =========================
with st.form("maschera_input"):
    peso = st.number_input("Peso corporeo (kg)", min_value=10.0, max_value=200.0, value=70.0, step=0.5)
    stato = st.selectbox("Condizioni del corpo", ["asciutto", "bagnato", "in acqua"], index=0, help=HELP_CONDIZIONE)
    vestizione = st.selectbox("Vestizione", ["nudo e scoperto", "vestito e/o coperto"], index=0)

    if stato == "in acqua":
        acqua_tipo = st.selectbox("Condizioni dell'acqua", ["acqua stagnante", "acqua corrente"], index=0)
        submit = st.form_submit_button("Aggiorna")
        if submit:
            fattore_finale = 0.35 if acqua_tipo == "acqua corrente" else 0.50
            st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
        st.stop()

    n_sottili = n_spessi = n_lenz_plus = n_cop_medie = n_cop_pesanti = 0
    has_lenz_pp = False
    if vestizione == "vestito e/o coperto":
        with st.expander("Vestiti e coperte", expanded=False):
            n_sottili = st.slider("Strati sottili", 0, 8, 0)
            n_spessi = st.slider("Strati spessi", 0, 6, 0)
            n_lenz_plus = st.slider("Lenzuola leggere (Lenz.+)", 0, 6, 0)
            n_cop_medie = st.slider("Coperte medie", 0, 5, 0)
            n_cop_pesanti = st.slider("Coperte pesanti", 0, 5, 0)
            has_lenz_pp = st.checkbox("Lenzuolo spesso (Lenz.++)")

    fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(
        n_sottili, n_spessi, n_lenz_plus, has_lenz_pp, n_cop_medie, n_cop_pesanti
    )

    correnti_aria = "/"
    if fattore_vestiti_coperte < 1.2:
        correnti_aria = st.selectbox("Correnti d’aria", ["senza correnti", "con correnti d'aria"], index=0, help=HELP_CORRENTI_ARIA)

    opts_appoggio = ["Indifferente", "Isolante", "Molto isolante", "Conduttivo"]
    if stato == "asciutto" and vestizione == "nudo e scoperto":
        opts_appoggio.append("Molto conduttivo")
    if stato == "asciutto":
        opts_appoggio += ["Foglie umide (>= 2 cm)", "Foglie secche (>= 2 cm)"]
    superficie_short = st.selectbox("Superficie di appoggio", opts_appoggio, index=0, help=HELP_SUPERFICIE)

    submit = st.form_submit_button("Aggiorna")

if submit:
    fattore = float(fattore_vestiti_coperte)
    fattore = applica_regole_superficie(fattore, superficie_short, stato, correnti_aria,
                                        vestizione, n_sottili, n_spessi, n_lenz_plus,
                                        has_lenz_pp, n_cop_medie, n_cop_pesanti)
    fattore, correnti_override = applica_correnti(fatt, stato, vestizione, superficie_short, correnti_aria,
                                                  n_sottili, n_spessi, n_lenz_plus,
                                                  has_lenz_pp, fattore_vestiti_coperte)
    if stato == "bagnato" and fattore_vestiti_coperte < 1.2 and not correnti_override:
        fattore -= 0.30
    if math.isnan(fattore):
        fattore = 1.0
    fattore = clamp(fattore)
    fattore_finale = correzione_peso_tabella2(fattore, float(peso))
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")

