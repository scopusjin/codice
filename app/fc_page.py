"""Dedicated FC view, using the reviewed HTML/JS panel as a local component."""

from copy import deepcopy
from math import isfinite
from pathlib import Path
from uuid import uuid4

import streamlit as st
import streamlit.components.v1 as components

from app.fc_catalog import load_examples
from app.fc_selection import apply_choice, sync_fc_weight, validate_choice
from app.fc_scenarios import scenario_draft

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
    if st.session_state.get("__full_fc_suggest_target") == "edit":
        st.session_state["__fc_draft"] = _current_fc_draft(st.session_state, home)
    st.session_state["__fc_form"] = _form_snapshot()
    st.session_state["__fc_home"] = home
    st.session_state["__fc_active"] = True
    st.session_state["__fc_instance"] = uuid4().hex
    st.session_state.pop("__fc_last_event", None)
    st.rerun()


def _current_fc_draft(state, home):
    """Open the active FC values, retaining their original weight-adaptation base."""
    if home == MSIL_PAGE:
        values = [state.get("FC_min_beta"), state.get("FC_max_beta")]
    elif state.get("stima_cautelativa_beta") and state.get("range_unico_beta"):
        values = [state.get("fc_min_val"), state.get("fc_other_val")]
    else:
        values = [state.get("fattore_correzione")] * 2
    choice = state.get("__fc_applied_choice") or {}
    matches = choice.get("range") == values and choice.get("weight") == state.get("peso")
    if matches and choice.get("scenarios"):
        return scenario_draft(choice)
    base = choice.get("base_range") if matches else None
    manual = choice.get("manual", True) if base is not None else True
    draft = deepcopy(choice.get("draft") or state.get("__fc_draft") or {})
    if choice.get("scenarios"):
        draft.pop("multiple", None)
        draft.pop("scenarios", None)
    draft.update(
        lo="" if values[0] is None else f"{values[0]:.2f}",
        hi="" if values[1] is None else f"{values[1]:.2f}",
        weight=state.get("peso"), manual=manual,
        manualBase=(base if base is not None else values) if manual else None,
        selectedBase=base if not manual else None,
        manualWeightAdjusted=bool(matches and choice.get("manual_weight_adjusted")),
        weightAdjusted=bool(matches and choice.get("weight_adjusted", choice.get("manual_weight_adjusted", False))),
    )
    return draft


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
            # A chosen FC updates the saved form through apply_choice below.
            if action != "use":
                sync_fc_weight(saved, weight)
            sync_fc_weight(st.session_state, weight)
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
        examples=load_examples(),
        weight=st.session_state.get("peso"),
        draft=st.session_state.get("__fc_draft"),
        instance=st.session_state["__fc_instance"],
        theme_base=st.get_option("theme.base") or "light",
        key="__fc_component_" + st.session_state["__fc_instance"],
        default=None,
    )
    _consume_event(event)
    st.stop()

