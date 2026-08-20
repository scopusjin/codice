# -*- coding: utf-8 -*-

import unittest

from app.parameters import INF_HOURS
from app.tanatology_data import (
    LIVOR_RANGES_BY_ID,
    LIVOR_TYPICAL_RANGES_BY_ID,
    RIGOR_RANGES_BY_ID,
    RIGOR_TYPICAL_RANGES_BY_ID,
)
from app.tanatology_states import (
    LIVOR_NOT_ASSESSED,
    LIVOR_ABSENT,
    LIVOR_CONFLUING,
    LIVOR_FULLY_MIGRATABLE,
    LIVOR_PARTIALLY_MIGRATABLE,
    LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE,
    LIVOR_FIXED,
    LIVOR_UNRELIABLE,
    RIGOR_NOT_ASSESSED,
    RIGOR_ABSENT,
    RIGOR_DEVELOPING,
    RIGOR_FULL,
    RIGOR_RESOLVING,
    RIGOR_RESOLVED,
    RIGOR_UNRELIABLE,
)


class TanatologyDataTests(unittest.TestCase):
    def test_livor_ranges_are_unchanged(self):
        self.assertEqual(LIVOR_RANGES_BY_ID, {
            LIVOR_NOT_ASSESSED: None,
            LIVOR_ABSENT: (0, 3),
            LIVOR_CONFLUING: (1, 4),
            LIVOR_FULLY_MIGRATABLE: (0, 6),
            LIVOR_PARTIALLY_MIGRATABLE: (4, 24),
            LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: (0, 24),
            LIVOR_FIXED: (4, INF_HOURS),
            LIVOR_UNRELIABLE: None,
        })

    def test_livor_typical_ranges_are_unchanged(self):
        self.assertEqual(LIVOR_TYPICAL_RANGES_BY_ID, {
            LIVOR_NOT_ASSESSED: None,
            LIVOR_ABSENT: (0, 0.33),
            LIVOR_CONFLUING: (1.5, 3.5),
            LIVOR_FULLY_MIGRATABLE: (0.33, 6),
            LIVOR_PARTIALLY_MIGRATABLE: (6, 12),
            LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: None,
            LIVOR_FIXED: (12, INF_HOURS),
            LIVOR_UNRELIABLE: None,
        })

    def test_rigor_ranges_are_unchanged(self):
        self.assertEqual(RIGOR_RANGES_BY_ID, {
            RIGOR_NOT_ASSESSED: None,
            RIGOR_ABSENT: (0, 7),
            RIGOR_DEVELOPING: (0.5, 20),
            RIGOR_FULL: (2, 96),
            RIGOR_RESOLVING: (24, 192),
            RIGOR_RESOLVED: (24, INF_HOURS),
            RIGOR_UNRELIABLE: None,
        })

    def test_rigor_typical_ranges_are_unchanged(self):
        self.assertEqual(RIGOR_TYPICAL_RANGES_BY_ID, {
            RIGOR_NOT_ASSESSED: None,
            RIGOR_ABSENT: (0, 3),
            RIGOR_DEVELOPING: (2, 10),
            RIGOR_FULL: (10, 85),
            RIGOR_RESOLVING: (29, 140),
            RIGOR_RESOLVED: (76, INF_HOURS),
        })


if __name__ == "__main__":
    unittest.main()
