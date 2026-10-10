"""Transfer an explicit FC choice; no scientific rules are reimplemented here."""

from decimal import Decimal, ROUND_HALF_UP
from math import isfinite

from app.fc_weight import adapt_fc_range
from app.fc_scenarios import adapt_scenarios, summarize_scenarios, scenario_temperature_bounds


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
    if "scenarios" in payload:
        scenarios = payload["scenarios"]
        if not isinstance(scenarios, list) or len(scenarios) < 2 or payload.get("manual") is not False:
            raise ValueError("Specificare almeno due scenari completi.")
        for item in scenarios:
            if (not isinstance(item, dict) or "scenarios" in item
                    or not isinstance(item.get("description"), str) or not item["description"].strip()
                    or not isinstance(item.get("draft"), dict)):
                raise ValueError("Scenario incompleto.")
            _, _, scenario_weight = validate_choice(item)
            if scenario_weight != weight:
                raise ValueError("Gli scenari devono usare lo stesso peso.")
        if summarize_scenarios(scenarios)[0] != [lo, hi]:
            raise ValueError("Il range deve comprendere tutti gli scenari.")
        scenario_temperature_bounds(payload)
    return round(lo, 2), round(hi, 2), weight


def sync_fc_weight(state, weight):
    """Synchronize the existing weight fields after caller validation."""
    state["peso"] = weight
    state["peso_widget"] = weight
    state["peso_str"] = f"{weight:.1f}"


def apply_choice(state, payload, *, msil=False, sync_weight=True):
    """Apply exactly the chosen bounds, without accumulating older suggestions."""
    lo, hi, weight = validate_choice(payload)
    if payload.get("scenarios"):
        payload = {**payload, "description": summarize_scenarios(payload["scenarios"])[1]}
    if payload.get("manual") is True and payload.get("base_range") is None:
        payload = {**payload, "base_range": [lo, hi], "manual_weight_adjusted": False}
    was_prudent = bool(state.get("stima_cautelativa_beta", False))
    interval = was_prudent or hi > lo or msil or bool(payload.get("scenarios"))
    if interval and not was_prudent:
        ta = state.get("ta_base_val", 20.0)
        state["__full_standard_ta_base_val"] = ta
        state["__full_standard_fattore_correzione"] = state.get("fattore_correzione", 1.0)
        for key in ("ta_other_val", "Ta_min_beta", "Ta_max_beta"):
            state[key] = ta
    if sync_weight:
        sync_fc_weight(state, weight)
    state["fattore_correzione"] = rounded_fc((lo + hi) / 2)
    for key in ("fc_min_val", "FC_min_beta", "__full_interval_fc_min_val"):
        state[key] = lo
    for key in ("fc_other_val", "FC_max_beta", "__full_interval_fc_other_val"):
        state[key] = hi
    state["fc_suggested_vals"] = [lo, hi]
    state["stima_cautelativa_beta"] = interval
    state["range_unico_beta"] = interval
    state["__prudent_explicit_ranges_initialized"] = True
    temperatures = scenario_temperature_bounds(payload)
    if temperatures is not None and sync_weight:
        for key in ("ta_base_val", "Ta_min_beta"):
            state[key] = temperatures[0]
        for key in ("ta_other_val", "Ta_max_beta"):
            state[key] = temperatures[1]
        state["ta_base_val_widget"] = temperatures[0]
        state["ta_base_val_str"] = f"{temperatures[0]:.1f}"
    if interval:
        state["__full_interval_ta_base_val"] = state.get("ta_base_val", 20.0)
        state["__full_interval_ta_other_val"] = state.get("ta_other_val", state.get("ta_base_val", 20.0))
    state["__fc_applied_choice"] = payload
    state["__fc_reviewed_weight"] = weight
    state["fc_riassunto_contatori"] = None
    state["fattori_condizioni_parentetica"] = None
    state["fattori_condizioni_testo"] = None if payload.get("scenarios") else payload.get("description") or None
    state["show_results"] = False
    state["run_stima_mobile"] = False
    # Both views share the same selected FC; a later switch to MSIL must not
    # resurrect its previous range or replace this choice with +/- 0.10.
    state["__msil_fc_chosen_range"] = [lo, hi]


