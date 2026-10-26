# -*- coding: utf-8 -*-

import unittest

from app.factor_ui_states import (
    BODY_LABEL_IT,
    BODY_LEGACY_VALUE,
    WATER_LABEL_IT,
    WATER_LEGACY_VALUE,
    FULL_CLOTHING_LABEL_IT,
)
from app.surface_ui_states import SURFACE_LABEL_IT
from app.full_factor_ui import (
    FULL_BODY_STATE_BY_LABEL,
    FULL_WATER_STATE_BY_LABEL,
    FULL_SURFACE_STATE_BY_LABEL,
    full_body_labels,
    full_body_state_id,
    full_body_legacy_value,
    full_water_labels,
    full_water_state_id,
    full_water_legacy_value,
    full_clothing_label,
    full_surface_labels,
    full_surface_label,
    full_surface_state_id,
    full_surface_legacy_value,
)


class FullFactorUiCompatibilityTests(unittest.TestCase):
    def test_body_labels_and_legacy_values_match_current_italian_ui(self):
        expected_labels = tuple(BODY_LABEL_IT.values())
        self.assertEqual(full_body_labels(), expected_labels)
        self.assertEqual(full_body_labels("it"), expected_labels)
        self.assertEqual(
            FULL_BODY_STATE_BY_LABEL,
            {label: state_id for state_id, label in BODY_LABEL_IT.items()},
        )
        for state_id, label in BODY_LABEL_IT.items():
            self.assertEqual(full_body_state_id(label), state_id)
            self.assertEqual(full_body_legacy_value(label), BODY_LEGACY_VALUE[state_id])
            self.assertEqual(full_body_legacy_value(label, "it"), BODY_LEGACY_VALUE[state_id])

    def test_water_labels_and_legacy_values_match_current_italian_ui(self):
        expected_labels = tuple(WATER_LABEL_IT.values())
        self.assertEqual(full_water_labels(), expected_labels)
        self.assertEqual(full_water_labels("it"), expected_labels)
        self.assertEqual(
            FULL_WATER_STATE_BY_LABEL,
            {label: state_id for state_id, label in WATER_LABEL_IT.items()},
        )
        for state_id, label in WATER_LABEL_IT.items():
            self.assertEqual(full_water_state_id(label), state_id)
            self.assertEqual(full_water_legacy_value(label), WATER_LEGACY_VALUE[state_id])
            self.assertEqual(full_water_legacy_value(label, "it"), WATER_LEGACY_VALUE[state_id])

    def test_clothing_labels_match_current_italian_ui(self):
        for category_id, label in FULL_CLOTHING_LABEL_IT.items():
            self.assertEqual(full_clothing_label(category_id), label)
            self.assertEqual(full_clothing_label(category_id, "it"), label)

    def test_surface_labels_and_legacy_values_match_current_italian_ui(self):
        expected_labels = tuple(SURFACE_LABEL_IT.values())
        self.assertEqual(full_surface_labels(), expected_labels)
        self.assertEqual(full_surface_labels("it"), expected_labels)
        self.assertEqual(
            FULL_SURFACE_STATE_BY_LABEL,
            {label: surface_id for surface_id, label in SURFACE_LABEL_IT.items()},
        )
        for surface_id, label in SURFACE_LABEL_IT.items():
            self.assertEqual(full_surface_label(surface_id), label)
            self.assertEqual(full_surface_label(surface_id, "it"), label)
            self.assertEqual(full_surface_state_id(label), surface_id)
            self.assertEqual(full_surface_legacy_value(label), label)
            self.assertEqual(full_surface_legacy_value(label, "it"), label)

    def test_unknown_labels_keep_key_error_behavior(self):
        with self.assertRaises(KeyError):
            full_body_legacy_value("unknown")
        with self.assertRaises(KeyError):
            full_water_legacy_value("unknown")
        with self.assertRaises(KeyError):
            full_surface_legacy_value("unknown")
        with self.assertRaises(KeyError):
            full_clothing_label("unknown")


if __name__ == "__main__":
    unittest.main()
