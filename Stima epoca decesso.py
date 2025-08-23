# -*- coding: utf-8 -*-
# Streamlit app: Stima epoca decesso
# Revisione con correzioni di robustezza e piccoli fix senza variare la logica di calcolo/UX.

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit.components.v1 as components
import numpy as np
from scipy.optimize import root_scalar
import datetime
import pandas as pd


# =========================
# Stato e costanti globali
# =========================
st.set_page_config(page_title="Stima Epoca della Morte", layout="centered")

if "fattore_correzione" not in st.session_state:
    st.session_state["fattore_correzione"] = 1.0


if "show_img_sopraciliare" not in st.session_state:
    st.session_state["show_img_sopraciliare"] = False
if "show_img_peribuccale" not in st.session_state:
    st.session_state["show_img_peribuccale"] = False
# Definiamo un valore che rappresenta "infinito" o un limite superiore molto elevato per i range aperti
INF_HOURS = 200  # Un valore sufficientemente grande per la scala del grafico e i calcoli

# --- Helper dei widget (testi tooltip) ---
HELP_COPERTE = (
    "**Tenerne conto solo se coprono la parte bassa di torace/addome**.   "
    "**Lenzuolo +** = telo sottile/1-2 lenzuola;   "
    "**Lenzuolo ++** = lenzuolo invernale/copriletto leggero;   "
    "**Coperta** = coperta mezza stagione/ sacco mortuario;   "
    "**Coperta +** = coperta pesante/ mantellina termica;   "
    "**Coperta ++** = coperta molto pesante/ più coperte medie;   "
    "**Coperta +++** = coperta imbottita pesante (es piumino invernale);   "
    "**Coperta ++++** = molti strati di coperte;   "
    "**Foglie ++** = strato medio di foglie su corpo/vestiti;   "
    "**Foglie +++** = strato spesso di foglie."
)


HELP_VESTITI = (
    "**Tenere conto solo degli indumenti che coprono la parte bassa di torace/addome**.   "
    "**Strati sottili** = t-shirt, camicia, maglia leggera;    "
    "**Strati spessi** = maglione, felpa in pile, giubbino;   "
    "**˃ strati** = ˃4 sottili o ˃2 spessi;   "
    "**˃˃ strati** = molti strati pesanti,"
)

HELP_SUPERFICIE = (
    "**Indifferente** = pavimento di casa/parquet, prato o terreno asciutto, asfalto;   "
    "**Isolante** = materasso, tappeto spesso;   "
    "**Molto isolante** = polistirolo, sacco a pelo tecnico, divano imbottito;   "
    "**Conduttivo** = cemento, pietra, pavimento in PVC, pavimentazione esterna;   "
    "**Molto conduttivo** = superficie metallica spessa all’esterno;   "
    "**Foglie umide/secche (≥2 cm)** = adagiato su strato di foglie"
)

HELP_CORRENTI_ARIA = (
    "**Sì** = all'aria aperta, finestra aperta con aria corrente, ventilatore;   "
    "**No** = ambiente chiuso/nessuna corrente percepibile"
)



# =========================
# Utility cache per Excel
# =========================

@st.cache_data
def load_tabelle_correzione():
    """
    Carica e normalizza le tabelle usate da calcola_fattore.
    Restituisce (tabella1, tabella2) o solleva eccezione con messaggio chiaro.
    """
    try:
        t1 = pd.read_excel("tabella rielaborata.xlsx", engine="openpyxl")
        t2 = pd.read_excel("tabella secondaria.xlsx", engine="openpyxl")
    except FileNotFoundError:
        raise
    except ImportError as e:
        raise RuntimeError("Il pacchetto 'openpyxl' è richiesto per leggere i file Excel.") from e

    t1['Fattore'] = pd.to_numeric(t1['Fattore'], errors='coerce')
    for col in ["Ambiente", "Vestiti", "Coperte", "Superficie d'appoggio", "Correnti"]:
        t1[col] = t1[col].astype(str).str.strip()
    return t1, t2

# =========================
# Funzioni esistenti (con fix robustezza)
# =========================

def calcola_fattore(peso: float):
    """
    Nuova implementazione del calcolo del Fattore di Correzione (motore 'delta' + Tabella 2).
    - Usa il peso della maschera generale (argomento 'peso').
    - Non introduce campi peso duplicati.
    - Presenta i risultati con lo stesso layout attuale.
    - Bottone '✅ Usa questo fattore' con identica funzionalità.
    - La parentetica rimane gestita a valle (qui resettiamo i placeholder come fai già).
    """
    import math
    import unicodedata
    import pandas as pd
    import streamlit as st

    # -------------------------
    # Helpers (motore 'delta')
    # -------------------------
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
    # =========================
    # Superfici — categorie canoniche (nuovo)
    # =========================
    SURF_INDIFF = "INDIFFERENTE"
    SURF_ISOL   = "ISOLANTE"
    SURF_MOLTOI = "MOLTO_ISOLANTE"
    SURF_COND   = "CONDUTTIVO"
    SURF_MOLTOC = "MOLTO_CONDUTTIVO"
    SURF_FOGLIU = "FOGLIE_UMIDE"
    SURF_FOGLIS = "FOGLIE_SECCHE"

    # Etichette mostrate all’utente → chiave canonica
    SURF_DISPLAY_TO_KEY = {
        # Indifferente
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

    # Ordine preferito per la select/radio
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
            if not (stato == "Asciutto" and is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)):
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

    def bagnato_base_senza_correnti(n_sottili: int, n_spessi: int) -> float:
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
        if n_spessi >= 2 or n_sottili >= 4:
            return 0.90
        if (n_spessi == 1 and n_sottili == 1) or (n_sottili == 3 and n_spessi == 0):
            return 0.80
        if (n_spessi == 1 and n_sottili == 0) or (n_sottili == 2 and n_spessi == 0):
            return 0.75
        if (n_sottili == 1 and n_spessi == 0):
            return 0.70
        return 0.70

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
        def is_poco_vestito(fvc: float) -> bool:
            return (1.0 < fvc < 1.2)

        if stato == "Bagnato":
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

        nudo_asciutto = (stato == "Asciutto" and is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti))
        poco_vest     = (stato == "Asciutto" and is_poco_vestito(fattore_vestiti_coperte))

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

    # -------------------------------------
    # Lettura scelte dalla UI (session_state)
    # -------------------------------------
      # --- CSS compatto per radio/toggle/slider (stile "delta") ---
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
        # -------------------------------------
    # 1) Condizione del corpo (label nascosta via CSS globale)
    # -------------------------------------
    stato_label = st.radio("dummy", ["Corpo asciutto", "Bagnato", "Immerso"], index=0, horizontal=True, key="radio_stato_corpo")
    stato_corpo = "Asciutto" if stato_label == "Corpo asciutto" else ("Bagnato" if stato_label == "Bagnato" else "Immerso")
    corpo_immerso  = (stato_corpo == "Immerso")
    corpo_bagnato  = (stato_corpo == "Bagnato")
    corpo_asciutto = (stato_corpo == "Asciutto")

     # -------------------------------------
    # Caso IMMERSO: scelta acqua + output + early return
    # -------------------------------------
    if corpo_immerso:
        # label nascosta dal tuo CSS globale
        acqua_label = st.radio(
            "dummy",
            ["In acqua stagnante", "In acqua corrente"],
            index=0,
            horizontal=True,
            key="radio_acqua"
        )

        # Fattori per l'acqua (coerenti con il motore 'delta')
        fattore_base = 0.50 if acqua_label == "In acqua stagnante" else 0.35
        fattore_finale = max(0.35, min(3.0, float(fattore_base)))  # clamp

        # Presentazione risultata come quando non c'è correzione peso (valore < 1.4)
        st.markdown(
            f"<div style='background-color:#e6f4ea; padding:10px; border-radius:5px;'>"
            f"Fattore di correzione suggerito: {fattore_finale:.2f}"
            f"</div>",
            unsafe_allow_html=True
        )

        # Bottone "Usa questo fattore" con la stessa funzionalità
        def _apply_fattore(val):
            st.session_state["fattore_correzione"] = round(float(val), 2)
            # reset parentetica (come nel tuo codice)
            st.session_state["fattori_condizioni_parentetica"] = None
            st.session_state["fattori_condizioni_testo"] = None
            # chiudi il pannello suggerimento
            st.session_state["toggle_fattore"] = False
            # riepilogo minimale per futura parentetica
            st.session_state["fc_riassunto_contatori"] = {
                "stato": "Immerso",
                "sottili": 0, "spessi": 0, "cop_medie": 0, "cop_pesanti": 0,
                "superficie": "/",
                "correnti": acqua_label,  # "In acqua stagnante"/"In acqua corrente"
            }

        st.button(
            "✅ Usa questo fattore",
            key="usa_fattore_btn",
            on_click=_apply_fattore,
            args=(fattore_finale,),
            use_container_width=True
        )

        return  # esci: niente vestiti/superficie/correnti d'aria quando Immerso
            
        # -------------------------------------
    # 3) Correnti + Vestiti sulla stessa riga
    #    - placeholder a sinistra per correnti
    #    - toggle "Vestito/coperto?" a destra
    # -------------------------------------
    col_corr, col_vest = st.columns([1.0, 1.3])
    with col_corr:
        corr_placeholder = st.empty()
    with col_vest:
        toggle_vestito = st.toggle(
            "Vestito/coperto?",
            value=st.session_state.get("toggle_vestito", False),
            key="toggle_vestito"
        )

    # -------------------------------------
        # -------------------------------------
    # 4) Slider vestizione (se ON)
    # -------------------------------------
    n_sottili_eq = n_spessi_eq = n_cop_medie = n_cop_pesanti = 0
    if toggle_vestito:
        col_layers, col_blankets = st.columns(2)
        with col_layers:
            n_sottili_eq = st.slider(
                "Strati leggeri (indumenti o teli sottili)",
                0, 8, st.session_state.get("strati_sottili", 0),
                key="strati_sottili"
            )
            n_spessi_eq = st.slider(
                "Strati pesanti (indumenti o teli spessi)",
                0, 6, st.session_state.get("strati_spessi", 0),
                key="strati_spessi"
            )
        with col_blankets:
            if corpo_asciutto:
                n_cop_medie = st.slider(
                    "Coperte di medio spessore",
                    0, 5, st.session_state.get("coperte_medie", 0),
                    key="coperte_medie"
                )
                n_cop_pesanti = st.slider(
                    "Coperte pesanti",
                    0, 5, st.session_state.get("coperte_pesanti", 0),
                    key="coperte_pesanti"
                )

    # Calcolo SEMPRE il fattore vestizione+coperte (serve per la visibilità del toggle correnti)
    fattore_vestiti_coperte = calcola_fattore_vestiti_coperte(
        n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
    )

    # -------------------------------------
    # Correnti d'aria nel placeholder di sinistra
    # - se ASCIUTTO e fattore >= 1.2 → nascondi toggle
    # - altrimenti mostra toggle
    # - BAGNATO: mostra toggle (logica specifica in applica_correnti)
    # - IMMERSO: gestito altrove con radio dell'acqua
    # -------------------------------------
    correnti_presenti = False
    if not corpo_immerso:
        with corr_placeholder.container():
            if (corpo_asciutto and (fattore_vestiti_coperte >= 1.2)):
                correnti_presenti = False
                st.empty()
            else:
                correnti_presenti = st.toggle(
                    "Correnti d'aria presenti?",
                    value=st.session_state.get("toggle_correnti_fc", False),
                    key="toggle_correnti_fc",
                    disabled=False
                )

    # Superficie (solo asciutto)
    superficie_key = None
    superficie_display_selected = "/"
    if corpo_asciutto:
        # nudo effettivo = toggle vestito OFF oppure tutti i contatori a zero
        nudo_eff = (not toggle_vestito) or is_nudo(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)

        # Opzioni disponibili: includo "Superficie metallica spessa (all’aperto)" solo se nudo
        options_display = SURF_DISPLAY_ORDER.copy()
        if not nudo_eff:
            options_display = [o for o in options_display if o != "Superficie metallica spessa (all’aperto)"]

        # mantieni la selezione precedente se ancora valida
        prev_display = st.session_state.get("superficie_display_sel")
        if prev_display not in options_display:
            prev_display = options_display[0]

        # puoi usare selectbox (come nel delta) oppure radio; qui uso selectbox per non “esplodere” in orizzontale
        superficie_display_selected = st.selectbox(
            "Superficie di appoggio",
            options_display,
            index=options_display.index(prev_display),
            key="superficie_display_sel"
        )
        superficie_key = SURF_DISPLAY_TO_KEY.get(superficie_display_selected, SURF_INDIFF)
    else:
        st.empty()
        
    # -------------------------
    # Calcolo fattore (delta)
    # -------------------------
    if corpo_immerso:
        # Valori fissi come nel motore delta
        fattore_base = 0.35 if (st.session_state.get("radio_acqua") == "In acqua corrente") else 0.50
    else:
        fatt_vest_cop = calcola_fattore_vestiti_coperte(n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti)
        fatt_tmp = float(fatt_vest_cop)
        if corpo_asciutto and superficie_key is not None:
            fatt_tmp = applica_regole_superficie(
                fatt_tmp, superficie_key, stato_corpo,
                n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti
            )
        fattore_base, _ = applica_correnti(
            clamp(fatt_tmp), stato_corpo, superficie_key, correnti_presenti,
            n_sottili_eq, n_spessi_eq, n_cop_medie, n_cop_pesanti,
            fatt_vest_cop
        )
        if math.isnan(fattore_base):
            fattore_base = 1.0
        fattore_base = clamp(float(fattore_base))

    # --------------------------------
    # Tabella 2: adattamento per peso
    # --------------------------------
    fattore_finale = float(fattore_base)
    try:
        if fattore_base >= 1.4 and float(peso) != 70.0:
            # Usa il tuo loader già presente nel file base
            _, tabella2 = load_tabelle_correzione()

            def parse_peso(col):
                s = str(col).strip().lower().replace('kg', '').replace('w', '')
                num = ''.join(ch for ch in s if (ch.isdigit() or ch in '.,'))
                num = num.replace(',', '.')
                return float(num) if num not in ("", ".", ",") else None

            pesi_col = {col: parse_peso(col) for col in tabella2.columns}
            pesi_col = {col: w for col, w in pesi_col.items() if w is not None}
            if not pesi_col:
                raise ValueError("Nessuna colonna peso valida in Tabella 2.")

            # Colonna 70 kg (la più vicina a 70)
            col_70 = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - 70.0))
            serie70 = pd.to_numeric(tabella2[col_70], errors='coerce')

            # Riga del valore più vicino al fattore_base nella colonna 70 kg
            idx_match = (serie70 - fattore_base).abs().idxmin()

            # Colonna del peso più vicino all'utente
            col_user = min(pesi_col.keys(), key=lambda c: abs(pesi_col[c] - float(peso)))

            # Valore adattato
            val_user = pd.to_numeric(tabella2.loc[idx_match, col_user], errors='coerce')
            if pd.notna(val_user):
                fattore_finale = clamp(float(val_user))
    except FileNotFoundError:
        st.warning("Impossibile applicare la correzione per il peso: file 'tabella secondaria.xlsx' non trovato. Uso il valore per 70 kg.")
    except Exception as e:
        st.warning(f"Impossibile applicare la correzione per il peso (uso il valore per 70 kg): {e}")

    # ---------------
    # Presentazione UI
    # ---------------
    if abs(fattore_finale - fattore_base) > 1e-9:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(
                f'<div style="background-color:#e6f4ea; padding:10px; border-radius:5px;">'
                f'Fattore di correzione (adattato per peso {float(peso):.1f} kg): {fattore_finale:.2f}'
                f'</div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<div style="color:gray; padding:10px;">Valore per 70 kg: {fattore_base:.2f}</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f'<div style="background-color:#e6f4ea; padding:10px; border-radius:5px;">'
            f'Fattore di correzione suggerito: {fattore_finale:.2f}'
            f'</div>',
            unsafe_allow_html=True
        )

    # ------------------------------
    # 
    
    # ------------------------------
    # Bottone: "Usa questo fattore"
    # ------------------------------
    def _apply_fattore(val):
        st.session_state["fattore_correzione"] = round(float(val), 2)
        # placeholders per parentetica (come nel tuo codice attuale)
        st.session_state["fattori_condizioni_parentetica"] = None
        st.session_state["fattori_condizioni_testo"] = None
        # chiude il pannello
        st.session_state["toggle_fattore"] = False

        # --- recupero sicuro dei campi UI usati nel riepilogo ---
        # Superficie (nuovo selectbox -> fallback vecchio radio -> "/")
        superficie_label_sel = (
            st.session_state.get("superficie_display_sel")
            or st.session_state.get("radio_superficie")
            or "/"
        )

        # Correnti: aria (toggle_correnti_fc) o acqua (radio_acqua)
        correnti_air_flag = bool(st.session_state.get("toggle_correnti_fc", False))
        acqua_sel = st.session_state.get("radio_acqua")  # "In acqua stagnante"/"In acqua corrente"/None

        correnti_descr = (
            "In acqua corrente" if acqua_sel == "In acqua corrente"
            else "In acqua stagnante" if acqua_sel == "In acqua stagnante"
            else ("Correnti d'aria presenti" if correnti_air_flag else "Senza correnti d'aria")
        )

        # Salva in sessione un riassunto minimale conforme al nuovo modello (contatori)
        st.session_state["fc_riassunto_contatori"] = {
            "stato": stato_corpo,  # "Asciutto"/"Bagnato"/"Immerso"
            "sottili": int(n_sottili_eq),
            "spessi": int(n_spessi_eq),
            "cop_medie": int(n_cop_medie),
            "cop_pesanti": int(n_cop_pesanti),
            "superficie": superficie_label_sel if corpo_asciutto else "/",
            "correnti": correnti_descr,
        }

    st.button(
        "✅ Usa questo fattore",
        key="usa_fattore_btn",
        on_click=_apply_fattore,
        args=(fattore_finale,),
        use_container_width=True
        )




