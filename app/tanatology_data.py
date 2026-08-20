# -*- coding: utf-8 -*-
"""Viste dei range tanatologici indicizzate con ID stabili.

I valori restano definiti esclusivamente in ``app.parameters``. Questo modulo
li espone tramite gli identificatori di ``app.tanatology_states`` senza
riscrivere, correggere o completare i dati esistenti.
"""

from __future__ import annotations

from app.parameters import (
    opzioni_macchie,
    macchie_medi,
    opzioni_rigidita,
    rigidita_medi,
)
from app.tanatology_states import livor_state_id, rigor_state_id


LIVOR_RANGES_BY_ID = {
    livor_state_id(label): value
    for label, value in opzioni_macchie.items()
}

LIVOR_TYPICAL_RANGES_BY_ID = {
    livor_state_id(label): value
    for label, value in macchie_medi.items()
}

RIGOR_RANGES_BY_ID = {
    rigor_state_id(label): value
    for label, value in opzioni_rigidita.items()
}

# Mantiene esattamente l'insieme di chiavi presente oggi in rigidita_medi.
# Non viene aggiunta artificialmente l'opzione "Non valutabile/Non attendibile".
RIGOR_TYPICAL_RANGES_BY_ID = {
    rigor_state_id(label): value
    for label, value in rigidita_medi.items()
}


__all__ = [
    "LIVOR_RANGES_BY_ID",
    "LIVOR_TYPICAL_RANGES_BY_ID",
    "RIGOR_RANGES_BY_ID",
    "RIGOR_TYPICAL_RANGES_BY_ID",
]
