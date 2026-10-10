"""Combine independent FC scenarios without changing scientific calculations."""

from copy import deepcopy

from app.fc_weight import adapt_fc_range


def summarize_scenarios(scenarios):
    bounds = [min(item["range"][0] for item in scenarios),
              max(item["range"][1] for item in scenarios)]
    descriptions = []
    for index, value in enumerate(bounds):
        texts = dict.fromkeys(item["description"] for item in scenarios
                              if item["range"][index] == value)
        descriptions.append(" / ".join(texts))
    text = (f"FC degli scenari considerati: {bounds[0]:.2f} [{descriptions[0]}]"
            f" — {bounds[1]:.2f} [{descriptions[1]}]")
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
