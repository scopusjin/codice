# -*- coding: utf-8 -*-
"""Adatta al desktop il sistema data/ora compatto della schermata Full.

Il renderer mobile già collaudato resta invariato. Sul desktop vengono riusati
soltanto i passaggi relativi ai parametri tanatologici speciali: titolo/helper
restano nella colonna desktop esistente, mentre il solo orario viene collocato
accanto al titolo e la data viene dedotta rispetto al rilievo principale.
"""

from contextlib import contextmanager
import datetime
import inspect

import streamlit as st

from app.device_mode import full_device_is_mobile
import app.special_datetime_ui as _special_datetime


_SIMPLE_DESKTOP_PARAMS = {
    _special_datetime.PARAM_MECHANICAL_MUSCLE,
    _special_datetime.PARAM_CHEMICAL_PUPILLARY,
}


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
    current_container = st.container

    context = {
        "parametro_id": None,
        "await_datetime": False,
        "datetime_labels_left": 0,
        "clock_container": None,
        "time_container": None,
    }

    def markdown_with_desktop_title(body, *args, **kwargs):
        if isinstance(body, str):
            if "<h5 class='mortem-full-title'" in body:
                visible_title = body.replace(
                    "class='mortem-full-title'",
                    "class='mortem-full-title-visible'",
                    1,
                )
                body = (
                    "<span class='mortem-full-title' aria-hidden='true' "
                    "style='display:none;'></span>"
                    + visible_title
                )
                kwargs["unsafe_allow_html"] = True
            elif (
                context["datetime_labels_left"] > 0
                and body.startswith(_special_datetime._DATETIME_LABEL_PREFIX)
            ):
                context["datetime_labels_left"] -= 1
                return None

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

        if (
            full_page
            and parametro_id in _special_datetime._SPECIAL_PARAM_IDS
            and values == (1.0, 2.0)
        ):
            context["clock_container"] = None
            context["time_container"] = None
            context["datetime_labels_left"] = 0
            return current_columns(spec, *args, **kwargs)

        # Meccanica e pupillare mantengono la riga desktop naturale: nella
        # seconda colonna vengono predisposti helper e orario, senza riusare
        # il margine negativo riservato alle due eccitabilità elettriche.
        if (
            full_page
            and parametro_id in _SIMPLE_DESKTOP_PARAMS
            and values == (1.0, 0.5)
        ):
            result = current_columns(spec, *args, **kwargs)
            try:
                title_cell, action_cell = result
            except (TypeError, ValueError):
                return result

            with action_cell:
                with current_container(
                    horizontal=True,
                    wrap=False,
                    horizontal_alignment="right",
                    vertical_alignment="center",
                    gap="xsmall",
                    width="stretch",
                    key=f"special_desktop_title_actions_{parametro_id}",
                ):
                    help_cell = current_container(
                        width="content",
                        key=f"special_desktop_title_help_{parametro_id}",
                    )
                    clock_cell = current_container(
                        width="content",
                        key=f"special_desktop_title_clock_{parametro_id}",
                    )
                    time_cell = current_container(
                        width=108,
                        key=f"special_desktop_title_time_{parametro_id}",
                    )

            with help_cell:
                _special_datetime._render_click_help(
                    _special_datetime._HELPER_TEXTS[parametro_id],
                    f"mortem_help_prudent_electrical_{parametro_id}",
                )

            context["clock_container"] = clock_cell
            context["time_container"] = time_cell
            return title_cell, action_cell

        # Le due eccitabilità elettriche continuano a riusare il percorso già
        # collaudato, che mantiene titolo/helper e orario nella stessa riga.
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

        # Dopo la checkbox legacy soppressa, il picker dei due parametri
        # semplici viene instradato nella cella predisposta nella riga titolo.
        if (
            full_page
            and parametro_id in _special_datetime._SPECIAL_PARAM_IDS
            and spec == 2
            and context["await_datetime"]
        ):
            context["await_datetime"] = False

            if (
                parametro_id in _SIMPLE_DESKTOP_PARAMS
                and context.get("time_container") is not None
            ):
                context["datetime_labels_left"] = 2
                clock_cell = context.get("clock_container")
                if clock_cell is not None:
                    with clock_cell:
                        current_markdown(
                            "<span title='Orario del rilievo' "
                            "style='font-size:0.76rem; line-height:1;'>🕒</span>",
                            unsafe_allow_html=True,
                        )
                return _special_datetime._NoopContext(), context["time_container"]

            with _reuse_compact_special_path():
                return current_columns(spec, *args, **kwargs)

        return current_columns(spec, *args, **kwargs)

    def date_input_with_inferred_special_date(label, *args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = _special_datetime._DATE_KEY_TO_PARAM_ID.get(kwargs.get("key"))
        if (
            parametro_id not in _special_datetime._SPECIAL_PARAM_IDS
            or not _special_datetime._is_full_page_frame(caller)
        ):
            return current_date_input(label, *args, **kwargs)

        key = kwargs.get("key")
        main_date = st.session_state.get("input_data_rilievo") or datetime.date.today()
        full_label = _special_datetime.SPECIAL_PARAM_LABEL_IT[parametro_id]
        inferred = _special_datetime._infer_measurement_date(
            main_date,
            st.session_state.get("input_ora_rilievo"),
            st.session_state.get(f"{full_label}_ora"),
        )
        st.session_state[key] = inferred
        st.session_state.pop(f"{key}__manual", None)
        st.session_state.pop(f"{key}__last_main", None)
        return inferred

    def button_with_desktop_inferred_dates(label, *args, **kwargs):
        caller = inspect.currentframe().f_back
        if (
            kwargs.get("key") != "btn_stima"
            or not _special_datetime._is_full_page_frame(caller)
        ):
            return current_button(label, *args, **kwargs)

        main_time_valid = _special_datetime._main_time_is_valid()
        st.session_state["usa_orario_custom"] = main_time_valid
        widgets = caller.f_locals.get("widgets_parametri_aggiuntivi")

        if main_time_valid and isinstance(widgets, dict):
            main_date = st.session_state.get("input_data_rilievo") or datetime.date.today()
            main_time = st.session_state.get("input_ora_rilievo")
            for parametro_id, full_label in _special_datetime.SPECIAL_PARAM_LABEL_IT.items():
                if parametro_id not in _special_datetime._SPECIAL_PARAM_IDS:
                    continue
                values = widgets.get(full_label)
                if not isinstance(values, dict):
                    continue
                inferred = _special_datetime._infer_measurement_date(
                    main_date,
                    main_time,
                    values.get("ora_rilievo")
                    or st.session_state.get(f"{full_label}_ora"),
                )
                values["data_rilievo"] = inferred
                st.session_state[f"{full_label}_data"] = inferred
        elif isinstance(widgets, dict):
            for values in widgets.values():
                if isinstance(values, dict):
                    values["data_rilievo"] = None
                    values["ora_rilievo"] = None

        return current_button(label, *args, **kwargs)

    st.markdown = markdown_with_desktop_title
    st.columns = columns_with_desktop_special_time
    st.date_input = date_input_with_inferred_special_date
    st.button = button_with_desktop_inferred_dates
    st._desktop_datetime_ui_installed = True
