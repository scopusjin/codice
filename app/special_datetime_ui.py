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
from app.full_mobile_layout import _render_click_help
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
_SHORT_LABELS = {
    PARAM_ELECTRICAL_SUPRACILIARY: "Ecc. elettrica sopraciliare",
    PARAM_ELECTRICAL_PERIORAL: "Ecc. elettrica peribuccale",
    PARAM_MECHANICAL_MUSCLE: "Ecc. muscolare meccanica",
    PARAM_CHEMICAL_PUPILLARY: "Ecc. chimica pupillare",
}
_HELPER_TEXTS = {
    PARAM_ELECTRICAL_SUPRACILIARY: (
        "Eccitabilità elettrica sopraciliare. "
        "Il metodo valuta la persistenza dell’eccitabilità muscolare elettrica residua mediante "
        "stimolazione elettrica della regione sopraciliare e classificazione dell’estensione della "
        "risposta muscolare. Posizionare gli elettrodi distanziati di circa 2 cm nella parte nasale "
        "del sopracciglio, a una profondità di circa 0.5 - 0.7 cm, e applicare uno stimolo di "
        "30 mA · 10 ms · 50 Hz."
    ),
    PARAM_ELECTRICAL_PERIORAL: (
        "Eccitabilità elettrica peribuccale. "
        "Il metodo valuta la persistenza dell’eccitabilità muscolare elettrica residua mediante "
        "stimolazione elettrica della regione peribuccale e classificazione della risposta come "
        "contrazione dei muscoli facciali, dei muscoli peribuccali, reazione focale o assenza di "
        "reazione. Posizionare gli elettrodi a circa 1 cm dagli angoli della bocca, a una profondità "
        "di circa 0.5 - 0.7 cm, e applicare uno stimolo di 30 mA · 10 ms · 50 Hz."
    ),
    PARAM_MECHANICAL_MUSCLE: (
        "Eccitabilità muscolare meccanica. "
        "Il metodo valuta la persistenza dell’eccitabilità muscolare meccanica residua mediante "
        "percussione del muscolo bicipite del braccio, osservando la risposta: contrazione dell’intero "
        "muscolo, tumefazione reversibile, piccola tumefazione persistente o nessuna reazione."
    ),
    PARAM_CHEMICAL_PUPILLARY: (
        "Eccitabilità chimica pupillare. "
        "Il metodo valuta la persistenza dell’eccitabilità chimica dell’iride mediante instillazione "
        "di atropina, tropicamide o acetilcolina e osservazione del diametro pupillare: dilatazione, "
        "riduzione o assenza di variazione."
    ),
}

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


class _MobileSpecialHelperContext:
    """Helper mobile con denominazione estesa e nota del parametro."""

    def __init__(self, parametro_id, popover_factory):
        self._parametro_id = parametro_id
        self._popover_factory = popover_factory

    def __enter__(self):
        helper_text = _HELPER_TEXTS[self._parametro_id]
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=\.)\s+", helper_text)
            if sentence.strip()
        ]
        with self._popover_factory(
            "?",
            key=f"mortem_help_prudent_electrical_{self._parametro_id}",
        ):
            for sentence in sentences:
                st.markdown(sentence)
        if self._parametro_id in {
            PARAM_ELECTRICAL_SUPRACILIARY,
            PARAM_ELECTRICAL_PERIORAL,
        }:
            st._suppress_legacy_electrical_image = True
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._parametro_id in {
            PARAM_ELECTRICAL_SUPRACILIARY,
            PARAM_ELECTRICAL_PERIORAL,
        }:
            st._suppress_legacy_electrical_image = False
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


