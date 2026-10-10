from copy import deepcopy
from datetime import date, datetime
import json
import unittest

from app.case_file import (CaseFileError, MAX_BYTES, case_filename, decode_case,
                           encode_case, restored_inputs, snapshot_case)
from app.fc_selection import apply_choice, refresh_fc_for_weight
from test_fc_scenarios import temperature_payload


class CaseFileTests(unittest.TestCase):
    def example(self):
        state = {"case_code": "IL26-10", "rt_val": 30., "tm_val": 37.2, "peso": 70.,
                 "input_data_rilievo": date(2026, 10, 10), "input_ora_rilievo": "09:15",
                 "selettore_macchie_ui": "Fisse", "selettore_rigidita_ui": "Presente, in aumento",
                 "mostra_parametri_aggiuntivi": True,
                 "Eccitabilità muscolare meccanica_selector": "Tumefazione reversibile",
                 "Eccitabilità muscolare meccanica_diversa": True,
                 "Eccitabilità muscolare meccanica_data": date(2026, 10, 9),
                 "Eccitabilità muscolare meccanica_ora": "23:45",
                 "Eccitabilità muscolare meccanica_ora__manual": True}
        apply_choice(state, temperature_payload())
        return state

    def test_complete_round_trip_and_subsequent_weight_adaptation(self):
        state = self.example()
        case = snapshot_case(state, "full")
        restored = restored_inputs(decode_case(encode_case(case)))
        for key in ("peso", "input_data_rilievo", "input_ora_rilievo", "__fc_applied_choice",
                    "Eccitabilità muscolare meccanica_selector", "Eccitabilità muscolare meccanica_data",
                    "Eccitabilità muscolare meccanica_ora", "Eccitabilità muscolare meccanica_ora__manual"):
            self.assertEqual(restored[key], state[key], key)
        self.assertEqual(restored["selettore_macchie_ui"], "Fisse")
        for weight in (100., 110., 70.):
            state["peso"] = restored["peso"] = weight
            refresh_fc_for_weight(state)
            refresh_fc_for_weight(restored)
            self.assertEqual(restored["__fc_applied_choice"], state["__fc_applied_choice"])

    def test_incomplete_inputs_and_fc_draft_are_distinct_from_applied_values(self):
        state = self.example()
        applied = deepcopy(state["__fc_applied_choice"])
        state.update(__fc_active=True, __fc_form=deepcopy(state),
                     __fc_draft={"state": "Immerso", "lo": "", "hi": "", "temperature": "",
                                 "fields": {"water": "stagnante"}, "weight": None, "manualBase": [None, None]},
                     case_code="x26-05")
        # Widget cleanup while the editor is open must not lose the home form.
        state.pop("input_data_rilievo")
        case = decode_case(encode_case(snapshot_case(state, "full")))
        self.assertTrue(case["editor_open"])
        self.assertEqual(case["fc_choice"], applied)
        self.assertEqual(case["fc_draft"]["temperature"], "")
        self.assertEqual(case["inputs"]["input_data_rilievo"], "2026-10-10")
        self.assertEqual(case["case_code"], "x26-05")
        incomplete = snapshot_case({"rt_val": None, "peso": None, "input_ora_rilievo": ""}, "msil")
        self.assertIsNone(restored_inputs(decode_case(encode_case(incomplete)))["peso"])

    def test_only_case_data_is_exported_and_case_code_is_preserved(self):
        for code in ("x26-05", "IL26-10", "12345", "IL26/10", ""):
            state = {**self.example(), "case_code": code, "secret": "not a case input",
                     "__full_device_mobile": True, "__fc_instance": "old", "mortem_decimal_peso": {"edit": True}}
            case = decode_case(encode_case(snapshot_case(state, "full")))
            self.assertEqual(case["case_code"], code)
            self.assertNotIn("not a case input", encode_case(case).decode())
            self.assertNotIn("__full_device_mobile", case["inputs"])
            self.assertNotIn("__fc_instance", case["inputs"])
            self.assertNotIn("/", case_filename(case))
            if code in ("x26-05", "IL26-10", "12345"):
                self.assertEqual(case_filename(case), f"mortem_{code}.json")

    def test_invalid_files_fail_before_any_restore(self):
        valid = snapshot_case(self.example(), "full")
        mutations = [lambda c: c.update(schema_version=999), lambda c: c.update(format="other"),
                     lambda c: c["inputs"].update(__fc_active=True),
                     lambda c: c["inputs"].update(peso=float("nan")),
                     lambda c: c["inputs"].update(input_data_rilievo="2026-99-99"),
                     lambda c: c["inputs"].update(henssge_round_minutes=7),
                     lambda c: c["signs"].update(livor="unknown"),
                     lambda c: c["fc_choice"]["scenarios"][0].update(temperature=None),
                     lambda c: c["fc_choice"].update(description="<script>bad()</script>"),
                     lambda c: c.update(fc_draft={"fields": {"water": []}})]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                bad = deepcopy(valid)
                mutate(bad)
                with self.assertRaises(CaseFileError):
                    decode_case(json.dumps(bad).encode())
        for raw in (b"not json", b"\xff", b"{" + b" " * MAX_BYTES, b'{"format":"mortem-case","format":"other"}'):
            with self.assertRaises(CaseFileError):
                decode_case(raw)

    def test_same_calculation_after_serialization(self):
        from app.graphing_cooling import compute_cooling_state
        original = self.example()
        restored = restored_inputs(decode_case(encode_case(snapshot_case(original, "full"))))
        def compute(state):
            return compute_cooling_state(input_rt=state["rt_val"], input_ta=state["ta_base_val"],
                input_tm=state["tm_val"], input_w=state["peso"], fattore_correzione=state["fattore_correzione"],
                data_ora_ispezione=datetime(2026, 10, 10, 9, 15), skip_warnings=True, cooling_options=state)
        self.assertEqual(compute(original), compute(restored))


if __name__ == "__main__":
    unittest.main()
