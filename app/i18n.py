# -*- coding: utf-8 -*-
"""Accesso centralizzato alle risorse localizzate dell'applicazione.

In questa fase è registrata esclusivamente la lingua italiana. Il modulo non
contiene testi e non dipende da Streamlit: seleziona una locale e offre helper
neutri rispetto alla lingua per testi ed etichette già separati dai dati e
dalla logica scientifica.
"""

from __future__ import annotations

from types import ModuleType
from typing import Dict, Mapping, Optional, Tuple

from app.locales import it, it_factor, it_henssge, it_ui
from app.factor_ui_states import (
    BODY_LABEL_IT,
    WATER_LABEL_IT,
    FULL_CLOTHING_LABEL_IT,
    MSIL_CLOTHING_LABEL_IT,
)
from app.surface_ui_states import SURFACE_LABEL_IT


DEFAULT_LANGUAGE = "it"

_LANGUAGE_LABELS: Dict[str, str] = {
    "it": "Italiano",
}

_LOCALES: Dict[str, ModuleType] = {
    "it": it,
}

_HENSSGE_LOCALES: Dict[str, ModuleType] = {
    "it": it_henssge,
}

_FACTOR_LOCALES: Dict[str, ModuleType] = {
    "it": it_factor,
}

_UI_LOCALES: Dict[str, ModuleType] = {
    "it": it_ui,
}

SUPPORTED_LANGUAGES: Tuple[str, ...] = tuple(_LOCALES.keys())


def normalize_language(language: Optional[str] = None) -> str:
    """Normalizza e valida il codice lingua.

    ``None`` o stringa vuota usano la lingua predefinita. Sono accettate
    differenze di maiuscole/minuscole; lingue non registrate sollevano
    ``ValueError`` invece di ricadere silenziosamente su un'altra lingua.
    """
    if language is None:
        return DEFAULT_LANGUAGE

    code = str(language).strip().lower()
    if not code:
        return DEFAULT_LANGUAGE
    if code not in _LOCALES:
        raise ValueError(f"Lingua non supportata: {language!r}")
    return code


def get_locale(language: Optional[str] = None) -> ModuleType:
    """Restituisce il modulo locale associato alla lingua richiesta."""
    return _LOCALES[normalize_language(language)]


def _get_henssge_locale(language: Optional[str] = None) -> ModuleType:
    """Restituisce il modulo locale dedicato ai testi Henssge/Qd."""
    return _HENSSGE_LOCALES[normalize_language(language)]


def _get_factor_locale(language: Optional[str] = None) -> ModuleType:
    """Restituisce il modulo locale dedicato alla descrizione del fattore di correzione."""
    return _FACTOR_LOCALES[normalize_language(language)]


def _get_ui_locale(language: Optional[str] = None) -> ModuleType:
    """Restituisce il modulo locale dedicato ai testi delle interfacce."""
    return _UI_LOCALES[normalize_language(language)]


def language_label(language: Optional[str] = None) -> str:
    """Etichetta leggibile della lingua richiesta."""
    return _LANGUAGE_LABELS[normalize_language(language)]


def ui_text(
    key: str,
    language: Optional[str] = None,
    **values,
) -> str:
    """Restituisce un testo localizzato dell'interfaccia."""
    return _get_ui_locale(language).ui_text(key, **values)


def _localized_mapping(
    locale: ModuleType,
    generic_name: str,
    italian_fallback: Mapping,
):
    """Recupera una mappa localizzata con fallback transitorio all'italiano."""
    mapping = getattr(locale, generic_name, None)
    if mapping is not None:
        return mapping
    if locale is it:
        return italian_fallback
    raise AttributeError(f"La locale {locale.__name__!r} non espone {generic_name!r}")


def livor_label(state_id: str, language: Optional[str] = None) -> str:
    """Etichetta localizzata dello stato delle ipostasi."""
    locale = get_locale(language)
    return _localized_mapping(locale, "LIVOR_LABEL_BY_ID", it.LIVOR_LABEL_IT)[state_id]


def rigor_label(state_id: str, language: Optional[str] = None) -> str:
    """Etichetta localizzata dello stato della rigidità cadaverica."""
    locale = get_locale(language)
    return _localized_mapping(locale, "RIGOR_LABEL_BY_ID", it.RIGOR_LABEL_IT)[state_id]


def special_parameter_label(param_id: str, language: Optional[str] = None) -> str:
    """Etichetta localizzata di un parametro tanatologico speciale."""
    locale = get_locale(language)
    return _localized_mapping(
        locale,
        "SPECIAL_PARAM_LABEL_BY_ID",
        it.SPECIAL_PARAM_LABEL_IT,
    )[param_id]


