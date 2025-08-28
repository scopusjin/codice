
# -*- coding: utf-8 -*-
# app/cautelativa.py — Stima cautelativa per raffreddamento (Henssge) su range.

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple, Optional, Dict, Any
import itertools
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from app.henssge import calcola_raffreddamento
from app.utils_time import arrotonda_quarto_dora   # <-- SOLO questa
from app.parameters import INF_HOURS

# ------------------------
# Costanti e default range
# ------------------------
DEFAULT_TA_DELTA = 1.0     # ±1 °C se range non specificato
DEFAULT_CF_DELTA = 0.1     # ±0.1   se range non specificato
DEFAULT_PESO_DELTA = 3.0   # ±3 kg se peso stimato

# Passi di discretizzazione predefiniti
DEFAULT_TA_STEP = 0.5
DEFAULT_CF_STEP = 0.05
DEFAULT_PESO_STEP = 1.0

# Limite di punti per dimensione per tenere le combinazioni gestibili
MAX_POINTS_PER_DIM = 25


@dataclass
class CautelativaResult:
    # Aggregati
    ore_min: float
    ore_max: float  # può valere INF_HOURS se applicata la regola 48–∞
    dt_min: Optional[datetime]
    dt_max: Optional[datetime]  # None se infinito
    qd_min: Optional[float]
    qd_max: Optional[float]
    # Dettagli
    n_combinazioni: int
    df_combinazioni: Optional[pd.DataFrame]
    # Riepilogo testuale
    summary_html: str
    parentetica: str


# ------------------------
# Utilità
# ------------------------
def _expand_range(value: float,
                  rng: Optional[Tuple[float, float]],
                  delta_if_none: float) -> Tuple[float, float]:
    if rng is None:
        return value - delta_if_none, value + delta_if_none
    a, b = rng
    return (min(a, b), max(a, b))


def _discretize(lo: float, hi: float, step: float,
                max_points: int = MAX_POINTS_PER_DIM) -> List[float]:
    if lo == hi:
        return [float(lo)]
    n = int(math.floor((hi - lo) / step)) + 1
    if n <= max_points:
        # Serie a step costante
        vals = [lo + i * step for i in range(n)]
        # Garantisce inclusione dell'estremo superiore
        if vals[-1] < hi - 1e-9:
            vals.append(hi)
        return [round(v, 6) for v in vals]
    # Sottocampionamento uniforme se troppi punti
    arr = np.linspace(lo, hi, max_points)
    return [float(round(v, 6)) for v in arr]


def _apply_rule_48_inf(ore_max: float) -> float:
    if ore_max is None:
        return INF_HOURS
    if ore_max > 48:
        return INF_HOURS
    return ore_max


def _to_datetimes(ore_min: float,
                  ore_max: float,
                  dt_ispezione: datetime) -> Tuple[Optional[datetime], Optional[datetime]]:

    def _is_inf(h: Optional[float]) -> bool:
        return (h is None) or (not math.isfinite(h)) or (h >= INF_HOURS - 1e-9)

    dt_min = None if _is_inf(ore_max) else arrotonda_quarto_dora(dt_ispezione - timedelta(hours=float(ore_max)))
    dt_max = None if _is_inf(ore_min) else arrotonda_quarto_dora(dt_ispezione - timedelta(hours=float(ore_min)))
    return dt_min, dt_max





# ------------------------
# Solver adapter
# ------------------------
def _default_solver(Ta: float, CF: float, peso_kg: float, **kwargs) -> Tuple[float, float, Optional[float]]:
    """
    Adattatore alla tua calcola_raffreddamento(Tr, Ta, T0, W, CF, round_minutes=...).
    Ritorna (ore_min, ore_max, Qd) per la combinazione corrente.
    """
    Tr = kwargs.get("Tr")
    T0 = kwargs.get("T0")
    round_minutes = kwargs.get("round_minutes", 30)

    # chiamata POSIZIONALE coerente con la tua app.henssge.calcola_raffreddamento
    t_med_round, t_min, t_max, t_med_raw, Qd = calcola_raffreddamento(
        Tr, Ta, T0, peso_kg, CF, round_minutes=round_minutes
    )

    ore_min = float(t_min)
    ore_max = float(t_max)
    qd = float(Qd) if (Qd is not None and np.isfinite(Qd)) else None
    return ore_min, ore_max, qd



