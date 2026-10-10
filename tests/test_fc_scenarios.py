from copy import deepcopy
import unittest

from app import i18n
from app.fc_page import _current_fc_draft, FULL_PAGE, MSIL_PAGE
from app.fc_selection import apply_choice, refresh_fc_for_weight, fc_weight_warning, validate_choice
from app.fc_scenarios import (matching_scenario_description, summarize_scenarios,
                             matching_temperature_scenarios, manual_fc_note)


def scenario_payload():
    scenarios = []
    for bounds, description in [([1.35, 1.35], "corpo asciutto, aria ferma"),
                                ([1.4, 1.4], "corpo bagnato, aria in movimento")]:
        scenarios.append({"range": bounds, "base_range": bounds[:], "weight": 70.,
                          "manual": True, "manual_weight_adjusted": False,
                          "description": description,
                          "draft": {"lo": str(bounds[0]), "hi": str(bounds[1]),
                                    "weight": 70., "manual": True, "manualBase": bounds[:]}})
    bounds, description = summarize_scenarios(scenarios)
    return {"range": bounds, "weight": 70., "manual": False,
            "rule": "multiple-scenarios", "base_range": None,
            "description": description, "scenarios": scenarios,
            "draft": {"multiple": True, "activeScenario": 1}}


def temperature_payload():
    payload = scenario_payload()
    for item, temperature in zip(payload["scenarios"], (20., 8.)):
        item["temperature"] = temperature
        item["draft"]["temperature"] = str(temperature)
    payload["scenarios"][1]["conditions"] = {"state": "Immerso"}
    return payload


