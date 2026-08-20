# -*- coding: utf-8 -*-

import unittest

from app.factor_calc import SURF_DISPLAY_ORDER
from app.surface_ui_states import (
    SURFACE_LABEL_IT,
    surface_legacy_value,
    surface_state_id,
)


class SurfaceUIStateTests(unittest.TestCase):
    def test_surface_labels_match_legacy_order_exactly(self):
        self.assertEqual(list(SURFACE_LABEL_IT.values()), list(SURF_DISPLAY_ORDER))

    def test_surface_round_trip_preserves_legacy_strings(self):
        for surface_id, label in SURFACE_LABEL_IT.items():
            self.assertEqual(surface_state_id(label), surface_id)
            self.assertEqual(surface_legacy_value(label), label)


if __name__ == "__main__":
    unittest.main()
