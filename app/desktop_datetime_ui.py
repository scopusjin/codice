# -*- coding: utf-8 -*-
"""Adatta al desktop il sistema data/ora compatto della schermata Full.

Il renderer mobile già collaudato resta invariato. Sul desktop vengono riusati
soltanto i passaggi relativi ai parametri tanatologici speciali: titolo/helper
restano nella colonna desktop esistente, mentre il solo orario viene collocato
accanto al titolo e la data viene dedotta rispetto al rilievo principale.
"""

from contextlib import contextmanager
import inspect

import streamlit as st

from app.device_mode import full_device_is_mobile
import app.special_datetime_ui as _special_datetime


@contextmanager
def _reuse_compact_special_path():
    """Riusa un singolo passaggio compatto senza classificare desktop come mobile."""
    original = _special_datetime.full_device_is_mobile
    _special_datetime.full_device_is_mobile = lambda: True
    try:
        yield
    finally:
        _special_datetime.full_device_is_mobile = original


def install_desktop_datetime_ui() -> None:
    """Installa titolo desktop e orari speciali compatti nella sola Full desktop."""
    if getattr(st, "_desktop_datetime_ui_installed", False):
        return
    if full_device_is_mobile():
        return

    current_markdown = st.markdown
    current_columns = st.columns
    current_date_input = st.date_input
    current_button = st.button

    context = {
        "parametro_id": None,
        "await_datetime": False,
    }

    def markdown_with_desktop_title(body, *args, **kwargs):
        if isinstance(body, str) and "mortem-full-title" in body:
            body = body.replace(
                "mortem-full-title",
                "mortem-full-title-desktop",
                1,
            )
        return current_markdown(body, *args, **kwargs)

    def columns_with_desktop_special_time(spec, *args, **kwargs):
        caller = inspect.currentframe().f_back
        full_page = _special_datetime._is_full_page_frame(caller)
        caller_parametro_id = (
            caller.f_locals.get("parametro_id")
            if full_page and caller is not None
            else None
        )
        if caller_parametro_id in _special_datetime._SPECIAL_PARAM_IDS:
            context["parametro_id"] = caller_parametro_id

        parametro_id = context["parametro_id"]
        values = _special_datetime._spec_values(spec)

        # La prima coppia [1, 2] resta desktop e conserva la griglia/selettore
        # esistente. Soltanto la successiva riga titolo/helper riusa il layout
        # compatto, che predispone anche il contenitore dell'orario a destra.
        if (
            full_page
            and parametro_id in _special_datetime._SPECIAL_PARAM_IDS
            and values == (1.0, 0.5)
        ):
            with _reuse_compact_special_path():
                return current_columns(spec, *args, **kwargs)

        if (
            full_page
            and parametro_id in _special_datetime._SPECIAL_PARAM_IDS
            and values == (0.75, 0.25)
        ):
            context["await_datetime"] = True
            return current_columns(spec, *args, **kwargs)

        # Dopo la checkbox legacy soppressa, il renderer compatto instrada il
        # picker nel contenitore già creato accanto al titolo e sopprime le due
        # etichette Data/Ora sottostanti.
        if (
            full_page
            and parametro_id in _special_datetime._SPECIAL_PARAM_IDS
            and spec == 2
            and context["await_datetime"]
        ):
            context["await_datetime"] = False
            with _reuse_compact_special_path():
                return current_columns(spec, *args, **kwargs)

        return current_columns(spec, *args, **kwargs)

    def date_input_with_inferred_special_date(label, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = _special_datetime._DATE_KEY_TO_PARAM_ID.get(kwargs.get("key"))
        if (
            parametro_id in _special_datetime._SPECIAL_PARAM_IDS
            and _special_datetime._is_full_page_frame(caller)
        ):
            with _reuse_compact_special_path():
                return current_date_input(label, *args, **kwargs)
        return current_date_input(label, *args, **kwargs)

    def button_with_desktop_inferred_dates(label, *args, **kwargs):
        caller = inspect.currentframe().f_back
        if (
            kwargs.get("key") == "btn_stima"
            and _special_datetime._is_full_page_frame(caller)
        ):
            with _reuse_compact_special_path():
                return current_button(label, *args, **kwargs)
        return current_button(label, *args, **kwargs)

    st.markdown = markdown_with_desktop_title
    st.columns = columns_with_desktop_special_time
    st.date_input = date_input_with_inferred_special_date
    st.button = button_with_desktop_inferred_dates
    st._desktop_datetime_ui_installed = True