def special_option_label(
    param_id: str,
    option_id: str,
    language: Optional[str] = None,
) -> str:
    """Etichetta localizzata di un'opzione tanatologica speciale."""
    locale = get_locale(language)
    return _localized_mapping(
        locale,
        "SPECIAL_OPTION_LABEL_BY_ID",
        it.SPECIAL_OPTION_LABEL_IT,
    )[param_id][option_id]


def body_label(state_id: str, language: Optional[str] = None) -> str:
    """Etichetta localizzata dello stato del corpo nel pannello FC."""
    locale = get_locale(language)
    return _localized_mapping(locale, "BODY_LABEL_BY_ID", BODY_LABEL_IT)[state_id]


def water_label(state_id: str, language: Optional[str] = None) -> str:
    """Etichetta localizzata del tipo di acqua nel pannello FC."""
    locale = get_locale(language)
    return _localized_mapping(locale, "WATER_LABEL_BY_ID", WATER_LABEL_IT)[state_id]


def full_clothing_label(state_id: str, language: Optional[str] = None) -> str:
    """Etichetta localizzata di indumenti/coperture nella UI completa."""
    locale = get_locale(language)
    return _localized_mapping(
        locale,
        "FULL_CLOTHING_LABEL_BY_ID",
        FULL_CLOTHING_LABEL_IT,
    )[state_id]


def msil_clothing_label(state_id: str, language: Optional[str] = None) -> str:
    """Etichetta localizzata di indumenti/coperture nella UI MSIL."""
    locale = get_locale(language)
    return _localized_mapping(
        locale,
        "MSIL_CLOTHING_LABEL_BY_ID",
        MSIL_CLOTHING_LABEL_IT,
    )[state_id]


def surface_label(surface_id: str, language: Optional[str] = None) -> str:
    """Etichetta localizzata della superficie di appoggio."""
    locale = get_locale(language)
    return _localized_mapping(locale, "SURFACE_LABEL_BY_ID", SURFACE_LABEL_IT)[surface_id]


def format_hours_minutes(h: int, m: int, language: Optional[str] = None) -> str:
    """Formattazione localizzata di ore e minuti."""
    return get_locale(language).format_hours_minutes(h, m)


def format_hours_range(
    h1: int,
    m1: int,
    h2: int,
    m2: int,
    language: Optional[str] = None,
) -> str:
    """Formattazione localizzata di un intervallo espresso in ore e minuti."""
    return get_locale(language).format_hours_range(h1, m1, h2, m2)


def simple_sentence_no_dt_not_over(duration: str, language: Optional[str] = None) -> str:
    """Frase breve localizzata per un limite massimo senza data/ora."""
    return get_locale(language).simple_sentence_no_dt_not_over(duration)


def simple_sentence_no_dt_over(duration: str, language: Optional[str] = None) -> str:
    """Frase breve localizzata per un limite minimo senza data/ora."""
    return get_locale(language).simple_sentence_no_dt_over(duration)


def simple_sentence_no_dt_range(interval: str, language: Optional[str] = None) -> str:
    """Frase breve localizzata per un intervallo senza data/ora."""
    return get_locale(language).simple_sentence_no_dt_range(interval)


def final_sentence_simple_over(duration: str, language: Optional[str] = None) -> str:
    """Frase conclusiva localizzata per un limite minimo senza data/ora."""
    return get_locale(language).final_sentence_simple_over(duration)


def final_sentence_simple_not_over(duration: str, language: Optional[str] = None) -> str:
    """Frase conclusiva localizzata per un limite massimo senza data/ora."""
    return get_locale(language).final_sentence_simple_not_over(duration)


def final_sentence_simple_range(interval: str, language: Optional[str] = None) -> str:
    """Frase conclusiva localizzata per un intervallo senza data/ora."""
    return get_locale(language).final_sentence_simple_range(interval)


def simple_sentence_dt_not_over(
    duration: str,
    lower_time: str,
    lower_date: str,
    inspection_time: str,
    inspection_date: str,
    language: Optional[str] = None,
) -> str:
    """Frase breve localizzata per un limite massimo con data/ora."""
    return get_locale(language).simple_sentence_dt_not_over(
        duration,
        lower_time,
        lower_date,
        inspection_time,
        inspection_date,
    )


def simple_sentence_dt_over(
    duration: str,
    cutoff_time: str,
    cutoff_date: str,
    language: Optional[str] = None,
) -> str:
    """Frase breve localizzata per un limite minimo con data/ora."""
    return get_locale(language).simple_sentence_dt_over(duration, cutoff_time, cutoff_date)


def simple_sentence_dt_range(
    interval: str,
    start_time: str,
    start_date: str,
    end_time: str,
    end_date: str,
    same_date: bool,
    language: Optional[str] = None,
) -> str:
    """Frase breve localizzata per un intervallo con data/ora."""
    return get_locale(language).simple_sentence_dt_range(
        interval,
        start_time,
        start_date,
        end_time,
        end_date,
        same_date,
    )


