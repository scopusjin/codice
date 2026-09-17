import unittest

from app.fc_selection import apply_choice, rounded_fc, validate_choice


class FCSelectionTests(unittest.TestCase):
    def test_exact_range_replaces_old_suggestions_and_keeps_temperature(self):
        state = {"peso": 70, "stima_cautelativa_beta": True,
                 "ta_base_val": 17.5, "ta_other_val": 21.0,
                 "fc_suggested_vals": [0.5, 3.0], "FC_min_beta": 0.5, "FC_max_beta": 3.0}
        apply_choice(state, {"range": [1.25, 1.45], "weight": 91.0})
        self.assertEqual((state["FC_min_beta"], state["FC_max_beta"]), (1.25, 1.45))
        self.assertEqual(state["fc_suggested_vals"], [1.25, 1.45])
        self.assertEqual((state["ta_base_val"], state["ta_other_val"]), (17.5, 21.0))
        self.assertEqual(state["peso"], 91)

    def test_range_from_single_mode_sets_equal_ambient_bounds(self):
        state = {"stima_cautelativa_beta": False, "ta_base_val": 19.5}
        apply_choice(state, {"range": [1.2, 1.3], "weight": 70})
        self.assertTrue(state["stima_cautelativa_beta"])
        self.assertEqual(state["Ta_min_beta"], 19.5)
        self.assertEqual(state["Ta_max_beta"], 19.5)

    def test_point_and_values_above_three(self):
        state = {}
        apply_choice(state, {"range": [3.15, 3.15], "weight": 40})
        self.assertEqual(state["fattore_correzione"], 3.15)
        self.assertFalse(state["stima_cautelativa_beta"])

    def test_msil_keeps_selected_bounds(self):
        state = {}
        apply_choice(state, {"range": [0.6, 0.75], "weight": 70}, msil=True)
        self.assertEqual(state["__msil_fc_chosen_range"], [0.6, 0.75])

    def test_invalid_values_do_not_change_state(self):
        for values, weight in [([1.5, 1.2], 70), ([float("nan"), 1], 70),
                               ([1, float("inf")], 70), ([0.3, 1], 70),
                               ([1.23, 1.3], 70), ([1, 1], 151)]:
            state = {"peso": 70}
            with self.assertRaises(ValueError):
                apply_choice(state, {"range": values, "weight": weight})
            self.assertEqual(state, {"peso": 70})
        self.assertEqual(rounded_fc(1.325), 1.35)

