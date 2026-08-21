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

from app.locales import it
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


def language_label(language: Optional[str] = None) -> str:
    """Etichetta leggibile della lingua richiesta."""
    return _LANGUAGE_LABELS[normalize_language(language)]


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
    "livor_label",
    "rigor_label",
    "special_parameter_label",
    "special_option_label",
    "body_label",
    "water_label",
    "full_clothing_label",
    "msil_clothing_label",
    "surface_label",
    "livor_description",
    "rigor_description",
    "special_description",
    "special_graph_label",
]
