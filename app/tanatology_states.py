# -*- coding: utf-8 -*-
"""Identificatori interni stabili per ipostasi e rigidità cadaverica.

Questo modulo separa il significato logico degli stati dalle etichette italiane
mostrate nell'interfaccia. Nella prima fase di refactoring mantiene una mappatura
bidirezionale con le stringhe legacy usate da ``app.parameters`` e ``app.textgen``.

Le UI possono quindi iniziare a lavorare con ID stabili senza modificare, per ora,
i dati scientifici o i testi prodotti dall'applicazione.
"""

from __future__ import annotations

from typing import Dict


# -----------------------------------------------------------------------------
# Ipostasi
# -----------------------------------------------------------------------------
LIVOR_NOT_ASSESSED = "livor_not_assessed"
LIVOR_ABSENT = "livor_absent"
LIVOR_CONFLUING = "livor_confluing"
LIVOR_FULLY_MIGRATABLE = "livor_fully_migratable"
LIVOR_PARTIALLY_MIGRATABLE = "livor_partially_migratable"
LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE = "livor_at_least_partially_migratable"
LIVOR_FIXED = "livor_fixed"
LIVOR_UNRELIABLE = "livor_unreliable"

LIVOR_LABEL_IT: Dict[str, str] = {
    LIVOR_NOT_ASSESSED: "Non valutate",
    LIVOR_ABSENT: "Non ancora comparse",
    LIVOR_CONFLUING: "In via di confluenza",
    LIVOR_FULLY_MIGRATABLE: "Completamente migrabili",
    LIVOR_PARTIALLY_MIGRATABLE: "Parzialmente migrabili",
    LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: "Migrabili perlomeno parzialmente",
    LIVOR_FIXED: "Fisse",
    LIVOR_UNRELIABLE: "Non valutabili/Non attendibili",
}

LIVOR_ID_BY_LEGACY_LABEL: Dict[str, str] = {
    label: state_id for state_id, label in LIVOR_LABEL_IT.items()
}


# -----------------------------------------------------------------------------
# Rigidità cadaverica
# -----------------------------------------------------------------------------
RIGOR_NOT_ASSESSED = "rigor_not_assessed"
RIGOR_ABSENT = "rigor_absent"
RIGOR_DEVELOPING = "rigor_developing"
RIGOR_FULL = "rigor_full"
RIGOR_RESOLVING = "rigor_resolving"
RIGOR_RESOLVED = "rigor_resolved"
RIGOR_UNRELIABLE = "rigor_unreliable"

RIGOR_LABEL_IT: Dict[str, str] = {
    RIGOR_NOT_ASSESSED: "Non valutata",
    RIGOR_ABSENT: "Non ancora apprezzabile",
    RIGOR_DEVELOPING: "Presente e in via di intensificazione e generalizzazione",
    RIGOR_FULL: "Presente, intensa e generalizzata",
    RIGOR_RESOLVING: "In via di risoluzione",
    RIGOR_RESOLVED: "Risolta",
    RIGOR_UNRELIABLE: "Non valutabile/Non attendibile",
}

RIGOR_ID_BY_LEGACY_LABEL: Dict[str, str] = {
    label: state_id for state_id, label in RIGOR_LABEL_IT.items()
}


# -----------------------------------------------------------------------------
# Adattatori temporanei verso il codice esistente
# -----------------------------------------------------------------------------
def livor_legacy_label(state_id: str) -> str:
    """Restituisce l'etichetta italiana legacy attualmente attesa dal motore."""
    return LIVOR_LABEL_IT[state_id]


def rigor_legacy_label(state_id: str) -> str:
    """Restituisce l'etichetta italiana legacy attualmente attesa dal motore."""
    return RIGOR_LABEL_IT[state_id]


def livor_state_id(legacy_label: str) -> str:
    """Converte una vecchia etichetta italiana nel corrispondente ID stabile."""
    return LIVOR_ID_BY_LEGACY_LABEL[legacy_label]


def rigor_state_id(legacy_label: str) -> str:
    """Converte una vecchia etichetta italiana nel corrispondente ID stabile."""
    return RIGOR_ID_BY_LEGACY_LABEL[legacy_label]


__all__ = [
    "LIVOR_NOT_ASSESSED",
    "LIVOR_ABSENT",
    "LIVOR_CONFLUING",
    "LIVOR_FULLY_MIGRATABLE",
    "LIVOR_PARTIALLY_MIGRATABLE",
    "LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE",
    "LIVOR_FIXED",
    "LIVOR_UNRELIABLE",
    "LIVOR_LABEL_IT",
    "LIVOR_ID_BY_LEGACY_LABEL",
    "RIGOR_NOT_ASSESSED",
    "RIGOR_ABSENT",
    "RIGOR_DEVELOPING",
    "RIGOR_FULL",
    "RIGOR_RESOLVING",
    "RIGOR_RESOLVED",
    "RIGOR_UNRELIABLE",
    "RIGOR_LABEL_IT",
    "RIGOR_ID_BY_LEGACY_LABEL",
    "livor_legacy_label",
    "rigor_legacy_label",
    "livor_state_id",
    "rigor_state_id",
]
