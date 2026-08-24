# -*- coding: utf-8 -*-

import streamlit as st

import app.perioral_single_grid as _perioral_single_grid
import app.sopraciliare_ui as _sopraciliare_ui
from app.special_datetime_ui import install_special_datetime_ui
from app.special_heading_ui import install_special_heading_style
from app.supra_single_grid import install_supra_single_grid


# Campi decimali della schermata completa: usiamo un input testuale controllato
# per evitare la localizzazione automatica del separatore decimale di
# <input type="number"> su browser/dispositivi configurati in italiano.
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


def _format_decimal_value(value, fmt: str) -> str:
    if value is None:
        return ""
    try:
        return fmt % float(value)
    except Exception:
        return str(value).replace(",", ".")


def _parse_decimal_value(raw):
    if raw is None:
        return None
    text = str(raw).strip().replace(",", ".")
    if text == "":
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _rounded_decimal(value, fmt: str):
    if value is None:
        return None
    try:
        return float(_format_decimal_value(value, fmt))
    except (TypeError, ValueError):
        return float(value)


def _decimal_text_input(
    label,
    *,
    value=None,
    step=1.0,
    format="%g",
    key=None,
    min_value=None,
    max_value=None,
    label_visibility="visible",
    disabled=False,
    **kwargs,
):
    text_key = f"__decimal_text_{key}"
    mirror_key = f"__decimal_mirror_{key}"

    logical_value = st.session_state.get(key, value)
    parsed_logical = _parse_decimal_value(logical_value)

    # Se il valore logico è stato aggiornato da altro codice (es. suggerimento FC),
    # riallinea la stringa mostrata prima di creare il widget.
    previous_mirror = st.session_state.get(mirror_key, object())
    if previous_mirror != parsed_logical or text_key not in st.session_state:
        st.session_state[text_key] = _format_decimal_value(parsed_logical, format)
        st.session_state[mirror_key] = parsed_logical

    def _commit_text():
        raw = st.session_state.get(text_key, "")
        parsed = _parse_decimal_value(raw)
        if parsed is None and str(raw).strip() != "":
            # Input non valido: ripristina l'ultimo valore numerico valido.
            st.session_state[text_key] = _format_decimal_value(
                st.session_state.get(key, value), format
            )
            return

        if parsed is not None:
            if min_value is not None:
                parsed = max(float(min_value), parsed)
            if max_value is not None:
                parsed = min(float(max_value), parsed)
            parsed = _rounded_decimal(parsed, format)

        st.session_state[key] = parsed
        st.session_state[mirror_key] = parsed
        st.session_state[text_key] = _format_decimal_value(parsed, format)

    st.text_input(
        label,
        key=text_key,
        label_visibility=label_visibility,
        disabled=disabled,
        on_change=_commit_text,
    )

    return st.session_state.get(key, parsed_logical)


def _number_input_with_decimal_point(label, *args, **kwargs):
    key = kwargs.get("key")
    # La MSIL usa ancora il number_input nativo: il suo FC ha label vuota.
    # In questo passaggio modifichiamo soltanto il riquadro Henssge completo.
    if key in _full_decimal_keys and str(label).strip():
        if args:
            # I campi interessati nell'app usano argomenti nominati; fallback
            # prudente al widget originale se in futuro la firma cambia.
            return _number_input_original(label, *args, **kwargs)
        return _decimal_text_input(label, **kwargs)
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
