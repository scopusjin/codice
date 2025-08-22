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

def is_nudo(n_sottili_eq: int, n_spessi_eq: int, n_cop_medie: int, n_cop_pesanti: int) -> bool:
    """Vero se nessuno strato/telo/coperta selezionato."""
    return (n_sottili_eq == 0 and n_spessi_eq == 0 and n_cop_medie == 0 and n_cop_pesanti == 0)

def calcola_fattore_vestiti_coperte(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti):
    """
    Regole VOLUTE:
    - Base 2.0 se >=1 coperta pesante (+0.3 per ciascuna pesante extra, +0.2 per ciascuna media)
    - Altrimenti base 1.8 se >=1 coperta media (+0.2 per ciascuna media extra)
    - Altrimenti base 1.0
    - +0.075 per ogni strato sottile (indumento o telo sottile)
    - +0.15  per ogni strato spesso  (indumento pesante o telo spesso)
    - Nessun cap a 1.8 in assenza di coperte (come da tua scelta).
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
    # per correnti in asciutto
    return (fattore_vestiti_coperte > 1.0 and fattore_vestiti_coperte < 1.2)

# === Bagnato: base SENZA correnti secondo tabella ===
def fattore_bagnato_base(n_sottili_eq: int, n_spessi_eq: int) -> float:
    """
    🌊 Bagnato — SENZA correnti (tabella):
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
    return 0.90  # nudo

# =========================
# Regole superficie (etichette lunghe)
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
    """Regole di appoggio (senza correnti). Chiamata solo quando NON bagnato/immerso."""
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
    - BAGNATO: override totale (tabella) + (−0.2 se correnti), cap 1.2; coperte => livello max.
    - ASCIUTTO: percentuali per superficie; 'nudo' rilevato dai contatori.
    """
    # --- BAGNATO ---
    if stato == "bagnato":
        # Se presenti coperte (anche se nascoste), promuovi al massimo livello della tabella
        n_sottili_eff = n_sottili_eq
        n_spessi_eff  = n_spessi_eq
        if (n_cop_medie > 0 or n_cop_pesanti > 0):
            n_sottili_eff = max(n_sottili_eff, 5)  # >4 sottili
            n_spessi_eff  = max(n_spessi_eff, 3)  # >2 spessi

        base = fattore_bagnato_base(n_sottili_eff, n_spessi_eff)
        val  = base - 0.2 if correnti_presenti else base
        return clamp(min(val, 1.2)), True

    # --- ASCIUTTO ---
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
        # per "molto conduttivo" in asciutto: −25%
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

# ---- Radio compatti: nascondi label e spazio con CSS ----
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

# Condizione del corpo (radio senza titolo/spazio)
stato_label = st.radio(
    "dummy",
    options=["Corpo asciutto", "Bagnato", "Immerso"],
    index=0,
    horizontal=True,
)
# Normalizza interno
stato = "asciutto" if stato_label == "Corpo asciutto" else ("bagnato" if stato_label == "Bagnato" else "in acqua")

# ==== Branch UI: Immerso vs non-immerso ====
if stato == "in acqua":
    # Radio acqua (senza titolo/spazio)
    acqua_label = st.radio(
        "dummy",
        options=["in acqua stagnante", "in acqua corrente"],
        index=0,
        horizontal=True,
    )
    fattore_finale = 0.35 if acqua_label == "in acqua corrente" else 0.50
    st.metric("Fattore di correzione", f"{fattore_finale:.2f}")
    st.stop()

# ---- Toggle correnti ----
toggle_correnti = st.toggle("Correnti d'aria presenti?", value=False)
correnti_presenti = bool(toggle_correnti)

# ---- Toggle vestizione + expander strati/coperte ----
n_sottili_eq = n_spessi_eq = n_cop_medie = n_cop_pesanti = 0
toggle_vestito = st.toggle("Vestito/coperto?", value=False)

if toggle_vestito:
    with st.expander(" ", expanded=True):  # header muto
        st.caption("Indicare il numero di strati sul corpo. Contano solo quelli che coprono la parte bassa del tronco.")
        c1e, c2e = st.columns(2)
        with c1e:
            n_sottili_eq = st.slider("Strati leggeri (indumenti o teli sottili)", 0, 8, 0, key="strati_sottili")
            if stato == "asciutto":
                n_cop_medie  = st.slider("Coperte di medio spessore", 0, 5, 0, key="coperte_medie")
        with c2e:
            n_spessi_eq  = st.slider("Strati pesanti (indumenti o teli spessi)", 0, 6, 0, key="strati_spessi")
            if stato == "asciutto":
                n_cop_pesanti= st.slider("Coperte pesanti", 0, 5, 0, key="coperte_pesanti")

# Avviso: switch ON ma nessuno strato → nudo ai fini del calcolo
if toggle_vestito and is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti):
    st.caption("⚠️ Nessuno strato impostato: il corpo è considerato **nudo** ai fini del calcolo.")

# ---- Superficie d’appoggio (SOLO se ASCIUTTO) ----
superficie = None
if stato == "asciutto":
    # Costruisci dopo l’expander così conosci se è nudo
    opts_appoggio = [SURF_INDIFF, SURF_ISOL, SURF_MOLTOI, SURF_COND]
    # Foglie solo se asciutto
    opts_appoggio += [SURF_FOGLIU, SURF_FOGLIS]
    # Metallo all’aperto solo se asciutto + nudo
    if is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti):
        opts_appoggio.append(SURF_MOLTOC)

    # Mantieni selezione precedente se valida
    prev = st.session_state.get("superficie_sel")
    if prev not in opts_appoggio:
        prev = opts_appoggio[0]
    superficie = st.selectbox(
        "Superficie di appoggio",
        opts_appoggio,
        index=opts_appoggio.index(prev),
        key="superficie_sel"
    )

# =========================
# Pipeline di calcolo
# =========================
# 1) Fattore vestiti/coperte
fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(
    n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
)
fattore = float(fattore_vestiti_coperte)

# 2) Superficie (solo se ASCIUTTO)
if stato == "asciutto" and superficie is not None:
    fattore = applica_regole_superficie(
        fattore, superficie, stato,
        n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
    )

# 3) Correnti (in BAGNATO: override totale + cap 1.2; in ASCIUTTO: percentuali)
fattore, _ = applica_correnti(
    fattore, stato, superficie, correnti_presenti,
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
