# -*- coding: utf-8 -*-

from app.full_tanatology import (
    FULL_LIVOR_STATE_BY_LABEL,
    FULL_RIGOR_STATE_BY_LABEL,
    full_livor_legacy_value,
    full_rigor_legacy_value,
)
from app.parameters import opzioni_macchie, opzioni_rigidita


def test_full_livor_ui_matches_current_parameter_options():
    assert list(FULL_LIVOR_STATE_BY_LABEL.keys()) == list(opzioni_macchie.keys())
    for ui_label in opzioni_macchie:
        assert full_livor_legacy_value(ui_label) == ui_label


def test_full_rigor_ui_matches_current_parameter_options():
    assert list(FULL_RIGOR_STATE_BY_LABEL.keys()) == list(opzioni_rigidita.keys())
    for ui_label in opzioni_rigidita:
        assert full_rigor_legacy_value(ui_label) == ui_label
