"""Weight adaptation used by the FC panel, for updates outside that panel.

Keep this equivalent to adjust/bounds/roundRange in fc_panel_frontend/index.html.
The cross-language regression test checks the existing formula and thresholds.
"""

from math import exp, floor, isfinite, pow


def adapt_fc_range(base_range, weight):
    """Adapt the original bounds, never bounds already corrected for a weight."""
    if not isinstance(base_range, (list, tuple)) or len(base_range) != 2:
        raise ValueError("Intervallo FC di base non valido")
    lo, hi = map(float, base_range)
    weight = float(weight)
    if not all(isfinite(v) for v in (lo, hi, weight)):
        raise ValueError("Valori non validi")
    if lo < 0.35 or hi < lo or not 4 <= weight <= 150:
        raise ValueError("Verificare FC e peso")

    weight_applies = weight < 60 or weight > 80

    def adjust(value):
        if value < 1.4 or not weight_applies:
            return value
        denominator = (pow(weight, -0.625) - 0.028) * (-3.24596 * exp(-0.89959 * value)) - 0.0354
        if denominator >= 0:
            raise ValueError("Adattamento al peso non calcolabile")
        adapted = pow(-1.2815 / denominator, 1.6) / weight
        if not isfinite(adapted) or adapted <= 0:
            raise ValueError("Adattamento al peso non calcolabile")
        return adapted

    values = [adjust(lo), adjust(hi)]
    if weight_applies and lo < 1.4 <= hi:
        # The panel includes both sides of the discontinuity in the interval.
        values.extend((1.4, adjust(1.4)))
    # Same half-step tolerance as the panel's roundFC, including float noise.
    return [floor(v * 20 + 0.5 + 1e-10) / 20 for v in (min(values), max(values))]
