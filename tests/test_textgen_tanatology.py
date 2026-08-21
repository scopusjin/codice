# -*- coding: utf-8 -*-

import unittest

from app.special_tanatology_states import (
    OPTION_NOT_ASSESSED,
    OPTION_UNRELIABLE,
    OPTION_NO_REACTION,
)
from app.textgen_tanatology import (
    resolve_special_state_id,
    special_description_is_reportable,
)


class TextgenTanatologyCompatibilityTests(unittest.TestCase):
    def test_stable_ids_control_reportability(self):
        self.assertFalse(special_description_is_reportable({"stato_id": OPTION_NOT_ASSESSED}))
        self.assertFalse(special_description_is_reportable({"stato_id": OPTION_UNRELIABLE}))
        self.assertTrue(special_description_is_reportable({"stato_id": OPTION_NO_REACTION}))

    def test_known_legacy_pair_is_resolved_to_stable_id(self):
        self.assertEqual(
            resolve_special_state_id({
                "nome": "Eccitabilità elettrica sopraciliare",
                "stato": "Nessuna reazione",
            }),
            OPTION_NO_REACTION,
        )
        self.assertEqual(
            resolve_special_state_id({
                "nome": "Eccitabilità chimica pupillare",
                "stato": "Non valutabile/non attendibile",
            }),
            OPTION_UNRELIABLE,
        )

    def test_legacy_fallback_matches_existing_textgen_behavior(self):
        self.assertFalse(special_description_is_reportable({"stato": "Non valutata"}))
        self.assertFalse(special_description_is_reportable({"stato": "Non valutabile/non attendibile"}))
        self.assertTrue(special_description_is_reportable({"stato": "Nessuna reazione"}))
        self.assertTrue(special_description_is_reportable({"stato": "Fase I"}))

    def test_stable_id_takes_precedence_over_legacy_label(self):
        self.assertTrue(special_description_is_reportable({
            "stato_id": OPTION_NO_REACTION,
            "stato": "Non valutata",
        }))
        self.assertFalse(special_description_is_reportable({
            "stato_id": OPTION_UNRELIABLE,
            "stato": "Nessuna reazione",
        }))


if __name__ == "__main__":
    unittest.main()
