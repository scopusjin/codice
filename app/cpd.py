# -*- coding: utf-8 -*-
"""Conditional Probability Distribution (CPD) for Henssge estimates.

Implements the construction described by Biermann & Potente (2011):
the Gaussian distribution underlying the nomogram interval is conditioned
on the time interval in which death is possible, then the narrowest
continuous interval containing 95.45% probability is selected.

All times are expressed as hours since death at the temperature measurement:
larger values are further in the past.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import norm


DEFAULT_TARGET_PROBABILITY = 0.9545


@dataclass(frozen=True)
class CPDResult:
    mean_hours: float
    sd_hours: float
    support_low_hours: float
    support_high_hours: float
    prior_mass_in_support: float
    excluded_prior_mass: float
    target_probability: float
    unconditional_low_hours: float
    unconditional_high_hours: float
    cpd_low_hours: float
    cpd_high_hours: float

    @property
    def cpd_width_hours(self) -> float:
        return self.cpd_high_hours - self.cpd_low_hours

    @property
    def support_width_hours(self) -> float:
        if math.isinf(self.support_high_hours):
            return math.inf
        return self.support_high_hours - self.support_low_hours


def build_cpd(
    *,
    mean_hours: float,
    sd_hours: float,
    lower_hours: float = 0.0,
    upper_hours: float = math.inf,
    target_probability: float = DEFAULT_TARGET_PROBABILITY,
) -> CPDResult:
    """Construct the shortest conditional interval with target probability.

    lower_hours and upper_hours are hard limits on the possible time since
    death at measurement. The default lower limit of 0 hours encodes the
    known fact that death had already occurred when temperature was measured.
    """
    mean_hours = float(mean_hours)
    sd_hours = float(sd_hours)
    lower_hours = float(lower_hours)
    upper_hours = float(upper_hours)
    target_probability = float(target_probability)

    if not np.isfinite(mean_hours):
        raise ValueError("Stima centrale Henssge non valida.")
    if not np.isfinite(sd_hours) or sd_hours <= 0:
        raise ValueError("Deviazione standard Henssge non valida.")
    if not np.isfinite(lower_hours):
        raise ValueError("Il limite minimo del TSD deve essere finito.")
    if math.isnan(upper_hours):
        raise ValueError("Il limite massimo del TSD non è valido.")
    if lower_hours < 0:
        raise ValueError("Il limite minimo del TSD non può essere negativo.")
    if upper_hours <= lower_hours:
        raise ValueError("Le condizioni non lasciano alcun intervallo temporale possibile.")
    if not (0 < target_probability < 1):
        raise ValueError("La probabilità bersaglio deve essere compresa tra 0 e 1.")

    def prior_cdf(x: float) -> float:
        return float(norm.cdf((x - mean_hours) / sd_hours))

    f_low = prior_cdf(lower_hours)
    f_high = 1.0 if math.isinf(upper_hours) else prior_cdf(upper_hours)
    remaining = f_high - f_low

    if not np.isfinite(remaining) or remaining <= 1e-14:
        raise ValueError(
            "La distribuzione Henssge attribuisce una probabilità numericamente nulla "
            "all’intervallo consentito dalle condizioni."
        )

    def cond_quantile(p: float) -> float:
        if p <= 0:
            return lower_hours
        if p >= 1:
            return upper_hours
        prior_p = f_low + p * remaining
        prior_p = min(max(prior_p, np.finfo(float).eps), 1.0 - np.finfo(float).eps)
        return float(mean_hours + sd_hours * norm.ppf(prior_p))

    max_start = 1.0 - target_probability

    def interval_width(start_p: float) -> float:
        left = cond_quantile(start_p)
        right = cond_quantile(start_p + target_probability)
        return right - left

    candidates = [0.0, max_start]
    if max_start > 1e-12:
        opt = minimize_scalar(
            interval_width,
            bounds=(0.0, max_start),
            method="bounded",
            options={"xatol": 1e-12},
        )
        if opt.success and np.isfinite(opt.x):
            candidates.append(float(opt.x))

    best_start = min(candidates, key=interval_width)
    cpd_low = cond_quantile(best_start)
    cpd_high = cond_quantile(best_start + target_probability)

    return CPDResult(
        mean_hours=mean_hours,
        sd_hours=sd_hours,
        support_low_hours=lower_hours,
        support_high_hours=upper_hours,
        prior_mass_in_support=remaining,
        excluded_prior_mass=1.0 - remaining,
        target_probability=target_probability,
        unconditional_low_hours=mean_hours - 2.0 * sd_hours,
        unconditional_high_hours=mean_hours + 2.0 * sd_hours,
        cpd_low_hours=cpd_low,
        cpd_high_hours=cpd_high,
    )


def density_values(result: CPDResult, x_hours):
    """Return prior and conditional density values for plotting."""
    x = np.asarray(x_hours, dtype=float)
    prior = norm.pdf((x - result.mean_hours) / result.sd_hours) / result.sd_hours
    in_support = x >= result.support_low_hours
    if not math.isinf(result.support_high_hours):
        in_support &= x <= result.support_high_hours
    conditional = np.where(in_support, prior / result.prior_mass_in_support, 0.0)
    return prior, conditional


__all__ = [
    "CPDResult",
    "DEFAULT_TARGET_PROBABILITY",
    "build_cpd",
    "density_values",
]