def arrotonda_quarto_dora(dt: datetime.datetime) -> datetime.datetime:
    """Arrotonda un datetime al quarto d’ora più vicino."""
    minuti = (dt.minute + 7) // 15 * 15
    if minuti == 60:
        dt += datetime.timedelta(hours=1)
        minuti = 0
    return dt.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=minuti)

def _split_hours_minutes(h: float):
    """Converte ore decimali in (ore, minuti) arrotondando correttamente, evitando '60 minuti'."""
    if h is None or (isinstance(h, float) and np.isnan(h)):
        return None
    total_minutes = int(round(h * 60))
    hours, minutes = divmod(total_minutes, 60)
    return hours, minutes

# Titolo più piccolo e con peso medio
st.markdown("<h5 style='margin-top:0; margin-bottom:10px;'>Stima epoca decesso</h5>", unsafe_allow_html=True)



# --- Dati per Macchie Ipostatiche e Rigidità Cadaverica (Esistenti) ---
opzioni_macchie = {
    "Non ancora comparse": (0, 3),
    "Migrabilità totale": (0, 6),
    "Migrabilità parziale": (4, 24),
    "Migrabilità perlomeno parziale": (0, 24),
    "Fissità assoluta": (10, INF_HOURS),
    "Non valutabili/Non attendibili": None
}
macchie_medi = {
    "Non ancora comparse": (0, 0.33),
    "Migrabilità totale": (0.33, 6),
    "Migrabilità parziale": (6, 12),
    "Migrabilità perlomeno parziale": None,
    "Fissità assoluta": (12, INF_HOURS),
    "Non valutabili/Non attendibili": None
}
testi_macchie = {
    "Non ancora comparse": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, non fossero ancora comparse. Secondo le comuni nozioni della medicina legale, le ipostasi compaiono entro 3 ore dal decesso (generalmente entro 15-20 minuti).",
    "Migrabilità totale": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero in una fase di migrabilità totale. Secondo le comuni nozioni della medicina legale, tale fase indica che fossero trascorse meno di 6 ore dal decesso. Generalmente le ipostasi compaiono dopo 20 minuti dal decesso.",
    "Migrabilità parziale": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero in una fase di migrabilità parziale. Secondo le comuni nozioni della medicina legale, tale fase indica che fossero trascorse tra le 4 ore e le 24 ore dal decesso.",
    "Migrabilità perlomeno parziale": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero in una fase di migrabilità perlomeno parziale (modificando la posizione del cadavere si sono modificate le macchie ipostatiche, ma, per le modalità e le tempistiche di esecuzione dell’ispezione legale, non è stato possibile dettagliare l’entità del fenomeno). Secondo le comuni nozioni della medicina legale, tale fase indica che fossero trascorse meno di 24 ore dal decesso.",
    "Fissità assoluta": "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero in una fase di fissità assoluta. Secondo le comuni nozioni della medicina legale, tale fase indica che fossero trascorse più di 10 ore dal decesso (fino a 30 ore le macchie possono non modificare la loro posizione alla movimentazione del corpo, ma la loro intensità può affievolirsi).",
    "Non valutabili/Non attendibili": "Le macchie ipostatiche non sono state valutate o i rilievi non sono considerati attendibili per la stima dell'epoca della morte."
}

opzioni_rigidita = {
    "Non ancora comparsa": (0, 7),
    "In via di formazione, intensificazione e generalizzazione": (0.5, 20),
    "Presente e generalizzata": (2, 96),
    "In via di risoluzione": (24, 192),
    "Ormai risolta": (24, INF_HOURS),
    "Non valutabile/Non attendibile": None
}
rigidita_medi = {
    "Non ancora comparsa": (0, 3),
    "In via di formazione, intensificazione e generalizzazione": (2, 10),
    "Presente e generalizzata": (10, 85),
    "In via di risoluzione": (29, 140),
    "Ormai risolta": (76, INF_HOURS)
}
rigidita_descrizioni = {
    "Non ancora comparsa": "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, non fosse ancora comparsa. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorse meno di 7 ore dal decesso (in genere la rigidità compare entro 2 - 3 ore dal decesso).",
    "In via di formazione, intensificazione e generalizzazione": "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse in via di formazione, intensificazione e generalizzazione. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorsi almeno 30 minuti dal decesso ma meno di 20 ore da esso (generalmente la formazione della rigidità si completa in 6-10 ore).",
    "Presente e generalizzata": "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse presente e generalizzata. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorse almeno 2 ore dal decesso ma meno di 96 ore da esso, cioè meno di 4 giorni (in genere la rigidità persiste sino a 29 – 85 ore).",
    "In via di risoluzione": "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse in via di risoluzione. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorse almeno 24 ore dal decesso ma meno di 192 ore da esso, cioè meno di 8 giorni (in genere la rigidità cadaverica inizia a risolversi dopo 57 ore, cioè dopo 2 giorni e mezzo dal decesso).",
    "Ormai risolta": "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse ormai risolta. Secondo le comuni nozioni della medicina legale, tali caratteristiche suggeriscono che fossero trascorse almeno 24 ore dal decesso (in genere la rigidità scompare entro 76 ore dal decesso, cioè dopo poco più  di 3 giorni).",
    "Non valutabile/Non attendibile": "La rigidità cadaverica non è stata valutata o i rilievi non sono considerati attendibili per la stima dell'epoca della morte."
}

