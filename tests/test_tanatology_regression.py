# -*- coding: utf-8 -*-
"""Test di regressione per range e testi tanatologici critici."""

import datetime
import unittest

import numpy as np

from app.locales.it import RIGOR_DESCRIPTION_IT_BY_ID, SPECIAL_DESCRIPTION_IT_BY_ID
from app.parameters import INF_HOURS, dati_parametri_aggiuntivi
from app.special_tanatology_states import (
    OPTION_NO_REACTION,
    PARAM_CHEMICAL_PUPILLARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_MECHANICAL_MUSCLE,
    PUPILLARY_NEGATIVE,
)
from app.tanatology_states import RIGOR_ABSENT
from app.textgen import (
    build_final_sentence,
    build_final_sentence_simple,
    build_simple_sentence,
    build_simple_sentence_no_dt,
)


class ScientificRangeRegressionTests(unittest.TestCase):
    def test_supraciliary_ranges_are_unchanged(self):
        ranges = dati_parametri_aggiuntivi["Eccitabilità elettrica sopraciliare"]["range"]
        self.assertEqual(ranges["Fase VI"], (1, 6))
        self.assertEqual(ranges["Fase V"], (2, 7))
        self.assertEqual(ranges["Fase IV"], (3, 8))
        self.assertEqual(ranges["Fase III"], (3.5, 13))
        self.assertEqual(ranges["Fase II"], (5, 16))
        self.assertEqual(ranges["Fase I"], (5, 22))
        self.assertEqual(ranges["Nessuna reazione"], (5, INF_HOURS))

    def test_perioral_ranges_are_unchanged(self):
        ranges = dati_parametri_aggiuntivi["Eccitabilità elettrica peribuccale"]["range"]
        self.assertEqual(ranges["Muscoli facciali (+++)"], (0, 11))
        self.assertEqual(ranges["Muscoli peribuccali (++)"], (0, 11))
        self.assertEqual(ranges["Reazione focale (+)"], (0, 11))
        self.assertEqual(ranges["Nessuna reazione"], (3, INF_HOURS))

    def test_mechanical_and_pupillary_ranges_are_unchanged(self):
        mechanical = dati_parametri_aggiuntivi["Eccitabilità muscolare meccanica"]["range"]
        self.assertEqual(mechanical["Contrazione dell’intero muscolo"], (0, 2.5))
        self.assertEqual(mechanical["Tumefazione reversibile"], (0, 5))
        self.assertEqual(mechanical["Piccola tumefazione persistente"], (0, 12))
        self.assertEqual(mechanical["Nessuna reazione"], (1.5, INF_HOURS))

        pupillary = dati_parametri_aggiuntivi["Eccitabilità chimica pupillare"]["range"]
        self.assertEqual(pupillary["Dilatazione con atropina"], (0, 10))
        self.assertEqual(pupillary["Nessuna variazione con atropina"], (3, INF_HOURS))
        self.assertEqual(pupillary["Dilatazione con tropicamide"], (0, 30))
        self.assertEqual(pupillary["Nessuna variazione con tropicamide"], (5, INF_HOURS))
        self.assertEqual(pupillary["Riduzione con acetilcolina"], (0, 46))
        self.assertEqual(pupillary["Nessuna variazione con acetilcolina"], (14, INF_HOURS))


class ItalianTextRegressionTests(unittest.TestCase):
    def test_rigor_keeps_requested_spacing(self):
        self.assertIn("2 - 3 ore", RIGOR_DESCRIPTION_IT_BY_ID[RIGOR_ABSENT])

    def test_negative_pupillary_response_has_no_dilation(self):
        text = SPECIAL_DESCRIPTION_IT_BY_ID[PARAM_CHEMICAL_PUPILLARY][PUPILLARY_NEGATIVE]
        self.assertIn("senza aumento del diametro della pupilla", text)
        self.assertNotIn("(con aumento del diametro della pupilla)", text)

    def test_supraciliary_no_reaction_ends_with_period(self):
        text = SPECIAL_DESCRIPTION_IT_BY_ID[PARAM_ELECTRICAL_SUPRACILIARY][OPTION_NO_REACTION]
        self.assertTrue(text.endswith("."))

    def test_short_sentences_cover_all_three_range_shapes(self):
        not_over = build_simple_sentence_no_dt(0, 6)
        over = build_simple_sentence_no_dt(5, np.inf)
        interval = build_simple_sentence_no_dt(2, 7)

        self.assertIn("<b>non oltre 6 ore prima</b>", not_over)
        self.assertIn("<b>oltre 5 ore prima</b>", over)
        self.assertIn("<b>tra 2 e 7 ore prima</b>", interval)

    def test_datetime_sentences_use_vale_a_dire(self):
        inspection = datetime.datetime(2026, 8, 23, 10, 0)

        interval = build_simple_sentence(2, 7, inspection)
        over = build_simple_sentence(5, np.inf, inspection)
        not_over = build_simple_sentence(0, 6, inspection)

        for text in (interval, over, not_over):
            self.assertIn("vale a dire", text)
            self.assertNotIn("ovvero", text.lower())

        self.assertIn("tra le ore 03:00 e le ore 08:00 del 23.08.2026", interval)
        self.assertIn("prima delle ore 05:00 del 23.08.2026", over)
        self.assertIn("successivamente alle ore 04:00 del 23.08.2026", not_over)
        self.assertIn("prima delle ore 10:00 del 23.08.2026", not_over)

    def test_final_sentences_cover_all_three_range_shapes(self):
        inspection = datetime.datetime(2026, 8, 23, 10, 0)

        self.assertIn("oltre 5 ore prima", build_final_sentence(5, np.inf, inspection))
        self.assertIn("non oltre 6 ore prima", build_final_sentence(0, 6, inspection))
        self.assertIn("tra 2 e 7 ore prima", build_final_sentence(2, 7, inspection))

        self.assertIn("oltre 5 ore prima", build_final_sentence_simple(5, np.inf))
        self.assertIn("non oltre 6 ore prima", build_final_sentence_simple(0, 6))
        self.assertIn("tra 2 e 7 ore prima", build_final_sentence_simple(2, 7))


if __name__ == "__main__":
    unittest.main()
