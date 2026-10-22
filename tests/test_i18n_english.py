"""Checks for translation coverage and scientific presentation invariants."""

from copy import deepcopy
import inspect
from string import Formatter
import unittest

from app import i18n, factor_ui_states as fs, surface_ui_states as surfaces
from app import tanatology_states as ts, special_tanatology_states as ss
from app.locales import en, en_factor, en_henssge, en_ui, it, it_factor, it_henssge, it_ui
from app.locales import en_msil, it_msil, en_perioral, it_perioral, en_supra, it_supra
from app.msil_tanatology import msil_livor_labels, msil_livor_legacy_value, msil_rigor_labels, msil_rigor_legacy_value


class EnglishResourcesTests(unittest.TestCase):
    def test_explicit_english_does_not_change_the_default(self):
        self.assertIs(i18n.get_locale(" EN "), en)
        self.assertEqual(i18n.language_label("en"), "English")
        self.assertEqual(i18n.ui_text("full.cooling_heading", "en"), "Postmortem body cooling")
        self.assertIs(i18n.get_locale(), it)
        self.assertEqual(i18n.ui_text("full.cooling_heading"), it_ui.UI_TEXT["full.cooling_heading"])

    def test_all_ui_keys_and_format_specifiers_are_present(self):
        self.assertEqual(set(it_ui.UI_TEXT), set(en_ui.UI_TEXT))
        def fields(value):
            return sorted((name, spec, conversion) for _, name, spec, conversion in Formatter().parse(value) if name is not None)
        for key in it_ui.UI_TEXT:
            with self.subTest(key=key):
                self.assertTrue(en_ui.UI_TEXT[key])
                self.assertEqual(fields(it_ui.UI_TEXT[key]), fields(en_ui.UI_TEXT[key]))
                self.assertEqual(i18n.ui_text(key, "en"), en_ui.UI_TEXT[key])
        self.assertIn("1.20", i18n.ui_text("full.fc_suggested", "en", value=1.2))
        self.assertIn("85 kg", i18n.ui_text("full.fc_adjusted_for_weight", "en", weight=85, base=1.1))

    def test_stable_label_ids_and_order_are_preserved(self):
        pairs = [
            (ts.LIVOR_LABEL_IT, en.LIVOR_LABEL_BY_ID),
            (ts.RIGOR_LABEL_IT, en.RIGOR_LABEL_BY_ID),
            (ss.SPECIAL_PARAM_LABEL_IT, en.SPECIAL_PARAM_LABEL_BY_ID),
            (fs.BODY_LABEL_IT, en.BODY_LABEL_BY_ID),
            (fs.WATER_LABEL_IT, en.WATER_LABEL_BY_ID),
            (fs.FULL_CLOTHING_LABEL_IT, en.FULL_CLOTHING_LABEL_BY_ID),
            (fs.MSIL_CLOTHING_LABEL_IT, en.MSIL_CLOTHING_LABEL_BY_ID),
            (surfaces.SURFACE_LABEL_IT, en.SURFACE_LABEL_BY_ID),
            (it_msil.MSIL_LIVOR_LABEL_BY_ID, en_msil.MSIL_LIVOR_LABEL_BY_ID),
            (it_msil.MSIL_RIGOR_LABEL_BY_ID, en_msil.MSIL_RIGOR_LABEL_BY_ID),
        ]
        pairs += [(labels, en.SPECIAL_OPTION_LABEL_BY_ID[param]) for param, labels in ss.SPECIAL_OPTION_LABEL_IT.items()]
        for source, translated in pairs:
            self.assertEqual(list(source), list(translated))
            self.assertEqual(len(set(translated.values())), len(translated))

    def test_msil_english_values_round_trip_to_existing_engine_labels(self):
        for label, state_id in zip(msil_livor_labels("en"), it_msil.MSIL_LIVOR_LABEL_BY_ID):
            self.assertEqual(msil_livor_legacy_value(label, "en"), ts.livor_legacy_label(state_id))
        for label, state_id in zip(msil_rigor_labels("en"), it_msil.MSIL_RIGOR_LABEL_BY_ID):
            self.assertEqual(msil_rigor_legacy_value(label, "en"), ts.rigor_legacy_label(state_id))

    def test_grid_intervals_are_identical_in_both_languages(self):
        self.assertEqual(en_perioral.PERIORAL_GRID_INTERVAL_BY_ID, it_perioral.PERIORAL_GRID_INTERVAL_BY_ID)
        self.assertEqual(list(en_supra.SUPRA_GRID_DETAIL_BY_ID), list(it_supra.SUPRA_GRID_DETAIL_BY_ID))
        for key, (_, interval) in it_supra.SUPRA_GRID_DETAIL_BY_ID.items():
            self.assertEqual(en_supra.SUPRA_GRID_DETAIL_BY_ID[key][1], interval)

    def test_every_current_finding_has_an_english_description(self):
        for state in ts.LIVOR_LABEL_IT:
            self.assertTrue(i18n.livor_description(state, "en"))
        for state in ts.RIGOR_LABEL_IT:
            self.assertTrue(i18n.rigor_description(state, "en"))
        for param in ss.SPECIAL_PARAM_LABEL_IT:
            self.assertTrue(i18n.special_graph_label(param, "en"))
            for option in ss.special_option_ids(param):
                with self.subTest(parameter=param, option=option):
                    self.assertTrue(i18n.special_option_label(param, option, "en"))
                    description = i18n.special_description(param, option, "en")
                    if option == ss.OPTION_NOT_ASSESSED:
                        self.assertIsNone(description)
                    else:
                        self.assertTrue(description)

    def test_locales_keep_public_rendering_call_signatures(self):
        def signature(fn):
            return [(p.name, p.kind, p.default) for p in inspect.signature(fn).parameters.values()]
        for source, translated in [(it, en), (it_henssge, en_henssge), (it_factor, en_factor)]:
            for name, fn in inspect.getmembers(source, inspect.isfunction):
                if name.startswith("_") or "legacy" in name or fn.__module__ != source.__name__:
                    continue
                target_name = name.removesuffix("_it")
                with self.subTest(function=target_name):
                    self.assertEqual(signature(fn), signature(getattr(translated, target_name)))

    def test_minimum_and_maximum_language_is_not_reversed(self):
        self.assertIn("more than 5 hours", i18n.simple_sentence_no_dt_over("5 hours", "en"))
        self.assertIn("no more than 5 hours", i18n.simple_sentence_no_dt_not_over("5 hours", "en"))
        text = i18n.potente_paragraph("43 hours", "1.8", high_temperature=True, language="en")
        for expected in ("above 23 °C", "limited case series", "minimum time since death", "at least 43 hours"):
            self.assertIn(expected, text)
        self.assertNotIn("confidence", text)
        for option in (ss.PERIORAL_MARKED, ss.PERIORAL_MODERATE, ss.PERIORAL_SLIGHT):
            self.assertIn("no more than 11 hours", i18n.special_description(ss.PARAM_ELECTRICAL_PERIORAL, option, "en"))
        for option, limit in (
            (ss.PUPILLARY_ATROPINE_DILATION, "less than 10 hours"),
            (ss.PUPILLARY_ATROPINE_NO_CHANGE, "at least 3 hours"),
            (ss.PUPILLARY_TROPICAMIDE_DILATION, "less than 30 hours"),
            (ss.PUPILLARY_TROPICAMIDE_NO_CHANGE, "at least 5 hours"),
            (ss.PUPILLARY_ACETYLCHOLINE_REDUCTION, "less than 46 hours"),
            (ss.PUPILLARY_ACETYLCHOLINE_NO_CHANGE, "at least 14 hours"),
        ):
            self.assertIn(limit, i18n.special_description(ss.PARAM_CHEMICAL_PUPILLARY, option, "en"))

    def test_qd_limits_and_status_wording(self):
        for low_ambient, threshold in ((True, "0.2"), (False, "0.5")):
            text = i18n.qd_summary(qd_text="0.18", ambient_at_most_23=low_ambient,
                                   threshold_text=threshold, within_limits=False, language="en")
            self.assertIn(f"Qd should be > {threshold}", text)
            self.assertIn("outside the range", text)
            self.assertIn("equals 1", text)
            self.assertIn("approaches 0", text)
        for status, phrase in (("all_optimal", "allow a sufficiently reliable estimate"),
                               ("mixed", "For some of the conditions"),
                               ("no_optimal_intermediate", "close to the lower limit"),
                               ("all_outside", "outside the range")):
            for single in (True, False):
                text = i18n.qd_range_summary(qd_min_text="0.18", qd_max_text="0.32",
                                             status=status, single_value=single, language="en")
                self.assertIn(phrase, text)
                self.assertIn("is 0.18" if single else "ranges from 0.18 to 0.32", text)

    def test_report_formatting_and_numbers(self):
        self.assertEqual(i18n.format_hours_minutes(1, 30, "en"), "1 hour 30 minutes")
        self.assertEqual(i18n.format_hours_minutes(0, 1, "en"), "1 minute")
        self.assertEqual(i18n.format_hours_range(2, 0, 3, 0, "en"), "between 2 and 3 hours")
        text = i18n.final_sentence_dt_range("between 2 and 4 hours", "10:25", "21.10.2026",
                                            "12:25", "21.10.2026", True, "en")
        self.assertIn("between 10:25 and 12:25 on 21.10.2026", text)
        self.assertIn("minimum and maximum time limits", text)
        for hours in (0, 0.5, 1, 1.5, 2, 2.999, 43):
            import re
            for formatter in ("prudent_hours_text", "prudent_graphing_hours_text"):
                english = getattr(en_henssge, formatter)(hours)
                italian = getattr(it_henssge, formatter)(hours)
                self.assertEqual(re.findall(r"\d+", english), re.findall(r"\d+", italian))

    def test_legacy_factor_values_are_read_without_mutation(self):
        summary = {"stato": "Immerso", "sottili": 1, "spessi": 0, "cop_medie": 0,
                   "cop_pesanti": 0, "superficie_key": "CONDUTTIVO", "correnti": "in acqua corrente",
                   "peso_adattato": True}
        before = deepcopy(summary)
        text = i18n.factor_correction_description(cf_value=0.35, summary=summary, language="en")
        for expected in ("0.35", "immersed body", "flowing water", "adjusted for body weight"):
            self.assertIn(expected, text)
        self.assertEqual(summary, before)
        self.assertEqual(i18n.factor_correction_description(cf_value=1.2, summary=summary,
                                                           manual_override=True, language="en"), "1.20")

    def test_scenario_text_is_escaped_without_changing_range(self):
        html = i18n.prudent_graphing_detail_list(header="Body cooling", ta_text="11–15 °C",
            cf_text="0.70–1.40", weight_text="85 kg", scenario_description="A < B & C", language="en")
        self.assertIn("A &lt; B &amp; C", html)
        self.assertIn("11–15 °C", html)
        self.assertNotIn("confidence", html)


if __name__ == "__main__":
    unittest.main()
