# -*- coding: utf-8 -*-
"""Anteprima di sviluppo della Full con vero viewport desktop da telefono."""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


_DESKTOP_WIDTH = 1440
_PREVIEW_HEIGHT = 920
_DEVICE_SESSION_KEY = "__full_device_mobile"
_MAIN_SCRIPT = Path(__file__).resolve().parents[1] / "Stima_epoca_decesso.py"
_MAIN_PAGE_CONFIG = (
    'st.set_page_config(page_title="Mor-tem", layout="wide", '
    'initial_sidebar_state="collapsed")'
)

try:
    _frame_mode = str(st.query_params.get("frame", "")).strip() == "1"
except Exception:
    _frame_mode = False

st.set_page_config(
    page_title="Mor-tem · Anteprima desktop",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if _frame_mode:
    source = _MAIN_SCRIPT.read_text(encoding="utf-8")
    if source.count(_MAIN_PAGE_CONFIG) != 1:
        st.error(
            "Anteprima desktop non disponibile: la configurazione della pagina Full "
            "è cambiata e il wrapper di sviluppo deve essere aggiornato."
        )
        st.stop()

    source = source.replace(_MAIN_PAGE_CONFIG, "", 1)
    st.session_state[_DEVICE_SESSION_KEY] = False
    exec(
        compile(source, str(_MAIN_SCRIPT), "exec"),
        {
            "__name__": "__main__",
            "__file__": str(_MAIN_SCRIPT),
        },
    )
    st.stop()

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

        const parentPath = window.parent.location.pathname;
        frame.src = `${{parentPath}}?frame=1`;

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
