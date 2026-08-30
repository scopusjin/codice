# -*- coding: utf-8 -*-
"""Classificazione stabile mobile/desktop per la schermata completa di Mor-tem."""

from collections.abc import Mapping

import streamlit as st

import app.full_mobile_compact as _full_mobile_compact
from app.full_mobile_compact import install_full_mobile_compact_css


_SESSION_KEY = "__full_device_mobile"


# Larghezza unica dei controlli numerici della Full. Queste regole vengono
# accodate al CSS compatto già iniettato a ogni rerun, quindi prevalgono sulle
# vecchie regole ``width: 100%`` senza aggiungere un secondo meccanismo di
# rendering degli stili.
_FULL_COOLING_ROW_WIDTH_CSS = r"""
<style>
@media (max-width: 768px) {
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_"]) {
    box-sizing: border-box !important;
    width: 20rem !important;
    max-width: 100% !important;
    min-width: 0 !important;
    align-self: flex-start !important;
  }
}

@media (min-width: 769px) {
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_"]) {
    box-sizing: border-box !important;
    width: 26rem !important;
    max-width: 100% !important;
    min-width: 0 !important;
    align-self: flex-start !important;
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
