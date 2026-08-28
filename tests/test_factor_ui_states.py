# -*- coding: utf-8 -*-

import unittest

from app.factor_ui_states import (
    BLANKET_HEAVY,
    BLANKET_MEDIUM,
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


class FactorUIStateTests(unittest.TestCase):
    def test_body_labels_and_legacy_values_are_unchanged(self):
        self.assertEqual(BODY_LABEL_IT, {
            BODY_DRY: "Corpo asciutto",
            BODY_WET: "Bagnato",
            BODY_IMMERSED: "Immerso",
        })
        self.assertEqual(body_legacy_value("Corpo asciutto"), "Asciutto")
        self.assertEqual(body_legacy_value("Bagnato"), "Bagnato")
        self.assertEqual(body_legacy_value("Immerso"), "Immerso")

    def test_water_labels_and_legacy_values_are_unchanged(self):
        self.assertEqual(WATER_LABEL_IT, {
            WATER_STILL: "In acqua stagnante",
            WATER_FLOWING: "In acqua corrente",
        })
        self.assertEqual(water_legacy_value("In acqua stagnante"), "stagnante")
        self.assertEqual(water_legacy_value("In acqua corrente"), "corrente")

    def test_blanket_labels_are_updated_only_in_full_ui(self):
        self.assertEqual(
            FULL_CLOTHING_LABEL_IT[BLANKET_MEDIUM],
            "Coperta / copriletto spesso",
        )
        self.assertEqual(
            FULL_CLOTHING_LABEL_IT[BLANKET_HEAVY],
            "Piumone / coperta molto spessa",
        )
        self.assertEqual(
            MSIL_CLOTHING_LABEL_IT[BLANKET_MEDIUM],
            "Coperte di medio spessore",
        )
        self.assertEqual(
            MSIL_CLOTHING_LABEL_IT[BLANKET_HEAVY],
            "Coperte pesanti/Mantelline termiche",
        )


if __name__ == "__main__":
    unittest.main()
