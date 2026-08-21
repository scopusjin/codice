# -*- coding: utf-8 -*-

import unittest

from app.textgen import (
    _fmt_hm_full,
    _fmt_range_hm,
    build_simple_sentence_no_dt,
)


class TextgenItalianTimeFormattingTests(unittest.TestCase):
    def test_hours_and_minutes_wording_is_preserved_exactly(self):
        self.assertEqual(_fmt_hm_full(1, 30), "1 ora 30 minuti")
        self.assertEqual(_fmt_hm_full(2, 0), "2 ore")
        self.assertEqual(_fmt_hm_full(0, 45), "45 minuti")
        self.assertEqual(_fmt_hm_full(0, 1), "1 minuto")
        self.assertEqual(_fmt_hm_full(0, 0), "0 minuti")

    def test_range_wording_is_preserved_exactly(self):
        self.assertEqual(_fmt_range_hm(2, 0, 3, 0), "tra 2 e 3 ore")
        self.assertEqual(
            _fmt_range_hm(2, 0, 3, 30),
            "tra 2 ore e 3 ore 30 minuti",
        )
        self.assertEqual(
            _fmt_range_hm(1, 30, 3, 0),
            "tra 1 ora 30 minuti e 3 ore",
        )

    def test_simple_sentence_without_datetime_keeps_current_html(self):
        self.assertEqual(
            build_simple_sentence_no_dt(1, 4),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "<b>tra 1 e 4 ore prima</b> "
            "dei rilievi dei dati tanatologici.</p>",
        )


if __name__ == "__main__":
    unittest.main()
