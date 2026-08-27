# -*- coding: utf-8 -*-
"""Regole di compattezza aggiuntive per la sola Full mobile."""

import streamlit as st


_FULL_MOBILE_COMPACT_CSS = r"""
<style>
@media (max-width: 768px) {
  /* Il riquadro Raffreddamento usa quasi tutta la larghezza disponibile. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"]) {
    padding: 0.42rem 0.34rem !important;
  }

  /* Titolo a sinistra; controllo Henssge + helper all'estrema destra sulla
     stessa riga. Tutti gli altri elementi continuano a occupare l'intera riga. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"])
  > [data-testid="stVerticalBlock"] {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) auto !important;
    column-gap: 0.18rem !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"])
  > [data-testid="stVerticalBlock"] > * {
    grid-column: 1 / -1;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"])
  > [data-testid="stVerticalBlock"] > *:has(.mortem-section-title) {
    grid-column: 1 !important;
    grid-row: 1 !important;
    align-self: center !important;
    min-width: 0 !important;
    margin: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-henssge_non_applicabile"])
  > [data-testid="stVerticalBlock"] > *:has([class*="st-key-mortem_help_row_henssge"]) {
    grid-column: 2 !important;
    grid-row: 1 !important;
    justify-self: end !important;
    align-self: center !important;
    width: max-content !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-mortem_help_row_henssge"] {
    width: max-content !important;
    min-width: max-content !important;
    gap: 0.10rem !important;
    margin: 0 !important;
    padding: 0 !important;
    justify-content: flex-end !important;
  }

  /* Il checkbox resta il vero controllo e conserva la stessa chiave/stato,
     ma sul mobile viene visualizzato soltanto come simbolo di divieto. */
  body:has([class*="st-key-stima_cautelativa_beta"])
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

  /* Il pannello FC non ha più un secondo riquadro: uno sfondo azzurro leggero
     delimita il gruppo senza sottrarre spazio laterale. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"]):not(:has([class*="st-key-henssge_non_applicabile"])),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"]):not(:has([class*="st-key-henssge_non_applicabile"])) {
    border: 0 !important;
    outline: 0 !important;
    box-shadow: none !important;
    border-radius: 0.55rem !important;
    background: rgba(33, 150, 243, 0.055) !important;
    padding: 0.34rem 0.28rem !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    width: 100% !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"]):not(:has([class*="st-key-henssge_non_applicabile"]))
  > [data-testid="stVerticalBlock"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"]):not(:has([class*="st-key-henssge_non_applicabile"]))
  > [data-testid="stVerticalBlock"] {
    border: 0 !important;
    outline: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 0 !important;
  }
}
</style>
"""


def install_full_mobile_compact_css() -> None:
    """Allega le regole al CSS iniziale della Full, senza render tardivi."""
    if getattr(st, "_full_mobile_compact_css_installed", False):
        return

    original_markdown = st.markdown

    def markdown_with_full_mobile_compact_css(body, *args, **kwargs):
        if isinstance(body, str) and ".final-text{" in body:
            # Viene appeso dopo il CSS responsive principale, così queste
            # regole più specifiche prevalgono senza manipolazioni DOM tardive.
            body = body + _FULL_MOBILE_COMPACT_CSS
            kwargs["unsafe_allow_html"] = True
        return original_markdown(body, *args, **kwargs)

    st.markdown = markdown_with_full_mobile_compact_css
    st._full_mobile_compact_css_installed = True
