import datetime
import json
import unittest
from uuid import uuid4
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class FCPageTests(unittest.TestCase):
    def test_single_panel_temperature_and_integer_weight_format_in_all_views(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                app = self.start(mobile, msil=msil)
                self.open(app, msil=msil)
                self.event(app, "use", range=[.5, .5], base_range=[.5, .5],
                           weight=70., temperature=8.5, manual=False,
                           description="corpo immerso in acqua ferma")
                self.assertEqual(app.session_state["ta_base_val"], 8.5)
                self.assertEqual(app.session_state["peso_str"], "70")
                weights = [json.loads(c.proto.json_args) for c in app.get("component_instance")
                           if "peso" in c.proto.id]
                for args in weights:
                    if "decimals" in args:
                        self.assertEqual(args["decimals"], 0)

    def test_home_scenario_button_temperature_application_and_blue_note(self):
        from test_fc_scenarios import temperature_payload
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                app = self.start(mobile, msil=msil)
                app.session_state["rt_val"] = 30.
                app.session_state["tm_val"] = 37.2
                app.button(key="btn_fc_scenarios").click().run()
                self.assertEqual(list(app.exception), [])
                self.assertTrue(app.session_state["__fc_draft"]["multiple"])
                self.assertEqual(len(app.session_state["__fc_draft"]["scenarios"]), 2)
                self.event(app, "use", **temperature_payload())
                self.assertEqual((app.session_state["Ta_min_beta"], app.session_state["Ta_max_beta"]), (8., 20.))
                app.button(key="btn_fc_scenarios").click().run()
                draft = app.session_state["__fc_draft"]
                self.assertEqual([s["temperature"] for s in draft["scenarios"]], ["20.0", "8.0"])
                self.event(app, "back", weight=100.)
                self.assertEqual(list(app.exception), [])
                self.assertEqual(app.session_state["__fc_applied_choice"]["range"], [1.3, 1.35])
                self.assertEqual((app.session_state["Ta_min_beta"], app.session_state["Ta_max_beta"]), (8., 20.))
                if not msil:
                    app.button(key="btn_stima").click().run()
                    self.assertEqual(list(app.exception), [])
                    text = app.session_state["__desc_dettagliate_html"]
                    self.assertIn("color:blue;font-size:small;'>FC impostato manualmente negli scenari 1, 2.", text)
                    self.assertIn("acqua 8 °C", text)

    def test_conditions_helper_replaces_toggle_and_panel_activates_ranges(self):
        for mobile in (False, True):
            with self.subTest(mobile=mobile):
                app = self.start(mobile)
                self.assertFalse(app.session_state["stima_cautelativa_beta"])
                self.assertNotIn("Condizioni variabili?", [e.label for e in app.toggle])
                self.assertTrue(any("Usa Più scenari" in e.value for e in app.markdown))
                self.choose_manual(app, [1., 1.5])
                for excluded in (True, False):
                    app.checkbox(key="henssge_non_applicabile").set_value(excluded).run()
                    self.assertEqual(list(app.exception), [])
                    self.assertTrue(app.session_state["range_unico_beta"])
                    self.assertTrue(app.session_state["stima_cautelativa_beta"])
                    self.assertNotIn("stima_cautelativa_beta", [e.key for e in app.toggle])
                    self.assertTrue(any("Usa Più scenari" in e.value for e in app.markdown))
                self.assertEqual(app.session_state["fc_min_val"], 1.)
                self.assertEqual(app.session_state["fc_other_val"], 1.5)

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

    def assert_weight(self, state, weight):
        self.assertEqual(state["peso"], weight)
        self.assertEqual(state["peso_widget"], weight)
        self.assertEqual(state["peso_str"], f"{weight:.0f}")

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
                self.assert_weight(app.session_state, 91.0)
                self.assertEqual(app.session_state["FC_min_beta"], 1.25)
                self.assertEqual(app.session_state["FC_max_beta"], 1.45)
                self.assertEqual(app.selectbox[0].value, selected)
                app.run()  # No replay of the old component action on the next rerun.
                self.assertFalse(app.session_state["__fc_active"])

    def test_back_updates_weight_without_applying_fc_and_reopens_draft(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                app = self.start(mobile, msil)
                app.session_state["fattore_correzione"] = 1.1
                self.open(app, msil)
                self.event(app, "back", weight=82.0, range=[2, 2.4], draft={"state": "Bagnato", "lo": "2.00", "hi": "2.40"})
                self.assertEqual(app.session_state["fattore_correzione"], 1.1)
                self.assert_weight(app.session_state, 82.0)
                self.open(app, msil)
                self.assertEqual(app.session_state["__fc_draft"]["state"], "Bagnato")

    def change_decimal(self, app, key, value):
        # AppTest has no custom-component setter. Send the real widget payload
        # so Streamlit runs V1/V2 callbacks, rather than editing logical state.
        widgets = app._tree.get_widget_states()
        candidates = [(e, value) for e in app.get("component_instance")
                      if e.proto.id.endswith("-" + key)]
        candidates += [(e, {"value": value}) for e in app.get("bidi_component")
                       if e.proto.id.endswith("-" + key + "-v2")]
        self.assertEqual(len(candidates), 1, key)
        element, payload = candidates[0]
        widget = widgets.widgets.add()
        widget.id = element.proto.id
        widget.json_value = json.dumps(payload)
        app._run(widgets)
        self.assertEqual(list(app.exception), [])

    def change_weight(self, app, weight, mobile, msil):
        scope = "" if mobile else ("_range" if app.session_state["stima_cautelativa_beta"] else "_single")
        key = "mortem_decimal_peso_widget" if msil else "mortem_decimal_peso" + scope
        self.change_decimal(app, key, weight)
        self.assertEqual(app.session_state["peso"], weight)

    def open_from_fc(self, app, key="fattore_correzione"):
        widgets = app._tree.get_widget_states()
        component_key = "mortem_decimal_" + key
        candidates = [(e, {"edit_token": uuid4().hex})
                      for e in app.get("component_instance") if e.proto.id.endswith("-" + component_key)]
        candidates += [(e, {"edit": True}) for e in app.get("bidi_component")
                       if e.proto.id.endswith("-" + component_key + "-v2")]
        self.assertEqual(len(candidates), 1)
        element, payload = candidates[0]
        widget = widgets.widgets.add()
        widget.id = element.proto.id
        widget.json_value = json.dumps(payload)
        app._run(widgets)
        self.assertEqual(list(app.exception), [])
        self.assertTrue(app.session_state["__fc_active"])

    def choose_manual(self, app, bounds, key="fattore_correzione"):
        self.open_from_fc(app, key)
        weight = app.session_state["peso"] or 70.
        draft = {**app.session_state["__fc_draft"], "lo": str(bounds[0]), "hi": str(bounds[1]),
                 "manual": True, "manualBase": bounds, "selectedBase": None,
                 "manualWeightAdjusted": False, "weight": weight}
        self.event(app, "use", range=bounds, base_range=bounds, weight=weight,
                   manual=True, manual_weight_adjusted=False, draft=draft)

    def test_fc_fields_only_open_panel_and_do_not_accept_inline_changes(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            for interval in ((False,) if msil else (False, True)):
                with self.subTest(mobile=mobile, msil=msil, interval=interval):
                    app = self.start(mobile, msil)
                    if interval:
                        self.choose_manual(app, [1., 1.5])
                    self.assertNotIn("Consiglia FC", [e.label for e in app.button] + [e.label for e in app.toggle])
                    for component in app.get("bidi_component"):
                        self.assertFalse(json.loads(component.proto.json).get("suggest_enabled", False))
                    for component in app.get("component_instance"):
                        self.assertFalse(json.loads(component.proto.json_args).get("suggest_enabled", False))
                    keys = ("fc_min_val", "fc_other_val") if interval else ("fattore_correzione",)
                    for key in keys:
                        before = app.session_state[key]
                        self.change_decimal(app, "mortem_decimal_" + key, 2.)
                        self.assertEqual(app.session_state[key], before)
                        self.open_from_fc(app, key)
                        draft = app.session_state["__fc_draft"]
                        if msil:
                            self.assertEqual([draft["lo"], draft["hi"]], ["0.90", "1.10"])
                        else:
                            self.assertEqual(float(draft["lo" if key != "fc_other_val" else "hi"]), before)
                        self.event(app, "back", weight=app.session_state["peso"])
                        self.assertEqual(app.session_state[key], before)
                        app.run()
                        self.assertFalse(app.session_state["__fc_active"])

    def test_main_weight_refreshes_point_and_range_in_every_view(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            for base, adjusted in (([1.4, 1.4], [1.3, 1.3]), ([2.8, 3.1], [2.3, 2.45])):
                with self.subTest(mobile=mobile, msil=msil, base=base):
                    app = self.start(mobile, msil)
                    self.open(app, msil)
                    self.event(app, "use", range=base, base_range=base, weight=70., manual=False)
                    for weight, expected in ((100., adjusted), (70., base)):
                        self.change_weight(app, weight, mobile, msil)
                        self.assertEqual(app.session_state["fc_suggested_vals"], expected)
                        self.assertEqual(app.session_state["__msil_fc_chosen_range"], expected)
                        self.assertFalse(any("ricontrollare il FC" in w.value for w in app.warning))
                        app.run()
                        self.assertEqual(list(app.exception), [])
                        self.assertEqual(app.session_state["fc_suggested_vals"], expected)
                        self.assertEqual(
                            [app.session_state["FC_min_beta"], app.session_state["FC_max_beta"]],
                            expected,
                        )
                        if not msil and app.session_state["stima_cautelativa_beta"]:
                            self.assertEqual(
                                [app.session_state["fc_min_val"], app.session_state["fc_other_val"]],
                                expected,
                            )
                        else:
                            from app.fc_selection import rounded_fc
                            self.assertEqual(app.session_state["fattore_correzione"], rounded_fc(sum(expected) / 2))

    def test_manual_panel_fc_adapts_its_own_values_after_helper_selection(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                app = self.start(mobile, msil)
                self.open(app, msil)
                self.event(app, "use", range=[2.8, 3.1], base_range=[2.8, 3.1], weight=70., manual=False)
                key = "fattore_correzione" if msil else "fc_min_val"
                self.choose_manual(app, [2.5, 2.5] if msil else [2.5, 3.1], key)
                self.assertTrue(app.session_state["__fc_applied_choice"]["manual"])
                self.change_weight(app, 100., mobile, msil)
                self.assertEqual(app.session_state[key], 2.1)
                expected = [2.1, 2.1] if msil else [2.1, 2.45]
                self.assertEqual([app.session_state["FC_min_beta"], app.session_state["FC_max_beta"]], expected)
                self.assertTrue(any("FC adattato per il peso" in w.value for w in app.caption))
                self.change_weight(app, 70., mobile, msil)
                self.assertEqual(app.session_state[key], 2.5)

    def test_manual_fc_entered_through_fc_field_refreshes_in_every_view(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                app = self.start(mobile, msil)
                self.choose_manual(app, [2., 2.])
                for weight, expected, notice in ((75., 2., False), (100., 1.75, True),
                                                 (70., 2., True), (75., 2., False), (100., 1.75, True)):
                    self.change_weight(app, weight, mobile, msil)
                    self.assertEqual(app.session_state["fattore_correzione"], expected)
                    notices = [w.value for w in app.caption if "FC adattato per il peso" in w.value]
                    self.assertEqual(bool(notices), notice)
                    self.assertFalse(app.session_state["__fc_active"])
                    app.run()
                    self.assertEqual(list(app.exception), [])
                    self.assertEqual(app.session_state["fattore_correzione"], expected)
                self.open_from_fc(app)
                self.assertEqual(app.session_state["__fc_draft"]["lo"], "1.75")
                self.assertEqual(app.session_state["__fc_draft"]["manualBase"], [2., 2.])
                self.assertTrue(app.session_state["__fc_draft"]["manualWeightAdjusted"])
                self.event(app, "use", range=[2.5, 2.5], base_range=[2.5, 2.5], weight=100.,
                           manual=True, manual_weight_adjusted=False)
                self.assertFalse(any("FC adattato per il peso" in w.value for w in app.caption))
                self.change_weight(app, 110., mobile, msil)
                self.assertEqual(app.session_state["fattore_correzione"], 2.)

    def test_manual_panel_choice_keeps_adjustment_notice_on_return(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                app = self.start(mobile, msil)
                self.open(app, msil)
                self.event(app, "use", range=[1.75, 1.75], base_range=[2., 2.],
                           weight=100., manual=True, manual_weight_adjusted=True)
                self.assertTrue(any("FC adattato per il peso" in w.value for w in app.caption))
                self.change_weight(app, 70., mobile, msil)
                self.assertEqual(app.session_state["fc_suggested_vals"], [2., 2.])

    def test_draft_syncs_weight_and_invalidates_saved_results_only_on_change(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                app = self.start(mobile, msil)
                app.session_state["show_results"] = True
                app.session_state["run_stima_mobile"] = True
                self.open(app, msil)
                saved = app.session_state["__fc_form"]
                previous_fc = saved["fattore_correzione"]
                self.event(app, "draft", weight=saved["peso"])
                self.assertTrue(app.session_state["__fc_form"]["show_results"])
                self.assertTrue(app.session_state["__fc_form"]["run_stima_mobile"])
                self.event(app, "draft", weight=82.5)
                for state in (app.session_state, app.session_state["__fc_form"]):
                    self.assert_weight(state, 82.5)
                self.assertFalse(app.session_state["__fc_form"]["show_results"])
                self.assertFalse(app.session_state["__fc_form"]["run_stima_mobile"])
                self.assertEqual(app.session_state["__fc_form"]["fattore_correzione"], previous_fc)
                self.assertTrue(app.session_state["__fc_active"])

    def test_invalid_weight_does_not_replace_live_or_saved_weight(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                app = self.start(mobile, msil)
                self.open(app, msil)
                self.event(app, "draft", weight=82.5)
                previous_fc = app.session_state["__fc_form"]["fattore_correzione"]
                for action in ("draft", "use"):
                    for weight in (None, "non valido", 3.9, 150.1):
                        self.event(app, action, weight=weight, range=[1.25, 1.45])
                        for state in (app.session_state, app.session_state["__fc_form"]):
                            self.assert_weight(state, 82.5)
                        self.assertTrue(app.session_state["__fc_active"])
                        self.assertEqual(app.session_state["__fc_form"]["fattore_correzione"], previous_fc)
                        if action == "use":
                            self.assertTrue(app.error)

    def test_msil_applies_exact_range_instead_of_center_plus_minus_point_one(self):
        app = self.start(msil=True)
        self.open(app, msil=True)
        self.event(app, "use", range=[0.6, 0.75], weight=72.0)
        self.assertEqual(app.session_state["FC_min_beta"], 0.6)
        self.assertEqual(app.session_state["FC_max_beta"], 0.75)
        self.assert_weight(app.session_state, 72.0)

    def test_invalid_message_does_not_apply_choice(self):
        app = self.start()
        self.open(app)
        self.event(app, "use", range=[1.4, 1.2], weight=70)
        self.assertTrue(app.session_state["__fc_active"])
        self.assertEqual(app.session_state["__fc_form"]["fattore_correzione"], 1)
        self.assertTrue(app.error)

    def test_scenarios_survive_apply_weight_change_and_reopening_in_all_views(self):
        from test_fc_scenarios import scenario_payload
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                app = self.start(mobile, msil)
                app.session_state["rt_val"] = 31.8
                self.open(app, msil)
                self.event(app, "use", **scenario_payload())
                self.assertFalse(app.session_state["__fc_active"])
                self.assertEqual(app.session_state["fc_suggested_vals"], [1.35, 1.4])
                self.change_weight(app, 100., mobile, msil)
                self.assertEqual(app.session_state["fc_suggested_vals"], [1.3, 1.35])
                self.assertFalse(app.session_state["__fc_active"])
                self.assertEqual(app.session_state["rt_val"], 31.8)
                self.open_from_fc(app, "fattore_correzione" if msil else "fc_min_val")
                draft = app.session_state["__fc_draft"]
                self.assertTrue(draft["multiple"])
                self.assertEqual(len(draft["scenarios"]), 2)
                self.assertEqual([draft["lo"], draft["hi"]], ["1.30", "1.30"])
                self.event(app, "back", weight=100., draft=draft)
                self.assertEqual(len(app.session_state["__fc_applied_choice"]["scenarios"]), 2)
                self.open_from_fc(app, "fattore_correzione" if msil else "fc_min_val")
                self.event(app, "use", range=[1., 1.], base_range=[1., 1.], weight=100.,
                           manual=False, draft={"multiple": False})
                self.assertNotIn("scenarios", app.session_state["__fc_applied_choice"])
                self.assertIsNone(app.session_state["fattori_condizioni_testo"])

    def test_tables_returns_to_fc_with_draft_and_form_intact(self):
        for mobile, msil in ((False, False), (True, False), (True, True)):
            with self.subTest(mobile=mobile, msil=msil):
                # Keep the real entrypoint so AppTest registers sibling pages.
                app = self.start(mobile)
                if msil:
                    app.switch_page("pages/App_MSIL.py").run()
                    self.assertEqual(list(app.exception), [])
                app.session_state["rt_val"] = 31.8
                self.open(app, msil)
                self.event(app, "tables", weight=74.0, draft={"state": "Bagnato", "lo": "0.60", "hi": "0.75"})
                self.assertIn("Tabelle di riferimento", [title.value for title in app.title])
                for state in (app.session_state, app.session_state["__fc_form"]):
                    self.assert_weight(state, 74.0)
                app.button(key="back_to_fc_top").click().run()
                self.assertEqual(list(app.exception), [])
                self.assertTrue(app.session_state["__fc_active"])
                self.assertEqual(app.session_state["__fc_draft"]["lo"], "0.60")
                self.event(app, "back", weight=74.0)
                self.assertEqual(app.session_state["rt_val"], 31.8)
                self.assert_weight(app.session_state, 74.0)
