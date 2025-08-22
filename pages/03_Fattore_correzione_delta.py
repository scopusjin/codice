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
# Superfici — categorie canoniche
# =========================
SURF_INDIFF = "INDIFFERENTE"
SURF_ISOL   = "ISOLANTE"
SURF_MOLTOI = "MOLTO_ISOLANTE"
SURF_COND   = "CONDUTTIVO"
SURF_MOLTOC = "MOLTO_CONDUTTIVO"
SURF_FOGLIU = "FOGLIE_UMIDE"
SURF_FOGLIS = "FOGLIE_SECCHE"

# Etichette mostrate all’utente (alcune mappano alla stessa categoria)
SURF_DISPLAY_TO_KEY = {
    # Indifferente (stesso effetto)
    "Pavimento di casa, piano in legno.": SURF_INDIFF,
    "Terreno, prato o asfalto asciutti": SURF_INDIFF,

    # Isolante / molto isolante
    "Materasso o tappeto spesso": SURF_ISOL,
    "Divano imbottito, sacco a pelo tecnico, polistirolo": SURF_MOLTOI,

    # Conduttivo (stesso effetto, tre varianti)
    "Cemento, pietra, PVC": SURF_COND,
    "Pavimentazione fredda (all’esterno, in cantina…)": SURF_COND,
    "Piano metallico (in ambiente interno)": SURF_COND,

    # Molto conduttivo (solo nudo + asciutto)
    "Superficie metallica spessa (all’aperto)": SURF_MOLTOC,

    # Foglie
    "Strato di foglie umide (≥2 cm)": SURF_FOGLIU,
    "Strato di foglie secche (≥2 cm)": SURF_FOGLIS,
}

# Ordine preferito per la select
SURF_DISPLAY_ORDER = [
    "Pavimento di casa, piano in legno.",
    "Terreno, prato o asfalto asciutti",
    "Materasso o tappeto spesso",
    "Divano imbottito, sacco a pelo tecnico, polistirolo",
    "Cemento, pietra, PVC",
    "Pavimentazione fredda (all’esterno, in cantina…)",
    "Piano metallico (in ambiente interno)",
    "Superficie metallica spessa (all’aperto)",
    "Strato di foglie umide (≥2 cm)",
    "Strato di foglie secche (≥2 cm)",
]

def applica_regole_superficie(
    fatt, superficie_key, stato,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
):
    """Regole appoggio (usa la chiave canonica)."""
    tot_items = n_sottili_eq + n_spessi_eq + n_cop_medie + n_cop_pesanti

    def only_thin_1():   return (n_sottili_eq == 1 and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)
    def only_thin_1_2(): return (n_sottili_eq in (1, 2) and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)

    if superficie_key == SURF_INDIFF:
        return fatt

    if superficie_key == SURF_ISOL:
        if tot_items == 0:      return 1.10
        elif only_thin_1():     return 1.20
        else:                   return fatt + 0.10

    if superficie_key == SURF_MOLTOI:
        if tot_items == 0:      return 1.30
        if only_thin_1_2():     return fatt + 0.30
        else:                   return fatt + 0.10

    if superficie_key == SURF_COND:
        if tot_items == 0:      return 0.75
        elif only_thin_1():     return fatt - 0.20
        else:                   return fatt - 0.10

    if superficie_key == SURF_MOLTOC:
        # Solo ASCIUTTO + NUDO produce 0.55
        if not (stato == "asciutto" and is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)):
            return fatt
        return 0.55

    if superficie_key == SURF_FOGLIU:
        if tot_items == 0:      return 1.20
        if only_thin_1_2():     return fatt + 0.20
        else:                   return fatt + 0.10

    if superficie_key == SURF_FOGLIS:
        if tot_items == 0:      return 1.50
        if only_thin_1_2():     return fatt + 0.30
        else:                   return fatt + 0.20

    return fatt

