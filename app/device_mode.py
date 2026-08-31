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
  /* Full desktop: ampia quanto serve, ma responsiva alla finestra. */
  html:has(body .mortem-full-title) {
    font-size: 18px !important;
  }

  html body:has(.mortem-full-title) div.block-container {
    box-sizing: border-box !important;
    width: min(96vw, 1440px) !important;
    max-width: 1440px !important;
    padding-left: clamp(0.8rem, 1.7vw, 1.5rem) !important;
    padding-right: clamp(0.8rem, 1.7vw, 1.5rem) !important;
  }

  html body:has(.mortem-full-title) .mortem-full-title {
    font-size: 1.28rem !important;
    line-height: 1.10 !important;
  }

  html body:has(.mortem-full-title) .mortem-section-title {
    font-size: 0.98rem !important;
    line-height: 1.12 !important;
    margin-bottom: 0.12rem !important;
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

  /* Compatta verticalmente il solo riquadro del raffreddamento. */
  html body:has(.mortem-full-title)
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"]) {
    padding: 0.72rem 0.92rem !important;
  }

  html body:has(.mortem-full-title)
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"]) > [data-testid="stVerticalBlock"] {
    justify-content: flex-start !important;
    gap: 0.34rem !important;
    min-height: 0 !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-cooling_standard_v2_grid_desktop"] > [data-testid="stVerticalBlock"],
  html body:has(.mortem-full-title)
  [class*="st-key-cooling_prudent_v2_grid_desktop"] > [data-testid="stVerticalBlock"] {
    gap: 0.42rem !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-cooling_heading_row_desktop"],
  html body:has(.mortem-full-title)
  [class*="st-key-cooling_heading_row_desktop"] [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    min-height: 1.65rem !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-cooling_heading_title_desktop"] {
    flex: 1 1 auto !important;
    min-width: 0 !important;
  }

  /* Su desktop Henssge è una checkbox testuale normale; l'icona resta mobile. */
  html body:has(.mortem-full-title)
  [class*="st-key-cooling_heading_actions_desktop"] {
    box-sizing: border-box !important;
    flex: 0 0 auto !important;
    width: max-content !important;
    min-width: max-content !important;
    max-width: none !important;
    overflow: visible !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-mortem_help_row_henssge"] {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    width: max-content !important;
    min-width: max-content !important;
    height: auto !important;
    min-height: 0 !important;
    gap: 0.22rem !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] {
    width: auto !important;
    min-width: max-content !important;
    max-width: none !important;
    height: auto !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  html body:has(.mortem-full-title)
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

  html body:has(.mortem-full-title)
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label > * {
    position: static !important;
    opacity: 1 !important;
    pointer-events: auto !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label::after {
    content: none !important;
    display: none !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label p {
    width: max-content !important;
    min-width: max-content !important;
    max-width: none !important;
    overflow: visible !important;
    white-space: nowrap !important;
    text-overflow: clip !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-mortem_help_row_henssge"] [data-testid="stCheckbox"] label p::before {
    content: "Metodo di ";
  }

  /* Una sola misura per tutti gli input principali: poco più larga della voce
     più lunga, ma capace di ridursi insieme alla finestra. */
  body:has([class*="st-key-stima_cautelativa_beta"]) {
    --mortem-cooling-row-width: clamp(21.5rem, 27vw, 27rem);
    --mortem-cooling-weight-shift: 0.55rem;
  }

  /* I due campi di ciascuna riga non si dilatano fino ai bordi della pagina. */
  html body:has(.mortem-full-title)
  [class*="st-key-cooling_standard_v2_grid_desktop"] [data-testid="stHorizontalBlock"],
  html body:has(.mortem-full-title)
  [class*="st-key-cooling_prudent_v2_grid_desktop"] [data-testid="stHorizontalBlock"]:not([class*="st-key-prudent_weight_row_desktop"]) {
    box-sizing: border-box !important;
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, var(--mortem-cooling-row-width))) !important;
    column-gap: clamp(0.70rem, 1.5vw, 1.15rem) !important;
    row-gap: 0 !important;
    width: max-content !important;
    max-width: 100% !important;
    min-width: 0 !important;
    justify-content: start !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-cooling_standard_v2_grid_desktop"] [data-testid="stHorizontalBlock"] > [data-testid="column"],
  html body:has(.mortem-full-title)
  [class*="st-key-cooling_prudent_v2_grid_desktop"] [data-testid="stHorizontalBlock"]:not([class*="st-key-prudent_weight_row_desktop"]) > [data-testid="column"] {
    box-sizing: border-box !important;
    flex: none !important;
    width: var(--mortem-cooling-row-width) !important;
    max-width: var(--mortem-cooling-row-width) !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* Su finestre che non contengono due righe complete, la griglia si riduce
     mantenendo due colonne finché possibile. */
  @media (max-width: 980px) {
    body:has([class*="st-key-stima_cautelativa_beta"]) {
      --mortem-cooling-row-width: min(43vw, 24rem);
    }
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_decimal_fcpanel_"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stElementContainer"]:has([class*="st-key-mortem_decimal_fcpanel_"]) {
    width: min(100%, 24rem) !important;
    max-width: 24rem !important;
  }

  /* Il pannello FC resta compatto e aderente ai suoi contenuti. */
  html body:has(.mortem-full-title)
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"]),
  html body:has(.mortem-full-title)
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"]) {
    box-sizing: border-box !important;
    width: min(100%, 44rem) !important;
    max-width: 44rem !important;
    min-width: 0 !important;
    align-self: flex-start !important;
  }

  html body:has(.mortem-full-title)
  [class*="st-key-fcpanel_std_switch_row"],
  html body:has(.mortem-full-title)
  [class*="st-key-fcpanel_caut_switch_row"],
  html body:has(.mortem-full-title)
  [class*="st-key-fcpanel_std_surface_select_desktop"],
  html body:has(.mortem-full-title)
  [class*="st-key-fcpanel_caut_surface_select_desktop"] {
    width: min(100%, 40rem) !important;
    max-width: 40rem !important;
  }

  html body:has(.mortem-full-title)
  [class*="fc_apply_block_mobile"] {
    width: max-content !important;
    max-width: 100% !important;
    min-width: 0 !important;
    margin: 0.10rem 0 0 !important;
    padding: 0 !important;
    border: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    overflow: visible !important;
  }

  html body:has(.mortem-full-title)
  [class*="fc_apply_row_mobile"] {
    width: max-content !important;
    max-width: 100% !important;
    min-width: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    justify-content: flex-start !important;
    gap: 0.28rem !important;
    overflow: visible !important;
  }

  html body:has(.mortem-full-title) .mortem-fc-inline-result {
    height: 2rem !important;
    min-height: 2rem !important;
    max-height: 2rem !important;
    padding: 0 0.10rem 0 0 !important;
    background: transparent !important;
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