def normalize_fc_input(state, key, *, msil=False):
    """Round a manual edit to the same nearest 0.05 used by the FC panel."""
    choice = state.get("__fc_applied_choice")
    # An incomplete manual edit must never restore an older, valid selection.
    choice = {**(choice or {}), "manual": True, "base_range": None,
              "manual_weight_adjusted": False, "weight_adjusted": False, "manual_center": msil}
    choice.pop("scenarios", None)
    state["__fc_applied_choice"] = choice
    try:
        value = rounded_fc(state.get(key))
    except (TypeError, ValueError):
        return
    state[key] = value
    values = ([value, value] if key == "fattore_correzione" else
              [state.get("fc_min_val"), state.get("fc_other_val")])
    try:
        # FC may be entered before weight in Sopralluogo. Validate its bounds
        # independently and retain them until a valid weight is available.
        lo, hi, _ = validate_choice({"range": values, "weight": 70})
    except (TypeError, ValueError, OverflowError):
        return
    try:
        _, _, weight = validate_choice({"range": [lo, hi], "weight": state.get("peso")})
    except (TypeError, ValueError, OverflowError):
        weight = None
    state["__fc_applied_choice"] = {
        **choice, "range": [lo, hi], "base_range": [lo, hi], "weight": weight,
    }
    state["__fc_reviewed_weight"] = weight


def refresh_fc_for_weight(state, *, msil=False):
    """Adapt the original selected bounds, never the last adapted result."""
    choice = state.get("__fc_applied_choice")
    if not isinstance(choice, dict) or choice.get("manual") not in (True, False):
        return False
    # Old manual edits retained the helper's bounds, not the operator's values.
    if choice.get("manual") is True and "manual_weight_adjusted" not in choice:
        return False
    pending_weight = choice.get("manual") is True and choice.get("weight") is None
    if not pending_weight and not fc_weight_needs_review(state):
        return False
    if choice.get("scenarios"):
        try:
            validate_choice(choice)
            updated = adapt_scenarios(choice, float(state.get("peso")))
            validate_choice(updated)
        except (TypeError, ValueError, OverflowError):
            return False
        apply_choice(state, updated, msil=msil, sync_weight=False)
        state["__full_standard_fattore_correzione"] = state["fattore_correzione"]
        return True
    try:
        lo, hi, previous_weight = validate_choice(
            {**choice, "weight": state.get("peso")} if pending_weight else choice
        )
        base = choice.get("base_range")
        # Older sessions have no base range. Never infer it from rounded bounds.
        original_manual = choice.get("manual") is True and base == [lo, hi]
        if not original_manual and adapt_fc_range(base, previous_weight) != [lo, hi]:
            return False
        weight = float(state.get("peso"))
        bounds = adapt_fc_range(base, weight)
        updated = {**choice, "range": bounds, "weight": weight,
                   "weight_adjusted": bounds != [lo, hi]}
        if choice.get("manual") is True:
            updated["manual_weight_adjusted"] = bounds != [lo, hi]
        validate_choice(updated)
    except (TypeError, ValueError, OverflowError):
        return False
    # In MSIL the weight widget has already been rendered. Only the FC changes.
    apply_choice(state, updated, msil=msil, sync_weight=False)
    if msil and choice.get("manual_center"):
        # Sopralluogo retains its documented +/- 0.10 around the entered FC.
        state.pop("__msil_fc_chosen_range", None)
    state["__full_standard_fattore_correzione"] = state["fattore_correzione"]
    return True


def fc_weight_needs_review(state):
    """Flag a changed weight when the FC has not been refreshed or reviewed."""
    choice = state.get("__fc_applied_choice")
    if not choice:
        return False
    try:
        previous = float(state.get("__fc_reviewed_weight", choice.get("weight")))
        current = float(state.get("peso"))
    except (TypeError, ValueError):
        return False
    return isfinite(previous) and isfinite(current) and abs(previous - current) > 1e-8


def fc_weight_warning(state):
    if fc_weight_needs_review(state):
        return "Peso modificato: ricontrollare il FC."
    choice = state.get("__fc_applied_choice") or {}
    if choice.get("weight_adjusted", choice.get("manual_weight_adjusted", False)):
        return "FC adattato per il peso."
    return None
