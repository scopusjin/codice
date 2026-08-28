# -*- coding: utf-8 -*-
"""Input numerico decimale con punto e controlli integrati per Mor-tem."""

import math
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from app.decimal_number_input_v2 import (
    is_full_mobile_v2_key,
    mobile_decimal_v2_available,
    render_mobile_decimal_v2,
)
from app.locales.it_ui import ui_text


_FRONTEND_DIR = (Path(__file__).resolve().parent / "decimal_number_input_frontend").absolute()
_component = components.declare_component(
    "mortem_decimal_number_input",
    path=str(_FRONTEND_DIR),
)
_FORMAT_RE = re.compile(r"^%\.(\d+)f$")
_TA_BASE_COMPONENT_KEY = "mortem_decimal_ta_base_val"
_TA_OTHER_COMPONENT_KEY = "mortem_decimal_ta_other_val"
_TA_STANDARD_HELP_OPEN_KEY = "__decimal_ta_standard_help_open"
_TA_RANGE_HELP_OPEN_KEY = "__decimal_ta_range_help_open"
_TA_RANGE_MOBILE_NOTE = (
    "Inserisci il valore minimo e massimo plausibili della temperatura ambientale media "
    "nel periodo tra il decesso e l’ispezione."
)


def _theme_value(option, fallback):
    try:
        value = st.get_option(option)
    except Exception:
        value = None
    return value or fallback


def _decimal_places(fmt: str, step) -> int:
    match = _FORMAT_RE.fullmatch(str(fmt or ""))
    if match:
        return max(0, min(8, int(match.group(1))))
    try:
        text = f"{abs(float(step)):.8f}".rstrip("0").rstrip(".")
        return len(text.split(".", 1)[1]) if "." in text else 0
    except Exception:
        return 2


def _finite_float(value):
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def decimal_number_input(
    value=None,
    *,
    step=1.0,
    format="%g",
    min_value=None,
    max_value=None,
    disabled=False,
    sync_token=0,
    aria_label="Valore numerico",
    compact_mobile=False,
    compact_label="",
    unit="",
    hide_group_heading=False,
    inline_weight_toggle=False,
    suggest_enabled=False,
    suggest_label="",
    suggest_active=False,
    on_suggest=None,
    on_change=None,
    key=None,
):
    """Restituisce float/None usando un controllo decimale non localizzato."""
    decimals = _decimal_places(format, step)
    current = _finite_float(value)
    minimum = _finite_float(min_value)
    maximum = _finite_float(max_value)

    # ``compact_mobile`` è il flag storico della resa compatta della Full.
    # La stessa UI V2 viene ora usata sia su mobile sia su desktop; la MSIL non
    # passa questo flag per le proprie chiavi e conserva quindi il renderer V1.
    compact_mobile = bool(compact_mobile)

    interval_mode = bool(
        st.session_state.get("stima_cautelativa_beta", False)
        and st.session_state.get("range_unico_beta", False)
    )
    is_ta_base = key == _TA_BASE_COMPONENT_KEY
    is_ta_other = key == _TA_OTHER_COMPONENT_KEY

    help_state_key = None
    help_text = ""
    if is_ta_base and not interval_mode:
        help_state_key = _TA_STANDARD_HELP_OPEN_KEY
        help_text = ui_text("full.ta_mean_help")
    elif is_ta_other and interval_mode:
        help_state_key = _TA_RANGE_HELP_OPEN_KEY
        help_text = _TA_RANGE_MOBILE_NOTE
    help_enabled = help_state_key is not None

    use_v2_mobile = bool(
        compact_mobile
        and is_full_mobile_v2_key(key)
        and mobile_decimal_v2_available()
    )

    if use_v2_mobile:
        result = render_mobile_decimal_v2(
            value=current,
            step=float(step),
            decimals=decimals,
            min_value=minimum,
            max_value=maximum,
            disabled=bool(disabled),
            sync_token=int(sync_token),
            aria_label=str(aria_label or "Valore numerico"),
            compact_label=str(compact_label or ""),
            unit=str(unit or ""),
            help_enabled=help_enabled,
            help_state_key=help_state_key,
            suggest_enabled=bool(suggest_enabled),
            suggest_label=str(suggest_label or ""),
            suggest_active=bool(suggest_active),
            on_suggest=on_suggest,
            on_change=on_change,
            key=key,
        )
    else:
        result = _component(
            value=current,
            step=float(step),
            decimals=decimals,
            min_value=minimum,
            max_value=maximum,
            disabled=bool(disabled),
            sync_token=int(sync_token),
            aria_label=str(aria_label or "Valore numerico"),
            compact_mobile=compact_mobile,
            compact_label=str(compact_label or ""),
            unit=str(unit or ""),
            help_enabled=help_enabled,
            hide_group_heading=bool(hide_group_heading),
            inline_weight_toggle=bool(inline_weight_toggle),
            suggest_enabled=bool(suggest_enabled),
            suggest_label=str(suggest_label or ""),
            suggest_active=bool(suggest_active),
            primary_color=_theme_value("theme.primaryColor", "#168AC1"),
            background_color=_theme_value("theme.secondaryBackgroundColor", "#F0F2F6"),
            text_color=_theme_value("theme.textColor", "#31333F"),
            key=key,
            on_change=on_change,
            default=current,
        )

    if isinstance(result, dict):
        suggest_token = result.get("suggest_token")
        if suggest_token is not None and callable(on_suggest):
            event_key = f"__decimal_suggest_event_{key or aria_label}"
            if st.session_state.get(event_key) != suggest_token:
                st.session_state[event_key] = suggest_token
                on_suggest()

        help_token = result.get("help_token")
        if help_token is not None and help_enabled:
            event_key = f"__decimal_help_event_{key or aria_label}"
            if st.session_state.get(event_key) != help_token:
                st.session_state[event_key] = help_token
                st.session_state[help_state_key] = not bool(
                    st.session_state.get(help_state_key, False)
                )

        result = result.get("value", current)

    if result is None:
        parsed_result = None
    else:
        parsed_result = _finite_float(result)
        if parsed_result is None:
            parsed_result = current
        if parsed_result is not None and minimum is not None:
            parsed_result = max(minimum, parsed_result)
        if parsed_result is not None and maximum is not None:
            parsed_result = min(maximum, parsed_result)
        if parsed_result is not None:
            parsed_result = round(parsed_result, decimals)

    if help_enabled and st.session_state.get(help_state_key, False):
        note_key = "ta_range_help_note" if interval_mode else "ta_standard_help_note"
        with st.container(key=note_key):
            st.caption(help_text)

    return parsed_result
