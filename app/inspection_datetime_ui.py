# -*- coding: utf-8 -*-
"""UI compatta per la data/ora iniziale dell'ispezione."""

import datetime

import streamlit as st


_PICKER_KEY = "input_ora_rilievo_clock"


def _parse_time(value):
    """Converte il valore storico HH:MM nel tipo datetime.time."""
    if isinstance(value, datetime.time):
        return value.replace(second=0, microsecond=0)
    if isinstance(value, str):
        try:
            return datetime.datetime.strptime(value.strip(), "%H:%M").time()
        except ValueError:
            pass
    return datetime.time(0, 0)


def install_inspection_datetime_ui():
    """Usa un vero clock picker e mantiene Data/Ora sulla stessa riga su mobile."""
    if getattr(st, "_inspection_datetime_ui_installed", False):
        return

    original_text_input = st.text_input

    # Mantiene soltanto la riga iniziale Data/Ora affiancata. Il selettore
    # :has() è limitato all'HorizontalBlock che contiene input_data_rilievo e
    # non modifica le altre st.columns dell'app.
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

    def text_input_with_clock_picker(label, *args, **kwargs):
        if kwargs.get("key") != "input_ora_rilievo":
            return original_text_input(label, *args, **kwargs)

        # Import locale: se durante un deploy la nuova dipendenza non fosse
        # ancora disponibile, l'app continua a funzionare con il widget nativo.
        try:
            from st_mui import time_picker as mui_time_picker
        except ImportError:
            mui_time_picker = None

        desired = _parse_time(st.session_state.get("input_ora_rilievo"))

        if mui_time_picker is not None:
            selected = mui_time_picker(
                label="",
                value=desired,
                ampm=False,
                key=_PICKER_KEY,
            )
        else:
            selected = st.time_input(
                label,
                value=desired,
                format="24h",
                key=_PICKER_KEY,
                label_visibility=kwargs.get("label_visibility", "visible"),
                width="stretch",
            )

        if selected is None:
            selected = desired
        if isinstance(selected, str):
            selected = _parse_time(selected)

        # Il valore legacy viene aggiornato dal valore restituito dal picker;
        # non riscriviamo mai lo stato del picker prima del render, evitando il
        # precedente ritorno automatico a 00:00 al blur/rerun.
        value = selected.strftime("%H:%M")
        st.session_state["input_ora_rilievo"] = value
        return value

    st.text_input = text_input_with_clock_picker
    st._inspection_datetime_ui_installed = True
