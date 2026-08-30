# -*- coding: utf-8 -*-
"""Classificazione stabile mobile/desktop per la schermata completa di Mor-tem."""

from collections.abc import Mapping

import streamlit as st

import app.full_mobile_compact as _full_mobile_compact
from app.full_mobile_compact import install_full_mobile_compact_css


_SESSION_KEY = "__full_device_mobile"


# Rifiniture esterne dei controlli del raffreddamento della Full.
# L'allineamento interno etichetta/valore/unità/−/+ resta responsabilità del
# componente V2; qui si governa soltanto la larghezza dei wrapper Streamlit e,
# in modalità prudente, la colonna esterna ±3 kg della riga Peso.
_FULL_COOLING_ROW_WIDTH_CSS = r"""
<style>
body:has([class*="st-key-stima_cautelativa_beta"]) {
  --mortem-cooling-row-width: 20rem;
  --mortem-cooling-action-col: 4.4rem;
}

/* Tutte le righe numeriche hanno la stessa larghezza complessiva. */
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-mortem_decimal_"],
body:has([class*="st-key-stima_cautelativa_beta"])
[data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_"]) {
  box-sizing: border-box !important;
  width: var(--mortem-cooling-row-width) !important;
  max-width: 100% !important;
  min-width: 0 !important;
  align-self: flex-start !important;
}

/* Condizioni variabili: Peso e ±3 kg formano una sola riga della stessa
   larghezza delle altre. Il componente Peso occupa le prime cinque colonne;
   ±3 kg occupa la colonna azione, senza spostare il valore 70.0. */
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_row_mobile"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_row_mobile"] [data-testid="stHorizontalBlock"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_row_desktop"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_row_desktop"] [data-testid="stHorizontalBlock"] {
  box-sizing: border-box !important;
  display: grid !important;
  grid-template-columns:
    minmax(0, calc(var(--mortem-cooling-row-width) - var(--mortem-cooling-action-col)))
    var(--mortem-cooling-action-col) !important;
  align-items: center !important;
  gap: 0 !important;
  width: var(--mortem-cooling-row-width) !important;
  max-width: 100% !important;
  min-width: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_value_mobile"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_value_desktop"] {
  box-sizing: border-box !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_value_mobile"] [class*="st-key-mortem_decimal_peso"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_value_desktop"] [class*="st-key-mortem_decimal_peso"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_value_mobile"] [data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_peso"]),
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_value_desktop"] [data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_peso"]) {
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_uncertainty_mobile"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_uncertainty_desktop"] {
  box-sizing: border-box !important;
  width: var(--mortem-cooling-action-col) !important;
  max-width: var(--mortem-cooling-action-col) !important;
  min-width: var(--mortem-cooling-action-col) !important;
  margin: 0 !important;
  padding: 0 0 0 0.18rem !important;
}

@media (max-width: 768px) {
  /* Il testo esplicativo della modalità prudente è già omesso visivamente
     nella Full mobile: eliminiamo anche il contenitore residuo che lasciava
     una fascia bianca tra il toggle e T. rettale. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-prudent_explicit_ranges"] {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_prudent_v2_stack_mobile"] {
    margin-top: 0 !important;
    padding-top: 0 !important;
    gap: 0.18rem !important;
  }

  /* Mantiene il toggle Condizioni variabili sopra eventuali wrapper della
     modalità che vengono montati/smontati durante il rerun. */
  [class*="st-key-stima_cautelativa_beta"] [data-testid="stToggle"],
  [class*="st-key-stima_cautelativa_beta"] [data-testid="stToggle"] label {
    position: relative !important;
    z-index: 3 !important;
    pointer-events: auto !important;
  }
}

@media (min-width: 769px) {
  body:has([class*="st-key-stima_cautelativa_beta"]) {
    --mortem-cooling-row-width: 28rem;
  }
}
</style>
"""

_full_mobile_compact._FULL_MOBILE_COMPACT_CSS += _FULL_COOLING_ROW_WIDTH_CSS


def _header_value(headers, name: str) -> str:
    """Legge un header anche da mapping semplici usati nei test."""
    try:
        value = headers.get(name)
    except Exception:
        value = None
    if value is not None:
        return str(value)

    target = name.casefold()
    try:
        items = headers.items()
    except Exception:
        return ""
    for key, value in items:
        if str(key).casefold() == target:
            return "" if value is None else str(value)
    return ""


def classify_mobile_headers(headers: Mapping | object) -> bool:
    """Classifica la richiesta come mobile usando Client Hint e User-Agent."""
    ch_mobile = _header_value(headers, "Sec-CH-UA-Mobile").strip().lower()
    if ch_mobile in {"?1", "1", "true"}:
        return True
    if ch_mobile in {"?0", "0", "false"}:
        return False

    user_agent = _header_value(headers, "User-Agent").casefold()
    if not user_agent:
        return False

    phone_tokens = (
        "iphone",
        "ipod",
        "windows phone",
        "opera mini",
        "opera mobi",
        "mobile",
    )
    if any(token in user_agent for token in phone_tokens):
        return True

    # Alcuni browser Android possono omettere "Mobile"; Android resta un
    # fallback utile per telefoni/PWA, mentre Sec-CH-UA-Mobile prevale quando
    # disponibile e distingue correttamente i tablet Chromium.
    return "android" in user_agent


def full_device_is_mobile() -> bool:
    """Restituisce una sola classificazione per tutta la sessione Streamlit."""
    if _SESSION_KEY in st.session_state:
        return bool(st.session_state[_SESSION_KEY])

    try:
        headers = st.context.headers
    except Exception:
        headers = {}

    mobile = classify_mobile_headers(headers)
    st.session_state[_SESSION_KEY] = mobile
    return mobile


# Il modulo viene importato molto presto dalla Full: agganciare qui il CSS
# permette di averlo già nel primo blocco di stile, senza lampeggi post-render.
install_full_mobile_compact_css()
