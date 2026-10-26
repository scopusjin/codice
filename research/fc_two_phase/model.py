"""Two-phase research calculation; deliberately not imported by the app.

Henssge 1981, pp. 159-162, equation III describes a *late* second phase.
Inferring the unmeasured transition temperature is our experimental extension.
All FC inputs must already be adjusted for body weight: no helper or state writes.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math

from research.fc_two_phase.reference import calcola_raffreddamento, cooling_coefficient


@dataclass(frozen=True)
class Inputs:
    rectal_c: float
    ambient_c: float
    weight_kg: float
    fc_before: float
    fc_after: float
    after_hours: float
    initial_c: float = 37.2


@dataclass(frozen=True)
class Result:
    status: str
    total_hours: float | None = None
    before_hours: float | None = None
    transition_c: float | None = None
    fast_term_fraction: float | None = None
    fast_term_gate: float = 0.01
    note: str = ""
    clinically_validated: bool = False


def _finite(value: float) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def single_phase_hours(temperature: float, inputs: Inputs, fc: float) -> float:
    """Reuse the app's unrounded point calculation, never its confidence limits."""
    return float(calcola_raffreddamento(
        temperature, inputs.ambient_c, inputs.initial_c, inputs.weight_kg, fc
    )[3])


def late_phase_elapsed(temperature: float, start_c: float, ambient_c: float,
                       coefficient: float) -> float:
    """Invert equation III with a KNOWN transition temperature (paper replay)."""
    if not all(_finite(v) for v in (temperature, start_c, ambient_c, coefficient)):
        raise ValueError("Finite numerical inputs are required.")
    if coefficient >= 0 or not ambient_c < temperature <= start_c:
        raise ValueError("Requires cooling above ambient and a negative coefficient.")
    return math.log((temperature - ambient_c) / (start_c - ambient_c)) / coefficient


def reconstruct(inputs: Inputs, *, max_fast_term_fraction: float = 0.01) -> Result:
    """Constant ambient, two chronological phases, known last-phase duration.

The adjustable 1% default is an engineering screen on the omitted exponential
term, NOT a published definition of plateau end or a clinical validity cutoff.
Even a passing result remains experimental. No confidence interval or FC to
apply to the app is produced. Unsupported cases have no PMI point output.
"""
    if not all(_finite(v) for v in asdict(inputs).values()):
        raise ValueError("All inputs must be finite real numbers (not booleans).")
    if not _finite(max_fast_term_fraction) or not 0 < max_fast_term_fraction < 0.2:
        raise ValueError("The diagnostic gate must be greater than 0 and less than 0.2.")
    if inputs.after_hours < 0:
        raise ValueError("The known duration cannot be negative.")
    b1 = cooling_coefficient(inputs.weight_kg, inputs.fc_before)
    b2 = cooling_coefficient(inputs.weight_kg, inputs.fc_after)

    def reject(status: str, note: str, **diagnostics: float) -> Result:
        return Result(status, fast_term_gate=max_fast_term_fraction, note=note, **diagnostics)

    if not 0 <= inputs.ambient_c <= 23:
        return reject("outside_temperature_scope", "Prototype restricted to ambient 0-23 C; no ambient changes.")
    if not inputs.ambient_c < inputs.rectal_c <= inputs.initial_c:
        return reject("incompatible_temperatures", "Requires ambient < measured <= initial temperature.")
    if inputs.rectal_c - inputs.ambient_c < 2:
        return reject("near_ambient", "Rectal-ambient difference below 2 C: outside this prototype's retained scope.")
    if inputs.after_hours > 160:
        return reject("outside_time_horizon", "Exceeds the app solver's 160-hour computational horizon.")

    # Merge identical phases exactly; an empty second phase has no thermal effect.
    if inputs.fc_before == inputs.fc_after or inputs.after_hours == 0:
        total = single_phase_hours(inputs.rectal_c, inputs, inputs.fc_before)
        if not math.isfinite(total):
            return reject("outside_time_horizon", "The existing single-phase solver returned no solution.")
        if inputs.after_hours > total + 1e-9:
            return reject("incompatible_duration", "The known postmortem phase would start before estimated death.")
        return Result("single_phase_reference", total, max(0.0, total-inputs.after_hours),
                      fast_term_gate=max_fast_term_fraction,
                      note="Exact reuse of the current single-phase calculation; no temporal extension applied.")

    # Inverse of T = Ta + (Tchange-Ta)*exp(B2*duration). Log form avoids overflow.
    log_q_change = math.log((inputs.rectal_c-inputs.ambient_c) /
                           (inputs.initial_c-inputs.ambient_c)) - b2*inputs.after_hours
    if log_q_change > 1e-12:
        return reject("incompatible_duration", "Reconstruction would exceed the assumed temperature at death.")
    transition = inputs.ambient_c + (inputs.initial_c-inputs.ambient_c)*math.exp(min(0.0, log_q_change))
    before = single_phase_hours(transition, inputs, inputs.fc_before)
    if not math.isfinite(before):
        return reject("outside_time_horizon", "The first-phase solver returned no solution.")

    # A=1.25, k=5 for the retained temperature branch: |second term|/first term.
    fraction = 0.2 * math.exp(4*b1*before)
    if fraction > max_fast_term_fraction:
        return reject("early_phase_requires_review",
                      "Omitted exponential term exceeds the selected numerical gate; PMI withheld. This is not a clinical plateau test.",
                      transition_c=transition, fast_term_fraction=fraction)
    total = before + inputs.after_hours
    if total > 160:
        return reject("outside_time_horizon", "Combined duration exceeds 160 hours.")
    return Result("experimental_two_phase", total, before, transition, fraction,
                  max_fast_term_fraction,
                  "Exploratory inverse reconstruction only. Passing the numerical gate does not establish scientific applicability.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rectal", type=float, required=True)
    parser.add_argument("--ambient", type=float, required=True)
    parser.add_argument("--weight", type=float, required=True)
    parser.add_argument("--fc-before", type=float, required=True)
    parser.add_argument("--fc-after", type=float, required=True)
    parser.add_argument("--hours-after-change", type=float, required=True)
    parser.add_argument("--initial", type=float, default=37.2)
    parser.add_argument("--fast-term-gate", type=float, default=0.01)
    args = parser.parse_args()
    try:
        inputs = Inputs(args.rectal, args.ambient, args.weight, args.fc_before,
                        args.fc_after, args.hours_after_change, args.initial)
        result = reconstruct(inputs, max_fast_term_fraction=args.fast_term_gate)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(asdict(result), indent=2, allow_nan=False))
    return 0 if result.total_hours is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
