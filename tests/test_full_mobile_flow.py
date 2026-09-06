# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

import app.decimal_number_input_v2 as decimal_v2
from app.mobile_shell import _MINIMAL_MOBILE_SHELL_CSS, _MOBILE_HEADER_HTML


class FullMobileFlowTests(unittest.TestCase):
    def _mobile_app(self):
        # Ogni AppTest possiede un registro componenti separato.
        decimal_v2._renderer = None
        script = Path(__file__).resolve().parents[1] / "Stima_epoca_decesso.py"
        app = AppTest.from_file(str(script), default_timeout=20)
        app.session_state["__full_device_mobile"] = True
        app.run(timeout=20)
        return app

    def test_mobile_navigation_uses_sidebar_only(self):
        app = self._mobile_app()

        self.assertEqual([str(item) for item in app.exception], [])
        self.assertNotIn("Modalità sopralluogo", [button.label for button in app.button])
        self.assertIn(
            "Dati tanatologici aggiuntivi",
            [toggle.label for toggle in app.toggle],
        )

    def test_mobile_header_hides_native_header_but_keeps_sidebar_trigger(self):
        css = _MINIMAL_MOBILE_SHELL_CSS
        html = _MOBILE_HEADER_HTML

        self.assertIn('header[data-testid="stHeader"]', css)
        native_header_rule = css.split(
            'header[data-testid="stHeader"],', 1
        )[1].split("}", 1)[0]
        self.assertIn("display: none", native_header_rule)

        self.assertIn('class="menu-button"', html)
        self.assertIn("function openSidebar()", html)
        self.assertIn('[data-testid="stExpandSidebarButton"]', html)
        self.assertIn('[data-testid="stSidebarCollapsedControl"]', html)

    def test_additional_tanatology_section_opens_cleanly(self):
        app = self._mobile_app()
        next(
            toggle for toggle in app.toggle
            if toggle.label == "Dati tanatologici aggiuntivi"
        ).set_value(True)
        app.run(timeout=20)

        self.assertEqual([str(item) for item in app.exception], [])
        self.assertEqual(
            [selectbox.label for selectbox in app.selectbox[-2:]],
            ["Eccitabilità muscolare meccanica", "Eccitabilità chimica pupillare"],
        )
        self.assertIn("Alterazioni putrefattive?", [item.label for item in app.checkbox])

    def test_mobile_results_open_without_duplicate_container(self):
        app = self._mobile_app()
        app.selectbox[0].select(app.selectbox[0].options[1])
        app.selectbox[1].select(app.selectbox[1].options[1])
        app.run(timeout=20)

        next(
            button for button in app.button
            if button.label == "Procedi con la stima"
        ).click()
        app.run(timeout=30)

        self.assertEqual([str(item) for item in app.exception], [])
        self.assertTrue(app.session_state["show_results"])
        self.assertTrue(app.session_state["__desc_dettagliate_html"])
        self.assertIn("Mostra grafico", [expander.label for expander in app.expander])

    def test_mobile_temperature_and_fc_helpers_stay_inside_v2_control(self):
        app = self._mobile_app()
        app.session_state["__decimal_ta_standard_help_open"] = True
        app.session_state["__decimal_fc_standard_help_open"] = True
        app.run(timeout=20)

        self.assertEqual([str(item) for item in app.exception], [])
        captions = [caption.value for caption in app.caption]
        self.assertFalse(any("temperatura ambientale media" in text for text in captions))
        self.assertFalse(any("fattore di correzione" in text for text in captions))
        self.assertFalse(bool(app.session_state["__decimal_ta_standard_help_open"]))
        self.assertFalse(bool(app.session_state["__decimal_fc_standard_help_open"]))

    def test_mobile_fc_range_reset_is_compact_and_inline(self):
        app = self._mobile_app()
        app.session_state["stima_cautelativa_beta"] = True
        app.session_state["__prudent_explicit_ranges_initialized"] = True
        app.session_state["range_unico_beta"] = True
        app.session_state["toggle_fattore_inline"] = True
        app.session_state["toggle_fattore"] = True
        app.session_state["__full_fc_suggest_target"] = "range"
        app.run(timeout=20)

        self.assertEqual([str(item) for item in app.exception], [])
        labels = [button.label for button in app.button]
        self.assertIn("→ Usalo", labels)
        self.assertIn("↻", labels)
        self.assertNotIn("Reset range", labels)


if __name__ == "__main__":
    unittest.main()
