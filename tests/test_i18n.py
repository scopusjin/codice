# -*- coding: utf-8 -*-

import unittest

from app import i18n
from app.locales import it
from app.special_tanatology_states import (
    PARAM_ELECTRICAL_SUPRACILIARY,
    SUPRA_PHASE_I,
)
from app.tanatology_states import LIVOR_ABSENT, RIGOR_FULL


class I18nItalianOnlyTests(unittest.TestCase):
    def test_default_and_supported_languages(self):
        self.assertEqual(i18n.DEFAULT_LANGUAGE, "it")
        self.assertEqual(i18n.SUPPORTED_LANGUAGES, ("it",))
        self.assertEqual(i18n.normalize_language(), "it")
        self.assertEqual(i18n.normalize_language(""), "it")
        self.assertEqual(i18n.normalize_language("IT"), "it")

    def test_get_locale_returns_exact_italian_module(self):
        self.assertIs(i18n.get_locale(), it)
        self.assertIs(i18n.get_locale("it"), it)
        self.assertEqual(i18n.language_label("it"), "Italiano")

    def test_language_neutral_labels_match_current_italian_labels(self):
        self.assertEqual(
            i18n.livor_label(LIVOR_ABSENT),
            it.LIVOR_LABEL_IT[LIVOR_ABSENT],
        )
        self.assertEqual(
            i18n.rigor_label(RIGOR_FULL),
            it.RIGOR_LABEL_IT[RIGOR_FULL],
        )
        self.assertEqual(
            i18n.special_parameter_label(PARAM_ELECTRICAL_SUPRACILIARY),
            it.SPECIAL_PARAM_LABEL_IT[PARAM_ELECTRICAL_SUPRACILIARY],
        )
        self.assertEqual(
            i18n.special_option_label(PARAM_ELECTRICAL_SUPRACILIARY, SUPRA_PHASE_I),
            it.SPECIAL_OPTION_LABEL_IT[PARAM_ELECTRICAL_SUPRACILIARY][SUPRA_PHASE_I],
        )

    def test_language_neutral_helpers_match_italian_locale(self):
        self.assertEqual(
            i18n.livor_description(LIVOR_ABSENT),
            it.livor_description_it(LIVOR_ABSENT),
        )
        self.assertEqual(
            i18n.rigor_description(RIGOR_FULL),
            it.rigor_description_it(RIGOR_FULL),
        )
        self.assertEqual(
            i18n.special_description(PARAM_ELECTRICAL_SUPRACILIARY, SUPRA_PHASE_I),
            it.special_description_it(PARAM_ELECTRICAL_SUPRACILIARY, SUPRA_PHASE_I),
        )
        self.assertEqual(
            i18n.special_graph_label(PARAM_ELECTRICAL_SUPRACILIARY),
            it.special_graph_label_it(PARAM_ELECTRICAL_SUPRACILIARY),
        )

    def test_unknown_ids_preserve_mapping_key_errors(self):
        with self.assertRaises(KeyError):
            i18n.livor_label("unknown")
        with self.assertRaises(KeyError):
            i18n.rigor_label("unknown")
        with self.assertRaises(KeyError):
            i18n.special_parameter_label("unknown")
        with self.assertRaises(KeyError):
            i18n.special_option_label(PARAM_ELECTRICAL_SUPRACILIARY, "unknown")

    def test_unsupported_language_is_rejected(self):
        with self.assertRaises(ValueError):
            i18n.get_locale("en")


if __name__ == "__main__":
    unittest.main()
