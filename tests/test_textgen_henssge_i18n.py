# -*- coding: utf-8 -*-

import unittest

from app import i18n
from app.textgen import paragrafo_raffreddamento_dettaglio


class TextgenHenssgeI18nTests(unittest.TestCase):
    def test_not_over_interval_wording_is_preserved(self):
        self.assertEqual(
            i18n.prudent_result_text(
                minimum_text="",
                maximum_text="4 ore",
                beyond=False,
                not_over=True,
            ),
            "non oltre 4 ore",
        )
        self.assertEqual(
            paragrafo_raffreddamento_dettaglio(
                t_min_visual=0.0,
                t_max_visual=4.0,
                t_med_round=None,
                qd_val=None,
                ta_val=20.0,
            ),
            "<ul><li>Applicando l'equazione di Henssge, è stimabile che il decesso sia avvenuto, all'incirca, "
            "non oltre 4 ore prima dei rilievi effettuati nel corso dell’ispezione legale.</li></ul>",
        )


if __name__ == "__main__":
    unittest.main()
