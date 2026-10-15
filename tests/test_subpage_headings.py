"""Layout regression checks for subpage titles and mobile inspection controls."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SubpageHeadingsTests(unittest.TestCase):
    def test_all_subpages_use_the_same_heading_renderer(self):
        expected = {
            "pages/2_Tabelle di riferimento.py": 'render_page_heading("Tabelle di riferimento")',
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

    def test_mobile_inspection_card_is_compact_without_touching_picker(self):
        main = (ROOT / "Stima_epoca_decesso.py").read_text(encoding="utf-8")
        self.assertIn('border=True, gap="xsmall", key="full_inspection_card"', main)
        self.assertIn('.st-key-full_inspection_card', main)
        self.assertIn('iframe[data-testid="stCustomComponentV1"]', main)
        picker = (ROOT / "app/native_time_picker.py").read_text(encoding="utf-8")
        self.assertIn("highlight_missing=main_datetime", picker)

    def test_long_msil_title_can_wrap_at_home_font_size(self):
        shell = (ROOT / "app/mobile_shell.py").read_text(encoding="utf-8")
        self.assertIn("font-size: 1.15rem;", shell)
        self.assertIn("white-space: normal;", shell)
        self.assertIn('height=46 if msil_title', shell)
        msil = (ROOT / "pages/App_MSIL.py").read_text(encoding="utf-8")
        self.assertIn("install_minimal_mobile_shell(msil_title=True)", msil)
        self.assertIn('font-size:clamp(1.2rem,1.25vw,1.5rem)', msil)


if __name__ == "__main__":
    unittest.main()
