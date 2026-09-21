import datetime
import json
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class FCPageTests(unittest.TestCase):
    def test_desktop_relocated_conditions_toggle_updates_mode_in_same_run(self):
        app = self.start(False)
        for enabled in (True, False, True):
            app.toggle(key="stima_cautelativa_beta").set_value(enabled).run()
            self.assertEqual(list(app.exception), [])
            self.assertEqual(app.session_state["range_unico_beta"], enabled)
            self.assertEqual(
                sum(toggle.key == "stima_cautelativa_beta" for toggle in app.toggle), 1,
            )
            labels = [e.value for e in app.markdown]
            self.assertEqual(any("Range fattore di correzione (FC)" in s for s in labels), enabled)
        for excluded in (True, False):
            app.checkbox(key="henssge_non_applicabile").set_value(excluded).run()
            self.assertEqual(list(app.exception), [])
            self.assertTrue(app.toggle(key="stima_cautelativa_beta").value)

    def test_special_helpers_across_desktop_and_mobile_sessions(self):
        # Streamlit wrappers are process-global, while device mode is per session.
        # Exercise both orders, including a mobile session after desktop setup.
        for mobile in (True, False, True, False):
            with self.subTest(mobile=mobile):
                app = self.start(mobile)
                app.session_state["input_data_rilievo"] = datetime.date(2026, 9, 17)
                app.session_state["input_ora_rilievo"] = "00:15"
                app.toggle(key="mostra_parametri_aggiuntivi").set_value(True).run()
                self.assertEqual(list(app.exception), [])
                self.assertEqual(
                    [selectbox.label for selectbox in app.selectbox[-2:]],
                    ["Eccitabilità muscolare meccanica", "Eccitabilità chimica pupillare"],
                )
                help_count = len(app.get("popover"))
                mechanical = app.selectbox[-2]
                mechanical.select(mechanical.options[1]).run()
                app.session_state[mechanical.label + "_ora"] = "23:45"
                app.session_state[mechanical.label + "_ora__manual"] = True
                app.session_state[mechanical.label + "_ora_native"] = "23:45"
                app.run()
                self.assertEqual(list(app.exception), [])
                self.assertEqual(
                    app.session_state[mechanical.label + "_data"],
                    datetime.date(2026, 9, 16),
                )
                self.open(app)
                self.event(app, "back", weight=70.0)
                self.assertTrue(app.session_state["mostra_parametri_aggiuntivi"])
                self.assertEqual(len(app.get("popover")), help_count)

    def start(self, mobile=False, msil=False):
        import app.decimal_number_input_v2 as decimal_v2
        decimal_v2._renderer = None
        script = "pages/App_MSIL.py" if msil else "Stima_epoca_decesso.py"
        app = AppTest.from_file(str(ROOT / script), default_timeout=30)
        app.session_state["__full_device_mobile"] = mobile
        app.run()
        self.assertEqual(list(app.exception), [])
        if not msil:
            titles = [e.proto.body for e in app.get("html")
                      if "id='mortem-page-title'" in e.proto.body]
            self.assertEqual(len(titles), 0 if mobile else 1)
            if titles:
                self.assertIn("STIMA EPOCA DECESSO", titles[0])
                self.assertNotIn("display:none", titles[0])
        return app

    def open(self, app, msil=False):
        app.session_state["toggle_fattore_inline_mobile" if msil else "toggle_fattore_inline_std"] = True
        app.session_state["toggle_fattore"] = True
        app.run()
        self.assertEqual(list(app.exception), [])
        self.assertTrue(app.session_state["__fc_active"])
        from app.fc_catalog import load_examples
        components = app.get("component_instance")
        fc_component = next(c for c in components if c.proto.component_name.endswith("mortem_fc_panel"))
        self.assertEqual(json.loads(fc_component.proto.json_args)["examples"], load_examples())

    def event(self, app, action, **values):
        instance = app.session_state["__fc_instance"]
        app.session_state["__fc_component_" + instance] = {
            "instance": instance, "event_id": action + str(values),
            "action": action, **values,
        }
        app.run()
        self.assertEqual(list(app.exception), [])

    def test_use_transfers_bounds_weight_and_preserves_form_on_desktop_and_mobile(self):
        for mobile in (False, True):
            with self.subTest(mobile=mobile):
                app = self.start(mobile)
                app.selectbox[0].select(app.selectbox[0].options[1]).run()
                selected = app.selectbox[0].value
                app.session_state["rt_val"] = 32.4
                app.session_state["ta_base_val"] = 19.3
                app.session_state["peso"] = 83.0
                self.open(app)
                self.event(app, "use", range=[1.25, 1.45], weight=91.0)
                self.assertFalse(app.session_state["__fc_active"])
                self.assertEqual(app.session_state["rt_val"], 32.4)
                self.assertEqual(app.session_state["ta_base_val"], 19.3)
                self.assertEqual(app.session_state["peso"], 91.0)
                self.assertEqual(app.session_state["FC_min_beta"], 1.25)
                self.assertEqual(app.session_state["FC_max_beta"], 1.45)
                self.assertEqual(app.selectbox[0].value, selected)
                app.run()  # No replay of the old component action on the next rerun.
                self.assertFalse(app.session_state["__fc_active"])

    def test_back_updates_weight_without_applying_fc_and_reopens_draft(self):
        app = self.start()
        app.session_state["fattore_correzione"] = 1.1
        self.open(app)
        self.event(app, "back", weight=82.0, range=[2, 2.4], draft={"state": "Bagnato", "lo": "2.00", "hi": "2.40"})
        self.assertEqual(app.session_state["fattore_correzione"], 1.1)
        self.assertEqual(app.session_state["peso"], 82)
        self.open(app)
        self.assertEqual(app.session_state["__fc_draft"]["state"], "Bagnato")

    def test_msil_applies_exact_range_instead_of_center_plus_minus_point_one(self):
        app = self.start(msil=True)
        self.open(app, msil=True)
        self.event(app, "use", range=[0.6, 0.75], weight=72.0)
        self.assertEqual(app.session_state["FC_min_beta"], 0.6)
        self.assertEqual(app.session_state["FC_max_beta"], 0.75)
        self.assertEqual(app.session_state["peso"], 72)

    def test_invalid_message_does_not_apply_choice(self):
        app = self.start()
        self.open(app)
        self.event(app, "use", range=[1.4, 1.2], weight=70)
        self.assertTrue(app.session_state["__fc_active"])
        self.assertEqual(app.session_state["__fc_form"]["fattore_correzione"], 1)
        self.assertTrue(app.error)

    def test_tables_returns_to_fc_with_draft_and_form_intact(self):
        app = self.start()
        app.session_state["rt_val"] = 31.8
        self.open(app)
        self.event(app, "tables", weight=74.0, draft={"state": "Bagnato", "lo": "0.60", "hi": "0.75"})
        self.assertIn("Tabelle di riferimento", [title.value for title in app.title])
        app.button(key="back_to_fc_top").click().run()
        self.assertEqual(list(app.exception), [])
        self.assertTrue(app.session_state["__fc_active"])
        self.assertEqual(app.session_state["__fc_draft"]["lo"], "0.60")
        self.event(app, "back", weight=74.0)
        self.assertEqual(app.session_state["rt_val"], 31.8)