class FCScenarioTests(unittest.TestCase):
    def test_temperatures_transfer_and_preserve_pairing_after_weight_change(self):
        state = {}
        apply_choice(state, temperature_payload())
        self.assertEqual((state["Ta_min_beta"], state["Ta_max_beta"]), (8., 20.))
        self.assertEqual((state["ta_base_val"], state["ta_other_val"]), (8., 20.))
        self.assertNotIn("°C", state["__fc_applied_choice"]["description"])
        self.assertEqual(matching_temperature_scenarios(state, [1.35, 1.4], 70., (8., 20.)),
                         [(20., [1.35, 1.35]), (8., [1.4, 1.4])])
        state["peso"] = 100.
        self.assertTrue(refresh_fc_for_weight(state))
        self.assertEqual(matching_temperature_scenarios(state, [1.3, 1.35], 100., (8., 20.)),
                         [(20., [1.35, 1.35]), (8., [1.3, 1.3])])
        state["ta_base_val"] = 6.  # Weight changes must not overwrite a home edit.
        state["peso"] = 70.
        self.assertTrue(refresh_fc_for_weight(state))
        self.assertEqual(state["ta_base_val"], 6.)

    def test_incomplete_temperature_group_is_rejected_without_partial_updates(self):
        for bad in (None, float("nan"), float("inf"), ""):
            payload = temperature_payload()
            payload["scenarios"][1]["temperature"] = bad
            state = {"peso": 70.}
            with self.assertRaises(ValueError):
                apply_choice(state, payload)
            self.assertEqual(state, {"peso": 70.})
        payload = temperature_payload()
        del payload["scenarios"][1]["temperature"]
        with self.assertRaises(ValueError):
            validate_choice(payload)

    def test_manual_provenance_moves_out_of_condition_summary(self):
        payload = temperature_payload()
        payload["scenarios"][0]["description"] += ", FC impostato manualmente"
        state = {}
        apply_choice(state, payload)
        self.assertNotIn("manualmente", state["__fc_applied_choice"]["description"])
        self.assertEqual(manual_fc_note(state, payload["range"], 70.),
                         "FC impostato manualmente negli scenari 1, 2.")
        self.assertIsNone(manual_fc_note(state, [1., 1.], 70.))

    def test_cooling_uses_only_paired_temperatures_and_blocks_stale_home_values(self):
        import datetime
        from unittest.mock import patch
        from app.graphing_cooling import compute_cooling_state
        from app.cautelativa import compute_raffreddamento_cautelativo
        state = {}
        apply_choice(state, temperature_payload())
        args = dict(input_rt=30., input_ta=8., input_tm=37.2, input_w=70.,
                    fattore_correzione=1.35, data_ora_ispezione=datetime.datetime(2026, 10, 10, 9),
                    skip_warnings=False, cooling_options=state)
        with patch('app.graphing_cooling.compute_raffreddamento_cautelativo',
                   wraps=compute_raffreddamento_cautelativo) as solver:
            cooling = compute_cooling_state(**args)
            self.assertTrue(cooling.raffreddamento_calcolabile)
            self.assertEqual(solver.call_args.kwargs["temperature_scenarios"],
                             [(20., [1.35, 1.35]), (8., [1.4, 1.4])])
            self.assertEqual(sum(dict(cooling.qd_status_counts).values()), 2)
            details = "".join(cooling.detail_blocks)
            self.assertIn("Temperature degli scenari: scenario 1: ambiente 20 °C; scenario 2: acqua 8 °C", details)
            self.assertIn("1.35 (corpo asciutto)", details)
            self.assertNotIn("corpo asciutto, ambiente", details)
            state["Ta_min_beta"] = 9.
            solver.reset_mock()
            cooling = compute_cooling_state(**args)
            solver.assert_not_called()
            self.assertFalse(cooling.raffreddamento_calcolabile)
            self.assertIn("Temperature modificate", cooling.validation_error)

    def test_exact_extremes_and_conditions(self):
        payload = scenario_payload()
        state = {}
        apply_choice(state, payload)
        self.assertEqual(state["fc_suggested_vals"], [1.35, 1.4])
        self.assertEqual(state["__fc_applied_choice"]["description"],
                         "FC degli scenari considerati: 1.35 (corpo asciutto)"
                         " — 1.40 (corpo bagnato, aria in movimento)")

    def test_saved_condition_descriptions_use_compact_wording(self):
        payload = temperature_payload()
        payload["scenarios"][0]["description"] = "corpo asciutto, aria ferma, su pavimento interno"
        payload["scenarios"][1]["description"] = "corpo immerso in acqua stagnante, prossima a 0 °C"
        state = {}
        apply_choice(state, payload)
        self.assertEqual(state["__fc_applied_choice"]["description"],
                         "FC degli scenari considerati: 1.35 (corpo asciutto, adagiato su pavimento)"
                         " — 1.40 (corpo immerso in acqua stagnante)")

    def test_weight_can_exchange_the_scenarios_defining_the_extremes(self):
        state = {}
        apply_choice(state, scenario_payload())
        for weight, expected in [(100., [1.3, 1.35]), (70., [1.35, 1.4])]:
            state["peso"] = weight
            self.assertTrue(refresh_fc_for_weight(state))
            choice = state["__fc_applied_choice"]
            self.assertEqual(choice["range"], expected)
            self.assertEqual([item["base_range"] for item in choice["scenarios"]], [[1.35, 1.35], [1.4, 1.4]])
            first_condition = "corpo bagnato" if weight == 100 else "corpo asciutto"
            self.assertIn(f"{expected[0]:.2f} ({first_condition}", choice["description"])
            self.assertEqual(fc_weight_warning(state), "FC adattato per il peso.")
        state["peso"] = 75.
        self.assertTrue(refresh_fc_for_weight(state))
        self.assertIsNone(fc_weight_warning(state))

    def test_disjoint_scenarios_do_not_fill_the_weight_threshold_gap(self):
        payload = scenario_payload()
        payload["scenarios"][1].update(range=[2., 2.], base_range=[2., 2.])
        payload["range"], _ = summarize_scenarios(payload["scenarios"])
        state = {}
        apply_choice(state, payload)
        state["peso"] = 100.
        self.assertTrue(refresh_fc_for_weight(state))
        self.assertEqual(state["fc_suggested_vals"], [1.35, 1.75])

    def test_reopening_keeps_active_scenario_distinct_from_overall_bounds(self):
        for msil, home in [(False, FULL_PAGE), (True, MSIL_PAGE)]:
            with self.subTest(msil=msil):
                state = {}
                apply_choice(state, scenario_payload(), msil=msil)
                state["peso"] = 100.
                refresh_fc_for_weight(state, msil=msil)
                draft = _current_fc_draft(state, home)
                self.assertTrue(draft["multiple"])
                self.assertEqual(draft["activeScenario"], 1)
                self.assertEqual([draft["lo"], draft["hi"]], ["1.30", "1.30"])
                self.assertEqual(draft["manualBase"], [1.4, 1.4])
                self.assertEqual(len(draft["scenarios"]), 2)

    def test_incomplete_or_inconsistent_group_is_atomic(self):
        for mutation in [lambda p:p.update(range=[1., 2.]),
                         lambda p:p["scenarios"][1].update(weight=100.),
                         lambda p:p["scenarios"][1].update(range=[None, 1.4]),
                         lambda p:p["scenarios"][1].update(description=""),
                         lambda p:p["scenarios"][1].update(scenarios=[]),
                         lambda p:p.update(scenarios=[]),
                         lambda p:p.update(manual=True)]:
            payload = scenario_payload()
            mutation(payload)
            state = {"peso": 70.}
            with self.assertRaises((TypeError, ValueError)):
                apply_choice(state, payload)
            self.assertEqual(state, {"peso": 70.})

    def test_invalid_adaptation_keeps_all_previous_scenarios(self):
        state = {}
        apply_choice(state, scenario_payload())
        state["__fc_applied_choice"]["scenarios"][1]["base_range"] = None
        previous = deepcopy(state["__fc_applied_choice"])
        state["peso"] = 100.
        self.assertFalse(refresh_fc_for_weight(state))
        self.assertEqual(state["__fc_applied_choice"], previous)
        self.assertEqual(fc_weight_warning(state), "Peso modificato: ricontrollare il FC.")

    def test_equal_fc_retains_multiple_conditions_and_range_output_mode(self):
        payload = scenario_payload()
        payload["scenarios"][1]["range"] = [1.35, 1.35]
        payload["range"], _ = summarize_scenarios(payload["scenarios"])
        state = {}
        apply_choice(state, payload)
        self.assertTrue(state["stima_cautelativa_beta"])
        text = state["__fc_applied_choice"]["description"]
        self.assertIn("corpo asciutto / corpo bagnato, aria in movimento", text)

    def test_report_conditions_are_escaped_and_only_match_the_applied_calculation(self):
        state = {}
        payload = scenario_payload()
        payload["scenarios"][0]["description"] = '<script>alert("test")</script>'
        apply_choice(state, payload)
        text = matching_scenario_description(state, [1.35, 1.4], 70.)
        html = i18n.prudent_graphing_detail_list(header="Riepilogo", ta_text="20 °C",
            cf_text="1.35–1.40", weight_text="70 kg", scenario_description=text)
        self.assertIn("FC degli scenari considerati:", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertNotIn("Range per il fattore", html)
        self.assertIsNone(matching_scenario_description(state, [1., 1.4], 70.))
        self.assertIsNone(matching_scenario_description(state, [1.35, 1.4], 100.))

    def test_actual_cooling_output_includes_conditions_without_changing_results(self):
        import datetime
        from app.graphing_cooling import compute_cooling_state
        state = {"ta_base_val": 20.}
        apply_choice(state, scenario_payload())
        args = dict(input_rt=30., input_ta=20., input_tm=37.2, input_w=70.,
                    fattore_correzione=1.35, data_ora_ispezione=datetime.datetime(2026, 10, 10, 9),
                    skip_warnings=False)
        with_scenarios = compute_cooling_state(**args, cooling_options=state)
        state.pop("__fc_applied_choice")
        without_scenarios = compute_cooling_state(**args, cooling_options=state)
        for field in ("t_min_raff_henssge", "t_max_raff_henssge", "Qd_min", "Qd_max"):
            self.assertEqual(getattr(with_scenarios, field), getattr(without_scenarios, field))
        self.assertIn("FC degli scenari considerati: 1.35 (corpo asciutto)", "".join(with_scenarios.detail_blocks))
        self.assertIn("1.40 (corpo bagnato, aria in movimento)", "".join(with_scenarios.detail_blocks))
        self.assertNotIn("FC degli scenari", "".join(without_scenarios.detail_blocks))


if __name__ == "__main__":
    unittest.main()
