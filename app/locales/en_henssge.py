"""English presentation resources for postmortem body cooling.

Applicability decisions remain in the scientific modules. Qd thresholds and
formatting branches reproduce the Italian resources; no limits are calculated here.
"""

from __future__ import annotations


def henssge_detail_paragraph(interval: str, extra: str = "") -> str:
    return (
        "<ul><li>Applying Henssge’s equation suggests that death occurred approximately "
        f"{interval} before the observations made during the medico-legal examination.{extra}</li></ul>"
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
        f"The mean estimate obtained from postmortem body cooling ({mean_hours} h) exceeds 30 hours. "
        "The reliability of Henssge’s method decreases significantly beyond this interval."
    )


_QD_EXPLANATION = (
    "Qd expresses the degree of body cooling in this case: it equals 1 at the initial body "
    "temperature and approaches 0 as the rectal temperature approaches the ambient temperature."
)


def qd_summary(*, qd_text: str, ambient_at_most_23: bool, threshold_text: str,
               within_limits: bool, status: str | None = None) -> str:
    condition = "ambient temperature ≤ 23 °C" if ambient_at_most_23 else "ambient temperature > 23 °C"
    threshold = "0.2" if ambient_at_most_23 else "0.5"
    resolved_status = status or ("optimal" if within_limits else "outside")
    if resolved_status == "intermediate":
        sentence = (
            "In this case, the parameters permit application of Henssge’s method, although Qd is close "
            "to the lower limit and therefore results in a wider estimated time interval"
        )
    elif resolved_status == "outside":
        sentence = (
            "In this case, Qd falls outside the range in which Henssge’s method provides a sufficiently reliable estimate"
        )
    else:
        sentence = "In this case, the parameters allow a sufficiently reliable estimate using Henssge’s method"
    return (
        f"<p style='color:blue;font-size:8pt;'> {sentence} "
        f"(with {condition}, Qd should be > {threshold}; in this case it is {qd_text}). {_QD_EXPLANATION}</p>"
    )


def qd_range_summary(*, qd_min_text: str, qd_max_text: str, status: str, single_value: bool) -> str:
    qd_value = f"is {qd_min_text}" if single_value else f"ranges from {qd_min_text} to {qd_max_text}"
    limits = (
        "with ambient temperature ≤ 23 °C, Qd should be > 0.2, whereas with ambient temperature > 23 °C "
        "it should be > 0.5"
    )
    if status == "all_optimal":
        sentence = "Under the conditions considered, the parameters allow a sufficiently reliable estimate using Henssge’s method"
    elif status == "mixed":
        sentence = (
            "For some of the conditions considered, Qd falls outside the range in which Henssge’s "
            "method provides a sufficiently reliable estimate"
        )
    elif status == "no_optimal_intermediate":
        sentence = (
            "Under the conditions considered, the parameters permit application of Henssge’s method, "
            "although Qd is close to the lower limit and therefore results in a wider estimated time interval"
        )
        limits = "with ambient temperature ≤ 23 °C, Qd should be > 0.2"
    else:
        sentence = (
            "Under the conditions considered, Qd falls outside the range in which Henssge’s method "
            "provides a sufficiently reliable estimate"
        )
    return (
        f"<p style='color:blue;font-size:8pt;'> {sentence} "
        f"({limits}; under the conditions considered, Qd {qd_value}). {_QD_EXPLANATION}</p>"
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
    return " and ".join(parts)


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
    return "The following parameters were considered in the assessment of postmortem body cooling."


def prudent_bullets(*, ta_text: str, cf_text: str, weight_text: str) -> str:
    return (
        "<ul><li>Range of mean ambient temperatures, allowing for possible temperature fluctuations "
        f"between death and the medico-legal examination: <b>{ta_text}</b>.</li>"
        "<li>Estimated range of corrective factors, considering the various conditions to which the "
        f"body may have been exposed: <b>{cf_text}</b>.</li>"
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
        f"Applying Henssge’s equation suggests that death occurred {result_text} before the "
        "observations made during the medico-legal examination."
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
                                ta_is_range: bool = True, cf_is_range: bool = True) -> str:
    from html import escape

    ta_label = "Range of mean ambient temperatures" if ta_is_range else "Mean ambient temperature"
    cf_label = (
        "Estimated range of corrective factors, considering the various conditions to which the body may have been exposed"
        if cf_is_range else "Corrective factor considered"
    )
    fc_item = (f"<li>{escape(scenario_description)}.</li>" if scenario_description else
               f"<li>{cf_label}: <b>{cf_text}</b>.</li>")
    return (
        f"<ul><li>{header}<ul style='list-style-type: circle; margin-left: 20px;'>"
        f"<li>{ta_label}, allowing for possible temperature fluctuations between death and the "
        f"medico-legal examination: <b>{ta_text}</b>.</li>{fc_item}"
        f"<li>Body weight: <b>{weight_text}</b>.</li></ul></li></ul>"
    )
