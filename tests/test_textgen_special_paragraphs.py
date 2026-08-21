# -*- coding: utf-8 -*-

import unittest

from app.special_tanatology_states import (
    OPTION_NO_REACTION,
    OPTION_UNRELIABLE,
)
from app.textgen import paragrafi_parametri_aggiuntivi


class TextgenSpecialParagraphRegressionTests(unittest.TestCase):
    def test_legacy_reportable_output_is_unchanged(self):
        params = [{
            "nome": "Eccitabilità elettrica sopraciliare",
            "stato": "Nessuna reazione",
            "descrizione": "Test descrizione",
        }]
        self.assertEqual(
            paragrafi_parametri_aggiuntivi(parametri=params),
            ["<ul><li>Test descrizione</li></ul>"],
        )

    def test_legacy_non_reportable_outputs_are_unchanged(self):
        params = [
            {"stato": "Non valutata", "descrizione": "A"},
            {"stato": "Non valutabile/non attendibile", "descrizione": "B"},
        ]
        self.assertEqual(paragrafi_parametri_aggiuntivi(parametri=params), [])

    def test_stable_ids_produce_same_html(self):
        reportable = [{
            "stato_id": OPTION_NO_REACTION,
            "stato": "Nessuna reazione",
            "descrizione": "Test descrizione",
        }]
        unreliable = [{
            "stato_id": OPTION_UNRELIABLE,
            "stato": "Nessuna reazione",
            "descrizione": "Non mostrare",
        }]
        self.assertEqual(
            paragrafi_parametri_aggiuntivi(parametri=reportable),
            ["<ul><li>Test descrizione</li></ul>"],
        )
        self.assertEqual(paragrafi_parametri_aggiuntivi(parametri=unreliable), [])


if __name__ == "__main__":
    unittest.main()
