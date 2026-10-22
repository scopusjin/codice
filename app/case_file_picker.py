"""One-click file selection; imported cases use the existing JSON validator."""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from app.case_file import CaseFileError, MAX_BYTES, decode_case


def consume_file_event(event, ui_id, state):
    if not isinstance(event, dict) or event.get("instance") != ui_id:
        return None
    event_id = event.get("event_id")
    if (event.get("action") != "open" or not isinstance(event_id, str)
            or not 1 <= len(event_id) <= 100 or event_id == state.get("__case_upload_event")):
        return None
    state["__case_upload_event"] = event_id
    raw = event.get("data")
    if not isinstance(raw, str) or len(raw) > MAX_BYTES:
        raise CaseFileError("File del caso non valido. Dimensione massima: 1 MB.")
    try:
        return decode_case(raw.encode("utf-8"))
    except UnicodeError as exc:
        raise CaseFileError("File del caso non valido.") from exc


def render_case_file_picker(ui_id, key):
    component = components.declare_component(
        "mortem_case_file_picker", path=str(Path(__file__).with_name("case_file_picker_frontend")))
    from app.language import current_language
    event = component(language=current_language(), instance=ui_id, max_bytes=MAX_BYTES, key=key, default=None)
    try:
        return consume_file_event(event, ui_id, st.session_state)
    except CaseFileError as exc:
        st.error(str(exc))
        return None
