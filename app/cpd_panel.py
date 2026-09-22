# -*- coding: utf-8 -*-
"""Streamlit panel for optional CPD analysis of a standard Henssge estimate."""

from __future__ import annotations

import datetime as dt
import math

import numpy as np
import pandas as pd
import streamlit as st

from app.cpd import build_cpd, density_values
from app.henssge import calcola_raffreddamento, henssge_uncertainty_halfwidth


def _inspection_datetime(use_custom, date_value, time_value):
    if not use_custom or not date_value or not time_value:
        return None
    if isinstance(time_value, dt.time):
        time_obj = time_value
    else:
        try:
            time_obj = dt.datetime.strptime(str(time_value), "%H:%M").time()
        except ValueError:
            return None
    return dt.datetime.combine(date_value, time_obj)


def _read_datetime(prefix: str, label: str):
    st.markdown(f"<div style='font-size:0.86rem;font-weight:500;margin-bottom:0.15rem;'>{label}</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="small")
    with c1:
        d = st.date_input("Data", value=None, format="DD/MM/YYYY", key=f"{prefix}_date", label_visibility="collapsed")
    with c2:
        t = st.time_input("Ora", value=None, step=60, key=f"{prefix}_time", label_visibility="collapsed")
    if d is None or t is None:
        return None
    return dt.datetime.combine(d, t)


def _fmt_hours(value: float) -> str:
    if math.isinf(value):
        return "∞"
    return f"{value:.2f} h"


def _fmt_tsd_interval(low: float, high: float) -> str:
    return f"{_fmt_hours(low)} – {_fmt_hours(high)}"


def _fmt_dt(value: dt.datetime) -> str:
    return value.strftime("%d.%m.%Y %H:%M")


def _fmt_absolute_interval(reference: dt.datetime, low_tsd: float, high_tsd: float) -> str:
    if math.isinf(high_tsd):
        return f"prima di {_fmt_dt(reference - dt.timedelta(hours=low_tsd))}"
    older = reference - dt.timedelta(hours=high_tsd)
    newer = reference - dt.timedelta(hours=low_tsd)
    return f"{_fmt_dt(older)} – {_fmt_dt(newer)}"


def _render_density_chart(result, reference_datetime):
    sigma = result.sd_hours
    left = max(0.0, min(result.support_low_hours, result.mean_hours - 3.5 * sigma, result.cpd_low_hours - 0.5 * sigma))
    right = max(result.mean_hours + 3.5 * sigma, result.cpd_high_hours + 0.5 * sigma, left + sigma)
    if not math.isinf(result.support_high_hours) and result.support_high_hours <= result.mean_hours + 5.0 * sigma:
        right = max(right, result.support_high_hours)
    right = max(right, left + 0.5)

    x = np.linspace(left, right, 401)
    prior, conditional = density_values(result, x)

    if reference_datetime is not None:
        times = [reference_datetime - dt.timedelta(hours=float(v)) for v in x]
        df = pd.DataFrame({"Ora": times, "Henssge": prior, "CPD": conditional}).sort_values("Ora")
        st.line_chart(df, x="Ora", y=["Henssge", "CPD"], height=220)
    else:
        df = pd.DataFrame({"TSD (h)": x, "Henssge": prior, "CPD": conditional})
        st.line_chart(df, x="TSD (h)", y=["Henssge", "CPD"], height=220)

    st.caption("Confronto tra densità Henssge non condizionata e densità CPD. L’altezza della curva rappresenta densità di probabilità, non probabilità puntuale.")


def render_cpd_panel(
    *,
    input_rt,
    input_ta,
    input_tm,
    input_w,
    fattore_correzione,
    usa_orario_custom: bool,
    input_data_rilievo,
    input_ora_rilievo,
    prudent_mode: bool,
    round_minutes: int = 30,
):
    """Render CPD only when a single standard Henssge distribution exists."""
    if prudent_mode:
        return

    try:
        t_med, t_min, t_max, t_med_raw, qd = calcola_raffreddamento(
            input_rt, input_ta, input_tm, input_w, fattore_correzione,
            round_minutes=round_minutes,
        )
    except Exception:
        return

    if not all(np.isfinite(v) for v in (t_med_raw, qd)):
        return

    # CPD is not offered in the late-cooling area where the app no longer
    # relies on a standard Henssge Gaussian interval.
    threshold = 0.2 if float(input_ta) <= 23.0 else 0.5
    if float(qd) <= threshold:
        return

    halfwidth = henssge_uncertainty_halfwidth(t_med_raw, qd, fattore_correzione)
    if not np.isfinite(halfwidth) or halfwidth <= 0:
        return
    sigma = float(halfwidth) / 2.0

    reference = _inspection_datetime(
        usa_orario_custom, input_data_rilievo, input_ora_rilievo
    )

    with st.expander("Analisi condizionata (CPD)", expanded=False):
        st.caption(
            "Integra limiti temporali indipendenti con la distribuzione Henssge. "
            "Le condizioni sono trattate come limiti rigidi: inserirle solo quando possono essere sostenute come tali."
        )

        lower = 0.0
        upper = math.inf
        assumptions = ["Decesso già avvenuto al momento del rilievo termometrico (TSD ≥ 0)."]

        use_last_alive = False
        use_found_dead = False
        last_alive = None
        found_dead = None

        if reference is not None:
            st.caption(f"Riferimento del rilievo termometrico: {_fmt_dt(reference)}")
            c1, c2 = st.columns(2, gap="small")
            with c1:
                use_last_alive = st.checkbox("Ultima volta visto/a vivo/a", key="cpd_use_last_alive")
            with c2:
                use_found_dead = st.checkbox("Rinvenuto/a già morto/a", key="cpd_use_found_dead")

            if use_last_alive:
                last_alive = _read_datetime("cpd_last_alive", "Ultima volta visto/a vivo/a")
                if last_alive is None:
                    st.info("Completare data e ora dell’ultima volta visto/a vivo/a.")
                    return
                if last_alive > reference:
                    st.error("L’ultima volta visto/a vivo/a non può essere successiva al rilievo termometrico.")
                    return
                upper = min(upper, (reference - last_alive).total_seconds() / 3600.0)
                assumptions.append(f"Ultima volta visto/a vivo/a: {_fmt_dt(last_alive)}.")

            if use_found_dead:
                found_dead = _read_datetime("cpd_found_dead", "Rinvenuto/a già morto/a")
                if found_dead is None:
                    st.info("Completare data e ora del rinvenimento già morto/a.")
                    return
                if found_dead > reference:
                    st.error("Il rinvenimento già morto/a non può essere successivo al rilievo termometrico.")
                    return
                lower = max(lower, (reference - found_dead).total_seconds() / 3600.0)
                assumptions.append(f"Rinvenuto/a già morto/a: {_fmt_dt(found_dead)}.")

            if last_alive is not None and found_dead is not None and last_alive > found_dead:
                st.error("La persona non può risultare viva dopo il momento in cui è stata rinvenuta già morta.")
                return
        else:
            st.info("Per usare «ultima volta visto/a vivo/a» e «rinvenuto/a già morto/a», inserire data e ora del rilievo termometrico nella sezione principale. I limiti TSD possono comunque essere usati.")

        c1, c2 = st.columns(2, gap="small")
        with c1:
            use_min_tsd = st.checkbox("Limite minimo TSD", key="cpd_use_min_tsd")
            if use_min_tsd:
                min_tsd = st.number_input("TSD minimo (h)", min_value=0.0, value=0.0, step=0.25, format="%.2f", key="cpd_min_tsd")
                lower = max(lower, float(min_tsd))
                assumptions.append(f"Limite minimo TSD: {float(min_tsd):.2f} h.")
        with c2:
            use_max_tsd = st.checkbox("Limite massimo TSD", key="cpd_use_max_tsd")
            if use_max_tsd:
                max_tsd = st.number_input("TSD massimo (h)", min_value=0.0, value=24.0, step=0.25, format="%.2f", key="cpd_max_tsd")
                upper = min(upper, float(max_tsd))
                assumptions.append(f"Limite massimo TSD: {float(max_tsd):.2f} h.")

        if upper <= lower:
            st.error("Le condizioni inserite sono incompatibili: non rimane alcun intervallo temporale possibile.")
            return

        try:
            result = build_cpd(
                mean_hours=float(t_med_raw),
                sd_hours=sigma,
                lower_hours=lower,
                upper_hours=upper,
            )
        except ValueError as exc:
            st.error(str(exc))
            return

        st.markdown("**Condizioni considerate**")
        st.markdown("\n".join(f"- {item}" for item in assumptions))

        if reference is not None:
            st.markdown(f"**Henssge ±2 SD:** {_fmt_absolute_interval(reference, result.unconditional_low_hours, result.unconditional_high_hours)}")
            st.markdown(f"**Intervallo temporalmente possibile:** {_fmt_absolute_interval(reference, result.support_low_hours, result.support_high_hours)}")
            st.markdown(f"**CPD 95.45%:** {_fmt_absolute_interval(reference, result.cpd_low_hours, result.cpd_high_hours)}")
        else:
            st.markdown(f"**Henssge ±2 SD:** {_fmt_tsd_interval(result.unconditional_low_hours, result.unconditional_high_hours)}")
            st.markdown(f"**Intervallo temporalmente possibile:** {_fmt_tsd_interval(result.support_low_hours, result.support_high_hours)}")
            st.markdown(f"**CPD 95.45%:** {_fmt_tsd_interval(result.cpd_low_hours, result.cpd_high_hours)}")

        st.caption(
            f"Probabilità Henssge originariamente contenuta nell’intervallo ammesso: "
            f"{result.prior_mass_in_support * 100:.2f}%. Dopo il condizionamento questa massa viene rinormalizzata al 100%."
        )

        if not (result.support_low_hours <= result.mean_hours <= result.support_high_hours):
            st.warning(
                "La stima centrale Henssge cade fuori dall’intervallo imposto dalle condizioni. "
                "In questa situazione la CPD è particolarmente sensibile a eventuali errori della stima termometrica; il risultato richiede cautela interpretativa."
            )

        _render_density_chart(result, reference)


__all__ = ["render_cpd_panel"]
