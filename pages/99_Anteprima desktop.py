# -*- coding: utf-8 -*-
"""Anteprima di sviluppo della Full con viewport desktop da telefono."""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


_DESKTOP_VIEWPORT_WIDTH = 1440
_DEVICE_SESSION_KEY = "__full_device_mobile"
_MAIN_SCRIPT = Path(__file__).resolve().parents[1] / "Stima_epoca_decesso.py"
_MAIN_PAGE_CONFIG = (
    'st.set_page_config(page_title="Mor-tem", layout="wide", '
    'initial_sidebar_state="collapsed")'
)


st.set_page_config(
    page_title="Mor-tem · Anteprima desktop",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Il componente vive nella sidebar per non aggiungere un elemento alla griglia
# principale della Full. Sul telefono imposta un layout viewport da 1440 px:
# il browser lo riduce alla larghezza fisica dello schermo e i breakpoint CSS
# desktop scattano come su un vero monitor. Uscendo dalla pagina il meta viewport
# originale viene ripristinato.
with st.sidebar:
    components.html(
        f"""
        <script>
        (() => {{
          const doc = window.parent.document;
          let viewport = doc.querySelector('meta[name="viewport"]');
          if (!viewport) {{
            viewport = doc.createElement('meta');
            viewport.setAttribute('name', 'viewport');
            doc.head.appendChild(viewport);
          }}

          if (!viewport.dataset.mortemDesktopPreviewOriginal) {{
            viewport.dataset.mortemDesktopPreviewOriginal =
              viewport.getAttribute('content') || 'width=device-width, initial-scale=1';
          }}

          viewport.setAttribute(
            'content',
            'width={_DESKTOP_VIEWPORT_WIDTH}, user-scalable=yes'
          );

          const restoreViewport = () => {{
            const original = viewport.dataset.mortemDesktopPreviewOriginal;
            if (original) viewport.setAttribute('content', original);
            delete viewport.dataset.mortemDesktopPreviewOriginal;
          }};

          window.addEventListener('pagehide', restoreViewport, {{ once: true }});
          window.addEventListener('beforeunload', restoreViewport, {{ once: true }});
          window.parent.dispatchEvent(new Event('resize'));
        }})();
        </script>
        """,
        height=1,
        width=1,
    )


source = _MAIN_SCRIPT.read_text(encoding="utf-8")
if source.count(_MAIN_PAGE_CONFIG) != 1:
    st.error(
        "Anteprima desktop non disponibile: la configurazione della pagina Full "
        "è cambiata e il wrapper di sviluppo deve essere aggiornato."
    )
    st.stop()

# La pagina di anteprima ha già eseguito set_page_config; rimuoviamo soltanto
# quella singola chiamata dalla copia in memoria del sorgente Full.
source = source.replace(_MAIN_PAGE_CONFIG, "", 1)

_missing = object()
_previous_device_mode = st.session_state.get(_DEVICE_SESSION_KEY, _missing)
st.session_state[_DEVICE_SESSION_KEY] = False

try:
    exec(
        compile(source, str(_MAIN_SCRIPT), "exec"),
        {
            "__name__": "__main__",
            "__file__": str(_MAIN_SCRIPT),
        },
    )
finally:
    # La forzatura desktop vale solo durante il render di questa pagina e non
    # contamina la Full normale quando si torna alla pagina principale.
    if _previous_device_mode is _missing:
        st.session_state.pop(_DEVICE_SESSION_KEY, None)
    else:
        st.session_state[_DEVICE_SESSION_KEY] = _previous_device_mode
