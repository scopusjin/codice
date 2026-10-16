# -*- coding: utf-8 -*-
"""Layout compatto delle ipostasi e simboli FC desktop/mobile."""

from contextlib import nullcontext
from pathlib import Path
import re
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.livor_picker import render_livor_picker
from app.livor_digitopressione import (
    PRESSURE_KEY, PRESSURE_VISIBILITY_KEY, PRESSURE_COMPLETE_FADING,
    render_livor_pressure_input,
)
from app.tanatology_states import LIVOR_FULLY_MIGRATABLE


class FakeStreamlit:
    def __init__(self, state=None):
        self.session_state = dict(state or {})
        self.containers = []
        self.selectboxes = []
        self.captions = []
        self.css = []

    def get_option(self, key):
        return "light" if key == "theme.base" else None

    def html(self, markup):
        self.css.append(markup)

    def container(self, **kwargs):
        self.containers.append(kwargs)
        return nullcontext()

    def caption(self, label):
        self.captions.append(label)

    def selectbox(self, label, options, **kwargs):
        self.selectboxes.append((label, tuple(options), kwargs))
        return self.session_state[kwargs["key"]]


class CompactLivorPickerTests(unittest.TestCase):
    def test_native_dropdown_has_all_options_and_original_state_key(self):
        choices = ("Non valutate", "Non ancora comparse", "Confluite e completamente migrabili")
        for key in ("selettore_macchie_ui", "selettore_macchie_mobile"):
            with self.subTest(key=key):
                fake = FakeStreamlit({key: choices[-1]})
                from app import livor_picker
                with patch.dict(sys.modules, {"streamlit": fake}), \\
                        patch.object(livor_picker, "_native_select", return_value=choices[-1]) as component:
                    result = render_livor_picker(
                        choices, state_key=key, picker_key="livor_picker_test",
                    )
                self.assertEqual(result, choices[-1])
                kwargs = component.call_args.kwargs
                self.assertEqual(kwargs["options"], list(choices))
                self.assertEqual(kwargs["value"], choices[-1])
                self.assertEqual(kwargs["key"], "livor_picker_test")
                self.assertEqual(fake.session_state[key], choices[-1])
                self.assertEqual(set(fake.session_state), {key})

    def test_recovered_case_uses_new_component_instance(self):
        choices = ("Non valutate", "Fisse")
        fake = FakeStreamlit({"selettore_macchie_ui": "Fisse", "__case_ui_id": "new-case"})
        from app import livor_picker
        with patch.dict(sys.modules, {"streamlit": fake}), \\
                patch.object(livor_picker, "_native_select", return_value=None) as component:
            selected = render_livor_picker(
                choices, state_key="selettore_macchie_ui", picker_key="livor_picker_test",
            )
        self.assertEqual(selected, "Fisse")
        self.assertEqual(component.call_args.kwargs["key"], "livor_picker_test_new-case")
        self.assertEqual(fake.session_state["selettore_macchie_ui"], "Fisse")

    def test_user_choice_updates_existing_state_key(self):
        fake = FakeStreamlit({"selettore_macchie_ui": "Non valutate"})
        from app import livor_picker
        with patch.dict(sys.modules, {"streamlit": fake}), \\
                patch.object(livor_picker, "_native_select", return_value="Fisse"):
            selected = render_livor_picker(
                ("Non valutate", "Fisse"),
                state_key="selettore_macchie_ui",
                picker_key="livor_picker_test",
            )
        self.assertEqual(selected, "Fisse")
        self.assertEqual(fake.session_state["selettore_macchie_ui"], "Fisse")

    def test_initial_value_and_invalid_component_result_are_safe(self):
        fake = FakeStreamlit()
        from app import livor_picker
        with patch.dict(sys.modules, {"streamlit": fake}), \\
                patch.object(livor_picker, "_native_select", return_value="unknown"):
            chosen = render_livor_picker(
                ("Non valutate", "Fisse"),
                state_key="selettore_macchie_ui",
                picker_key="livor_picker_test",
                default_label="Fisse",
            )
        self.assertEqual(chosen, "Fisse")
        self.assertEqual(fake.session_state["selettore_macchie_ui"], "Fisse")

    def test_browser_native_options_overlay_without_streamlit_popover(self):
        repo = Path(__file__).resolve().parents[1]
        html = (repo / "app/livor_picker_frontend/index.html").read_text(encoding="utf-8")
        self.assertIn('<select id="livor-choice"', html)
        self.assertIn("new Option(value, value)", html)
        self.assertIn("streamlit:setComponentValue", html)
        self.assertIn("streamlit:setFrameHeight", html)
        self.assertIn("appearance: auto", html)
        self.assertIn("font: 400 13px", html)
        self.assertNotIn('type="radio"', html)

    def test_digitopressione_is_compact_and_slightly_indented(self):
        fake = FakeStreamlit({
            PRESSURE_VISIBILITY_KEY: True,
            PRESSURE_KEY: PRESSURE_COMPLETE_FADING,
        })
        with patch.dict(sys.modules, {"streamlit": fake}):
            value = render_livor_pressure_input(
                LIVOR_FULLY_MIGRATABLE, "Scomparsa alla digitopressione?",
            )
        self.assertEqual(value, PRESSURE_COMPLETE_FADING)
        self.assertEqual(fake.captions, ["Scomparsa alla digitopressione?"])
        self.assertEqual(fake.containers[0]["key"], "livor_pressure_subquestion")
        self.assertIsNone(fake.containers[0]["gap"])
        self.assertIn("padding-left: 0.75rem", fake.css[0])
        self.assertEqual(fake.selectboxes[0][2]["key"], PRESSURE_KEY)
        self.assertEqual(fake.selectboxes[0][2]["label_visibility"], "collapsed")

    def test_digitopressione_remains_hidden_when_disabled(self):
        fake = FakeStreamlit({PRESSURE_VISIBILITY_KEY: False})
        with patch.dict(sys.modules, {"streamlit": fake}):
            render_livor_pressure_input(LIVOR_FULLY_MIGRATABLE, "Scomparsa alla digitopressione?")
        self.assertEqual(fake.selectboxes, [])
        self.assertEqual(fake.captions, [])


class DesktopFCIconsTests(unittest.TestCase):
    def test_desktop_shows_existing_mobile_clothing_and_blanket_svg(self):
        repo = Path(__file__).resolve().parents[1]
        html = (repo / "app/fc_panel_frontend/index.html").read_text(encoding="utf-8")
        css = (repo / "app/fc_panel_frontend/panel.css").read_text(encoding="utf-8")
        legend = re.search(r'<legend class="desktop-coverings-legend"[^>]*>(.*?)</legend>', html, re.S)
        self.assertIsNotNone(legend)
        sources = re.findall(r'<span class="covering-icons"[^>]*>(.*?)</span>', html, re.S)
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0], sources[1])
        self.assertEqual(sources[0].count("<svg"), 2)
        self.assertIn("#fc-full .desktop-coverings-legend{display:none}", css)
        self.assertIn("#fc-full[data-desktop=true] .desktop-coverings-legend{display:block", css)
        self.assertIn("#fc-full[data-desktop=true] #counts .category{display:none}", css)


if __name__ == "__main__":
    unittest.main()
