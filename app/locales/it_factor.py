# -*- coding: utf-8 -*-
"""Testi italiani per la descrizione del fattore di correzione.

Il modulo contiene soltanto rendering testuale/presentazionale. Le regole di
calcolo del fattore di correzione restano in ``app.factor_calc``.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


_SURF_INDIFF = "INDIFFERENTE"
_SURF_ISOL = "ISOLANTE"
_SURF_MOLTOI = "MOLTO_ISOLANTE"
_SURF_COND = "CONDUTTIVO"
_SURF_MOLTOC = "MOLTO_CONDUTTIVO"
_SURF_FOGLIU = "FOGLIE_UMIDE"
_SURF_FOGLIS = "FOGLIE_SECCHE"


def _surface_category_from_key(k: Optional[str]) -> Optional[str]:
    if not k or k == _SURF_INDIFF:
        return None
    if k in {_SURF_ISOL, _SURF_FOGLIU, _SURF_FOGLIS}:
        return "isolante"
    if k == _SURF_MOLTOI:
        return "molto isolante"
    if k == _SURF_COND:
        return "conduttiva"
    if k == _SURF_MOLTOC:
        return "molto conduttiva"
    return None


def _format_state(state: Optional[str]) -> Optional[str]:
    if not state:
        return None
    if state == "Immerso":
        return "corpo immerso"
    if state == "Bagnato":
        return "corpo bagnato"
    return None


def _format_current(current: Optional[str]) -> Optional[str]:
    if not current or current == "/":
        return None
    current_low = current.lower()
    if "acqua corrente" in current_low:
        return "in acqua corrente"
    if "acqua stagnante" in current_low:
        return "in acqua stagnante"
    if "correnti d'aria" in current_low or "con correnti" in current_low or "esposto a corrente" in current_low:
        return "con correnti d'aria"
    return None


def _format_clothing(thin: int, thick: int, state: Optional[str]) -> Optional[str]:
    if thin == 0 and thick == 0:
        if state in ("Bagnato", "Immerso"):
            return "nudo"
        return "corpo nudo"
    if thick == 0:
        if 1 <= thin <= 2:
            return "con indosso pochi strati leggeri"
        if 3 <= thin <= 4:
            return "con indosso alcuni strati leggeri"
        if thin >= 5:
            return "con indosso molti strati leggeri"
    if thin == 0:
        if 1 <= thick <= 2:
            return "con indosso pochi strati pesanti"
        if 3 <= thick <= 4:
            return "con indosso vari strati pesanti"
        if thick >= 5:
            return "con indosso molti strati pesanti"
    total = thin + thick
    if 1 <= total <= 2:
        return "con indosso pochi strati di vario spessore"
    if 3 <= total <= 4:
        return "con indosso alcuni strati di vario spessore"
    if total >= 5:
        return "con indosso molti strati di vario spessore"
    return None


def _format_blankets(medium: int, heavy: int, naked: bool) -> Optional[str]:
    if medium == 0 and heavy == 0:
        return None
    if medium > 0 and heavy == 0:
        if medium == 1:
            base = "sotto una coperta di medio spessore"
        elif medium == 2:
            base = "sotto due coperte di medio spessore"
        else:
            base = "sotto varie coperte di medio spessore"
        return ("corpo nudo " + base) if naked else base
    if heavy > 0 and medium == 0:
        if heavy == 1:
            base = "sotto una coperta pesante"
        elif heavy == 2:
            base = "sotto due coperte pesanti"
        else:
            base = "sotto varie coperte pesanti"
        return ("corpo nudo " + base) if naked else base
    total = medium + heavy
    if 1 <= total <= 2:
        base = "sotto poche coperte di diverso spessore"
    elif 3 <= total <= 4:
        base = "sotto alcune coperte di diverso spessore"
    else:
        base = "sotto molte coperte di diverso spessore"
    return ("corpo nudo " + base) if naked else base


def factor_correction_description(
    *,
    cf_value: float,
    summary: Optional[Dict[str, Any]],
    fallback_text: Optional[str] = None,
    manual_override: bool = False,
) -> str:
    cf_text = f"{float(cf_value):.2f}"

    if manual_override:
        return cf_text

    if not summary:
        return (
            f"{cf_text} (in base ai fattori scelti: {fallback_text})."
            if fallback_text
            else f"{cf_text} (da adattare sulla base dei fattori scelti)."
        )

    state = summary.get("stato")
    state_text = _format_state(state)

    thin = int(summary.get("sottili", 0))
    thick = int(summary.get("spessi", 0))
    clothing_text = _format_clothing(thin, thick, state)

    medium = int(summary.get("cop_medie", 0))
    heavy = int(summary.get("cop_pesanti", 0))
    naked = thin == 0 and thick == 0
    blankets_text = _format_blankets(medium, heavy, naked)

    surface_category = _surface_category_from_key(summary.get("superficie_key"))
    surface_text = (
        f"adagiato su superficie termicamente {surface_category}"
        if surface_category
        else None
    )

    current_value = summary.get("correnti")
    current_text = _format_current(current_value) if isinstance(current_value, str) else None

    parts = [
        part
        for part in (state_text, clothing_text, blankets_text, surface_text, current_text)
        if part
    ]

    weight_note = (
        "Il fattore di correzione è stato adattato per il peso corporeo."
        if summary.get("peso_adattato")
        else None
    )

    if parts or weight_note:
        inner = ", ".join(parts)
        if weight_note:
            inner = (inner + ". " + weight_note) if inner else weight_note
        return f"{cf_text} ({inner})"

    return (
        f"{cf_text} (in base ai fattori scelti: {fallback_text})."
        if fallback_text
        else f"{cf_text} (da adattare sulla base dei fattori scelti)."
    )


__all__ = ["factor_correction_description"]
