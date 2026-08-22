# -*- coding: utf-8 -*-
"""UI semplificata per data/ora dei parametri tanatologici speciali.

Quando la data/ora globale dei rilievi è attiva, la vecchia conferma
"valutato a un'ora diversa" viene resa implicita. I normali widget Data/Ora
del file principale restano invece intatti, così non interferiamo con layout,
titoli o renderer delle eccitabilità elettriche.
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


def install_special_datetime_ui():
    """Elimina soltanto la conferma intermedia prima dei campi Data/Ora."""
    if getattr(st, "_special_datetime_ui_installed", False):
        return

    original_checkbox = st.checkbox

    # Nasconde esclusivamente il vecchio testo arancione che accompagnava
    # la checkbox ora resa implicita. Non sostituiamo st.markdown.
    st.markdown(
        """
        <style>
        div[style*="font-size: 0.8em"][style*="color: orange"] {
            display: none !important;
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
            # I campi Data/Ora diventano direttamente disponibili e sono
            # inizializzati dal codice originale con data/ora dell'ispezione.
            st.session_state[key] = True
            return True

        return original_checkbox(label, *args, **kwargs)

    st.checkbox = checkbox_without_different_time
    st._special_datetime_ui_installed = True
