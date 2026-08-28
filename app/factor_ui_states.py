# -*- coding: utf-8 -*-
"""Identificatori UI stabili per il pannello del fattore di correzione.

Questo modulo separa le etichette mostrate all'utente dai valori legacy che
``app.factor_calc`` riceve attualmente. Non contiene formule, soglie o regole
di calcolo.
"""

from __future__ import annotations

from typing import Dict


# -----------------------------------------------------------------------------
# Stato del corpo
# -----------------------------------------------------------------------------
BODY_DRY = "body_dry"
BODY_WET = "body_wet"
BODY_IMMERSED = "body_immersed"

BODY_LABEL_IT: Dict[str, str] = {
    BODY_DRY: "Corpo asciutto",
    BODY_WET: "Bagnato",
    BODY_IMMERSED: "Immerso",
}

BODY_LEGACY_VALUE: Dict[str, str] = {
    BODY_DRY: "Asciutto",
    BODY_WET: "Bagnato",
    BODY_IMMERSED: "Immerso",
}

BODY_ID_BY_LABEL_IT: Dict[str, str] = {
    label: state_id for state_id, label in BODY_LABEL_IT.items()
}


# -----------------------------------------------------------------------------
# Tipo di acqua
# -----------------------------------------------------------------------------
WATER_STILL = "water_still"
WATER_FLOWING = "water_flowing"

WATER_LABEL_IT: Dict[str, str] = {
    WATER_STILL: "In acqua stagnante",
    WATER_FLOWING: "In acqua corrente",
}

WATER_LEGACY_VALUE: Dict[str, str] = {
    WATER_STILL: "stagnante",
    WATER_FLOWING: "corrente",
}

WATER_ID_BY_LABEL_IT: Dict[str, str] = {
    label: state_id for state_id, label in WATER_LABEL_IT.items()
}


# -----------------------------------------------------------------------------
# Categorie di indumenti/coperture
# -----------------------------------------------------------------------------
LAYER_THIN = "layer_thin"
LAYER_THICK = "layer_thick"
BLANKET_MEDIUM = "blanket_medium"
BLANKET_HEAVY = "blanket_heavy"

FULL_CLOTHING_LABEL_IT: Dict[str, str] = {
    LAYER_THIN: "Strati leggeri (indumenti o teli sottili)",
    LAYER_THICK: "Strati pesanti (indumenti o teli spessi)",
    BLANKET_MEDIUM: "Coperta / copriletto spesso",
    BLANKET_HEAVY: "Piumone / coperta molto spessa",
}

MSIL_CLOTHING_LABEL_IT: Dict[str, str] = {
    LAYER_THIN: "Strati leggeri (indumenti o teli sottili)",
    LAYER_THICK: "Strati pesanti (indumenti o teli spessi)",
    BLANKET_MEDIUM: "Coperte di medio spessore",
    BLANKET_HEAVY: "Coperte pesanti/Mantelline termiche",
}


# -----------------------------------------------------------------------------
# Adattatori verso il comportamento esistente
# -----------------------------------------------------------------------------
def body_state_id(ui_label: str) -> str:
    return BODY_ID_BY_LABEL_IT[ui_label]


def body_legacy_value(ui_label: str) -> str:
    return BODY_LEGACY_VALUE[body_state_id(ui_label)]


def water_state_id(ui_label: str) -> str:
    return WATER_ID_BY_LABEL_IT[ui_label]


def water_legacy_value(ui_label: str) -> str:
    return WATER_LEGACY_VALUE[water_state_id(ui_label)]


__all__ = [
    "BODY_DRY",
    "BODY_WET",
    "BODY_IMMERSED",
    "BODY_LABEL_IT",
    "BODY_LEGACY_VALUE",
    "BODY_ID_BY_LABEL_IT",
    "WATER_STILL",
    "WATER_FLOWING",
    "WATER_LABEL_IT",
    "WATER_LEGACY_VALUE",
    "WATER_ID_BY_LABEL_IT",
    "LAYER_THIN",
    "LAYER_THICK",
    "BLANKET_MEDIUM",
    "BLANKET_HEAVY",
    "FULL_CLOTHING_LABEL_IT",
    "MSIL_CLOTHING_LABEL_IT",
    "body_state_id",
    "body_legacy_value",
    "water_state_id",
    "water_legacy_value",
]
