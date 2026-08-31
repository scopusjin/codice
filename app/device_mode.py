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
  --mortem-cooling-weight-shift: 0.55rem;
}

/* L'intestazione del raffreddamento non deve mai diventare un'area scrollabile.
   La specificità supera le vecchie regole responsive che lasciavano overflow
   visibile, senza modificare la disposizione di titolo, Henssge e pulsante ?. */
html body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-cooling_heading_row_mobile"],
html body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-cooling_heading_row_mobile"] [data-testid="stHorizontalBlock"],
html body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-cooling_heading_row_desktop"],
html body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-cooling_heading_row_desktop"] [data-testid="stHorizontalBlock"] {
  box-sizing: border-box !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  height: auto !important;
  min-height: 0 !important;
  max-height: none !important;
  overflow: hidden !important;
  scrollbar-width: none !important;
}

html body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-cooling_heading_row_mobile"]::-webkit-scrollbar,
html body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-cooling_heading_row_mobile"] [data-testid="stHorizontalBlock"]::-webkit-scrollbar,
html body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-cooling_heading_row_desktop"]::-webkit-scrollbar,
html body:has([class*="st-key-stima_cautelativa_beta"])
[class*="st-key-cooling_heading_row_desktop"] [data-testid="stHorizontalBlock"]::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
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
   larghezza delle altre. La parte numerica viene accorciata leggermente per
   mantenere 70.0 sulla stessa verticale dei valori delle altre righe. */
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
    minmax(
      0,
      calc(
        var(--mortem-cooling-row-width)
        - var(--mortem-cooling-action-col)
        - var(--mortem-cooling-weight-shift)
      )
    )
    calc(var(--mortem-cooling-action-col) + var(--mortem-cooling-weight-shift)) !important;
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
  width: calc(var(--mortem-cooling-action-col) + var(--mortem-cooling-weight-shift)) !important;
  max-width: calc(var(--mortem-cooling-action-col) + var(--mortem-cooling-weight-shift)) !important;
  min-width: calc(var(--mortem-cooling-action-col) + var(--mortem-cooling-weight-shift)) !important;
  margin: 0 !important;
  padding: 0 0 0 0.18rem !important;
}

/* La riga del risultato FC resta centrata come gruppo anche su desktop. */
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_row_mobile"] {
  justify-content: center !important;
  gap: 0.34rem !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_value_mobile"],
body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] {
  flex: 0 0 auto !important;
  width: max-content !important;
  min-width: max-content !important;
  margin: 0 !important;
  padding: 0 !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
[class*="fc_apply_action_mobile"] {
  margin-left: 0.08rem !important;
}

body:has([class*="st-key-stima_cautelativa_beta"])
.mortem-fc-inline-result {
  padding-left: 0 !important;
  padding-right: 0 !important;
}

@media (max-width: 768px) {
  /* Il testo esplicativo della modalità prudente non deve lasciare spazio. */
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

  /* Compensa il gap verticale del blocco Streamlit tra il toggle e la pila
     prudente: le righe iniziano subito sotto Condizioni variabili. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-cooling_prudent_v2_stack_mobile"] {
    margin-top: -0.70rem !important;
    padding-top: 0 !important;
    gap: 0.18rem !important;
  }

  [class*="st-key-stima_cautelativa_beta"] [data-testid="stToggle"],
  [class*="st-key-stima_cautelativa_beta"] [data-testid="stToggle"] label {
    position: relative !important;
    z-index: 3 !important;
    pointer-events: auto !important;
  }

  /* Il pannello suggerimenti ha la stessa larghezza della riga FC e risale
     fino a raccordarsi con Consiglia. Lo sfondo usa la stessa miscela del
     pulsante Consiglia attivo nel componente V2. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] {
    box-sizing: border-box !important;
    width: var(--mortem-cooling-row-width) !important;
    max-width: 100% !important;
    min-width: 0 !important;
    margin-top: -0.70rem !important;
    margin-bottom: 0 !important;
    padding: 0.52rem 0.24rem 0.34rem !important;
    border: 0 !important;
    border-radius: 0 0 0.55rem 0.55rem !important;
    box-shadow: none !important;
    background: color-mix(
      in srgb,
      var(--st-secondary-background-color, #F0F2F6) 86%,
      var(--st-primary-color, #168AC1) 14%
    ) !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] > [data-testid="stVerticalBlock"] {
    gap: 0.18rem !important;
  }

  /* Un po' più di respiro prima e dopo la riga Vestiti/coperte. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] [class*="st-key-fcpanel_std_switch_row"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] [class*="st-key-fcpanel_caut_switch_row"] {
    margin-top: 0.20rem !important;
    margin-bottom: 0.08rem !important;
  }

  /* FC suggerito e Usalo restano centrati, con un distacco minimo tra i due. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] [class*="fc_apply_block_mobile"] {
    width: 100% !important;
    margin-top: 0.10rem !important;
    padding-top: 0.08rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-full_fc_panel_mobile"] [class*="fc_apply_row_mobile"] {
    width: 100% !important;
    justify-content: center !important;
    gap: 0.34rem !important;
  }
}

@media (min-width: 769px) {
  /* La versione completa desktop sfrutta meglio la larghezza disponibile,
     senza modificare la resa mobile né la pagina MSIL. */
  html:has(body .mortem-full-title) {
    font-size: 18px !important;
  }

  html body:has(.mortem-full-title) div.block-container {
    box-sizing: border-box !important;
    width: min(94vw, 1500px) !important;
    max-width: 1500px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
  }

  html body:has(.mortem-full-title) .mortem-full-title {
    font-size: 1.28rem !important;
    line-height: 1.10 !important;
  }

  html body:has(.mortem-full-title) .mortem-section-title {
    font-size: 0.98rem !important;
    line-height: 1.18 !important;
  }

  html body:has(.mortem-full-title) [data-testid="stCheckbox"] label p,
  html body:has(.mortem-full-title) [data-testid="stToggle"] label p,
  html body:has(.mortem-full-title) [data-baseweb="select"] * {
    font-size: 0.96rem !important;
  }

  html body:has(.mortem-full-title) [data-testid="stDateInput"] input,
  html body:has(.mortem-full-title) button {
    font-size: 0.96rem !important;
  }

  /* L'azione Henssge deve mostrare per intero il testo, senza ellissi. */
  html body:has(.mortem-full-title)
  [class*="st-key-cooling_heading_actions_desktop"] {
    box-sizing: border-box !important;
    flex: 0 0 18.5rem !important;
    width: 18.5rem !important;
    min-width: 18.5rem !important;
    max-width: 18.5rem !important;
    overflow: visible !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-cooling_heading_actions_desktop"] [data-testid="stCheckbox"],
  html body:has(.mortem-full-title)
  [class*="st-key-cooling_heading_actions_desktop"] [data-testid="stCheckbox"] label,
  html body:has(.mortem-full-title)
  [class*="st-key-cooling_heading_actions_desktop"] [data-testid="stCheckbox"] label p {
    box-sizing: border-box !important;
    width: max-content !important;
    min-width: max-content !important;
    max-width: none !important;
    overflow: visible !important;
    white-space: nowrap !important;
    text-overflow: clip !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-cooling_heading_actions_desktop"] [data-testid="stCheckbox"] label p::before {
    content: "Metodo di ";
  }

  body:has([class*="st-key-stima_cautelativa_beta"]) {
    --mortem-cooling-row-width: 36rem;
    --mortem-cooling-weight-shift: 0.55rem;
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
