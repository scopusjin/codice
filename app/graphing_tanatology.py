# -*- coding: utf-8 -*-
"""Adattatori tanatologici puri per ``app.graphing``.

Questo modulo traduce le stringhe legacy oggi ricevute dal motore grafico negli
ID stabili introdotti dal refactoring. I valori scientifici e le descrizioni
continuano a provenire dalle fonti esistenti; qui non vengono definiti nuovi
range, soglie o criteri.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from app.parameters import dati_parametri_aggiuntivi
from app.tanatology_states import (
    LIVOR_ID_BY_LEGACY_LABEL,
    RIGOR_ID_BY_LEGACY_LABEL,
)
from app.tanatology_data import (
    LIVOR_RANGES_BY_ID,
    LIVOR_TYPICAL_RANGES_BY_ID,
    RIGOR_RANGES_BY_ID,
    RIGOR_TYPICAL_RANGES_BY_ID,
)
from app.special_tanatology_states import (
    OPTION_NOT_ASSESSED,
    PARAM_ELECTRICAL_PERIORAL,
    SPECIAL_PARAM_ID_BY_LEGACY_LABEL,
    SPECIAL_OPTION_ID_BY_LEGACY_LABEL,
    special_description,
    special_range,
)

RangeValue = Optional[Tuple[float, float]]


@dataclass(frozen=True)
class BaseTanatologyRanges:
    livor_id: Optional[str]
    livor_range: RangeValue
    livor_typical_range: RangeValue
    rigor_id: Optional[str]
    rigor_range: RangeValue
    rigor_typical_range: RangeValue


@dataclass(frozen=True)
class SpecialTanatologyValue:
    parameter_id: Optional[str]
    option_id: Optional[str]
    legacy_description_key: str
    range_value: RangeValue
    description: Optional[str]
    is_not_assessed: bool


def resolve_base_tanatology_ranges(
    livor_legacy_label: str,
    rigor_legacy_label: str,
) -> BaseTanatologyRanges:
    """Restituisce gli stessi range legacy, indicizzati tramite ID stabili.

    Per etichette sconosciute conserva il comportamento permissivo dei vecchi
    ``dict.get``: ID e range risultano ``None`` invece di sollevare eccezioni.
    """
    livor_id = LIVOR_ID_BY_LEGACY_LABEL.get(livor_legacy_label)
    rigor_id = RIGOR_ID_BY_LEGACY_LABEL.get(rigor_legacy_label)

    return BaseTanatologyRanges(
        livor_id=livor_id,
        livor_range=LIVOR_RANGES_BY_ID.get(livor_id),
        livor_typical_range=LIVOR_TYPICAL_RANGES_BY_ID.get(livor_id),
        rigor_id=rigor_id,
        rigor_range=RIGOR_RANGES_BY_ID.get(rigor_id),
        rigor_typical_range=RIGOR_TYPICAL_RANGES_BY_ID.get(rigor_id),
    )


def resolve_special_tanatology_value(
    parameter_legacy_label: str,
    selected_legacy_label: str,
) -> SpecialTanatologyValue:
    """Normalizza un parametro speciale mantenendo la compatibilità legacy.

    La normalizzazione ``split(':')[0]`` per il parametro peribuccale replica
    esplicitamente il comportamento già presente in ``app.graphing``.
    """
    parameter_id = SPECIAL_PARAM_ID_BY_LEGACY_LABEL.get(parameter_legacy_label)

    description_key = (
        selected_legacy_label.split(":")[0].strip()
        if parameter_id == PARAM_ELECTRICAL_PERIORAL
        else selected_legacy_label.strip()
    )

    option_id = None
    if parameter_id is not None:
        option_id = SPECIAL_OPTION_ID_BY_LEGACY_LABEL[parameter_id].get(description_key)

    if option_id is not None:
        range_value = special_range(parameter_id, option_id)
        description = special_description(parameter_id, option_id)
        is_not_assessed = option_id == OPTION_NOT_ASSESSED
    else:
        # Fallback identico alla struttura legacy per eventuali input storici
        # non ancora rappresentati dagli ID stabili.
        legacy_data = dati_parametri_aggiuntivi.get(parameter_legacy_label, {})
        range_dict = legacy_data.get("range", {})
        exact_key = next(
            (key for key in range_dict if key.strip() == description_key),
            None,
        )
        range_value = range_dict.get(exact_key)
        description = legacy_data.get("descrizioni", {}).get(description_key)
        is_not_assessed = selected_legacy_label == "Non valutata"

    return SpecialTanatologyValue(
        parameter_id=parameter_id,
        option_id=option_id,
        legacy_description_key=description_key,
        range_value=range_value,
        description=description,
        is_not_assessed=is_not_assessed,
    )


__all__ = [
    "BaseTanatologyRanges",
    "SpecialTanatologyValue",
    "resolve_base_tanatology_ranges",
    "resolve_special_tanatology_value",
]
