import datetime as dt
import unittest
from app.utils_time import arrotonda_quarto_dora
from app.textgen import build_final_sentence, build_simple_sentence, nota_limiti_stima, nota_arrotondamento_orari
from app.language import using_language
from app.case_report import build_word_blocks


class FinalTimeTests(unittest.TestCase):
    def test_nearest_quarter_including_seconds_and_midnight(self):
        for source, expected in [("2026-10-26T12:07:29", "2026-10-26T12:00"),
                                 ("2026-10-26T12:07:30", "2026-10-26T12:15"),
                                 ("2026-10-26T12:22:31", "2026-10-26T12:30"),
                                 ("2026-10-26T23:58", "2026-10-27T00:00")]:
            self.assertEqual(arrotonda_quarto_dora(dt.datetime.fromisoformat(source)), dt.datetime.fromisoformat(expected))

    def test_rounded_dates_agree_in_both_conclusions_and_languages(self):
        inspection = dt.datetime(2026, 10, 27, 2, 58)
        for language in ("it", "en"):
            with using_language(language):
                for build in (build_final_sentence, build_simple_sentence):
                    text = build(2, 3, inspection)
                    self.assertIn("00:00", text)
                    self.assertIn("01:00", text)
                    self.assertIn("27.10.2026", text)
                    self.assertNotIn("26.10.2026", text)

    def test_inspection_time_is_preserved(self):
        text = build_final_sentence(0, 4, dt.datetime(2026, 10, 27, 11, 28))
        self.assertIn("07:30", text)
        self.assertIn("11:28", text)

    def test_caution_keeps_italics_in_word(self):
        for language in ("it", "en"):
            with using_language(language):
                caution = nota_limiti_stima()
                self.assertEqual(caution.count("<i>"), 2)
                blocks = build_word_blocks(input_html="", cooling_html="", livor="", rigor="", conclusion="Conclusion" + caution)
                self.assertIn(caution, blocks["conclusion"]["html"])
                self.assertIn("color:blue", nota_arrotondamento_orari())
