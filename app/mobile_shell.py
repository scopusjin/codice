# -*- coding: utf-8 -*-
"""Cornice mobile minimale condivisa dalle due modalità di Mor-tem."""

import streamlit as st


_MINIMAL_MOBILE_SHELL_CSS = r"""
<style>
@media (max-width: 768px) {
  /* Nessuna barra Streamlit visibile: resta soltanto il comando nativo
     che apre la sidebar, fissato nell'angolo superiore sinistro. */
  header[data-testid="stHeader"] {
    min-height: 2.35rem !important;
    height: 2.35rem !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
  }

  header[data-testid="stHeader"] [data-testid="stToolbar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    min-height: 2.35rem !important;
    height: 2.35rem !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
  }

  header[data-testid="stHeader"] [data-testid="stStatusWidget"],
  header[data-testid="stHeader"] [data-testid="stAppDeployButton"],
  header[data-testid="stHeader"] [data-testid="stToolbarActionButton"],
  header[data-testid="stHeader"] [data-testid="stMainMenu"],
  header[data-testid="stHeader"] [data-testid="viewerBadge"],
  header[data-testid="stHeader"] #MainMenu,
  header[data-testid="stHeader"] [class*="viewerBadge"],
  #stDecoration,
  [data-testid="stDecoration"] {
    display: none !important;
    visibility: hidden !important;
  }

  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"] {
    position: fixed !important;
    top: 0.34rem !important;
    left: 0.38rem !important;
    z-index: 1000001 !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: 2rem !important;
    min-width: 2rem !important;
    height: 2rem !important;
    min-height: 2rem !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    pointer-events: auto !important;
  }

  [data-testid="stExpandSidebarButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    align-items: center !important;
    justify-content: center !important;
    width: 2rem !important;
    min-width: 2rem !important;
    height: 2rem !important;
    min-height: 2rem !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    pointer-events: auto !important;
  }

  [data-testid="stExpandSidebarButton"] button {
    width: 2rem !important;
    min-width: 2rem !important;
    height: 2rem !important;
    min-height: 2rem !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
  }

  [data-testid="stMainBlockContainer"],
  div.block-container {
    padding-top: 0.42rem !important;
  }

  [data-testid="stElementContainer"]:has(.mortem-full-title),
  [data-testid="stElementContainer"]:has(.mortem-msil-page-title) {
    box-sizing: border-box !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 2rem !important;
    margin: 0 0 0.18rem 0 !important;
    padding: 0 2.35rem !important;
  }

  .mortem-full-title,
  .mortem-msil-page-title {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: center !important;
  }
}
</style>
"""


def install_minimal_mobile_shell() -> None:
    """Installa la cornice mobile dopo ``st.set_page_config``."""
    st.markdown(_MINIMAL_MOBILE_SHELL_CSS, unsafe_allow_html=True)
