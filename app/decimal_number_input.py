# -*- coding: utf-8 -*-
"""Input numerico decimale con punto e controlli integrati per Mor-tem."""

import math
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


_FRONTEND_DIR = (Path(__file__).resolve().parent / "decimal_number_input_frontend").absolute()
_component = components.declare_component(
    "mortem_decimal_number_input",
    path=str(_FRONTEND_DIR),
)
_FORMAT_RE = re.compile(r"^%\.(\d+)f$")


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
    on_change=None,
    key=None,
):
    """Restituisce float/None usando un controllo decimale non localizzato."""
    decimals = _decimal_places(format, step)
    current = _finite_float(value)
    minimum = _finite_float(min_value)
    maximum = _finite_float(max_value)

    result = _component(
        value=current,
        step=float(step),
        decimals=decimals,
        min_value=minimum,
        max_value=maximum,
        disabled=bool(disabled),
        sync_token=int(sync_token),
        aria_label=str(aria_label or "Valore numerico"),
        compact_mobile=bool(compact_mobile),
        compact_label=str(compact_label or ""),
        unit=str(unit or ""),
        hide_group_heading=bool(hide_group_heading),
        inline_weight_toggle=bool(inline_weight_toggle),
        primary_color=_theme_value("theme.primaryColor", "#168AC1"),
        background_color=_theme_value("theme.secondaryBackgroundColor", "#F0F2F6"),
        text_color=_theme_value("theme.textColor", "#31333F"),
        key=key,
        on_change=on_change,
        default=current,
    )

    if result is None:
        return None

    parsed = _finite_float(result)
    if parsed is None:
        return current
    if minimum is not None:
        parsed = max(minimum, parsed)
    if maximum is not None:
        parsed = min(maximum, parsed)
    return round(parsed, decimals)
