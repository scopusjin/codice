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
