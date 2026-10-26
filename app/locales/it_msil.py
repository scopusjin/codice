# -*- coding: utf-8 -*-
"""Etichette italiane specifiche dell'interfaccia MSIL."""

from __future__ import annotations

from app.tanatology_states import (
    LIVOR_NOT_ASSESSED,
    LIVOR_ABSENT,
    LIVOR_CONFLUING,
    LIVOR_CONFLUENT,
    LIVOR_CONFLUENT_FULLY_MIGRATABLE,
    LIVOR_FULLY_MIGRATABLE,
    LIVOR_PARTIALLY_MIGRATABLE,
    LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE,
    LIVOR_FIXED,
    RIGOR_NOT_ASSESSED,
    RIGOR_ABSENT,
    RIGOR_DEVELOPING,
    RIGOR_FULL,
    RIGOR_RESOLVING,
    RIGOR_RESOLVED,
)


MSIL_LIVOR_LABEL_IT_BY_ID = {
    LIVOR_NOT_ASSESSED: "🩸 IPOSTASI?",
    LIVOR_ABSENT: "Ipostasi assenti",
    LIVOR_CONFLUING: "Ipostasi presenti, non confluite",
    LIVOR_CONFLUENT: "Ipostasi confluite",
    LIVOR_FULLY_MIGRATABLE: "Ipostasi completamente migrabili (confluenza non specificata)",
    LIVOR_CONFLUENT_FULLY_MIGRATABLE: "Ipostasi confluite e completamente migrabili",
    LIVOR_PARTIALLY_MIGRATABLE: "Ipostasi parzialmente migrabili",
    LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: "Ipostasi almeno in parte migrabili",
    LIVOR_FIXED: "Ipostasi non migrabili",
}

MSIL_RIGOR_LABEL_IT_BY_ID = {
    RIGOR_NOT_ASSESSED: "💪🏻 RIGOR MORTIS?",
    RIGOR_ABSENT: "Rigor assente",
    RIGOR_DEVELOPING: "Rigor presente e in aumento",
    RIGOR_FULL: "Rigor ubiquitario e di intensità massima",
    RIGOR_RESOLVING: "Rigor in risoluzione",
    RIGOR_RESOLVED: "Rigor risolto",
}

# Alias neutrali rispetto alla lingua usati dal livello i18n.
MSIL_LIVOR_LABEL_BY_ID = MSIL_LIVOR_LABEL_IT_BY_ID
MSIL_RIGOR_LABEL_BY_ID = MSIL_RIGOR_LABEL_IT_BY_ID


__all__ = [
    "MSIL_LIVOR_LABEL_IT_BY_ID",
    "MSIL_RIGOR_LABEL_IT_BY_ID",
    "MSIL_LIVOR_LABEL_BY_ID",
    "MSIL_RIGOR_LABEL_BY_ID",
]
