# -*- coding: utf-8 -*-
"""UI compatta per data/ora dei parametri tanatologici speciali.

La vecchia conferma "valutato a un'ora diversa" viene resa implicita.
Data e ora vengono mostrati direttamente su una sola riga compatta anche
su schermi stretti; i widget effettivi sono definiti dalla pagina Full.
"""

import inspect

import streamlit as st

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

_ORANGE_PROMPT_PREFIX = (
    "<div style='font-size: 0.8em; color: orange; margin-bottom: 3px;'>"
)
_DATETIME_LABEL_PREFIX = "<div style='font-size: 0.88rem; padding-top: 0.4rem;'>"


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
    original_selectbox = st.selectbox

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
            if context["await_checkbox"] and body.startswith(_ORANGE_PROMPT_PREFIX):
                return None

            if (
                context["datetime_labels_left"] > 0
                and body.startswith(_DATETIME_LABEL_PREFIX)
            ):
                context["datetime_labels_left"] -= 1
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

    st.selectbox = selectbox_with_special_context
    st.checkbox = checkbox_without_different_time
    st.markdown = markdown_without_datetime_labels
    st.columns = columns_with_compact_datetime
    st._special_datetime_ui_installed = True
