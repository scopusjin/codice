import json
import subprocess
import unittest
from copy import deepcopy
from pathlib import Path

from app.fc_selection import (
    apply_choice, fc_weight_needs_review, normalize_fc_input, refresh_fc_for_weight,
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

    def test_manual_edits_including_clearing_a_field_disable_refresh(self):
        for key in ('fattore_correzione', 'fc_min_val', 'fc_other_val'):
            for value in (1.75, None):
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

    def test_manual_legacy_and_inconsistent_choices_are_not_reinterpreted(self):
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

