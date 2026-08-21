# -*- coding: utf-8 -*-
"""Adattatori degli stati tanatologici per l'interfaccia completa.

La pagina completa mostra attualmente direttamente le etichette italiane legacy.
Questo modulo introduce un passaggio esplicito tra etichetta UI e identificatore
interno stabile, mantenendo invariato il valore passato al codice esistente.

Nessun range, criterio medico-legale o calcolo è definito o modificato qui.
"""

from __future__ import annotations

from typing import Dict

from app import i18n
from app.tanatology_states import (
    LIVOR_LABEL_IT,
    RIGOR_LABEL_IT,
    livor_legacy_label,
    rigor_legacy_label,
)


# Etichetta mostrata nella UI completa -> identificatore interno stabile.
# L'ordine segue quello già definito in tanatology_states.py e riproduce
# l'ordine attuale dei menu della pagina completa.
FULL_LIVOR_STATE_BY_LABEL: Dict[str, str] = {
    i18n.livor_label(state_id): state_id for state_id in LIVOR_LABEL_IT
}

FULL_RIGOR_STATE_BY_LABEL: Dict[str, str] = {
    i18n.rigor_label(state_id): state_id for state_id in RIGOR_LABEL_IT
}


def full_livor_state_id(ui_label: str) -> str:
    """Restituisce l'ID stabile associato a una voce della UI completa."""
    return FULL_LIVOR_STATE_BY_LABEL[ui_label]


def full_rigor_state_id(ui_label: str) -> str:
    """Restituisce l'ID stabile associato a una voce della UI completa."""
    return FULL_RIGOR_STATE_BY_LABEL[ui_label]


def full_livor_legacy_value(ui_label: str) -> str:
    """Restituisce il valore legacy attualmente atteso dal motore."""
    return livor_legacy_label(full_livor_state_id(ui_label))


def full_rigor_legacy_value(ui_label: str) -> str:
    """Restituisce il valore legacy attualmente atteso dal motore."""
    return rigor_legacy_label(full_rigor_state_id(ui_label))


__all__ = [
    "FULL_LIVOR_STATE_BY_LABEL",
    "FULL_RIGOR_STATE_BY_LABEL",
    "full_livor_state_id",
    "full_rigor_state_id",
    "full_livor_legacy_value",
    "full_rigor_legacy_value",
]
