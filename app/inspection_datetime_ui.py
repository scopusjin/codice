# -*- coding: utf-8 -*-
"""UI compatta per la data/ora iniziale dell'ispezione."""

import streamlit as st

from app.native_time_picker import native_time_picker


_PICKER_KEY = "input_ora_rilievo_native"
_ROW_PENDING_ATTR = "_inspection_datetime_row_pending"


def install_inspection_datetime_ui():
    """Usa il picker orario nativo e mantiene Data/Ora affiancate su mobile."""
    if getattr(st, "_inspection_datetime_ui_installed", False):
        return

    original_toggle = st.toggle
    original_columns = st.columns
    original_text_input = st.text_input

    st.markdown(
        """
        <style>
        /* Solo la coppia Data/Ora iniziale: due metà fisse anche su mobile. */
        .st-key-inspection_datetime_row div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
            gap: 0.40rem !important;
            width: 100% !important;
        }

        .st-key-inspection_datetime_row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            width: 100% !important;
            min-width: 0 !important;
            max-width: none !important;
            flex: none !important;
        }

        .st-key-inspection_datetime_row [data-testid="stDateInput"],
        .st-key-inspection_datetime_row [data-testid="stCustomComponentV1"] {
            width: 100% !important;
            min-width: 0 !important;
        }

        .st-key-inspection_datetime_row iframe {
            width: 100% !important;
            min-width: 0 !important;
            height: 40px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def toggle_with_datetime_marker(label, *args, **kwargs):
        result = original_toggle(label, *args, **kwargs)
        if kwargs.get("key") == "usa_orario_custom":
            setattr(st, _ROW_PENDING_ATTR, bool(result))
        return result

    def columns_with_datetime_row(spec, *args, **kwargs):
        if getattr(st, _ROW_PENDING_ATTR, False):
            setattr(st, _ROW_PENDING_ATTR, False)
            if spec == 2:
                # Crea un'ancora CSS esclusiva per questa sola coppia di colonne.
                with st.container(key="inspection_datetime_row"):
                    return original_columns(spec, *args, **kwargs)
        return original_columns(spec, *args, **kwargs)

    def text_input_with_native_time(label, *args, **kwargs):
        if kwargs.get("key") != "input_ora_rilievo":
            return original_text_input(label, *args, **kwargs)

        value = st.session_state.get("input_ora_rilievo")
        if not isinstance(value, str) or len(value) != 5:
            value = kwargs.get("value") if isinstance(kwargs.get("value"), str) else "00:00"

        selected = native_time_picker(value, key=_PICKER_KEY)
        st.session_state["input_ora_rilievo"] = selected
        return selected

    st.toggle = toggle_with_datetime_marker
    st.columns = columns_with_datetime_row
    st.text_input = text_input_with_native_time
    st._inspection_datetime_ui_installed = True
