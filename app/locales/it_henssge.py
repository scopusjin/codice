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
        "prima dei rilievi effettuati al momento dell’ispezione legale."
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


__all__ = [
    "henssge_detail_paragraph",
    "henssge_qd_outside_warning",
    "henssge_qd_partial_warning",
    "henssge_over_thirty_warning",
    "qd_summary",
]
