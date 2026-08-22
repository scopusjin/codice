# -*- coding: utf-8 -*-
"""UI compatta per la data/ora iniziale dell'ispezione."""

import datetime

import streamlit as st


_PICKER_KEY = "input_ora_rilievo_picker"


def _parse_time(value):
    """Converte il valore storico HH:MM nel tipo richiesto da st.time_input."""
    if isinstance(value, datetime.time):
        return value.replace(second=0, microsecond=0)
    if isinstance(value, str):
        try:
            return datetime.datetime.strptime(value.strip(), "%H:%M").time()
        except ValueError:
            pass
    return datetime.time(0, 0)


def install_inspection_datetime_ui():
    """Usa un time picker e mantiene Data/Ora sulla stessa riga anche su mobile."""
    if getattr(st, "_inspection_datetime_ui_installed", False):
        return

    original_text_input = st.text_input

    # La riga Data/Ora resta quella nativa del file principale. Il CSS agisce
    # solo sull'HorizontalBlock che contiene il widget con key input_data_rilievo,
    # quindi non modifica nessun'altra st.columns dell'app.
    st.markdown(
        """
        <style>
        div[data-testid="stHorizontalBlock"]:has(.st-key-input_data_rilievo) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 0.4rem !important;
            width: 100% !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.st-key-input_data_rilievo) > div {
            flex: 1 1 0 !important;
            width: 0 !important;
            min-width: 0 !important;
            max-width: none !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.st-key-input_data_rilievo) div[data-baseweb="input"],
        div[data-testid="stHorizontalBlock"]:has(.st-key-input_data_rilievo) input {
            width: 100% !important;
            min-width: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def text_input_with_time_picker(label, *args, **kwargs):
        if kwargs.get("key") != "input_ora_rilievo":
            return original_text_input(label, *args, **kwargs)

        source = st.session_state.get("input_ora_rilievo")
        desired = _parse_time(source)

        current = st.session_state.get(_PICKER_KEY)
        if isinstance(current, datetime.time):
            current = current.replace(second=0, microsecond=0)
        if current != desired:
            st.session_state[_PICKER_KEY] = desired

        selected = st.time_input(
            label,
            value=desired,
            step=datetime.timedelta(minutes=5),
            key=_PICKER_KEY,
            label_visibility=kwargs.get("label_visibility", "visible"),
            width="stretch",
        )
        value = selected.strftime("%H:%M")
        st.session_state["input_ora_rilievo"] = value
        return value

    st.text_input = text_input_with_time_picker
    st._inspection_datetime_ui_installed = True
