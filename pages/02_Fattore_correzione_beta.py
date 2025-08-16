# pages/02_Fattore_correzione_beta.py
# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

# =========================================
# Config pagina
# =========================================
st.set_page_config(
    page_title="Fattore di correzione (beta)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Fattore di correzione — beta")
st.caption("Modalità Tabella (originale) + Modalità Formula (senza tabella). La correzione per il peso (Tabella 2) resta applicata.")

# =========================================
# HELP (testi di guida) – invariati
# =========================================
HELP_COPERTE = (
    "**Tenerne conto solo se coprono la parte bassa di torace/addome**.   "
    "**Lenzuolo +** = telo sottile/1-2 lenzuola;   "
    "**Lenzuolo ++** = lenzuolo invernale/copriletto leggero;   "
    "**Coperta** = coperta mezza stagione/ sacco mortuario;   "
    "**Coperta +** = coperta pesante/ mantellina termica;   "
    "**Coperta ++** = coperta molto pesante/ più coperte medie;   "
    "**Coperta +++** = coperta imbottita pesante (es piumino invernale);   "
    "**Coperta ++++** = molti strati di coperte;   "
    "**Strato di foglie di medio spessore** = foglie su corpo/vestiti;   "
    "**Spesso strato di foglie** = strato spesso di foglie."
)
HELP_VESTITI = (
    "**Tenere conto solo degli indumenti che coprono la parte bassa di torace/addome**.   "
    "**Strati sottili** = t-shirt, camicia, maglia leggera;    "
    "**Strati spessi** = maglione, felpa in pile, giubbino;   "
    "**˃ strati** = ˃4 sottili o ˃2 spessi;   "
    "**˃˃ strati** = molti strati pesanti."
)
HELP_SUPERFICIE = (
    "**Indifferente** = pavimento di casa/parquet, prato o terreno asciutto, asfalto;   "
    "**Isolante** = materasso, tappeto spesso;   "
    "**Molto isolante** = polistirolo, sacco a pelo tecnico, divano imbottito;   "
    "**Conduttivo** = cemento, pietra, pavimento in PVC, pavimentazione esterna;   "
    "**Molto conduttivo** = superficie metallica spessa all’esterno;   "
    "**Foglie umide/secche (≥2 cm)** = adagiato su strato di foglie"
)

# =========================================
# Cache caricamento Tabelle 1/2 (per modalità Tabella e per correzione peso)
# =========================================
@st.cache_data
def load_tabelle_correzione():
    """
    Colonne attese in Tabella 1:
      Ambiente, Vestiti, Coperte, Correnti, Superficie d'appoggio, Fattore
    Tabella 2: colonne con pesi (es. '50 kg', '70 kg', '90 kg' ...)
    """
    t1 = pd.read_excel("tabella rielaborata.xlsx", engine="openpyxl")
    t2 = pd.read_excel("tabella secondaria.xlsx", engine="openpyxl")
    t1["Fattore"] = pd.to_numeric(t1["Fattore"], errors="coerce")
    for col in ["Ambiente", "Vestiti", "Coperte", "Superficie d'appoggio", "Correnti"]:
        t1[col] = t1[col].astype(str).str.strip()
    return t1, t2

# =========================================
# Correzione peso (Tabella 2) – riuso identico
# =========================================
def applica_tabella2(fattore_base: float, peso: float, tabella2: pd.DataFrame):
    """
    Applica la correzione per il peso usando la Tabella 2
    (stessa logica dell'implementazione originale).
    """
    if not (fattore_base >= 1.4 and float(peso) != 70.0):
        return fattore_base, False, {}

    try:
        t2 = tabella2.copy()

        def parse_peso(col_name: str):
            s = str(col_name).strip().lower().replace("kg", "").replace("w", "")
            num = "".join(ch for ch in s if (ch.isdigit() or ch in ".,"))
            num = num.replace(",", ".")
            try:
                return float(num)
            except Exception:
                return None

        pesi_col = {col: parse_peso(col) for col in t2.columns}
        pesi_col = {col: w for col, w in pesi_col.items() if w is not None}
        if not pesi_col:
            raise ValueError("Nessuna colonna peso valida in Tabella 2.")

        col_70 = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - 70.0))
        serie70 = pd.to_numeric(t2[col_70], errors="coerce")
        idx_match = (serie70 - fattore_base).abs().idxmin()

        col_user = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - float(peso)))
        val_user = pd.to_numeric(t2.loc[idx_match, col_user], errors="coerce")

        if pd.notna(val_user):
            return float(val_user), True, {
                "colonna_70kg": f"{col_70} (≈70 kg)",
                "riga_match_indice": str(idx_match),
                "colonna_peso_utente": f"{col_user} (≈{peso:.1f} kg)"
            }
    except Exception:
        pass

    return fattore_base, False, {}