# =========================
# Correnti d'aria
# =========================
def applica_correnti(
    fatt, stato, superficie_key, correnti_presenti: bool,
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

    if superficie_key == SURF_INDIFF:
        if nudo_asciutto: return fatt * 0.75, True
        if poco_vest:     return fatt * 0.80, True
    elif superficie_key == SURF_ISOL:
        if nudo_asciutto: return fatt * 0.80, True
        if poco_vest:     return fatt * 0.85, True
    elif superficie_key == SURF_MOLTOI:
        if nudo_asciutto or poco_vest: return fatt * 0.90, True
    elif superficie_key == SURF_COND:
        if nudo_asciutto or poco_vest: return fatt * 0.75, True
    elif superficie_key == SURF_MOLTOC:
        return fatt * 0.75, True

    return fatt, False

def correzione_peso_tabella2(f_base: float, peso_kg: float) -> float:
    if f_base < 1.4:
        return clamp(f_base)
    approx = f_base * (0.98 + (peso_kg / 70.0) * 0.02)
    return clamp(approx)

# =========================
# UI — compattazione & ordine
# =========================

# Peso
peso = st.number_input("Peso corporeo (kg)", min_value=10.0, max_value=200.0, value=70.0, step=0.5)

# CSS compatto
st.markdown(
    """
    <style>
      /* Radio: nascondi label e riduci margini */
      div[data-testid="stRadio"] > label {display:none !important;}
      div[data-testid="stRadio"] {margin-top:-14px; margin-bottom:-10px;}
      div[data-testid="stRadio"] div[role="radiogroup"] {gap:0.4rem;}
      /* Toggle: riduci margini verticali */
      div[data-testid="stToggle"] {margin-top:-6px; margin-bottom:-6px;}
      /* Slider: compattazione leggera */
      div[data-testid="stSlider"] {margin-top:-4px; margin-bottom:-2px;}
    </style>
    """,
    unsafe_allow_html=True
)

# 1) Condizione del corpo
stato_label = st.radio("dummy", ["Corpo asciutto", "Bagnato", "Immerso"], index=0, horizontal=True)
stato = "asciutto" if stato_label == "Corpo asciutto" else ("bagnato" if stato_label == "Bagnato" else "in acqua")

# 2) Immerso: radio stagnante/corrente e stop
if stato == "in acqua":
    acqua_label = st.radio("dummy", ["in acqua stagnante", "in acqua corrente"], index=0, horizontal=True)
    fattore_finale = 0.35 if acqua_label == "in acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# Placeholder per Superficie (la mostriamo dopo aver letto gli slider)
surface_placeholder = st.empty()

# 3) Correnti + Vestiti sulla stessa riga
col_corr, col_vest = st.columns([1.0, 1.3])
with col_corr:
    corr_placeholder = st.empty()
with col_vest:
    toggle_vestito = st.toggle("Vestito/coperto?", value=st.session_state.get("toggle_vestito", False), key="toggle_vestito")

# 4) Slider vestizione (se ON)
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

# Calcolo fattore vestizione (serve anche per decidere visibilità correnti)
fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)

# Correnti: nascondi se asciutto e fattore >= 1.2
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

# 5) Superficie (solo ASCIUTTO), con voci granulari e mappatura a chiave canonica
def _superficie_options_for_state(is_nudo_eff: bool):
    """Restituisce la lista di etichette visuali filtrate per lo stato corrente."""
    # Base: tutte le opzioni tranne "metallo all’aperto" (che richiede nudo)
    opts = [
        "Pavimento di casa, piano in legno.",
        "Terreno, prato o asfalto asciutti",
        "Materasso o tappeto spesso",
        "Divano imbottito, sacco a pelo tecnico, polistirolo",
        "Cemento, pietra, PVC",
        "Pavimentazione fredda (all’esterno, in cantina…)",
        "Piano metallico (in ambiente interno)",
        "Strato di foglie umide (≥2 cm)",
        "Strato di foglie secche (≥2 cm)",
    ]
    # "Superficie metallica spessa (all’aperto)" solo se nudo effettivo
    if is_nudo_eff:
        opts.insert(7, "Superficie metallica spessa (all’aperto)")  # prima delle foglie
    return opts

superficie_key = None
superficie_display_selected = None

with surface_placeholder.container():
    if stato == "asciutto":
        nudo_eff = (not toggle_vestito) or is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)
        options_display = _superficie_options_for_state(nudo_eff)

        # Recupera ultima selezione visuale, se ancora valida; altrimenti default alla prima
        prev_display = st.session_state.get("superficie_display_sel")
        if prev_display not in options_display:
            prev_display = options_display[0]

        superficie_display_selected = st.selectbox(
            "Superficie di appoggio",
            options_display,
            index=options_display.index(prev_display),
            key="superficie_display_sel"
        )
        superficie_key = SURF_DISPLAY_TO_KEY.get(superficie_display_selected, SURF_INDIFF)
    else:
        st.empty()

# =========================
# Pipeline di calcolo
# =========================
fattore = float(fattore_vestiti_coperte)

if stato == "asciutto" and superficie_key is not None:
    fattore = applica_regole_superficie(
        fattore, superficie_key, stato,
        n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
    )

fattore, _ = applica_correnti(
    fattore, stato, superficie_key, correnti_presenti,
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti,
    fattore_vestiti_coperte
)

if math.isnan(fattore):
    fattore = 1.0
fattore = clamp(fattore)

# Correzione peso (stub)
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
