# -*- coding: utf-8 -*-

from app.factor_ui_states import (
    BLANKET_HEAVY,
    BODY_IMMERSED,
    BODY_WET,
    BODY_DRY,
    BODY_LABEL_IT,
    FULL_CLOTHING_LABEL_IT,
    MSIL_CLOTHING_LABEL_IT,
    WATER_FLOWING,
    WATER_LABEL_IT,
    WATER_STILL,
    body_legacy_value,
    water_legacy_value,
)


def test_body_labels_and_legacy_values_are_unchanged():
    assert BODY_LABEL_IT == {
        BODY_DRY: "Corpo asciutto",
        BODY_WET: "Bagnato",
        BODY_IMMERSED: "Immerso",
    }
    assert body_legacy_value("Corpo asciutto") == "Asciutto"
    assert body_legacy_value("Bagnato") == "Bagnato"
    assert body_legacy_value("Immerso") == "Immerso"


def test_water_labels_and_legacy_values_are_unchanged():
    assert WATER_LABEL_IT == {
        WATER_STILL: "In acqua stagnante",
        WATER_FLOWING: "In acqua corrente",
    }
    assert water_legacy_value("In acqua stagnante") == "stagnante"
    assert water_legacy_value("In acqua corrente") == "corrente"


def test_heavy_blanket_label_is_shared_between_uis():
    expected = "Coperte pesanti/Mantelline termiche"
    assert FULL_CLOTHING_LABEL_IT[BLANKET_HEAVY] == expected
    assert MSIL_CLOTHING_LABEL_IT[BLANKET_HEAVY] == expected
