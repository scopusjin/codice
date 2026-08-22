# -*- coding: utf-8 -*-
"""UI compatta per data/ora dei parametri tanatologici speciali.

Mantiene invariata la logica esistente: quando l'orario globale dei rilievi è
attivo, ogni parametro valutato usa direttamente data e ora modificabili.
La vecchia checkbox "valutato a un'ora diversa" viene resa implicita.
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


def _spec_values(spec):
    if isinstance(spec, int):
        return None
    try:
        return tuple(float(value) for value in spec)
    except (TypeError, ValueError):
        return None


def install_special_datetime_ui():
    """Elimina il click intermedio e mantiene Data/Ora affiancate anche su mobile."""
    if getattr(st, "_special_datetime_ui_installed", False):
        return

    original_checkbox = st.checkbox
    original_markdown = st.markdown
    original_columns = st.columns

    # Le due celle native restano in una sola riga e possono restringersi.
    original_markdown(
        """
        <style>
        [class*="st-key-special_datetime_row_"] {
            width: 100% !important;
            margin-top: 0 !important;
            margin-bottom: 0.18rem !important;
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
        }

        [class*="st-key-special_datetime_row_"] div[data-baseweb="input"],
        [class*="st-key-special_datetime_row_"] input {
            min-width: 0 !important;
            width: 100% !important;
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
            # La data/ora visibile è già il controllo: nessuna conferma aggiuntiva.
            st.session_state[key] = True
            return True

        return original_checkbox(label, *args, **kwargs)

    def markdown_without_datetime_prompts(body, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None

        if parametro_id in _SPECIAL_PARAM_IDS and isinstance(body, str):
            # Sopprime la vecchia riga arancione "valutato a un'ora diversa".
            if caller.f_locals.get("chiave_checkbox") and "color: orange" in body:
                return None

            # I campi sono autoesplicativi e compatti: niente riga-label separata.
            measurement_date = caller.f_locals.get("measurement_date")
            measurement_time = caller.f_locals.get("measurement_time")
            if isinstance(measurement_date, str) and measurement_date and measurement_date in body:
                return None
            if isinstance(measurement_time, str) and measurement_time and measurement_time in body:
                return None

        return original_markdown(body, *args, **kwargs)

    def columns_with_compact_datetime(spec, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None

        if parametro_id in _SPECIAL_PARAM_IDS:
            values = _spec_values(spec)

            # La vecchia riga testo + checkbox diventa completamente vuota.
            if (
                values == (0.75, 0.25)
                and caller.f_locals.get("chiave_checkbox")
                and bool(caller.f_locals.get("usa_orario_custom_globale", False))
            ):
                return st.empty(), st.empty()

            # Questa è esclusivamente la riga Data | Ora del singolo parametro.
            if (
                spec == 2
                and bool(caller.f_locals.get("usa_orario_custom_globale", False))
                and bool(caller.f_locals.get("usa_orario_personalizzato", False))
            ):
                # Passiamo prima dal wrapper columns già installato, così i due
                # parametri elettrici restano nella rispettiva metà della coppia.
                staging, _ = original_columns([1000, 1], gap="small")
                with staging:
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

        return original_columns(spec, *args, **kwargs)

    st.checkbox = checkbox_without_different_time
    st.markdown = markdown_without_datetime_prompts
    st.columns = columns_with_compact_datetime
    st._special_datetime_ui_installed = True
