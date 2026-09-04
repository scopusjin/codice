# -*- coding: utf-8 -*-

import datetime
import unittest
import numpy as np

from app.textgen import (
    _fmt_hm_full,
    _fmt_range_hm,
    build_final_sentence,
    build_simple_sentence,
    build_simple_sentence_no_dt,
    build_final_sentence_simple,
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
            _fmt_range_hm(1, 0, 6, 30),
            "tra 1 ora e 6 ore 30 minuti",
        )
        self.assertEqual(
            _fmt_range_hm(1, 30, 3, 0),
            "tra 1 ora 30 minuti e 3 ore",
        )

    def test_final_sentence_with_datetime_keeps_current_html(self):
        isp_dt = datetime.datetime(2026, 8, 21, 14, 0)
        self.assertEqual(
            build_final_sentence(2, np.inf, isp_dt),
            "<p>La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta all'incirca "
            "<b>oltre 2 ore prima</b> dei rilievi effettuati nel corso dell’ispezione legale, "
            "vale a dire <b>prima delle ore 12:00 del 21.08.2026</b>.</p>",
        )
        self.assertEqual(
            build_final_sentence(0, 4, isp_dt),
            "<p>La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali minimi e massimi, "
            "consente di stimare che la morte sia avvenuta all'incirca <b>non oltre 4 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale, "
            "vale a dire <b>successivamente alle ore 10:00 del 21.08.2026 "
            "(ma prima delle ore 14:00 del 21.08.2026)</b>.</p>",
        )
        self.assertEqual(
            build_final_sentence(1, 4, isp_dt),
            "<p>La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali minimi e massimi, "
            "consente di stimare che la morte sia avvenuta all'incirca <b>tra 1 e 4 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale, "
            "vale a dire circa <b>tra le ore 10:00 e le ore 13:00 del 21.08.2026</b>.</p>",
        )

    def test_final_sentence_with_datetime_preserves_cross_midnight_window(self):
        isp_dt = datetime.datetime(2026, 8, 21, 2, 0)
        self.assertEqual(
            build_final_sentence(1, 4, isp_dt),
            "<p>La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali minimi e massimi, "
            "consente di stimare che la morte sia avvenuta all'incirca <b>tra 1 e 4 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale, "
            "vale a dire circa <b>tra le ore 22:00 del 20.08.2026 e le ore 01:00 del 21.08.2026</b>.</p>",
        )

    def test_simple_sentence_with_datetime_keeps_current_html(self):
        isp_dt = datetime.datetime(2026, 8, 21, 14, 0)
        self.assertEqual(
            build_simple_sentence(0, 4, isp_dt),
            "<p>EPOCA DEL DECESSO STIMATA: non oltre 4 ore prima "
            "dei rilievi effettuati nel corso dell’ispezione legale, "
            "vale a dire all'incirca tra le ore 10:00 e le 14:00 del 21.08.2026.</p>",
        )
        self.assertEqual(
            build_simple_sentence(2, np.inf, isp_dt),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "<b>oltre 2 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale, "
            "vale a dire <b>prima delle ore 12:00 del 21.08.2026</b>.</p>",
        )
        self.assertEqual(
            build_simple_sentence(1, 4, isp_dt),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "<b>tra 1 e 4 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale, "
            "vale a dire circa <b>tra le ore 10:00 e le ore 13:00 del 21.08.2026</b>.</p>",
        )

    def test_simple_sentence_with_datetime_preserves_cross_midnight_window(self):
        isp_dt = datetime.datetime(2026, 8, 21, 2, 0)
        self.assertEqual(
            build_simple_sentence(0, 4, isp_dt),
            "<p>EPOCA DEL DECESSO STIMATA: non oltre 4 ore prima "
            "dei rilievi effettuati nel corso dell’ispezione legale, "
            "vale a dire all'incirca tra le ore 22:00 del 20.08.2026 e le 02:00 del 21.08.2026.</p>",
        )
        self.assertEqual(
            build_simple_sentence(1, 4, isp_dt),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "<b>tra 1 e 4 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale, "
            "vale a dire circa <b>tra le ore 22:00 del 20.08.2026 e le ore 01:00 del 21.08.2026</b>.</p>",
        )

    def test_simple_sentence_without_datetime_keeps_current_html(self):
        self.assertEqual(
            build_simple_sentence_no_dt(1, 4),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "<b>tra 1 e 4 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale.</p>",
        )
        self.assertEqual(
            build_simple_sentence_no_dt(0, 4),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "<b>non oltre 4 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale.</p>",
        )
        self.assertEqual(
            build_simple_sentence_no_dt(2, np.inf),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "<b>oltre 2 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale.</p>",
        )

    def test_final_sentence_simple_keeps_current_html(self):
        self.assertEqual(
            build_final_sentence_simple(2, np.inf),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali, "
            "consente di stimare che la morte sia avvenuta all'incirca <b>oltre 2 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale.</p>",
        )
        self.assertEqual(
            build_final_sentence_simple(0, 4),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali, "
            "consente di stimare che la morte sia avvenuta all'incirca <b>non oltre 4 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale.</p>",
        )
        self.assertEqual(
            build_final_sentence_simple(1, 4),
            "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
            "La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali, "
            "consente di stimare che la morte sia avvenuta all'incirca <b>tra 1 e 4 ore prima</b> "
            "dei rilievi effettuati nel corso dell’ispezione legale.</p>",
        )


if __name__ == "__main__":
    unittest.main()
