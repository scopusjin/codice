# -*- coding: utf-8 -*-
"""Orchestrazione del raffreddamento cadaverico usata da ``app.graphing``.

Il modulo separa la gestione Henssge standard/prudente dal rendering e dalla
combinazione con gli altri parametri tanatologici. Formule, soglie e testi
restano quelli già utilizzati dal motore grafico.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import streamlit as st

from app import i18n
from app.cautelativa import compute_raffreddamento_cautelativo
from app.henssge import calcola_raffreddamento
from app.parameters import INF_HOURS
from app.textgen import paragrafo_raffreddamento_dettaglio
from app.utils_time import round_quarter_hour


def _is_num(x):
    return x is not None and not (isinstance(x, float) and np.isnan(x))


def _classify_qd_for_ta(ta, qd) -> str | None:
    """Classifica Qd usando la soglia pertinente alla Ta della combinazione."""
    if not _is_num(ta) or not _is_num(qd):
        return None

    ta = float(ta)
    qd = float(qd)
    if ta <= 23.0:
        if qd <= 0.2:
            return "outside"
        if qd < 0.3:
            return "intermediate"
        return "optimal"

    return "outside" if qd <= 0.5 else "optimal"


def _aggregate_qd_status(counts: dict[str, int]) -> str | None:
    """Riassume la distribuzione delle combinazioni senza produrre testi UI."""
    total = sum(counts.values())
    if total == 0:
        return None
    if counts["optimal"] == total:
        return "all_optimal"
    if counts["optimal"] > 0:
        return "mixed"
    if counts["intermediate"] > 0:
        return "no_optimal_intermediate"
    return "all_outside"


@dataclass(frozen=True)
class CoolingState:
    Tr_val: object
    Ta_val: object
    T0_val: object
    W_val: object
    CF_val: object
    t_min_raff_henssge: float
    t_max_raff_henssge: float
    t_med_raff_henssge_rounded_raw: float
    t_med_raff_henssge_rounded: float
    Qd_val_check: float
    Qd_min: float
    Qd_max: float
    qd_range_status: str | None
    qd_status_counts: tuple[tuple[str, int], ...]
    raffreddamento_calcolabile: bool
    Ta_for_pot: float
    qd_threshold: float
    gate_fail: bool
    detail_blocks: tuple[str, ...]


def compute_cooling_state(
    *,
    input_rt,
    input_ta,
    input_tm,
    input_w,
    fattore_correzione,
    data_ora_ispezione: datetime.datetime,
    skip_warnings: bool,
) -> CoolingState:
    # --- normalizza locali; modalità silenziosa disattiva Henssge se mancano input ---
    Tr_val, Ta_val, T0_val, W_val, CF_val = input_rt, input_ta, input_tm, input_w, fattore_correzione

    # placeholder valori calcolati
    t_min_raff_henssge = np.nan
    t_max_raff_henssge = np.nan
    t_med_raff_henssge_rounded_raw = np.nan
    t_med_raff_henssge_rounded = np.nan
    Qd_val_check = np.nan
    Qd_min = np.nan
    Qd_max = np.nan
    qd_range_status = None
    qd_status_counts: tuple[tuple[str, int], ...] = ()
    raffreddamento_calcolabile = True
    detail_blocks: list[str] = []

    if skip_warnings and (
        W_val is None or W_val <= 0 or any(v is None for v in [Tr_val, Ta_val, T0_val])
    ):
        Tr_val = Ta_val = T0_val = W_val = CF_val = np.nan
        raffreddamento_calcolabile = False

    #
    # Ta di riferimento e soglia Qd (prudente → usa Ta_max)
    if _is_num(Ta_val):
        Ta_for_pot = float(st.session_state.get("Ta_max_beta", Ta_val)) \
                     if st.session_state.get("stima_cautelativa_beta", False) else float(Ta_val)
    else:
        Ta_for_pot = np.nan

    qd_threshold = 0.2 if (_is_num(Ta_for_pot) and Ta_for_pot <= 23) else 0.5
    # --- Gate fisico: abilita Henssge solo se Tr ≥ Ta (alla 1ª cifra) + 0.10 ---
    gate_fail = False
    if _is_num(Tr_val) and _is_num(Ta_val):
        tr_dec = Decimal(str(Tr_val)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        ta_dec = Decimal(str(Ta_val)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        diff_dec = tr_dec - ta_dec  # differenza arrotondata a 0.1 °C
        if diff_dec < Decimal("0.1"):
            raffreddamento_calcolabile = False
            gate_fail = True
            t_min_raff_henssge = np.nan
            t_max_raff_henssge = np.nan
            t_med_raff_henssge_rounded_raw = np.nan
            t_med_raff_henssge_rounded = np.nan
            Qd_val_check = np.nan

    # =========================
    # Henssge standard / Cautelativa
    # =========================
    if st.session_state.get("stima_cautelativa_beta", False):
        if raffreddamento_calcolabile:
            # --- TA range ---
            Ta_range = None
            if "Ta_min_beta" in st.session_state and "Ta_max_beta" in st.session_state:
                a, b = float(st.session_state["Ta_min_beta"]), float(st.session_state["Ta_max_beta"])
                if a > b:
                    a, b = b, a
                Ta_range = (a, b)

            # --- FC range: priorità al manuale se presente, poi suggerito, poi ±0.10 ---
            CF_range = None
            min_k = st.session_state.get("FC_min_beta", None)
            max_k = st.session_state.get("FC_max_beta", None)

            if min_k is not None and max_k is not None:
                a, b = float(min_k), float(max_k)
                if a > b:
                    a, b = b, a
                CF_range = (max(a, 0.01), max(b, 0.01))
            else:
                vals = st.session_state.get("fc_suggested_vals", [])
                if len(vals) == 2:
                    a, b = sorted([float(vals[0]), float(vals[1])])
                    CF_range = (max(a, 0.01), max(b, 0.01))
                elif len(vals) == 1:
                    v = float(vals[0])
                    CF_range = (max(v - 0.10, 0.01), max(v + 0.10, 0.01))
                else:
                    CF_range = None  # il core userà ±0.10 su CF_value

            # --- calcolo cautelativo ---
            res = compute_raffreddamento_cautelativo(
                dt_ispezione=data_ora_ispezione,
                Ta_value=float(Ta_val),
                CF_value=float(CF_val),
                peso_kg=float(W_val),
                Ta_range=Ta_range,
                CF_range=CF_range,
                peso_stimato=bool(st.session_state.get("peso_stimato_beta", False)),
                mostra_tabella=True,
                solver_kwargs={
                    "Tr": float(Tr_val),
                    "T0": float(T0_val),
                    "round_minutes": int(st.session_state.get("henssge_round_minutes", 30)),
                },
            )

            # --- mappa output cautelativa ---
            t_min_raff_henssge = float(res.ore_min)
            t_max_raff_henssge = (
                np.nan if (not np.isfinite(res.ore_max) or res.ore_max >= INF_HOURS - 1e-9)
                else float(res.ore_max)
            )
            _tmed_raw = (
                t_min_raff_henssge if np.isnan(t_max_raff_henssge)
                else 0.5 * (t_min_raff_henssge + t_max_raff_henssge)
            )
            t_med_raff_henssge_rounded_raw = float(_tmed_raw)
            t_med_raff_henssge_rounded = round_quarter_hour(_tmed_raw)
            Qd_min = float(res.qd_min) if res.qd_min is not None else np.nan
            Qd_max = float(res.qd_max) if res.qd_max is not None else np.nan
            Qd_val_check = Qd_min

            qd_counts = {"optimal": 0, "intermediate": 0, "outside": 0}
            if res.df_combinazioni is not None:
                for row in res.df_combinazioni.itertuples(index=False):
                    status = _classify_qd_for_ta(row.Ta, row.Qd)
                    if status is not None:
                        qd_counts[status] += 1
            qd_range_status = _aggregate_qd_status(qd_counts)
            qd_status_counts = tuple(
                (status, qd_counts[status])
                for status in ("optimal", "intermediate", "outside")
            )
            raffreddamento_calcolabile = True

            # --- Range Ta/CF per riepilogo ---
            if "Ta_min_beta" in st.session_state and "Ta_max_beta" in st.session_state:
                ta_lo = float(st.session_state["Ta_min_beta"])
                ta_hi = float(st.session_state["Ta_max_beta"])
            else:
                ta_lo = float(Ta_val) - 1.0
                ta_hi = float(Ta_val) + 1.0
            ta_txt = f"{ta_lo:.1f} – {ta_hi:.1f} °C"

            if st.session_state.get("FC_min_beta") is not None and st.session_state.get("FC_max_beta") is not None:
                cf_lo = float(st.session_state["FC_min_beta"])
                cf_hi = float(st.session_state["FC_max_beta"])
            else:
                vals = st.session_state.get("fc_suggested_vals", [])
                if len(vals) == 2:
                    cf_lo, cf_hi = sorted([float(vals[0]), float(vals[1])])
                elif len(vals) == 1:
                    v = float(vals[0])
                    cf_lo, cf_hi = v - 0.10, v + 0.10
                else:
                    v = float(CF_val)
                    cf_lo, cf_hi = v - 0.10, v + 0.10
            cf_lo = max(cf_lo, 0.01)
            cf_hi = max(cf_hi, 0.01)
            cf_txt = f"{cf_lo:.2f} – {cf_hi:.2f}"

            p_txt = (
                f"{max(W_val - 3, 1):.0f}–{(W_val + 3):.0f} kg"
                if st.session_state.get("peso_stimato_beta", False)
                else f"{W_val:.0f} kg"
            )

            # --- header / bullets / conclusione ---
            header_blk = getattr(res, "header_html", None) or getattr(res, "header", None)
            bullets_blk = getattr(res, "bullets_html", None) or getattr(res, "bullets", None)
            conclusione_blk = getattr(res, "conclusione_html", None) or getattr(res, "conclusione", None)

            if not (header_blk and bullets_blk and conclusione_blk):
                t_lo = round_quarter_hour(t_min_raff_henssge)
                if np.isnan(t_max_raff_henssge):
                    risultato_txt = i18n.prudent_graphing_result_at_least(
                        i18n.prudent_graphing_hours_text(t_lo)
                    )
                else:
                    t_hi = round_quarter_hour(t_max_raff_henssge)
                    risultato_txt = i18n.prudent_graphing_result_range(
                        i18n.prudent_graphing_hours_text(t_lo),
                        i18n.prudent_graphing_hours_text(t_hi),
                    )

                header_blk = i18n.prudent_header()
                bullets_blk = i18n.prudent_simple_bullets(
                    ta_text=ta_txt,
                    cf_text=cf_txt,
                    weight_text=p_txt,
                )
                conclusione_blk = i18n.prudent_conclusion(risultato_txt)

            if header_blk:
                elenco_html = i18n.prudent_graphing_detail_list(
                    header=header_blk,
                    ta_text=ta_txt,
                    cf_text=cf_txt,
                    weight_text=p_txt,
                )
            else:
                elenco_html = "<ul></ul>"
            detail_blocks.append(elenco_html)

            t_min_vis = t_min_raff_henssge
            t_max_vis = t_max_raff_henssge
            par_h_caut = paragrafo_raffreddamento_dettaglio(
                t_min_visual=t_min_vis,
                t_max_visual=t_max_vis,
                t_med_round=t_med_raff_henssge_rounded,
                qd_val=Qd_val_check,
                ta_val=Ta_val,
                qd_range_status=qd_range_status,
            )
            if par_h_caut:
                detail_blocks.append(par_h_caut)

        else:
            # Henssge escluso
            pass
    else:
        if raffreddamento_calcolabile:
            round_minutes = int(st.session_state.get("henssge_round_minutes", 30))
            (
                t_med_raff_henssge_rounded,
                t_min_raff_henssge,
                t_max_raff_henssge,
                t_med_raff_henssge_rounded_raw,
                Qd_val_check,
            ) = calcola_raffreddamento(
                Tr_val, Ta_val, T0_val, W_val, CF_val, round_minutes=round_minutes
            )
            Qd_min = Qd_val_check
            Qd_max = Qd_val_check
            raffreddamento_calcolabile = (
                not np.isnan(t_med_raff_henssge_rounded) and t_med_raff_henssge_rounded >= 0
            )
        else:
            pass

    return CoolingState(
        Tr_val=Tr_val,
        Ta_val=Ta_val,
        T0_val=T0_val,
        W_val=W_val,
        CF_val=CF_val,
        t_min_raff_henssge=t_min_raff_henssge,
        t_max_raff_henssge=t_max_raff_henssge,
        t_med_raff_henssge_rounded_raw=t_med_raff_henssge_rounded_raw,
        t_med_raff_henssge_rounded=t_med_raff_henssge_rounded,
        Qd_val_check=Qd_val_check,
        Qd_min=Qd_min,
        Qd_max=Qd_max,
        qd_range_status=qd_range_status,
        qd_status_counts=qd_status_counts,
        raffreddamento_calcolabile=raffreddamento_calcolabile,
        Ta_for_pot=Ta_for_pot,
        qd_threshold=qd_threshold,
        gate_fail=gate_fail,
        detail_blocks=tuple(detail_blocks),
    )


__all__ = ["CoolingState", "compute_cooling_state"]
