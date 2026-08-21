# -*- coding: utf-8 -*-
"""Testi italiani relativi al raffreddamento cadaverico e al metodo di Henssge.

Il modulo contiene soltanto rendering testuale/presentazionale. Soglie, criteri
di applicabilità e decisioni scientifiche restano nei moduli di logica.
"""

from __future__ import annotations


def henssge_detail_paragraph(interval: str, extra: str = "") -> str:
    return (
        "<ul><li>Applicando l'equazione di Henssge, è stimabile che il decesso sia avvenuto, all'incirca, "
        f"{interval} "
        "prima dei rilievi effettuati nel corso dell’ispezione legale."
        f"{extra}</li></ul>"
    )


def henssge_qd_outside_warning() -> str:
    return (
        " <b>I valori ottenuti sono al di fuori dell'intervallo ottimale di applicazione dell'equazione.</b> "
        "La stima ottenuta non ha una solida base statistica e deve quindi essere considerata con cautela. "
        "Per la stima dell'epoca del decesso è opportuno basarsi soprattutto sugli altri dati tanatologici disponibili."
    )


def henssge_qd_partial_warning() -> str:
    return (
        " <b>Alcuni dei valori rilevati sono al di fuori dell'intervallo ottimale di applicazione dell'equazione.</b> "
        "La stima ottenuta non ha una solida base statistica e deve quindi essere considerata con cautela. "
        "Per la stima dell'epoca del decesso è opportuno basarsi soprattutto sugli altri dati tanatologici disponibili."
    )


def henssge_over_thirty_warning(mean_hours: str) -> str:
    return (
        "La stima media ottenuta dal raffreddamento cadaverico "
        f"({mean_hours} h) è superiore alle 30 ore. "
        "L'affidabilità del metodo di Henssge diminuisce significativamente oltre questo intervallo."
    )


def qd_summary(
    *,
    qd_text: str,
    ambient_at_most_23: bool,
    threshold_text: str,
    within_limits: bool,
) -> str:
    condition = "T. amb ≤ 23 °C" if ambient_at_most_23 else "T. amb > 23 °C"
    status = (
        "rientra nei limiti ottimali"
        if within_limits
        else "è inferiore ai limiti ottimali"
    )
    return (
        "<p style='color:blue;font-size:small;'> Nel caso in esame, l'equazione di Henssge per il raffreddamento cadaverico "
        f"ha Qd = {qd_text}. Tale parametro {status} per applicare l'equazione "
        f"(per {condition}, Qd deve essere superiore a {threshold_text}).</p>"
    )


def prudent_range_text(a: float, b: float, unit: str) -> str:
    """Formatta un range prudenziale mantenendo la resa storica."""
    if abs(a - b) < 1e-9:
        return f"{a:g} {unit}"
    return f"{a:g}–{b:g} {unit}"


def prudent_hours_text(hours: float) -> str:
    """Formatta ore decimali come nel riepilogo prudenziale storico."""
    import math

    if hours is None or not math.isfinite(hours):
        return "—"
    h = int(hours)
    m = int(round((hours - h) * 60))
    parts = []
    if h > 0:
        parts.append(f"{h} {'ora' if h == 1 else 'ore'}")
    if m > 0:
        parts.append(f"{m} {'minuto' if m == 1 else 'minuti'}")
    if not parts:
        return "0 ore"
    return " e ".join(parts)


def prudent_parenthetical(*, ta_text: str, cf_text: str, weight_text: str, estimated_weight: bool) -> str:
    suffix = ", peso stimato" if estimated_weight else ""
    return f"(raffreddamento stimato su Ta {ta_text}, CF {cf_text}, peso {weight_text}{suffix})"


def prudent_estimated_weight(weight_text: str) -> str:
    return f"{weight_text} (stimato)"


def prudent_result_text(*, minimum_text: str, maximum_text: str | None, beyond: bool, not_over: bool) -> str:
    if beyond:
        return f"oltre {minimum_text}"
    if not_over:
        return f"non oltre {maximum_text}"
    return f"tra circa {minimum_text} e {maximum_text}"


