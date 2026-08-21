# -*- coding: utf-8 -*-
"""Adattatori localizzati per il pannello FC dell'interfaccia MSIL.

Il modulo mantiene distinta la presentazione MSIL dalla UI completa e converte
le etichette mostrate negli stessi valori legacy già attesi da ``factor_calc``.
Non contiene formule, soglie o regole di calcolo.
"""

from __future__ import annotations

from typing import Dict

from app import i18n
from app.factor_ui_states import (
    BODY_LABEL_IT,
    BODY_LEGACY_VALUE,
    WATER_LABEL_IT,
    WATER_LEGACY_VALUE,
    MSIL_CLOTHING_LABEL_IT,
)
from app.surface_ui_states import SURFACE_LABEL_IT


MSIL_BODY_STATE_BY_LABEL: Dict[str, str] = {
    i18n.body_label(state_id): state_id for state_id in BODY_LABEL_IT
}

MSIL_WATER_STATE_BY_LABEL: Dict[str, str] = {
    i18n.water_label(state_id): state_id for state_id in WATER_LABEL_IT
}

MSIL_SURFACE_STATE_BY_LABEL: Dict[str, str] = {
    i18n.surface_label(surface_id): surface_id for surface_id in SURFACE_LABEL_IT
}


def msil_body_labels():
    return tuple(MSIL_BODY_STATE_BY_LABEL.keys())


def msil_body_state_id(ui_label: str) -> str:
    return MSIL_BODY_STATE_BY_LABEL[ui_label]


def msil_body_legacy_value(ui_label: str) -> str:
    return BODY_LEGACY_VALUE[msil_body_state_id(ui_label)]


def msil_water_labels():
    return tuple(MSIL_WATER_STATE_BY_LABEL.keys())


def msil_water_state_id(ui_label: str) -> str:
    return MSIL_WATER_STATE_BY_LABEL[ui_label]


def msil_water_legacy_value(ui_label: str) -> str:
    return WATER_LEGACY_VALUE[msil_water_state_id(ui_label)]


def msil_clothing_label(category_id: str) -> str:
    if category_id not in MSIL_CLOTHING_LABEL_IT:
        raise KeyError(category_id)
    return i18n.msil_clothing_label(category_id)


def msil_surface_labels():
    return tuple(MSIL_SURFACE_STATE_BY_LABEL.keys())


def msil_surface_label(surface_id: str) -> str:
    if surface_id not in SURFACE_LABEL_IT:
        raise KeyError(surface_id)
    return i18n.surface_label(surface_id)


def msil_surface_state_id(ui_label: str) -> str:
    return MSIL_SURFACE_STATE_BY_LABEL[ui_label]


def msil_surface_legacy_value(ui_label: str) -> str:
    return SURFACE_LABEL_IT[msil_surface_state_id(ui_label)]


__all__ = [
    "MSIL_BODY_STATE_BY_LABEL",
    "MSIL_WATER_STATE_BY_LABEL",
    "MSIL_SURFACE_STATE_BY_LABEL",
    "msil_body_labels",
    "msil_body_state_id",
    "msil_body_legacy_value",
    "msil_water_labels",
    "msil_water_state_id",
    "msil_water_legacy_value",
    "msil_clothing_label",
    "msil_surface_labels",
    "msil_surface_label",
    "msil_surface_state_id",
    "msil_surface_legacy_value",
]
