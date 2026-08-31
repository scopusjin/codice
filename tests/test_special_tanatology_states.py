# -*- coding: utf-8 -*-

import unittest

from app.parameters import INF_HOURS, dati_parametri_aggiuntivi
from app.special_tanatology_states import (
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_MECHANICAL_MUSCLE,
    PARAM_CHEMICAL_PUPILLARY,
    OPTION_NOT_ASSESSED,
    OPTION_UNRELIABLE,
    OPTION_NO_REACTION,
    SUPRA_PHASE_I,
    SUPRA_PHASE_II,
    SUPRA_PHASE_III,
    SUPRA_PHASE_IV,
    SUPRA_PHASE_V,
    SUPRA_PHASE_VI,
    PERIORAL_MARKED,
    PERIORAL_MODERATE,
    PERIORAL_SLIGHT,
    MECH_WHOLE_MUSCLE,
    MECH_REVERSIBLE_SWELLING,
    MECH_SMALL_PERSISTENT_SWELLING,
    PUPILLARY_POSITIVE,
    PUPILLARY_NEGATIVE,
    SPECIAL_PARAM_LABEL_IT,
    special_option_ids,
    special_option_legacy_labels,
    special_range,
)


EXPECTED_RANGES = {
    PARAM_ELECTRICAL_SUPRACILIARY: {
        OPTION_NOT_ASSESSED: None,
        SUPRA_PHASE_I: (5, 22),
        SUPRA_PHASE_II: (5, 16),
        SUPRA_PHASE_III: (3.5, 13),
        SUPRA_PHASE_IV: (3, 8),
        SUPRA_PHASE_V: (2, 7),
        SUPRA_PHASE_VI: (1, 6),
        OPTION_NO_REACTION: (5, INF_HOURS),
        OPTION_UNRELIABLE: None,
    },
    PARAM_ELECTRICAL_PERIORAL: {
        OPTION_NOT_ASSESSED: None,
        PERIORAL_MARKED: (0, 11),
        PERIORAL_MODERATE: (0, 11),
        PERIORAL_SLIGHT: (0, 11),
        OPTION_NO_REACTION: (3, INF_HOURS),
        OPTION_UNRELIABLE: None,
    },
    PARAM_MECHANICAL_MUSCLE: {
        OPTION_NOT_ASSESSED: None,
        MECH_WHOLE_MUSCLE: (0, 2.5),
        MECH_REVERSIBLE_SWELLING: (0, 5),
        MECH_SMALL_PERSISTENT_SWELLING: (0, 12),
        OPTION_NO_REACTION: (1.5, INF_HOURS),
        OPTION_UNRELIABLE: None,
    },
    PARAM_CHEMICAL_PUPILLARY: {
        OPTION_NOT_ASSESSED: None,
        OPTION_UNRELIABLE: None,
        PUPILLARY_POSITIVE: (0, 30),
        PUPILLARY_NEGATIVE: (5, INF_HOURS),
    },
}


class SpecialTanatologyStateTests(unittest.TestCase):
    def test_parameter_order_and_labels_match_legacy_data(self):
        self.assertEqual(
            list(SPECIAL_PARAM_LABEL_IT.values()),
            list(dati_parametri_aggiuntivi.keys()),
        )

    def test_option_order_and_labels_match_legacy_data(self):
        for param_id, param_label in SPECIAL_PARAM_LABEL_IT.items():
            self.assertEqual(
                list(special_option_legacy_labels(param_id)),
                list(dati_parametri_aggiuntivi[param_label]["opzioni"]),
            )

    def test_all_current_ranges_are_locked(self):
        for param_id, expected_options in EXPECTED_RANGES.items():
            for option_id, expected_range in expected_options.items():
                self.assertEqual(special_range(param_id, option_id), expected_range)

    def test_expected_range_set_covers_every_option(self):
        for param_id, expected_options in EXPECTED_RANGES.items():
            self.assertEqual(set(expected_options), set(special_option_ids(param_id)))


if __name__ == "__main__":
    unittest.main()
