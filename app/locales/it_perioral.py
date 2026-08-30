# -*- coding: utf-8 -*-
"""Etichette sintetiche italiane della griglia peribuccale.

Gli intervalli sono separati dalle immagini e indicizzati tramite gli ID stabili
delle opzioni. Range e descrizioni scientifiche restano nei moduli dati.
"""

from app.special_tanatology_states import (
    OPTION_NO_REACTION,
    OPTION_NOT_ASSESSED,
    OPTION_UNRELIABLE,
    PERIORAL_MARKED,
    PERIORAL_MODERATE,
    PERIORAL_SLIGHT,
)


PERIORAL_GRID_INTERVAL_BY_ID = {
    PERIORAL_MARKED: "< 2½ h",
    PERIORAL_MODERATE: "1–5 h",
    PERIORAL_SLIGHT: "2–6 h",
    OPTION_NO_REACTION: "> 3 h",
    OPTION_UNRELIABLE: "",
    OPTION_NOT_ASSESSED: "",
}


__all__ = ["PERIORAL_GRID_INTERVAL_BY_ID"]
