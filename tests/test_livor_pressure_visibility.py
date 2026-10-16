# -*- coding: utf-8 -*-
"""La preferenza per la digitopressione resta distinta dal reperto tanatologico."""

import unittest

from app.livor_digitopressione import (
    PRESSURE_KEY,
    PRESSURE_VISIBILITY_KEY,
    PRESSURE_NOT_ASSESSED,
    PRESSURE_COMPLETE_FADING,
    PRESSURE_INCOMPLETE_FADING,
    effective_livor_pressure,
    pressure_is_enabled,
)
from app.graphing_tanatology import resolve_base_tanatology_ranges


class LivorPressureVisibilityTests(unittest.TestCase):
    def test_visible_by_default(self):
        state = {}
        self.assertTrue(pressure_is_enabled(state))
        self.assertEqual(effective_livor_pressure(state), PRESSURE_NOT_ASSESSED)

    def test_existing_answer_is_ignored_when_hidden_and_not_deleted(self):
        for choice in (PRESSURE_COMPLETE_FADING, PRESSURE_INCOMPLETE_FADING):
            state = {PRESSURE_KEY: choice, PRESSURE_VISIBILITY_KEY: False}
            self.assertFalse(pressure_is_enabled(state))
            self.assertEqual(effective_livor_pressure(state), PRESSURE_NOT_ASSESSED)
            self.assertEqual(state[PRESSURE_KEY], choice)
            selected = resolve_base_tanatology_ranges(
                "In via di confluenza", "Non valutata",
                effective_livor_pressure(state),
            )
            self.assertEqual(selected.livor_range, (0, 4))

    def test_enabled_answer_is_preserved_for_the_same_livor(self):
        state = {
            PRESSURE_KEY: PRESSURE_INCOMPLETE_FADING,
            PRESSURE_VISIBILITY_KEY: False,
        }
        self.assertEqual(effective_livor_pressure(state), PRESSURE_NOT_ASSESSED)
        state[PRESSURE_VISIBILITY_KEY] = True
        self.assertEqual(effective_livor_pressure(state), PRESSURE_INCOMPLETE_FADING)
        selected = resolve_base_tanatology_ranges(
            "In via di confluenza", "Non valutata",
            effective_livor_pressure(state),
        )
        self.assertEqual(selected.livor_range, (1, 4))

    def test_invalid_pressure_value_never_affects_calculation(self):
        state = {PRESSURE_KEY: "obsolete-value", PRESSURE_VISIBILITY_KEY: True}
        self.assertEqual(effective_livor_pressure(state), PRESSURE_NOT_ASSESSED)


if __name__ == "__main__":
    unittest.main()
