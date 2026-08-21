# -*- coding: utf-8 -*-
"""Compatibilità legacy per i testi tanatologici italiani.

Il contenuto è stato spostato in ``app.locales.it``. Questo modulo resta
temporaneamente disponibile per non modificare i chiamanti esistenti.
"""

import app.i18n as i18n
from app.locales.it import *
from app.locales.it import __all__


def livor_description_it(state_id: str):
    return i18n.livor_description(state_id)


def rigor_description_it(state_id: str):
    return i18n.rigor_description(state_id)
