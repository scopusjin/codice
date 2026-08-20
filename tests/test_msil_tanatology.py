# -*- coding: utf-8 -*-

from app.msil_tanatology import (
    MSIL_LIVOR_STATE_BY_LABEL,
    MSIL_RIGOR_STATE_BY_LABEL,
    msil_livor_legacy_value,
    msil_rigor_legacy_value,
)


def test_msil_livor_values_are_legacy_compatible():
    expected = {
        "🩸 IPOSTASI?": "Non valutate",
        "Ipostasi assenti": "Non ancora comparse",
        "Ipostasi almeno in parte migrabili": "Migrabili perlomeno parzialmente",
        "Ipostasi non migrabili": "Fisse",
    }
    assert set(MSIL_LIVOR_STATE_BY_LABEL) == set(expected)
    for ui_label, legacy_value in expected.items():
        assert msil_livor_legacy_value(ui_label) == legacy_value


def test_msil_rigor_values_are_legacy_compatible():
    expected = {
        "💪🏻 RIGOR MORTIS?": "Non valutata",
        "Rigor assente": "Non ancora apprezzabile",
        "Rigor presente e in aumento": "Presente e in via di intensificazione e generalizzazione",
        "Rigor ubiquitario e di intensità massima": "Presente, intensa e generalizzata",
        "Rigor in risoluzione": "In via di risoluzione",
        "Rigor risolto": "Risolta",
    }
    assert set(MSIL_RIGOR_STATE_BY_LABEL) == set(expected)
    for ui_label, legacy_value in expected.items():
        assert msil_rigor_legacy_value(ui_label) == legacy_value
