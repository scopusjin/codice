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

def is_nudo(n_sottili_eq: int, n_spessi_eq: int, n_cop_medie: int, n_cop_pesanti: int) -> bool:
    """Vero se nessuno strato/lenzuolo/coperta selezionato."""
    return (n_sottili_eq == 0 and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)

def calcola_fattore_vestiti_coperte(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti):
    """
    Regole VOLUTE:
    - Base 2.0 se >=1 coperta pesante (+0.3 per ciascuna pesante extra, +0.2 per ciascuna media)
    - Altrimenti base 1.8 se >=1 coperta media (+0.2 per ciascuna media extra)
    - Altrimenti base 1.0
    - +0.075 per ogni strato sottile (indumento o lenzuolo sottile)
    - +0.15  per ogni strato spesso  (indumento pesante o lenzuolo spesso)
    - Nessun cap a 1.8 in assenza di coperte (come richiesto).
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
    # come da specifiche precedenti per le correnti in asciutto
    return (fattore_vestiti_coperte > 1.0 and fattore_vestiti_coperte < 1.2)

# === Nuova logica bagnato: base SENZA correnti in funzione degli strati ===
def fattore_bagnato_base(n_sottili_eq: int, n_spessi_eq: int) -> float:
    """
    🌊 Bagnato — SENZA correnti (tua tabella):
    - Nudo → 0.9
    - 1 sottile → 1.0
    - 1 spesso oppure 2 sottili → 1.1
    - 2 spessi oppure 3–4 sottili → 1.15
    - >2 spessi oppure >4 sottili → 1.2
    """
    if n_spessi_eq > 2 or n_sottili_eq > 4:
        return 1.20
    if n_spessi_eq == 2 or (3 <= n_sottili_eq <= 4):
        return 1.15
    if n_spessi_eq == 1 or n_sottili_eq == 2:
        return 1.10
    if n_sottili_eq == 1:
        return 1.00
    # nudo (0,0)
    return 0.90

def applica_regole_superficie(
    fatt, superficie_short, stato, n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
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
        if not (stato == "asciutto" and is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)):
            return fatt  # guard-rail
        return 0.55  # correnti eventualmente DOPO

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
    fatt, stato, superficie_short, correnti_presenti: bool,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti,
    fattore_vestiti_coperte
):
    """
    - BAGNATO: override totale secondo tabella + (−0.2 se correnti), cap 1.2, coperte = livello max.
    - ASCIUTTO: regole percentuali come definito, basate su 'is_nudo' e 'poco vestito'.
    """
    # --- BLOCCO BAGNATO ---
    if stato == "bagnato":
        # Se presenti coperte, promuovi al massimo livello
        n_sottili_eff = n_sottili_eq
        n_spessi_eff  = n_spessi_eq
        if (n_cop_medie > 0 or n_cop_pesanti > 0):
            n_sottili_eff = max(n_sottili_eff, 5)  # >4 sottili
            n_spessi_eff  = max(n_spessi_eff, 3)  # >2 spessi

        base = fattore_bagnato_base(n_sottili_eff, n_spessi_eff)
        val  = base - 0.2 if correnti_presenti else base
        return clamp(min(val, 1.2)), True

    # --- BLOCCO ASCIUTTO ---
    if not correnti_presenti:
        return fatt, False

    nudo_asciutto = (stato == "asciutto" and is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti))
    poco_vest     = (stato == "asciutto" and is_poco_vestito(fattore_vestiti_coperte))

    if superficie_short == "Indifferente":
        if nudo_asciutto:
            return fatt * 0.75, True
        if poco_vest:
            return fatt * 0.80, True

    elif superficie_short == "Isolante":
        if nudo_asciutto:
            return fatt * 0.80, True
        if poco_vest:
            return fatt * 0.85, True

    elif superficie_short == "Molto isolante":
        if nudo_asciutto or poco_vest:
            return fatt * 0.90, True

    elif superficie_short == "Conduttivo":
        if nudo_asciutto or poco_vest:
            return fatt * 0.75, True

    elif superficie_short == "Molto conduttivo":
        # solo nudo è ammesso da UI; −25% richiesto
        return fatt * 0.75, True

    return fatt, False

def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    if f_base < 1.4:
        return clamp(f_base)
    approx = f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return clamp(approx)

# =========================
# UI reattiva
# =========================
st.subheader("Input")

# Peso
peso = st.number_input("Peso corporeo (kg)", min_value=10.0, max_value=200.0, value=70.0, step=0.5)

# ---- Condizione del corpo: radio orizzontale, senza label/spazio (via CSS) ----
st.markdown(
    """
    <style>
    /* Nasconde il label e compatta il blocco radio */
    div[data-testid="stRadio"] > label {display: none !important;}
    div[data-testid="stRadio"] {margin-top: -14px; margin-bottom: -10px;}
    /* Avvicina i bottoni orizzontali */
    div[data-testid="stRadio"] div[role="radiogroup"] {gap: 0.4rem;}
    </style>
    """,
    unsafe_allow_html=True
)
stato_label = st.radio(
    "dummy",
    options=["Corpo asciutto", "Bagnato", "Immerso"],
    index=0,
    horizontal=True,
)
if stato_label == "Corpo asciutto":
    stato = "asciutto"
elif stato_label == "Bagnato":
    stato = "bagnato"
else:
    stato = "in acqua"

# ==== Branch UI: Immerso vs non-immerso ====
if stato == "in acqua":
    # Radio acqua compatto (riusa CSS del radio)
    acqua_label = st.radio(
        "dummy",
        options=["in acqua stagnante", "in acqua corrente"],
        index=0,
        horizontal=True,
    )
    fattore_finale = 0.35 if acqua_label == "in acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# ---- Superficie d’appoggio (solo se NON immerso) ----
vestizione_assunta = "nudo e scoperto"  # per opzioni iniziali
opts_appoggio = ["Indifferente", "Isolante", "Molto isolante", "Conduttivo"]
if stato == "asciutto":
    opts_appoggio.append("Molto conduttivo")  # visibile (guard-rail in funzioni)
    opts_appoggio += ["Foglie umide (>= 2 cm)", "Foglie secche (>= 2 cm)"]
superficie_short = st.selectbox("Superficie di appoggio", opts_appoggio, index=0, help=HELP_SUPERFICIE)

# ---- Switch affiancati (solo se NON immerso) ----
c1, c2 = st.columns(2)
with c1:
    toggle_vestito = st.toggle("Vestito/coperto?", value=False)
with c2:
    toggle_correnti = st.toggle("Correnti d'aria presenti?", value=False)
correnti_presenti = bool(toggle_correnti)
vestizione_label = "vestito e/o coperto" if toggle_vestito else "nudo e scoperto"

# ---- Expander vestizione/coperte ----
n_sottili_eq = n_spessi_eq = n_cop_medie = n_cop_pesanti = 0
if toggle_vestito:
    with st.expander(" ", expanded=True):  # header muto
        st.caption("Indicare il numero di strati sul corpo. Hanno influenza solo quelli che coprono la parte bassa del tronco.")
        c1e, c2e = st.columns(2)
        with c1e:
            n_sottili_eq = st.slider("Strati leggeri (indumenti o lenzuola sottili)", 0, 8, 0)
            # Coperte visibili solo se NON bagnato
            if stato != "bagnato":
                n_cop_medie = st.slider("Coperte di medio spessore", 0, 5, 0)
        with c2e:
            n_spessi_eq = st.slider("Strati pesanti (indumenti o lenzuola spesse)", 0, 6, 0)
            if stato != "bagnato":
                n_cop_pesanti = st.slider("Coperte pesanti", 0, 5, 0)

# Avviso se switch ON ma nessuno strato impostato (si calcola come nudo)
if toggle_vestito and is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti):
    st.caption("⚠️ Nessuno strato impostato: il corpo è considerato **nudo** ai fini del calcolo.")

# =========================
# Pipeline di calcolo
# =========================
# 1) Fattore vestiti/coperte (serve per asciutto e per 'poco vestito')
fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
)
fattore = float(fattore_vestiti_coperte)

# 2) Superficie
fattore = applica_regole_superficie(
    fattore, superficie_short, stato,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
)

# 3) Correnti (in bagnato: override totale + cap 1.2; in asciutto: percentuali)
fattore, _ = applica_correnti(
    fattore, stato, superficie_short, correnti_presenti,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti,
    fattore_vestiti_coperte
)

# 4) Sicurezza + peso
if math.isnan(fattore):
    fattore = 1.0
fattore = clamp(fattore)
fattore_finale = correzione_peso_tabella2(fattore, float(peso))

# =========================
# Output
# =========================
st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
