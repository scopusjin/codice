"""Small case menu shared by Full and Sopralluogo."""

from copy import deepcopy
from uuid import uuid4

import streamlit as st

from app.case_file import (
    CaseFileError, PAGES, app_version, case_filename, decode_case, encode_case,
    restored_inputs, snapshot_case,
)
from app.livor_digitopressione import PRESSURE_VISIBILITY_KEY


def _queue_import(case, ui_id):
    # The actual replacement happens at the start of the next script run,
    # before any of the case's widgets have been instantiated.
    if ui_id == st.session_state.get("__case_ui_id", ""):
        st.session_state["__case_pending_import"] = case


def _store_case_code(widget_key, ui_id):
    # Keep the identifier independent of widget cleanup when changing views.
    if ui_id != st.session_state.get("__case_ui_id", "") or widget_key not in st.session_state:
        return
    st.session_state["case_code"] = st.session_state[widget_key]
    if st.session_state.get("__fc_active"):
        st.session_state.setdefault("__fc_form", {})["case_code"] = st.session_state["case_code"]


def prepare_case_import(home):
    pending = st.session_state.pop("__case_pending_import", None)
    if pending is None:
        return
    try:
        values = restored_inputs(pending)
    except CaseFileError as exc:
        st.error(str(exc))
        return
    word_link = st.session_state.pop("__word_launch_pending", None) or st.session_state.get("__word_return")
    if word_link and word_link.get("case_code") != pending["case_code"]:
        word_link = None
    # Keep the receiving device's layout, never the exporting device's layout.
    mobile = st.session_state.get("__full_device_mobile")
    # Le preferenze di visualizzazione appartengono alla sessione, non al caso.
    ui_preferences = {
        key: st.session_state[key]
        for key in (PRESSURE_VISIBILITY_KEY,)
        if key in st.session_state
    }
    # A fresh numeric sync token also updates already mounted custom controls.
    sync = {k: int(v) + 1 for k, v in st.session_state.items()
            if k.startswith("__decimal_component_sync_") and type(v) is int}
    for key in list(st.session_state):
        del st.session_state[key]
    st.session_state.update(values)
    if word_link:
        st.session_state["__word_return"] = word_link
    st.session_state.update(sync)
    st.session_state.update(ui_preferences)
    # Fresh menu controls prevent a late update from the old case (including
    # an empty identifier) from overwriting the case that has just been loaded.
    st.session_state["__case_ui_id"] = uuid4().hex
    if mobile is not None:
        st.session_state["__full_device_mobile"] = mobile
    if pending["editor_open"]:
        st.session_state["__fc_form"] = deepcopy({k: v for k, v in values.items() if not k.startswith("__fc_")})
        st.session_state["__fc_active"] = True
        st.session_state["__fc_home"] = PAGES[pending["view"]]
        st.session_state["__fc_instance"] = uuid4().hex
    st.session_state["__case_loaded_notice"] = True
    if home != PAGES[pending["view"]]:
        st.switch_page(PAGES[pending["view"]])


def _close_case_dialog():
    st.session_state["__case_dialog_open"] = False


@st.dialog("Caso", width="small", on_dismiss=_close_case_dialog)
def _case_dialog(view, suffix):
    def widget_key(name):
        return name + ("_" + suffix if suffix else "")

    code_key = widget_key("__case_code_input")
    if code_key not in st.session_state:
        st.session_state[code_key] = st.session_state.get("case_code", "")
    st.text_input("Sigla / numero del caso", key=code_key, max_chars=80,
                  placeholder="Es. x26-05 oppure IL26-10", on_change=_store_case_code,
                  args=(code_key, suffix))
    mode = st.segmented_control("Operazione", ["Scarica", "Carica"], default="Scarica",
                                key=widget_key("__case_dialog_mode"),
                                selection_mode="single", label_visibility="collapsed")
    data = None
    try:
        case = snapshot_case(st.session_state, view)
        data = encode_case(case)
    except CaseFileError as exc:
        st.error(str(exc))
    if mode != "Carica":
        if data is not None:
            if case.get("report") is None:
                st.caption("Per includere le descrizioni, esegui la stima con i dati attuali prima di salvare.")
            st.download_button("Scarica JSON", data, file_name=case_filename(case),
                               mime="application/json", key=widget_key("case_download"),
                               on_click="ignore", icon=":material/download:")
    else:
        uploaded = st.file_uploader("File del caso", type=["json"], max_upload_size=1,
                                    key=widget_key("case_upload"), label_visibility="collapsed")
        if uploaded is not None:
            try:
                imported = decode_case(uploaded.getvalue())
            except CaseFileError as exc:
                st.error(str(exc))
            else:
                name = imported["case_code"] or "Senza sigla"
                saved_mode = "Completa" if imported["view"] == "full" else "Sopralluogo"
                st.text(f"{name} · {saved_mode}")
                if imported["app_version"] != app_version():
                    st.caption("File salvato con una versione diversa dell’app: verificare la stima ricalcolata.")
                st.caption("L’apertura sostituisce i dati attuali. Il file originale resta invariato.")
                if st.button("Sostituisci e apri", key=widget_key("case_open")):
                    _queue_import(imported, suffix)
                    st.rerun()


def render_case_menu(home, slot=None):
    view = next(name for name, page in PAGES.items() if page == home)
    suffix = st.session_state.get("__case_ui_id", "")
    menu_key = "case_menu" + ("_" + suffix if suffix else "")
    target = slot.container() if slot is not None else st.container()
    with target:
        with st.container(horizontal=True, horizontal_alignment="right", gap="xsmall", key="case_menu_row"):
            if code := st.session_state.get("case_code", ""):
                st.text(code, width="content")
            if st.button("Caso", icon=":material/folder_open:", width="content", key=menu_key):
                st.session_state["__case_dialog_open"] = True
            if st.session_state.get("__case_dialog_open", False):
                _case_dialog(view, suffix)
        if st.session_state.pop("__case_loaded_notice", False):
            st.toast("Caso caricato. I risultati saranno ricalcolati con Procedi con la stima.")
