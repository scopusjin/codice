"""Regression checks for the second audit batch: domains, clocks and FC edits."""
import datetime as dt
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.cautelativa import compute_raffreddamento_cautelativo
from app.fc_selection import apply_choice, normalize_fc_input, fc_weight_needs_review
from app.graphing_cooling import compute_cooling_state, _potente_limit_for_combination
from app.henssge import calcola_raffreddamento, cooling_coefficient, round_to_step_minutes


class AuditNumericRegressionTests(unittest.TestCase):
    def cooling(self, options=None, **values):
        inputs = dict(input_rt=30., input_ta=20., input_tm=37.2, input_w=70.,
                      fattore_correzione=1., data_ora_ispezione=dt.datetime(2026, 1, 2, 12, 7),
                      skip_warnings=True, cooling_options=options or {})
        inputs.update(values)
        with patch('app.graphing_cooling.st', SimpleNamespace(session_state={})):
            return compute_cooling_state(**inputs)

    def test_fc_above_three_remains_calculable_in_decreasing_domain(self):
        times = [calcola_raffreddamento(30, 20, 37.2, 70, fc)[3] for fc in (2, 3, 4)]
        self.assertTrue(all(math.isfinite(t) for t in times))
        self.assertLess(times[0], times[1])
        self.assertLess(times[1], times[2])
        self.assertIsNone(self.cooling(fattore_correzione=4.).validation_error)

    def test_non_decreasing_branch_cannot_produce_a_death_time(self):
        for weight, fc in [(70., 10.), (150., 3.), (1e300, 1e300), (1e-300, 1e-300)]:
            with self.subTest(weight=weight, fc=fc):
                with self.assertRaises(ValueError):
                    cooling_coefficient(weight, fc)
                self.assertTrue(all(math.isnan(v) for v in
                    calcola_raffreddamento(30, 20, 37.2, weight, fc)))
                self.assertIsNone(_potente_limit_for_combination(20, fc, weight))
                self.assertTrue(self.cooling(input_w=weight, fattore_correzione=fc).validation_error)

    def test_range_is_rejected_if_only_its_upper_end_is_invalid(self):
        options = dict(stima_cautelativa_beta=True, Ta_min_beta=20., Ta_max_beta=20.,
                       FC_min_beta=2., FC_max_beta=3.)
        result = self.cooling(options, input_w=150.)
        self.assertTrue(result.validation_error)
        self.assertTrue(math.isnan(result.t_min_raff_henssge))
        with self.assertRaises(ValueError):
            compute_raffreddamento_cautelativo(dt_ispezione=dt.datetime(2026, 1, 1),
                Ta_value=20, CF_value=2.5, peso_kg=150, Ta_range=(20, 20), CF_range=(2, 3))

    def test_domain_check_includes_estimated_weight_upper_bound(self):
        options = dict(stima_cautelativa_beta=True, Ta_min_beta=20., Ta_max_beta=20.,
                       FC_min_beta=3., FC_max_beta=3., peso_stimato_beta=False)
        self.assertIsNone(self.cooling(options, input_w=147.).validation_error)
        self.assertTrue(self.cooling({**options, 'peso_stimato_beta': True},
                                    input_w=147.).validation_error)

    def test_durations_and_dates_use_one_rounding_at_each_selected_precision(self):
        inspection = dt.datetime(2026, 1, 2, 12, 7)
        for step in (6, 15, 30):
            with self.subTest(step=step):
                expected = calcola_raffreddamento(30, 20, 37.2, 70, 1., round_minutes=step)
                result = compute_raffreddamento_cautelativo(dt_ispezione=inspection,
                    Ta_value=20, CF_value=1, peso_kg=70, Ta_range=(20, 20), CF_range=(1, 1),
                    solver_kwargs=dict(Tr=30, T0=37.2, round_minutes=step))
                self.assertAlmostEqual((inspection - result.dt_min).total_seconds()/3600, expected[2])
                self.assertAlmostEqual((inspection - result.dt_max).total_seconds()/3600, expected[1])
                result2 = self.cooling(dict(stima_cautelativa_beta=True,
                    Ta_min_beta=20., Ta_max_beta=20., FC_min_beta=1., FC_max_beta=1.,
                    henssge_round_minutes=step))
                self.assertEqual(result2.t_med_raff_henssge_rounded,
                                 round_to_step_minutes((expected[1]+expected[2])/2, step))

    def test_manual_fc_rounds_nearest_including_half_step(self):
        for value, expected in [(1.23, 1.25), (1.22, 1.20), (1.325, 1.35), (3.16, 3.15)]:
            state = {'fattore_correzione': value, 'peso': 70}
            normalize_fc_input(state, 'fattore_correzione')
            self.assertEqual(state['fattore_correzione'], expected)
        state = {'fc_min_val': None}
        normalize_fc_input(state, 'fc_min_val')
        self.assertIsNone(state['fc_min_val'])

    def test_weight_change_reminds_without_replacing_manual_choice(self):
        state = {}
        apply_choice(state, {'range': [1.5, 1.8], 'weight': 70})
        state['peso'] = 90
        self.assertTrue(fc_weight_needs_review(state))
        self.assertEqual((state['FC_min_beta'], state['FC_max_beta']), (1.5, 1.8))
        state['peso'] = 70
        self.assertFalse(fc_weight_needs_review(state))
        state['peso'] = 90
        normalize_fc_input(state, 'fc_min_val')
        self.assertFalse(fc_weight_needs_review(state))
        state['peso'] = 95
        self.assertTrue(fc_weight_needs_review(state))
        apply_choice(state, {'range': [1.4, 1.6], 'weight': 95})
        self.assertFalse(fc_weight_needs_review(state))
