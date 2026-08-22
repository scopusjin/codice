# -*- coding: utf-8 -*-
"""UI compatta per data/ora dei parametri tanatologici speciali.

La vecchia conferma "valutato a un'ora diversa" viene resa implicita.
Data e ora restano i widget originali, ma vengono mostrati direttamente
su una sola riga compatta anche su schermi stretti.
"""

import inspect

import streamlit as st

from app.special_tanatology_states import (
    PARAM_CHEMICAL_PUPILLARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_MECHANICAL_MUSCLE,
)


_SPECIAL_PARAM_IDS = {
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_MECHANICAL_MUSCLE,
    PARAM_CHEMICAL_PUPILLARY,
}

_ELECTRICAL_PARAM_IDS = {
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_ELECTRICAL_PERIORAL,
}


class _NoopContext:
    """Context manager che non crea alcun elemento Streamlit."""

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def _spec_values(spec):
    if isinstance(spec, int):
        return None
    try:
        return tuple(float(value) for value in spec)
    except (TypeError, ValueError):
        return None


def install_special_datetime_ui():
    """Mostra direttamente Data | Ora senza righe o conferme intermedie."""
    if getattr(st, "_special_datetime_ui_installed", False):
        return

    original_checkbox = st.checkbox
    original_markdown = st.markdown
    original_columns = st.columns

    original_markdown(
        """
        <style>
        [class*="st-key-special_datetime_row_"] {
            width: 100% !important;
            margin-top: 0.10rem !important;
            margin-bottom: 0.20rem !important;
        }

        [class*="st-key-special_datetime_row_"] div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 0.35rem !important;
            width: 100% !important;
        }

        [class*="st-key-special_datetime_row_"] div[data-testid="stHorizontalBlock"] > div {
            flex: 1 1 0 !important;
            width: 0 !important;
            min-width: 0 !important;
            max-width: none !important;
        }

        [class*="st-key-special_datetime_row_"] div[data-baseweb="input"],
        [class*="st-key-special_datetime_row_"] input {
            width: 100% !important;
            min-width: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def checkbox_without_different_time(label, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None
        chiave_checkbox = caller.f_locals.get("chiave_checkbox") if caller else None
        key = kwargs.get("key")

        if (
            parametro_id in _SPECIAL_PARAM_IDS
            and isinstance(key, str)
            and key == chiave_checkbox
            and bool(caller.f_locals.get("usa_orario_custom_globale", False))
        ):
            st.session_state[key] = True
            return True

        return original_checkbox(label, *args, **kwargs)

    def markdown_without_datetime_labels(body, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None

        if parametro_id in _SPECIAL_PARAM_IDS and isinstance(body, str):
            # Vecchia frase arancione: soppressa esattamente, senza toccare altri markdown.
            if body.startswith(
                "<div style='font-size: 0.8em; color: orange; margin-bottom: 3px;'>"
            ):
                return None

            # Le etichette Data/Ora sopra i campi non servono più: i due widget
            # sono affiancati e mantengono comunque il proprio label accessibile.
            prefix = "<div style='font-size: 0.88rem; padding-top: 0.4rem;'>"
            measurement_date = caller.f_locals.get("measurement_date")
            measurement_time = caller.f_locals.get("measurement_time")
            if isinstance(measurement_date, str) and body == f"{prefix}{measurement_date}</div>":
                return None
            if isinstance(measurement_time, str) and body == f"{prefix}{measurement_time}</div>":
                return None

        return original_markdown(body, *args, **kwargs)

    def _datetime_boxes(parametro_id):
        with st.container(
            horizontal=True,
            horizontal_alignment="left",
            gap="small",
            key=f"special_datetime_row_{parametro_id}",
        ):
            date_box = st.container(
                width="stretch",
                key=f"special_datetime_date_{parametro_id}",
            )
            time_box = st.container(
                width="stretch",
                key=f"special_datetime_time_{parametro_id}",
            )
        return date_box, time_box

    def columns_with_compact_datetime(spec, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None

        if parametro_id in _SPECIAL_PARAM_IDS:
            values = _spec_values(spec)

            # Elimina fisicamente la vecchia riga testo + checkbox.
            if (
                values == (0.75, 0.25)
                and caller.f_locals.get("chiave_checkbox")
                and bool(caller.f_locals.get("usa_orario_custom_globale", False))
            ):
                return _NoopContext(), _NoopContext()

            # Sostituisce solo la riga Data/Ora del singolo parametro.
            if (
                spec == 2
                and bool(caller.f_locals.get("usa_orario_custom_globale", False))
                and bool(caller.f_locals.get("usa_orario_personalizzato", False))
            ):
                if parametro_id in _ELECTRICAL_PARAM_IDS:
                    # original_columns è il layout elettrico già installato: questa
                    # chiamata crea l'ancora dentro la metà corretta della coppia.
                    anchor, _ = original_columns([1000, 1], gap="small")
                    with anchor:
                        return _datetime_boxes(parametro_id)

                return _datetime_boxes(parametro_id)

        return original_columns(spec, *args, **kwargs)

    st.checkbox = checkbox_without_different_time
    st.markdown = markdown_without_datetime_labels
    st.columns = columns_with_compact_datetime
    st._special_datetime_ui_installed = True