# =========================================
# MODALITÀ FORMULA (senza tabella): funzione di calcolo
# =========================================
def calcola_fattore_formula(
    n_sottili: int,
    n_spessi: int,
    n_lenzuolo_piu: int,
    n_lenzuolo_piu_piu: int,
    n_coperte_medie: int,
    n_coperte_pesanti: int,
    stato_corpo: str,
    corrente_tipo: str,      # "aria" | "acqua" | "/"
    corrente_label: str,     # "Nessuna corrente"/"Esposto a corrente d'aria"/"In acqua stagnante"/"In acqua corrente"/"/"
    superficie: str          # una delle superfici o "/"
) -> float:
    """
    Implementa le regole fornite:
    - Ogni strato sottile: +0.075 fino a MAX 1.8 (cap sul valore mentre sommo i contributi “sottili/ spessi/ lenzuolo+”).
    - Ogni strato spesso: +0.15 fino a MAX 1.8.
    - Ogni Lenzuolo +: +0.075 fino a MAX 1.8.
    - Lenzuolo ++: base 1.0, +0.15 per ciascun incremento, con CAP del contributo L++ a +1.0 (=> “fino a 2”).
    - Coperta media: se presente, base almeno 1.5, +0.2 per ciascun incremento.
    - Coperta pesante: base almeno 1.5, +0.3 per ciascun incremento.

    NOTE:
    - Per ora NON applico attenuazioni/boost dovuti a correnti e superficie: verranno aggiunti quando fornisci le regole.
    - Se coesistono media e pesante, uso la base più alta (>=1.5).
    """

    # Base
    base = 1.0
    if (n_coperte_medie > 0) or (n_coperte_pesanti > 0):
        base = max(base, 1.5)

    value = base

    # Contributi che hanno CAP del valore a 1.8 mentre si sommano (sottili, spessi, L+)
    def cap_18(x):  # helper
        return min(x, 1.8)

    # 1) strati sottili
    value = cap_18(value + 0.075 * max(0, n_sottili))

    # 2) strati spessi
    value = cap_18(value + 0.15 * max(0, n_spessi))

    # 3) Lenzuolo +
    value = cap_18(value + 0.075 * max(0, n_lenzuolo_piu))

    # 4) Lenzuolo ++: contributo separato con cap +1.0 (così “da 1 a 2”)
    contrib_lpp = min(0.15 * max(0, n_lenzuolo_piu_piu), 1.0)
    value += contrib_lpp

    # 5) Coperte medie: +0.2 ciascuna
    value += 0.2 * max(0, n_coperte_medie)

    # 6) Coperte pesanti: +0.3 ciascuna
    value += 0.3 * max(0, n_coperte_pesanti)

    # ===== Correnti e superficie: per ora NEUTRE =====
    # (inseriremo modifiche qui quando mi darai i dettagli)
    _ = (stato_corpo, corrente_tipo, corrente_label, superficie)

    return float(value)

