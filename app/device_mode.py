# -*- coding: utf-8 -*-
"""Classificazione stabile mobile/desktop per la schermata completa di Mor-tem."""

from collections.abc import Mapping

import streamlit as st

import app.full_mobile_compact as _full_mobile_compact
from app.full_mobile_compact import install_full_mobile_compact_css


_SESSION_KEY = "__full_device_mobile"


# Griglia unica dei controlli del raffreddamento della Full.
# Il CSS viene accodato al blocco compatto già iniettato a ogni rerun:
# non introduce un secondo meccanismo di stile e resta stabile dopo Consiglia.
_FULL_COOLING_ROW_WIDTH_CSS = r"""
<style>
body:has([class*="st-key-stima_cautelativa_beta"]) {
  --mortem-cooling-row-width: 20rem;
  --mortem-cooling-label-col: 7.5rem;
  --mortem-cooling-value-col: 3rem;
  --mortem-cooling-unit-col: 1.5rem;
  --mortem-cooling-step-col: 1.8rem;
  --mortem-cooling-action-col: 4.4rem;
}

/* Tutti i componenti numerici hanno la stessa larghezza complessiva. */
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

/* Dentro ogni riga: etichetta | valore | unità | − | + | azione.
   La colonna azione resta vuota quando non serve; così valori e pulsanti
   rimangono perfettamente incolonnati con la riga FC/Consiglia. */
body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile {
  position: relative !important;
  display: grid !important;
  grid-template-columns:
    var(--mortem-cooling-label-col)
    var(--mortem-cooling-value-col)
    var(--mortem-cooling-unit-col)
    var(--mortem-cooling-step-col)
    var(--mortem-cooling-step-col)
    var(--mortem-cooling-action-col) !important;
  align-items: stretch !important;
  width: 100% !important;
  min-width: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile .mobile-label {
  grid-column: 1 !important;
  min-width: 0 !important;
  width: auto !important;
  padding-left: 8px !important;
  padding-right: 5px !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile .number-input {
  grid-column: 2 !important;
  box-sizing: border-box !important;
  width: 100% !important;
  min-width: 0 !important;
  max-width: none !important;
  margin-left: 0 !important;
  padding-left: 1px !important;
  padding-right: 3px !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile .mobile-unit {
  grid-column: 3 !important;
  box-sizing: border-box !important;
  display: flex !important;
  width: 100% !important;
  min-width: 0 !important;
  justify-content: flex-start !important;
  padding-left: 1px !important;
  padding-right: 1px !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile .mobile-unit:empty {
  visibility: hidden !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile .number-minus {
  grid-column: 4 !important;
  width: 100% !important;
  min-width: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile .number-plus {
  grid-column: 5 !important;
  width: 100% !important;
  min-width: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile .suggest-button {
  grid-column: 6 !important;
  box-sizing: border-box !important;
  width: 100% !important;
  min-width: 0 !important;
  max-width: none !important;
}

/* Il ? della temperatura appartiene visivamente alla colonna etichetta,
   senza spostare la colonna dei valori. */
body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile .temperature-help.is-visible {
  position: absolute !important;
  left: calc(var(--mortem-cooling-label-col) - 1.55rem) !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  width: 1.35rem !important;
  height: 100% !important;
  z-index: 2 !important;
  margin: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile.has-help .mobile-label {
  padding-right: 1.7rem !important;
}

/* Riga Peso con ±3 kg: il toggle occupa esattamente la colonna "azione".
   Il componente numerico usa le prime cinque colonne, quindi 70.0 resta
   allineato con tutti gli altri valori. */
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
    calc(var(--mortem-cooling-row-width) - var(--mortem-cooling-action-col))
    var(--mortem-cooling-action-col) !important;
  align-items: center !important;
  gap: 0 !important;
  width: var(--mortem-cooling-row-width) !important;
  max-width: 100% !important;
  min-width: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_row_mobile"] [data-testid="column"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_row_desktop"] [data-testid="column"] {
  width: 100% !important;
  min-width: 0 !important;
  max-width: none !important;
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
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_value_mobile"] .number-control.compact-mobile,
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_value_desktop"] .number-control.compact-mobile {
  grid-template-columns:
    var(--mortem-cooling-label-col)
    var(--mortem-cooling-value-col)
    var(--mortem-cooling-unit-col)
    var(--mortem-cooling-step-col)
    var(--mortem-cooling-step-col) !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_uncertainty_mobile"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-prudent_weight_uncertainty_desktop"] {
  width: var(--mortem-cooling-action-col) !important;
  max-width: var(--mortem-cooling-action-col) !important;
  min-width: var(--mortem-cooling-action-col) !important;
  margin: 0 !important;
  padding-left: 0.18rem !important;
}

/* Anche i contatori di vestiti/coperte usano le stesse colonne di valore e
   −/+; cambia solo l'altezza compatta della riga. */
body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile.is-dense .number-input,
body:has([class*="st-key-stima_cautelativa_beta"])
.number-control.compact-mobile.is-dense .step-button {
  width: 100% !important;
  min-width: 0 !important;
  max-width: none !important;
}

@media (min-width: 769px) {
  body:has([class*="st-key-stima_cautelativa_beta"]) {
    --mortem-cooling-row-width: 28rem;
    --mortem-cooling-label-col: 15.5rem;
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
