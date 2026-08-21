# -*- coding: utf-8 -*-
"""Adattatori localizzati per il pannello FC dell'interfaccia MSIL.

Il modulo mantiene distinta la presentazione MSIL dalla UI completa e converte
le etichette mostrate negli stessi valori legacy già attesi da ``factor_calc``.
Non contiene formule, soglie o regole di calcolo.
"""

from __future__ import annotations

from typing import Dict, Optional

from app import i18n
from app.factor_ui_states import (
    BODY_LABEL_IT,
    BODY_LEGACY_VALUE,
    WATER_LABEL_IT,
    WATER_LEGACY_VALUE,
    MSIL_CLOTHING_LABEL_IT,
)
from app.surface_ui_states import SURFACE_LABEL_IT


# Mappe italiane statiche mantenute come compatibilità legacy.
MSIL_BODY_STATE_BY_LABEL: Dict[str, str] = {
    i18n.body_label(state_id): state_id for state_id in BODY_LABEL_IT
}

MSIL_WATER_STATE_BY_LABEL: Dict[str, str] = {
    i18n.water_label(state_id): state_id for state_id in WATER_LABEL_IT
}

MSIL_SURFACE_STATE_BY_LABEL: Dict[str, str] = {
    i18n.surface_label(surface_id): surface_id for surface_id in SURFACE_LABEL_IT
}


def msil_body_labels(language: Optional[str] = None):
    return tuple(i18n.body_label(state_id, language) for state_id in BODY_LABEL_IT)


def msil_body_state_id(ui_label: str, language: Optional[str] = None) -> str:
    state_by_label = {
        i18n.body_label(state_id, language): state_id
        for state_id in BODY_LABEL_IT
    }
    return state_by_label[ui_label]


def msil_body_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    return BODY_LEGACY_VALUE[msil_body_state_id(ui_label, language)]


def msil_water_labels(language: Optional[str] = None):
    return tuple(i18n.water_label(state_id, language) for state_id in WATER_LABEL_IT)


def msil_water_state_id(ui_label: str, language: Optional[str] = None) -> str:
    state_by_label = {
        i18n.water_label(state_id, language): state_id
        for state_id in WATER_LABEL_IT
    }
    return state_by_label[ui_label]


def msil_water_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    return WATER_LEGACY_VALUE[msil_water_state_id(ui_label, language)]


def msil_clothing_label(category_id: str, language: Optional[str] = None) -> str:
    if category_id not in MSIL_CLOTHING_LABEL_IT:
        raise KeyError(category_id)
    return i18n.msil_clothing_label(category_id, language)


def msil_surface_labels(language: Optional[str] = None):
    return tuple(i18n.surface_label(surface_id, language) for surface_id in SURFACE_LABEL_IT)


def msil_surface_label(surface_id: str, language: Optional[str] = None) -> str:
    if surface_id not in SURFACE_LABEL_IT:
        raise KeyError(surface_id)
    return i18n.surface_label(surface_id, language)


def msil_surface_state_id(ui_label: str, language: Optional[str] = None) -> str:
    state_by_label = {
        i18n.surface_label(surface_id, language): surface_id
        for surface_id in SURFACE_LABEL_IT
    }
    return state_by_label[ui_label]


def msil_surface_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    return SURFACE_LABEL_IT[msil_surface_state_id(ui_label, language)]


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
