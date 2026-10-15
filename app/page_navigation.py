"""History of internal pages, excluding reruns and transient FC editor frames.

The navigation stack is session-only and never part of a saved case.
"""

FULL_PAGE = "Stima_epoca_decesso.py"
MSIL_PAGE = "pages/App_MSIL.py"
TABLES_PAGE = "pages/2_Tabelle di riferimento.py"
REFERENCES_PAGE = "pages/9_Reference.py"
SETTINGS_PAGE = "pages/Impostazioni.py"
FC_VIEW = "__fc_editor_view__"

_HISTORY_KEY = "mortem_page_history"
_KNOWN_VIEWS = frozenset((
    FULL_PAGE, MSIL_PAGE, TABLES_PAGE, REFERENCES_PAGE, SETTINGS_PAGE, FC_VIEW,
))


def _history(state):
    stored = state.get(_HISTORY_KEY)
    if not isinstance(stored, list):
        return []
    return [view for view in stored if isinstance(view, str) and view in _KNOWN_VIEWS][-20:]


def record_page_visit(state, view):
    """Register a navigation, never a Streamlit widget rerun."""
    if view not in _KNOWN_VIEWS:
        raise ValueError("Pagina non riconosciuta.")
    history = _history(state)
    if not state.get("__fc_active") and history and history[-1] == FC_VIEW:
        # The FC editor was closed: returning to the form is not a new page.
        history.pop()
    if not history or history[-1] != view:
        history.append(view)
    state[_HISTORY_KEY] = history[-20:]


def previous_view(state, current):
    """Return the actual previous view, not a stale FC flag."""
    history = _history(state)
    if not history or history[-1] != current:
        return None
    for view in reversed(history[:-1]):
        if view == FC_VIEW and not state.get("__fc_active"):
            continue
        if view != current:
            return view
    return None


def back_label(state, current):
    return "← Indietro al FC" if previous_view(state, current) == FC_VIEW else "← Indietro"


def go_back(state, current):
    """Consume one history step and return a valid Streamlit page path."""
    target = previous_view(state, current)
    history = _history(state)
    if history and history[-1] == current:
        history.pop()
    if target is None:
        target = FULL_PAGE
        history = [FULL_PAGE]
    else:
        while history and history[-1] != target:
            history.pop()
    state[_HISTORY_KEY] = history[-20:]
    if target == FC_VIEW:
        home = state.get("__fc_home")
        return home if home in (FULL_PAGE, MSIL_PAGE) else FULL_PAGE
    return target


def render_back_button(current, *, key="back_home"):
    """Render one back control with a label based on actual provenance."""
    import streamlit as st
    if st.button(back_label(st.session_state, current), key=key):
        st.switch_page(go_back(st.session_state, current))
