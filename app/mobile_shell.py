# -*- coding: utf-8 -*-
"""Cornice mobile minimale condivisa dalle due modalità di Mor-tem."""

import streamlit as st
import streamlit.components.v1 as components


_MINIMAL_MOBILE_SHELL_CSS = r"""
<style>
@media (max-width: 768px) {
  /* Su mobile la barra Streamlit non partecipa al layout: il comando per la
     sidebar viene renderizzato nella normale riga del titolo qui sotto. */
  header[data-testid="stHeader"],
  #stDecoration,
  [data-testid="stDecoration"] {
    display: none !important;
  }

  [data-testid="stMainBlockContainer"],
  div.block-container {
    padding-top: 0.28rem !important;
  }

  /* Il titolo originale resta la fonte del testo, ma non occupa una seconda
     riga: il componente della testata lo legge e lo mostra accanto al menu. */
  [data-testid="stElementContainer"]:has(.mortem-full-title),
  [data-testid="stElementContainer"]:has(.mortem-msil-page-title) {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }
}
</style>
"""


_MOBILE_HEADER_HTML = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {
    margin: 0;
    padding: 0;
    background: transparent;
    overflow: hidden;
  }
  .mobile-page-head {
    box-sizing: border-box;
    display: grid;
    grid-template-columns: 2rem minmax(0, 1fr) 2rem;
    align-items: center;
    width: 100%;
    min-height: 2rem;
    margin: 0;
    padding: 0;
  }
  .menu-button {
    box-sizing: border-box;
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;
    width: 2rem;
    height: 2rem;
    margin: 0;
    padding: 0;
    border: 0;
    background: transparent;
    color: #31333f;
    cursor: pointer;
  }
  .menu-button span {
    display: block;
    width: 16px;
    height: 2px;
    border-radius: 999px;
    background: currentColor;
  }
  .page-title {
    grid-column: 2;
    min-width: 0;
    margin: 0;
    padding: 0;
    text-align: center;
    color: #31333f;
    font-size: 1.15rem;
    font-weight: 650;
    line-height: 1.05;
    white-space: nowrap;
  }
  .page-title.msil {
    font-size: 0.95rem;
  }
</style>
</head>
<body>
  <div class="mobile-page-head">
    <button class="menu-button" type="button" aria-label="Apri menu" title="Apri menu">
      <span></span><span></span><span></span>
    </button>
    <div class="page-title"></div>
  </div>

<script>
(() => {
  const parentWindow = window.parent;
  const parentDocument = parentWindow.document;
  const title = document.querySelector(".page-title");
  const menu = document.querySelector(".menu-button");

  function syncAppearance(source) {
    const sourceStyle = parentWindow.getComputedStyle(source);
    title.style.fontFamily = sourceStyle.fontFamily;
    title.style.color = sourceStyle.color;
    menu.style.color = sourceStyle.color;
  }

  function syncTitle() {
    const full = parentDocument.querySelector(".mortem-full-title");
    const msil = parentDocument.querySelector(".mortem-msil-page-title");
    const source = full || msil;
    if (!source) {
      window.setTimeout(syncTitle, 40);
      return;
    }
    title.textContent = source.textContent.trim();
    title.classList.toggle("msil", Boolean(msil));
    syncAppearance(source);
  }

  function openSidebar() {
    const selectors = [
      '[data-testid="stExpandSidebarButton"] button',
      '[data-testid="stSidebarCollapsedControl"] button',
      '[data-testid="collapsedControl"] button',
      '[data-testid="stExpandSidebarButton"]',
      '[data-testid="stSidebarCollapsedControl"]',
      '[data-testid="collapsedControl"]'
    ];
    for (const selector of selectors) {
      const target = parentDocument.querySelector(selector);
      if (target) {
        target.click();
        return;
      }
    }
  }

  menu.addEventListener("click", openSidebar);
  syncTitle();
})();
</script>
</body>
</html>
"""


def _request_is_mobile() -> bool:
    """Classifica la richiesta senza importare moduli UI con effetti collaterali."""
    if "__full_device_mobile" in st.session_state:
        return bool(st.session_state["__full_device_mobile"])

    try:
        headers = st.context.headers
    except Exception:
        headers = {}

    try:
        ch_mobile = str(headers.get("Sec-CH-UA-Mobile") or "").strip().lower()
    except Exception:
        ch_mobile = ""
    if ch_mobile in {"?1", "1", "true"}:
        return True
    if ch_mobile in {"?0", "0", "false"}:
        return False

    try:
        user_agent = str(headers.get("User-Agent") or "").casefold()
    except Exception:
        user_agent = ""

    return any(
        token in user_agent
        for token in (
            "iphone",
            "ipod",
            "windows phone",
            "opera mini",
            "opera mobi",
            "mobile",
            "android",
        )
    )


def install_minimal_mobile_shell() -> None:
    """Installa una testata mobile nel normale flusso della pagina."""
    st.markdown(_MINIMAL_MOBILE_SHELL_CSS, unsafe_allow_html=True)
    if _request_is_mobile():
        components.html(_MOBILE_HEADER_HTML, height=34, scrolling=False)
