# -*- coding: utf-8 -*-

import unittest

from app.parameters import (
    opzioni_macchie,
    macchie_medi,
    opzioni_rigidita,
    rigidita_medi,
    dati_parametri_aggiuntivi,
)
from app.graphing_tanatology import (
    resolve_base_tanatology_ranges,
    resolve_special_tanatology_value,
)


class GraphingTanatologyCompatibilityTests(unittest.TestCase):
    def test_all_livor_ranges_match_legacy_dictionaries(self):
        rigor_default = next(iter(opzioni_rigidita))
        for label, expected_range in opzioni_macchie.items():
            resolved = resolve_base_tanatology_ranges(label, rigor_default)
            self.assertEqual(resolved.livor_range, expected_range)
            self.assertEqual(resolved.livor_typical_range, macchie_medi.get(label))

    def test_all_rigor_ranges_match_legacy_dictionaries(self):
        livor_default = next(iter(opzioni_macchie))
        for label, expected_range in opzioni_rigidita.items():
            resolved = resolve_base_tanatology_ranges(livor_default, label)
            self.assertEqual(resolved.rigor_range, expected_range)
            self.assertEqual(resolved.rigor_typical_range, rigidita_medi.get(label))

    def test_unknown_base_labels_keep_old_permissive_lookup_behavior(self):
        resolved = resolve_base_tanatology_ranges("__unknown_livor__", "__unknown_rigor__")
        self.assertIsNone(resolved.livor_id)
        self.assertIsNone(resolved.livor_range)
        self.assertIsNone(resolved.livor_typical_range)
        self.assertIsNone(resolved.rigor_id)
        self.assertIsNone(resolved.rigor_range)
        self.assertIsNone(resolved.rigor_typical_range)

    def test_all_special_ranges_and_descriptions_match_legacy_data(self):
        for parameter_label, data in dati_parametri_aggiuntivi.items():
            for option_label in data["opzioni"]:
                resolved = resolve_special_tanatology_value(parameter_label, option_label)
                self.assertEqual(
                    resolved.range_value,
                    data["range"].get(option_label),
                    msg=f"Range mismatch: {parameter_label} / {option_label}",
                )
                self.assertEqual(
                    resolved.description,
                    data["descrizioni"].get(option_label),
                    msg=f"Description mismatch: {parameter_label} / {option_label}",
                )
                self.assertEqual(
                    resolved.is_not_assessed,
                    option_label == "Non valutata",
                )

    def test_perioral_colon_suffix_preserves_existing_normalization(self):
        parameter_label = "Eccitabilità elettrica peribuccale"
        resolved = resolve_special_tanatology_value(
            parameter_label,
            "Discreta (++): nota accessoria",
        )
        self.assertEqual(
            resolved.range_value,
            dati_parametri_aggiuntivi[parameter_label]["range"]["Discreta (++)"],
        )
        self.assertEqual(
            resolved.description,
            dati_parametri_aggiuntivi[parameter_label]["descrizioni"]["Discreta (++)"],
        )


if __name__ == "__main__":
    unittest.main()
