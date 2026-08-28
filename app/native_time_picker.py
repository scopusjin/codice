# -*- coding: utf-8 -*-
"""Picker orario personalizzato per Mor-tem."""

import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from app.device_mode import full_device_is_mobile


_FRONTEND_DIR = (Path(__file__).resolve().parent / "native_time_picker_frontend").absolute()
_component = components.declare_component(
    "mortem_native_time_picker",
    path=str(_FRONTEND_DIR),
)
_TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


def _theme_value(option, fallback):
    try:
        value = st.get_option(option)
    except Exception:
        value = None
    return value or fallback


def native_time_picker(value="00:00", *, key=None):
    """Restituisce un orario HH:MM; ruote touch solo sulla Full mobile."""
    if not isinstance(value, str) or not _TIME_RE.fullmatch(value.strip()):
        value = "00:00"
    else:
        value = value.strip()

    result = _component(
        value=value,
        mobile=full_device_is_mobile(),
        primary_color=_theme_value("theme.primaryColor", "#168AC1"),
        background_color=_theme_value("theme.secondaryBackgroundColor", "#F0F2F6"),
        text_color=_theme_value("theme.textColor", "#31333F"),
        key=key,
        default=value,
    )

    if isinstance(result, str) and _TIME_RE.fullmatch(result):
        return result
    return value
