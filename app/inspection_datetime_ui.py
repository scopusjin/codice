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

    # st-mui usa Components v2 senza isolamento CSS: possiamo quindi uniformare
    # il solo picker iniziale ai widget Streamlit e, contemporaneamente, impedire
    # che le due colonne Data/Ora vadano a capo sugli schermi stretti.
    st.markdown(
        """
        <style>
        /* Riga iniziale Data/Ora: contiene insieme il date_input nativo e il
           TimePicker MUI. Questo selettore non intercetta gli altri st.columns. */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: stretch !important;
            gap: 0.40rem !important;
            width: 100% !important;
        }

        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        > div[data-testid="stColumn"] {
            flex: 1 1 calc(50% - 0.20rem) !important;
            width: calc(50% - 0.20rem) !important;
            min-width: 0 !important;
            max-width: calc(50% - 0.20rem) !important;
        }

        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        [data-testid="stCustomComponentV2"],
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        .MuiFormControl-root {
            width: 100% !important;
            min-width: 0 !important;
            margin: 0 !important;
        }

        /* st-mui aggiunge 0.5 di padding verticale al suo Box. Lo azzeriamo
           soltanto nella riga iniziale per ottenere la stessa altezza della data. */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        .MuiBox-root:has(> .MuiFormControl-root) {
            width: 100% !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        /* Aspetto coerente con i widget Streamlit. */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        [class*="MuiPickersInputBase-root"],
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        [class*="MuiOutlinedInput-root"] {
            box-sizing: border-box !important;
            min-height: 2.5rem !important;
            height: 2.5rem !important;
            background: var(--st-secondary-background-color, #f0f2f6) !important;
            border-radius: 0.5rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        [class*="MuiPickersOutlinedInput-notchedOutline"],
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        .MuiOutlinedInput-notchedOutline {
            border-color: rgba(49, 51, 63, 0.20) !important;
            border-width: 1px !important;
        }

        /* Hover, focus ed eventuale stato di validazione restano sempre blu. */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        [class*="MuiPickersInputBase-root"]:hover [class*="notchedOutline"],
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        [class*="MuiOutlinedInput-root"]:hover .MuiOutlinedInput-notchedOutline,
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        .Mui-focused [class*="notchedOutline"],
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        .Mui-focused .MuiOutlinedInput-notchedOutline,
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        .Mui-error [class*="notchedOutline"],
        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        .Mui-error .MuiOutlinedInput-notchedOutline {
            border-color: var(--st-primary-color, #168AC1) !important;
            border-width: 1.5px !important;
        }

        div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
        .MuiSvgIcon-root {
            color: var(--st-primary-color, #168AC1) !important;
        }

        /* Il quadrante mantiene gli stessi toni blu del resto dell'interfaccia. */
        .MuiClockPointer-root,
        .MuiClock-pin,
        .MuiClockNumber-root.Mui-selected {
            background-color: var(--st-primary-color, #168AC1) !important;
        }

        .MuiClockPointer-thumb {
            border-color: var(--st-primary-color, #168AC1) !important;
        }

        @media (max-width: 768px) {
            div[data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]):has(.MuiFormControl-root)
            > div[data-testid="stColumn"] {
                flex: 1 1 calc(50% - 0.20rem) !important;
                width: calc(50% - 0.20rem) !important;
                min-width: 0 !important;
                max-width: calc(50% - 0.20rem) !important;
            }
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
