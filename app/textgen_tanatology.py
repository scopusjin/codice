# -*- coding: utf-8 -*-
"""Helper tanatologici per la generazione testuale.

La decisione se mostrare una descrizione di un parametro tanatologico speciale
viene espressa tramite ID stabili. Il fallback sulle etichette legacy mantiene
la compatibilità con i chiamanti che non passano ancora ``stato_id``.
"""

from __future__ import annotations

from typing import Any, Mapping

from app.special_tanatology_states import (
    OPTION_NOT_ASSESSED,
    OPTION_UNRELIABLE,
)


NON_REPORTABLE_SPECIAL_STATE_IDS = frozenset({
    OPTION_NOT_ASSESSED,
    OPTION_UNRELIABLE,
})

# Compatibilità temporanea per strutture legacy prive di stato_id.
_NON_REPORTABLE_LEGACY_LABELS = frozenset({
    "Non valutata",
    "Non valutabile/non attendibile",
})


def special_description_is_reportable(parameter: Mapping[str, Any]) -> bool:
    """True se la descrizione del parametro speciale deve essere mostrata.

    Se è disponibile ``stato_id`` usa esclusivamente l'ID stabile. In assenza
    dell'ID replica il controllo legacy sulle due etichette italiane correnti.
    """
    state_id = parameter.get("stato_id")
    if state_id is not None:
        return state_id not in NON_REPORTABLE_SPECIAL_STATE_IDS

    legacy_state = parameter.get("stato", "")
    return legacy_state not in _NON_REPORTABLE_LEGACY_LABELS


__all__ = [
    "NON_REPORTABLE_SPECIAL_STATE_IDS",
    "special_description_is_reportable",
]
