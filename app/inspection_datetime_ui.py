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

    # Nell'app il TimePicker iniziale è l'unico componente MUI. Usiamo quindi
    # direttamente le classi MUI, senza dipendere dal wrapper Streamlit, che può
    # cambiare struttura tra desktop e mobile.
    st.markdown(
        """
        <style>
        /* Data/Ora iniziali: la riga che contiene input_data_rilievo non deve
           mai andare a capo, nemmeno sugli schermi stretti. */
        div[data-testid="stHorizontalBlock"]:has(.st-key-input_data_rilievo) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: stretch !important;
            gap: 0.40rem !important;
            width: 100% !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.st-key-input_data_rilievo) > div {
            flex: 1 1 0 !important;
            width: 0 !important;
            min-width: 0 !important;
            max-width: none !important;
        }

        /* Il Box esterno di st-mui aggiunge padding verticale: lo togliamo per
           ottenere la stessa altezza del date_input nativo. */
        .MuiBox-root:has(> .MuiFormControl-root) {
            width: 100% !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        .MuiFormControl-root {
            width: 100% !important;
            min-width: 0 !important;
            margin: 0 !important;
        }

        /* Campo ora: stesso ingombro e stesso sfondo dei widget Streamlit. */
        .MuiPickersInputBase-root,
        .MuiPickersOutlinedInput-root,
        .MuiOutlinedInput-root,
        .MuiInputBase-root {
            box-sizing: border-box !important;
            min-height: 2.50rem !important;
            height: 2.50rem !important;
            background: var(--st-secondary-background-color, #f0f2f6) !important;
            border-radius: 0.50rem !important;
            font-family: inherit !important;
            font-size: inherit !important;
        }

        .MuiPickersInputBase-root input,
        .MuiOutlinedInput-root input,
        .MuiInputBase-root input {
            box-sizing: border-box !important;
            height: 2.50rem !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        .MuiPickersOutlinedInput-notchedOutline,
        .MuiOutlinedInput-notchedOutline,
        .MuiOutlinedInput-root fieldset,
        .MuiPickersInputBase-root fieldset {
            border-color: rgba(49, 51, 63, 0.20) !important;
            border-width: 1px !important;
            border-radius: 0.50rem !important;
        }

        /* Hover, focus e validazione: sempre blu, mai rosso. */
        .MuiPickersInputBase-root:hover .MuiPickersOutlinedInput-notchedOutline,
        .MuiPickersInputBase-root:hover fieldset,
        .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline,
        .MuiOutlinedInput-root:hover fieldset,
        .Mui-focused .MuiPickersOutlinedInput-notchedOutline,
        .Mui-focused .MuiOutlinedInput-notchedOutline,
        .Mui-focused fieldset,
        .Mui-error .MuiPickersOutlinedInput-notchedOutline,
        .Mui-error .MuiOutlinedInput-notchedOutline,
        .Mui-error fieldset {
            border-color: var(--st-primary-color, #168AC1) !important;
            border-width: 1.5px !important;
        }

        .MuiFormHelperText-root.Mui-error {
            color: var(--st-primary-color, #168AC1) !important;
        }

        .MuiSvgIcon-root {
            color: var(--st-primary-color, #168AC1) !important;
        }

        /* Quadrante del picker. */
        .MuiClockPointer-root,
        .MuiClock-pin,
        .MuiClockNumber-root.Mui-selected {
            background-color: var(--st-primary-color, #168AC1) !important;
        }

        .MuiClockPointer-thumb {
            border-color: var(--st-primary-color, #168AC1) !important;
        }

        @media (max-width: 768px) {
            div[data-testid="stHorizontalBlock"]:has(.st-key-input_data_rilievo) {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.st-key-input_data_rilievo) > div {
                flex: 1 1 0 !important;
                width: 0 !important;
                min-width: 0 !important;
                max-width: none !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def text_input_with_clock_picker(label, *args, **kwargs):
        if kwargs.get("key") != "input_ora_rilievo":
            return original_text_input(label, *args, **kwargs)

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
                clearable=False,
                open_to="hours",
                views=("hours", "minutes"),
                format="HH:mm",
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

        value = selected.strftime("%H:%M")
        st.session_state["input_ora_rilievo"] = value
        return value

    st.text_input = text_input_with_clock_picker
    st._inspection_datetime_ui_installed = True
