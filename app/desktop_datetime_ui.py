# -*- coding: utf-8 -*-
"""Adatta al desktop data/ora e titoli della schermata Full.

Il desktop mantiene il proprio layout: i quattro parametri tanatologici speciali
usano una riga nativa e stabile per titolo, helper e orario; la data del singolo
rilievo viene dedotta rispetto al rilievo principale. Il renderer mobile resta
separato e invariato.
"""

import datetime
import inspect

import streamlit as st

from app.device_mode import full_device_is_mobile
import app.full_mobile_compact as _full_mobile_compact
import app.full_mobile_layout as _full_mobile_layout
import app.special_datetime_ui as _special_datetime


_ELECTRICAL_DESKTOP_PARAMS = {
    _special_datetime.PARAM_ELECTRICAL_SUPRACILIARY,
    _special_datetime.PARAM_ELECTRICAL_PERIORAL,
}


def _desktop_initial_style_bundle(body: str) -> str:
    """Raccoglie il CSS iniziale in un solo blocco senza creare righe di layout."""
    responsive_css = _full_mobile_layout._FULL_MOBILE_CSS.replace(
        "padding-top: 2rem !important;",
        "padding-top: 0.55rem !important;",
        1,
    )
    return (
        _special_datetime._FULL_INITIAL_FRAMELESS_CSS
        + responsive_css
        + body
        + _full_mobile_compact._FULL_MOBILE_COMPACT_CSS
    )


def install_desktop_datetime_ui() -> None:
    """Installa gli adattamenti dedicati alla sola Full desktop."""
    if getattr(st, "_desktop_datetime_ui_installed", False):
        return
    if full_device_is_mobile():
        return

    current_markdown = st.markdown
    current_columns = st.columns
    current_date_input = st.date_input
    current_button = st.button
    current_container = st.container
    current_number_input = st.number_input

    context = {
        "parametro_id": None,
        "await_datetime": False,
        "datetime_labels_left": 0,
        "clock_container": None,
        "time_container": None,
    }

    def markdown_with_desktop_title(body, *args, **kwargs):
        if isinstance(body, str):
            # Il blocco iniziale contiene esclusivamente CSS. Su desktop viene
            # inviato tramite st.html: Streamlit lo colloca nell'event container
            # e non crea righe vuote nella griglia principale.
            if ".final-text{" in body and body.lstrip().startswith("<style>"):
                return st.html(_desktop_initial_style_bundle(body))

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

    def number_input_without_legacy_fc_split(label, *args, **kwargs):
        """Il FC standard usa direttamente la larghezza assegnata dal layout desktop."""
        if (
            kwargs.get("key") == "fattore_correzione"
            and not st.session_state.get("stima_cautelativa_beta", False)
            and kwargs.get("_mortem_compact_label") == ""
        ):
            clean_kwargs = dict(kwargs)
            clean_kwargs.pop("_mortem_compact_label", None)
            # L'etichetta desktop è già renderizzata subito sopra il controllo.
            # Passare label vuota evita sia l'etichetta interna sia il vecchio
            # secondo st.columns che dimezzava il campo al primo render.
            return current_number_input("", *args, **clean_kwargs)
        return current_number_input(label, *args, **kwargs)

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

        # Tutti e quattro i parametri usano ora la stessa struttura desktop.
        # Nessun passaggio viene più fatto fingendo che il desktop sia mobile.
        if (
            full_page
            and parametro_id in _special_datetime._SPECIAL_PARAM_IDS
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

            # Le due eccitabilità elettriche conservano il proprio popover
            # legacy, che il renderer elettrico trasforma nell'helper uniforme.
            # Per meccanica e pupillare l'helper viene montato qui direttamente.
            if parametro_id not in _ELECTRICAL_DESKTOP_PARAMS:
                with help_cell:
                    _special_datetime._render_click_help(
                        _special_datetime._HELPER_TEXTS[parametro_id],
                        f"mortem_help_prudent_electrical_{parametro_id}",
                    )

            context["clock_container"] = clock_cell
            context["time_container"] = time_cell
            return title_cell, help_cell

        if (
            full_page
            and parametro_id in _special_datetime._SPECIAL_PARAM_IDS
            and values == (0.75, 0.25)
        ):
            context["await_datetime"] = True
            return current_columns(spec, *args, **kwargs)

        if (
            full_page
            and parametro_id in _special_datetime._SPECIAL_PARAM_IDS
            and spec == 2
            and context["await_datetime"]
        ):
            context["await_datetime"] = False
            if context.get("time_container") is not None:
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
    st.number_input = number_input_without_legacy_fc_split
    st.columns = columns_with_desktop_special_time
    st.date_input = date_input_with_inferred_special_date
    st.button = button_with_desktop_inferred_dates
    st._desktop_datetime_ui_installed = True
