# -*- coding: utf-8 -*-
"""Gli errori di validazione del raffreddamento non sono descrizioni tanatologiche."""

import datetime
import unittest

from app.graphing_cooling import compute_cooling_state


class CoolingValidationDetailsTests(unittest.TestCase):
    def _compute(self, **overrides):
        values = {
            "input_rt": None,
            "input_ta": None,
            "input_tm": 37.2,
            "input_w": None,
            "fattore_correzione": None,
            "data_ora_ispezione": datetime.datetime(2026, 10, 16, 12, 0),
            "skip_warnings": True,
            "cooling_options": {},
        }
        values.update(overrides)
        return compute_cooling_state(**values)

    def test_missing_cooling_inputs_keep_warning_but_not_description(self):
        result = self._compute()
        self.assertIsNotNone(result.validation_error)
        self.assertIn("Mancano", result.validation_error)
        self.assertFalse(result.raffreddamento_calcolabile)
        self.assertEqual(result.detail_blocks, ())

    def test_invalid_factor_keeps_warning_but_not_description(self):
        result = self._compute(
            input_rt=30.0, input_ta=20.0, input_w=70.0,
            fattore_correzione=0,
        )
        self.assertIn("FC valido", result.validation_error)
        self.assertFalse(result.raffreddamento_calcolabile)
        self.assertEqual(result.detail_blocks, ())


if __name__ == "__main__":
    unittest.main()
