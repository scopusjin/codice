"""Presentational FC helpers and optional inspection-time empty field."""
import importlib
import unittest
from pathlib import Path
from unittest.mock import patch

from app.device_mode import _uniform_helper_container_key
from app.full_mobile_layout import _FULL_MOBILE_CSS

time_picker = importlib.import_module("app.native_time_picker")


class FCUIHelpersAndTimeTests(unittest.TestCase):
    def test_henssge_and_scenario_helpers_share_the_same_slot_style(self):
        self.assertEqual(
            _uniform_helper_container_key("mortem_help_henssge"),
            "fcpanel_std_vest_help_slot_henssge",
        )
        self.assertEqual(
            _uniform_helper_container_key("mortem_help_prudent_scenarios"),
            "fcpanel_std_vest_help_slot_scenarios",
        )
        self.assertIn(
            '[class*="st-key-fcpanel_std_vest_help_slot_"] [data-testid="stPopoverButton"]',
            _FULL_MOBILE_CSS,
        )
        self.assertIn(
            '[data-testid="stPopoverButton"] [aria-hidden="true"]',
            _FULL_MOBILE_CSS,
        )

    def test_only_main_inspection_time_uses_optional_empty_highlight(self):
        state = {
            "__full_datetime_always_visible": True,
            "input_ora_rilievo": time_picker.EMPTY_TIME_SENTINEL,
        }
        calls = []

        def component(**kwargs):
            calls.append(kwargs)
            return kwargs["value"]

        with (
            patch.object(time_picker.st, "session_state", state),
            patch.object(time_picker, "full_device_is_mobile", return_value=True),
            patch.object(time_picker, "_component", side_effect=component),
            patch.object(time_picker, "_theme_value", return_value="#f0f0f0"),
        ):
            self.assertEqual(
                time_picker.native_time_picker(
                    time_picker.EMPTY_TIME_SENTINEL,
                    key="input_ora_rilievo_native",
                ),
                time_picker.EMPTY_TIME_SENTINEL,
            )
            self.assertTrue(calls[-1]["highlight_missing"])
            self.assertEqual(calls[-1]["value"], "")

            time_picker.native_time_picker(
                time_picker.EMPTY_TIME_SENTINEL,
                key="sopraciliare_ora_native",
                inherited=True,
            )
            self.assertFalse(calls[-1]["highlight_missing"])
            self.assertEqual(calls[-1]["value"], "")

            time_picker.native_time_picker("12:30", key="input_ora_rilievo_native")
            self.assertTrue(calls[-1]["highlight_missing"])
            self.assertEqual(calls[-1]["value"], "12:30")

    def test_time_frontend_updates_highlight_with_operator_input(self):
        frontend = Path(__file__).resolve().parents[1] / "app" / "native_time_picker_frontend"
        js = (frontend / "main.js").read_text(encoding="utf-8")
        css = (frontend / "style.css").read_text(encoding="utf-8")
        self.assertIn('highlightMissing = Boolean(args.highlight_missing)', js)
        self.assertIn('timeControl.classList.toggle("needs-input", missing)', js)
        self.assertIn('timeInput.setAttribute("aria-invalid", "false")', js)
        self.assertIn('.time-control.needs-input {', css)
        self.assertIn('.time-control.needs-input #time-input {', css)
        self.assertIn('.time-control.needs-input #time-input::placeholder', css)
        self.assertNotIn('border-color: #b33b32', css)

    def test_legacy_numeric_input_highlights_field_not_entire_row(self):
        css_path = Path(__file__).resolve().parents[1] / "app" / "decimal_number_input_frontend" / "style.css"
        css = css_path.read_text(encoding="utf-8")
        self.assertNotIn('.number-control.needs-input {', css)
        self.assertIn('.number-control.needs-input #number-input {', css)
        self.assertIn('.number-control.needs-input.has-unit .mobile-unit {', css)


if __name__ == "__main__":
    unittest.main()
