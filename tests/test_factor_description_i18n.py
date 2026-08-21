# -*- coding: utf-8 -*-

import unittest

from app.factor_calc import (
    SURF_COND,
    build_cf_description,
)


class FactorDescriptionItalianCompatibilityTests(unittest.TestCase):
    def test_manual_override_keeps_numeric_only_output(self):
        self.assertEqual(
            build_cf_description(1.4, None, manual_override=True),
            "1.40",
        )

    def test_missing_summary_keeps_current_fallback_wording(self):
        self.assertEqual(
            build_cf_description(1.4, None),
            "1.40 (da adattare sulla base dei fattori scelti).",
        )
        self.assertEqual(
            build_cf_description(1.4, None, fallback_text="condizioni non specificate"),
            "1.40 (in base ai fattori scelti: condizioni non specificate).",
        )

    def test_dry_naked_condductive_airflow_weight_adapted_keeps_current_output(self):
        riassunto = {
            "stato": "Asciutto",
            "sottili": 0,
            "spessi": 0,
            "cop_medie": 0,
            "cop_pesanti": 0,
            "superficie_key": SURF_COND,
            "correnti": "Correnti d'aria presenti",
            "peso_adattato": True,
        }
        self.assertEqual(
            build_cf_description(1.4, riassunto),
            "1.40 (corpo nudo, adagiato su superficie termicamente conduttiva, con correnti d'aria. "
            "Il fattore di correzione è stato adattato per il peso corporeo.)",
        )

    def test_immersed_current_water_keeps_current_output(self):
        riassunto = {
            "stato": "Immerso",
            "sottili": 0,
            "spessi": 0,
            "cop_medie": 0,
            "cop_pesanti": 0,
            "superficie_key": None,
            "correnti": "in acqua corrente",
            "peso_adattato": False,
        }
        self.assertEqual(
            build_cf_description(0.35, riassunto),
            "0.35 (corpo immerso, nudo, in acqua corrente)",
        )

    def test_clothing_and_blanket_wording_is_preserved(self):
        riassunto = {
            "stato": "Asciutto",
            "sottili": 2,
            "spessi": 0,
            "cop_medie": 0,
            "cop_pesanti": 1,
            "superficie_key": None,
            "correnti": None,
            "peso_adattato": False,
        }
        self.assertEqual(
            build_cf_description(2.14, riassunto),
            "2.14 (con indosso pochi strati leggeri, sotto una coperta pesante)",
        )


if __name__ == "__main__":
    unittest.main()
