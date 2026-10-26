"""Research checks: published numerical replay, scope, and app isolation."""
from dataclasses import replace
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

from research.fc_two_phase.compare import compare, published_grid, source_rows
from research.fc_two_phase.model import Inputs, late_phase_elapsed, reconstruct, single_phase_hours
from research.fc_two_phase.reference import cooling_coefficient


class TwoPhasePrototypeTests(unittest.TestCase):
    def setUp(self):
        self.example = Inputs(17.2, 12.4, 65, 1, .75, 6)

    def test_replays_every_printed_second_phase_time(self):
        rows = source_rows()
        self.assertEqual(len(rows), 19)
        for row in rows:
            with self.subTest(time=row["hours_since_death"]):
                raw = late_phase_elapsed(row["rectal_c"], 20.3, 12.4, -.0845)
                self.assertAlmostEqual(published_grid(raw), row["published_phase2_hours"], places=9)

    def test_published_coefficient_from_weight_and_fc(self):
        self.assertAlmostEqual(cooling_coefficient(65, .75), -.0845, places=4)

    def test_measured_transition_replay_is_distinct_from_unknown_transition(self):
        replay = late_phase_elapsed(17.2, 20.3, 12.4, -.0845)
        self.assertAlmostEqual(replay, 5.8964123261, places=7)
        result = reconstruct(self.example)
        self.assertEqual(result.status, "experimental_two_phase")
        self.assertAlmostEqual(result.transition_c, 20.3699573388, places=8)
        self.assertAlmostEqual(result.total_hours, 26.5891109231, places=7)
        self.assertFalse(result.clinically_validated)

    def test_zero_duration_matches_app_exactly(self):
        case = replace(self.example, after_hours=0)
        result = reconstruct(case)
        self.assertEqual(result.status, "single_phase_reference")
        self.assertEqual(result.total_hours, single_phase_hours(case.rectal_c, case, case.fc_before))

    def test_identical_phases_merge_exactly_for_different_weights(self):
        for weight, fc in [(50, .75), (65, 1), (90, 1.5), (100, 2)]:
            with self.subTest(weight=weight, fc=fc):
                case = Inputs(25, 15, weight, fc, fc, 1)
                self.assertEqual(reconstruct(case).total_hours, single_phase_hours(25, case, fc))

    def test_known_duration_cannot_predate_death_in_merged_phases(self):
        result = reconstruct(Inputs(36, 15, 70, 1, 1, 20))
        self.assertEqual(result.status, "incompatible_duration")
        self.assertIsNone(result.total_hours)

    def test_early_transition_withholds_pmi(self):
        result = reconstruct(Inputs(35, 15, 70, 1, .75, .2))
        self.assertEqual(result.status, "early_phase_requires_review")
        self.assertGreater(result.fast_term_fraction, .01)
        self.assertIsNone(result.total_hours)
        self.assertIsNone(result.before_hours)

    def test_diagnostic_gate_is_explicit_and_does_not_validate(self):
        result = reconstruct(self.example, max_fast_term_fraction=.0001)
        self.assertEqual(result.status, "early_phase_requires_review")
        self.assertEqual(result.fast_term_gate, .0001)
        self.assertFalse(result.clinically_validated)

    def test_reconstruction_above_initial_temperature_is_rejected(self):
        result = reconstruct(replace(self.example, after_hours=100))
        self.assertEqual(result.status, "incompatible_duration")
        self.assertIsNone(result.total_hours)

    def test_close_to_ambient_or_hot_ambient_is_outside_scope(self):
        for case, status in [(replace(self.example, rectal_c=14.2), "near_ambient"),
                             (Inputs(30, 24, 70, 1, .75, 1), "outside_temperature_scope"),
                             (replace(self.example, ambient_c=-1), "outside_temperature_scope")]:
            with self.subTest(status=status):
                result = reconstruct(case)
                self.assertEqual(result.status, status)
                self.assertIsNone(result.total_hours)

    def test_invalid_numeric_inputs_are_not_silently_accepted(self):
        for field, value in [("weight_kg", 0), ("fc_after", -1), ("fc_before", 10),
                             ("after_hours", -1), ("after_hours", float("inf")),
                             ("rectal_c", float("nan")), ("fc_before", True)]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                reconstruct(replace(self.example, **{field: value}))

    def test_impossible_temperatures_and_horizon_return_no_number(self):
        for case, status in [(replace(self.example, rectal_c=40), "incompatible_temperatures"),
                             (replace(self.example, rectal_c=12.4), "incompatible_temperatures"),
                             (replace(self.example, after_hours=161), "outside_time_horizon")]:
            with self.subTest(status=status):
                result = reconstruct(case)
                self.assertEqual(result.status, status)
                self.assertIsNone(result.total_hours)

    def test_paper_replay_rejects_invalid_domains(self):
        for args in [(12, 20.3, 12.4, -.0845), (21, 20.3, 12.4, -.0845),
                     (17.2, 20.3, 12.4, 0), (float("nan"), 20.3, 12.4, -.0845)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                late_phase_elapsed(*args)

    def test_late_synthetic_round_trip_is_numerical_not_clinical_validation(self):
        for weight, before_fc, after_fc, before_h, after_h in [(65, 1, .75, 22, 6),
                                                              (90, 1.5, 1, 50, 4),
                                                              (65, .75, 1.2, 20, 5)]:
            b1 = cooling_coefficient(weight, before_fc)
            b2 = cooling_coefficient(weight, after_fc)
            change = 12.4 + (37.2-12.4)*(1.25*math.exp(b1*before_h)-.25*math.exp(5*b1*before_h))
            measured = 12.4 + (change-12.4)*math.exp(b2*after_h)
            case = Inputs(measured, 12.4, weight, before_fc, after_fc, after_h)
            result = reconstruct(case)
            with self.subTest(case=case):
                self.assertEqual(result.status, "experimental_two_phase")
                self.assertAlmostEqual(result.total_hours, before_h+after_h, places=7)
                self.assertFalse(result.clinically_validated)

    def test_comparison_does_not_treat_repeated_measures_as_independent_bodies(self):
        rows, summary = compare()
        self.assertEqual(summary["independent_bodies"], 1)
        self.assertEqual(summary["reproduced_printed_rows"], 19)
        self.assertEqual(summary["comparison"]["two_phase_extension"]["n_measurements"], 16)
        self.assertEqual(len(summary["suppressed_rows"]), 2)
        # This case does not establish uniformly better accuracy: preserve that finding.
        self.assertGreater(summary["comparison"]["two_phase_extension"]["mean_absolute_error_hours"],
                           summary["comparison"]["constant_fc_before"]["mean_absolute_error_hours"])
        self.assertTrue(all(r["reconstruction_error_hours"] < 0 for r in rows if r["reconstruction_error_hours"] is not None))

    def test_fresh_import_does_not_load_streamlit_or_app_package(self):
        code = ("import sys,json; import research.fc_two_phase.model; "
                "print(json.dumps({'app': 'app' in sys.modules, 'streamlit': 'streamlit' in sys.modules}))")
        run = subprocess.run([sys.executable, "-c", code], cwd=Path(__file__).resolve().parents[1],
                             text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(run.stdout), {"app": False, "streamlit": False})
        self.assertEqual(run.stderr, "")

    def test_command_line_emits_only_json_and_rejected_case_has_no_estimate(self):
        run = subprocess.run([sys.executable, "-m", "research.fc_two_phase.model", "--rectal", "35",
                              "--ambient", "15", "--weight", "70", "--fc-before", "1",
                              "--fc-after", ".75", "--hours-after-change", ".2"],
                             cwd=Path(__file__).resolve().parents[1], text=True, capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)["status"], "early_phase_requires_review")
        self.assertEqual(run.stderr, "")


if __name__ == "__main__":
    unittest.main()
