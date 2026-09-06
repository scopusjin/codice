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
EMPTY_TIME_SENTINEL = "__mortem_empty_time__"


def _theme_value(option, fallback):
    try:
        value = st.get_option(option)
    except Exception:
        value = None
    return value or fallback


def _inherited_background_color():
    base = str(_theme_value("theme.base", "light")).lower()
    return "#3b2a00" if base == "dark" else "#fff3cd"


def _full_datetime_component(key) -> bool:
    if not st.session_state.get("__full_datetime_always_visible", False):
        return False
    return isinstance(key, str) and (
        key == "input_ora_rilievo_native" or key.endswith("_ora_native")
    )


def native_time_picker(
    value="00:00",
    *,
    key=None,
    inherited=False,
    allow_empty=False,
    open_default_now=False,
):
    """Restituisce un orario HH:MM con selettore a ghiere nella Full.

    Nella Full con data/ora sempre visibili il campo può restare vuoto. In quel
    caso l'apertura delle ghiere parte dall'ora locale del browser senza
    registrarla finché l'utente non preme «Imposta». Su desktop restano inoltre
    disponibili digitazione, frecce da tastiera e rotellina.
    """
    full_datetime = _full_datetime_component(key)
    main_datetime = full_datetime and key == "input_ora_rilievo_native"
    mobile = full_device_is_mobile()
    picker_enabled = bool(mobile or full_datetime)
    overlay_picker = bool(mobile or full_datetime)
    allow_empty = bool(allow_empty or full_datetime)
    open_default_now = bool(open_default_now or full_datetime)

    if value == EMPTY_TIME_SENTINEL:
        value = ""

    # I parametri speciali ereditano anche il vuoto del rilievo principale.
    # Il codice legacy passa "00:00" come fallback: qui lo neutralizziamo solo
    # quando il campo è ancora ereditato, senza toccare un valore già manuale.
    if full_datetime and not main_datetime and inherited:
        main_value = st.session_state.get("input_ora_rilievo")
        if main_value in (None, "", EMPTY_TIME_SENTINEL):
            value = ""

    if isinstance(value, str):
        value = value.strip()
    else:
        value = ""

    if not _TIME_RE.fullmatch(value):
        value = "" if allow_empty else "00:00"

    inherited_state = bool(inherited) or (main_datetime and value == "")

    result = _component(
        value=value,
        mobile=mobile,
        picker_enabled=picker_enabled,
        overlay_picker=overlay_picker,
        # Compatibilità con il frontend precedente durante un deploy progressivo.
        overlay_mobile=overlay_picker,
        primary_color=_theme_value("theme.primaryColor", "#168AC1"),
        background_color=_theme_value("theme.secondaryBackgroundColor", "#F0F2F6"),
        text_color=_theme_value("theme.textColor", "#31333F"),
        inherited=inherited_state,
        inherited_background_color=_inherited_background_color(),
        allow_empty=allow_empty,
        open_default_now=open_default_now,
        key=key,
        default=value,
    )

    if allow_empty and result == "":
        # La pagina Full legacy usa la truthiness di input_ora_rilievo per
        # decidere se sostituire il vuoto con 00:00. Manteniamo quindi una
        # sentinella interna, mentre il componente continua a mostrare il campo
        # realmente vuoto. Per gli orari speciali ereditati la stessa sentinella
        # evita che il fallback legacy 00:00 li trasformi in valori manuali.
        if main_datetime:
            return EMPTY_TIME_SENTINEL
        if full_datetime and inherited:
            main_value = st.session_state.get("input_ora_rilievo")
            if main_value in (None, "", EMPTY_TIME_SENTINEL):
                return EMPTY_TIME_SENTINEL
        return ""
    if isinstance(result, str) and _TIME_RE.fullmatch(result):
        return result
    if main_datetime and value == "":
        return EMPTY_TIME_SENTINEL
    return value
