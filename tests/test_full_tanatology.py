# -*- coding: utf-8 -*-

import unittest

from app.full_tanatology import (
    FULL_LIVOR_STATE_BY_LABEL,
    FULL_RIGOR_STATE_BY_LABEL,
    FULL_SPECIAL_PARAM_BY_LABEL,
    full_livor_labels,
    full_rigor_labels,
    full_livor_state_id,
    full_rigor_state_id,
    full_livor_legacy_value,
    full_rigor_legacy_value,
    full_special_parameter_ids,
    full_special_parameter_labels,
    full_special_parameter_id,
    full_special_parameter_legacy_value,
    full_special_option_labels,
    full_special_option_id,
    full_special_option_legacy_value,
)
from app.parameters import (
    opzioni_macchie,
    dati_parametri_aggiuntivi,
)
from app.special_tanatology_states import (
    PARAM_ELECTRICAL_SUPRACILIARY,
    SPECIAL_PARAM_LABEL_IT,
    special_option_ids,
    special_option_legacy_labels,
)


class FullTanatologyMappingTests(unittest.TestCase):
    def test_full_livor_ui_matches_current_parameter_options(self):
        current_labels = tuple(opzioni_macchie.keys())
        self.assertEqual(
            tuple(FULL_LIVOR_STATE_BY_LABEL.keys()),
            current_labels,
        )
        self.assertEqual(full_livor_labels(), current_labels)
        self.assertEqual(full_livor_labels("it"), current_labels)
        for ui_label in opzioni_macchie:
            self.assertEqual(
                full_livor_state_id(ui_label),
                FULL_LIVOR_STATE_BY_LABEL[ui_label],
            )
            self.assertEqual(full_livor_legacy_value(ui_label), ui_label)

    def test_full_rigor_ui_matches_current_labels_and_legacy_values(self):
        current_labels = (
            "Non valutata",
            "Non ancora apprezzabile",
            "Presente, in aumento",
            "Presente, intensa e generalizzata",
            "In via di risoluzione",
            "Risolta",
            "Non valutabile/Non attendibile",
        )
        self.assertEqual(
            tuple(FULL_RIGOR_STATE_BY_LABEL.keys()),
            current_labels,
        )
        self.assertEqual(full_rigor_labels(), current_labels)
        self.assertEqual(full_rigor_labels("it"), current_labels)
        for ui_label in current_labels:
            self.assertEqual(
                full_rigor_state_id(ui_label),
                FULL_RIGOR_STATE_BY_LABEL[ui_label],
            )
            expected_legacy = (
                "Presente e in via di intensificazione e generalizzazione"
                if ui_label == "Presente, in aumento"
                else ui_label
            )
            self.assertEqual(full_rigor_legacy_value(ui_label), expected_legacy)

    def test_full_special_parameter_ui_matches_current_order_and_legacy_values(self):
        current_ids = tuple(SPECIAL_PARAM_LABEL_IT.keys())
        current_labels = tuple(SPECIAL_PARAM_LABEL_IT.values())
        self.assertEqual(tuple(FULL_SPECIAL_PARAM_BY_LABEL.keys()), current_labels)
        self.assertEqual(full_special_parameter_ids(), current_ids)
        self.assertEqual(full_special_parameter_labels(), current_labels)
        self.assertEqual(full_special_parameter_labels("it"), current_labels)

        for param_id, legacy_label in SPECIAL_PARAM_LABEL_IT.items():
            self.assertEqual(full_special_parameter_id(legacy_label), param_id)
            self.assertEqual(
                full_special_parameter_legacy_value(param_id),
                legacy_label,
            )
            self.assertIn(legacy_label, dati_parametri_aggiuntivi)

    def test_full_special_options_match_current_order_ids_and_legacy_values(self):
        for param_id in SPECIAL_PARAM_LABEL_IT:
            current_labels = tuple(special_option_legacy_labels(param_id))
            self.assertEqual(full_special_option_labels(param_id), current_labels)
            self.assertEqual(full_special_option_labels(param_id, "it"), current_labels)

            for option_id, legacy_label in zip(
                special_option_ids(param_id),
                current_labels,
            ):
                self.assertEqual(
                    full_special_option_id(param_id, legacy_label),
                    option_id,
                )
                self.assertEqual(
                    full_special_option_legacy_value(param_id, legacy_label),
                    legacy_label,
                )

    def test_unknown_special_labels_preserve_key_errors(self):
        with self.assertRaises(KeyError):
            full_special_parameter_id("unknown")
        with self.assertRaises(KeyError):
            full_special_option_id(PARAM_ELECTRICAL_SUPRACILIARY, "unknown")


if __name__ == "__main__":
    unittest.main()
