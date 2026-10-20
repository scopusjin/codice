# -*- coding: utf-8 -*-

import unittest

LEGACY_SURFACE_ORDER = ['Pavimento di casa/piano in legno.', 'Asfalto/terreno/prato asciutti', 'Materasso/tappeto spesso', 'Divano/sacco a pelo tecnico/polistirolo', 'Cemento/pietra/PVC', 'Pavimento freddo (all’aperto/in cantina)', 'Piano metallico (all’interno)', 'Piano metallico spesso (all’aperto)', 'Strato di foglie umide (≥2 cm)', 'Strato di foglie secche (≥2 cm)']
from app.surface_ui_states import (
    SURFACE_LABEL_IT,
    surface_legacy_value,
    surface_state_id,
)


class SurfaceUIStateTests(unittest.TestCase):
    def test_surface_labels_match_legacy_order_exactly(self):
        self.assertEqual(list(SURFACE_LABEL_IT.values()), LEGACY_SURFACE_ORDER)

    def test_surface_round_trip_preserves_legacy_strings(self):
        for surface_id, label in SURFACE_LABEL_IT.items():
            self.assertEqual(surface_state_id(label), surface_id)
            self.assertEqual(surface_legacy_value(label), label)


if __name__ == "__main__":
    unittest.main()
