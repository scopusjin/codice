import json
import subprocess
import unittest
from copy import deepcopy
from pathlib import Path

from app.fc_selection import (
    apply_choice, fc_weight_needs_review, fc_weight_warning, normalize_fc_input, refresh_fc_for_weight,
)
from app.fc_weight import adapt_fc_range

ROOT = Path(__file__).resolve().parents[1]


class FCWeightTests(unittest.TestCase):
    def automatic_choice(self, base=(2.8, 3.1), weight=70):
        return {"range": adapt_fc_range(base, weight), "base_range": list(base),
                "weight": weight, "manual": False, "description": "condizioni conservate"}

    def test_same_outputs_as_existing_panel_formula(self):
        # Execute the actual panel functions, including the discontinuity and
        # rounding. This prevents the server and browser paths drifting apart.
        result = subprocess.run(['node', '-e', r'''
const {api}=require('./tests/fc_panel_harness.cjs');
const ranges=[[1.3,1.4],[1.35,1.6],[1.4,3.1],[0.75,1.8],[2.8,3.1]];
for(let n=7;n<=200;n++)ranges.push([n/20,n/20]);
const weights=[4,10,20,40,59.9,59.99,60,70,80,80.01,80.1,90,100,110,150];
console.log(JSON.stringify(ranges.flatMap(base=>weights.map(weight=>({
    base,weight,expected:api.roundRange(api.bounds(...base,weight))
})))));
'''], cwd=ROOT, text=True, capture_output=True, check=True, timeout=30)
        for case in json.loads(result.stdout):
            with self.subTest(base=case['base'], weight=case['weight']):
                self.assertEqual(adapt_fc_range(case['base'], case['weight']), case['expected'])

    def test_repeated_weight_changes_always_use_original_bounds(self):
        state = {"ta_base_val": 18., "ta_other_val": 22., "stima_cautelativa_beta": True}
        apply_choice(state, self.automatic_choice())
        for weight, expected in [(100, [2.3, 2.45]), (70, [2.8, 3.1]), (100, [2.3, 2.45])]:
            state['peso'] = weight
            state['show_results'] = state['run_stima_mobile'] = True
            self.assertTrue(refresh_fc_for_weight(state))
            self.assertEqual([state['FC_min_beta'], state['FC_max_beta']], expected)
            self.assertEqual(state['__msil_fc_chosen_range'], expected)
            self.assertEqual(state['__fc_applied_choice']['base_range'], [2.8, 3.1])
            self.assertEqual(state['fattori_condizioni_testo'], 'condizioni conservate')
            self.assertEqual((state['ta_base_val'], state['ta_other_val']), (18., 22.))
            self.assertFalse(fc_weight_needs_review(state))
            self.assertFalse(state['show_results'])
            self.assertFalse(state['run_stima_mobile'])
            unchanged = deepcopy(state)
            self.assertFalse(refresh_fc_for_weight(state))
            self.assertEqual(state, unchanged)

    def test_first_choice_at_nonstandard_weight_keeps_unadapted_base(self):
        state = {}
        apply_choice(state, self.automatic_choice(weight=100))
        state['peso'] = 70
        self.assertTrue(refresh_fc_for_weight(state))
        self.assertEqual(state['fc_suggested_vals'], [2.8, 3.1])

    def test_incomplete_manual_edits_disable_refresh(self):
        for key in ('fattore_correzione', 'fc_min_val', 'fc_other_val'):
            for value in (None, float('nan'), 0):
                with self.subTest(key=key, value=value):
                    state = {}
                    apply_choice(state, self.automatic_choice())
                    state[key] = value
                    normalize_fc_input(state, key)
                    state['peso'] = 100
                    unchanged = deepcopy(state)
                    self.assertFalse(refresh_fc_for_weight(state))
                    self.assertEqual(state, unchanged)
                    self.assertTrue(fc_weight_needs_review(state))

    def test_legacy_and_inconsistent_choices_are_not_reinterpreted(self):
        choices = [
            {**self.automatic_choice(), 'manual': True},
            {'range': [2.8, 3.1], 'weight': 70},
            {**self.automatic_choice(), 'base_range': None},
            {**self.automatic_choice(), 'base_range': [1.2, 1.3]},
        ]
        for choice in choices:
            state = {}
            apply_choice(state, choice)
            state['peso'] = 100
            unchanged = deepcopy(state)
            self.assertFalse(refresh_fc_for_weight(state))
            self.assertEqual(state, unchanged)

    def test_direct_manual_point_changes_only_when_required_and_keeps_its_base(self):
        state = {'peso': 70, 'fattore_correzione': 2.0}
        normalize_fc_input(state, 'fattore_correzione')
        self.assertIsNone(fc_weight_warning(state))
        state['peso'] = 75
        self.assertTrue(refresh_fc_for_weight(state))
        self.assertEqual(state['fattore_correzione'], 2.)
        self.assertIsNone(fc_weight_warning(state))
        for weight in (100, 110, 70, 100):
            state['peso'] = weight
            self.assertTrue(refresh_fc_for_weight(state))
            self.assertEqual(state['fc_suggested_vals'], adapt_fc_range([2., 2.], weight))
            self.assertEqual(state['__fc_applied_choice']['base_range'], [2., 2.])
            self.assertIn('FC adattato per il peso', fc_weight_warning(state))
            self.assertFalse(refresh_fc_for_weight(state))

    def test_reentering_manual_fc_resets_base_and_notice(self):
        state = {'peso': 70, 'fattore_correzione': 2.0}
        normalize_fc_input(state, 'fattore_correzione')
        state['peso'] = 100
        refresh_fc_for_weight(state)
        state['fattore_correzione'] = 2.5
        normalize_fc_input(state, 'fattore_correzione')
        self.assertIsNone(fc_weight_warning(state))
        self.assertEqual(state['fattore_correzione'], 2.5)
        state['peso'] = 110
        self.assertTrue(refresh_fc_for_weight(state))
        self.assertEqual(state['fc_suggested_vals'], adapt_fc_range([2.5, 2.5], 110))

    def test_manual_range_edit_replaces_the_helper_base(self):
        for key, value, base in (('fc_min_val', 2.5, [2.5, 3.1]),
                                 ('fc_other_val', 3.5, [2.8, 3.5])):
            state = {}
            apply_choice(state, self.automatic_choice())
            state[key] = value
            normalize_fc_input(state, key)
            state['peso'] = 100
            self.assertTrue(refresh_fc_for_weight(state))
            self.assertEqual(state['fc_suggested_vals'], adapt_fc_range(base, 100))
            self.assertIn('FC adattato per il peso', fc_weight_warning(state))

    def test_manual_panel_choice_and_nonstandard_initial_weight(self):
        for weight in (70, 100):
            state = {}
            apply_choice(state, {'range': [2., 2.], 'weight': weight, 'manual': True})
            self.assertEqual(state['fattore_correzione'], 2.)
            state['peso'] = 110
            self.assertTrue(refresh_fc_for_weight(state))
            self.assertEqual(state['fc_suggested_vals'], adapt_fc_range([2., 2.], 110))

    def test_fc_below_threshold_does_not_show_an_adjustment_notice(self):
        state = {'peso': 70, 'fattore_correzione': 1.3}
        normalize_fc_input(state, 'fattore_correzione')
        state['peso'] = 100
        self.assertTrue(refresh_fc_for_weight(state))
        self.assertEqual(state['fattore_correzione'], 1.3)
        self.assertIsNone(fc_weight_warning(state))

    def test_notice_describes_only_an_actual_change_at_the_latest_weight(self):
        for manual in (False, True):
            state = {}
            choice = self.automatic_choice(base=[2., 2.])
            if manual:
                choice.update(manual=True, manual_weight_adjusted=False)
            apply_choice(state, choice)
            for weight, notice in ((100., True), (70., True), (75., False)):
                state['peso'] = weight
                self.assertTrue(refresh_fc_for_weight(state))
                self.assertEqual(fc_weight_warning(state), 'FC adattato per il peso.' if notice else None)

    def test_manual_fc_entered_before_weight_is_retained_until_weight_is_valid(self):
        state = {'peso': None, 'fattore_correzione': 2.}
        normalize_fc_input(state, 'fattore_correzione', msil=True)
        for weight in (None, 0., 200.):
            state['peso'] = weight
            self.assertFalse(refresh_fc_for_weight(state, msil=True))
            self.assertEqual(state['fattore_correzione'], 2.)
        state['peso'] = 100.
        self.assertTrue(refresh_fc_for_weight(state, msil=True))
        self.assertEqual(state['fattore_correzione'], 1.75)
        self.assertNotIn('__msil_fc_chosen_range', state)
        self.assertIn('FC adattato per il peso', fc_weight_warning(state))

    def test_invalid_weight_preserves_the_last_valid_choice(self):
        state = {}
        apply_choice(state, self.automatic_choice())
        for weight in (None, 'invalid', 3.9, 150.1, float('inf')):
            state['peso'] = weight
            unchanged = deepcopy(state)
            self.assertFalse(refresh_fc_for_weight(state))
            self.assertEqual(state, unchanged)
        state['peso'] = 100
        self.assertTrue(refresh_fc_for_weight(state))

    def test_point_and_threshold_crossing_ranges(self):
        for base, expected in [([1.4, 1.4], [1.3, 1.3]), ([1.35, 1.4], [1.3, 1.4]),
                               ([1.2, 1.3], [1.2, 1.3])]:
            state = {}
            apply_choice(state, self.automatic_choice(base))
            state['peso'] = 100
            self.assertTrue(refresh_fc_for_weight(state))
            self.assertEqual(state['fc_suggested_vals'], expected)