def prudent_header() -> str:
    return (
        "Per quanto attiene la valutazione del raffreddamento cadaverico, "
        "sono stati stimati i parametri di seguito indicati."
    )


def prudent_bullets(*, ta_text: str, cf_text: str, weight_text: str) -> str:
    return (
        "<ul>"
        f"<li>Range di temperature ambientali medie (tenendo conto delle possibili escursioni termiche verificatesi tra decesso e ispezione legale): <b>{ta_text}</b>.</li>"
        f"<li>Range per il fattore di correzione (considerate le possibili condizioni in cui può essersi trovato il corpo): <b>{cf_text}</b>.</li>"
        f"<li>Peso corporeo: <b>{weight_text}</b>.</li>"
        "</ul>"
    )


def prudent_simple_bullets(*, ta_text: str, cf_text: str, weight_text: str) -> str:
    return (
        "<ul>"
        f"<li>Range di temperature ambientali medie: <b>{ta_text}</b></li>"
        f"<li>Range per il fattore di correzione: <b>{cf_text}</b></li>"
        f"<li>Peso corporeo: <b>{weight_text}</b></li>"
        "</ul>"
    )


def prudent_conclusion(result_text: str) -> str:
    return (
        "Applicando l'equazione di Henssge, è possibile stimare che il decesso "
        f"sia avvenuto {result_text} prima dei rilievi effettuati nel corso "
        "dell’ispezione legale."
    )


def prudent_summary_html(*, ta_text: str, cf_text: str, weight_text: str, result_text: str) -> str:
    return "<br>".join([
        prudent_header(),
        prudent_bullets(ta_text=ta_text, cf_text=cf_text, weight_text=weight_text),
        prudent_conclusion(result_text),
    ])


def prudent_graphing_hours_text(hours: float) -> str:
    """Formatta ore decimali come il fallback storico di graphing.py."""
    import math

    if not math.isfinite(hours):
        return ""
    h = int(hours)
    m = int(round((hours - h) * 60))
    if m == 60:
        h += 1
        m = 0
    if m == 0:
        return f"{h} {'ora' if h == 1 else 'ore'}"
    return f"{h} {'ora' if h == 1 else 'ore'} {m} minuti"


def prudent_graphing_result_at_least(duration: str) -> str:
    return f"almeno {duration}"


def prudent_graphing_result_range(start: str, end: str) -> str:
    return f"tra {start} e {end}"


def prudent_graphing_detail_list(*, header: str, ta_text: str, cf_text: str, weight_text: str) -> str:
    return (
        "<ul>"
        f"<li>{header}"
        "<ul style='list-style-type: circle; margin-left: 20px;'>"
        f"<li>Range di temperature ambientali medie (tenendo conto delle possibili escursioni termiche verificatesi tra decesso e ispezione legale): <b>{ta_text}</b>.</li>"
        f"<li>Range per il fattore di correzione (considerate le possibili condizioni in cui può essersi trovato il corpo): <b>{cf_text}</b>.</li>"
        f"<li>Peso corporeo: <b>{weight_text}</b>.</li>"
        "</ul></li>"
        "</ul>"
    )


__all__ = [
    "henssge_detail_paragraph",
    "henssge_qd_outside_warning",
    "henssge_qd_partial_warning",
    "henssge_over_thirty_warning",
    "qd_summary",
    "prudent_range_text",
    "prudent_hours_text",
    "prudent_parenthetical",
    "prudent_estimated_weight",
    "prudent_result_text",
    "prudent_header",
    "prudent_bullets",
    "prudent_simple_bullets",
    "prudent_conclusion",
    "prudent_summary_html",
    "prudent_graphing_hours_text",
    "prudent_graphing_result_at_least",
    "prudent_graphing_result_range",
    "prudent_graphing_detail_list",
]
