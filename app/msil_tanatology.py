# -*- coding: utf-8 -*-
"""Adattatori degli stati tanatologici usati dall'interfaccia MSIL.

Il modulo separa le etichette semplificate mostrate nella pagina MSIL dagli
identificatori interni stabili. Le funzioni ``*_legacy_value`` restituiscono
esattamente le stringhe italiane attualmente attese dal codice esistente.

Nessun range, testo medico-legale o criterio di calcolo è definito qui.
"""

from __future__ import annotations

from typing import Dict, Optional

from app import i18n
from app.locales import it_msil
from app.tanatology_states import livor_legacy_label, rigor_legacy_label


# Mappe italiane statiche mantenute come compatibilità legacy.
MSIL_LIVOR_STATE_BY_LABEL: Dict[str, str] = {
    label: state_id for state_id, label in it_msil.MSIL_LIVOR_LABEL_IT_BY_ID.items()
}

MSIL_RIGOR_STATE_BY_LABEL: Dict[str, str] = {
    label: state_id for state_id, label in it_msil.MSIL_RIGOR_LABEL_IT_BY_ID.items()
}


def _msil_livor_labels_by_id(language: Optional[str] = None):
    """Mappa localizzata delle etichette MSIL delle ipostasi."""
    code = i18n.normalize_language(language)
    if code == "it":
        return it_msil.MSIL_LIVOR_LABEL_BY_ID
    locale = i18n.get_locale(code)
    mapping = getattr(locale, "MSIL_LIVOR_LABEL_BY_ID", None)
    if mapping is None:
        raise AttributeError(
            f"La locale {locale.__name__!r} non espone 'MSIL_LIVOR_LABEL_BY_ID'"
        )
    return mapping


def _msil_rigor_labels_by_id(language: Optional[str] = None):
    """Mappa localizzata delle etichette MSIL della rigidità."""
    code = i18n.normalize_language(language)
    if code == "it":
        return it_msil.MSIL_RIGOR_LABEL_BY_ID
    locale = i18n.get_locale(code)
    mapping = getattr(locale, "MSIL_RIGOR_LABEL_BY_ID", None)
    if mapping is None:
        raise AttributeError(
            f"La locale {locale.__name__!r} non espone 'MSIL_RIGOR_LABEL_BY_ID'"
        )
    return mapping


def msil_livor_labels(language: Optional[str] = None):
    """Etichette MSIL delle ipostasi nell'identico ordine corrente."""
    return tuple(_msil_livor_labels_by_id(language).values())


def msil_rigor_labels(language: Optional[str] = None):
    """Etichette MSIL della rigidità nell'identico ordine corrente."""
    return tuple(_msil_rigor_labels_by_id(language).values())


def msil_livor_state_id(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce l'ID stabile associato a una voce della UI MSIL."""
    state_by_label = {
        label: state_id
        for state_id, label in _msil_livor_labels_by_id(language).items()
    }
    return state_by_label[ui_label]


def msil_rigor_state_id(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce l'ID stabile associato a una voce della UI MSIL."""
    state_by_label = {
        label: state_id
        for state_id, label in _msil_rigor_labels_by_id(language).items()
    }
    return state_by_label[ui_label]


def msil_livor_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce il valore legacy che App_MSIL passa oggi al motore."""
    return livor_legacy_label(msil_livor_state_id(ui_label, language))


def msil_rigor_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce il valore legacy che App_MSIL passa oggi al motore."""
    return rigor_legacy_label(msil_rigor_state_id(ui_label, language))


__all__ = [
    "MSIL_LIVOR_STATE_BY_LABEL",
    "MSIL_RIGOR_STATE_BY_LABEL",
    "msil_livor_labels",
    "msil_rigor_labels",
    "msil_livor_state_id",
    "msil_rigor_state_id",
    "msil_livor_legacy_value",
    "msil_rigor_legacy_value",
]
