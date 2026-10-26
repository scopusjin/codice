"""Session language; calculation inputs and legacy option values stay unchanged."""

from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache, wraps
import inspect
import json

LANGUAGE_KEY = "mortem_language"
_override = ContextVar("mortem_language_override", default=None)


def current_language():
    if _override.get() is not None:
        return _override.get()
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    if get_script_run_ctx(suppress_warning=True) is None:
        return "it"
    import streamlit as st
    return "en" if st.session_state.get(LANGUAGE_KEY) == "en" else "it"


@contextmanager
def using_language(language):
    """Execution-local override for report rendering and regression checks."""
    if language not in ("it", "en"):
        raise ValueError(language)
    token = _override.set(language)
    try:
        yield
    finally:
        _override.reset(token)


class _PresentationLocale:
    @lru_cache(maxsize=None)
    def __getattr__(self, name):
        from app import i18n
        function = getattr(i18n, name)
        if not callable(function) or "language" not in inspect.signature(function).parameters:
            return function
        signature = inspect.signature(function)

        @wraps(function)
        def render(*args, **kwargs):
            bound = signature.bind_partial(*args, **kwargs)
            if bound.arguments.get("language") is None:
                bound.arguments["language"] = current_language()
            return function(*bound.args, **bound.kwargs)
        return render


presentation_i18n = _PresentationLocale()


@lru_cache(maxsize=2)
def _language_option_label(code):
    """Embedded flags avoid platform-dependent emoji rendering."""
    from base64 import b64encode
    if code == "it":
        drawing = '<path fill="#009246" d="M0 0h10v20H0z"/><path fill="#fff" d="M10 0h10v20H10z"/><path fill="#ce2b37" d="M20 0h10v20H20z"/>'
    else:
        drawing = ('<path fill="#012169" d="M0 0h30v20H0z"/>'
                   '<path stroke="#fff" stroke-width="4" d="m0 0 30 20M30 0 0 20"/>'
                   '<path stroke="#c8102e" stroke-width="1.5" d="m0 0 30 20M30 0 0 20"/>'
                   '<path stroke="#fff" stroke-width="7" d="M15 0v20M0 10h30"/>'
                   '<path stroke="#c8102e" stroke-width="4" d="M15 0v20M0 10h30"/>')
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="20" viewBox="0 0 30 20">' + drawing + '</svg>'
    uri = "data:image/svg+xml;base64," + b64encode(svg.encode()).decode()
    name = "Italia" if code == "it" else "United Kingdom"
    return f"![{name}]({uri}) {code.upper()}"


def render_language_selector():
    import streamlit as st
    st.session_state.setdefault(LANGUAGE_KEY, "it")
    st.session_state.setdefault("mortem_language_widget", st.session_state[LANGUAGE_KEY])

    def change():
        st.session_state[LANGUAGE_KEY] = st.session_state["mortem_language_widget"] or "it"
        # Reports are regenerated below from the same inputs; never export stale prose.
        for key in ("__case_report", "__desc_dettagliate_html", "__word_report_blocks", "frase_breve"):
            st.session_state.pop(key, None)

    st.html("""<style>
      .st-key-mortem_language_row button {
        min-height: 1.55rem !important;
        padding: 0.1rem 0.4rem !important;
      }
      .st-key-mortem_language_row button,
      .st-key-mortem_language_row button p {
        font-size: 0.72rem !important;
        line-height: 1.15 !important;
      }
      .st-key-mortem_language_row button {
        background: transparent !important;
        color: #64748b !important;
        border-color: #d8dee5 !important;
        box-shadow: none !important;
      }
      .st-key-mortem_language_row button[aria-pressed="true"],
      .st-key-mortem_language_row button[aria-checked="true"],
      .st-key-mortem_language_row button[data-testid="stBaseButton-segmented_controlActive"] {
        background: #eef1f4 !important;
        color: #334155 !important;
        border-color: #b8c2cc !important;
      }
      .st-key-mortem_language_row button img {
        width: 1.1rem;
        height: 0.75rem;
        object-fit: contain;
      }
    </style>""")
    # Ordinary page footer: scrolls with the content, without a pinned overlay.
    with st.container(horizontal=True, horizontal_alignment="right", gap=None,
                      key="mortem_language_row"):
        st.segmented_control("Lingua / Language", ["it", "en"],
                             format_func=_language_option_label,
                             selection_mode="single", key="mortem_language_widget",
                             on_change=change, label_visibility="collapsed", width="content")
    _translate_navigation()


def _translate_navigation():
    """Native multipage navigation is emitted before page rendering.

    Localise only its visible link text; hrefs and page identity remain intact.
    """
    import streamlit as st
    names = {
        "Stima epoca decesso": "Time since death estimation",
        "App MSIL": "Scene examination",
        "Tabelle di riferimento": "Reference tables",
        "Impostazioni": "Settings",
        "Reference": "References",
    }
    script = """<script>(() => {
      const names = __NAMES__, english = __ENGLISH__;
      window.__mortemNavigationObserver?.disconnect();
      const update = () => {
        for (const node of document.querySelectorAll('[data-testid="stSidebarNavLink"] span')) {
          const source = node.dataset.mortemNavLabel || node.textContent.trim();
          if (!Object.hasOwn(names, source)) continue;
          node.dataset.mortemNavLabel = source;
          const label = english ? names[source] : source;
          if (node.textContent !== label) node.textContent = label;
        }
      };
      update();
      window.__mortemNavigationObserver = new MutationObserver(update);
      window.__mortemNavigationObserver.observe(document.body, {childList:true, subtree:true, characterData:true});
    })();</script>"""
    st.html(script.replace("__NAMES__", json.dumps(names)).replace("__ENGLISH__", json.dumps(current_language() == "en")),
            unsafe_allow_javascript=True)
