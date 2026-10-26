"""Browser-only case archive; imported data uses the existing case validator."""

from pathlib import Path
from uuid import uuid4

import streamlit as st
import streamlit.components.v1 as components

from app.case_file import CaseFileError, app_version, decode_case


def consume_open_event(event, control):
    if not isinstance(event, dict) or event.get("instance") != control["instance"]:
        return None
    event_id = event.get("event_id")
    if (not isinstance(event_id, str) or not 1 <= len(event_id) <= 100
            or event_id == control.get("last_event") or event.get("action") != "open"):
        return None
    control["last_event"] = event_id
    raw = event.get("data")
    if not isinstance(raw, str):
        raise CaseFileError("Caso salvato nel browser non valido. Nessun dato è stato modificato.")
    return decode_case(raw.encode("utf-8"))


def render_browser_cases(data, *, enabled, mode="all"):
    control = st.session_state.setdefault("__case_browser", {"instance": uuid4().hex})
    component = components.declare_component(
        "mortem_browser_cases", path=str(Path(__file__).with_name("case_browser_frontend")))
    event = component(data=data, enabled=enabled, mode=mode, instance=control["instance"],
                      app_version=app_version(), key="__case_browser_" + control["instance"], default=None)
    try:
        return consume_open_event(event, control)
    except (CaseFileError, UnicodeError) as exc:
        st.error(str(exc) if isinstance(exc, CaseFileError) else "Caso salvato nel browser non valido.")
        return None
