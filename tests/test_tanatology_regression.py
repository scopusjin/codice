# -*- coding: utf-8 -*-
"""Test di regressione per range e testi tanatologici critici."""

import datetime
import unittest

import numpy as np

from app.locales.it import (
    LIVOR_DESCRIPTION_IT_BY_ID, LIVOR_PRESSURE_DESCRIPTION_IT_BY_ID,
    RIGOR_DESCRIPTION_IT_BY_ID, SPECIAL_DESCRIPTION_IT_BY_ID,
)
from app.livor_digitopressione import PRESSURE_COMPLETE_FADING, PRESSURE_INCOMPLETE_FADING
from app.locales.it_supra import SUPRA_GRID_DETAIL_BY_ID
from app.parameters import INF_HOURS, dati_parametri_aggiuntivi, opzioni_macchie, macchie_medi
from app.special_tanatology_states import (
    OPTION_NO_REACTION,
    PARAM_CHEMICAL_PUPILLARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_MECHANICAL_MUSCLE,
    MECH_WHOLE_MUSCLE,
    MECH_REVERSIBLE_SWELLING,
    MECH_SMALL_PERSISTENT_SWELLING,
    PERIORAL_MARKED,
    PERIORAL_MODERATE,
    PERIORAL_SLIGHT,
    PUPILLARY_NEGATIVE,
    SUPRA_PHASE_I,
    SUPRA_PHASE_II,
    SUPRA_PHASE_III,
    SUPRA_PHASE_IV,
    SUPRA_PHASE_V,
    SUPRA_PHASE_VI,
)
from app.tanatology_states import (
    LIVOR_CONFLUING, LIVOR_CONFLUENT, LIVOR_CONFLUENT_FULLY_MIGRATABLE, RIGOR_ABSENT,
)
from app.textgen import (
    build_final_sentence,
    build_final_sentence_simple,
    build_simple_sentence,
    build_simple_sentence_no_dt,
)


