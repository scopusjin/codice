# app/henssge.py
from __future__ import annotations
from typing import List, Tuple
import numpy as np
from scipy.optimize import root_scalar
from app.cooling_inputs import finite_number

INF_HOURS = 200.0  # opzionale

def round_to_step_minutes(x: float, step_minutes: int = 15) -> float:
    """Arrotonda 'x' ore allo step in minuti (6, 15, 30...)."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    step_hours = step_minutes / 60.0
    return np.round(x / step_hours) * step_hours

def round_quarter_hour(x: float) -> float:
    """Compat: quarto d’ora (15 min)."""
    return round_to_step_minutes(x, 15)

def cooling_coefficient(weight: float, fc: float) -> float:
    """Require the decreasing cooling branch; there is no fixed FC ceiling."""
    message = "La combinazione di FC e peso non consente il calcolo con questa formula. Verificare i valori."
    if not all(finite_number(v) and float(v) > 0 for v in (weight, fc)):
        raise ValueError(message)
    product = float(weight) * float(fc)
    if not np.isfinite(product) or product <= 0:
        raise ValueError(message)
    coefficient = -1.2815 * product ** (-5 / 8) + 0.0284
    if not np.isfinite(coefficient) or coefficient >= 0:
        raise ValueError(message)
    return coefficient


def calcola_raffreddamento(
    Tr: float, Ta: float, T0: float, W: float, CF: float, *,
    round_minutes: int = 30   # default 30 min
) -> Tuple[float, float, float, float, float]:
    """
    Ritorna: (t_med, t_min, t_max, t_med_raw, Qd)
    t_min/max/med sono arrotondati allo step scelto.
    """
    # Validazioni base
    if not all(finite_number(v) for v in (Tr, Ta, T0, W, CF)):
        return np.nan, np.nan, np.nan, np.nan, np.nan
    Tr, Ta, T0, W, CF = map(float, (Tr, Ta, T0, W, CF))
    if W <= 0 or CF <= 0:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    temp_tolerance = 1e-6
    if Tr <= Ta + temp_tolerance:
        return np.nan, np.nan, np.nan, np.nan, np.nan
    if abs(T0 - Ta) < temp_tolerance:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    Qd = (Tr - Ta) / (T0 - Ta)
    if np.isnan(Qd) or Qd <= 0 or Qd > 1:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    # Evita che l'errore floating-point sposti valori matematicamente esatti
    # dall'altro lato delle soglie Qd usate dal metodo e dalla presentazione.
    for qd_boundary in (0.2, 0.3, 0.5):
        if np.isclose(Qd, qd_boundary, rtol=0.0, atol=1e-12):
            Qd = qd_boundary
            break

    A = 1.25 if Ta <= 23 else 10/9
    try:
        B = cooling_coefficient(W, CF)
    except ValueError:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    def Qp(t: float) -> float:
        if t < 0:
            return np.inf
        try:
            val = A*np.exp(B*t) + (1 - A)*np.exp((A/(A-1))*B*t)
            return np.nan if np.isinf(val) or abs(val) > 1e10 else val
        except Exception:
            return np.nan

    qp_at_0, qp_at_160 = Qp(0), Qp(160)
    eps = 1e-9
    if (np.isnan(qp_at_0) or np.isnan(qp_at_160)
        or not (min(qp_at_160, qp_at_0)-eps <= Qd <= max(qp_at_160, qp_at_0)+eps)):
        return np.nan, np.nan, np.nan, np.nan, np.nan

    try:
        sol = root_scalar(lambda t: Qp(t) - Qd, bracket=[0, 160], method='bisect')
        t_med_raw = sol.root
    except Exception:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    if Qd <= 0.2:
        Dt_raw = t_med_raw * 0.20
    elif CF == 1:
        Dt_raw = 2.8 if Qd > 0.5 else 3.2 if Qd > 0.3 else 4.5
    else:
        Dt_raw = 2.8 if Qd > 0.5 else 4.5 if Qd > 0.3 else 7.0

    # Arrotondamento configurabile
    t_med = round_to_step_minutes(t_med_raw, round_minutes)
    t_min = round_to_step_minutes(max(0.0, t_med_raw - Dt_raw), round_minutes)
    t_max = round_to_step_minutes(t_med_raw + Dt_raw, round_minutes)

    return t_med, t_min, t_max, t_med_raw, Qd

def ranges_in_disaccordo_completa(r_inizio: List[float], r_fine: List[float]) -> bool:
    intervalli = []
    for start, end in zip(r_inizio, r_fine):
        s = start if not np.isnan(start) else -np.inf
        e = end if not np.isnan(end) else np.inf
        intervalli.append((s, e))
    for i, (s1, e1) in enumerate(intervalli):
        if not any(i != j and s1 <= e2 and s2 <= e1 for j, (s2, e2) in enumerate(intervalli)):
            return True
    return False

__all__ = [
    "INF_HOURS",
    "round_quarter_hour",
    "round_to_step_minutes",
    "calcola_raffreddamento",
    "cooling_coefficient",
    "ranges_in_disaccordo_completa",
]