# =========================================
# MODALITÀ TABELLA (originale)
# =========================================
def calcola_fattore_tabella(peso: float):
    try:
        tabella1, tabella2 = load_tabelle_correzione()
    except Exception as e:
        st.error(f"Errore nel caricamento delle tabelle: {e}")
        return

    # CORPO (etichette compatte → mapping tabella)
    corpo_label = st.radio("", ["Corpo asciutto", "Corpo bagnato", "Corpo immerso"], key="corpo_tab", horizontal=True)
    mapping_corpo = {"Corpo asciutto": "Asciutto", "Corpo bagnato": "Bagnato", "Corpo immerso": "Immerso"}
    stato_corpo = mapping_corpo[corpo_label]

    scelta_vestiti = "/"
    scelta_coperte = "/"
    superficie = "/"
    corrente = "/"

    if stato_corpo == "Immerso":
        corr_acqua = st.radio("", ["Senza correnti d'acqua", "Con correnti d'acqua"], key="acqua_tab", horizontal=True)
        corrente = "In acqua stagnante" if "Senza" in corr_acqua else "In acqua corrente"

    elif stato_corpo == "Bagnato":
        scelta_vestiti = st.radio("**Strati di indumenti**",
                                  ["Nudo", "1-2 strati sottili", "1-2 strati spessi",
                                   "2-3 strati sottili", "3-4 strati sottili", "˃ strati", "˃˃ strati"],
                                  key="vestiti_tab", horizontal=True, help=HELP_VESTITI)
        corr_aria = st.radio("", ["Senza correnti d'aria", "Con correnti d'aria"], key="aria_tab", horizontal=True)
        corrente = "Nessuna corrente" if "Senza" in corr_aria else "Esposto a corrente d'aria"

    else:
        scelta_vestiti = st.radio("**Strati di indumenti**",
                                  ["Nudo", "1-2 strati sottili", "2-3 strati sottili",
                                   "3-4 strati sottili", "1-2 strati spessi", "˃ strati", "˃˃ strati"],
                                  key="vestiti_tab", horizontal=True, help=HELP_VESTITI)
        scelta_coperte = st.radio("**Coperte?**",
                                  ["Nessuna coperta", "Lenzuolo +", "Lenzuolo ++",
                                   "Coperta", "Coperta +", "Coperta ++", "Coperta +++", "Coperta ++++",
                                   "Strato di foglie di medio spessore", "Spesso strato di foglie"],
                                  key="coperte_tab", horizontal=True, help=HELP_COPERTE)

        if scelta_coperte in ["Strato di foglie di medio spessore", "Spesso strato di foglie"]:
            corrente = "/"
            superficie = "/"
            scelta_vestiti = "/"
        else:
            corr_aria = st.radio("", ["Senza correnti d'aria", "Con correnti d'aria"], key="aria_tab", horizontal=True)
            corrente = "Nessuna corrente" if "Senza" in corr_aria else "Esposto a corrente d'aria"

            if (scelta_vestiti == "Nudo" and scelta_coperte == "Nessuna coperta"):
                opzioni_superficie = ["Indifferente", "Molto isolante", "Isolante",
                                      "Foglie umide (≥2 cm)", "Foglie secche (≥2 cm)", "Molto conduttivo", "Conduttivo"]
            else:
                opzioni_superficie = ["Indifferente", "Molto isolante", "Isolante", "Conduttivo"]
            superficie = st.radio("**Appoggio**", opzioni_superficie, key="superficie_tab", horizontal=True, help=HELP_SUPERFICIE)

    # Match e calcolo
    tabella1_mask = (
        (tabella1["Ambiente"] == stato_corpo) &
        (tabella1["Vestiti"] == scelta_vestiti) &
        (tabella1["Coperte"] == scelta_coperte) &
        (tabella1["Superficie d'appoggio"] == superficie) &
        (tabella1["Correnti"] == corrente)
    )
    riga = tabella1[tabella1_mask]
    if riga.empty:
        st.warning("Nessuna combinazione valida trovata nella tabella.")
        return

    fattore_base = float(pd.to_numeric(riga["Fattore"], errors="coerce").dropna().iloc[0])

    fattore_finale, applied_t2, t2_details = applica_tabella2(fattore_base, peso, tabella2)

    # Output
    if abs(fattore_finale - fattore_base) > 1e-9:
        st.success(f"Fattore (adattato al peso {peso:.1f} kg): **{fattore_finale:.2f}**")
        st.caption(f"Valore per 70 kg: {fattore_base:.2f}")
    else:
        st.success(f"Fattore suggerito: **{fattore_finale:.2f}**")
    st.info("Tabella 2: " + ("applicata" if applied_t2 else "non applicata"))

# =========================================
# UI: scelta modalità + Peso
# =========================================
modo = st.toggle("Usa **Formula (senza tabella)**", value=True, help="Se disattivo, uso la Tabella rielaborata.")
peso = st.number_input("Peso (kg)", min_value=10.0, max_value=250.0, value=70.0, step=0.5, key="peso_beta")

