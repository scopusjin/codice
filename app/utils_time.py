# app/utils_time.py

import datetime
import numpy as np

def round_hours_to_minutes(x: float, minutes: int) -> float:
    """Arrotonda 'x' ore al multiplo di 'minutes' minuti più vicino."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    step_h = minutes / 60.0
    return np.round(x / step_h) * step_h

def round_datetime_to_minutes(dt: datetime.datetime, minutes: int) -> datetime.datetime:
    """Arrotonda un datetime al multiplo di 'minutes' minuti più vicino."""
    step = minutes
    tot = dt.hour * 60 + dt.minute + dt.second / 60 + dt.microsecond / 60_000_000
    rounded = int(np.floor(tot / step + 0.5)) * step
    dh, dm = divmod(rounded, 60)
    base = dt.replace(minute=0, second=0, microsecond=0)
    return base.replace(hour=0) + datetime.timedelta(hours=dh, minutes=dm)

# --- Funzioni esistenti, ora basate sulle nuove ---
def arrotonda_quarto_dora(dt: datetime.datetime) -> datetime.datetime:
    """Arrotonda un datetime al quarto d’ora (15′) più vicino."""
    return round_datetime_to_minutes(dt, 15)

def split_hours_minutes(h: float) -> tuple[int, int] | None:
    if h is None or (isinstance(h, float) and np.isnan(h)):
        return None
    total_minutes = int(round(h * 60))
    hours, minutes = divmod(total_minutes, 60)
    return hours, minutes

# Compat: usata in vari punti del codice per 15′ sulle ORE decimali
def round_quarter_hour(x: float) -> float:
    return round_hours_to_minutes(x, 15)

__all__ = [
    "arrotonda_quarto_dora", "split_hours_minutes",
    "round_hours_to_minutes", "round_datetime_to_minutes",
    "round_quarter_hour",
]


def round_display_hours(hours: float, minutes: int = 15, *, upper: bool = False) -> float:
    """Round one displayed bound outward, never a computational intermediate."""
    if not np.isfinite(hours):
        return hours
    units = float(hours) * 60.0 / minutes
    nearest = round(units)
    if abs(units - nearest) <= 1e-10:
        units = nearest
    bound = np.ceil(units) if upper else np.floor(units)
    return float(bound * minutes / 60.0)


def round_display_datetime(dt: datetime.datetime, minutes: int = 15, *, upper: bool = False) -> datetime.datetime:
    """Round a calendar bound outward; retain midnight/day transitions."""
    midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    hours = (dt - midnight).total_seconds() / 3600.0
    return midnight + datetime.timedelta(hours=round_display_hours(hours, minutes, upper=upper))
