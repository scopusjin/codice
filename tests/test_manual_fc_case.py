"""Manual FC values must remain exportable without a body-condition selection."""
from copy import deepcopy
import unittest

from app.case_file import CaseFileError, decode_case, encode_case, restored_inputs, snapshot_case
from app.case_report import capture_report
from app.fc_selection import apply_choice
from app.word_launch import word_result


class ManualFCCaseTests(unittest.TestCase):
    def example(self, bounds=(1.0, 1.3), *, nested=False):
        draft = {"state": "", "manual": True, "lo": str(bounds[0]),
                 "hi": str(bounds[1]), "fields": {}, "weight": 75.0}
        if nested:
            draft["scenarios"] = [deepcopy(draft), {"state": "", "fields": {}}]
        state = {"case_code": "X26.117", "peso": 75.0, "rt_val": 34.4,
                 "tm_val": 37.2, "ta_base_val": 14.5}
        apply_choice(state, {"range": list(bounds), "weight": 75.0,
                             "manual": True, "draft": deepcopy(draft)})
        state["__fc_draft"] = deepcopy(draft)
        return state

    def test_manual_single_and_interval_round_trip_with_empty_condition(self):
        for bounds in ((1.0, 1.0), (1.0, 1.3)):
            for nested in (False, True):
                for view in ("full", "msil"):
                    with self.subTest(bounds=bounds, nested=nested, view=view):
                        state = self.example(bounds, nested=nested)
                        case = decode_case(encode_case(snapshot_case(state, view)))
                        restored = restored_inputs(case)
                        self.assertEqual(restored["__fc_applied_choice"], state["__fc_applied_choice"])
                        self.assertEqual(restored["__fc_draft"], state["__fc_draft"])
                        self.assertEqual(restored["peso"], 75.0)

    def test_empty_unapplied_draft_survives_export(self):
        state = {"__fc_active": True, "__fc_draft": {"state": "", "fields": {}}}
        case = decode_case(encode_case(snapshot_case(state, "full")))
        self.assertTrue(case["editor_open"])
        self.assertIsNone(case["fc_choice"])
        self.assertEqual(case["fc_draft"], state["__fc_draft"])

    def test_manual_fc_report_and_word_download_include_current_valuations(self):
        for view, active in (("full", "show_results"), ("msil", "run_stima_mobile")):
            with self.subTest(view=view):
                state = self.example(nested=True)
                blocks = {"conclusion": {"html": "<p>Valutazione corrente.</p>",
                          "text": "Valutazione corrente.", "insert_when": "always"}}
                state.update({active: True, "__desc_dettagliate_html": "<p>Valutazione corrente.</p>",
                              "__word_report_blocks": blocks,
                              "__word_return": {"request_id": "a" * 32, "case_code": "X26.117"}})
                capture_report(state, view)
                raw, filename = word_result(state, view)
                case = decode_case(raw)
                self.assertEqual(filename, "stimaX26.117.json")
                self.assertEqual(case["report"]["word_blocks"], blocks)
                self.assertEqual(case["fc_choice"]["range"], [1.0, 1.3])
                self.assertEqual(case["word_return"]["case_code"], "X26.117")
                state["rt_val"] = 34.5
                self.assertIsNone(word_result(state, view))

    def test_known_conditions_are_preserved(self):
        for condition in ("Asciutto", "Bagnato", "Immerso"):
            state = self.example()
            state["__fc_draft"]["state"] = condition
            case = decode_case(encode_case(snapshot_case(state, "full")))
            self.assertEqual(case["fc_draft"]["state"], condition)

    def test_full_page_manual_fc_reaches_word_download_without_exception(self):
        from pathlib import Path
        from streamlit.testing.v1 import AppTest
        import app.decimal_number_input_v2 as decimal_v2
        decimal_v2._renderer = None
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "Stima_epoca_decesso.py"),
                                default_timeout=30).run()
        for key, value in self.example(nested=True).items():
            app.session_state[key] = value
        app.session_state["selettore_macchie"] = "Fisse"
        app.session_state["selettore_macchie_ui"] = "Fisse"
        app.session_state["__word_return"] = {"request_id": "a" * 32, "case_code": "X26.117"}
        app.run()
        app.button(key="btn_stima").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any(button.proto.label == "Scarica riepilogo per Word"
                            for button in app.get("download_button")))
        raw, filename = word_result(app.session_state._state.filtered_state, "full")
        self.assertEqual(filename, "stimaX26.117.json")
        self.assertTrue(decode_case(raw)["report"]["word_blocks"])

    def test_invalid_condition_values_are_still_rejected(self):
        for value in (None, True, 0, [], {}, "Dry", "non valido", " "):
            for nested in (False, True):
                with self.subTest(value=value, nested=nested):
                    state = self.example(nested=nested)
                    draft = state["__fc_applied_choice"]["draft"]
                    if nested:
                        draft = draft["scenarios"][0]
                    draft["state"] = value
                    with self.assertRaises(CaseFileError):
                        snapshot_case(state, "full")


if __name__ == "__main__":
    unittest.main()
