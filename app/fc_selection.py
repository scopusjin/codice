"""Transfer an explicit FC choice; no scientific rules are reimplemented here."""

from decimal import Decimal, ROUND_HALF_UP
from math import isfinite


def rounded_fc(value):
    value = float(value)
    if not isfinite(value):
        raise ValueError("FC non valido")
    return float((Decimal(str(value)) / Decimal("0.05")).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    ) * Decimal("0.05"))


def validate_choice(payload):
    values = payload.get("range")
    if not isinstance(values, list) or len(values) != 2:
        raise ValueError("Inserire minimo e massimo.")
    lo, hi = map(float, values)
    weight = float(payload.get("weight"))
    if not all(isfinite(v) for v in (lo, hi, weight)):
        raise ValueError("Valori non validi.")
    if lo < 0.35 or hi < lo or not 4 <= weight <= 150:
        raise ValueError("Verificare FC e peso.")
    if any(abs(v - rounded_fc(v)) > 1e-8 for v in (lo, hi)):
        raise ValueError("Il FC deve essere espresso in passi di 0.05.")
    return round(lo, 2), round(hi, 2), weight


def apply_choice(state, payload, *, msil=False):
    """Apply exactly the chosen bounds, without accumulating older suggestions."""
    lo, hi, weight = validate_choice(payload)
    was_prudent = bool(state.get("stima_cautelativa_beta", False))
    interval = was_prudent or hi > lo or msil
    if interval and not was_prudent:
        ta = state.get("ta_base_val", 20.0)
        state["__full_standard_ta_base_val"] = ta
        state["__full_standard_fattore_correzione"] = state.get("fattore_correzione", 1.0)
        for key in ("ta_other_val", "Ta_min_beta", "Ta_max_beta"):
            state[key] = ta
    state["peso"] = weight
    state["peso_widget"] = weight
    state["peso_str"] = f"{weight:.1f}"
    state["fattore_correzione"] = rounded_fc((lo + hi) / 2)
    for key in ("fc_min_val", "FC_min_beta", "__full_interval_fc_min_val"):
        state[key] = lo
    for key in ("fc_other_val", "FC_max_beta", "__full_interval_fc_other_val"):
        state[key] = hi
    state["fc_suggested_vals"] = [lo, hi]
    state["stima_cautelativa_beta"] = interval
    state["range_unico_beta"] = interval
    state["__prudent_explicit_ranges_initialized"] = True
    if interval:
        state["__full_interval_ta_base_val"] = state.get("ta_base_val", 20.0)
        state["__full_interval_ta_other_val"] = state.get("ta_other_val", state.get("ta_base_val", 20.0))
    state["__fc_applied_choice"] = payload
    state["fc_riassunto_contatori"] = None
    state["fattori_condizioni_parentetica"] = None
    state["fattori_condizioni_testo"] = payload.get("description") or None
    state["show_results"] = False
    state["run_stima_mobile"] = False
    # Both views share the same selected FC; a later switch to MSIL must not
    # resurrect its previous range or replace this choice with +/- 0.10.
    state["__msil_fc_chosen_range"] = [lo, hi]