class ScientificRangeRegressionTests(unittest.TestCase):
    def test_livor_confluence_has_no_positive_lower_bound(self):
        self.assertEqual(opzioni_macchie["In via di confluenza"], (0, 4))
        self.assertEqual(macchie_medi["In via di confluenza"], (1.5, 3.5))
        description = LIVOR_DESCRIPTION_IT_BY_ID[LIVOR_CONFLUING]
        self.assertIn("meno di 4 ore", description)
        self.assertNotIn("più di 1 ora", description)

    def test_confluent_livor_text_matches_combined_interval(self):
        self.assertEqual(opzioni_macchie["Confluenti (migrabilità non valutata)"][:1], (1,))
        self.assertEqual(opzioni_macchie["Confluenti e completamente migrabili"], (1, 6))
        self.assertIsNone(macchie_medi["Confluenti e completamente migrabili"])
        self.assertIn("almeno un’ora", LIVOR_DESCRIPTION_IT_BY_ID[LIVOR_CONFLUENT])
        self.assertIn("tra 1 e 6 ore", LIVOR_DESCRIPTION_IT_BY_ID[LIVOR_CONFLUENT_FULLY_MIGRATABLE])

    def test_livor_pressure_descriptions_explain_scientific_bounds(self):
        full = LIVOR_PRESSURE_DESCRIPTION_IT_BY_ID[PRESSURE_COMPLETE_FADING]
        incomplete = LIVOR_PRESSURE_DESCRIPTION_IT_BY_ID[PRESSURE_INCOMPLETE_FADING]
        self.assertIn("completamente", full)
        self.assertIn("limite massimo di 20 ore", full)
        self.assertIn("non scomparivano completamente", incomplete)
        self.assertIn("limite minimo di 1 ora", incomplete)

    def test_supraciliary_ranges_match_integrated_limits(self):
        ranges = dati_parametri_aggiuntivi["Eccitabilità elettrica sopraciliare"]["range"]
        self.assertEqual(ranges["Fase VI"], (0, 6))
        self.assertEqual(ranges["Fase V"], (1, 7))
        self.assertEqual(ranges["Fase IV"], (2, 8))
        self.assertEqual(ranges["Fase III"], (3, 13))
        self.assertEqual(ranges["Fase II"], (3.5, 16))
        self.assertEqual(ranges["Fase I"], (5, 22))
        self.assertEqual(ranges["Nessuna reazione"], (5, INF_HOURS))

    def test_supraciliary_image_captions_match_integrated_limits(self):
        expected = {
            SUPRA_PHASE_VI: "<6 h",
            SUPRA_PHASE_V: ">1 h; <7 h",
            SUPRA_PHASE_IV: ">2 h; <8 h",
            SUPRA_PHASE_III: ">3 h; <13 h",
            SUPRA_PHASE_II: ">3½ h; <16 h",
            SUPRA_PHASE_I: ">5 h; <22 h",
        }
        for option_id, interval in expected.items():
            self.assertEqual(SUPRA_GRID_DETAIL_BY_ID[option_id][1], interval)


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
        self.assertEqual(mechanical["Piccola tumefazione persistente"], (0, 13))
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

    def test_supraciliary_phase_v_description_matches_engine(self):
        interval = dati_parametri_aggiuntivi["Eccitabilità elettrica sopraciliare"]["range"]["Fase V"]
        self.assertEqual(interval, (1, 7))
        description = SPECIAL_DESCRIPTION_IT_BY_ID[PARAM_ELECTRICAL_SUPRACILIARY][SUPRA_PHASE_V]
        self.assertIn("più di 1 ora e meno di 7 ore", description)
        self.assertNotIn("tra le 2 e le 7 ore", description)

    def test_supraciliary_no_reaction_ends_with_period(self):
        text = SPECIAL_DESCRIPTION_IT_BY_ID[PARAM_ELECTRICAL_SUPRACILIARY][OPTION_NO_REACTION]
        self.assertTrue(text.endswith("."))

    def test_perioral_descriptions_explain_henssge_binary_choice(self):
        perioral = SPECIAL_DESCRIPTION_IT_BY_ID[PARAM_ELECTRICAL_PERIORAL]
        for option in (PERIORAL_MARKED, PERIORAL_MODERATE, PERIORAL_SLIGHT):
            text = perioral[option]
            self.assertIn("metodo integrato di Henssge", text)
            self.assertIn("indipendentemente dalla sua estensione", text)
            self.assertIn("non fossero trascorse più di 11 ore", text)
            self.assertNotIn("metodo meno recente", text)
        self.assertIn("metodo integrato di Henssge", perioral[OPTION_NO_REACTION])
        self.assertIn("fossero trascorse più di 3 ore", perioral[OPTION_NO_REACTION])

    def test_mechanical_descriptions_match_operational_limits(self):
        whole = SPECIAL_DESCRIPTION_IT_BY_ID[PARAM_MECHANICAL_MUSCLE][MECH_WHOLE_MUSCLE]
        reversible = SPECIAL_DESCRIPTION_IT_BY_ID[PARAM_MECHANICAL_MUSCLE][MECH_REVERSIBLE_SWELLING]
        persistent = SPECIAL_DESCRIPTION_IT_BY_ID[PARAM_MECHANICAL_MUSCLE][MECH_SMALL_PERSISTENT_SWELLING]

        self.assertIn("non fossero trascorse più di 2 ore e 30 minuti", whole)
        self.assertIn("non fossero trascorse più di 5 ore", reversible)
        self.assertIn("non fossero trascorse più di 13 ore", persistent)
        self.assertNotIn("24 ore", persistent)

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
        self.assertIn("tra le ore 04:00 e le 10:00 del 23.08.2026", not_over)
        self.assertNotIn("successivamente alle ore", not_over)
        # The short result summary intentionally bolds its heading;
        # the "not over" estimate itself must remain plain text.
        self.assertIn("<b>EPOCA DEL DECESSO STIMATA:</b>", not_over)
        self.assertEqual(not_over.count("<b>"), 1)

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
