# -*- coding: utf-8 -*-
"""Compatibilità legacy per i testi tanatologici italiani.

Il contenuto è stato spostato in ``app.locales.it``. Questo modulo resta
temporaneamente disponibile per non modificare i chiamanti esistenti.
"""

import app.i18n as i18n
from app.locales.it import *
from app.locales.it import __all__
from app.special_tanatology_states import (
    PARAM_MECHANICAL_MUSCLE,
    MECH_WHOLE_MUSCLE,
    MECH_REVERSIBLE_SWELLING,
    MECH_SMALL_PERSISTENT_SWELLING,
    SPECIAL_PARAM_LABEL_IT,
    SPECIAL_OPTION_LABEL_IT,
)


_MECHANICAL_DESCRIPTIONS_IT = {
    MECH_WHOLE_MUSCLE: (
        "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla contrazione "
        "dell’intero muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce che il decesso "
        "fosse avvenuto non oltre 2 ore e 30 minuti prima della valutazione del dato tanatologico."
    ),
    MECH_REVERSIBLE_SWELLING: (
        "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione "
        "di una tumefazione reversibile del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce "
        "che il decesso fosse avvenuto non oltre 5 ore prima della valutazione del dato tanatologico."
    ),
    MECH_SMALL_PERSISTENT_SWELLING: (
        "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione "
        "di una piccola tumefazione persistente del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione "
        "suggerisce che il decesso fosse avvenuto non oltre 12 ore prima della valutazione del dato tanatologico."
    ),
}

# Mantiene allineata la locale italiana già caricata da app.i18n e la vista
# legacy importata da app.parameters senza duplicare la logica dei range.
SPECIAL_DESCRIPTION_IT_BY_ID[PARAM_MECHANICAL_MUSCLE].update(_MECHANICAL_DESCRIPTIONS_IT)
_mechanical_param_label = SPECIAL_PARAM_LABEL_IT[PARAM_MECHANICAL_MUSCLE]
_mechanical_legacy_descriptions = SPECIAL_DESCRIPTIONS_LEGACY_BY_PARAM_LABEL[_mechanical_param_label]
for _option_id, _description in _MECHANICAL_DESCRIPTIONS_IT.items():
    _mechanical_legacy_descriptions[
        SPECIAL_OPTION_LABEL_IT[PARAM_MECHANICAL_MUSCLE][_option_id]
    ] = _description


def livor_description_it(state_id: str):
    return i18n.livor_description(state_id)


def rigor_description_it(state_id: str):
    return i18n.rigor_description(state_id)
