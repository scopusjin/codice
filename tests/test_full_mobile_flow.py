# -*- coding: utf-8 -*-

import ast
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

import app.decimal_number_input_v2 as decimal_v2
from app.mobile_shell import (
    _HOST_CHROME_HTML, _MINIMAL_APP_CHROME_CSS,
    _MINIMAL_MOBILE_SHELL_CSS, _MOBILE_HEADER_HTML,
)


class FullMobileFlowTests(unittest.TestCase):
    def _mobile_app(self):
        # Ogni AppTest possiede un registro componenti separato.
        decimal_v2._renderer = None
        script = Path(__file__).resolve().parents[1] / "Stima_epoca_decesso.py"
        app = AppTest.from_file(str(script), default_timeout=20)
        app.session_state["__full_device_mobile"] = True
        app.run(timeout=20)
        return app

    def test_primary_cards_have_native_compact_gap_on_mobile_only(self):
        source = (Path(__file__).resolve().parents[1] / "Stima_epoca_decesso.py").read_text(encoding="utf-8")
        self.assertIn('st.container(gap="xsmall", key="full_mobile_primary_cards")', source)
        self.assertIn('if full_device_is_mobile() else st', source)
        for card in ("full_inspection_card", "full_cooling_card", "full_signs_card"):
            self.assertIn(f'with primary_cards.container(border=True, key="{card}"):', source)
        self.assertIn("primary_cards.warning(warning)", source)
        self.assertIn("primary_cards.caption(warning)", source)
        ast.parse(source)

    def test_mobile_navigation_uses_sidebar_only(self):
        app = self._mobile_app()

        self.assertEqual([str(item) for item in app.exception], [])
        self.assertNotIn("Modalità sopralluogo", [button.label for button in app.button])
        self.assertIn(
            "Dati tanatologici aggiuntivi",
            [toggle.label for toggle in app.toggle],
        )

    def test_host_chrome_uses_hidden_javascript_html(self):
        # The injected bridge must not create a second iframe or reserve
        # space above the already-tested mobile header.
        script = Path(__file__).resolve().parents[1] / "app" / "mobile_shell.py"
        source = script.read_text(encoding="utf-8")
        module = ast.parse(source)
        install = next(
            node for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "install_minimal_app_chrome"
        )
        calls = [
            node for node in ast.walk(install)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "st"
            and node.func.attr == "html"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id == "_HOST_CHROME_HTML"
        ]
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            {option.arg: ast.literal_eval(option.value) for option in calls[0].keywords},
            {"unsafe_allow_javascript": True},
        )
        self.assertFalse(any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "iframe"
            for node in ast.walk(install)
        ))
        self.assertNotIn("components.html(", source)
        self.assertIn(".st-key-mortem_host_chrome", _MINIMAL_APP_CHROME_CSS)
        self.assertIn("display: none !important", _MINIMAL_APP_CHROME_CSS)
        self.assertIn("let host = window;", _HOST_CHROME_HTML)
        self.assertNotIn("let host = window.parent;", _HOST_CHROME_HTML)
        self.assertIn("const doc = host.document", _HOST_CHROME_HTML)
        self.assertIn("catch (_)", _HOST_CHROME_HTML)

    def test_mobile_styles_load_before_header_without_markdown_spacers(self):
        # The first-load mobile CSS must be registered before any visual
        # element, rather than generating a blank Markdown row.
        shell = Path(__file__).resolve().parents[1] / "app" / "mobile_shell.py"
        tree = ast.parse(shell.read_text(encoding="utf-8"))
        install = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "install_minimal_mobile_shell"
        )
        html_calls = [
            node for node in ast.walk(install)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "st"
            and node.func.attr == "html"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id == "_MINIMAL_MOBILE_SHELL_CSS"
        ]
        self.assertEqual(len(html_calls), 1)
        self.assertFalse(any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "markdown"
            and any(isinstance(arg, ast.Name) and arg.id == "_MINIMAL_MOBILE_SHELL_CSS"
                    for arg in node.args)
            for node in ast.walk(install)
        ))
        first_css_line = html_calls[0].lineno
        host_setup_line = next(
            node.lineno for node in ast.walk(install)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "install_minimal_app_chrome"
        )
        header_line = next(
            node.lineno for node in ast.walk(install)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "iframe"
        )
        self.assertLess(first_css_line, host_setup_line)
        self.assertLess(host_setup_line, header_line)

        # The existing Full-specific CSS rules must still be included, but
        # mobile-only style content must go through the zero-spacing st.html.
        compact = (
            Path(__file__).resolve().parents[1] / "app" / "full_mobile_compact.py"
        ).read_text(encoding="utf-8")
        self.assertIn('body = body + _FULL_MOBILE_COMPACT_CSS', compact)
        self.assertIn('if st.session_state.get("__full_device_mobile", False) and not args:', compact)
        self.assertIn('return st.html(body)', compact)
        app = self._mobile_app()
        self.assertEqual([str(item) for item in app.exception], [])

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

    def test_mobile_header_uses_supported_iframe_with_fixed_height(self):
        # This is the header only: the host-chrome bridge is a separate change.
        script = Path(__file__).resolve().parents[1] / "app" / "mobile_shell.py"
        module = ast.parse(script.read_text(encoding="utf-8"))
        install = next(
            node for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "install_minimal_mobile_shell"
        )
        calls = [
            node for node in ast.walk(install)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "st"
            and node.func.attr == "iframe"
        ]
        self.assertEqual(len(calls), 1)
        header = calls[0]
        self.assertEqual(len(header.args), 1)
        self.assertIsInstance(header.args[0], ast.Name)
        self.assertEqual(header.args[0].id, "_MOBILE_HEADER_HTML")
        self.assertEqual(
            {option.arg: ast.literal_eval(option.value) for option in header.keywords},
            {"height": 34},
        )
        self.assertIn("menu.addEventListener(\"click\", openSidebar)", _MOBILE_HEADER_HTML)
        self.assertIn("title.textContent = source.textContent.trim()", _MOBILE_HEADER_HTML)

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

    def test_mobile_fc_suggestion_opens_dedicated_component(self):
        app = self._mobile_app()
        app.session_state["stima_cautelativa_beta"] = True
        app.session_state["__prudent_explicit_ranges_initialized"] = True
        app.session_state["range_unico_beta"] = True
        app.session_state["toggle_fattore_inline"] = True
        app.session_state["toggle_fattore"] = True
        app.session_state["__full_fc_suggest_target"] = "range"
        app.run(timeout=20)

        self.assertEqual([str(item) for item in app.exception], [])
        self.assertTrue(app.session_state["__fc_active"])
        self.assertEqual(len(app.get("component_instance")), 1)
        self.assertNotIn("Procedi con la stima", [button.label for button in app.button])
        html = (Path(__file__).resolve().parents[1] / "app/fc_panel_frontend/index.html").read_text()
        self.assertIn('id="use"', html)
        self.assertIn('id="restore"', html)


if __name__ == "__main__":
    unittest.main()
