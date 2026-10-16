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
    FAMILY_LIVOR,
    FAMILY_RIGOR,
    FAMILY_COOLING,
    legacy_family_key,
    special_family_id,
    resolve_base_tanatology_ranges,
    resolve_special_tanatology_value,
)
from app.special_tanatology_states import PARAM_ELECTRICAL_SUPRACILIARY
from app.livor_digitopressione import PRESSURE_COMPLETE_FADING, PRESSURE_INCOMPLETE_FADING


class GraphingTanatologyCompatibilityTests(unittest.TestCase):
    def test_stable_graph_family_ids_keep_legacy_grouping_fallback(self):
        self.assertEqual(FAMILY_LIVOR, "livor")
        self.assertEqual(FAMILY_RIGOR, "rigor")
        self.assertEqual(FAMILY_COOLING, "cooling")
        self.assertEqual(
            legacy_family_key("Raffreddamento cadaverico (intervallo minimo)"),
            "raffreddamento cadaverico",
        )
        self.assertEqual(
            special_family_id(
                PARAM_ELECTRICAL_SUPRACILIARY,
                "Eccitabilità elettrica sopraciliare",
            ),
            f"special:{PARAM_ELECTRICAL_SUPRACILIARY}",
        )
        self.assertEqual(
            special_family_id(None, "Parametro legacy (nota)"),
            "legacy:parametro legacy",
        )

    def test_all_livor_ranges_match_legacy_dictionaries(self):
        rigor_default = next(iter(opzioni_rigidita))
        for label, expected_range in opzioni_macchie.items():
            resolved = resolve_base_tanatology_ranges(label, rigor_default)
            self.assertEqual(resolved.livor_range, expected_range)
            self.assertEqual(resolved.livor_typical_range, macchie_medi.get(label))

    def test_confluence_and_migrability_are_independent_clinical_intervals(self):
        expected = {
            "In via di confluenza": (0, 4),
            "Confluenti (migrabilità non valutata)": (1, 200),
            "Confluenti e completamente migrabili": (1, 6),
            "Completamente migrabili": (0, 6),
            "Parzialmente migrabili": (4, 24),
            "Migrabili perlomeno parzialmente": (0, 24),
            "Fisse": (4, 200),
        }
        for state, expected_range in expected.items():
            self.assertEqual(
                resolve_base_tanatology_ranges(state, "Non valutata").livor_range,
                expected_range,
            )

    def test_digitopressione_intersects_only_livor_bounds(self):
        examples = (
            ("In via di confluenza", PRESSURE_INCOMPLETE_FADING, (1, 4), (1.5, 3.5)),
            ("Completamente migrabili", PRESSURE_INCOMPLETE_FADING, (1, 6), (1, 6)),
            ("Confluenti (migrabilità non valutata)", PRESSURE_COMPLETE_FADING, (1, 20), None),
            ("Parzialmente migrabili", PRESSURE_COMPLETE_FADING, (4, 20), (6, 12)),
            ("Fisse", PRESSURE_COMPLETE_FADING, (4, 20), (12, 20)),
        )
        for state, pressure, expected, expected_typical in examples:
            with self.subTest(state=state, pressure=pressure):
                base = resolve_base_tanatology_ranges(state, "Non valutata")
                combined = resolve_base_tanatology_ranges(state, "Non valutata", pressure)
                self.assertEqual(combined.livor_range, expected)
                self.assertEqual(combined.livor_typical_range, expected_typical)
                self.assertEqual(combined.rigor_range, base.rigor_range)
        # Un rilievo residuo non deve modificare ipostasi assenti/non valutate.
        for state in ("Non ancora comparse", "Non valutate", "Non valutabili/Non attendibili"):
            self.assertEqual(
                resolve_base_tanatology_ranges(state, "Non valutata", PRESSURE_INCOMPLETE_FADING),
                resolve_base_tanatology_ranges(state, "Non valutata"),
            )

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

    def test_all_special_ranges_and_descriptions_match_current_data(self):
        for parameter_label, data in dati_parametri_aggiuntivi.items():
            for option_label in data["opzioni"]:
                resolved = resolve_special_tanatology_value(parameter_label, option_label)
                self.assertEqual(
                    resolved.range_value,
                    data["range"].get(option_label),
                    msg=f"Range mismatch: {parameter_label} / {option_label}",
                )
                expected_description = data["descrizioni"].get(option_label)
                if expected_description is not None:
                    self.assertEqual(
                        resolved.description,
                        expected_description,
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
            "Muscoli peribuccali (++): nota accessoria",
        )
        self.assertEqual(
            resolved.range_value,
            dati_parametri_aggiuntivi[parameter_label]["range"]["Muscoli peribuccali (++)"],
        )
        self.assertEqual(
            resolved.description,
            dati_parametri_aggiuntivi[parameter_label]["descrizioni"]["Muscoli peribuccali (++)"],
        )

    def test_unknown_special_parameter_preserves_legacy_key_error(self):
        with self.assertRaises(KeyError):
            resolve_special_tanatology_value(
                "__unknown_parameter__",
                "Non valutata",
            )


if __name__ == "__main__":
    unittest.main()
