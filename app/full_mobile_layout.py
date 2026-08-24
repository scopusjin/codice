# -*- coding: utf-8 -*-
"""Layout responsive della schermata completa di Mor-tem.

Il CSS viene inserito al primo ``st.markdown`` della pagina, quindi dopo
``st.set_page_config`` ma prima dei widget. In questo modo il layout mobile è
già attivo al primo render e non dipende da manipolazioni DOM post-render del
componente numerico.
"""

import streamlit as st


_FULL_MOBILE_CSS = r"""
<style>
@media (max-width: 768px) {
  /* Le regole principali sono limitate alla schermata completa: la MSIL non
     possiede il toggle stima_cautelativa_beta. */
  body:has([class*="st-key-stima_cautelativa_beta"]) .mortem-full-field-heading {
    display: none !important;
  }

  /* Le due righe Streamlit dei parametri diventano una pila di controlli a
     tutta larghezza già al primo render. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_rt_val"]),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_ta_base_val"]) {
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    gap: clamp(0.22rem, 1vw, 0.36rem) !important;
    width: 100% !important;
    margin: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_rt_val"])
  > [data-testid="column"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-mortem_decimal_ta_base_val"])
  > [data-testid="column"] {
    flex: 0 0 auto !important;
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* Nota prudenziale e switch "Specifica range" restano ordinati in verticale
     senza comprimersi in due colonne sul telefono. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-range_unico_beta"]) {
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    gap: clamp(0.20rem, 1vw, 0.34rem) !important;
    width: 100% !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has([class*="st-key-range_unico_beta"])
  > [data-testid="column"] {
    flex: 0 0 auto !important;
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* Riga Peso: il controllo prende tutto lo spazio residuo; ±3 kg occupa
     esattamente il proprio contenuto e non può spezzarsi. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has(> [data-testid="column"]:nth-child(2) [class*="st-key-peso_stimato_beta"]) {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) max-content !important;
    align-items: center !important;
    column-gap: clamp(0.10rem, 0.8vw, 0.22rem) !important;
    row-gap: 0 !important;
    width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has(> [data-testid="column"]:nth-child(2) [class*="st-key-peso_stimato_beta"])
  > [data-testid="column"] {
    width: auto !important;
    max-width: none !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"]:has(> [data-testid="column"]:nth-child(2) [class*="st-key-peso_stimato_beta"])
  > [data-testid="column"]:nth-child(2),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"] [data-testid="stToggle"] {
    width: max-content !important;
    max-width: max-content !important;
    min-width: max-content !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"] label {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: clamp(0.16rem, 0.7vw, 0.26rem) !important;
    width: max-content !important;
    min-width: max-content !important;
    margin: 0 !important;
    padding: 0 !important;
    white-space: nowrap !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"] label p,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [class*="st-key-peso_stimato_beta"] label span {
    width: max-content !important;
    min-width: max-content !important;
    white-space: nowrap !important;
    overflow-wrap: normal !important;
    word-break: keep-all !important;
  }

  /* Se il componente aggiunge le vecchie classi di compattezza, la geometria
     resta comunque quella statica sopra: nessun salto di layout. */
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stHorizontalBlock"].mortem-decimal-compact-row {
    gap: clamp(0.22rem, 1vw, 0.36rem) !important;
    row-gap: 0 !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlock"].mortem-decimal-compact-stack {
    gap: clamp(0.22rem, 1vw, 0.36rem) !important;
  }

  /* Pannello Suggerisci FC della schermata completa. I prefissi std/caut sono
     distinti da fcpanel_mobile usato dalla MSIL. */
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  [data-testid="stVerticalBlock"],
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  [data-testid="stVerticalBlock"] {
    gap: clamp(0.24rem, 1.1vw, 0.42rem) !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  div[role="radiogroup"],
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  div[role="radiogroup"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: clamp(0.18rem, 1vw, 0.34rem) !important;
  }

  [data-testid="stHorizontalBlock"]:has([class*="st-key-fcpanel_std_toggle_vestito"]),
  [data-testid="stHorizontalBlock"]:has([class*="st-key-fcpanel_caut_toggle_vestito"]) {
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    gap: clamp(0.18rem, 1vw, 0.32rem) !important;
    width: 100% !important;
  }

  [data-testid="stHorizontalBlock"]:has([class*="st-key-fcpanel_std_toggle_vestito"])
  > [data-testid="column"],
  [data-testid="stHorizontalBlock"]:has([class*="st-key-fcpanel_caut_toggle_vestito"])
  > [data-testid="column"] {
    flex: 0 0 auto !important;
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  [data-testid="stToggle"],
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  [data-testid="stToggle"] {
    margin: 0 !important;
    padding: 0 !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  [data-testid="stSelectbox"] > label,
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  [data-testid="stSelectbox"] > label {
    margin-bottom: 0.15rem !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_std_radio_stato_corpo"])
  [data-testid="stButton"] button,
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-fcpanel_caut_radio_stato_corpo"])
  [data-testid="stButton"] button {
    min-height: 2.2rem !important;
  }
}
</style>
"""


_FIELD_HEADING_TOKENS = (
    "T. rettale",
    "T. ante-mortem",
    "Peso",
    "T. ambientale",
    "Fattore di correzione",
)


def _tag_full_field_heading(body):
    if not isinstance(body, str):
        return body
    if "font-size: 0.88rem;" not in body or "padding-top" in body:
        return body
    if not any(token in body for token in _FIELD_HEADING_TOKENS):
        return body

    source_single = "<div style='font-size: 0.88rem;'>"
    source_double = '<div style="font-size: 0.88rem;">'
    replacement = "<div class='mortem-full-field-heading' style='font-size: 0.88rem;'>"
    if source_single in body:
        return body.replace(source_single, replacement, 1)
    if source_double in body:
        return body.replace(source_double, replacement, 1)
    return body


def install_full_mobile_layout():
    """Installa CSS/heading tagging senza eseguire comandi Streamlit all'import."""
    if getattr(st, "_full_mobile_layout_installed", False):
        return

    original_markdown = st.markdown
    css_injected = False

    def markdown_with_full_mobile_layout(body, *args, **kwargs):
        nonlocal css_injected
        if not css_injected:
            original_markdown(_FULL_MOBILE_CSS, unsafe_allow_html=True)
            css_injected = True
        return original_markdown(_tag_full_field_heading(body), *args, **kwargs)

    st.markdown = markdown_with_full_mobile_layout
    st._full_mobile_layout_installed = True
