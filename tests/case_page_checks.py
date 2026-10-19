"""Real Streamlit state restoration, isolated from legacy global UI wrappers."""
from datetime import date
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest
from app.case_file import decode_case, encode_case, snapshot_case

ROOT = Path(__file__).resolve().parents[1]


class CasePageTests(unittest.TestCase):
    def start(self, mobile=False, msil=False):
        import app.decimal_number_input_v2 as decimal_v2
        decimal_v2._renderer = None
        app = AppTest.from_file(str(ROOT / ("pages/App_MSIL.py" if msil else "Stima_epoca_decesso.py")), default_timeout=30)
        app.session_state["__full_device_mobile"] = mobile
        app.run()
        self.assertEqual(list(app.exception), [])
        return app

    def test_modal_modes_and_identifier_survive_close(self):
        import json
        app = self.start()
        self.assertFalse(app.get("dialog"))
        app.button(key="case_menu").click().run()
        self.assertTrue(app.get("dialog"))
        app.text_input(key="__case_code_input").set_value("CASE-MODAL").run()
        self.assertTrue(app.get("download_button"))
        self.assertFalse(any(c.proto.component_name.endswith("mortem_browser_cases")
                             for c in app.get("component_instance")))
        self.assertFalse(app.get("file_uploader"))
        app.session_state["__case_dialog_mode"] = "Carica"
        app.run()
        self.assertEqual(list(app.exception), [])
        self.assertFalse(any(c.proto.component_name.endswith("mortem_browser_cases")
                             for c in app.get("component_instance")))
        self.assertTrue(app.get("file_uploader"))
        self.assertFalse(app.get("download_button"))
        app.session_state["__case_dialog_open"] = False
        app.run()
        self.assertEqual(app.session_state["case_code"], "CASE-MODAL")
        app.button(key="case_menu").click().run()
        self.assertEqual(app.text_input(key="__case_code_input").value, "CASE-MODAL")

    def test_round_trip_between_devices_and_replacement_of_existing_case(self):
        for msil in (False, True):
            with self.subTest(msil=msil):
                app = self.start(False, msil)
                app.button(key="case_menu").click().run()
                app.text_input(key="__case_code_input").set_value("IL26-10").run()
                app.session_state["__case_dialog_open"] = False
                app.run()  # Close the dialog with a full rerun.
                app.session_state["selettore_macchie"] = "Non valutate"
                app.session_state["rt_val"] = 30.
                app.session_state["peso"] = 82.5
                app.session_state["ta_base_val"] = 15.
                app.run()
                app.button(key="btn_stima_mobile" if msil else "btn_stima").click().run()
                self.assertEqual(list(app.exception), [])
                before = app.session_state["__desc_dettagliate_html"]
                saved = decode_case(encode_case(snapshot_case(app.session_state._state.filtered_state, "msil" if msil else "full")))
                target = self.start(True, msil)
                target.session_state["__fc_draft"] = {"state": "Bagnato"}
                target.session_state["__fc_applied_choice"] = {"manual": True, "base_range": [3., 3.]}
                target.session_state["__case_pending_import"] = saved
                target.run()
                self.assertEqual(list(target.exception), [])
                self.assertEqual(list(target.error), [])
                self.assertTrue(target.session_state["__full_device_mobile"])
                self.assertEqual(target.session_state["peso"], saved["inputs"]["peso"])
                self.assertEqual(target.session_state["case_code"], "IL26-10")
                self.assertIsNone(target.session_state["__fc_draft"])
                self.assertFalse(target.session_state["run_stima_mobile" if msil else "show_results"])
                target.button(key="btn_stima_mobile" if msil else "btn_stima").click().run()
                self.assertEqual(list(target.exception), [])
                self.assertEqual(target.session_state["__desc_dettagliate_html"], before)

    def test_additional_parameters_and_different_measurement_datetime(self):
        from app.case_file import restored_inputs
        app = self.start()
        app.toggle(key="mostra_parametri_aggiuntivi").set_value(True).run()
        app.session_state["input_data_rilievo"] = date(2026, 10, 10)
        app.session_state["input_ora_rilievo"] = "00:15"
        app.session_state["Eccitabilità muscolare meccanica_selector"] = "Tumefazione reversibile"
        app.session_state["Eccitabilità muscolare meccanica_diversa"] = True
        app.session_state["Eccitabilità muscolare meccanica_ora"] = "23:45"
        app.session_state["Eccitabilità muscolare meccanica_ora__manual"] = True
        app.run()
        saved = snapshot_case(app.session_state._state.filtered_state, "full")
        target = self.start(True)
        target.session_state["__case_pending_import"] = decode_case(encode_case(saved))
        target.run()
        self.assertEqual(list(target.exception), [])
        self.assertTrue(target.session_state["mostra_parametri_aggiuntivi"])
        for key, value in restored_inputs(saved).items():
            if key.startswith("Eccitabilità muscolare meccanica_"):
                self.assertEqual(target.session_state[key], value, key)

    def test_editor_draft_resumes_without_applying_it(self):
        from app.fc_selection import apply_choice
        from test_fc_scenarios import temperature_payload
        app = self.start()
        state = app.session_state._state.filtered_state
        apply_choice(state, temperature_payload())
        state.update(__fc_active=True, __fc_form=state.copy(),
                     __fc_draft={"state": "Immerso", "temperature": "", "fields": {"water": "stagnante"},
                                 "lo": "", "hi": "", "weight": 70.}, case_code="x26-05")
        saved = snapshot_case(state, "full")
        app.session_state["__case_pending_import"] = saved
        app.run()
        self.assertEqual(list(app.exception), [])
        self.assertTrue(app.session_state["__fc_active"])
        self.assertEqual(app.session_state["__fc_draft"]["temperature"], "")
        self.assertEqual(app.session_state["__fc_applied_choice"]["range"], [1.35, 1.4])
        self.assertEqual(app.session_state["case_code"], "x26-05")
        self.assertFalse(any(c.proto.component_name.endswith("mortem_browser_cases")
                             for c in app.get("component_instance")))
        # Leaving the restored editor must retain later draft edits, without
        # replaying the draft that was present when the file was imported.
        import json
        widgets = app._tree.get_widget_states()
        component = next(c for c in app.get("component_instance")
                         if c.proto.component_name.endswith("mortem_fc_panel"))
        widget = widgets.widgets.add()
        widget.id = component.proto.id
        widget.json_value = json.dumps({"instance": app.session_state["__fc_instance"],
            "event_id": "case-back", "action": "back", "weight": 70.,
            "draft": {**saved["fc_draft"], "temperature": "8"}})
        app._run(widgets)
        self.assertEqual(list(app.exception), [])
        self.assertFalse(app.session_state["__fc_active"])
        self.assertEqual(app.session_state["__fc_draft"]["temperature"], "8")
        next(b for b in app.button if b.label == "Caso").click().run()
        self.assertEqual(next(w.value for w in app.text_input if w.label == "Sigla / numero del caso"), "x26-05")
        self.assertTrue(app.get("download_button"))
        downloaded = decode_case(encode_case(snapshot_case(app.session_state._state.filtered_state, "full")))
        self.assertEqual(downloaded["fc_draft"]["temperature"], "8")
        self.assertEqual(downloaded["fc_choice"], saved["fc_choice"])
        app.session_state["__case_dialog_open"] = False
        app.run()
        app.button(key="btn_fc_scenarios").click().run()
        self.assertEqual(app.session_state["case_code"], "x26-05")

    def test_import_opens_saved_calculation_mode(self):
        for source_msil in (False, True):
            with self.subTest(source_msil=source_msil):
                source = self.start(msil=source_msil)
                saved = snapshot_case(source.session_state._state.filtered_state, "msil" if source_msil else "full")
                saved["case_code"] = "x26-05"
                # Keep the real multipage entrypoint; a standalone AppTest of
                # pages/App_MSIL.py cannot navigate to the actual main script.
                target = self.start()
                if not source_msil:
                    target.switch_page("pages/App_MSIL.py").run()
                target.session_state["__case_pending_import"] = saved
                target.run()
                self.assertEqual(list(target.exception), [])
                self.assertEqual(target.session_state["case_code"], "x26-05")
                key = "btn_stima_mobile" if source_msil else "btn_stima"
                self.assertIn(key, [b.key for b in target.button])

    def test_file_import_restores_case_and_does_not_replay(self):
        import json
        for msil in (False, True):
            with self.subTest(msil=msil):
                app = self.start(msil=msil)
                saved = snapshot_case({"case_code": "BROWSER-TEST", "peso": 91., "rt_val": 28.},
                                      "msil" if msil else "full")
                app.button(key="case_menu").click().run()
                self.assertFalse(any(c.proto.component_name.endswith("mortem_browser_cases")
                                     for c in app.get("component_instance")))
                app.session_state["__case_pending_import"] = decode_case(encode_case(saved))
                app.run()
                self.assertEqual(list(app.exception), [])
                self.assertEqual(app.session_state["case_code"], "BROWSER-TEST")
                self.assertEqual(app.session_state["peso"], 91.)
                self.assertNotIn("__case_browser", app.session_state)
                app.session_state["peso"] = 72.
                app.run()
                self.assertEqual(app.session_state["peso"], 72.)
                self.assertEqual(list(app.exception), [])


if __name__ == "__main__":
    unittest.main()
