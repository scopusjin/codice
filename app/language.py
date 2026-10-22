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


def render_language_selector():
    import streamlit as st
    st.session_state.setdefault(LANGUAGE_KEY, "it")
    st.session_state.setdefault("mortem_language_widget", st.session_state[LANGUAGE_KEY])

    def change():
        st.session_state[LANGUAGE_KEY] = st.session_state["mortem_language_widget"] or "it"
        # Reports are regenerated below from the same inputs; never export stale prose.
        for key in ("__case_report", "__desc_dettagliate_html", "__word_report_blocks", "frase_breve"):
            st.session_state.pop(key, None)

    with st.container(horizontal=True, horizontal_alignment="right", key="mortem_language_row"):
        st.segmented_control("Lingua / Language", ["it", "en"],
                             format_func=lambda code: "Italiano" if code == "it" else "English",
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
        "Anteprima desktop": "Desktop preview",
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
