"""Regression checks for the technical desktop preview's Streamlit iframe."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pages" / "99_Anteprima desktop.py"


class DesktopPreviewTests(unittest.TestCase):
    def test_preview_embeds_html_with_supported_iframe(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertNotIn("streamlit.components.v1", source)
        self.assertNotIn("components.html(", source)
        tree = ast.parse(source)
        calls = [
            node for node in tree.body
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "st"
            and node.value.func.attr == "iframe"
        ]
        self.assertEqual(len(calls), 1)
        call = calls[0].value
        self.assertEqual(len(call.args), 1)
        self.assertEqual(len(call.keywords), 1)
        self.assertEqual(call.keywords[0].arg, "height")
        self.assertIsInstance(call.keywords[0].value, ast.Name)
        self.assertEqual(call.keywords[0].value.id, "_PREVIEW_HEIGHT")

        # Compile the actual call with a minimal UI stub. The nested iframe
        # and resize script must keep their previous working behavior.
        for width in (390, 1280, 1440):
            with self.subTest(width=width):
                rendered = []
                scope = {
                    "st": SimpleNamespace(iframe=lambda html, **kw: rendered.append((html, kw))),
                    "_DESKTOP_WIDTH": width,
                    "_PREVIEW_HEIGHT": 920,
                }
                exec(compile(ast.Module(body=calls, type_ignores=[]),
                             str(PAGE), "exec"), scope)
                self.assertEqual(len(rendered), 1)
                html, kwargs = rendered[0]
                self.assertEqual(kwargs, {"height": 920})
                self.assertIn('id="mortem-desktop-frame"', html)
                self.assertIn(f"width: {width}px", html)
                self.assertIn(f"const desktopWidth = {width};", html)
                self.assertIn("const parentPath = window.parent.location.pathname;", html)
                self.assertIn("frame.src = `${parentPath}?frame=1`;", html)
                self.assertIn("new ResizeObserver(resizePreview).observe(shell);", html)
                self.assertIn('transform-origin: top left;', html)


if __name__ == "__main__":
    unittest.main()