def final_sentence_dt_over(
    duration: str,
    cutoff_time: str,
    cutoff_date: str,
    language: Optional[str] = None,
) -> str:
    """Frase conclusiva localizzata per un limite minimo con data/ora."""
    return get_locale(language).final_sentence_dt_over(duration, cutoff_time, cutoff_date)


def final_sentence_dt_not_over(
    duration: str,
    lower_time: str,
    lower_date: str,
    inspection_time: str,
    inspection_date: str,
    language: Optional[str] = None,
) -> str:
    """Frase conclusiva localizzata per un limite massimo con data/ora."""
    return get_locale(language).final_sentence_dt_not_over(
        duration,
        lower_time,
        lower_date,
        inspection_time,
        inspection_date,
    )


def final_sentence_dt_range(
    interval: str,
    start_time: str,
    start_date: str,
    end_time: str,
    end_date: str,
    same_date: bool,
    language: Optional[str] = None,
) -> str:
    """Frase conclusiva localizzata per un intervallo con data/ora."""
    return get_locale(language).final_sentence_dt_range(
        interval,
        start_time,
        start_date,
        end_time,
        end_date,
        same_date,
    )


def putrefactive_paragraph(language: Optional[str] = None) -> str:
    """Paragrafo localizzato sui processi trasformativi post-mortali."""
    return get_locale(language).putrefactive_paragraph()


def parameter_summary(labels: list[str], language: Optional[str] = None) -> str:
    """Riepilogo localizzato dei parametri utilizzati nella stima."""
    return get_locale(language).parameter_summary(labels)


def potente_paragraph(
    duration: str,
    days: str,
    language: Optional[str] = None,
) -> str:
    """Paragrafo localizzato relativo alla stima secondo Potente et al."""
    return get_locale(language).potente_paragraph(duration, days)


def cooling_input_paragraph(
    *,
    inspection_time: Optional[str],
    inspection_date: Optional[str],
    ta_text: str,
    tr_text: str,
    weight_text: str,
    t0_text: str,
    correction_description: str,
    language: Optional[str] = None,
) -> str:
    """Riepilogo localizzato degli input utilizzati per il raffreddamento."""
    return get_locale(language).cooling_input_paragraph(
        inspection_time=inspection_time,
        inspection_date=inspection_date,
        ta_text=ta_text,
        tr_text=tr_text,
        weight_text=weight_text,
        t0_text=t0_text,
        correction_description=correction_description,
    )


def henssge_detail_paragraph(
    interval: str,
    extra: str = "",
    language: Optional[str] = None,
) -> str:
    """Paragrafo localizzato con la stima dettagliata secondo Henssge."""
    return _get_henssge_locale(language).henssge_detail_paragraph(interval, extra)


def henssge_qd_outside_warning(language: Optional[str] = None) -> str:
    """Avviso localizzato per Qd nella fascia più critica."""
    return _get_henssge_locale(language).henssge_qd_outside_warning()


def henssge_qd_partial_warning(language: Optional[str] = None) -> str:
    """Avviso localizzato per Qd nella fascia intermedia."""
    return _get_henssge_locale(language).henssge_qd_partial_warning()


def henssge_over_thirty_warning(
    mean_hours: str,
    language: Optional[str] = None,
) -> str:
    """Avviso localizzato per una stima media superiore a 30 ore."""
    return _get_henssge_locale(language).henssge_over_thirty_warning(mean_hours)


def qd_summary(
    *,
    qd_text: str,
    ambient_at_most_23: bool,
    threshold_text: str,
    within_limits: bool,
    language: Optional[str] = None,
) -> str:
    """Riepilogo localizzato del valore Qd e del relativo confronto."""
    return _get_henssge_locale(language).qd_summary(
        qd_text=qd_text,
        ambient_at_most_23=ambient_at_most_23,
        threshold_text=threshold_text,
        within_limits=within_limits,
    )


def prudent_range_text(a: float, b: float, unit: str, language: Optional[str] = None) -> str:
    return _get_henssge_locale(language).prudent_range_text(a, b, unit)


def prudent_hours_text(hours: float, language: Optional[str] = None) -> str:
    return _get_henssge_locale(language).prudent_hours_text(hours)


def prudent_parenthetical(
    *, ta_text: str, cf_text: str, weight_text: str, estimated_weight: bool,
    language: Optional[str] = None,
) -> str:
    return _get_henssge_locale(language).prudent_parenthetical(
        ta_text=ta_text, cf_text=cf_text, weight_text=weight_text,
        estimated_weight=estimated_weight,
    )


