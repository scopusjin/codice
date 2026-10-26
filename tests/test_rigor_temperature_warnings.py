# -*- coding: utf-8 -*-

import unittest

from app import i18n
from app.graphing import _rigor_temperature_warning_keys


class RigorTemperatureWarningTests(unittest.TestCase):
    def test_standard_thresholds_are_inclusive(self):
        rigor_range = (0, 7)
        self.assertEqual(
            _rigor_temperature_warning_keys(rigor_range, 10, {}),
            ["graph.rigor_low_temperature_warning"],
        )
        self.assertEqual(
            _rigor_temperature_warning_keys(rigor_range, 30, {}),
            ["graph.rigor_high_temperature_warning"],
        )
        self.assertEqual(
            _rigor_temperature_warning_keys(rigor_range, 20, {}),
            [],
        )

    def test_prudent_temperature_range_checks_both_extremes(self):
        rigor_range = (2, 96)
        options = {
            "stima_cautelativa_beta": True,
            "Ta_min_beta": 9,
            "Ta_max_beta": 31,
        }
        self.assertEqual(
            _rigor_temperature_warning_keys(rigor_range, 20, options),
            [
                "graph.rigor_low_temperature_warning",
                "graph.rigor_high_temperature_warning",
            ],
        )

    def test_no_warning_without_usable_rigor_range(self):
        self.assertEqual(
            _rigor_temperature_warning_keys(None, 5, {}),
            [],
        )

    def test_warning_texts_do_not_expose_thresholds(self):
        self.assertEqual(
            i18n.ui_text("graph.rigor_low_temperature_warning"),
            "La bassa temperatura ambientale può rallentare il decorso della rigidità cadaverica e prolungarne la persistenza.",
        )
        self.assertEqual(
            i18n.ui_text("graph.rigor_high_temperature_warning"),
            "L'elevata temperatura ambientale può accelerare la comparsa e la successiva risoluzione della rigidità cadaverica.",
        )


if __name__ == "__main__":
    unittest.main()