def _infer_measurement_date(main_date, main_time, measurement_time):
    """Deduce il giorno più vicino al rilievo principale, gestendo la mezzanotte."""
    if not isinstance(main_date, datetime.date):
        main_date = datetime.date.today()
    if not (
        isinstance(main_time, str)
        and _TIME_RE.fullmatch(main_time.strip())
        and isinstance(measurement_time, str)
        and _TIME_RE.fullmatch(measurement_time.strip())
    ):
        return main_date

    main_hour, main_minute = (int(part) for part in main_time.split(":"))
    measure_hour, measure_minute = (int(part) for part in measurement_time.split(":"))
    delta_minutes = (measure_hour * 60 + measure_minute) - (main_hour * 60 + main_minute)

    if delta_minutes < -12 * 60:
        return main_date + datetime.timedelta(days=1)
    if delta_minutes > 12 * 60:
        return main_date - datetime.timedelta(days=1)
    return main_date


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
    original_popover = st.popover

    # Stato locale del renderer: viene impostato dal selectbox del parametro
    # speciale e consumato soltanto dalla sequenza immediatamente successiva.
    context = {
        "parametro_id": None,
        "param_container": None,
        "clock_container": None,
        "time_container": None,
        "special_outer_pending": False,
        "await_checkbox": False,
        "await_datetime": False,
        "datetime_labels_left": 0,
    }

    original_markdown(
        """
        <style>
        [class*="st-key-special_datetime_row_"] {
            width: 100% !important;
            margin-top: 0.06rem !important;
            margin-bottom: 0.08rem !important;
        }

        @media (max-width: 768px) {
          body:has(.mortem-full-title)
          [data-testid="stMainBlockContainer"] {
            padding-top: 0.55rem !important;
          }

          body:has(.mortem-full-title)
          [data-testid="stElementContainer"][class*="st-key-special_datetime_row_"],
          body:has(.mortem-full-title)
          [data-testid="stElementContainer"]:has([class*="st-key-special_datetime_row_"]) {
            margin-top: -1.35rem !important;
            margin-bottom: 0 !important;
          }

          body:has(.mortem-full-title)
          [class*="st-key-special_datetime_row_"] {
            margin-top: -0.24rem !important;
            margin-bottom: 0.02rem !important;
          }

          body:has(.mortem-full-title)
          [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"][class*="st-key-special_datetime_row_"]),
          body:has(.mortem-full-title)
          [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] > [class*="st-key-special_datetime_row_"]) {
            gap: 0.18rem !important;
          }
        }

        [class*="st-key-special_datetime_row_"] div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 0.30rem !important;
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
        special_outer = bool(context.get("special_outer_pending"))
        if (
            kwargs.get("border") is True
            and _is_full_page_frame(caller)
            and full_device_is_mobile()
            and ("full_mobile" not in caller.f_locals or special_outer)
        ):
            kwargs["border"] = False
            if special_outer:
                context["special_outer_pending"] = False
        return original_container(*args, **kwargs)

    def toggle_without_main_datetime_switch(label, *args, **kwargs):
        caller = inspect.currentframe().f_back
        if kwargs.get("key") == "mostra_parametri_aggiuntivi" and _is_full_page_frame(caller):
            result = original_toggle(label, *args, **kwargs)
            context["special_outer_pending"] = bool(
                result and full_device_is_mobile()
            )
            return result

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

    def popover_with_mobile_special_helper(*args, **kwargs):
        caller = inspect.currentframe().f_back
        parametro_id = caller.f_locals.get("parametro_id") if caller else None
        if (
            full_device_is_mobile()
            and parametro_id in {
                PARAM_ELECTRICAL_SUPRACILIARY,
                PARAM_ELECTRICAL_PERIORAL,
            }
        ):
            return _MobileSpecialHelperContext(parametro_id, original_popover)
        return original_popover(*args, **kwargs)

    def markdown_without_datetime_labels(body, *args, **kwargs):
        if isinstance(body, str):
            if ".final-text{" in body:
                body = _FULL_INITIAL_FRAMELESS_CSS + body
                kwargs["unsafe_allow_html"] = True

            parametro_id = context["parametro_id"]
            if full_device_is_mobile() and parametro_id in _SHORT_LABELS:
                full_label = SPECIAL_PARAM_LABEL_IT[parametro_id]
                if f"{full_label}:" in body:
                    body = (
                        "<div class='mortem-section-title'>"
                        f"{_SHORT_LABELS[parametro_id]}"
                        "</div>"
                    )
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
        if key == "input_data_rilievo" and key in st.session_state:
            kwargs.pop("value", None)

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

        if full_device_is_mobile():
            full_label = SPECIAL_PARAM_LABEL_IT[parametro_id]
            ora_key = f"{full_label}_ora"
            result = _infer_measurement_date(
                main_date,
                st.session_state.get("input_ora_rilievo"),
                st.session_state.get(ora_key),
            )
            st.session_state[key] = result
            st.session_state.pop(manual_key, None)
            st.session_state.pop(last_main_key, None)
            return result

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
            vertical_alignment="center",
            gap="xsmall",
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
            context["parametro_id"] = parametro_id
        else:
            parametro_id = context["parametro_id"]

        values = _spec_values(spec)
        mobile = full_device_is_mobile()

        # La sopraciliare conserva il suo stack compatto già collaudato. Anche
        # meccanica e pupillare usano uno stack locale senza gap per avvicinare
        # esclusivamente la riga titolo al proprio selettore. La peribuccale
        # mantiene invece il layout della griglia già collaudato.
        if parametro_id in _SPECIAL_PARAM_IDS and values == (1.0, 2.0):
            context["clock_container"] = None
            context["time_container"] = None
            result = original_columns(spec, *args, **kwargs)
            try:
                context["param_container"] = result[0]
            except (TypeError, IndexError):
                context["param_container"] = None

            compact_mobile_params = {
                PARAM_ELECTRICAL_SUPRACILIARY: "special_supra_mobile_stack",
                PARAM_MECHANICAL_MUSCLE: "special_mechanical_mobile_stack",
                PARAM_CHEMICAL_PUPILLARY: "special_pupillary_mobile_stack",
            }
            compact_key = compact_mobile_params.get(parametro_id)
            if mobile and compact_key and context["param_container"] is not None:
                with context["param_container"]:
                    compact_stack = original_container(
                        gap=None,
                        key=compact_key,
                    )
                context["param_container"] = compact_stack
                return compact_stack, compact_stack
            return result

        # Su mobile ogni parametro speciale usa una sola riga: titolo breve e
        # helper a sinistra, simbolo orologio e picker ancorati a destra.
        if (
            mobile
            and parametro_id in _SPECIAL_PARAM_IDS
            and values == (1.0, 0.5)
            and context.get("param_container") is not None
        ):
            with context["param_container"]:
                with original_container(
                    horizontal=True,
                    wrap=False,
                    horizontal_alignment="distribute",
                    vertical_alignment="center",
                    gap="xsmall",
                    key=f"electrical_title_help_row_{parametro_id}",
                ):
                    left_group = original_container(
                        horizontal=True,
                        wrap=False,
                        vertical_alignment="center",
                        gap="xsmall",
                        width="stretch",
                        key=f"special_title_left_{parametro_id}",
                    )
                    time_group = original_container(
                        horizontal=True,
                        wrap=False,
                        vertical_alignment="center",
                        gap="xsmall",
                        width="content",
                        key=f"special_title_time_group_{parametro_id}",
                    )

                with left_group:
                    title_cell = original_container(
                        width="content",
                        key=f"electrical_title_text_{parametro_id}",
                    )
                    help_cell = original_container(
                        width="content",
                        key=f"electrical_title_help_{parametro_id}",
                    )

                with time_group:
                    clock_cell = original_container(
                        width="content",
                        key=f"special_title_clock_{parametro_id}",
                    )
                    time_cell = original_container(
                        width=108,
                        key=f"special_datetime_time_title_{parametro_id}",
                    )

            context["clock_container"] = clock_cell
            context["time_container"] = time_cell

            # Per i due parametri senza vecchio popover l'helper va inserito
            # direttamente nella cella predisposta; gli elettrici lo ricevono
            # dal popover legacy intercettato subito dopo dal chiamante.
            if parametro_id in {
                PARAM_MECHANICAL_MUSCLE,
                PARAM_CHEMICAL_PUPILLARY,
            }:
                with help_cell:
                    _render_click_help(
                        _HELPER_TEXTS[parametro_id],
                        f"mortem_help_prudent_electrical_{parametro_id}",
                    )

            return title_cell, help_cell

        usa_orario_custom_globale = bool(
            st.session_state.get("usa_orario_custom", False)
        )

        if parametro_id in _SPECIAL_PARAM_IDS and usa_orario_custom_globale:
            # La riga legacy testo + checkbox compare solo dopo un selectbox
            # speciale valutato: la sostituiamo con due contesti vuoti e
            # aspettiamo la checkbox che il codice chiamante esegue subito dopo.
            if values == (0.75, 0.25):
                context["await_checkbox"] = True
                context["await_datetime"] = False
                return _NoopContext(), _NoopContext()

            # Su mobile la data è dedotta e il solo orario viene renderizzato
            # nel contenitore predisposto all'estrema destra del titolo.
            if spec == 2 and context["await_datetime"]:
                context["await_datetime"] = False
                context["datetime_labels_left"] = 2

                if (
                    mobile
                    and parametro_id in _SPECIAL_PARAM_IDS
                    and context.get("time_container") is not None
                ):
                    clock_cell = context.get("clock_container")
                    if clock_cell is not None:
                        with clock_cell:
                            original_markdown(
                                "<span title='Orario del rilievo' style='font-size:0.76rem; line-height:1;'>🕒</span>",
                                unsafe_allow_html=True,
                            )
                    return _NoopContext(), context["time_container"]

                anchor = context.get("param_container")
                if anchor is None:
                    anchor, _ = original_columns([1000, 1], gap="small")
                with anchor:
                    return _datetime_boxes(parametro_id)

        return original_columns(spec, *args, **kwargs)

    def button_with_effective_main_datetime(label, *args, **kwargs):
        caller = inspect.currentframe().f_back
        if kwargs.get("key") == "btn_stima" and _is_full_page_frame(caller):
            main_time_valid = _main_time_is_valid()
            st.session_state["usa_orario_custom"] = main_time_valid
            widgets = caller.f_locals.get("widgets_parametri_aggiuntivi")

            if main_time_valid and full_device_is_mobile() and isinstance(widgets, dict):
                main_date = st.session_state.get("input_data_rilievo") or datetime.date.today()
                main_time = st.session_state.get("input_ora_rilievo")
                for parametro_id, full_label in SPECIAL_PARAM_LABEL_IT.items():
                    if parametro_id not in _SPECIAL_PARAM_IDS:
                        continue
                    values = widgets.get(full_label)
                    if not isinstance(values, dict):
                        continue
                    inferred_date = _infer_measurement_date(
                        main_date,
                        main_time,
                        values.get("ora_rilievo")
                        or st.session_state.get(f"{full_label}_ora"),
                    )
                    values["data_rilievo"] = inferred_date
                    st.session_state[f"{full_label}_data"] = inferred_date

            # Se l'ora principale è vuota, la data/ora resta solo informativa:
            # anche eventuali modifiche ai singoli parametri non devono traslare
            # i range, esattamente come nel precedente stato toggle OFF.
            if not main_time_valid and isinstance(widgets, dict):
                for values in widgets.values():
                    if isinstance(values, dict):
                        values["data_rilievo"] = None
                        values["ora_rilievo"] = None

        return original_button(label, *args, **kwargs)

    st.container = container_without_initial_mobile_frames
    st.toggle = toggle_without_main_datetime_switch
    st.selectbox = selectbox_with_special_context
    st.checkbox = checkbox_without_different_time
    st.popover = popover_with_mobile_special_helper
    st.markdown = markdown_without_datetime_labels
    st.date_input = date_input_with_main_inheritance
    st.columns = columns_with_compact_datetime
    st.button = button_with_effective_main_datetime
    st._special_datetime_ui_installed = True