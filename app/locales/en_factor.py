"""English rendering of legacy corrective-factor summaries.

Input field names and values remain unchanged. Any free-text fallback supplied
by the caller must already be in the requested language.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def _surface_category_from_key(k: Optional[str]) -> Optional[str]:
    if not k or k == "INDIFFERENTE":
        return None
    if k in {"ISOLANTE", "FOGLIE_UMIDE", "FOGLIE_SECCHE"}:
        return "insulating"
    if k == "MOLTO_ISOLANTE":
        return "highly insulating"
    if k == "CONDUTTIVO":
        return "conductive"
    if k == "MOLTO_CONDUTTIVO":
        return "highly conductive"
    return None


def _format_state(state: Optional[str]) -> Optional[str]:
    if not state:
        return None
    if state == "Immerso":
        return "immersed body"
    if state == "Bagnato":
        return "wet body"
    return None


def _format_current(current: Optional[str]) -> Optional[str]:
    if not current or current == "/":
        return None
    current_low = current.lower()
    if "acqua corrente" in current_low:
        return "in flowing water"
    if "acqua stagnante" in current_low:
        return "in still water"
    if "correnti d'aria" in current_low or "con correnti" in current_low or "esposto a corrente" in current_low:
        return "in moving air"
    return None


def _format_clothing(thin: int, thick: int, state: Optional[str]) -> Optional[str]:
    if thin == 0 and thick == 0:
        return "unclothed" if state in ("Bagnato", "Immerso") else "unclothed body"
    if thick == 0:
        if 1 <= thin <= 2:
            return "wearing a few thin layers"
        if 3 <= thin <= 4:
            return "wearing several thin layers"
        if thin >= 5:
            return "wearing many thin layers"
    if thin == 0:
        if 1 <= thick <= 2:
            return "wearing a few thicker layers"
        if 3 <= thick <= 4:
            return "wearing several thicker layers"
        if thick >= 5:
            return "wearing many thicker layers"
    total = thin + thick
    if 1 <= total <= 2:
        return "wearing a few layers of varying thickness"
    if 3 <= total <= 4:
        return "wearing several layers of varying thickness"
    if total >= 5:
        return "wearing many layers of varying thickness"
    return None


def _format_blankets(medium: int, heavy: int, naked: bool) -> Optional[str]:
    if medium == 0 and heavy == 0:
        return None
    if medium > 0 and heavy == 0:
        if medium == 1:
            base = "under one medium-thickness blanket"
        elif medium == 2:
            base = "under two medium-thickness blankets"
        else:
            base = "under several medium-thickness blankets"
    elif heavy > 0 and medium == 0:
        if heavy == 1:
            base = "under one thick blanket"
        elif heavy == 2:
            base = "under two thick blankets"
        else:
            base = "under several thick blankets"
    else:
        total = medium + heavy
        if 1 <= total <= 2:
            base = "under a few blankets of varying thickness"
        elif 3 <= total <= 4:
            base = "under several blankets of varying thickness"
        else:
            base = "under many blankets of varying thickness"
    return ("unclothed body " + base) if naked else base


def factor_correction_description(*, cf_value: float, summary: Optional[Dict[str, Any]],
                                  fallback_text: Optional[str] = None, manual_override: bool = False) -> str:
    cf_text = f"{float(cf_value):.2f}"
    if manual_override:
        return cf_text
    if not summary:
        return (
            f"{cf_text} (based on the selected factors: {fallback_text})." if fallback_text
            else f"{cf_text} (to be adjusted on the basis of the selected factors)."
        )

    state = summary.get("stato")
    thin = int(summary.get("sottili", 0))
    thick = int(summary.get("spessi", 0))
    medium = int(summary.get("cop_medie", 0))
    heavy = int(summary.get("cop_pesanti", 0))
    surface_category = _surface_category_from_key(summary.get("superficie_key"))
    surface_text = f"lying on a thermally {surface_category} base" if surface_category else None
    current_value = summary.get("correnti")
    current_text = _format_current(current_value) if isinstance(current_value, str) else None
    parts = [part for part in (
        _format_state(state), _format_clothing(thin, thick, state),
        _format_blankets(medium, heavy, thin == 0 and thick == 0), surface_text, current_text,
    ) if part]
    weight_note = "The corrective factor has been adjusted for body weight." if summary.get("peso_adattato") else None
    if parts or weight_note:
        inner = ", ".join(parts)
        if weight_note:
            inner = (inner + ". " + weight_note) if inner else weight_note
        return f"{cf_text} ({inner})"
    return (
        f"{cf_text} (based on the selected factors: {fallback_text})." if fallback_text
        else f"{cf_text} (to be adjusted on the basis of the selected factors)."
    )