# --- Dati per i Nuovi Parametri Aggiuntivi ---
dati_parametri_aggiuntivi = {
    "Eccitabilità elettrica sopraciliare": {
        "opzioni": ["Non valutata", "Fase I", "Fase II", "Fase III", "Fase IV", "Fase V", "Fase VI", "Nessuna reazione", "Non valutabile/non attendibile"],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (5, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Fase VI": (1, 6),
            "Fase V": (2, 7),
            "Fase IV": (3, 8),
            "Fase III": (3.5, 13),
            "Fase II": (5, 16),
            "Fase I": (5, 22),
                    },
         "descrizioni": {
             "Fase VI": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata dei muscoli della fronte, dell’orbita, della guancia. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra 1 e 6 ore prima delle valutazioni del dato tanatologico.",
             "Fase V": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata dei muscoli della fronte e dell’orbita. Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il decesso fosse avvenuto tra le 2 e le 7 ore prima delle valutazioni del dato tanatologico.",
             "Fase IV": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata dei muscoli orbicolari (superiori e inferiori). Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il decesso fosse avvenuto tra le 3 e le 8 ore prima delle valutazioni del dato tanatologico.",
             "Fase III": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione dei muscoli dell’intera palpebra superiore. Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il decesso fosse avvenuto tra le 3 ore e 30 minuti e le 13 ore prima delle valutazioni del dato tanatologico.",
             "Fase II": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione dei muscoli di meno di 2/3 della palpebra superiore. Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il decesso fosse avvenuto tra le 5 e le 16 ore prima delle valutazioni del dato tanatologico.",
             "Fase I": "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione accennata di una minima porzione della palpebra superiore (meno di 1/3). Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra le 5 e le 22 ore prima delle valutazioni del dato tanatologico.",
             "Non valutabile/non attendibile": "Non è stato possibile valutare l'eccitabilità muscolare elettrica residua sopraciliare o il suo rilievo non è da considerarsi attendibile.",
             "Nessuna reazione": "L’applicazione di uno stimolo elettrico in regione sopraciliare non ha prodotto contrazioni muscolari. Tale risultato permette solamente di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse più di 5 ore dal decesso"
         }
    },
    "Eccitabilità elettrica peribuccale": {
        "opzioni": ["Non valutata", "Marcata ed estesa (+++)", "Discreta (++)", "Accennata (+)", "Nessuna reazione", "Non valutabile/non attendibile"],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (6, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Marcata ed estesa (+++)": (0, 2.5), # 2 ore 30 minuti = 2.5 ore
            "Discreta (++)": (1, 5),
            "Accennata (+)": (2, 6)
        },
        "descrizioni": {
            "Marcata ed estesa (+++)": "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione marcata ai muscoli peribuccali e ai muscoli facciali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto meno di 2 ore e mezzo prima delle valutazioni del dato tanatologico.",
            "Discreta (++)": "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione discreta ai muscoli peribuccali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra 1 e 5 ore prima delle valutazioni del dato tanatologico.",
            "Accennata (+)": "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione solo accennata dei muscoli peribuccali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra le 2 e le 6 ore prima delle valutazioni del dato tanatologico.",
            "Non valutabile/non attendibile": "Non è stato possibile valutare l'eccitabilità muscolare elettrica residua peribuccale o i rilievi non sono attendibili per la stima dell'epoca della morte.",
            "Nessuna reazione": "L’applicazione di uno stimolo elettrico in regione peribuccale non ha prodotto contrazioni muscolari. Tale risultato permette solamente di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse più di 6 ore dal decesso."
        }
    },
    "Eccitabilità muscolare meccanica": {
        "opzioni": ["Non valutata", "Contrazione reversibile dell’intero muscolo", "Formazione di una tumefazione reversibile", "Formazione di una piccola tumefazione persistente", "Nessuna reazione", "Non valutabile/non attendibile"],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (1.5, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Formazione di una piccola tumefazione persistente": (0, 12), # Meno di 12 ore = 0-12 (Henssge dice 13)
            "Formazione di una tumefazione reversibile": (2, 5),
            "Contrazione reversibile dell’intero muscolo": (0, 2)   # Meno di 2 ore = 0-2
        },
         "descrizioni": {
             "Formazione di una piccola tumefazione persistente": "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione di una piccola tumefazione persistente del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce che il decesso fosse avvenuto meno di 12 ore prima delle valutazioni del dato tanatologico.",
             "Formazione di una tumefazione reversibile": "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione di una tumefazione reversibile del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce che il decesso fosse avvenuto tra le 2 e le 5 ore prima delle valutazioni del dato tanatologico.",
             "Contrazione reversibile dell’intero muscolo": "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla contrazione reversibile dell’intero muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce che il decesso fosse avvenuto meno di 2 ore prima delle valutazioni del dato tanatologico.",
             "Non valutabile/non attendibile": "Non è stato possibile valutare l'eccitabilità muscolare meccanica o i rilievi non sono attendibili per la stima dell'epoca della morte.",
             "Nessuna reazione": "L’applicazione di uno stimolo meccanico al muscolo del braccio non ha prodotto contrazioni muscolari evidenti. Tale risultato permette solamente di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse più di 1 ora e 30 minuti dal decesso."
         }
    },
    "Eccitabilità chimica pupillare": {
        "opzioni": ["Non valutata", "Non valutabile/non attendibile","Positiva", "Negativa"],
        "range": {
            "Non valutata": None,
            "Non valutabile/non attendibile": None,
            "Positiva": (0, 30), # Meno di 30 ore = 0-30
            "Negativa": (5, INF_HOURS) # Più di 5 ore. Usiamo un limite superiore elevato (200h) per il grafico e i calcoli, coerente con gli altri range massimi.(con atropina hansegee dice 3- 10
        },
         "descrizioni": {
             "Positiva": "L’eccitabilità pupillare chimica residua, nel momento dell’ispezione legale, era caratterizzata da una risposta dei muscoli pupillari dell’occhio (con aumento del diametro della pupilla) all’instillazione intraoculare di atropina. Tale reazione suggerisce che il decesso fosse avvenuto meno di 30 ore prima delle valutazioni medico legali.",
             "Negativa": "L’eccitabilità pupillare chimica residua, nel momento dell’ispezione legale, era caratterizzata da una assenza di risposta dei muscoli pupillari dell’occhio (con aumento del diametro della pupilla) all'instillazione intraoculare di atropina. Tale reazione suggerisce che il decesso fosse avvenuto più di 5 ore prima delle valutazioni medico legali.",
             "Non valutabile/non attendibile": "L'eccitabilità chimica pupillare non era valutabile o i rilievi non sono considerati attendibili per la stima dell'epoca della morte."
         }
    }
}
nomi_brevi = {
    "Macchie ipostatiche": "Ipostasi",
    "Rigidità cadaverica": "Rigor",
    "Raffreddamento cadaverico": "Raffreddamento",
    "Eccitabilità elettrica peribuccale": "Ecc. elettrica peribuccale",
    "Eccitabilità elettrica sopraciliare": "Ecc. elettrica sopraciliare",
    "Eccitabilità chimica pupillare": "Ecc. pupillare",
    "Eccitabilità muscolare meccanica": "Ecc. meccanica"
}

# --- Funzioni di Utilità e Calcolo Henssge (Esistenti) ---
def round_quarter_hour(x):
    if np.isnan(x):
        return np.nan
    return np.round(x * 2) / 2

def calcola_raffreddamento(Tr, Ta, T0, W, CF):
    # Controllo per temperature non valide per il calcolo di Henssge
    if Tr is None or Ta is None or T0 is None or W is None or CF is None:
         return np.nan, np.nan, np.nan, np.nan, np.nan # Restituisce 5 NaN
    #
    # Considera non valido se Tr è "molto vicino" o inferiore a Ta
    temp_tolerance = 1e-6
    if Tr <= Ta + temp_tolerance:
        return np.nan, np.nan, np.nan, np.nan, np.nan # Restituisce 5 NaN
    # Controllo esplicito per evitare divisione per zero nel calcolo di Qd
    if abs(T0 - Ta) < temp_tolerance: # Controlla se il denominatore è molto vicino a zero
         return np.nan, np.nan, np.nan, np.nan, np.nan # Restituisce 5 NaN

    # Ora calcola Qd solo se i controlli iniziali sono passati
    Qd = (Tr - Ta) / (T0 - Ta)

    # Assicurati che Qd sia un valore valido e rientri in un range plausibile (es. > 0 e <= 1)
    if np.isnan(Qd) or Qd <= 0 or Qd > 1:
         return np.nan, np.nan, np.nan, np.nan, np.nan # Restituisce 5 NaN

    A = 1.25 if Ta <= 23 else 10/9
    B = -1.2815 * (CF * W)**(-5/8) + 0.0284

    def Qp(t):
        try:
            if t < 0:
                return np.inf
            val = A * np.exp(B * t) + (1 - A) * np.exp((A / (A - 1)) * B * t)
            if np.isinf(val) or abs(val) > 1e10:
                 return np.nan
            return val
        except OverflowError:
             return np.nan
        except Exception:
             return np.nan

    t_med_raw = np.nan

    qp_at_0 = Qp(0)
    qp_at_160 = Qp(160)

    eps = 1e-9
    if np.isnan(qp_at_0) or np.isnan(qp_at_160) or not (min(qp_at_160, qp_at_0) - eps <= Qd <= max(qp_at_160, qp_at_0) + eps):
        t_med_raw = np.nan
    else:
         try:
             sol = root_scalar(lambda t: Qp(t) - Qd, bracket=[0, 160], method='bisect')
             t_med_raw = sol.root
         except ValueError:
             t_med_raw = np.nan
         except Exception:
             t_med_raw = np.nan

    Dt_raw = 0

    if not np.isnan(t_med_raw) and not np.isnan(Qd):
         if Qd <= 0.2:
              Dt_raw = t_med_raw * 0.20
         elif CF == 1:
              Dt_raw = 2.8 if Qd > 0.5 else 3.2 if Qd > 0.3 else 4.5
         else: # CF != 1
              Dt_raw = 2.8 if Qd > 0.5 else 4.5 if Qd > 0.3 else 7

    t_med = round_quarter_hour(t_med_raw) if not np.isnan(t_med_raw) else np.nan
    t_min = round_quarter_hour(t_med_raw - Dt_raw) if not np.isnan(t_med_raw) else np.nan
    t_max = round_quarter_hour(t_med_raw + Dt_raw) if not np.isnan(t_med_raw) else np.nan

    t_min = max(0.0, t_min) if not np.isnan(t_min) else np.nan

    return t_med, t_min, t_max, t_med_raw, Qd

def ranges_in_disaccordo_completa(r_inizio, r_fine):
    intervalli = []
    for start, end in zip(r_inizio, r_fine):
        s = start if not np.isnan(start) else -np.inf
        e = end if not np.isnan(end) else np.inf
        intervalli.append((s, e))

    for i, (s1, e1) in enumerate(intervalli):
        si_sovrappone = False
        for j, (s2, e2) in enumerate(intervalli):
            if i == j:
                continue
            if s1 <= e2 and s2 <= e1:
                si_sovrappone = True
                break
        if not si_sovrappone:
            return True  # almeno uno è completamente isolato
    return False

