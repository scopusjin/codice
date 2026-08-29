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


def _install_mobile_overlay_css():
    """Fa aprire la rotella sopra il layout senza rialzare la riga Streamlit."""
    if getattr(st, "_native_time_picker_overlay_css_installed", False):
        return

    st.markdown(
        """
        <style>
        @media (max-width: 768px) {
          [data-testid="stElementContainer"]:has(iframe[title*="mortem_native_time_picker"]),
          [data-testid="stCustomComponentV1"]:has(iframe[title*="mortem_native_time_picker"]) {
            position: relative !important;
            height: 40px !important;
            min-height: 40px !important;
            overflow: visible !important;
            z-index: 50 !important;
          }

          [data-testid="stColumn"]:has(iframe[title*="mortem_native_time_picker"]) {
            overflow: visible !important;
            position: relative !important;
            z-index: 50 !important;
          }

          iframe[title*="mortem_native_time_picker"] {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            z-index: 1000 !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st._native_time_picker_overlay_css_installed = True


def _theme_value(option, fallback):
    try:
        value = st.get_option(option)
    except Exception:
        value = None
    return value or fallback


def native_time_picker(value="00:00", *, key=None):
    """Restituisce un orario HH:MM; ruote touch solo sulla Full mobile."""
    _install_mobile_overlay_css()

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
