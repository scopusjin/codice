# app/henssge.py
# -*- coding: utf-8 -*-
"""
Logica del raffreddamento (Henssge) e utilità correlate.
Contiene solo funzioni pure (nessuna dipendenza da Streamlit).
"""

from __future__ import annotations
from typing import List, Tuple
import numpy as np
from scipy.optimize import root_scalar

INF_HOURS = 200.0  # opzionale: utile per funzioni di supporto

def round_quarter_hour(x: float) -> float:
    """Arrotonda 'x' ore al quarto d’ora più vicino (0.25 h)."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    return np.round(x * 4) / 4.0

def calcola_raffreddamento(
    Tr: float, Ta: float, T0: float, W: float, CF: float
) -> Tuple[float, float, float, float, float]:
    """
    Calcola l'intervallo Henssge.
    Ritorna: (t_med, t_min, t_max, t_med_raw, Qd)

    - t_* sono in ore (t_min/max arrotondati al quarto d’ora).
    - Se non calcolabile, restituisce cinque NaN.
    """
    # Validazioni base
    if Tr is None or Ta is None or T0 is None or W is None or CF is None:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    temp_tolerance = 1e-6
    # Tr deve essere > Ta
    if Tr <= Ta + temp_tolerance:
        return np.nan, np.nan, np.nan, np.nan, np.nan
    # Denominatore non ~0
    if abs(T0 - Ta) < temp_tolerance:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    # Rapporto Qd (raffreddamento relativo)
    Qd = (Tr - Ta) / (T0 - Ta)
    if np.isnan(Qd) or Qd <= 0 or Qd > 1:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    # Parametri di Henssge
    A = 1.25 if Ta <= 23 else 10/9
    B = -1.2815 * (CF * W)**(-5/8) + 0.0284  # coeff. di raffreddamento

    def Qp(t: float) -> float:
        """Soluzione analitica del modello di raffreddamento."""
        try:
            if t < 0:
                return np.inf
            val = A * np.exp(B * t) + (1 - A) * np.exp((A / (A - 1)) * B * t)
            if np.isinf(val) or abs(val) > 1e10:
                return np.nan
            return val
        except Exception:
            return np.nan

    # Verifica se Qd è nel range della funzione
    qp_at_0 = Qp(0)
    qp_at_160 = Qp(160)
    eps = 1e-9
    if (np.isnan(qp_at_0) or np.isnan(qp_at_160)
        or not (min(qp_at_160, qp_at_0) - eps <= Qd <= max(qp_at_160, qp_at_0) + eps)):
        return np.nan, np.nan, np.nan, np.nan, np.nan

    # Radice per trovare t tale che Qp(t) = Qd
    try:
        sol = root_scalar(lambda t: Qp(t) - Qd, bracket=[0, 160], method='bisect')
        t_med_raw = sol.root
    except Exception:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    # Ampiezza dell’intervallo (Dt) secondo regole operative
    if Qd <= 0.2:
        Dt_raw = t_med_raw * 0.20                      # ±20% della media quando Qd è molto basso
    elif CF == 1:
        Dt_raw = 2.8 if Qd > 0.5 else 3.2 if Qd > 0.3 else 4.5
    else:
        Dt_raw = 2.8 if Qd > 0.5 else 4.5 if Qd > 0.3 else 7.0

    # Arrotondamenti e clamping minimo a 0
    t_med = round_quarter_hour(t_med_raw)
    t_min = round_quarter_hour(max(0.0, t_med_raw - Dt_raw))
    t_max = round_quarter_hour(t_med_raw + Dt_raw)

    return t_med, t_min, t_max, t_med_raw, Qd


def ranges_in_disaccordo_completa(
    r_inizio: List[float], r_fine: List[float]
) -> bool:
    """
    Ritorna True se almeno un intervallo (start,end) è completamente isolato
    (non si sovrappone con nessun altro), trattando NaN come -inf/+inf.
    """
    intervalli = []
    for start, end in zip(r_inizio, r_fine):
        s = start if not np.isnan(start) else -np.inf
        e = end if not np.isnan(end) else np.inf
        intervalli.append((s, e))

    for i, (s1, e1) in enumerate(intervalli):
        si_sovrappone = False
        for j, (s2, e2) in enumerate(intervalli):
            if i == j:
                continue
            if s1 <= e2 and s2 <= e1:
                si_sovrappone = True
                break
        if not si_sovrappone:
            return True
    return False


__all__ = [
    "INF_HOURS",
    "round_quarter_hour",
    "calcola_raffreddamento",
    "ranges_in_disaccordo_completa",
]

