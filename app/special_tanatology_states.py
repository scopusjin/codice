# -*- coding: utf-8 -*-
"""Identificatori stabili per i parametri tanatologici aggiuntivi.

Il modulo separa gli ID interni dalle etichette italiane attualmente usate da
``app.parameters``. I range scientifici e le descrizioni legacy restano
accessibili tramite adattatori compatibili, senza dipendenze top-level dai dati.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

RangeValue = Optional[Tuple[float, float]]


# -----------------------------------------------------------------------------
# Parametri
# -----------------------------------------------------------------------------
PARAM_ELECTRICAL_SUPRACILIARY = "electrical_supraciliary"
PARAM_ELECTRICAL_PERIORAL = "electrical_perioral"
PARAM_MECHANICAL_MUSCLE = "mechanical_muscle"
PARAM_CHEMICAL_PUPILLARY = "chemical_pupillary"

SPECIAL_PARAM_LABEL_IT: Dict[str, str] = {
    PARAM_ELECTRICAL_SUPRACILIARY: "Eccitabilità elettrica sopraciliare",
    PARAM_ELECTRICAL_PERIORAL: "Eccitabilità elettrica peribuccale",
    PARAM_MECHANICAL_MUSCLE: "Eccitabilità muscolare meccanica",
    PARAM_CHEMICAL_PUPILLARY: "Eccitabilità chimica pupillare",
}

SPECIAL_PARAM_ID_BY_LEGACY_LABEL = {
    label: param_id for param_id, label in SPECIAL_PARAM_LABEL_IT.items()
}


# -----------------------------------------------------------------------------
# Opzioni comuni
# -----------------------------------------------------------------------------
OPTION_NOT_ASSESSED = "not_assessed"
OPTION_UNRELIABLE = "unreliable"
OPTION_NO_REACTION = "no_reaction"


# Eccitabilità elettrica sopraciliare
SUPRA_PHASE_I = "phase_i"
SUPRA_PHASE_II = "phase_ii"
SUPRA_PHASE_III = "phase_iii"
SUPRA_PHASE_IV = "phase_iv"
SUPRA_PHASE_V = "phase_v"
SUPRA_PHASE_VI = "phase_vi"

# Eccitabilità elettrica peribuccale
PERIORAL_MARKED = "marked_extensive"
PERIORAL_MODERATE = "moderate"
PERIORAL_SLIGHT = "slight"

# Eccitabilità muscolare meccanica
MECH_WHOLE_MUSCLE = "whole_muscle_reversible_contraction"
MECH_REVERSIBLE_SWELLING = "reversible_swelling"
MECH_SMALL_PERSISTENT_SWELLING = "small_persistent_swelling"

# Eccitabilità chimica pupillare
# I due ID storici restano disponibili per compatibilità con le descrizioni
# legacy, ma non sono più mostrati nel menu della UI completa.
PUPILLARY_POSITIVE = "positive"
PUPILLARY_NEGATIVE = "negative"

PUPILLARY_ATROPINE_DILATION = "atropine_dilation"
PUPILLARY_ATROPINE_NO_CHANGE = "atropine_no_change"
PUPILLARY_TROPICAMIDE_DILATION = "tropicamide_dilation"
PUPILLARY_TROPICAMIDE_NO_CHANGE = "tropicamide_no_change"
PUPILLARY_ACETYLCHOLINE_REDUCTION = "acetylcholine_reduction"
PUPILLARY_ACETYLCHOLINE_NO_CHANGE = "acetylcholine_no_change"

_PUPILLARY_HENSSGE_OPTION_IDS = (
    PUPILLARY_ATROPINE_DILATION,
    PUPILLARY_ATROPINE_NO_CHANGE,
    PUPILLARY_TROPICAMIDE_DILATION,
    PUPILLARY_TROPICAMIDE_NO_CHANGE,
    PUPILLARY_ACETYLCHOLINE_REDUCTION,
    PUPILLARY_ACETYLCHOLINE_NO_CHANGE,
)


SPECIAL_OPTION_LABEL_IT: Dict[str, Dict[str, str]] = {
    PARAM_ELECTRICAL_SUPRACILIARY: {
        OPTION_NOT_ASSESSED: "Non valutata",
        SUPRA_PHASE_I: "Fase I",
        SUPRA_PHASE_II: "Fase II",
        SUPRA_PHASE_III: "Fase III",
        SUPRA_PHASE_IV: "Fase IV",
        SUPRA_PHASE_V: "Fase V",
        SUPRA_PHASE_VI: "Fase VI",
        OPTION_NO_REACTION: "Nessuna reazione",
        OPTION_UNRELIABLE: "Non valutabile/non attendibile",
    },
    PARAM_ELECTRICAL_PERIORAL: {
        OPTION_NOT_ASSESSED: "Non valutata",
        PERIORAL_MARKED: "Muscoli facciali (+++)",
        PERIORAL_MODERATE: "Muscoli peribuccali (++)",
        PERIORAL_SLIGHT: "Reazione focale (+)",
        OPTION_NO_REACTION: "Nessuna reazione",
        OPTION_UNRELIABLE: "Non valutabile/non attendibile",
    },
    PARAM_MECHANICAL_MUSCLE: {
        OPTION_NOT_ASSESSED: "Non valutata",
        MECH_WHOLE_MUSCLE: "Contrazione reversibile dell’intero muscolo",
        MECH_REVERSIBLE_SWELLING: "Formazione di una tumefazione reversibile",
        MECH_SMALL_PERSISTENT_SWELLING: "Formazione di una piccola tumefazione persistente",
        OPTION_NO_REACTION: "Nessuna reazione",
        OPTION_UNRELIABLE: "Non valutabile/non attendibile",
    },
    PARAM_CHEMICAL_PUPILLARY: {
        OPTION_NOT_ASSESSED: "Non valutata",
        OPTION_UNRELIABLE: "Non valutabile/non attendibile",
        # Alias legacy mantenuti per non interrompere import e documenti storici.
        PUPILLARY_POSITIVE: "Positiva",
        PUPILLARY_NEGATIVE: "Negativa",
        PUPILLARY_ATROPINE_DILATION: "Dilatazione con atropina",
        PUPILLARY_ATROPINE_NO_CHANGE: "Nessuna variazione con atropina",
        PUPILLARY_TROPICAMIDE_DILATION: "Dilatazione con tropicamide",
        PUPILLARY_TROPICAMIDE_NO_CHANGE: "Nessuna variazione con tropicamide",
        PUPILLARY_ACETYLCHOLINE_REDUCTION: "Riduzione con acetilcolina",
        PUPILLARY_ACETYLCHOLINE_NO_CHANGE: "Nessuna variazione con acetilcolina",
    },
}

SPECIAL_OPTION_ID_BY_LEGACY_LABEL: Dict[str, Dict[str, str]] = {
    param_id: {label: option_id for option_id, label in labels.items()}
    for param_id, labels in SPECIAL_OPTION_LABEL_IT.items()
}


# -----------------------------------------------------------------------------
# Adattatori legacy
# -----------------------------------------------------------------------------
def special_param_legacy_label(param_id: str) -> str:
    return SPECIAL_PARAM_LABEL_IT[param_id]


def special_param_id(legacy_label: str) -> str:
    return SPECIAL_PARAM_ID_BY_LEGACY_LABEL[legacy_label]


def special_option_legacy_label(param_id: str, option_id: str) -> str:
    return SPECIAL_OPTION_LABEL_IT[param_id][option_id]


def special_option_id(param_id: str, legacy_label: str) -> str:
    return SPECIAL_OPTION_ID_BY_LEGACY_LABEL[param_id][legacy_label]


def special_option_ids(param_id: str):
    """Opzioni nell'identico ordine della UI legacy."""
    if param_id == PARAM_CHEMICAL_PUPILLARY:
        return (
            OPTION_NOT_ASSESSED,
            *_PUPILLARY_HENSSGE_OPTION_IDS,
            OPTION_UNRELIABLE,
        )
    return tuple(SPECIAL_OPTION_LABEL_IT[param_id].keys())


