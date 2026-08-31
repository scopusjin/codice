# -*- coding: utf-8 -*-
"""Classificazione stabile mobile/desktop per la schermata completa di Mor-tem."""

from collections.abc import Mapping

import streamlit as st

import app.full_mobile_compact as _full_mobile_compact
from app.full_mobile_compact import install_full_mobile_compact_css


_SESSION_KEY = "__full_device_mobile"


# Sul desktop il CSS della Full deve nascere già con Henssge testuale.
# Sostituiamo quindi, prima dell'iniezione nel browser, il solo blocco desktop
# che trasformava la checkbox in icona. Il blocco mobile resta intatto.
_DESKTOP_HENSSGE_ICON_RULES = r'''  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] {
    width: 1.55rem !important;
    min-width: 1.55rem !important;
    max-width: 1.55rem !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label {
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 1.55rem !important;
    min-width: 1.55rem !important;
    height: 1.55rem !important;
    min-height: 1.55rem !important;
    margin: 0 !important;
    padding: 0 !important;
    cursor: pointer !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label > * {
    position: absolute !important;
    opacity: 0 !important;
    pointer-events: none !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label::after {
    content: "⦸";
    position: static !important;
    display: block !important;
    font-size: 1.22rem !important;
    line-height: 1 !important;
    font-weight: 500 !important;
    opacity: 0.58;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label:has(input:checked)::after {
    opacity: 1 !important;
    color: #c62828 !important;
    font-weight: 700 !important;
  }
'''

_DESKTOP_HENSSGE_TEXT_RULES = r'''  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_row_desktop"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_row_desktop"] [data-testid="stHorizontalBlock"] {
    box-sizing: border-box !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    overflow: visible !important;
    scrollbar-width: none !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_title_desktop"] {
    flex: 1 1 13rem !important;
    width: auto !important;
    min-width: 13rem !important;
    max-width: none !important;
    overflow: visible !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_title_desktop"] .mortem-section-title {
    width: max-content !important;
    min-width: max-content !important;
    max-width: none !important;
    overflow: visible !important;
    white-space: nowrap !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_row_desktop"]::-webkit-scrollbar,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_heading_row_desktop"] [data-testid="stHorizontalBlock"]::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] {
    width: auto !important;
    min-width: max-content !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label {
    position: static !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: max-content !important;
    min-width: max-content !important;
    max-width: none !important;
    height: auto !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    white-space: nowrap !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label > * {
    position: static !important;
    opacity: 1 !important;
    pointer-events: auto !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label::after {
    content: none !important;
    display: none !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label p {
    width: max-content !important;
    min-width: max-content !important;
    max-width: none !important;
    overflow: visible !important;
    white-space: nowrap !important;
    text-overflow: clip !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label p::before {
    content: "Metodo di ";
  }

  /* Pannello FC desktop: stessa resa compatta della Full mobile, mantenendo
     però le etichette estese già fornite dal ramo desktop. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"]):not(:has([class*="st-key-henssge_non_applicabile"])),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"]):not(:has([class*="st-key-henssge_non_applicabile"])) {
    box-sizing: border-box !important;
    width: min(100%, 46rem) !important;
    max-width: 46rem !important;
    min-width: 0 !important;
    align-self: flex-start !important;
    margin: 0.18rem 0 0 0 !important;
    padding: 0.34rem 0.42rem !important;
    border: 0 !important;
    border-radius: 0.55rem !important;
    box-shadow: none !important;
    background: color-mix(
      in srgb,
      var(--st-secondary-background-color, #F0F2F6) 86%,
      var(--st-primary-color, #168AC1) 14%
    ) !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  > [data-testid="stVerticalBlock"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  > [data-testid="stVerticalBlock"] {
    gap: 0.16rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_switch_row"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_switch_row"] {
    margin-top: 0.12rem !important;
    margin-bottom: -0.08rem !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_fcpanel_"] {
    height: 34px !important;
    min-height: 34px !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_fcpanel_"] iframe {
    display: block !important;
    height: 34px !important;
    min-height: 34px !important;
    max-height: 34px !important;
  }

  /* I quattro stepper degli strati desktop hanno tutti la stessa larghezza,
     poco superiore a quella necessaria per l'etichetta più lunga. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_fcpanel_"][class*="_strati_sottili"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_fcpanel_"][class*="_strati_spessi"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_fcpanel_"][class*="_coperte_medie"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_fcpanel_"][class*="_coperte_pesanti"] {
    box-sizing: border-box !important;
    width: min(100%, 29rem) !important;
    max-width: 29rem !important;
    min-width: 0 !important;
    align-self: flex-start !important;
  }

  /* Sul desktop il selettore mantiene il testo interno ma non il titolo
     separato "Superficie di appoggio". */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_surface_select_desktop"] [data-testid="stSelectbox"] > label,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_surface_select_desktop"] [data-testid="stSelectbox"] > label {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_surface_select_desktop"] [data-testid="stSelectbox"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_surface_select_desktop"] [data-testid="stSelectbox"] {
    margin-top: 0.04rem !important;
    margin-bottom: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_fc_apply_row_mobile"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_fc_apply_row_mobile"] {
    align-items: center !important;
    gap: 0.34rem !important;
    margin-top: 0.04rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_fc_apply_value_mobile"] .mortem-fc-inline-result,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_fc_apply_value_mobile"] .mortem-fc-inline-result {
    display: flex !important;
    align-items: center !important;
    min-height: 2.2rem !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_std_fc_apply_action_mobile"] button,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-fcpanel_caut_fc_apply_action_mobile"] button {
    min-height: 2.2rem !important;
    height: 2.2rem !important;
    margin: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }
'''


def _prepare_full_desktop_henssge_css() -> None:
    css = _full_mobile_compact._FULL_MOBILE_COMPACT_CSS
    marker = "@media (min-width: 769px) {"
    prefix, separator, desktop_css = css.partition(marker)
    if not separator or _DESKTOP_HENSSGE_ICON_RULES not in desktop_css:
        return
    desktop_css = desktop_css.replace(
        _DESKTOP_HENSSGE_ICON_RULES,
        _DESKTOP_HENSSGE_TEXT_RULES,
        1,
    )
    _full_mobile_compact._FULL_MOBILE_COMPACT_CSS = prefix + separator + desktop_css


_prepare_full_desktop_henssge_css()


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
