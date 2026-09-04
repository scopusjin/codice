# -*- coding: utf-8 -*-
"""Anteprima di sviluppo della Full con vero viewport desktop da telefono."""

import streamlit as st
import streamlit.components.v1 as components


_DESKTOP_WIDTH = 1440
_PREVIEW_HEIGHT = 920

st.set_page_config(
    page_title="Mor-tem · Anteprima desktop",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.caption(
    "Anteprima tecnica: la Full è caricata in un vero viewport da 1440 px "
    "e ridotta in scala per essere controllata dal telefono."
)

components.html(
    f"""
    <style>
      html, body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        background: transparent;
      }}
      #mortem-preview-shell {{
        position: relative;
        width: 100%;
        height: {_PREVIEW_HEIGHT}px;
        overflow: hidden;
        background: transparent;
      }}
      #mortem-desktop-frame {{
        position: absolute;
        top: 0;
        left: 0;
        width: {_DESKTOP_WIDTH}px;
        border: 0;
        transform-origin: top left;
        background: white;
      }}
    </style>

    <div id="mortem-preview-shell">
      <iframe
        id="mortem-desktop-frame"
        src="/"
        title="Mor-tem desktop preview"
        scrolling="yes"
      ></iframe>
    </div>

    <script>
      (() => {{
        const desktopWidth = {_DESKTOP_WIDTH};
        const previewHeight = {_PREVIEW_HEIGHT};
        const shell = document.getElementById("mortem-preview-shell");
        const frame = document.getElementById("mortem-desktop-frame");

        const resizePreview = () => {{
          const availableWidth =
            shell.clientWidth || document.documentElement.clientWidth || window.innerWidth;
          const scale = Math.min(1, availableWidth / desktopWidth);
          frame.style.width = `${{desktopWidth}}px`;
          frame.style.height = `${{Math.ceil(previewHeight / scale)}}px`;
          frame.style.transform = `scale(${{scale}})`;
        }};

        resizePreview();
        window.addEventListener("resize", resizePreview);
        new ResizeObserver(resizePreview).observe(shell);
      }})();
    </script>
    """,
    height=_PREVIEW_HEIGHT,
    scrolling=False,
)
