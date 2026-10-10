"""Combine independent FC scenarios without changing scientific calculations."""

from copy import deepcopy

from app.fc_weight import adapt_fc_range
from app.cooling_inputs import finite_number


def scenario_conditions(item):
    # Keep previously saved drafts consistent with the compact summary.
    text = item["description"].replace(", FC impostato manualmente", "")
    text = text.replace(", aria ferma", "").replace(", movimento dell’aria non ricostruibile", "")
    text = text.replace(", prossima a 0 °C", "")
    return text.replace(", su pavimento interno", ", adagiato su pavimento").replace(
        ", su normale pavimento interno", ", adagiato su pavimento")


def scenario_temperature_bounds(choice):
    scenarios = choice.get("scenarios") or []
    if not scenarios or not any("temperature" in item for item in scenarios):
        return None  # Previously saved FC-only scenarios keep their former behavior.
    if not all(finite_number(item.get("temperature")) for item in scenarios):
        raise ValueError("Specificare la temperatura di ogni scenario.")
    values = [float(item["temperature"]) for item in scenarios]
    return min(values), max(values)


def summarize_scenarios(scenarios):
    bounds = [min(item["range"][0] for item in scenarios),
              max(item["range"][1] for item in scenarios)]
    descriptions = []
    for index, value in enumerate(bounds):
        texts = dict.fromkeys(scenario_conditions(item) for item in scenarios
                              if item["range"][index] == value)
        descriptions.append(" / ".join(texts))
    text = (f"FC degli scenari considerati: {bounds[0]:.2f} ({descriptions[0]})"
            f" — {bounds[1]:.2f} ({descriptions[1]})")
    return bounds, text


def scenario_draft(choice):
    """Keep the active editor separate from the overall range on reopening."""
    draft = deepcopy(choice.get("draft") or {})
    scenarios = [deepcopy(item["draft"]) for item in choice["scenarios"]]
    active = draft.get("activeScenario", 0)
    if not isinstance(active, int) or not 0 <= active < len(scenarios):
        active = 0
    return {**draft, **scenarios[active], "multiple": True,
            "activeScenario": active, "scenarios": scenarios,
            "scenarioWeightAdjusted": bool(choice.get("weight_adjusted"))}


def adapt_scenarios(choice, weight):
    """Adapt EACH original base before combining; never adapt the envelope."""
    scenarios = []
    for item in choice["scenarios"]:
        base, previous = item.get("base_range"), item["range"]
        original_manual = item.get("manual") is True and base == previous
        if not original_manual and adapt_fc_range(base, item["weight"]) != previous:
            raise ValueError("Base del FC dello scenario non coerente.")
        bounds = adapt_fc_range(base, weight)
        changed = bounds != previous
        updated = {**item, "range": bounds, "weight": weight,
                   "weight_adjusted": changed,
                   "manual_weight_adjusted": bool(item.get("manual") and changed)}
        updated["draft"] = {**item["draft"], "lo": f"{bounds[0]:.2f}",
                            "hi": f"{bounds[1]:.2f}", "weight": weight,
                            "manual": bool(item.get("manual")),
                            "manualBase": base if item.get("manual") else None,
                            "selectedBase": base if not item.get("manual") else None,
                            "manualWeightAdjusted": updated["manual_weight_adjusted"],
                            "weightAdjusted": changed}
        scenarios.append(updated)
    bounds, description = summarize_scenarios(scenarios)
    updated = {**choice, "range": bounds, "weight": weight, "scenarios": scenarios,
               "description": description, "weight_adjusted": bounds != choice["range"]}
    updated["draft"] = scenario_draft(updated)
    return updated


def matching_scenario_description(state, bounds, weight):
    """Do not attach old scenario conditions to a different calculation."""
    choice = state.get("__fc_applied_choice") or {}
    if (not choice.get("scenarios") or choice.get("range") != list(bounds)
            or choice.get("weight") != weight):
        return None
    return summarize_scenarios(choice["scenarios"])[1]


def matching_temperature_scenarios(state, bounds, weight, temperatures):
    """Reject stale temperatures instead of silently crossing unrelated inputs."""
    if matching_scenario_description(state, bounds, weight) is None:
        return None
    choice = state["__fc_applied_choice"]
    expected = scenario_temperature_bounds(choice)
    if expected is None:
        return None
    if tuple(temperatures) != expected:
        raise ValueError("Temperature modificate: aggiornare le temperature nel pannello Più scenari.")
    return [(float(item["temperature"]), item["range"]) for item in choice["scenarios"]]


def manual_fc_note(state, bounds, weight):
    choice = state.get("__fc_applied_choice") or {}
    if choice.get("range") != list(bounds) or choice.get("weight") != weight:
        return None
    if choice.get("scenarios"):
        indices = [str(i) for i, item in enumerate(choice["scenarios"], 1) if item.get("manual")]
        if indices:
            label = "nello scenario " if len(indices) == 1 else "negli scenari "
            return "FC impostato manualmente " + label + ", ".join(indices) + "."
    elif choice.get("manual"):
        return "FC impostato manualmente dall’operatore."
    return None
