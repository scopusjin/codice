# -*- coding: utf-8 -*-

import unittest

from app.tanatology_states import (
    LIVOR_LABEL_IT,
    RIGOR_LABEL_IT,
    livor_legacy_label,
    rigor_legacy_label,
    livor_state_id,
    rigor_state_id,
)


class TanatologyStateMappingTests(unittest.TestCase):
    def test_livor_round_trip(self):
        for state_id, label in LIVOR_LABEL_IT.items():
            self.assertEqual(livor_legacy_label(state_id), label)
            self.assertEqual(livor_state_id(label), state_id)

    def test_rigor_round_trip(self):
        for state_id, label in RIGOR_LABEL_IT.items():
            self.assertEqual(rigor_legacy_label(state_id), label)
            self.assertEqual(rigor_state_id(label), state_id)

    def test_labels_are_unique(self):
        self.assertEqual(len(LIVOR_LABEL_IT), len(set(LIVOR_LABEL_IT.values())))
        self.assertEqual(len(RIGOR_LABEL_IT), len(set(RIGOR_LABEL_IT.values())))


if __name__ == "__main__":
    unittest.main()
