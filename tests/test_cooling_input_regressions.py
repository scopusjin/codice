import datetime
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.cautelativa import compute_raffreddamento_cautelativo
from app.graphing_cooling import compute_cooling_state
from app.henssge import calcola_raffreddamento


class CoolingInputRegressionTests(unittest.TestCase):
    def cooling(self, state, **values):
        inputs = dict(input_rt=30., input_ta=20., input_tm=37.2,
                      input_w=70., fattore_correzione=1.,
                      data_ora_ispezione=datetime.datetime(2026, 1, 1, 12),
                      skip_warnings=True)
        inputs.update(values)
        with patch('app.graphing_cooling.st', SimpleNamespace(session_state=state)):
            return compute_cooling_state(**inputs)

    def test_temperature_range_does_not_depend_on_endpoint_order(self):
        outputs = []
        for first, second in [(20., 35.), (35., 20.)]:
            result = self.cooling(dict(stima_cautelativa_beta=True,
                Ta_min_beta=first, Ta_max_beta=second, FC_min_beta=1., FC_max_beta=1.),
                input_ta=first)
            self.assertFalse(result.gate_fail)
            self.assertTrue(result.raffreddamento_calcolabile)
            outputs.append((result.t_min_raff_henssge, result.t_max_raff_henssge,
                            result.qd_range_status, result.detail_blocks))
        self.assertEqual(outputs[0], outputs[1])

    def test_incomplete_ranges_never_use_old_suggestions(self):
        complete = dict(stima_cautelativa_beta=True, Ta_min_beta=20., Ta_max_beta=20.,
                        FC_min_beta=1.4, FC_max_beta=1.8, fc_suggested_vals=[.9, 1.1])
        for missing in ('FC_min_beta', 'FC_max_beta', 'Ta_min_beta', 'Ta_max_beta'):
            for absent in (False, True):
                with self.subTest(missing=missing, absent=absent):
                    state = dict(complete)
                    if absent:
                        state.pop(missing)
                    else:
                        state[missing] = None
                    result = self.cooling(state)
                    self.assertFalse(result.raffreddamento_calcolabile)
                    self.assertTrue(result.validation_error)
                    self.assertTrue(math.isnan(result.t_min_raff_henssge))

    def test_invalid_fc_and_weight_are_rejected_before_solving(self):
        for key in ('input_w', 'fattore_correzione'):
            for value in (0., -1., math.nan, math.inf):
                with self.subTest(key=key, value=value):
                    result = self.cooling({}, **{key: value})
                    self.assertFalse(result.raffreddamento_calcolabile)
                    self.assertTrue(result.validation_error)

    def test_low_estimated_weight_does_not_generate_zero_or_negative_weights(self):
        state = dict(stima_cautelativa_beta=True, peso_stimato_beta=True,
                     Ta_min_beta=20., Ta_max_beta=20., FC_min_beta=1., FC_max_beta=1.)
        result = self.cooling(state, input_w=2.)
        self.assertFalse(result.raffreddamento_calcolabile)
        self.assertIn('peso', result.validation_error.lower())

    def test_solver_returns_nan_for_invalid_positive_parameters(self):
        for weight, fc in [(0, 1), (70, 0), (-1, 1), (70, -1), (math.inf, 1)]:
            with self.subTest(weight=weight, fc=fc):
                self.assertTrue(all(math.isnan(v) for v in
                    calcola_raffreddamento(30, 20, 37.2, weight, fc)))

    def test_range_solver_rejects_invalid_domains_explicitly(self):
        base = dict(dt_ispezione=datetime.datetime(2026, 1, 1, 12), Ta_value=20.,
                    CF_value=1., peso_kg=70., solver_kwargs={'Tr': 30., 'T0': 37.2})
        for invalid in ({'peso_kg': 2., 'peso_stimato': True},
                        {'CF_range': (0., 1.)}, {'Ta_range': (20., math.inf)},
                        {'CF_value': None}, {'CF_range': (None, 1.)}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                compute_raffreddamento_cautelativo(**{**base, **invalid})
