# app/utils_time.py
# -*- coding: utf-8 -*-
"""
Utility per la gestione di date/ore e conversioni in minuti/ore.
"""

import datetime
import numpy as np


def arrotonda_quarto_dora(dt: datetime.datetime) -> datetime.datetime:
    """
    Arrotonda un datetime al quarto d’ora più vicino.
    """
    minuti = (dt.minute + 7) // 15 * 15
    if minuti == 60:
        dt += datetime.timedelta(hours=1)
        minuti = 0
    return dt.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=minuti)


def split_hours_minutes(h: float) -> tuple[int, int] | None:
    """
    Converte ore decimali in (ore, minuti), evitando '60 minuti'.
    Ritorna None se h non è valido.
    """
    if h is None or (isinstance(h, float) and np.isnan(h)):
        return None
    total_minutes = int(round(h * 60))
    hours, minutes = divmod(total_minutes, 60)
    return hours, minutes


__all__ = ["arrotonda_quarto_dora", "split_hours_minutes"]

