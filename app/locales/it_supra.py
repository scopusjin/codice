# -*- coding: utf-8 -*-
"""Etichette sintetiche italiane della griglia sopraciliare.

I testi sono separati dalle immagini e indicizzati tramite gli ID stabili delle
opzioni. Le informazioni scientifiche usate nei calcoli restano nei moduli dati.
"""

from app.special_tanatology_states import (
    OPTION_NO_REACTION,
    OPTION_NOT_ASSESSED,
    OPTION_UNRELIABLE,
    SUPRA_PHASE_I,
    SUPRA_PHASE_II,
    SUPRA_PHASE_III,
    SUPRA_PHASE_IV,
    SUPRA_PHASE_V,
    SUPRA_PHASE_VI,
)


SUPRA_GRID_DETAIL_BY_ID = {
    SUPRA_PHASE_VI: ("Fronte + orbita + guancia", "1–6 h"),
    SUPRA_PHASE_V: ("Fronte + orbita", "2–7 h"),
    SUPRA_PHASE_IV: ("Orbicolari sup. + inf.", "3–8 h"),
    SUPRA_PHASE_III: ("Palpebra sup. intera", "3½–13 h"),
    SUPRA_PHASE_II: ("< 2/3 palpebra sup.", "5–16 h"),
    SUPRA_PHASE_I: ("< 1/3 palpebra sup.", "5–22 h"),
    OPTION_NO_REACTION: ("", "> 5 h"),
    OPTION_UNRELIABLE: ("", ""),
    OPTION_NOT_ASSESSED: ("", ""),
}


__all__ = ["SUPRA_GRID_DETAIL_BY_ID"]
