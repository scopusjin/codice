# -*- coding: utf-8 -*-
"""UI compatta per la data/ora iniziale dell'ispezione."""

import datetime
import inspect

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
    original_columns = st.columns

    st.markdown(
        """
        <style>
        .st-key-inspection_datetime_row {
            width: 100% !important;
        }

        .st-key-inspection_datetime_row div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 0.4rem !important;
            width: 100% !important;
        }

        .st-key-inspection_datetime_row div[data-testid="stHorizontalBlock"] > div {
            flex: 1 1 0 !important;
            width: 0 !important;
            min-width: 0 !important;
            max-width: none !important;
        }

        .st-key-inspection_datetime_row div[data-baseweb="input"],
        .st-key-inspection_datetime_row input {
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

    def columns_with_compact_inspection_datetime(spec, *args, **kwargs):
        caller = inspect.currentframe().f_back

        # È l'unica st.columns(2) eseguita dopo il toggle iniziale ma prima
        # della creazione degli alias locali input_data_rilievo/input_ora_rilievo.
        is_initial_datetime_row = (
            spec == 2
            and bool(caller and caller.f_locals.get("usa_orario_custom", False))
            and caller is not None
            and "input_data_rilievo" not in caller.f_locals
        )
        if not is_initial_datetime_row:
            return original_columns(spec, *args, **kwargs)

        with st.container(
            horizontal=True,
            horizontal_alignment="left",
            gap="small",
            key="inspection_datetime_row",
        ):
            date_box = st.container(width="stretch", key="inspection_datetime_date")
            time_box = st.container(width="stretch", key="inspection_datetime_time")
        return date_box, time_box

    st.text_input = text_input_with_time_picker
    st.columns = columns_with_compact_inspection_datetime
    st._inspection_datetime_ui_installed = True