# --- Definizione Widget (Streamlit) ---
with st.container(border=True):
    
    # 📌 1. Data e ora ispezione legale
    st.markdown("<div style='font-size: 0.88rem;'>Data e ora dei rilievi tanatologici:</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="small")
    with col1:
        input_data_rilievo = st.date_input("Data ispezione legale:", value=datetime.date.today(), label_visibility="collapsed")

    with col2:
        input_ora_rilievo = st.text_input(
            "Ora ispezione legale (HH:MM):",
            value="00:00",
            label_visibility="collapsed"
        )

# 📌 2. Ipostasi e rigidità (2 colonne stessa riga) — RIQUADRO
with st.container(border=True):
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>Ipostasi:</div>", unsafe_allow_html=True)
        selettore_macchie = st.selectbox("Macchie ipostatiche:", options=list(opzioni_macchie.keys()), label_visibility="collapsed")
    with col2:
        st.markdown("<div style='font-size: 0.88rem;'>Rigidità cadaverica:</div>", unsafe_allow_html=True)
        selettore_rigidita = st.selectbox("Rigidità cadaverica:", options=list(opzioni_rigidita.keys()), label_visibility="collapsed")



# 📌 3–4. Temperature + Peso/Fattore — RIQUADRO
with st.container(border=True):

    # 📌 3. Temperature (3 colonne gap small)
    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>T. rettale (°C):</div>", unsafe_allow_html=True)
        input_rt = st.number_input("T. rettale (°C):", value=35.0, step=0.1, format="%.1f", label_visibility="collapsed")
    with col2:
        st.markdown("<div style='font-size: 0.88rem;'>T. ambientale media (°C):</div>", unsafe_allow_html=True)
        input_ta = st.number_input("T. ambientale (°C):", value=20.0, step=0.1, format="%.1f", label_visibility="collapsed")
    with col3:
        st.markdown("<div style='font-size: 0.88rem;'>T. ante-mortem stimata (°C):</div>", unsafe_allow_html=True)
        input_tm = st.number_input("T. ante-mortem stimata (°C):", value=37.2, step=0.1, format="%.1f", label_visibility="collapsed")

    # 📌 4. Peso + Fattore di correzione + pulsante "Suggerisci" (mini-link)
    col1, col2 = st.columns([1, 3], gap="small")
    with col1:
        st.markdown("<div style='font-size: 0.88rem;'>Peso corporeo (kg):</div>", unsafe_allow_html=True)
        input_w = st.number_input("Peso (kg):", value=70.0, step=1.0, format="%.1f", label_visibility="collapsed")
        st.session_state["peso"] = input_w

    with col2:
        subcol1, subcol2 = st.columns([1.5, 1], gap="small")
        with subcol1:
            st.markdown("<div style='font-size: 0.88rem;'>Fattore di correzione (FC):</div>", unsafe_allow_html=True)
            fattore_correzione = st.number_input(
                "Fattore di correzione:",
                step=0.1,
                format="%.2f",
                label_visibility="collapsed",
                key="fattore_correzione"
            )

        with subcol2:
            mostra_fattore = st.toggle(
                "Suggerisci FC",
                value=st.session_state.get("toggle_fattore", False),
                key="toggle_fattore"
            )

# — Pannello suggerimento FC a tutta pagina —
if st.session_state.get("toggle_fattore", False):
    with st.container(border=True):
        calcola_fattore(peso=st.session_state.get("peso", 70))
        







# Pulsante per mostrare/nascondere i parametri aggiuntivi
mostra_parametri_aggiuntivi = st.checkbox("Aggiungi dati tanatologici speciali")

widgets_parametri_aggiuntivi = {}

if mostra_parametri_aggiuntivi:
    with st.container(border=True):  # bordo come per "Suggerisci fattore di correzione"
        for nome_parametro, dati_parametro in dati_parametri_aggiuntivi.items():
            col1, col2 = st.columns([1, 2], gap="small")
            with col1:
                subcol1, subcol2 = st.columns([1, 0.5])
                with subcol1:
                    st.markdown(
                        f"<div style='font-size: 0.88rem; padding-top: 0.4rem;'>{nome_parametro}:</div>",
                        unsafe_allow_html=True
                    )
                with subcol2:
                    if nome_parametro in ["Eccitabilità elettrica sopraciliare", "Eccitabilità elettrica peribuccale"]:
                        with st.popover(" "):  # trigger invisibile ma associato alla posizione del testo
                            if nome_parametro == "Eccitabilità elettrica sopraciliare":
                                st.image(
                                    "https://raw.githubusercontent.com/scopusjin/codice/main/immagini/eccitabilit%C3%A0.PNG",
                                    width=400
                                )
                            elif nome_parametro == "Eccitabilità elettrica peribuccale":
                                st.image(
                                    "https://raw.githubusercontent.com/scopusjin/codice/main/immagini/peribuccale.PNG",
                                    width=300
                                )
            with col2:
                selettore = st.selectbox(
                    label=nome_parametro,
                    options=dati_parametro["opzioni"],
                    key=f"{nome_parametro}_selector",
                    label_visibility="collapsed"
                )

            data_picker = None
            ora_input = None
            usa_orario_personalizzato = False

            if selettore != "Non valutata":
                chiave_checkbox = f"{nome_parametro}_diversa"
                col1, col2 = st.columns([0.2, 0.2], gap="small")
                with col1:
                    st.markdown(
                        "<div style='font-size: 0.8em; color: orange; margin-bottom: 3px;'>"
                        "Il dato è stato valutato a un orario diverso rispetto a quello precedentemente indicato?"
                        "</div>",
                        unsafe_allow_html=True
                    )
                with col2:
                    usa_orario_personalizzato = st.checkbox(
                        label="",
                        key=chiave_checkbox
                    )

            if usa_orario_personalizzato:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Data rilievo:</div>", unsafe_allow_html=True)
                    data_picker = st.date_input(
                        "Data rilievo:",
                        value=input_data_rilievo,
                        key=f"{nome_parametro}_data",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown("<div style='font-size: 0.88rem; padding-top: 0.4rem;'>Ora rilievo:</div>", unsafe_allow_html=True)
                    ora_input = st.text_input(
                        "Ora rilievo (HH:MM):",
                        value=input_ora_rilievo,
                        key=f"{nome_parametro}_ora",
                        label_visibility="collapsed"
                    )

            widgets_parametri_aggiuntivi[nome_parametro] = {
                "selettore": selettore,
                "data_rilievo": data_picker,
                "ora_rilievo": ora_input
            }
        chk_putrefattive = st.checkbox(
            "Alterazioni putrefattive?",
            value=st.session_state.get("alterazioni_putrefattive", False),
        )
        st.session_state["alterazioni_putrefattive"] = chk_putrefattive
else:
    st.session_state["alterazioni_putrefattive"] = False
    
st.markdown("""
    <style>
    div.stButton > button {
        border: 2px solid #2196F3 !important;
        color: black !important;
        background-color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
        padding: 0.6em 2em !important;
    }
    div.stButton > button:hover {
        background-color: #E3F2FD !important;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    pulsante_genera_stima = st.button("STIMA EPOCA DECESSO")


def aggiorna_grafico():
        # --- Raccolta messaggi per nuova UI compatta ---
    avvisi = []              # tutti gli avvisi arancioni
    dettagli = []            # testi lunghi/descrittivi per l’expander
    frase_finale_html = None # “La valutazione complessiva…”
    frase_secondaria_html = None  # eventuale variante “Senza considerare Potente…”

    # --- Validazione Input Data/Ora Ispezione Legale ---
    if not input_data_rilievo or not input_ora_rilievo:
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Inserisci data e ora dell'ispezione legale.</p>", unsafe_allow_html=True)
        return

    try:
        ora_isp_obj = datetime.datetime.strptime(input_ora_rilievo, '%H:%M')
        minuti_isp = ora_isp_obj.minute
    except ValueError:
        st.markdown("<p style='color:red;font-weight:bold;'>⚠️ Errore: Formato ora ispezione legale non valido. Utilizzare il formato HH:MM (es. 14:30).</p>", unsafe_allow_html=True)
        return

    data_ora_ispezione_originale = datetime.datetime.combine(input_data_rilievo, ora_isp_obj.time())
    data_ora_ispezione = arrotonda_quarto_dora(data_ora_ispezione_originale)

    # --- Recupero Valori Input per Calcoli (Esistenti) ---
    Tr_val = input_rt
    Ta_val = input_ta
    T0_val = input_tm
    W_val = input_w
    CF_val = st.session_state.get("fattore_correzione", 1.0)

    # Validazioni extra (robustezza)
    if W_val is None or W_val <= 0:
        st.error("⚠️ Peso non valido. Inserire un valore > 0 kg.")
        return
    if CF_val is None or CF_val <= 0:
        st.error("⚠️ Fattore di correzione non valido. Inserire un valore > 0.")
        return
    if any(v is None for v in [Tr_val, Ta_val, T0_val]):
        st.error("⚠️ Temperature mancanti.")
        return

    macchie_selezionata = selettore_macchie
    rigidita_selezionata = selettore_rigidita

    t_med_raff_hensge_rounded, t_min_raff_hensge, t_max_raff_hensge, t_med_raff_hensge_rounded_raw, Qd_val_check = calcola_raffreddamento(
        Tr_val, Ta_val, T0_val, W_val, CF_val
    )
    qd_threshold = 0.2 if Ta_val <= 23 else 0.5
    raffreddamento_calcolabile = not np.isnan(t_med_raff_hensge_rounded) and t_med_raff_hensge_rounded >= 0

    temp_difference_small = False
    if Tr_val is not None and Ta_val is not None and (Tr_val - Ta_val) is not None and (Tr_val - Ta_val) < 2.0 and (Tr_val - Ta_val) >= 0:
        temp_difference_small = True

    macchie_range_valido = macchie_selezionata != "Non valutabili/Non attendibili"
    macchie_range = opzioni_macchie.get(macchie_selezionata) if macchie_range_valido else (np.nan, np.nan)
    macchie_medi_range = macchie_medi.get(macchie_selezionata) if macchie_range_valido else None

    rigidita_range_valido = rigidita_selezionata != "Non valutabile/Non attendibile"
    rigidita_range = opzioni_rigidita.get(rigidita_selezionata) if rigidita_range_valido else (np.nan, np.nan)
    rigidita_medi_range = rigidita_medi.get(rigidita_selezionata) if rigidita_range_valido else None

    parametri_aggiuntivi_da_considerare = []
    nota_globale_range_adattato = False

    for nome_parametro, widgets_param in widgets_parametri_aggiuntivi.items():
        stato_selezionato = widgets_param["selettore"]
        data_rilievo_param = widgets_param["data_rilievo"]
        ora_rilievo_param_str = widgets_param["ora_rilievo"]

        if stato_selezionato == "Non valutata":
            continue

        chiave_descrizione = stato_selezionato.split(':')[0].strip()

        # Ora param: normalizza a datetime.time e controlla mezz'ora
        if not ora_rilievo_param_str or ora_rilievo_param_str.strip() == "":
            ora_rilievo_time = data_ora_ispezione.time()
        else:
            try:
                ora_rilievo_time = datetime.datetime.strptime(ora_rilievo_param_str, '%H:%M').time()
                
            except ValueError:
                avvisi.append(f"⚠️ {nome_parametro}: formato ora di rilievo '{ora_rilievo_param_str}' non valido (usa HH:MM, es. 14:30) → parametro escluso dalla stima.")
                continue

        # Se data personalizzata assente, usa quella dell’ispezione
        if data_rilievo_param is None:
            data_rilievo_param = data_ora_ispezione.date()

        # Determina la chiave corretta da usare per cercare nel dizionario dei range
        if nome_parametro == "Eccitabilità elettrica peribuccale":
            chiave_descrizione = stato_selezionato.split(':')[0].strip()
        else:
            chiave_descrizione = stato_selezionato.strip()

        # Forza il recupero esatto della chiave anche se ci sono spazi invisibili
        chiave_esatta = None
        for k in dati_parametri_aggiuntivi[nome_parametro]["range"].keys():
            if k.strip() == chiave_descrizione:
                chiave_esatta = k
                break

        range_valori = dati_parametri_aggiuntivi[nome_parametro]["range"].get(chiave_esatta)
        range_originale = range_valori

        if range_valori:
            descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(chiave_descrizione, f"Descrizione non trovata per lo stato '{stato_selezionato}'.")


            data_ora_param_raw = datetime.datetime.combine(data_rilievo_param, ora_rilievo_time)
            data_ora_param = arrotonda_quarto_dora(data_ora_param_raw)
            differenza_ore = (data_ora_param - data_ora_ispezione).total_seconds() / 3600.0
            if range_originale[1] >= INF_HOURS:
                range_traslato = (range_originale[0] - differenza_ore, INF_HOURS)
            else:
                range_traslato = (range_originale[0] - differenza_ore, range_originale[1] - differenza_ore)

            range_traslato_rounded = (round_quarter_hour(range_traslato[0]), round_quarter_hour(range_traslato[1]))
            range_traslato_rounded = (max(0, range_traslato_rounded[0]), range_traslato_rounded[1])

            parametri_aggiuntivi_da_considerare.append({
                "nome": nome_parametro,
                "stato": stato_selezionato,
                "range_traslato": range_traslato_rounded,
                "descrizione": descrizione,
                "differenza_ore": differenza_ore,
                "adattato": differenza_ore != 0
            })

            differenze_ore_set = set(
                p["differenza_ore"]
                for p in parametri_aggiuntivi_da_considerare
                if p.get("adattato")
            )
            nota_globale_range_adattato = len(differenze_ore_set) == 1 and len(differenze_ore_set) > 0

        elif dati_parametri_aggiuntivi[nome_parametro]["range"].get(stato_selezionato) is None:
            descrizione = dati_parametri_aggiuntivi[nome_parametro]["descrizioni"].get(chiave_descrizione, f"Il parametro {nome_parametro} ({stato_selezionato}) non ha un range temporale definito o descrizione specifica.")
            parametri_aggiuntivi_da_considerare.append({
                "nome": nome_parametro,
                "stato": stato_selezionato,
                "range_traslato": (np.nan, np.nan),
                "descrizione": descrizione
            })

    # --- Determinazione Range Raffreddamento per Visualizzazione nel Grafico ---
    # Il range visualizzato per Henssge > 30h sarà un range ±20% attorno a t_med_raw
    t_min_raff_visualizzato = np.nan
    t_max_raff_visualizzato = np.nan

    # --- Definisce i range USATI per l'intersezione (stima complessiva) ---
    ranges_per_intersezione_inizio = []
    ranges_per_intersezione_fine = []
    # Lista per tenere traccia dei nomi dei parametri USATI per l'intersezione
    nomi_parametri_usati_per_intersezione = []

    # Determina se visualizzare il range Henssge sul grafico
    visualizza_hensge_grafico = raffreddamento_calcolabile

    if visualizza_hensge_grafico:
        # Usa i limiti calcolati da calcola_raffreddamento per la visualizzazione
        t_min_raff_visualizzato = t_min_raff_hensge
        t_max_raff_visualizzato = t_max_raff_hensge
    else:
        # Se non visualizzabile, imposta NaN
        t_min_raff_visualizzato = np.nan
        t_max_raff_visualizzato = np.nan

    # --- Fine Determinazione Range Raffreddamento Visualizzazione ---

    # Aggiunge range macchie se valido e presente
    if macchie_range_valido and macchie_range is not None:
        ranges_per_intersezione_inizio.append(macchie_range[0])
        ranges_per_intersezione_fine.append(macchie_range[1])
        nomi_parametri_usati_per_intersezione.append("macchie ipostatiche")

    # Aggiunge range rigidità se valido e presente
    if rigidita_range_valido and rigidita_range is not None:
        ranges_per_intersezione_inizio.append(rigidita_range[0])
        ranges_per_intersezione_fine.append(rigidita_range[1])
        nomi_parametri_usati_per_intersezione.append("rigidità cadaverica")

    # --- Stima minima post mortem secondo Potente et al. ---
    mt_ore = None
    mt_giorni = None
    usa_potente_per_intersezione = False

    if not any(np.isnan(val) for val in [Tr_val, Ta_val, CF_val, W_val]):
        if Tr_val <= Ta_val + 1e-6:
            mt_ore = None
            mt_giorni = None
        else:
            Qd_potente = (Tr_val - Ta_val) / (37.2 - Ta_val)
            if Qd_potente < qd_threshold:
                B_potente = -1.2815 * (CF_val * W_val) ** (-5 / 8) + 0.0284
                ln_term = np.log(0.16) if Ta_val <= 23 else np.log(0.45)
                mt_ore = round(ln_term / B_potente, 1)
                mt_giorni = round(mt_ore / 24, 1)
        usa_potente_per_intersezione = (
            (not np.isnan(Qd_val_check)) and
            (Qd_val_check < qd_threshold) and
            (mt_ore is not None) and (not np.isnan(mt_ore))
        )

    # Aggiunge range dei parametri aggiuntivi, considerando sempre il limite inferiore
    for p in parametri_aggiuntivi_da_considerare:
        if not np.isnan(p["range_traslato"][0]):
            ranges_per_intersezione_inizio.append(p["range_traslato"][0])
            if np.isnan(p["range_traslato"][1]) or p["range_traslato"][1] >= INF_HOURS:
                ranges_per_intersezione_fine.append(np.nan)
            else:
                ranges_per_intersezione_fine.append(p["range_traslato"][1])
            nomi_parametri_usati_per_intersezione.append(p["nome"])

    # --- Logica Henssge/Potente per intersezione ---
    if raffreddamento_calcolabile:
        # Se deve essere usato solo il limite inferiore
        usa_solo_limite_inferiore_henssge = False
        if not np.isnan(Qd_val_check) and Qd_val_check < 0.2:
            usa_solo_limite_inferiore_henssge = True

        altri_parametri_con_range = any([
            macchie_range_valido and macchie_range[1] < INF_HOURS,
            rigidita_range_valido and rigidita_range[1] < INF_HOURS,
            any(
                not np.isnan(p["range_traslato"][0]) and
                not np.isnan(p["range_traslato"][1]) and
                p["range_traslato"][1] < INF_HOURS
                for p in parametri_aggiuntivi_da_considerare
            )
        ])

        if usa_potente_per_intersezione:
            # Usa solo Potente, senza aggiungere Henssge
            ranges_per_intersezione_inizio.append(mt_ore)
            ranges_per_intersezione_fine.append(np.nan)
            nome_raffreddamento_intersezione = "raffreddamento cadaverico (intervallo minimo secondo Potente et al.)"
            nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)

        elif usa_solo_limite_inferiore_henssge:
            if mt_ore is not None and not np.isnan(mt_ore):
                ranges_per_intersezione_inizio.append(mt_ore)
                ranges_per_intersezione_fine.append(np.nan)
                nome_raffreddamento_intersezione = "raffreddamento cadaverico (intervallo minimo secondo Potente et al.)"
                nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
            else:
                ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                ranges_per_intersezione_fine.append(np.nan)
                nome_raffreddamento_intersezione = (
                    "raffreddamento cadaverico (è stato considerato solo il limite inferiore, "
                    "vista la limitata affidabilità del calcolo per i motivi sopraesposti)"
                )
                nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)

        else:
            if t_med_raff_hensge_rounded_raw > 48:
                if altri_parametri_con_range:
                    if t_min_raff_hensge > 48:
                        ranges_per_intersezione_inizio.append(48.0)
                        ranges_per_intersezione_fine.append(np.nan)
                        nome_raffreddamento_intersezione = (
                            "raffreddamento cadaverico (che è stato considerato genericamente > 48h, "
                            "vista la limitata affidabilità del calcolo per i motivi sopraesposti)"
                        )
                        nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
                    else:
                        ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                        ranges_per_intersezione_fine.append(t_max_raff_hensge)
                        nome_raffreddamento_intersezione = "raffreddamento cadaverico"
                        nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)
            else:
                ranges_per_intersezione_inizio.append(t_min_raff_hensge)
                ranges_per_intersezione_fine.append(t_max_raff_hensge)
                nome_raffreddamento_intersezione = "raffreddamento cadaverico"
                nomi_parametri_usati_per_intersezione.append(nome_raffreddamento_intersezione)

    # Se Potente non è stato usato per intersezione, ma è disponibile, lo aggiunge come parametro separato
    if (not usa_potente_per_intersezione) and ('mt_ore' in locals()) and (mt_ore is not None) and (not np.isnan(mt_ore)):
        ranges_per_intersezione_inizio.append(mt_ore)
        ranges_per_intersezione_fine.append(np.nan)

    # Calcolo intersezione finale
    if len(ranges_per_intersezione_inizio) > 0:
        comune_inizio = max(ranges_per_intersezione_inizio)

        if mt_ore is not None and not np.isnan(mt_ore):
            altri_limiti_inferiori = [
                v for v, n in zip(ranges_per_intersezione_inizio, nomi_parametri_usati_per_intersezione)
                if "raffreddamento cadaverico" not in n.lower() or "potente" in n.lower()
            ]
            if len(altri_limiti_inferiori) > 0:
                limite_minimo_altri = max(altri_limiti_inferiori)
                if mt_ore >= limite_minimo_altri:
                    comune_inizio = round(mt_ore)

        superiori_finiti = [v for v in ranges_per_intersezione_fine if not np.isnan(v) and v < INF_HOURS]

        if len(superiori_finiti) > 0:
            comune_fine = min(superiori_finiti)
        else:
            comune_fine = np.nan

        if np.isnan(comune_fine):
            overlap = True
        else:
            overlap = comune_inizio <= comune_fine
    else:
        comune_inizio, comune_fine = np.nan, np.nan
        overlap = False

    # --- Sezione dedicata alla generazione del grafico ---

    # Determina il numero totale di parametri da mostrare nel grafico
    num_params_grafico = 0
    if macchie_range_valido: num_params_grafico += 1
    if rigidita_range_valido: num_params_grafico += 1
    if visualizza_hensge_grafico: num_params_grafico += 1
    num_params_grafico += len([p for p in parametri_aggiuntivi_da_considerare if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1])])

    if num_params_grafico > 0:
        fig, ax = plt.subplots(figsize=(10, max(2, 1.5 + 0.5 * num_params_grafico)))
# --- STILI LINEE (pieni e tratteggiati) ---
        LINE_W  = 6              # stesso spessore per pieno e tratteggio
        DASH_LS = (0, (2, 1))    # tratteggio corto: 4 on, 3 off
        CAP     = 'butt'         # terminali piatti (coerenti)
        parametri_grafico = []
        ranges_to_plot_inizio = []
        ranges_to_plot_fine = []

        # --- Etichette e range: IPOSTASI ---
        if macchie_range_valido and macchie_range is not None:
            nome_breve_macchie = "Ipostasi"
            if macchie_range[1] < INF_HOURS:
                label_macchie = f"{nome_breve_macchie}\n({macchie_range[0]:.1f}–{macchie_range[1]:.1f} h)"
            else:
                label_macchie = f"{nome_breve_macchie}\n(≥ {macchie_range[0]:.1f} h)"
            parametri_grafico.append(label_macchie)
            ranges_to_plot_inizio.append(macchie_range[0])
            ranges_to_plot_fine.append(macchie_range[1] if macchie_range[1] < INF_HOURS else INF_HOURS)

        # --- Etichette e range: RIGIDITÀ ---
        if rigidita_range_valido and rigidita_range is not None:
            nome_breve_rigidita = "Rigor"
            if rigidita_range[1] < INF_HOURS:
                label_rigidita = f"{nome_breve_rigidita}\n({rigidita_range[0]:.1f}–{rigidita_range[1]:.1f} h)"
            else:
                label_rigidita = f"{nome_breve_rigidita}\n(≥ {rigidita_range[0]:.1f} h)"
            parametri_grafico.append(label_rigidita)
            ranges_to_plot_inizio.append(rigidita_range[0])
            ranges_to_plot_fine.append(rigidita_range[1] if rigidita_range[1] < INF_HOURS else INF_HOURS)

        # --- Etichette e range: RAFFREDDAMENTO ---
        label_hensge = None
        if raffreddamento_calcolabile:
            nome_breve_hensge = "Raffreddamento"
            usa_solo_limite_inferiore_henssge = not np.isnan(Qd_val_check) and Qd_val_check < 0.2

            if usa_solo_limite_inferiore_henssge:
                maggiore_di_valore = t_min_raff_hensge
                usa_potente = False
                if mt_ore is not None and not np.isnan(mt_ore):
                    maggiore_di_valore = round(mt_ore)
                    usa_potente = True

                if usa_potente:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore} h)"
                else:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore:.1f} h)\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"

                ranges_to_plot_inizio.append(t_min_raff_hensge)
                ranges_to_plot_fine.append(t_max_raff_hensge)

            elif t_med_raff_hensge_rounded_raw is not None and t_med_raff_hensge_rounded_raw > 30:
                maggiore_di_valore = 30.0
                usa_potente = False
                if mt_ore is not None and not np.isnan(mt_ore):
                    maggiore_di_valore = round(mt_ore)
                    usa_potente = True

                if usa_potente:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore} h)"
                else:
                    label_hensge = f"{nome_breve_hensge}\n(> {maggiore_di_valore:.1f} h)\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"

                ranges_to_plot_inizio.append(t_min_raff_hensge)
                ranges_to_plot_fine.append(t_max_raff_hensge)

            else:
                label_hensge = f"{nome_breve_hensge}\n({t_min_raff_hensge:.1f}–{t_max_raff_hensge:.1f} h)"
                ranges_to_plot_inizio.append(t_min_raff_hensge)
                ranges_to_plot_fine.append(t_max_raff_hensge)

            parametri_grafico.append(label_hensge)

        # --- Etichette e range: PARAMETRI AGGIUNTIVI ---
        for param in parametri_aggiuntivi_da_considerare:
            if not np.isnan(param["range_traslato"][0]) and not np.isnan(param["range_traslato"][1]):
                nome_breve = nomi_brevi.get(param['nome'], param['nome'])
                if param['range_traslato'][1] == INF_HOURS:
                    label_param_aggiuntivo = f"{nome_breve}\n(≥ {param['range_traslato'][0]:.1f} h)"
                else:
                    label_param_aggiuntivo = f"{nome_breve}\n({param['range_traslato'][0]:.1f}–{param['range_traslato'][1]:.1f} h)"
                if param.get('adattato', False):
                    label_param_aggiuntivo += " *"
                parametri_grafico.append(label_param_aggiuntivo)
                ranges_to_plot_inizio.append(param["range_traslato"][0])
                ranges_to_plot_fine.append(param["range_traslato"][1] if param["range_traslato"][1] < INF_HOURS else INF_HOURS)

        
        # ==============================
        # 1) RAFFREDDAMENTO verde (SOTTO)
        #    - Disegnato PRIMA delle linee blu
        #    - Cap dinamico e tratteggio fino al 20% in più
        # ==============================

        TAIL_FACTOR = 1.20
        DEFAULT_CAP_IF_NO_FINITE = 72.0  # 3 giorni se non esistono massimi finiti

        # Estremo superiore finito più grande (cap "finito")
        finite_ends_all = [e for e in ranges_to_plot_fine if not np.isnan(e) and e < INF_HOURS]
        cap_base = max(finite_ends_all) if finite_ends_all else DEFAULT_CAP_IF_NO_FINITE

        # Inizi dei segmenti "infiniti" blu (per stimare una base della coda)
        infinite_starts_blue = [
            s for s, e in zip(ranges_to_plot_inizio, ranges_to_plot_fine)
            if not np.isnan(s) and (np.isnan(e) or e >= INF_HOURS)
        ]

        # Inizi dei segmenti verdi speciali (Potente, soglia >30h)
        special_inf_starts_green = []
        if raffreddamento_calcolabile and label_hensge is not None and label_hensge in parametri_grafico:
            if mt_ore is not None and not np.isnan(mt_ore):
                special_inf_starts_green.append(mt_ore)
            if (not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and
                t_med_raff_hensge_rounded_raw is not None and t_med_raff_hensge_rounded_raw > 30):
                special_inf_starts_green.append(30.0)

        # Base della coda = max tra cap finito, inizi infiniti blu e verdi
        if infinite_starts_blue or special_inf_starts_green:
            tail_base = max([cap_base] + infinite_starts_blue + special_inf_starts_green)
        else:
            tail_base = cap_base

        TAIL_END = tail_base * TAIL_FACTOR  # fine tratteggio + fine grafico

        if raffreddamento_calcolabile and label_hensge is not None and label_hensge in parametri_grafico:
            idx_raff = parametri_grafico.index(label_hensge)

            # Segmento Potente (da mt_ore a ∞): solido fino a cap finito, poi tratteggiato fino a TAIL_END
            if mt_ore is not None and not np.isnan(mt_ore):
                solid_from = float(mt_ore)
                solid_to   = max(solid_from, cap_base)

                # parte piena
                if solid_from < TAIL_END and solid_to > solid_from:
                    ax.hlines(
                        y=idx_raff,
                        xmin=solid_from, xmax=min(solid_to, TAIL_END),
                        color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1
                    )

                # tratteggio
                dash_start = max(solid_to, solid_from)
                if TAIL_END > dash_start:
                    ax.hlines(
                        y=idx_raff,
                        xmin=dash_start, xmax=TAIL_END,
                        color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1,
                        linestyle=DASH_LS
                    )

            # Segmento >30h (Qd>0.2 e t_med_raw>30): solido fino a cap finito, poi tratteggiato fino a TAIL_END
            if (not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and
                t_med_raff_hensge_rounded_raw is not None and t_med_raff_hensge_rounded_raw > 30):
                solid_from = 30.0
                solid_to   = max(solid_from, cap_base)

                # parte piena
                if solid_from < TAIL_END and solid_to > solid_from:
                    ax.hlines(
                        y=idx_raff,
                        xmin=solid_from, xmax=min(solid_to, TAIL_END),
                        color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1
                    )

                # tratteggio
                dash_start = max(solid_to, solid_from)
                if TAIL_END > dash_start:
                    ax.hlines(
                        y=idx_raff,
                        xmin=dash_start, xmax=TAIL_END,
                        color='mediumseagreen', linewidth=LINE_W, alpha=1.0, zorder=1,
                        linestyle=DASH_LS
                    )
                    
        
        # 2) LINEE BLU DI BASE (tutti i range)
        #    - Finite: come prima
        #    - Infinite: solido fino a cap finito, poi tratteggiato fino a TAIL_END
        # ==============================
        for i, (s, e) in enumerate(zip(ranges_to_plot_inizio, ranges_to_plot_fine)):
            if np.isnan(s):
                continue

            is_infinite = (np.isnan(e) or e >= INF_HOURS)

            if not is_infinite:
                ax.hlines(i, s, e, color='steelblue', linewidth=6, zorder=2)
            else:
                solid_to = max(s, cap_base)
                if solid_to > s and s < TAIL_END:
                    ax.hlines(i, s, min(solid_to, TAIL_END), color='steelblue', linewidth=6, zorder=2)
                dash_start = max(solid_to, s)
                if TAIL_END > dash_start:
                    ax.hlines(i, dash_start, TAIL_END,
                              color='steelblue', linewidth=LINE_W, zorder=2, linestyle=DASH_LS)
                    

        # --- Asse X: termina esattamente a TAIL_END (niente 10% extra) ---
        ax.set_xlim(0, TAIL_END)
        ax.margins(x=0)       # rimuove margine automatico
        max_x_value = TAIL_END  # per la logica delle linee rosse sotto

        # ==============================
        # 3) IPOSTASI/RIGOR Verdi (SOPRA)
        #    - Mediane verdi opache; se la mediana è "infinita": solido fino a cap_base + tratteggio fino a TAIL_END
        # ==============================
        # Mapping asse Y statico per righe principali
        y_indices_mapping = {}
        current_y_index = 0
        if macchie_range_valido and macchie_range is not None:
            y_indices_mapping["Macchie ipostatiche"] = current_y_index
            current_y_index += 1
        if rigidita_range_valido and rigidita_range is not None:
            y_indices_mapping["Rigidità cadaverica"] = current_y_index
            current_y_index += 1
        if raffreddamento_calcolabile:
            y_indices_mapping["Raffreddamento cadaverico"] = current_y_index
            current_y_index += 1

        # --- Mediana IPOSTASI (solido + tratteggio se infinita) ---
        if macchie_range_valido and macchie_medi_range is not None and "Macchie ipostatiche" in y_indices_mapping:
            y = y_indices_mapping["Macchie ipostatiche"]
            m_s, m_e = macchie_medi_range
            is_infinite_m = (m_e is None) or (np.isnan(m_e)) or (m_e >= INF_HOURS)

            if not is_infinite_m:
                ax.hlines(y, m_s, m_e, color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
            else:
                solid_to = max(m_s, cap_base)
                if solid_to > m_s and m_s < TAIL_END:
                    ax.hlines(y, m_s, min(solid_to, TAIL_END), color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
                dash_start = max(solid_to, m_s)
                if TAIL_END > dash_start:
                    # uso plot per avere tratteggio sicuro sopra le blu
                    ax.plot([dash_start, TAIL_END], [y, y],
                            color='mediumseagreen', linewidth=LINE_W, alpha=1.0,
                            linestyle=DASH_LS, zorder=3)
                              
                    

        # --- Mediana RIGIDITÀ (solido + tratteggio se infinita) ---
        if rigidita_range_valido and rigidita_medi_range is not None and "Rigidità cadaverica" in y_indices_mapping:
            y = y_indices_mapping["Rigidità cadaverica"]
            r_s, r_e = rigidita_medi_range
            is_infinite_r = (r_e is None) or (np.isnan(r_e)) or (r_e >= INF_HOURS)

            if not is_infinite_r:
                ax.hlines(y, r_s, r_e, color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
            else:
                solid_to = max(r_s, cap_base)
                if solid_to > r_s and r_s < TAIL_END:
                    ax.hlines(y, r_s, min(solid_to, TAIL_END), color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
                dash_start = max(solid_to, r_s)
                if TAIL_END > dash_start:
                    # uso plot per avere tratteggio sicuro sopra le blu
                    ax.plot([dash_start, TAIL_END], [y, y],
                            color='mediumseagreen', linewidth=LINE_W, alpha=1.0,
                            linestyle=DASH_LS, zorder=3)

        # --- Marker corto verde sul punto medio del raffreddamento ---
        if raffreddamento_calcolabile:
            if "Raffreddamento cadaverico" in y_indices_mapping and not (np.isnan(t_min_raff_visualizzato) or np.isnan(t_max_raff_visualizzato)):
                y_pos_raffreddamento = y_indices_mapping["Raffreddamento cadaverico"]
                punto_medio_raffreddamento = (t_min_raff_visualizzato + t_max_raff_visualizzato) / 2.0
                offset = 0.1
                if (punto_medio_raffreddamento - offset) < TAIL_END:
                    ax.hlines(y_pos_raffreddamento,
                              max(0, punto_medio_raffreddamento - offset),
                              min(TAIL_END, punto_medio_raffreddamento + offset),
                              color='mediumseagreen', linewidth=6, alpha=1.0, zorder=3)
        
         # --- Asse Y, etichette e limiti ---
        ax.set_yticks(range(len(parametri_grafico)))
        ax.set_yticklabels(parametri_grafico, fontsize=15)
        ax.set_xlabel("Ore dal decesso")
        ax.grid(True, axis='x', linestyle=':', alpha=0.6)

        # Intervallo finale in rosso (clippato a TAIL_END)
        if overlap and (np.isnan(comune_fine) or comune_fine > 0):
            if comune_inizio < TAIL_END:
                ax.axvline(max(0, comune_inizio), color='red', linestyle='--')
            if not np.isnan(comune_fine) and comune_fine > 0:
                ax.axvline(min(TAIL_END, comune_fine), color='red', linestyle='--')

        plt.tight_layout()
        st.pyplot(fig)
                             


    # --- NOTE/AVVISI: raccogli in 'avvisi' (niente stampa diretta) ---
    if nota_globale_range_adattato:
        dettagli.append(
            "<p style='color:gray;font-size:small;'>* alcuni parametri sono stati valutati a orari diversi; i range sono stati traslati per renderli confrontabili.</p>"
        )

    if minuti_isp not in [0, 15, 30, 45]:
        avvisi.append("NB: l’orario dei rilievi è stato arrotondato al quarto d’ora più vicino.")

    hensge_input_forniti = (
        input_rt is not None and
        input_ta is not None and
        input_tm is not None and
        input_w is not None and
        st.session_state.get('fattore_correzione', None) is not None
    )

    if hensge_input_forniti:
        if Ta_val > 25:
            avvisi.append("Per temperature ambientali &gt; 25 °C, variazioni del fattore di correzione possono influenzare notevolmente i risultati.")
        if Ta_val < 18:
            avvisi.append("Per temperature ambientali &lt; 18 °C, la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati.")
        if temp_difference_small:
            avvisi.append("Essendo minima la differenza tra temperatura rettale e ambientale, è possibile che il cadavere fosse ormai in equilibrio termico con l'ambiente. La stima ottenuta dal raffreddamento cadaverico va interpretata con attenzione.")
        if abs(Tr_val - T0_val) <= 1.0:
            avvisi.append(
                "Considerato che la temperatura rettale è molto simile alla temperatura ante-mortem stimata, "
                "è possibile che il raffreddamento si trovi ancora nella fase di plateau o non sia ancora iniziato; "
                "in tale fase la precisione del metodo è ridotta."
            )
            
        if not raffreddamento_calcolabile:
            avvisi.append("Non è stato possibile applicare il metodo di Henssge (temperature incoerenti o fuori range del nomogramma).")

    # --- Dettaglio del raffreddamento cadaverico con dati di input (da mostrare prima del testo Henssge) ---
    try:
        orario_isp = data_ora_ispezione.strftime('%H:%M')
        data_isp = data_ora_ispezione.strftime('%d.%m.%Y')
    except Exception:
        orario_isp = input_ora_rilievo or "—"
        data_isp = input_data_rilievo.strftime('%d.%m.%Y') if input_data_rilievo else "—"

    ta_txt = f"{Ta_val:.1f}" if Ta_val is not None else "—"
    tr_txt = f"{Tr_val:.1f}" if Tr_val is not None else "—"
    w_txt  = f"{W_val:.1f}"  if W_val  is not None else "—"
    t0_txt = f"{T0_val:.1f}" if T0_val is not None else "—"
    cf_val = st.session_state.get('fattore_correzione', CF_val if CF_val is not None else None)
    cf_txt = f"{cf_val:.2f}" if cf_val is not None else "—"

     # === Ricostruzione robusta della parentetica dalle scelte correnti (versione con ˃ / ˃˃) ===
    import unicodedata

    def _norm(s: str):
        if s is None:
            return None
        s = unicodedata.normalize("NFKC", str(s)).strip()
        # normalizza tutte le varianti di “>” al carattere U+02C3 (˃)
        s = (s.replace(">", "˃")
               .replace("›", "˃")
               .replace("＞", "˃"))
        # uniforma doppie frecce
        s = s.replace("˃ ˃", "˃˃").replace("˃˃", "˃˃")
        return s

    def _classifica_superficie(s: str):
        if not s or s == "/":
            return None
        s_low = s.lower()
        if ("metall" in s_low) or ("cemento" in s_low) or ("pietra" in s_low) or ("pvc" in s_low) or ("pavimentazione esterna" in s_low):
            return "conduttiva"
        if ("materasso" in s_low) or ("tappeto" in s_low) or ("imbottitura" in s_low) or ("foglie" in s_low):
            return "isolante"
        return "indifferente"

    def _format_vestiti(v: str):
        if not v or v == "/":
            return None
        v = _norm(v)
        if v == "Nudo":
            return "nudo"
        if v == "1-2 strati sottili":
            return "con 1–2 strati di indumenti sottili"
        if v == "2-3 strati sottili":
            return "con 2–3 strati di indumenti sottili"
        if v == "3-4 strati sottili":
            return "con 3–4 strati di indumenti sottili"
        if v == "1-2 strati spessi":
            return "con 1–2 strati di indumenti spessi"
        # nuove etichette Excel
        if v == "˃ strati":
            return "con molti strati di indumenti"
        if v == "˃˃ strati":
            return "con moltissimi strati di indumenti"
        return f"con indumenti ({v.lower()})"

    def _format_coperte(c: str):
        if not c or c == "/":
            return None
        if c == "Nessuna coperta":
            return "senza coperte"
        if c.startswith("Coperta spessa (es copriletto)"):
            return "sotto una coperta pesante"
        if c.startswith("Coperte più spesse (es coperte di lana)"):
            return "sotto una coperta discretamente pesante"
        if c.startswith("Coperta pesante (es piumino imbottito)"):
            return "sotto una coperta molto pesante"
        if c == "Molte coperte pesanti":
            return "sotto molte coperte pesanti"
        if c == "Strato di foglie di medio spessore":
            return "coperto da uno strato di foglie"
        if c == "Spesso strato di foglie":
            return "coperto da uno spesso strato di foglie"
        return f"con coperte ({c.lower()})"

    def _format_corrente(c: str):
        if not c or c == "/":
            return None
        if c == "Nessuna corrente":
            return "senza correnti d'aria"
        if c == "Esposto a corrente d'aria":
            return "con correnti d'aria"
        if c == "In acqua corrente":
            return "in acqua corrente"
        if c == "In acqua stagnante":
            return "in acqua stagnante"
        return c.lower()

    def _format_stato_corpo(s: str):
        if not s:
            return None
        return {
            "Asciutto": "corpo asciutto",
            "Bagnato": "corpo bagnato",
            "Immerso": "corpo immerso"
        }.get(s, str(s).lower())

    # Leggi scelte correnti
    stato_sc = st.session_state.get("radio_stato_corpo")
    vest_sc  = _norm(st.session_state.get("radio_vestiti", "/"))
    cop_sc   = st.session_state.get("scelta_coperte_radio", "/")
    sup_sc   = st.session_state.get("radio_superficie", "/")
    corr_sc  = st.session_state.get("radio_corrente") or st.session_state.get("radio_acqua") or "/"

    # Ricostruzione testi
    vestiti_txt = _format_vestiti(vest_sc)
    coperte_txt = _format_coperte(cop_sc)
    superf_cat  = _classifica_superficie(sup_sc)
    corr_txt    = _format_corrente(corr_sc)
    stato_txt   = _format_stato_corpo(stato_sc)

    parts_parent = []
    if stato_txt:    parts_parent.append(stato_txt)
    if vestiti_txt:  parts_parent.append(vestiti_txt)
    if coperte_txt:  parts_parent.append(coperte_txt)
    if superf_cat:   parts_parent.append(f"adagiato su superficie termicamente {superf_cat}")
    if corr_txt:     parts_parent.append(corr_txt)

    parent = "(" + ", ".join(parts_parent) + ")" if parts_parent else None
    if not parent:
        # fallback alla versione salvata dal bottone “Usa questo fattore”
        parent = st.session_state.get("fattori_condizioni_parentetica")

    if parent:
        cf_descr = f"{cf_txt} {parent}"
    elif st.session_state.get("fattori_condizioni_testo"):
        cf_descr = f"{cf_txt} (in base ai fattori scelti: {st.session_state['fattori_condizioni_testo']})."
    else:
        cf_descr = f"{cf_txt} (da adattare sulla base dei fattori scelti)."

    dettagli.append(
        "<ul><li>Per quanto attiene la valutazione del raffreddamento cadaverico, sono stati considerati gli elementi di seguito indicati."
        "<ul>"
        f"<li>Temperature misurate nel corso dell’ispezione legale verso le ore {orario_isp} del {data_isp}:"
        "<ul>"
        f"<li>Temperatura ambientale: {ta_txt} °C.</li>"
        f"<li>Temperatura rettale: {tr_txt} °C.</li>"
        "</ul>"
        "</li>"
        f"<li>Peso del cadavere misurato in sala autoptica: {w_txt} kg.</li>"
        f"<li>Temperatura corporea ipotizzata al momento della morte: {t0_txt} °C.</li>"
        f"<li>Fattore di correzione ipotizzato dagli scriventi in base alle condizioni ambientali (per quanto noto): {cf_descr}</li>"
        "</ul>"
        "</li></ul>"
    )


    # --- Testo Henssge dettagliato (va nell’expander) ---
    if raffreddamento_calcolabile:
        if 't_min_raff_visualizzato' in locals() and not (np.isnan(t_min_raff_visualizzato) or np.isnan(t_max_raff_visualizzato)):
            hm = _split_hours_minutes(t_min_raff_visualizzato); min_raff_hours, min_raff_minutes = hm if hm else (0, 0)
            hm = _split_hours_minutes(t_max_raff_visualizzato); max_raff_hours, max_raff_minutes = hm if hm else (0, 0)
            min_raff_hour_text = "ora" if min_raff_hours == 1 and min_raff_minutes == 0 else "ore"
            max_raff_hour_text = "ora" if max_raff_hours == 1 and max_raff_minutes == 0 else "ore"

            # Frase Henssge base originale
            testo_raff_base = (
                f"Applicando il nomogramma di Henssge, è possibile stimare che il decesso sia avvenuto tra circa "
                f"{min_raff_hours} {min_raff_hour_text}{'' if min_raff_minutes == 0 else f' {min_raff_minutes} minuti'} e "
                f"{max_raff_hours} {max_raff_hour_text}{'' if max_raff_minutes == 0 else f' {max_raff_minutes} minuti'} "
                f"prima dei rilievi effettuati al momento dell’ispezione legale."
            )

            elenco_extra = []

            # Qd basso (<0.2)
            if not np.isnan(Qd_val_check) and Qd_val_check < 0.2:
                elenco_extra.append(
                    f"<li>"
                    f"I valori ottenuti, tuttavia, sono in parte o totalmente fuori dai range ottimali delle equazioni applicabili "
                    f"(Valore di Qd ottenuto: <b>{Qd_val_check:.5f}</b>, &lt; 0.2) "
                    f"(il range temporale indicato è stato calcolato, grossolanamente, come pari al ±20% del valore medio ottenuto dalla stima del raffreddamento cadaverico - {t_med_raff_hensge_rounded:.1f} ore -, ma tale range è privo di una solida base statistica). "
                    f"In mancanza di ulteriori dati o interpretazioni, si può presumere che il raffreddamento cadaverico fosse ormai concluso. "
                    f"Per tale motivo, il range ottenuto è da ritenersi del tutto indicativo e per la stima dell'epoca del decesso è consigliabile far riferimento principalmente ad altri dati tanatologici."
                    f"</li>"
                )

            # Qd alto e durata > 30h
            if not np.isnan(Qd_val_check) and Qd_val_check > 0.2 and t_med_raff_hensge_rounded_raw > 30:
                elenco_extra.append(
                    f"<li>"
                    f"<span style='color:orange; font-weight:bold;'>"
                    f"La stima media ottenuta dal raffreddamento cadaverico ({t_med_raff_hensge_rounded:.1f} h) è superiore alle 30 ore. "
                    f"L'affidabilità del metodo di Henssge diminuisce significativamente oltre questo intervallo."
                    f"</span>"
                    f"</li>"
                )

            paragrafo = f"<ul><li>{testo_raff_base}"
            if elenco_extra:
                paragrafo += "<ul>" + "".join(elenco_extra) + "</ul>"
            paragrafo += "</li></ul>"
            dettagli.append(paragrafo)

        # Metodo Potente: solo come punto elenco nei dettagli
        if (mt_ore is not None) and (not np.isnan(mt_ore)) and (Qd_val_check is not None) and (Qd_val_check < qd_threshold):
            condizione_temp = "T. amb ≤ 23 °C" if Ta_val <= 23 else "T. amb > 23 °C"
            dettagli.append(
                f"<ul><li>Lo studio di Potente et al. permette di stimare grossolanamente l’intervallo minimo post-mortem quando i dati non consentono di ottenere risultati attendibili con il metodo di Henssge "
                f"(Qd &lt; {qd_threshold} e {condizione_temp}). "
                f"Applicandolo al caso specifico, si può ipotizzare che, al momento dell’ispezione legale, fossero trascorse almeno <b>{mt_ore:.0f}</b> ore (≈ {mt_giorni:.1f} giorni) dal decesso.</li></ul>"
            )


    # --- Descrizioni macchie/rigidità/parametri: tutte nei dettagli ---
    dettagli.append(f"<ul><li>{testi_macchie[macchie_selezionata]}</li></ul>")
    dettagli.append(f"<ul><li>{rigidita_descrizioni[rigidita_selezionata]}</li></ul>")
    for param in parametri_aggiuntivi_da_considerare:
        if param['stato'] not in ('Non valutata', 'Non valutabile/non attendibile'):
            dettagli.append(f"<ul><li>{param['descrizione']}</li></ul>")
    # Punto elenco extra (solo descrizione dettagliata) se sono state osservate alterazioni putrefattive
    if st.session_state.get("alterazioni_putrefattive", False):
        dettagli.append(
            "<ul><li>Per quanto riguarda i processi trasformativi post-mortali (compresi quelli putrefattivi), "
            "la loro insorgenza è influenzata da numerosi fattori, esogeni (ad esempio temperatura ambientale, "
            "esposizione ai fenomeni metereologici…) ed endogeni (temperatura corporea, infezioni prima del decesso, "
            "presenza di ferite…). Poiché tali processi possono manifestarsi in un intervallo temporale estremamente "
            "variabile, da poche ore a diverse settimane dopo il decesso, la loro valutazione non permette di formulare "
            "ulteriori precisazioni sull’epoca della morte.</li></ul>"
        )

    # --- Frase finale: identica alla tua logica, ma salvata in 'frase_finale_html' ---
    if overlap:
        try:
            isp = data_ora_ispezione
        except Exception:
            return

        limite_superiore_infinito = np.isnan(comune_fine) or comune_fine == INF_HOURS

        if (not np.isnan(Qd_val_check) and Qd_val_check < 0.3
            and comune_inizio > 30
            and (np.isnan(comune_fine) or comune_fine == INF_HOURS)):
            hm = _split_hours_minutes(comune_inizio); comune_inizio_hours, comune_inizio_minutes = hm if hm else (0, 0)
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 and comune_inizio_minutes == 0 else "ore"
            da = isp - datetime.timedelta(hours=comune_inizio)
            if not np.isnan(Qd_val_check) and Qd_val_check <= 0.2 and not np.isnan(mt_ore) and mt_ore > 30:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                    f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                    f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
                )
            else:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                    f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                    f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}. "
                    f"Occorre tener conto che l'affidabilità del metodo di Henssge diminuisce significativamente quando sono trascorse più di 30 ore dal decesso, e tale dato è da considerarsi del tutto indicativo."
                )
        elif limite_superiore_infinito:
            if mt_ore is not None and not np.isnan(mt_ore):
                if abs(comune_inizio - mt_ore) < 0.25:
                    comune_inizio = round(mt_ore)
            hm = _split_hours_minutes(comune_inizio); comune_inizio_hours, comune_inizio_minutes = hm if hm else (0, 0)
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 and comune_inizio_minutes == 0 else "ore"
            da = isp - datetime.timedelta(hours=comune_inizio)
            testo = (
                f"La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta "
                f"<b>oltre</b> {comune_inizio_hours} {comune_inizio_hour_text}"
                f"{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero prima delle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
            )
        elif comune_inizio == 0:
            hm = _split_hours_minutes(comune_fine); comune_fine_hours, comune_fine_minutes = hm if hm else (0, 0)
            fine_hour_text = "ora" if comune_fine_hours == 1 else "ore"
            da = isp - datetime.timedelta(hours=comune_fine)
            testo = (
                f"La valutazione complessiva dei dati tanatologici, integrando i limiti temporali massimi e minimi derivanti dalle considerazioni precedenti, "
                f"consente di stimare che la morte sia avvenuta <b>non oltre</b> "
                f"{comune_fine_hours} {fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                f"prima dei rilievi effettuati durante l’ispezione legale, ovvero successivamente alle ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
            )
        else:
            hm = _split_hours_minutes(comune_inizio); comune_inizio_hours, comune_inizio_minutes = hm if hm else (0, 0)
            hm = _split_hours_minutes(comune_fine); comune_fine_hours, comune_fine_minutes = hm if hm else (0, 0)
            comune_inizio_hour_text = "ora" if comune_inizio_hours == 1 else "ore"
            comune_fine_hour_text = "ora" if comune_fine_hours == 1 else "ore"
            da = isp - datetime.timedelta(hours=comune_fine)
            aa = isp - datetime.timedelta(hours=comune_inizio)
            if da.date() == aa.date():
                testo = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{comune_inizio_hours} {comune_inizio_hour_text}{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} e "
                    f"{comune_fine_hours} {comune_fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {da.strftime('%H:%M')} e le ore {aa.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')}."
                )
            else:
                testo = (
                    f"La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali massimi e minimi, "
                    f"consente di stimare che la morte sia avvenuta tra circa "
                    f"{comune_inizio_hours} {comune_inizio_hour_text}{'' if comune_inizio_minutes == 0 else f' {comune_inizio_minutes} minuti'} e "
                    f"{comune_fine_hours} {comune_fine_hour_text}{'' if comune_fine_minutes == 0 else f' {comune_fine_minutes} minuti'} "
                    f"prima dei rilievi effettuati durante l’ispezione legale, ovvero circa tra le ore {da.strftime('%H:%M')} del {da.strftime('%d.%m.%Y')} e le ore {aa.strftime('%H:%M')} del {aa.strftime('%d.%m.%Y')}."
                )
        frase_finale_html = f"<b>{testo}</b>"

    # --- Variante “Senza considerare Potente” (se applicabile) → mostrata sotto la frase finale, non in expander
    if any("potente" in nome.lower() for nome in nomi_parametri_usati_per_intersezione):
        range_inizio_senza_potente = []
        range_fine_senza_potente = []

        if macchie_range_valido and macchie_range is not None:
            range_inizio_senza_potente.append(macchie_range[0]); range_fine_senza_potente.append(macchie_range[1])
        if rigidita_range_valido and rigidita_range is not None:
            range_inizio_senza_potente.append(rigidita_range[0]); range_fine_senza_potente.append(rigidita_range[1])
        for p in parametri_aggiuntivi_da_considerare:
            if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1]):
                range_inizio_senza_potente.append(p["range_traslato"][0]); range_fine_senza_potente.append(p["range_traslato"][1])
        if raffreddamento_calcolabile:
            range_inizio_senza_potente.append(t_min_raff_hensge); range_fine_senza_potente.append(t_max_raff_hensge)

        if len(range_inizio_senza_potente) >= 2:
            inizio_senza_potente = max(range_inizio_senza_potente)
            fine_senza_potente = min(range_fine_senza_potente)
            if inizio_senza_potente <= fine_senza_potente:
                hm = _split_hours_minutes(inizio_senza_potente); inizio_h, inizio_m = hm if hm else (0, 0)
                hm = _split_hours_minutes(fine_senza_potente); fine_h, fine_m = hm if hm else (0, 0)
                inizio_text = "ora" if inizio_h == 1 and inizio_m == 0 else "ore"
                fine_text = "ora" if fine_h == 1 and fine_m == 0 else "ore"
                dt_inizio = data_ora_ispezione - datetime.timedelta(hours=fine_senza_potente)
                dt_fine = data_ora_ispezione - datetime.timedelta(hours=inizio_senza_potente)
                frase_secondaria_html = (
                    f"<b>Senza considerare lo studio di Potente</b>, la valutazione complessiva consente di stimare che la morte sia avvenuta tra circa "
                    f"{inizio_h} {inizio_text}{'' if inizio_m == 0 else f' {inizio_m} minuti'} e "
                    f"{fine_h} {fine_text}{'' if fine_m == 0 else f' {fine_m} minuti'} "
                    f"prima dei rilievi, ovvero tra le ore {dt_inizio.strftime('%H:%M')} del {dt_inizio.strftime('%d.%m.%Y')} "
                    f"e le ore {dt_fine.strftime('%H:%M')} del {dt_fine.strftime('%d.%m.%Y')}."
                )

    # --- Riepilogo parametri usati (era arancione piccolo) → dettagli
    if overlap and len(nomi_parametri_usati_per_intersezione) > 0:
        nomi_parametri_finali_per_riepilogo = []
        for nome in nomi_parametri_usati_per_intersezione:
            if ("raffreddamento cadaverico" in nome.lower()
                and "potente" not in nome.lower()
                and mt_ore is not None
                and not np.isnan(mt_ore)
                and abs(comune_inizio - mt_ore) < 0.25):
                continue
            nomi_parametri_finali_per_riepilogo.append(nome)
        if len(nomi_parametri_finali_per_riepilogo) == 1:
            p = nomi_parametri_finali_per_riepilogo[0]
            dettagli.append(f"<p style='color:orange;font-size:small;'>La stima complessiva si basa sul seguente parametro: {p[0].lower() + p[1:]}.</p>")
        elif len(nomi_parametri_finali_per_riepilogo) > 1:
            parametri_usati_str = ', '.join(p[0].lower() + p[1:] for p in nomi_parametri_finali_per_riepilogo[:-1])
            parametri_usati_str += f" e {nomi_parametri_finali_per_riepilogo[-1][0].lower() + nomi_parametri_finali_per_riepilogo[-1][1:]}"
            dettagli.append(f"<p style='color:orange;font-size:small;'>La stima complessiva si basa sui seguenti parametri: {parametri_usati_str}.</p>")


    # --- Messaggi di discordanza (rossi) → dettagli
    num_potential_ranges_used = sum(
        1
        for start, end in zip(ranges_per_intersezione_inizio, ranges_per_intersezione_fine)
        if start is not None and end is not None
    )


    # === RENDER COMPATTO ===
    if avvisi:
        with st.expander(f"⚠️ Avvertenze ({len(avvisi)})"):
            st.warning("\n".join(f"- {msg}" for msg in avvisi))

    if frase_finale_html:
        st.markdown(frase_finale_html, unsafe_allow_html=True)
    with st.expander("Descrizioni dettagliate"):
        if frase_secondaria_html:
            st.markdown(
                f"<div style='border:1px solid #ccc; padding:10px; color:gray; font-size:small;'>{frase_secondaria_html}</div>",
                unsafe_allow_html=True
            )
        for blocco in dettagli:
            st.markdown(blocco, unsafe_allow_html=True)



 
    if overlap and len(nomi_parametri_usati_per_intersezione) > 0:
        # Filtra la lista dei nomi da mostrare nel riepilogo finale
        nomi_parametri_finali_per_riepilogo = []
        for nome in nomi_parametri_usati_per_intersezione:
            # Escludi il raffreddamento Henssge generico se non usato
            if (
                "raffreddamento cadaverico" in nome.lower()
                and "potente" not in nome.lower()
                and mt_ore is not None
                and not np.isnan(mt_ore)
                and abs(comune_inizio - mt_ore) < 0.25
            ):
                continue
            nomi_parametri_finali_per_riepilogo.append(nome)

        num_parametri_usati_intersezione = len(nomi_parametri_finali_per_riepilogo)
        if num_parametri_usati_intersezione == 1:
            p = nomi_parametri_finali_per_riepilogo[0]
            messaggio_parametri = f"La stima complessiva si basa sul seguente parametro: {p[0].lower() + p[1:]}."
        elif num_parametri_usati_intersezione > 1:
            parametri_usati_str = ', '.join(p[0].lower() + p[1:] for p in nomi_parametri_finali_per_riepilogo[:-1])
            parametri_usati_str += f" e {nomi_parametri_finali_per_riepilogo[-1][0].lower() + nomi_parametri_finali_per_riepilogo[-1][1:]}"
            messaggio_parametri = f"La stima complessiva si basa sui seguenti parametri: {parametri_usati_str}."
        else:
            messaggio_parametri = None

        if messaggio_parametri:
            st.markdown(
                f"<p style='color:orange;font-size:small;'>{messaggio_parametri}</p>",
                unsafe_allow_html=True
            )

    elif not overlap and num_potential_ranges_used >= 2:
        st.markdown(
            "<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>",
            unsafe_allow_html=True
        )
    elif ranges_in_disaccordo_completa(ranges_per_intersezione_inizio, ranges_per_intersezione_fine):
        st.markdown(
            "<p style='color:red;font-weight:bold;'>⚠️ Le stime basate sui singoli dati tanatologici sono tra loro discordanti.</p>",
            unsafe_allow_html=True
        )


# Al click del pulsante, esegui la funzione principale
if pulsante_genera_stima:
    aggiorna_grafico()
