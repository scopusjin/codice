# -*- coding: utf-8 -*-

import unittest

from app.factor_ui_states import (
    BODY_LABEL_IT,
    BODY_LEGACY_VALUE,
    WATER_LABEL_IT,
    WATER_LEGACY_VALUE,
    MSIL_CLOTHING_LABEL_IT,
)
from app.surface_ui_states import SURFACE_LABEL_IT
from app.msil_factor_ui import (
    MSIL_BODY_STATE_BY_LABEL,
    MSIL_WATER_STATE_BY_LABEL,
    MSIL_SURFACE_STATE_BY_LABEL,
    msil_body_labels,
    msil_body_state_id,
    msil_body_legacy_value,
    msil_water_labels,
    msil_water_state_id,
    msil_water_legacy_value,
    msil_clothing_label,
    msil_surface_labels,
    msil_surface_label,
    msil_surface_state_id,
    msil_surface_legacy_value,
)


class MSILFactorUiCompatibilityTests(unittest.TestCase):
    def test_body_labels_and_legacy_values_match_current_ui(self):
        expected_labels = tuple(BODY_LABEL_IT.values())
        self.assertEqual(msil_body_labels(), expected_labels)
        self.assertEqual(msil_body_labels("it"), expected_labels)
        self.assertEqual(
            MSIL_BODY_STATE_BY_LABEL,
            {label: state_id for state_id, label in BODY_LABEL_IT.items()},
        )
        for state_id, label in BODY_LABEL_IT.items():
            self.assertEqual(msil_body_state_id(label), state_id)
            self.assertEqual(msil_body_legacy_value(label), BODY_LEGACY_VALUE[state_id])
            self.assertEqual(msil_body_legacy_value(label, "it"), BODY_LEGACY_VALUE[state_id])

    def test_water_labels_and_legacy_values_match_current_ui(self):
        expected_labels = tuple(WATER_LABEL_IT.values())
        self.assertEqual(msil_water_labels(), expected_labels)
        self.assertEqual(msil_water_labels("it"), expected_labels)
        self.assertEqual(
            MSIL_WATER_STATE_BY_LABEL,
            {label: state_id for state_id, label in WATER_LABEL_IT.items()},
        )
        for state_id, label in WATER_LABEL_IT.items():
            self.assertEqual(msil_water_state_id(label), state_id)
            self.assertEqual(msil_water_legacy_value(label), WATER_LEGACY_VALUE[state_id])
            self.assertEqual(msil_water_legacy_value(label, "it"), WATER_LEGACY_VALUE[state_id])

    def test_msil_clothing_labels_match_current_ui(self):
        for category_id, label in MSIL_CLOTHING_LABEL_IT.items():
            self.assertEqual(msil_clothing_label(category_id), label)
            self.assertEqual(msil_clothing_label(category_id, "it"), label)

    def test_surface_labels_and_legacy_values_match_current_ui(self):
        expected_labels = tuple(SURFACE_LABEL_IT.values())
        self.assertEqual(msil_surface_labels(), expected_labels)
        self.assertEqual(msil_surface_labels("it"), expected_labels)
        self.assertEqual(
            MSIL_SURFACE_STATE_BY_LABEL,
            {label: surface_id for surface_id, label in SURFACE_LABEL_IT.items()},
        )
        for surface_id, label in SURFACE_LABEL_IT.items():
            self.assertEqual(msil_surface_label(surface_id), label)
            self.assertEqual(msil_surface_label(surface_id, "it"), label)
            self.assertEqual(msil_surface_state_id(label), surface_id)
            self.assertEqual(msil_surface_legacy_value(label), label)
            self.assertEqual(msil_surface_legacy_value(label, "it"), label)

    def test_unknown_labels_keep_key_error_behavior(self):
        with self.assertRaises(KeyError):
            msil_body_legacy_value("unknown")
        with self.assertRaises(KeyError):
            msil_water_legacy_value("unknown")
        with self.assertRaises(KeyError):
            msil_surface_label("unknown")
        with self.assertRaises(KeyError):
            msil_surface_legacy_value("unknown")
        with self.assertRaises(KeyError):
            msil_clothing_label("unknown")


if __name__ == "__main__":
    unittest.main()