def prudent_estimated_weight(weight_text: str, language: Optional[str] = None) -> str:
    return _get_henssge_locale(language).prudent_estimated_weight(weight_text)


def prudent_result_text(
    *, minimum_text: str, maximum_text: Optional[str], beyond: bool, not_over: bool,
    language: Optional[str] = None,
) -> str:
    return _get_henssge_locale(language).prudent_result_text(
        minimum_text=minimum_text, maximum_text=maximum_text,
        beyond=beyond, not_over=not_over,
    )


def prudent_header(language: Optional[str] = None) -> str:
    return _get_henssge_locale(language).prudent_header()


def prudent_bullets(
    *, ta_text: str, cf_text: str, weight_text: str,
    language: Optional[str] = None,
) -> str:
    return _get_henssge_locale(language).prudent_bullets(
        ta_text=ta_text, cf_text=cf_text, weight_text=weight_text,
    )


def prudent_simple_bullets(
    *, ta_text: str, cf_text: str, weight_text: str,
    language: Optional[str] = None,
) -> str:
    return _get_henssge_locale(language).prudent_simple_bullets(
        ta_text=ta_text, cf_text=cf_text, weight_text=weight_text,
    )


def prudent_conclusion(result_text: str, language: Optional[str] = None) -> str:
    return _get_henssge_locale(language).prudent_conclusion(result_text)


def prudent_summary_html(
    *, ta_text: str, cf_text: str, weight_text: str, result_text: str,
    language: Optional[str] = None,
) -> str:
    return _get_henssge_locale(language).prudent_summary_html(
        ta_text=ta_text, cf_text=cf_text, weight_text=weight_text,
        result_text=result_text,
    )


def prudent_graphing_result_at_least(duration: str, language: Optional[str] = None) -> str:
    return _get_henssge_locale(language).prudent_graphing_result_at_least(duration)


def prudent_graphing_result_range(start: str, end: str, language: Optional[str] = None) -> str:
    return _get_henssge_locale(language).prudent_graphing_result_range(start, end)


def prudent_graphing_detail_list(
    *, header: str, ta_text: str, cf_text: str, weight_text: str,
    language: Optional[str] = None,
) -> str:
    return _get_henssge_locale(language).prudent_graphing_detail_list(
        header=header, ta_text=ta_text, cf_text=cf_text, weight_text=weight_text,
    )


def factor_correction_description(
    *,
    cf_value: float,
    summary: Optional[dict],
    fallback_text: Optional[str] = None,
    manual_override: bool = False,
    language: Optional[str] = None,
) -> str:
    """Descrizione localizzata del fattore di correzione."""
    return _get_factor_locale(language).factor_correction_description(
        cf_value=cf_value,
        summary=summary,
        fallback_text=fallback_text,
        manual_override=manual_override,
    )


def livor_description(state_id: str, language: Optional[str] = None):
    """Descrizione localizzata dello stato delle ipostasi."""
    return get_locale(language).livor_description_it(state_id)


def rigor_description(state_id: str, language: Optional[str] = None):
    """Descrizione localizzata dello stato della rigidità cadaverica."""
    return get_locale(language).rigor_description_it(state_id)


def special_description(param_id: str, option_id: str, language: Optional[str] = None):
    """Descrizione localizzata di un parametro tanatologico speciale."""
    return get_locale(language).special_description_it(param_id, option_id)


def special_graph_label(param_id: str, language: Optional[str] = None):
    """Etichetta breve localizzata per il grafico."""
    return get_locale(language).special_graph_label_it(param_id)


__all__ = [
    "DEFAULT_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "normalize_language",
    "get_locale",
    "language_label",
    "ui_text",
    "livor_label",
    "rigor_label",
    "special_parameter_label",
    "special_option_label",
    "body_label",
    "water_label",
    "full_clothing_label",
    "msil_clothing_label",
    "surface_label",
    "format_hours_minutes",
    "format_hours_range",
    "simple_sentence_no_dt_not_over",
    "simple_sentence_no_dt_over",
    "simple_sentence_no_dt_range",
    "final_sentence_simple_over",
    "final_sentence_simple_not_over",
    "final_sentence_simple_range",
    "simple_sentence_dt_not_over",
    "simple_sentence_dt_over",
    "simple_sentence_dt_range",
    "final_sentence_dt_over",
    "final_sentence_dt_not_over",
    "final_sentence_dt_range",
    "putrefactive_paragraph",
    "parameter_summary",
    "potente_paragraph",
    "cooling_input_paragraph",
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
    "prudent_graphing_result_at_least",
    "prudent_graphing_result_range",
    "prudent_graphing_detail_list",
    "factor_correction_description",
    "livor_description",
    "rigor_description",
    "special_description",
    "special_graph_label",
]