# ------------------------
# Core
# ------------------------
def compute_raffreddamento_cautelativo(
    *,
    dt_ispezione: datetime,
    Ta_value: float,
    CF_value: float,
    peso_kg: float,
    # Opzioni di range opzionali
    Ta_range: Optional[Tuple[float, float]] = None,
    CF_range: Optional[Tuple[float, float]] = None,
    peso_stimato: bool = False,
    # Passi
    Ta_step: float = DEFAULT_TA_STEP,
    CF_step: float = DEFAULT_CF_STEP,
    peso_step: float = DEFAULT_PESO_STEP,
    # Controllo dimensioni
    max_points_per_dim: int = MAX_POINTS_PER_DIM,
    # Solver
    solver: Callable[..., Tuple[float, float, Optional[float]]] = _default_solver,
    solver_kwargs: Optional[Dict[str, Any]] = None,
    # Opzioni
    mostra_tabella: bool = True,
    applica_regola_48_inf: bool = True,
) -> CautelativaResult:
    """
    Esegue il prodotto cartesiano delle combinazioni (Ta, CF, peso) e aggrega il range.
    Se Ta_range/CF_range non sono specificati, usa ±1 °C e ±0.1.
    Se peso_stimato=True, usa ±3 kg. Altrimenti peso fisso.
    """
    solver_kwargs = solver_kwargs or {}

    # 1) Costruisci i range effettivi
    Ta_lo, Ta_hi = _expand_range(Ta_value, Ta_range, DEFAULT_TA_DELTA)
    CF_lo, CF_hi = _expand_range(CF_value, CF_range, DEFAULT_CF_DELTA)

    if peso_stimato:
        p_lo, p_hi = _expand_range(peso_kg, None, DEFAULT_PESO_DELTA)
    else:
        p_lo, p_hi = peso_kg, peso_kg

    # 2) Discretizza
    Ta_vals = _discretize(Ta_lo, Ta_hi, Ta_step, max_points_per_dim)
    CF_vals = _discretize(CF_lo, CF_hi, CF_step, max_points_per_dim)
    P_vals = _discretize(p_lo, p_hi, peso_step, max_points_per_dim)

    # 3) Itera combinazioni
    recs: List[Dict[str, Any]] = []
    ore_mins: List[float] = []
    ore_maxs: List[float] = []
    qds: List[float] = []

    for Ta, CF, P in itertools.product(Ta_vals, CF_vals, P_vals):
        ore_min, ore_max, qd = solver(Ta=Ta, CF=CF, peso_kg=P, **solver_kwargs)

        # Normalizzazione
        if ore_min < 0:
            ore_min = 0.0
        if ore_max < ore_min:
            ore_max = ore_min

        ore_mins.append(ore_min)
        ore_maxs.append(ore_max)
        if qd is not None and math.isfinite(qd):
            qds.append(qd)

        if mostra_tabella:
            recs.append({
                "Ta": Ta,
                "CF": CF,
                "peso_kg": P,
                "ore_min": ore_min,
                "ore_max": ore_max,
                "Qd": qd,
            })

    # 4) Aggregati
    agg_min = float(min(ore_mins)) if ore_mins else float("inf")
    agg_max_raw = float(max(ore_maxs)) if ore_maxs else float("inf")
    agg_max = _apply_rule_48_inf(agg_max_raw) if applica_regola_48_inf else agg_max_raw

    qd_min = float(min(qds)) if qds else None
    qd_max = float(max(qds)) if qds else None

    # 5) Datetime range relativo all’ispezione
    dt_min, dt_max = _to_datetimes(agg_min, agg_max, dt_ispezione)

    # 6) Tabella combinazioni opzionale
    df = pd.DataFrame.from_records(recs) if (mostra_tabella and recs) else None

    # 7) Frasi di riepilogo e parentetica
    summary = build_summary_html(
        Ta_lo, Ta_hi, CF_lo, CF_hi, p_lo, p_hi,
        agg_min, agg_max, dt_min, dt_max, qd_min, qd_max,
        peso_stimato=peso_stimato, agg_max_raw=agg_max_raw,
    )
    paren = build_parentetica_cautelativa(
        Ta_lo, Ta_hi, CF_lo, CF_hi, p_lo, p_hi, peso_stimato
    )

    return CautelativaResult(
        ore_min=agg_min,
        ore_max=agg_max,
        dt_min=dt_min,
        dt_max=dt_max if math.isfinite(agg_max) else None,
        qd_min=qd_min,
        qd_max=qd_max,
        n_combinazioni=len(recs) if recs else (len(Ta_vals)*len(CF_vals)*len(P_vals)),
        df_combinazioni=df,
        summary_html=summary,
        parentetica=paren,
    )


# ------------------------
# Frasi di riepilogo
# ------------------------
def _fmt_range(a: float, b: float, unit: str) -> str:
    if abs(a - b) < 1e-9:
        return f"{a:g} {unit}"
    return f"{a:g}–{b:g} {unit}"


