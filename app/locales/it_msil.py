# -*- coding: utf-8 -*-
"""Etichette italiane specifiche dell'interfaccia MSIL."""

from __future__ import annotations

from app.tanatology_states import (
    LIVOR_NOT_ASSESSED,
    LIVOR_ABSENT,
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


__all__ = [
    "MSIL_LIVOR_LABEL_IT_BY_ID",
    "MSIL_RIGOR_LABEL_IT_BY_ID",
]
