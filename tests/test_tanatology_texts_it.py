# -*- coding: utf-8 -*-

import unittest

from app.parameters import (
    testi_macchie,
    rigidita_descrizioni,
    dati_parametri_aggiuntivi,
    nomi_brevi,
)
from app.tanatology_states import LIVOR_LABEL_IT, RIGOR_LABEL_IT
from app.special_tanatology_states import SPECIAL_PARAM_LABEL_IT, SPECIAL_OPTION_LABEL_IT
from app.tanatology_texts_it import (
    LIVOR_DESCRIPTION_IT_BY_ID,
    RIGOR_DESCRIPTION_IT_BY_ID,
    SPECIAL_DESCRIPTION_IT_BY_ID,
    SPECIAL_GRAPH_LABEL_IT_BY_ID,
    TESTI_MACCHIE_LEGACY,
    RIGIDITA_DESCRIZIONI_LEGACY,
    SPECIAL_DESCRIPTIONS_LEGACY_BY_PARAM_LABEL,
    NOMI_BREVI_LEGACY,
)


class TanatologyItalianTextsCompatibilityTests(unittest.TestCase):
    def test_livor_descriptions_match_legacy_exactly(self):
        expected = {
            state_id: testi_macchie.get(label)
            for state_id, label in LIVOR_LABEL_IT.items()
        }
        self.assertEqual(LIVOR_DESCRIPTION_IT_BY_ID, expected)
        self.assertEqual(TESTI_MACCHIE_LEGACY, testi_macchie)

    def test_rigor_descriptions_match_legacy_exactly(self):
        expected = {
            state_id: rigidita_descrizioni.get(label)
            for state_id, label in RIGOR_LABEL_IT.items()
        }
        self.assertEqual(RIGOR_DESCRIPTION_IT_BY_ID, expected)
        self.assertEqual(RIGIDITA_DESCRIZIONI_LEGACY, rigidita_descrizioni)

    def test_special_descriptions_match_legacy_exactly(self):
        expected = {
            param_id: {
                option_id: dati_parametri_aggiuntivi[param_label]["descrizioni"].get(option_label)
                for option_id, option_label in SPECIAL_OPTION_LABEL_IT[param_id].items()
            }
            for param_id, param_label in SPECIAL_PARAM_LABEL_IT.items()
        }
        self.assertEqual(SPECIAL_DESCRIPTION_IT_BY_ID, expected)

        legacy_expected = {
            param_label: data["descrizioni"]
            for param_label, data in dati_parametri_aggiuntivi.items()
        }
        self.assertEqual(SPECIAL_DESCRIPTIONS_LEGACY_BY_PARAM_LABEL, legacy_expected)

    def test_graph_labels_match_legacy_exactly(self):
        expected_special = {
            param_id: nomi_brevi.get(param_label, param_label)
            for param_id, param_label in SPECIAL_PARAM_LABEL_IT.items()
        }
        self.assertEqual(SPECIAL_GRAPH_LABEL_IT_BY_ID, expected_special)
        self.assertEqual(NOMI_BREVI_LEGACY, nomi_brevi)


if __name__ == "__main__":
    unittest.main()
