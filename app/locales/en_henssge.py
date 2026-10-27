"""English presentation resources for postmortem body cooling.

Applicability decisions remain in the scientific modules. Qd thresholds and
formatting branches reproduce the Italian resources; no limits are calculated here.
"""

from __future__ import annotations


def henssge_detail_paragraph(interval: str, extra: str = "") -> str:
    return (
        "<ul><li>Henssge’s method suggests that death occurred approximately "
        f"{interval} before temperature measurement.{extra}</li></ul>"
    )


def henssge_qd_outside_warning() -> str:
    return ""


def henssge_qd_partial_warning() -> str:
    return ""


def henssge_qd_range_mixed_warning() -> str:
    return ""


def henssge_qd_range_intermediate_warning() -> str:
    return ""


def henssge_over_thirty_warning(mean_hours: str) -> str:
    return (
        f"The mean cooling-based estimate ({mean_hours} h) exceeds 30 hours. "
        "The reliability of Henssge’s method decreases significantly beyond this interval."
    )


_QD_EXPLANATION = (
    "Qd expresses relative body cooling: it equals 1 at the initial body temperature "
    "and approaches 0 as rectal and ambient temperatures converge."
)


def qd_summary(*, qd_text: str, ambient_at_most_23: bool, threshold_text: str,
               within_limits: bool, status: str | None = None) -> str:
    condition = "ambient temperature ≤ 23 °C" if ambient_at_most_23 else "ambient temperature > 23 °C"
    threshold = "0.2" if ambient_at_most_23 else "0.5"
    resolved_status = status or ("optimal" if within_limits else "outside")
    if resolved_status == "intermediate":
        sentence = (
            "Henssge’s method remains applicable, but Qd is close to the lower limit, "
            "giving a wider estimated interval"
        )
    elif resolved_status == "outside":
        sentence = (
            "Qd is outside the range for a sufficiently reliable Henssge estimate"
        )
    else:
        sentence = "Qd is within the range for a sufficiently reliable Henssge estimate"
    return (
        f"<p style='color:blue;font-size:8pt;'> {sentence} "
        f"({condition}: Qd should be > {threshold}; Qd = {qd_text}). {_QD_EXPLANATION}</p>"
    )


def qd_range_summary(*, qd_min_text: str, qd_max_text: str, status: str, single_value: bool) -> str:
    qd_value = f"is {qd_min_text}" if single_value else f"ranges from {qd_min_text} to {qd_max_text}"
    limits = (
        "Qd should be > 0.2 at ambient temperature ≤ 23 °C, or > 0.5 at ambient temperature > 23 °C"
    )
    if status == "all_optimal":
        sentence = "All conditions fall within the range for a sufficiently reliable Henssge estimate"
    elif status == "mixed":
        sentence = (
            "Some conditions fall outside the range for a sufficiently reliable Henssge estimate"
        )
    elif status == "no_optimal_intermediate":
        sentence = (
            "Henssge’s method remains applicable, but Qd is close to the lower limit, "
            "giving a wider estimated interval"
        )
        limits = "Qd should be > 0.2 at ambient temperature ≤ 23 °C"
    else:
        sentence = (
            "All conditions fall outside the range for a sufficiently reliable Henssge estimate"
        )
    return (
        f"<p style='color:blue;font-size:8pt;'> {sentence} "
        f"({limits}; Qd {qd_value}). {_QD_EXPLANATION}</p>"
    )


def prudent_range_text(a: float, b: float, unit: str) -> str:
    if abs(a - b) < 1e-9:
        return f"{a:g} {unit}"
    return f"{a:g}–{b:g} {unit}"


def prudent_hours_text(hours: float) -> str:
    import math

    if hours is None or not math.isfinite(hours):
        return "—"
    h = int(hours)
    m = int(round((hours - h) * 60))
    parts = []
    if h > 0:
        parts.append(f"{h} {'hour' if h == 1 else 'hours'}")
    if m > 0:
        parts.append(f"{m} {'minute' if m == 1 else 'minutes'}")
    if not parts:
        return "0 hours"
    return " ".join(parts)


def prudent_parenthetical(*, ta_text: str, cf_text: str, weight_text: str, estimated_weight: bool) -> str:
    suffix = ", estimated weight" if estimated_weight else ""
    return f"(cooling estimated using Ta {ta_text}, CF {cf_text}, weight {weight_text}{suffix})"


