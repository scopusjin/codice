# -*- coding: utf-8 -*-
"""Adattatori degli stati tanatologici per l'interfaccia completa.

La pagina completa mostra attualmente direttamente le etichette italiane legacy.
Questo modulo introduce un passaggio esplicito tra etichetta UI e identificatore
interno stabile, mantenendo invariato il valore passato al codice esistente.

Nessun range, criterio medico-legale o calcolo è definito o modificato qui.
"""

from __future__ import annotations

from typing import Dict, Optional

from app import i18n
from app.tanatology_states import (
    LIVOR_LABEL_IT,
    RIGOR_LABEL_IT,
    livor_legacy_label,
    rigor_legacy_label,
)
from app.special_tanatology_states import (
    SPECIAL_PARAM_LABEL_IT,
    special_param_legacy_label,
    special_option_ids,
    special_option_legacy_label,
)


# Mappe italiane statiche mantenute come compatibilità legacy.
# Le funzioni sottostanti ricostruiscono invece le etichette in base alla lingua
# richiesta, così la UI non resta vincolata ai valori calcolati all'importazione.
FULL_LIVOR_STATE_BY_LABEL: Dict[str, str] = {
    i18n.livor_label(state_id): state_id for state_id in LIVOR_LABEL_IT
}

FULL_RIGOR_STATE_BY_LABEL: Dict[str, str] = {
    i18n.rigor_label(state_id): state_id for state_id in RIGOR_LABEL_IT
}

FULL_SPECIAL_PARAM_BY_LABEL: Dict[str, str] = {
    i18n.special_parameter_label(param_id): param_id
    for param_id in SPECIAL_PARAM_LABEL_IT
}


def full_livor_labels(language: Optional[str] = None):
    """Etichette localizzate delle ipostasi nell'identico ordine corrente."""
    return tuple(i18n.livor_label(state_id, language) for state_id in LIVOR_LABEL_IT)


def full_rigor_labels(language: Optional[str] = None):
    """Etichette localizzate della rigidità nell'identico ordine corrente."""
    return tuple(i18n.rigor_label(state_id, language) for state_id in RIGOR_LABEL_IT)


def full_livor_state_id(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce l'ID stabile associato a una voce della UI completa."""
    state_by_label = {
        i18n.livor_label(state_id, language): state_id
        for state_id in LIVOR_LABEL_IT
    }
    return state_by_label[ui_label]


def full_rigor_state_id(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce l'ID stabile associato a una voce della UI completa."""
    state_by_label = {
        i18n.rigor_label(state_id, language): state_id
        for state_id in RIGOR_LABEL_IT
    }
    return state_by_label[ui_label]


def full_livor_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce il valore legacy attualmente atteso dal motore."""
    return livor_legacy_label(full_livor_state_id(ui_label, language))


def full_rigor_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce il valore legacy attualmente atteso dal motore."""
    return rigor_legacy_label(full_rigor_state_id(ui_label, language))


def full_special_parameter_ids():
    """ID stabili dei parametri speciali nell'identico ordine corrente."""
    return tuple(SPECIAL_PARAM_LABEL_IT.keys())


def full_special_parameter_labels(language: Optional[str] = None):
    """Etichette localizzate dei parametri speciali nell'ordine corrente."""
    return tuple(
        i18n.special_parameter_label(param_id, language)
        for param_id in full_special_parameter_ids()
    )


def full_special_parameter_id(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce l'ID stabile associato al parametro speciale mostrato."""
    parameter_by_label = {
        i18n.special_parameter_label(param_id, language): param_id
        for param_id in full_special_parameter_ids()
    }
    return parameter_by_label[ui_label]


def full_special_parameter_label(param_id: str, language: Optional[str] = None) -> str:
    """Restituisce l'etichetta localizzata del parametro speciale."""
    return i18n.special_parameter_label(param_id, language)


def full_special_parameter_legacy_value(param_id: str) -> str:
    """Restituisce il nome legacy del parametro atteso dai dati esistenti."""
    return special_param_legacy_label(param_id)


def full_special_option_labels(param_id: str, language: Optional[str] = None):
    """Etichette localizzate delle opzioni nell'identico ordine corrente."""
    return tuple(
        i18n.special_option_label(param_id, option_id, language)
        for option_id in special_option_ids(param_id)
    )


def full_special_option_id(
    param_id: str,
    ui_label: str,
    language: Optional[str] = None,
) -> str:
    """Restituisce l'ID stabile dell'opzione mostrata nella UI."""
    option_by_label = {
        i18n.special_option_label(param_id, option_id, language): option_id
        for option_id in special_option_ids(param_id)
    }
    return option_by_label[ui_label]


def full_special_option_legacy_value(
    param_id: str,
    ui_label: str,
    language: Optional[str] = None,
) -> str:
    """Restituisce l'opzione legacy attualmente attesa dal motore."""
    option_id = full_special_option_id(param_id, ui_label, language)
    return special_option_legacy_label(param_id, option_id)


__all__ = [
    "FULL_LIVOR_STATE_BY_LABEL",
    "FULL_RIGOR_STATE_BY_LABEL",
    "FULL_SPECIAL_PARAM_BY_LABEL",
    "full_livor_labels",
    "full_rigor_labels",
    "full_livor_state_id",
    "full_rigor_state_id",
    "full_livor_legacy_value",
    "full_rigor_legacy_value",
    "full_special_parameter_ids",
    "full_special_parameter_labels",
    "full_special_parameter_id",
    "full_special_parameter_label",
    "full_special_parameter_legacy_value",
    "full_special_option_labels",
    "full_special_option_id",
    "full_special_option_legacy_value",
]
