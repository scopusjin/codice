"""Shared numeric validation for cooling calculations (no UI or scientific rules)."""

import math


def finite_number(value):
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def checked_interval(values, label, *, positive=False):
    if values is None or len(values) != 2 or not all(finite_number(v) for v in values):
        raise ValueError(f"Completare minimo e massimo di {label}.")
    lo, hi = sorted(float(v) for v in values)
    if positive and lo <= 0:
        raise ValueError(f"Gli estremi di {label} devono essere maggiori di zero.")
    return lo, hi


def checked_weight(weight, *, estimated=False):
    if not finite_number(weight) or float(weight) <= 0:
        raise ValueError("Inserire un peso valido, maggiore di zero.")
    value = float(weight)
    if estimated and value <= 3:
        raise ValueError("Con peso stimato ±3 kg, anche il peso minimo deve essere maggiore di zero.")
    return value
