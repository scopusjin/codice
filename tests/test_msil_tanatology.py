# -*- coding: utf-8 -*-

import unittest

from app.msil_tanatology import (
    MSIL_LIVOR_STATE_BY_LABEL,
    MSIL_RIGOR_STATE_BY_LABEL,
    msil_livor_labels,
    msil_rigor_labels,
    msil_livor_state_id,
    msil_rigor_state_id,
    msil_livor_legacy_value,
    msil_rigor_legacy_value,
)


class MSILTanatologyMappingTests(unittest.TestCase):
    def test_msil_livor_values_are_legacy_compatible(self):
        expected = {
            "🩸 IPOSTASI?": "Non valutate",
            "Ipostasi assenti": "Non ancora comparse",
            "Ipostasi almeno in parte migrabili": "Migrabili perlomeno parzialmente",
            "Ipostasi non migrabili": "Fisse",
        }
        expected_labels = tuple(expected.keys())
        self.assertEqual(set(MSIL_LIVOR_STATE_BY_LABEL), set(expected))
        self.assertEqual(msil_livor_labels(), expected_labels)
        self.assertEqual(msil_livor_labels("it"), expected_labels)
        for ui_label, legacy_value in expected.items():
            self.assertEqual(
                msil_livor_state_id(ui_label),
                MSIL_LIVOR_STATE_BY_LABEL[ui_label],
            )
            self.assertEqual(msil_livor_legacy_value(ui_label), legacy_value)
            self.assertEqual(msil_livor_legacy_value(ui_label, "it"), legacy_value)

    def test_msil_rigor_values_are_legacy_compatible(self):
        expected = {
            "💪🏻 RIGOR MORTIS?": "Non valutata",
            "Rigor assente": "Non ancora apprezzabile",
            "Rigor presente e in aumento": "Presente e in via di intensificazione e generalizzazione",
            "Rigor ubiquitario e di intensità massima": "Presente, intensa e generalizzata",
            "Rigor in risoluzione": "In via di risoluzione",
            "Rigor risolto": "Risolta",
        }
        expected_labels = tuple(expected.keys())
        self.assertEqual(set(MSIL_RIGOR_STATE_BY_LABEL), set(expected))
        self.assertEqual(msil_rigor_labels(), expected_labels)
        self.assertEqual(msil_rigor_labels("it"), expected_labels)
        for ui_label, legacy_value in expected.items():
            self.assertEqual(
                msil_rigor_state_id(ui_label),
                MSIL_RIGOR_STATE_BY_LABEL[ui_label],
            )
            self.assertEqual(msil_rigor_legacy_value(ui_label), legacy_value)
            self.assertEqual(msil_rigor_legacy_value(ui_label, "it"), legacy_value)


if __name__ == "__main__":
    unittest.main()
