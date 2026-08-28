# -*- coding: utf-8 -*-

import unittest

from app import i18n
from app.cautelativa import build_parentetica_cautelativa, build_summary_html


class PrudentCoolingTextCompatibilityTests(unittest.TestCase):
    def test_prudent_formatters_keep_current_text(self):
        self.assertEqual(i18n.prudent_range_text(19.0, 21.0, "°C"), "19–21 °C")
        self.assertEqual(i18n.prudent_range_text(0.9, 1.1, ""), "0.9–1.1 ")
        self.assertEqual(i18n.prudent_hours_text(1.5), "1 ora e 30 minuti")
        self.assertEqual(i18n.prudent_hours_text(0.0), "0 ore")

    def test_parenthetical_keeps_current_output(self):
        self.assertEqual(
            build_parentetica_cautelativa(19.0, 21.0, 0.9, 1.1, 67.0, 73.0, True),
            "(raffreddamento stimato su Ta 19–21 °C, CF 0.9–1.1 , peso 67–73 kg, peso stimato)",
        )

    def test_summary_keeps_current_output(self):
        expected = (
            "Per quanto attiene la valutazione del raffreddamento cadaverico, "
            "sono stati stimati i parametri di seguito indicati."
            "<br><ul>"
            "<li>Range di temperature ambientali medie (tenendo conto delle possibili escursioni termiche verificatesi tra decesso e ispezione legale): <b>19–21 °C</b>.</li>"
            "<li>Range per il fattore di correzione (considerate le possibili condizioni in cui può essersi trovato il corpo): <b>0.9–1.1 </b>.</li>"
            "<li>Peso corporeo: <b>70 kg</b>.</li>"
            "</ul>"
            "<br>Applicando l'equazione di Henssge, è possibile stimare che il decesso "
            "sia avvenuto tra circa 5 ore e 10 ore prima dei rilievi effettuati nel corso "
            "dell’ispezione legale."
        )
        self.assertEqual(
            build_summary_html(
                19.0, 21.0, 0.9, 1.1, 70.0, 70.0,
                5.0, 10.0, None, None, None, None,
                peso_stimato=False,
            ),
            expected,
        )

    def test_estimated_weight_marker_keeps_current_output(self):
        self.assertEqual(i18n.prudent_estimated_weight("67–73 kg"), "67–73 kg (stimato)")

    def test_graphing_fallback_renderers_keep_current_output(self):
        self.assertEqual(i18n.prudent_graphing_hours_text(0.5), "0 ore 30 minuti")
        self.assertEqual(i18n.prudent_graphing_hours_text(1.0), "1 ora")
        self.assertEqual(i18n.prudent_graphing_hours_text(1.5), "1 ora 30 minuti")
        self.assertEqual(i18n.prudent_graphing_hours_text(2.0), "2 ore")
        self.assertEqual(i18n.prudent_graphing_hours_text(float("inf")), "")
        self.assertEqual(
            i18n.prudent_graphing_result_at_least("5 ore"),
            "almeno 5 ore",
        )
        self.assertEqual(
            i18n.prudent_graphing_result_range("5 ore", "10 ore"),
            "tra 5 ore e 10 ore",
        )
        self.assertEqual(
            i18n.prudent_header(),
            "Per quanto attiene la valutazione del raffreddamento cadaverico, "
            "sono stati stimati i parametri di seguito indicati.",
        )
        self.assertEqual(
            i18n.prudent_simple_bullets(
                ta_text="19.0 – 21.0 °C",
                cf_text="0.90 – 1.10",
                weight_text="70 kg",
            ),
            "<ul>"
            "<li>Range di temperature ambientali medie: <b>19.0 – 21.0 °C</b></li>"
            "<li>Range per il fattore di correzione: <b>0.90 – 1.10</b></li>"
            "<li>Peso corporeo: <b>70 kg</b></li>"
            "</ul>",
        )
        self.assertEqual(
            i18n.prudent_conclusion("tra 5 ore e 10 ore"),
            "Applicando l'equazione di Henssge, è possibile stimare che il decesso "
            "sia avvenuto tra 5 ore e 10 ore prima dei rilievi effettuati nel corso "
            "dell’ispezione legale.",
        )
        self.assertEqual(
            i18n.prudent_graphing_detail_list(
                header=i18n.prudent_header(),
                ta_text="19.0 – 21.0 °C",
                cf_text="0.90 – 1.10",
                weight_text="70 kg",
            ),
            "<ul>"
            "<li>Per quanto attiene la valutazione del raffreddamento cadaverico, sono stati stimati i parametri di seguito indicati."
            "<ul style='list-style-type: circle; margin-left: 20px;'>"
            "<li>Range di temperature ambientali medie (tenendo conto delle possibili escursioni termiche verificatesi tra decesso e ispezione legale): <b>19.0 – 21.0 °C</b>.</li>"
            "<li>Range per il fattore di correzione (considerate le possibili condizioni in cui può essersi trovato il corpo): <b>0.90 – 1.10</b>.</li>"
            "<li>Peso corporeo: <b>70 kg</b>.</li>"
            "</ul></li>"
            "</ul>",
        )


if __name__ == "__main__":
    unittest.main()
