"""Dedicated FC view, using the reviewed HTML/JS panel as a local component."""

from copy import deepcopy
from math import isfinite
from pathlib import Path
from uuid import uuid4

import streamlit as st
import streamlit.components.v1 as components

from app.fc_selection import apply_choice, validate_choice

TABLES_PAGE = "pages/2_Tabelle di riferimento.py"
FULL_PAGE = "Stima_epoca_decesso.py"
MSIL_PAGE = "pages/App_MSIL.py"
_FRONTEND = Path(__file__).with_name("fc_panel_frontend")
_TOGGLES = ("toggle_fattore", "toggle_fattore_inline", "toggle_fattore_inline_std", "toggle_fattore_inline_mobile")


def _form_snapshot():
    # Trigger/component return values must not be replayed when the form returns.
    # Logical fields and native selectors (including their dates) are retained.
    return deepcopy({key: value for key, value in st.session_state.items()
        if not key.startswith(("__fc_", "mortem_", "btn_", "desktop_caut_fc_"))
        and not key.endswith("_button") and key not in {"back_home", "__next_fc"}})


def _close_flags(values):
    for key in _TOGGLES:
        values[key] = False
    values.pop("__full_fc_suggest_target", None)


def open_fc_page(home=FULL_PAGE):
    st.session_state["__fc_form"] = _form_snapshot()
    st.session_state["__fc_home"] = home
    st.session_state["__fc_active"] = True
    st.session_state["__fc_instance"] = uuid4().hex
    st.session_state.pop("__fc_last_event", None)
    st.rerun()


def _return_to_form():
    saved = st.session_state.get("__fc_form", {})
    _close_flags(saved)
    st.session_state["__fc_resume"] = saved
    st.session_state["__fc_active"] = False
    st.session_state["__fc_tables_return"] = False
    st.rerun()


def _consume_event(event):
    if not isinstance(event, dict) or event.get("instance") != st.session_state.get("__fc_instance"):
        return
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or event_id == st.session_state.get("__fc_last_event"):
        return
    st.session_state["__fc_last_event"] = event_id
    action = event.get("action")
    if action not in {"draft", "back", "tables", "use"}:
        return
    if action == "use":
        try:
            validate_choice(event)
        except (TypeError, ValueError, OverflowError) as exc:
            st.error(str(exc))
            return
    if isinstance(event.get("draft"), dict):
        st.session_state["__fc_draft"] = event["draft"]
    saved = st.session_state.setdefault("__fc_form", {})
    try:
        weight = float(event.get("weight"))
        if isfinite(weight) and 4 <= weight <= 150:
            if saved.get("peso") != weight:
                saved["show_results"] = False
                saved["run_stima_mobile"] = False
            for values in (saved, st.session_state):
                values["peso"] = weight
                values["peso_widget"] = weight
                values["peso_str"] = f"{weight:.1f}"
    except (TypeError, ValueError, OverflowError):
        pass
    if action == "use":
        apply_choice(saved, event, msil=st.session_state.get("__fc_home") == MSIL_PAGE)
        st.session_state["__fc_form"] = saved
        _return_to_form()
    elif action == "back":
        _return_to_form()
    elif action == "tables":
        st.session_state["__fc_tables_return"] = True
        st.switch_page(TABLES_PAGE)


def render_fc_route_if_requested(home=FULL_PAGE):
    """Called before any form widgets: no edits to already-instantiated widgets."""
    resume = st.session_state.pop("__fc_resume", None)
    if isinstance(resume, dict):
        for key, value in resume.items():
            st.session_state[key] = value
        st.session_state.pop("__full_fc_suggest_target", None)
    if not st.session_state.get("__fc_active"):
        if any(st.session_state.get(key, False) for key in _TOGGLES):
            open_fc_page(home)
        return
    # A stable component key retains the browser controls across draft reruns.
    component = components.declare_component("mortem_fc_panel", path=str(_FRONTEND))
    event = component(
        weight=st.session_state.get("peso"),
        draft=st.session_state.get("__fc_draft"),
        instance=st.session_state["__fc_instance"],
        theme_base=st.get_option("theme.base") or "light",
        key="__fc_component_" + st.session_state["__fc_instance"],
        default=None,
    )
    _consume_event(event)
    st.stop()

