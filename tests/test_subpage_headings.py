"""Layout regression checks for subpage titles and mobile inspection controls."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SubpageHeadingsTests(unittest.TestCase):
    def test_all_subpages_use_the_same_heading_renderer(self):
        expected = {
            "pages/2_Tabelle di riferimento.py": 'render_page_heading("Metodi e tabelle di riferimento")',
            "pages/9_Reference.py": 'render_page_heading("Riferimenti bibliografici")',
            "pages/Impostazioni.py": 'render_page_heading("⚙️ Impostazioni")',
        }
        for path, title in expected.items():
            with self.subTest(path=path):
                source = (ROOT / path).read_text(encoding="utf-8")
                ast.parse(source)
                self.assertIn(title, source)
        helper = (ROOT / "app/page_heading.py").read_text(encoding="utf-8")
        self.assertIn("mortem-full-title mortem-subpage-title", helper)
        self.assertIn("font-weight: 650", helper)
        self.assertIn("1.15rem", helper)
        self.assertIn("text-transform: uppercase", helper)
        self.assertIn("margin-bottom: 0 !important", helper)
        # Only one st.html call: an extra CSS-only slot previously left a mobile gap.
        tree = ast.parse(helper)
        render = next(node for node in tree.body
                      if isinstance(node, ast.FunctionDef) and node.name == "render_page_heading")
        html_calls = [node for node in ast.walk(render)
                      if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                      and node.func.attr == "html"]
        self.assertEqual(len(html_calls), 1)

    def test_mobile_inspection_card_is_compact_without_touching_picker(self):
        main = (ROOT / "Stima_epoca_decesso.py").read_text(encoding="utf-8")
        self.assertIn('border=True, gap="small", key="full_inspection_card"', main)
        self.assertIn('padding: 0.55rem 0.65rem !important', main)
        self.assertNotIn('gap: 0.2rem !important', main)
        self.assertIn('.st-key-full_inspection_card', main)
        self.assertIn('iframe[data-testid="stCustomComponentV1"]', main)
        picker = (ROOT / "app/native_time_picker.py").read_text(encoding="utf-8")
        self.assertIn("highlight_missing=main_datetime", picker)

    def test_long_msil_title_can_wrap_at_home_font_size(self):
        shell = (ROOT / "app/mobile_shell.py").read_text(encoding="utf-8")
        self.assertIn("font-size: 1.15rem;", shell)
        self.assertIn("white-space: normal;", shell)
        self.assertIn('height: 100%;', shell)
        self.assertIn('padding: 2px 0 0;', shell)
        self.assertIn('text-transform: uppercase;', shell)
        self.assertIn('height=46 if msil_title', shell)
        msil = (ROOT / "disabled_pages/App_MSIL.py").read_text(encoding="utf-8")
        self.assertIn("install_minimal_mobile_shell(msil_title=True)", msil)
        self.assertIn('font-size:clamp(1.2rem,1.25vw,1.5rem)', msil)
        self.assertIn('text-transform:uppercase!important', msil)
        panel = (ROOT / "app/fc_panel_frontend/panel.css").read_text(encoding="utf-8")
        scenarios = (ROOT / "app/fc_panel_frontend/scenarios.css").read_text(encoding="utf-8")
        self.assertIn("text-transform:uppercase;margin:0", panel)
        self.assertIn(".scenario-toolbar{margin:0 0 6px}", scenarios)


if __name__ == "__main__":
    unittest.main()