def prudent_estimated_weight(weight_text: str) -> str:
    return f"{weight_text} (estimated)"


def prudent_result_text(*, minimum_text: str, maximum_text: str | None, beyond: bool, not_over: bool) -> str:
    if beyond:
        return f"more than {minimum_text}"
    if not_over:
        return f"no more than {maximum_text}"
    return f"between approximately {minimum_text} and {maximum_text}"


def prudent_header() -> str:
    return "Postmortem body cooling was assessed using:"


def prudent_bullets(*, ta_text: str, cf_text: str, weight_text: str) -> str:
    return (
        "<ul><li>Range of mean ambient temperatures between death and examination, allowing for "
        f"possible fluctuations: <b>{ta_text}</b>.</li>"
        "<li>Estimated range of corrective factors for the possible exposure conditions: "
        f"<b>{cf_text}</b>.</li>"
        f"<li>Body weight: <b>{weight_text}</b>.</li></ul>"
    )


def prudent_simple_bullets(*, ta_text: str, cf_text: str, weight_text: str) -> str:
    return (
        f"<ul><li>Range of mean ambient temperatures: <b>{ta_text}</b></li>"
        f"<li>Estimated range of corrective factors: <b>{cf_text}</b></li>"
        f"<li>Body weight: <b>{weight_text}</b></li></ul>"
    )


def prudent_conclusion(result_text: str) -> str:
    return (
        f"Henssge’s method suggests that death occurred {result_text} before temperature measurement."
    )


def prudent_summary_html(*, ta_text: str, cf_text: str, weight_text: str, result_text: str) -> str:
    return "<br>".join([
        prudent_header(),
        prudent_bullets(ta_text=ta_text, cf_text=cf_text, weight_text=weight_text),
        prudent_conclusion(result_text),
    ])


def prudent_graphing_hours_text(hours: float) -> str:
    import math

    if not math.isfinite(hours):
        return ""
    h = int(hours)
    m = int(round((hours - h) * 60))
    if m == 60:
        h += 1
        m = 0
    if m == 0:
        return f"{h} {'hour' if h == 1 else 'hours'}"
    return f"{h} {'hour' if h == 1 else 'hours'} {m} minutes"


def prudent_graphing_result_at_least(duration: str) -> str:
    return f"at least {duration}"


def prudent_graphing_result_range(start: str, end: str) -> str:
    return f"between {start} and {end}"


def prudent_graphing_detail_list(*, header: str, ta_text: str, cf_text: str, weight_text: str,
                                scenario_description: str | None = None,
                                ta_is_range: bool = True, cf_is_range: bool = True,
                                measured_values: tuple | None = None) -> str:
    from html import escape

    ta_label = "Range of mean ambient temperatures" if ta_is_range else "Mean ambient temperature"
    cf_label = (
        "Estimated range of corrective factors for the possible exposure conditions"
        if cf_is_range else "Corrective factor"
    )
    fc_item = (f"<li>{escape(scenario_description)}.</li>" if scenario_description else
               f"<li>{cf_label}: <b>{cf_text}</b>.</li>")
    measured_html = ""
    if measured_values is not None:
        ta, tr, t0 = measured_values
        measured_ta = f"{ta:.1f}" if ta is not None else "—"
        measured_html = (
            "<li>Temperatures measured during the medico-legal examination:<ul>"
            f"<li>Ambient temperature: {measured_ta} °C.</li>"
            f"<li>Rectal temperature: {tr:.1f} °C.</li></ul></li>"
            f"<li>Body weight measured in the autopsy room: <b>{weight_text}</b>.</li>"
            f"<li>Assumed body temperature at death: {t0:.1f} °C.</li>"
        )
    weight_html = "" if measured_values is not None else f"<li>Body weight: <b>{weight_text}</b>.</li>"
    return (
        f"<ul><li>{header}<ul style='list-style-type: circle; margin-left: 20px;'>"
        f"{measured_html}<li>{ta_label} between death and examination, allowing for possible fluctuations: "
        f"<b>{ta_text}</b>.</li>{fc_item}"
        f"{weight_html}</ul></li></ul>"
    )
