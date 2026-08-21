# -*- coding: utf-8 -*-
"""Adattatori localizzati per il pannello del fattore di correzione completo.

Il modulo separa le etichette mostrate dalla UI dai valori legacy ancora attesi
da ``app.factor_calc``. Non contiene formule, soglie o regole di calcolo.
"""

from __future__ import annotations

from typing import Dict

from app import i18n
from app.factor_ui_states import (
    BODY_LABEL_IT,
    BODY_LEGACY_VALUE,
    WATER_LABEL_IT,
    WATER_LEGACY_VALUE,
    FULL_CLOTHING_LABEL_IT,
)
from app.surface_ui_states import SURFACE_LABEL_IT


FULL_BODY_STATE_BY_LABEL: Dict[str, str] = {
    i18n.body_label(state_id): state_id for state_id in BODY_LABEL_IT
}

FULL_WATER_STATE_BY_LABEL: Dict[str, str] = {
    i18n.water_label(state_id): state_id for state_id in WATER_LABEL_IT
}

FULL_SURFACE_STATE_BY_LABEL: Dict[str, str] = {
    i18n.surface_label(surface_id): surface_id for surface_id in SURFACE_LABEL_IT
}


def full_body_labels():
    """Etichette localizzate degli stati del corpo nell'ordine corrente."""
    return tuple(FULL_BODY_STATE_BY_LABEL.keys())


def full_body_state_id(ui_label: str) -> str:
    """Restituisce l'ID stabile dello stato del corpo mostrato nella UI."""
    return FULL_BODY_STATE_BY_LABEL[ui_label]


def full_body_legacy_value(ui_label: str) -> str:
    """Restituisce il valore legacy dello stato del corpo atteso dal motore."""
    return BODY_LEGACY_VALUE[full_body_state_id(ui_label)]


def full_water_labels():
    """Etichette localizzate dei tipi di acqua nell'ordine corrente."""
    return tuple(FULL_WATER_STATE_BY_LABEL.keys())


def full_water_state_id(ui_label: str) -> str:
    """Restituisce l'ID stabile del tipo di acqua mostrato nella UI."""
    return FULL_WATER_STATE_BY_LABEL[ui_label]


def full_water_legacy_value(ui_label: str) -> str:
    """Restituisce il valore legacy del tipo di acqua atteso dal motore."""
    return WATER_LEGACY_VALUE[full_water_state_id(ui_label)]


def full_clothing_label(category_id: str) -> str:
    """Etichetta localizzata di una categoria di indumenti/coperture."""
    if category_id not in FULL_CLOTHING_LABEL_IT:
        raise KeyError(category_id)
    return i18n.full_clothing_label(category_id)


def full_surface_labels():
    """Etichette localizzate delle superfici nell'ordine corrente."""
    return tuple(FULL_SURFACE_STATE_BY_LABEL.keys())


def full_surface_state_id(ui_label: str) -> str:
    """Restituisce l'ID stabile della superficie mostrata nella UI."""
    return FULL_SURFACE_STATE_BY_LABEL[ui_label]


def full_surface_legacy_value(ui_label: str) -> str:
    """Restituisce la stringa legacy della superficie attesa dal motore."""
    return SURFACE_LABEL_IT[full_surface_state_id(ui_label)]


__all__ = [
    "FULL_BODY_STATE_BY_LABEL",
    "FULL_WATER_STATE_BY_LABEL",
    "FULL_SURFACE_STATE_BY_LABEL",
    "full_body_labels",
    "full_body_state_id",
    "full_body_legacy_value",
    "full_water_labels",
    "full_water_state_id",
    "full_water_legacy_value",
    "full_clothing_label",
    "full_surface_labels",
    "full_surface_state_id",
    "full_surface_legacy_value",
]
