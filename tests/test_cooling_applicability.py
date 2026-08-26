# -*- coding: utf-8 -*-

import datetime
import unittest

from app.cautelativa import compute_raffreddamento_cautelativo
from app.graphing_cooling import _aggregate_qd_status, _classify_qd_for_ta
from app.henssge import INF_HOURS, calcola_raffreddamento, round_to_step_minutes


class CoolingApplicabilityTests(unittest.TestCase):
    def test_qd_boundaries_are_strict(self):
        self.assertEqual(_classify_qd_for_ta(23.0, 0.2), "outside")
        self.assertEqual(_classify_qd_for_ta(23.0, 0.200001), "intermediate")
        self.assertEqual(_classify_qd_for_ta(23.0, 0.299999), "intermediate")
        self.assertEqual(_classify_qd_for_ta(23.0, 0.3), "optimal")
        self.assertEqual(_classify_qd_for_ta(24.0, 0.5), "outside")
        self.assertEqual(_classify_qd_for_ta(24.0, 0.500001), "optimal")

    def test_qd_status_aggregation_distinguishes_mixed_and_intermediate(self):
        self.assertEqual(
            _aggregate_qd_status({"optimal": 3, "intermediate": 0, "outside": 0}),
            "all_optimal",
        )
        self.assertEqual(
            _aggregate_qd_status({"optimal": 0, "intermediate": 3, "outside": 0}),
            "no_optimal_intermediate",
        )
        self.assertEqual(
            _aggregate_qd_status({"optimal": 1, "intermediate": 1, "outside": 1}),
            "mixed",
        )
        self.assertEqual(
            _aggregate_qd_status({"optimal": 0, "intermediate": 0, "outside": 3}),
            "all_outside",
        )

    def test_prudent_operational_henssge_excludes_outside_combinations(self):
        def solver(*, Ta, CF, peso_kg, **kwargs):
            if Ta <= 23.0:
                return 10.0, 20.0, 0.25
            return 5.0, 50.0, 0.40

        result = compute_raffreddamento_cautelativo(
            dt_ispezione=datetime.datetime(2026, 8, 27, 0, 0),
            Ta_value=22.0,
            CF_value=1.0,
            peso_kg=70.0,
            Ta_range=(20.0, 24.0),
            CF_range=(1.0, 1.0),
            Ta_step=4.0,
            solver=solver,
            mostra_tabella=True,
        )

        self.assertEqual(result.ore_min, 10.0)
        self.assertEqual(result.ore_max, 20.0)
        self.assertEqual(result.qd_min, 0.25)
        self.assertEqual(result.qd_max, 0.40)
        self.assertIsNotNone(result.df_combinazioni)
        self.assertEqual(len(result.df_combinazioni), 2)
        self.assertEqual(set(result.df_combinazioni["ore_min"]), {5.0, 10.0})
        self.assertEqual(set(result.df_combinazioni["ore_max"]), {20.0, 50.0})

    def test_prudent_all_outside_leaves_operational_henssge_empty(self):
        def solver(*, Ta, CF, peso_kg, **kwargs):
            return 5.0, 50.0, 0.20

        result = compute_raffreddamento_cautelativo(
            dt_ispezione=datetime.datetime(2026, 8, 27, 0, 0),
            Ta_value=22.0,
            CF_value=1.0,
            peso_kg=70.0,
            Ta_range=(20.0, 24.0),
            CF_range=(1.0, 1.0),
            Ta_step=4.0,
            solver=solver,
            mostra_tabella=True,
        )

        self.assertEqual(result.ore_min, INF_HOURS)
        self.assertEqual(result.ore_max, INF_HOURS)
        self.assertIsNone(result.dt_min)
        self.assertIsNone(result.dt_max)
        self.assertIsNotNone(result.df_combinazioni)
        self.assertEqual(len(result.df_combinazioni), 2)

    def test_twenty_percent_rule_remains_limited_to_qd_at_most_point_two(self):
        Ta = 20.0
        T0 = 37.2
        W = 70.0
        CF = 1.0

        Tr_020 = Ta + 0.20 * (T0 - Ta)
        _, t_min_020, t_max_020, t_med_raw_020, qd_020 = calcola_raffreddamento(
            Tr_020, Ta, T0, W, CF, round_minutes=30
        )
        self.assertEqual(qd_020, 0.2)
        self.assertEqual(
            t_min_020,
            round_to_step_minutes(max(0.0, t_med_raw_020 * 0.80), 30),
        )
        self.assertEqual(
            t_max_020,
            round_to_step_minutes(t_med_raw_020 * 1.20, 30),
        )

        Tr_021 = Ta + 0.21 * (T0 - Ta)
        _, t_min_021, t_max_021, t_med_raw_021, qd_021 = calcola_raffreddamento(
            Tr_021, Ta, T0, W, CF, round_minutes=30
        )
        self.assertAlmostEqual(qd_021, 0.21, places=12)
        self.assertEqual(
            t_min_021,
            round_to_step_minutes(max(0.0, t_med_raw_021 - 4.5), 30),
        )
        self.assertEqual(
            t_max_021,
            round_to_step_minutes(t_med_raw_021 + 4.5, 30),
        )


if __name__ == "__main__":
    unittest.main()