def _fmt_dt(dt: Optional[datetime]) -> str:
    if dt is None:
        return "∞"
    return dt.strftime("%d.%m.%Y, %H:%M")


def build_summary_html(
    Ta_lo: float, Ta_hi: float,
    CF_lo: float, CF_hi: float,
    p_lo: float, p_hi: float,
    ore_min: float, ore_max: float,
    dt_min: Optional[datetime], dt_max: Optional[datetime],
    qd_min: Optional[float], qd_max: Optional[float],
    *, peso_stimato: bool, agg_max_raw: float
) -> str:
    # Formattazioni base
    ta_txt = _fmt_range(round(Ta_lo, 2), round(Ta_hi, 2), "°C")
    cf_txt = _fmt_range(round(CF_lo, 3), round(CF_hi, 3), "")

    # Peso: se "stimato" mostra SEMPRE il range + (stimato),
    # altrimenti se non stimato e i limiti coincidono mostra singolo valore.
    if peso_stimato:
        p_txt = _fmt_range(round(p_lo, 1), round(p_hi, 1), "kg") + " (stimato)"
    else:
        if abs(p_lo - p_hi) < 1e-9:
            p_txt = f"{round(p_lo, 1):g} kg"
        else:
            p_txt = _fmt_range(round(p_lo, 1), round(p_hi, 1), "kg")

    # Frase risultato nello stile dell’app:
    # - aperto all’infinito  -> "superiore a X ore"
    # - da 0 a limite        -> "entro Y ore"
    # - intervallo chiuso    -> "tra circa X e Y ore"
    if ore_max >= INF_HOURS - 1e-9:
        risultato_txt = f"superiore a {ore_min:g} ore"
    elif ore_min <= 1e-9:
        risultato_txt = f"entro {ore_max:g} ore"
    else:
        risultato_txt = f"tra circa {ore_min:g} e {ore_max:g} ore"

    # Corpo testuale: intestazione + elenco puntato + frase finale + (intervallo datetimes) + (Qd)
    header = (
        "Per quanto attiene la valutazione del raffreddamento cadaverico, "
        "sono stati considerati i parametri di seguito indicati."
    )
    bullets = (
        "<ul>"
        f"<li>Range di temperature ambientali considerato per valutare la temperatura ambientale media: <b>{ta_txt}</b>.</li>"
        f"<li>Fattore di correzione stimato come compreso tra: <b>{cf_txt}</b>.</li>"
        f"<li>Peso corporeo considerato: <b>{p_txt}</b>.</li>"
        "</ul>"
    )
    conclusione = (
        "Applicando l'equazione di Henssge, è possibile stimare che il decesso "
        f"sia avvenuto {risultato_txt} prima dei rilievi effettuati al momento "
        "dell’ispezione legale."
    )

    intervallo_dt = f"Intervallo temporale corrispondente: <b>{_fmt_dt(dt_min)} – {_fmt_dt(dt_max)}</b>."
    qd_line = f"Qd aggregato: <b>{qd_min:.3f}–{qd_max:.3f}</b>." if (qd_min is not None and qd_max is not None) else ""

    parts = [header, bullets, conclusione, intervallo_dt]
    if qd_line:
        parts.append(qd_line)

    return "<br>".join(parts)




def build_parentetica_cautelativa(
    Ta_lo: float, Ta_hi: float,
    CF_lo: float, CF_hi: float,
    p_lo: float, p_hi: float,
    peso_stimato: bool
) -> str:
    """
    Parentetica breve e standardizzata per la frase complessiva.
    Esempio: "(raffreddamento stimato su Ta 18–20 °C, CF 1.2–1.3, peso 68–74 kg)"
    """
    ta_txt = _fmt_range(round(Ta_lo, 2), round(Ta_hi, 2), "°C")
    cf_txt = _fmt_range(round(CF_lo, 3), round(CF_hi, 3), "")
    p_txt = _fmt_range(round(p_lo, 1), round(p_hi, 1), "kg")
    suffix = ", peso stimato" if peso_stimato else ""
    return f"(raffreddamento stimato su Ta {ta_txt}, CF {cf_txt}, peso {p_txt}{suffix})"


# ------------------------
# Hook per Streamlit (facoltativo)
# ------------------------
def render_tabella_combinazioni(df: pd.DataFrame) -> None:
    """
    Mostra una tabella compatta con colonne essenziali.
    Integra dove già mostri le tabelle opzionali.
    """
    import streamlit as st
    if df is None or df.empty:
        return
    with st.expander(f"Combinazioni calcolate ({len(df)})"):
        st.dataframe(
            df[["Ta", "CF", "peso_kg", "ore_min", "ore_max", "Qd"]]
              .sort_values(["ore_min", "ore_max"]).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )
