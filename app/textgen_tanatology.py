# -*- coding: utf-8 -*-
"""Helper tanatologici per la generazione testuale.

La decisione se mostrare una descrizione di un parametro tanatologico speciale
viene espressa tramite ID stabili. Il fallback sulle etichette legacy mantiene
la compatibilità con strutture non ancora riconducibili agli ID.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from app.special_tanatology_states import (
    OPTION_NOT_ASSESSED,
    OPTION_UNRELIABLE,
    SPECIAL_PARAM_ID_BY_LEGACY_LABEL,
    SPECIAL_OPTION_ID_BY_LEGACY_LABEL,
)


NON_REPORTABLE_SPECIAL_STATE_IDS = frozenset({
    OPTION_NOT_ASSESSED,
    OPTION_UNRELIABLE,
})

# Compatibilità temporanea per strutture non riconducibili agli ID stabili.
_NON_REPORTABLE_LEGACY_LABELS = frozenset({
    "Non valutata",
    "Non valutabile/non attendibile",
})


def resolve_special_state_id(parameter: Mapping[str, Any]) -> Optional[str]:
    """Ricava lo stato stabile da ``stato_id`` o dalla coppia legacy nome/stato."""
    state_id = parameter.get("stato_id")
    if state_id is not None:
        return state_id

    parameter_id = SPECIAL_PARAM_ID_BY_LEGACY_LABEL.get(parameter.get("nome"))
    if parameter_id is None:
        return None

    return SPECIAL_OPTION_ID_BY_LEGACY_LABEL[parameter_id].get(parameter.get("stato", ""))


def special_description_is_reportable(parameter: Mapping[str, Any]) -> bool:
    """True se la descrizione del parametro speciale deve essere mostrata.

    Quando lo stato è riconoscibile usa l'ID stabile. Solo per strutture non
    riconosciute replica il controllo legacy sulle due etichette italiane.
    """
    state_id = resolve_special_state_id(parameter)
    if state_id is not None:
        return state_id not in NON_REPORTABLE_SPECIAL_STATE_IDS

    legacy_state = parameter.get("stato", "")
    return legacy_state not in _NON_REPORTABLE_LEGACY_LABELS


__all__ = [
    "NON_REPORTABLE_SPECIAL_STATE_IDS",
    "resolve_special_state_id",
    "special_description_is_reportable",
]
