# -*- coding: utf-8 -*-
"""Confine dei testi tanatologici italiani.

Questo modulo espone descrizioni e nomi brevi tramite ID stabili. Durante la
fase di transizione i valori italiani vengono letti dai dizionari legacy di
``app.parameters``: il contenuto testuale resta quindi identico, mentre i
consumatori non devono più conoscere le chiavi italiane.
"""

from __future__ import annotations

from app.parameters import (
    testi_macchie,
    rigidita_descrizioni,
    dati_parametri_aggiuntivi,
    nomi_brevi,
)
from app.tanatology_states import (
    LIVOR_LABEL_IT,
    RIGOR_LABEL_IT,
    LIVOR_ID_BY_LEGACY_LABEL,
    RIGOR_ID_BY_LEGACY_LABEL,
)
from app.special_tanatology_states import (
    SPECIAL_PARAM_LABEL_IT,
    SPECIAL_OPTION_LABEL_IT,
)


LIVOR_DESCRIPTION_IT_BY_ID = {
    state_id: testi_macchie.get(label)
    for state_id, label in LIVOR_LABEL_IT.items()
}

RIGOR_DESCRIPTION_IT_BY_ID = {
    state_id: rigidita_descrizioni.get(label)
    for state_id, label in RIGOR_LABEL_IT.items()
}

SPECIAL_DESCRIPTION_IT_BY_ID = {
    param_id: {
        option_id: dati_parametri_aggiuntivi[param_label]["descrizioni"].get(option_label)
        for option_id, option_label in SPECIAL_OPTION_LABEL_IT[param_id].items()
    }
    for param_id, param_label in SPECIAL_PARAM_LABEL_IT.items()
}

SPECIAL_GRAPH_LABEL_IT_BY_ID = {
    param_id: nomi_brevi.get(param_label, param_label)
    for param_id, param_label in SPECIAL_PARAM_LABEL_IT.items()
}


def livor_description_it(state_id: str):
    return LIVOR_DESCRIPTION_IT_BY_ID.get(state_id)


def rigor_description_it(state_id: str):
    return RIGOR_DESCRIPTION_IT_BY_ID.get(state_id)


def livor_description_from_legacy_it(legacy_label: str):
    state_id = LIVOR_ID_BY_LEGACY_LABEL.get(legacy_label)
    return LIVOR_DESCRIPTION_IT_BY_ID.get(state_id)


def rigor_description_from_legacy_it(legacy_label: str):
    state_id = RIGOR_ID_BY_LEGACY_LABEL.get(legacy_label)
    return RIGOR_DESCRIPTION_IT_BY_ID.get(state_id)


def special_description_it(param_id: str, option_id: str):
    return SPECIAL_DESCRIPTION_IT_BY_ID[param_id].get(option_id)


def special_graph_label_it(param_id: str):
    return SPECIAL_GRAPH_LABEL_IT_BY_ID[param_id]


__all__ = [
    "LIVOR_DESCRIPTION_IT_BY_ID",
    "RIGOR_DESCRIPTION_IT_BY_ID",
    "SPECIAL_DESCRIPTION_IT_BY_ID",
    "SPECIAL_GRAPH_LABEL_IT_BY_ID",
    "livor_description_it",
    "rigor_description_it",
    "livor_description_from_legacy_it",
    "rigor_description_from_legacy_it",
    "special_description_it",
    "special_graph_label_it",
]
