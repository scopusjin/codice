# -*- coding: utf-8 -*-
"""Adattatori localizzati per il pannello del fattore di correzione completo.

Il modulo separa le etichette mostrate dalla UI dai valori legacy ancora attesi
da ``app.factor_calc``. Non contiene formule, soglie o regole di calcolo.
"""

from __future__ import annotations

from typing import Dict, Optional

import streamlit as st

from app import i18n
from app.factor_ui_states import (
    BODY_LABEL_IT,
    BODY_LEGACY_VALUE,
    WATER_LABEL_IT,
    WATER_LEGACY_VALUE,
    FULL_CLOTHING_LABEL_IT,
)
from app.surface_ui_states import SURFACE_LABEL_IT


# Mappe italiane statiche mantenute come compatibilità legacy.
FULL_BODY_STATE_BY_LABEL: Dict[str, str] = {
    i18n.body_label(state_id): state_id for state_id in BODY_LABEL_IT
}

FULL_WATER_STATE_BY_LABEL: Dict[str, str] = {
    i18n.water_label(state_id): state_id for state_id in WATER_LABEL_IT
}

FULL_SURFACE_STATE_BY_LABEL: Dict[str, str] = {
    i18n.surface_label(surface_id): surface_id for surface_id in SURFACE_LABEL_IT
}


def _install_full_water_radio_position_css() -> None:
    """Posiziona la scelta del tipo d'acqua senza comprimere la riga principale."""
    st.html(
        """
        <style>
        @media (min-width: 769px) {
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_desktop"] {
            position: relative !important;
            overflow: visible !important;
          }

          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_desktop"]
          [data-testid="stElementContainer"]:has([class*="st-key-fcpanel_std_radio_acqua"]),
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_desktop"]
          [data-testid="stElementContainer"]:has([class*="st-key-fcpanel_caut_radio_acqua"]) {
            position: absolute !important;
            top: 0.30rem !important;
            right: 0.42rem !important;
            width: max-content !important;
            min-width: max-content !important;
            max-width: none !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
            z-index: 2 !important;
          }

          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_desktop"]
          [class*="st-key-fcpanel_std_radio_acqua"][data-testid="stRadio"],
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_desktop"]
          [class*="st-key-fcpanel_std_radio_acqua"] [data-testid="stRadio"],
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_desktop"]
          [class*="st-key-fcpanel_caut_radio_acqua"][data-testid="stRadio"],
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_desktop"]
          [class*="st-key-fcpanel_caut_radio_acqua"] [data-testid="stRadio"] {
            width: max-content !important;
            min-width: max-content !important;
            max-width: none !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
          }
        }

        @media (max-width: 768px) {
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_mobile"]
          [data-testid="stElementContainer"]:has([class*="st-key-fcpanel_std_radio_acqua"]),
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_mobile"]
          [data-testid="stElementContainer"]:has([class*="st-key-fcpanel_caut_radio_acqua"]) {
            width: max-content !important;
            min-width: max-content !important;
            max-width: 100% !important;
            align-self: flex-end !important;
            margin: 0.16rem 0 0 auto !important;
            padding: 0 !important;
            overflow: visible !important;
          }

          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_mobile"]
          [class*="st-key-fcpanel_std_radio_acqua"][data-testid="stRadio"],
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_mobile"]
          [class*="st-key-fcpanel_std_radio_acqua"] [data-testid="stRadio"],
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_mobile"]
          [class*="st-key-fcpanel_caut_radio_acqua"][data-testid="stRadio"],
          body:has([class*="st-key-stima_cautelativa_beta"])
          [class*="st-key-full_fc_panel_mobile"]
          [class*="st-key-fcpanel_caut_radio_acqua"] [data-testid="stRadio"] {
            width: max-content !important;
            min-width: max-content !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
          }
        }
        </style>
        """
    )


_install_full_water_radio_position_css()


def full_body_labels(language: Optional[str] = None):
    """Etichette localizzate degli stati del corpo nell'ordine corrente."""
    return tuple(i18n.body_label(state_id, language) for state_id in BODY_LABEL_IT)


def full_body_state_id(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce l'ID stabile dello stato del corpo mostrato nella UI."""
    state_by_label = {
        i18n.body_label(state_id, language): state_id
        for state_id in BODY_LABEL_IT
    }
    return state_by_label[ui_label]


def full_body_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce il valore legacy dello stato del corpo atteso dal motore."""
    return BODY_LEGACY_VALUE[full_body_state_id(ui_label, language)]


def full_water_labels(language: Optional[str] = None):
    """Etichette localizzate dei tipi di acqua nell'ordine corrente."""
    return tuple(i18n.water_label(state_id, language) for state_id in WATER_LABEL_IT)


def full_water_state_id(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce l'ID stabile del tipo di acqua mostrato nella UI."""
    state_by_label = {
        i18n.water_label(state_id, language): state_id
        for state_id in WATER_LABEL_IT
    }
    return state_by_label[ui_label]


def full_water_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce il valore legacy del tipo di acqua atteso dal motore."""
    return WATER_LEGACY_VALUE[full_water_state_id(ui_label, language)]


def full_clothing_label(category_id: str, language: Optional[str] = None) -> str:
    """Etichetta localizzata di una categoria di indumenti/coperture."""
    if category_id not in FULL_CLOTHING_LABEL_IT:
        raise KeyError(category_id)
    return i18n.full_clothing_label(category_id, language)


def full_surface_labels(language: Optional[str] = None):
    """Etichette localizzate delle superfici nell'ordine corrente."""
    return tuple(i18n.surface_label(surface_id, language) for surface_id in SURFACE_LABEL_IT)


def full_surface_label(surface_id: str, language: Optional[str] = None) -> str:
    """Restituisce l'etichetta localizzata di una specifica superficie."""
    if surface_id not in SURFACE_LABEL_IT:
        raise KeyError(surface_id)
    return i18n.surface_label(surface_id, language)


def full_surface_state_id(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce l'ID stabile della superficie mostrata nella UI."""
    state_by_label = {
        i18n.surface_label(surface_id, language): surface_id
        for surface_id in SURFACE_LABEL_IT
    }
    return state_by_label[ui_label]


def full_surface_legacy_value(ui_label: str, language: Optional[str] = None) -> str:
    """Restituisce la stringa legacy della superficie attesa dal motore."""
    return SURFACE_LABEL_IT[full_surface_state_id(ui_label, language)]


__all__ = [
    "FULL_BODY_STATE_BY_LABEL",
    "FULL_WATER_STATE_BY_LABEL",
    "FULL_SURFACE_STATE_BY_LABEL",
    "full_body_labels",
    "full_body_state_id",
    "full_body_legacy_value",
    "full_water_labels",
    "full_water_state_id",
    "full_water_legacy_value",
    "full_clothing_label",
    "full_surface_labels",
    "full_surface_label",
    "full_surface_state_id",
    "full_surface_legacy_value",
]
