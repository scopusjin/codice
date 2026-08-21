# -*- coding: utf-8 -*-
"""Adattatori degli stati tanatologici usati dall'interfaccia MSIL.

Il modulo separa le etichette semplificate mostrate nella pagina MSIL dagli
identificatori interni stabili. Le funzioni ``*_legacy_value`` restituiscono
esattamente le stringhe italiane attualmente attese dal codice esistente.

Nessun range, testo medico-legale o criterio di calcolo è definito qui.
"""

from __future__ import annotations

from typing import Dict

from app.locales.it_msil import (
    MSIL_LIVOR_LABEL_IT_BY_ID,
    MSIL_RIGOR_LABEL_IT_BY_ID,
)
from app.tanatology_states import livor_legacy_label, rigor_legacy_label


# Etichetta mostrata nella UI MSIL -> identificatore interno stabile.
MSIL_LIVOR_STATE_BY_LABEL: Dict[str, str] = {
    label: state_id for state_id, label in MSIL_LIVOR_LABEL_IT_BY_ID.items()
}

MSIL_RIGOR_STATE_BY_LABEL: Dict[str, str] = {
    label: state_id for state_id, label in MSIL_RIGOR_LABEL_IT_BY_ID.items()
}


def msil_livor_state_id(ui_label: str) -> str:
    """Restituisce l'ID stabile associato a una voce della UI MSIL."""
    return MSIL_LIVOR_STATE_BY_LABEL[ui_label]


def msil_rigor_state_id(ui_label: str) -> str:
    """Restituisce l'ID stabile associato a una voce della UI MSIL."""
    return MSIL_RIGOR_STATE_BY_LABEL[ui_label]


def msil_livor_legacy_value(ui_label: str) -> str:
    """Restituisce il valore legacy che App_MSIL passa oggi al motore."""
    return livor_legacy_label(msil_livor_state_id(ui_label))


def msil_rigor_legacy_value(ui_label: str) -> str:
    """Restituisce il valore legacy che App_MSIL passa oggi al motore."""
    return rigor_legacy_label(msil_rigor_state_id(ui_label))


__all__ = [
    "MSIL_LIVOR_STATE_BY_LABEL",
    "MSIL_RIGOR_STATE_BY_LABEL",
    "msil_livor_state_id",
    "msil_rigor_state_id",
    "msil_livor_legacy_value",
    "msil_rigor_legacy_value",
]
