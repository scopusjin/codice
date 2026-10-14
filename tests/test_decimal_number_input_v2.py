import unittest

from streamlit.testing.v1 import AppTest

from app.decimal_number_input_v2 import (
    _CSS,
    _JS,
    _component_instance_key,
    is_full_mobile_v2_key,
    mobile_decimal_v2_available,
)


class DecimalNumberInputV2Tests(unittest.TestCase):
    def test_v2_is_available_with_current_streamlit(self):
        self.assertTrue(mobile_decimal_v2_available())

    def test_v2_scope_is_full_mobile_only(self):
        for key in (
            "mortem_decimal_rt_val",
            "mortem_decimal_tm_val",
            "mortem_decimal_peso",
            "mortem_decimal_ta_base_val",
            "mortem_decimal_ta_other_val",
            "mortem_decimal_fattore_correzione",
            "mortem_decimal_fc_min_val",
            "mortem_decimal_fc_other_val",
        ):
            self.assertTrue(is_full_mobile_v2_key(key))

        for key in (
            "mortem_decimal_rt_val_widget",
            "mortem_decimal_ta_base_val_widget",
            "mortem_decimal_peso_widget",
            None,
        ):
            self.assertFalse(is_full_mobile_v2_key(key))

    def test_temperature_label_follows_actual_temperature_mode(self):
        from unittest.mock import patch
        import app

        state = {
            "stima_cautelativa_beta": True,
            "range_unico_beta": True,
            "ambient_temperature_range": False,
        }
        with patch.object(app.st, "session_state", state):
            for mobile, single_label, range_label in (
                (True, "T. amb. media", "T. amb. 1"),
                (False, "T. ambientale media", "T. ambientale media 1"),
            ):
                with patch.object(app, "full_device_is_mobile", return_value=mobile):
                    self.assertEqual(app._compact_mobile_label("unused", "ta_base_val"), single_label)
                    state["ambient_temperature_range"] = True
                    self.assertEqual(app._compact_mobile_label("unused", "ta_base_val"), range_label)
                    state["ambient_temperature_range"] = False

    def test_independent_single_value_helpers_even_in_prudent_mode(self):
        import importlib
        from unittest.mock import patch

        decimal = importlib.import_module("app.decimal_number_input")
        state = {
            "stima_cautelativa_beta": True,
            "range_unico_beta": True,
            "ambient_temperature_range": False,
            "fc_input_range": False,
        }
        captured = []
        def recorder(**kwargs):
            captured.append(kwargs)
            return kwargs["value"]
        with (
            patch.object(decimal.st, "session_state", state),
            patch.object(decimal, "mobile_decimal_v2_available", return_value=True),
            patch.object(decimal, "render_mobile_decimal_v2", side_effect=recorder),
        ):
            def help_for(key, value, label):
                captured.clear()
                decimal.decimal_number_input(value=value, compact_mobile=True,
                                             compact_label=label, key=key)
                self.assertEqual(len(captured), 1)
                return captured[0]

            ta = help_for("mortem_decimal_ta_base_val", 19., "T. amb. media")
            self.assertTrue(ta["help_enabled"])
            self.assertEqual(ta["help_state_key"], decimal._TA_STANDARD_HELP_OPEN_KEY)
            fc = help_for("mortem_decimal_fattore_correzione", 1., "FC")
            self.assertTrue(fc["help_enabled"])
            self.assertEqual(fc["help_state_key"], decimal._FC_STANDARD_HELP_OPEN_KEY)

            state["ambient_temperature_range"] = True
            ta_range = help_for("mortem_decimal_ta_other_val", 20., "T. amb. 2")
            self.assertTrue(ta_range["help_enabled"])
            self.assertEqual(ta_range["help_state_key"], decimal._TA_RANGE_HELP_OPEN_KEY)
            state["ambient_temperature_range"] = False
            self.assertTrue(help_for("mortem_decimal_ta_base_val", 19., "T. amb. media")["help_enabled"])

            state["fc_input_range"] = True
            fc_range = help_for("mortem_decimal_fc_other_val", 1.4, "FC max")
            self.assertTrue(fc_range["help_enabled"])
            self.assertEqual(fc_range["help_state_key"], decimal._FC_RANGE_HELP_OPEN_KEY)
            state["fc_input_range"] = False
            self.assertTrue(help_for("mortem_decimal_fattore_correzione", 1., "FC")["help_enabled"])

    def test_incomplete_main_fields_highlight_entire_control(self):
        self.assertIn(".number-control.needs-input:not(.is-dense) {", _CSS)
        self.assertIn(".number-control.needs-input:not(.is-dense) .label-help-cluster", _CSS)
        self.assertIn("control.classList.toggle('needs-input', missing)", _JS)
        self.assertIn("input.placeholder = missing ? '…' : ''", _JS)

    def test_v2_component_key_avoids_reserved_event_delimiter(self):
        component_key = _component_instance_key("mortem_decimal_rt_val")
        self.assertEqual(component_key, "mortem_decimal_rt_val-v2")
        self.assertNotIn("__", component_key)

    def test_mobile_control_has_white_label_and_no_reserved_empty_action(self):
        self.assertIn("background: var(--st-background-color, #FFFFFF);", _CSS)
        self.assertIn("width: max-content;", _CSS)
        self.assertIn(".external-action", _CSS)

    def test_mobile_help_uses_document_body_portal(self):
        self.assertIn("document.body.appendChild(portal)", _JS)
        self.assertIn("data-mortem-decimal-help-portal", _JS)
        self.assertIn("openMobileHelpPortal(mobileHelpText)", _JS)

    def test_fc_has_no_inline_range_action(self):
        from unittest.mock import patch
        import app.decimal_number_input_v2 as v2
        for locked in (False, True):
            state = dict(__full_device_mobile=True, ambient_temperature_range=True,
                         fc_input_range=False, ta_base_val=20., ta_other_val=25.,
                         stima_cautelativa_beta=True, fattore_correzione=1.)
            if locked:
                state['__fc_applied_choice'] = {'scenarios': [{}, {}], 'range': [1., 1.]}
            calls = []
            def renderer(**kwargs):
                calls.append(kwargs)
                return {'value': 1.}
            with patch.object(v2.st, 'session_state', state), patch.object(v2, '_get_renderer', return_value=renderer):
                v2.render_mobile_decimal_v2(
                    value=1., step=0.05, decimals=2, min_value=None, max_value=None,
                    disabled=False, sync_token=0, aria_label='FC', compact_label='FC', unit='',
                    help_enabled=False, help_state_key=None, help_text='', suggest_enabled=False,
                    suggest_label='', suggest_active=False, on_suggest=None, on_change=None,
                    key='mortem_decimal_fattore_correzione')
                call = calls[0]
                self.assertEqual(call['height'], 40)
                self.assertFalse(call['data']['suggest_enabled'])
                self.assertFalse(call['data']['temperature_action'])

    def test_inline_temperature_action_uses_existing_state_and_is_absent_when_locked(self):
        from unittest.mock import patch
        import app.decimal_number_input_v2 as v2
        for interval in (False, True):
            for locked in (False, True):
                state = dict(__full_device_mobile=True, ambient_temperature_range=interval,
                             ta_base_val=20., fattore_correzione=1.)
                calls = []
                def renderer(**kwargs):
                    calls.append(kwargs)
                    return {'value': 20.}
                with patch.object(v2.st, 'session_state', state), patch.object(v2, '_get_renderer', return_value=renderer):
                    v2.render_mobile_decimal_v2(
                        value=20., step=0.1, decimals=1, min_value=None, max_value=None,
                        disabled=locked, sync_token=0, aria_label='T. ambientale',
                        compact_label='T. ambientale', unit='°C', help_enabled=False,
                        help_state_key=None, help_text='', suggest_enabled=False,
                        suggest_label='', suggest_active=False, on_suggest=None,
                        on_change=None, key='mortem_decimal_ta_base_val')
                    call = calls[0]
                    self.assertEqual(call['height'], 40)
                    self.assertEqual(call['data']['temperature_action'], not locked)
                    self.assertEqual(call['data']['suggest_enabled'], not locked)
                    if not locked:
                        self.assertEqual(call['data']['suggest_label'], 'Valore singolo?' if interval else 'Range?')
                        call['on_suggest_change']()
                        self.assertEqual(state['ambient_temperature_range'], not interval)
                        self.assertEqual(state['ta_base_val'], 20.)

    def test_scenario_temperatures_open_editor_without_inline_range_action(self):
        from unittest.mock import patch
        import app.decimal_number_input_v2 as v2

        for key in ("mortem_decimal_ta_base_val", "mortem_decimal_ta_other_val"):
            with self.subTest(key=key):
                state = dict(__full_device_mobile=True,
                             stima_cautelativa_beta=True,
                             ambient_temperature_range=True)
                calls, opened = [], []

                def renderer(**kwargs):
                    calls.append(kwargs)
                    return {"value": 20.}

                with patch.object(v2.st, "session_state", state), patch.object(v2, "_get_renderer", return_value=renderer):
                    v2.render_mobile_decimal_v2(
                        value=20., step=0.1, decimals=1, min_value=None, max_value=None,
                        disabled=False, sync_token=0, aria_label="T. ambientale",
                        compact_label="T. amb.", unit="°C", help_enabled=False,
                        help_state_key=None, help_text="", suggest_enabled=False,
                        suggest_label="", suggest_active=False, on_suggest=None,
                        on_change=None, on_edit=lambda: opened.append(key), key=key,
                    )

                self.assertEqual(len(calls), 1)
                data = calls[0]["data"]
                self.assertFalse(data["disabled"])
                self.assertTrue(data["edit_on_click"])
                self.assertFalse(data["temperature_action"])
                self.assertFalse(data["suggest_enabled"])
                calls[0]["on_edit_change"]()
                self.assertEqual(opened, [key])

    def test_v2_mounts_and_reruns_without_streamlit_exception(self):
        script = r'''
import app.decimal_number_input_v2 as v2

# AppTest esegue lo script in un proprio ScriptRunContext: la registrazione
# deve avvenire qui, non nel processo unittest esterno.
v2._renderer = None

for key, label, value in (
    ("mortem_decimal_rt_val", "T. rettale", 35.0),
    ("mortem_decimal_tm_val", "T. ante-mortem", 37.0),
):
    v2.render_mobile_decimal_v2(
        value=value,
        step=0.1,
        decimals=1,
        min_value=None,
        max_value=None,
        disabled=False,
        sync_token=0,
        aria_label=label,
        compact_label=label,
        unit="°C",
        help_enabled=False,
        help_state_key=None,
        help_text="",
        suggest_enabled=False,
        suggest_label="",
        suggest_active=False,
        on_suggest=None,
        on_change=None,
        key=key,
    )
'''
        app = AppTest.from_string(script)
        app.run(timeout=10)
        first_errors = [str(item) for item in app.exception]
        self.assertEqual(first_errors, [])

        app.run(timeout=10)
        rerun_errors = [str(item) for item in app.exception]
        self.assertEqual(rerun_errors, [])


if __name__ == "__main__":
    unittest.main()