def special_option_legacy_labels(param_id: str):
    """Etichette nell'identico ordine della UI legacy."""
    return tuple(
        SPECIAL_OPTION_LABEL_IT[param_id][option_id]
        for option_id in special_option_ids(param_id)
    )


def special_range(param_id: str, option_id: str) -> RangeValue:
    """Range letto direttamente da app.parameters, senza duplicare valori."""
    from app.parameters import dati_parametri_aggiuntivi

    param_label = special_param_legacy_label(param_id)
    option_label = special_option_legacy_label(param_id, option_id)
    return dati_parametri_aggiuntivi[param_label]["range"][option_label]


def special_description(param_id: str, option_id: str):
    """Descrizione corrente esposta tramite il livello i18n."""
    if (
        param_id in {PARAM_CHEMICAL_PUPILLARY, PARAM_ELECTRICAL_PERIORAL}
        and (param_id != PARAM_CHEMICAL_PUPILLARY or option_id in _PUPILLARY_HENSSGE_OPTION_IDS)
    ):
        from app.parameters import dati_parametri_aggiuntivi

        param_label = special_param_legacy_label(param_id)
        option_label = special_option_legacy_label(param_id, option_id)
        return dati_parametri_aggiuntivi[param_label]["descrizioni"].get(option_label)

    from app.i18n import special_description as localized_special_description

    return localized_special_description(param_id, option_id)


__all__ = [
    "PARAM_ELECTRICAL_SUPRACILIARY",
    "PARAM_ELECTRICAL_PERIORAL",
    "PARAM_MECHANICAL_MUSCLE",
    "PARAM_CHEMICAL_PUPILLARY",
    "SPECIAL_PARAM_LABEL_IT",
    "SPECIAL_PARAM_ID_BY_LEGACY_LABEL",
    "OPTION_NOT_ASSESSED",
    "OPTION_UNRELIABLE",
    "OPTION_NO_REACTION",
    "SUPRA_PHASE_I",
    "SUPRA_PHASE_II",
    "SUPRA_PHASE_III",
    "SUPRA_PHASE_IV",
    "SUPRA_PHASE_V",
    "SUPRA_PHASE_VI",
    "PERIORAL_MARKED",
    "PERIORAL_MODERATE",
    "PERIORAL_SLIGHT",
    "MECH_WHOLE_MUSCLE",
    "MECH_REVERSIBLE_SWELLING",
    "MECH_SMALL_PERSISTENT_SWELLING",
    "PUPILLARY_POSITIVE",
    "PUPILLARY_NEGATIVE",
    "PUPILLARY_ATROPINE_DILATION",
    "PUPILLARY_ATROPINE_NO_CHANGE",
    "PUPILLARY_TROPICAMIDE_DILATION",
    "PUPILLARY_TROPICAMIDE_NO_CHANGE",
    "PUPILLARY_ACETYLCHOLINE_REDUCTION",
    "PUPILLARY_ACETYLCHOLINE_NO_CHANGE",
    "SPECIAL_OPTION_LABEL_IT",
    "SPECIAL_OPTION_ID_BY_LEGACY_LABEL",
    "special_param_legacy_label",
    "special_param_id",
    "special_option_legacy_label",
    "special_option_id",
    "special_option_ids",
    "special_option_legacy_labels",
    "special_range",
    "special_description",
]
