# -*- coding: utf-8 -*-
"""UI compatta per data/ora dei parametri tanatologici speciali.

Nella pagina Full la data/ora principale è sempre visibile: il vecchio toggle
viene soppresso e l'assenza dell'ora mantiene la stessa semantica del precedente
stato OFF. Per i parametri speciali data e ora sono mostrate direttamente,
ereditate dal rilievo principale e modificabili senza conferme intermedie.
"""

import datetime
import inspect
import re

import streamlit as st

from app.device_mode import full_device_is_mobile
from app.native_time_picker import EMPTY_TIME_SENTINEL
from app.special_tanatology_states import (
    PARAM_CHEMICAL_PUPILLARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_MECHANICAL_MUSCLE,
    SPECIAL_PARAM_LABEL_IT,
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

_SELECTOR_KEY_TO_PARAM_ID = {
    f"{label}_selector": param_id
    for param_id, label in SPECIAL_PARAM_LABEL_IT.items()
}
_DATE_KEY_TO_PARAM_ID = {
    f"{label}_data": param_id
    for param_id, label in SPECIAL_PARAM_LABEL_IT.items()
}

_ORANGE_PROMPT_PREFIX = (
    "<div style='font-size: 0.8em; color: orange; margin-bottom: 3px;'>"
)
_DATETIME_LABEL_PREFIX = "<div style='font-size: 0.88rem; padding-top: 0.4rem;'>"
_TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")

_FULL_INITIAL_FRAMELESS_CSS = r"""
<style>
@media (max-width: 768px) {
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-inspection_datetime_row"]),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-selettore_macchie_ui"]),
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-inspection_datetime_row"]) > [data-testid="stVerticalBlock"],
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-selettore_macchie_ui"]) > [data-testid="stVerticalBlock"] {
    border: 0 !important;
    border-width: 0 !important;
    border-color: transparent !important;
    outline: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
  }

  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-inspection_datetime_row"])::before,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-inspection_datetime_row"])::after,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-selettore_macchie_ui"])::before,
  body:has([class*="st-key-stima_cautelativa_beta"])
  [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-selettore_macchie_ui"])::after {
    border: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
  }
}
</style>
"""


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


def _is_full_page_frame(frame) -> bool:
    if frame is None:
        return False
    filename = str(frame.f_globals.get("__file__", "")).replace("\\", "/")
    return filename.endswith("/Stima_epoca_decesso.py") or filename == "Stima_epoca_decesso.py"


def _main_time_is_valid() -> bool:
    value = st.session_state.get("input_ora_rilievo")
    return isinstance(value, str) and bool(_TIME_RE.fullmatch(value.strip()))


def install_special_datetime_ui():
    """Installa data/ora sempre visibili nella Full e UI speciale compatta."""
    if getattr(st, "_special_datetime_ui_installed", False):
        return

    original_checkbox = st.checkbox
    original_markdown = st.markdown
    original_columns = st.columns
    original_selectbox = st.selectbox
    original_toggle = st.toggle
    original_date_input = st.date_input
    original_button = st.button
    original_container = st.container

    # Stato locale del renderer: viene impostato dal selectbox del parametro
    # speciale e consumato soltanto dalla sequenza immediatamente successiva.
    context = {
        "parametro_id": None,
        "await_checkbox": False,
        "await_datetime": False,
        "datetime_labels_left": 0,
    }

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
        [class*="st-key-special_datetime_row_"] input,
        [class*="st-key-special_datetime_time_"] iframe {
            width: 100% !important;
            min-width: 0 !important;
        }

        [class*="st-key-special_datetime_time_"] iframe {
            display: block !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def container_without_initial_mobile_frames(*args, **kwargs):
        caller = inspect.currentframe().f_back
        if (
            kwargs.get("border") is True
            and _is_full_page_frame(caller)
            and full_device_is_mobile()
            and "full_mobile" not in caller.f_locals
        ):
            kwargs["border"] = False
        return original_container(*args, **kwargs)

    def toggle_without_main_datetime_switch(label, *args, **kwargs):
        caller = inspect.currentframe().f_back
        if kwargs.get("key") == "usa_orario_custom" and _is_full_page_frame(caller):
            original_markdown(
                "<div class='mortem-section-title'>Data e ora rilievi tanatologici</div>",
                unsafe_allow_html=True,
            )
            # Il codice della pagina continua a percorrere il ramo legacy ON,
            # così i campi restano montati. L'effettiva applicazione della data/ora
            # viene decisa in fondo alla pagina in base alla presenza di un'ora valida.
            st.session_state["__full_datetime_always_visible"] = True
            st.session_state["usa_orario_custom"] = True
            if not st.session_state.get("input_ora_rilievo"):
                # Sentinella truthy: impedisce al codice legacy di sostituire il
                # campo vuoto con 00:00 prima che il picker venga renderizzato.
                st.session_state["input_ora_rilievo"] = EMPTY_TIME_SENTINEL
            return True
        return original_toggle(label, *args, **kwargs)

    def selectbox_with_special_context(label, options, *args, **kwargs):
        parametro_id = _SELECTOR_KEY_TO_PARAM_ID.get(kwargs.get("key"))
        if parametro_id is not None:
            context["parametro_id"] = parametro_id
            context["await_checkbox"] = False
            context["await_datetime"] = False
            context["datetime_labels_left"] = 0
        return original_selectbox(label, options, *args, **kwargs)

    def checkbox_without_different_time(label, *args, **kwargs):
        parametro_id = context["parametro_id"]
        key = kwargs.get("key")
        expected_key = None
        if parametro_id in _SPECIAL_PARAM_IDS:
            expected_key = f"{SPECIAL_PARAM_LABEL_IT[parametro_id]}_diversa"

        if (
            context["await_checkbox"]
            and isinstance(key, str)
            and key == expected_key
            and bool(st.session_state.get("usa_orario_custom", False))
        ):
            st.session_state[key] = True
            context["await_checkbox"] = False
            context["await_datetime"] = True
            return True

        return original_checkbox(label, *args, **kwargs)

    def markdown_without_datetime_labels(body, *args, **kwargs):
        if isinstance(body, str):
            if ".final-text{" in body:
                body = _FULL_INITIAL_FRAMELESS_CSS + body
                kwargs["unsafe_allow_html"] = True

            if context["await_checkbox"] and body.startswith(_ORANGE_PROMPT_PREFIX):
                return None

            if (
                context["datetime_labels_left"] > 0
                and body.startswith(_DATETIME_LABEL_PREFIX)
            ):
                context["datetime_labels_left"] -= 1
                return None

        return original_markdown(body, *args, **kwargs)

    def date_input_with_main_inheritance(label, *args, **kwargs):
        key = kwargs.get("key")
        parametro_id = _DATE_KEY_TO_PARAM_ID.get(key)
        caller = inspect.currentframe().f_back
        if (
            parametro_id not in _SPECIAL_PARAM_IDS
            or not _is_full_page_frame(caller)
            or not st.session_state.get("__full_datetime_always_visible", False)
        ):
            return original_date_input(label, *args, **kwargs)

        main_date = st.session_state.get("input_data_rilievo") or datetime.date.today()
        manual_key = f"{key}__manual"
        last_main_key = f"{key}__last_main"
        manual = bool(st.session_state.get(manual_key, False))
        last_main = st.session_state.get(last_main_key)
        current = st.session_state.get(key)

        if not manual:
            if current is None or last_main is None or current == last_main:
                st.session_state[key] = main_date
            kwargs["value"] = st.session_state.get(key, main_date)

        result = original_date_input(label, *args, **kwargs)

        if result == main_date:
            st.session_state[manual_key] = False
            st.session_state[last_main_key] = main_date
        else:
            st.session_state[manual_key] = True

        return result

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
        # Il ciclo dei parametri conosce parametro_id già prima del selectbox.
        # Recuperarlo anche dal chiamante permette al layout elettrico sottostante
        # di creare subito la coppia sopraciliare/peribuccale nel punto corretto.
        caller = inspect.currentframe().f_back
        caller_parametro_id = caller.f_locals.get("parametro_id") if caller else None
        if caller_parametro_id in _SPECIAL_PARAM_IDS:
            parametro_id = caller_parametro_id
        else:
            parametro_id = context["parametro_id"]

        usa_orario_custom_globale = bool(
            st.session_state.get("usa_orario_custom", False)
        )

        if parametro_id in _SPECIAL_PARAM_IDS and usa_orario_custom_globale:
            values = _spec_values(spec)

            # La riga legacy testo + checkbox compare solo dopo un selectbox
            # speciale valutato: la sostituiamo con due contesti vuoti e
            # aspettiamo la checkbox che il codice chiamante esegue subito dopo.
            if values == (0.75, 0.25):
                context["await_checkbox"] = True
                context["await_datetime"] = False
                return _NoopContext(), _NoopContext()

            # Dopo la checkbox resa implicitamente True arriva esattamente la
            # riga Data/Ora. Il flag viene consumato subito, evitando che altre
            # st.columns(2) dell'app possano essere intercettate per errore.
            if spec == 2 and context["await_datetime"]:
                context["await_datetime"] = False
                context["datetime_labels_left"] = 2

                if parametro_id in _ELECTRICAL_PARAM_IDS:
                    # original_columns è il layout elettrico già installato:
                    # crea l'ancora nella metà corretta della coppia.
                    anchor, _ = original_columns([1000, 1], gap="small")
                    with anchor:
                        return _datetime_boxes(parametro_id)

                return _datetime_boxes(parametro_id)

        return original_columns(spec, *args, **kwargs)

    def button_with_effective_main_datetime(label, *args, **kwargs):
        caller = inspect.currentframe().f_back
        if kwargs.get("key") == "btn_stima" and _is_full_page_frame(caller):
            main_time_valid = _main_time_is_valid()
            st.session_state["usa_orario_custom"] = main_time_valid

            # Se l'ora principale è vuota, la data/ora resta solo informativa:
            # anche eventuali modifiche ai singoli parametri non devono traslare
            # i range, esattamente come nel precedente stato toggle OFF.
            if not main_time_valid:
                widgets = caller.f_locals.get("widgets_parametri_aggiuntivi")
                if isinstance(widgets, dict):
                    for values in widgets.values():
                        if isinstance(values, dict):
                            values["data_rilievo"] = None
                            values["ora_rilievo"] = None

        return original_button(label, *args, **kwargs)

    st.container = container_without_initial_mobile_frames
    st.toggle = toggle_without_main_datetime_switch
    st.selectbox = selectbox_with_special_context
    st.checkbox = checkbox_without_different_time
    st.markdown = markdown_without_datetime_labels
    st.date_input = date_input_with_main_inheritance
    st.columns = columns_with_compact_datetime
    st.button = button_with_effective_main_datetime
    st._special_datetime_ui_installed = True