# =========================================
# Modalità FORMULA: contatori + calcolo
# =========================================
if modo:
    st.subheader("Contatori di copertura/indumenti (Formula)")

    colA, colB, colC = st.columns(3)
    with colA:
        n_sottili = st.number_input("n. strati sottili", 0, 50, 0, 1)
        n_spessi = st.number_input("n. strati spessi", 0, 50, 0, 1)
    with colB:
        n_lenzuolo_piu = st.number_input("n. Lenzuolo +", 0, 50, 0, 1)
        n_lenzuolo_piu_piu = st.number_input("n. Lenzuolo ++", 0, 50, 0, 1)
    with colC:
        n_coperte_medie = st.number_input("n. Coperte (medie)", 0, 50, 0, 1)
        n_coperte_pesanti = st.number_input("n. Coperte (pesanti)", 0, 50, 0, 1)

    # Corpo + Correnti + Superficie (per ora neutri nella formula; li useremo dopo)
    corpo = st.radio("", ["Corpo asciutto", "Corpo bagnato", "Corpo immerso"], horizontal=True)
    mappa_corpo = {"Corpo asciutto": "Asciutto", "Corpo bagnato": "Bagnato", "Corpo immerso": "Immerso"}
    stato_corpo = mappa_corpo[corpo]

    corrente_tipo = "/"
    corrente_label = "/"
    if stato_corpo == "Immerso":
        corrente_tipo = "acqua"
        c = st.radio("", ["Senza correnti d'acqua", "Con correnti d'acqua"], horizontal=True)
        corrente_label = "In acqua stagnante" if "Senza" in c else "In acqua corrente"
    elif stato_corpo == "Bagnato" or stato_corpo == "Asciutto":
        corrente_tipo = "aria"
        c = st.radio("", ["Senza correnti d'aria", "Con correnti d'aria"], horizontal=True)
        corrente_label = "Nessuna corrente" if "Senza" in c else "Esposto a corrente d'aria"

    superficie = "/"
    if stato_corpo == "Asciutto":
        # Solo per coerenza UI (non influisce ancora sul calcolo)
        base_opts = ["Indifferente", "Molto isolante", "Isolante", "Conduttivo"]
        extra_opts = ["Foglie umide (≥2 cm)", "Foglie secche (≥2 cm)", "Molto conduttivo"]
        if (n_sottili == 0 and n_spessi == 0 and n_lenzuolo_piu == 0 and
            n_lenzuolo_piu_piu == 0 and n_coperte_medie == 0 and n_coperte_pesanti == 0):
            # Caso "nudo senza coperture": offro anche le opzioni aggiuntive come nella tabella
            opzioni_superficie = base_opts + extra_opts
        else:
            opzioni_superficie = base_opts
        superficie = st.radio("**Appoggio**", opzioni_superficie, horizontal=True, help=HELP_SUPERFICIE)

    # Calcolo formula
    fattore_base = calcola_fattore_formula(
        n_sottili=n_sottili,
        n_spessi=n_spessi,
        n_lenzuolo_piu=n_lenzuolo_piu,
        n_lenzuolo_piu_piu=n_lenzuolo_piu_piu,
        n_coperte_medie=n_coperte_medie,
        n_coperte_pesanti=n_coperte_pesanti,
        stato_corpo=stato_corpo,
        corrente_tipo=corrente_tipo,
        corrente_label=corrente_label,
        superficie=superficie
    )

    # Correzione peso (Tabella 2), se disponibile
    applied_t2 = False
    t2_details = {}
    try:
        _, tabella2 = load_tabelle_correzione()
        fattore_finale, applied_t2, t2_details = applica_tabella2(fattore_base, peso, tabella2)
    except Exception:
        fattore_finale = fattore_base

    # Output
    if abs(fattore_finale - fattore_base) > 1e-9:
        st.success(f"Fattore (formula, adattato al peso {peso:.1f} kg): **{fattore_finale:.2f}**")
        st.caption(f"Valore formula per 70 kg: {fattore_base:.2f}")
    else:
        st.success(f"Fattore (formula): **{fattore_finale:.2f}**")

    st.info("Tabella 2: " + ("applicata" if applied_t2 else "non applicata"))

# =========================================
# Modalità TABELLA (per confronto)
# =========================================
else:
    calcola_fattore_tabella(peso)
    
