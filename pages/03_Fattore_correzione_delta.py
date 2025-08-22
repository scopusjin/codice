# pages/03_Fattore_correzione_delta.py
# -*- coding: utf-8 -*-
import math
import streamlit as st

# =========================
# Config
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

def is_nudo(n_sottili_eq: int, n_spessi_eq: int, n_cop_medie: int, n_cop_pesanti: int) -> bool:
    return (n_sottili_eq == 0 and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)

def calcola_fattore_vestiti_coperte(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti):
    """
    - Base 2.0 se >=1 coperta pesante (+0.3 per ciascuna pesante extra, +0.2 per ciascuna media)
    - Altrimenti base 1.8 se >=1 coperta media (+0.2 per ciascuna media extra)
    - Altrimenti base 1.0
    - +0.075 per ogni strato sottile (indumento o telo sottile)
    - +0.15  per ogni strato spesso  (indumento pesante o telo spesso)
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
    return (1.0 < fattore_vestiti_coperte < 1.2)

# =========================
# Bagnato — tabelle
# =========================
def bagnato_base_senza_correnti(n_sottili: int, n_spessi: int) -> float:
    """
    🌊 Bagnato — SENZA correnti (cap 1.2):
    - Nudo → 0.9
    - 1 sottile → 1.0
    - 1 spesso oppure 2 sottili → 1.1
    - 2 spessi oppure 3–4 sottili → 1.15
    - >2 spessi oppure >4 sottili → 1.2
    """
    if n_spessi > 2 or n_sottili > 4:
        return 1.20
    if n_spessi == 2 or (3 <= n_sottili <= 4):
        return 1.15
    if n_spessi == 1 or n_sottili == 2:
        return 1.10
    if n_sottili == 1:
        return 1.00
    return 0.90

def bagnato_con_correnti(n_sottili: int, n_spessi: int) -> float:
    """
    💨 Bagnato — CON correnti (cap 0.9):
    - Nudo → 0.7
    - 1 sottile → 0.7
    - 1 spesso oppure 2 sottili → 0.75
    - 1 spesso + 1 sottile oppure 3 sottili → 0.8
    - 2+ spessi oppure 4+ sottili → 0.9 (cap)
    """
    if n_spessi >= 2 or n_sottili >= 4:
        return 0.90
    if (n_spessi == 1 and n_sottili == 1) or (n_sottili == 3 and n_spessi == 0):
        return 0.80
    if (n_spessi == 1 and n_sottili == 0) or (n_sottili == 2 and n_spessi == 0):
        return 0.75
    if (n_sottili == 1 and n_spessi == 0):
        return 0.70
    return 0.70

# =========================
# Superfici (etichette lunghe)
# =========================
SURF_INDIFF = "Pavimento di casa, terreno o prato asciutti, asfalto, legno"
SURF_ISOL   = "Materasso o tappeto spesso"
SURF_MOLTOI = "Divano imbottito, sacco a pelo tecnico, polistirolo"
SURF_COND   = "Cemento, pietra, PVC, pavimento esterno/cantina, piano metallico (al chiuso)"
SURF_MOLTOC = "Superficie metallica spessa (all’aperto)"
SURF_FOGLIU = "Strato di foglie umide (≥2 cm)"
SURF_FOGLIS = "Strato di foglie secche (≥2 cm)"

def applica_regole_superficie(
    fatt, superficie, stato,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
):
    """Regole appoggio (solo quando NON bagnato/immerso)."""
    tot_items = n_sottili_eq + n_spessi_eq + n_cop_medie + n_cop_pesanti

    def only_thin_1():   return (n_sottili_eq == 1 and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)
    def only_thin_1_2(): return (n_sottili_eq in (1, 2) and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)

    if superficie == SURF_INDIFF:
        return fatt

    if superficie == SURF_ISOL:
        if tot_items == 0:      return 1.10
        elif only_thin_1():     return 1.20
        else:                   return fatt + 0.10

    if superficie == SURF_MOLTOI:
        if tot_items == 0:      return 1.30
        if only_thin_1_2():     return fatt + 0.30
        else:                   return fatt + 0.10

    if superficie == SURF_COND:
        if tot_items == 0:      return 0.75
        elif only_thin_1():     return fatt - 0.20
        else:                   return fatt - 0.10

    if superficie == SURF_MOLTOC:
        # Solo ASCIUTTO + NUDO produce 0.55
        if not (stato == "asciutto" and is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)):
            return fatt
        return 0.55

    if superficie == SURF_FOGLIU:
        if tot_items == 0:      return 1.20
        if only_thin_1_2():     return fatt + 0.20
        else:                   return fatt + 0.10

    if superficie == SURF_FOGLIS:
        if tot_items == 0:      return 1.50
        if only_thin_1_2():     return fatt + 0.30
        else:                   return fatt + 0.20

    return fatt

# =========================
# Correnti d'aria
# =========================
def applica_correnti(
    fatt, stato, superficie, correnti_presenti: bool,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti,
    fattore_vestiti_coperte
):
    """
    - BAGNATO: tabella dedicata (cap 1.2 senza correnti, cap 0.9 con correnti).
      Coperte ⇒ promozione al livello massimo.
    - ASCIUTTO: percentuali per superficie; 'nudo' dai contatori; 'poco vestito' dal fattore.
    """
    if stato == "bagnato":
        n_sottili_eff = n_sottili_eq
        n_spessi_eff  = n_spessi_eq
        if (n_cop_medie > 0 or n_cop_pesanti > 0):
            n_sottili_eff = max(n_sottili_eff, 5)  # >4 sottili
            n_spessi_eff  = max(n_spessi_eff, 3)   # >2 spessi
        if correnti_presenti:
            return bagnato_con_correnti(n_sottili_eff, n_spessi_eff), True
        else:
            return bagnato_base_senza_correnti(n_sottili_eff, n_spessi_eff), True

    if not correnti_presenti:
        return fatt, False

    nudo_asciutto = (stato == "asciutto" and is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti))
    poco_vest     = (stato == "asciutto" and is_poco_vestito(fattore_vestiti_coperte))

    if superficie == SURF_INDIFF:
        if nudo_asciutto: return fatt * 0.75, True
        if poco_vest:     return fatt * 0.80, True
    elif superficie == SURF_ISOL:
        if nudo_asciutto: return fatt * 0.80, True
        if poco_vest:     return fatt * 0.85, True
    elif superficie == SURF_MOLTOI:
        if nudo_asciutto or poco_vest: return fatt * 0.90, True
    elif superficie == SURF_COND:
        if nudo_asciutto or poco_vest: return fatt * 0.75, True
    elif superficie == SURF_MOLTOC:
        return fatt * 0.75, True

    return fatt, False

def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    if f_base < 1.4:
        return clamp(f_base)
    approx = f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return clamp(approx)

# =========================
# UI — compattazione (punti 1–4)
# =========================

# Peso
peso = st.number_input("Peso corporeo (kg)", min_value=10.0, max_value=200.0, value=70.0, step=0.5)

# CSS compatto per radio, toggle e slider
st.markdown(
    """
    <style>
      /* Radio: nascondi label e riduci margini */
      div[data-testid="stRadio"] > label {display:none !important;}
      div[data-testid="stRadio"] {margin-top:-14px; margin-bottom:-10px;}
      div[data-testid="stRadio"] div[role="radiogroup"] {gap:0.4rem;}
      /* Toggle: riduci margini verticali */
      div[data-testid="stToggle"] {margin-top:-6px; margin-bottom:-6px;}
      /* Slider: compattazione leggera fra slider successivi */
      div[data-testid="stSlider"] {margin-top:-4px; margin-bottom:-2px;}
    </style>
    """,
    unsafe_allow_html=True
)

# 1) Condizione del corpo (radio compatto)
stato_label = st.radio("dummy", ["Corpo asciutto", "Bagnato", "Immerso"], index=0, horizontal=True)
stato = "asciutto" if stato_label == "Corpo asciutto" else ("bagnato" if stato_label == "Bagnato" else "in acqua")

# 2) Se IMMERSO: radio compatto stagnante/corrente e chiudi
if stato == "in acqua":
    acqua_label = st.radio("dummy", ["in acqua stagnante", "in acqua corrente"], index=0, horizontal=True)
    fattore_finale = 0.35 if acqua_label == "in acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# Placeholder per Superficie (la mostriamo dopo aver letto gli slider)
surface_placeholder = st.empty()

# 3) Correnti e Vestiti sulla stessa riga (punti 1 & 3 & 4: ordine + allineamento + proporzioni)
col_corr, col_vest = st.columns([1.0, 1.3])
with col_corr:
    corr_placeholder = st.empty()   # Render iniziale, forse verrà nascosto dopo gli slider
with col_vest:
    toggle_vestito = st.toggle("Vestito/coperto?", value=st.session_state.get("toggle_vestito", False), key="toggle_vestito")

# 4) Slider vestizione inline (visibili se switch ON)
n_sottili_eq = n_spessi_eq = n_cop_medie = n_cop_pesanti = 0
if toggle_vestito:
    c1, c2 = st.columns(2)
    with c1:
        n_sottili_eq = st.slider("Strati leggeri (indumenti o teli sottili)", 0, 8, st.session_state.get("strati_sottili", 0), key="strati_sottili")
        if stato == "asciutto":
            n_cop_medie  = st.slider("Coperte di medio spessore", 0, 5, st.session_state.get("coperte_medie", 0), key="coperte_medie")
    with c2:
        n_spessi_eq  = st.slider("Strati pesanti (indumenti o teli spessi)", 0, 6, st.session_state.get("strati_spessi", 0), key="strati_spessi")
        if stato == "asciutto":
            n_cop_pesanti= st.slider("Coperte pesanti", 0, 5, st.session_state.get("coperte_pesanti", 0), key="coperte_pesanti")

# Calcolo fattore vestizione (serve anche per decidere la visibilità del toggle Correnti)
fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)

# (Ri)render del toggle Correnti nel suo placeholder, subito dopo il corpo (prima dei vestiti),
# ma nascondilo se ininfluente: ASCIUTTO & fattore_vestiti >= 1.2
with corr_placeholder.container():
    if (stato == "asciutto") and (fattore_vestiti_coperte >= 1.2):
        correnti_presenti = False
        st.empty()
    else:
        correnti_presenti = st.toggle(
            "Correnti d'aria presenti?",
            value=st.session_state.get("toggle_correnti", False),
            key="toggle_correnti",
            disabled=False
        )

# Superficie (solo ASCIUTTO), mostrata dopo che sappiamo se è nudo effettivo
superficie = None
with surface_placeholder.container():
    if stato == "asciutto":
        nudo_eff = (not toggle_vestito) or is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)
        opts_appoggio = [SURF_INDIFF, SURF_ISOL, SURF_MOLTOI, SURF_COND, SURF_FOGLIU, SURF_FOGLIS]
        if nudo_eff:
            opts_appoggio.append(SURF_MOLTOC)
        prev = st.session_state.get("superficie_sel")
        if prev not in opts_appoggio:
            prev = opts_appoggio[0]
        superficie = st.selectbox("Superficie di appoggio", opts_appoggio, index=opts_appoggio.index(prev), key="superficie_sel")
    else:
        st.empty()

# =========================
# Pipeline di calcolo
# =========================
fattore = float(fattore_vestiti_coperte)

if stato == "asciutto" and superficie is not None:
    fattore = applica_regole_superficie(
        fattore, superficie, stato,
        n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
    )

fattore, _ = applica_correnti(
    fattore, stato, superficie, correnti_presenti,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti,
    fattore_vestiti_coperte
)

if math.isnan(fattore):
    fattore = 1.0
fattore = clamp(fattore)

# (facoltativa) correzione peso "tabella 2"
def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    if f_base < 1.4:
        return clamp(f_base)
    approx = f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return clamp(approx)

fattore_finale = correzione_peso_tabella2(fattore, float(peso))

# =========================
# Output
# =========================
st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
