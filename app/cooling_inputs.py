"""Shared numeric validation for cooling calculations (no UI or scientific rules)."""

import math


def finite_number(value):
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def missing_cooling_inputs(*, input_rt, input_ta, input_tm, input_w,
                           fattore_correzione, options=None):
    """Describe every empty field, including incomplete explicit intervals."""
    options = {} if options is None else options
    prudent = bool(options.get("stima_cautelativa_beta", False))

    def interval_missing(raw_keys, bound_keys, label):
        keys = raw_keys if all(key in options for key in raw_keys) else bound_keys
        count = sum(not finite_number(options.get(key)) for key in keys)
        if count == 2:
            return label
        if count == 1:
            return "uno dei due valori di " + label.removeprefix("la ").removeprefix("il ")
        return None

    ambient = (interval_missing(("ta_base_val", "ta_other_val"),
                               ("Ta_min_beta", "Ta_max_beta"), "la temperatura ambientale")
               if prudent else ("la temperatura ambientale" if not finite_number(input_ta) else None))
    temperatures = ["la temperatura rettale" if not finite_number(input_rt) else None,
                    ambient,
                    "la temperatura ante-mortem" if not finite_number(input_tm) else None]
    if all(temperatures) and ambient == "la temperatura ambientale":
        missing = ["tutte le temperature (rettale, ambientale e ante-mortem)"]
    else:
        missing = [field for field in temperatures if field]
    if not finite_number(input_w):
        missing.append("il peso corporeo")
    fc = (interval_missing(("fc_min_val", "fc_other_val"),
                           ("FC_min_beta", "FC_max_beta"), "il FC")
          if prudent else ("il FC" if not finite_number(fattore_correzione) else None))
    if fc:
        missing.append(fc)
    if not missing:
        return None
    plural = len(missing) > 1 or missing[0].startswith("tutte ")
    fields = missing[0] if len(missing) == 1 else ", ".join(missing[:-1]) + " e " + missing[-1]
    return ("Mancano " if plural else "Manca ") + fields + "."


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
