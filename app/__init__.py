# -*- coding: utf-8 -*-

import streamlit as st

import app.perioral_single_grid as _perioral_single_grid
import app.sopraciliare_ui as _sopraciliare_ui
from app.decimal_number_input import decimal_number_input
from app.special_datetime_ui import install_special_datetime_ui
from app.special_heading_ui import install_special_heading_style
from app.supra_single_grid import install_supra_single_grid


# Campi decimali della schermata completa: il componente dedicato mantiene
# il punto decimale e i controlli −/+ nello stesso riquadro.
_full_decimal_keys = {
    "rt_val",
    "tm_val",
    "peso",
    "ta_base_val",
    "ta_other_val",
    "fattore_correzione",
    "fc_min_val",
    "fc_other_val",
}
_number_input_original = st.number_input


def _same_decimal_value(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    try:
        return abs(float(a) - float(b)) < 1e-12
    except (TypeError, ValueError):
        return a == b


def _number_input_with_decimal_point(label, *args, **kwargs):
    key = kwargs.get("key")
    # La MSIL usa ancora il number_input nativo: i suoi campi hanno label vuota.
    # In questo passaggio modifichiamo soltanto il riquadro Henssge completo.
    if key in _full_decimal_keys and str(label).strip():
        if args:
            # I campi interessati nell'app usano argomenti nominati; fallback
            # prudente al widget originale se in futuro la firma cambia.
            return _number_input_original(label, *args, **kwargs)

        logical_value = st.session_state.get(key, kwargs.get("value"))
        mirror_key = f"__decimal_component_mirror_{key}"
        sync_key = f"__decimal_component_sync_{key}"

        if mirror_key not in st.session_state:
            st.session_state[mirror_key] = logical_value
        st.session_state.setdefault(sync_key, 0)

        external_change = not _same_decimal_value(
            logical_value,
            st.session_state.get(mirror_key),
        )
        if external_change:
            st.session_state[sync_key] += 1
            st.session_state[mirror_key] = logical_value

        result = decimal_number_input(
            value=logical_value,
            step=kwargs.get("step", 1.0),
            format=kwargs.get("format", "%g"),
            min_value=kwargs.get("min_value"),
            max_value=kwargs.get("max_value"),
            disabled=kwargs.get("disabled", False),
            sync_token=st.session_state[sync_key],
            aria_label=label,
            key=f"mortem_decimal_{key}",
        )

        # Durante una sincronizzazione esterna (es. “Suggerisci FC”) il valore
        # restituito dal componente può essere quello del render precedente:
        # in quel solo passaggio prevale il valore logico appena aggiornato.
        if external_change:
            return logical_value

        st.session_state[key] = result
        st.session_state[mirror_key] = result
        return result

    return _number_input_original(label, *args, **kwargs)


st.number_input = _number_input_with_decimal_point


# La tavola peribuccale originale lascia più bianco sotto i disegni rispetto
# alla sopraciliare. Manteniamo però bocca e mento integralmente visibili.
_perioral_single_grid._IMAGE_ONLY_FRACTION = 0.82

install_supra_single_grid(_sopraciliare_ui)
_perioral_single_grid.install_perioral_single_grid(_sopraciliare_ui)
_sopraciliare_ui.install_sopraciliare_click_selector()

_electrical_selectbox = st.selectbox


def _selectbox_with_perioral_grid(label, options, *args, **kwargs):
    if label == _sopraciliare_ui._PERIORAL_LABEL:
        return _sopraciliare_ui._render_perioral_tile_grid(
            widget_key=kwargs.get("key"),
            options=list(options),
        )
    return _electrical_selectbox(label, options, *args, **kwargs)


st.selectbox = _selectbox_with_perioral_grid
install_special_heading_style()
install_special_datetime_ui()
