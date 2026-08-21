# -*- coding: utf-8 -*-

import unittest

from app import i18n


class RuntimeUiTextCompatibilityTests(unittest.TestCase):
    def test_data_source_messages_keep_current_text(self):
        self.assertEqual(
            i18n.ui_text("data.weight_table_missing"),
            "Tabella correttiva del peso non trovata: continuo senza.",
        )
        self.assertEqual(
            i18n.ui_text("data.openpyxl_missing"),
            "Per leggere il file .xlsx serve 'openpyxl'. Installa con: pip install openpyxl",
        )
        self.assertEqual(
            i18n.ui_text("data.weight_table_read_error", error="errore test"),
            "Impossibile leggere l'Excel della tabella peso: errore test",
        )

    def test_graphing_messages_keep_current_text(self):
        self.assertEqual(
            i18n.ui_text("graph.invalid_weight"),
            "⚠️ Peso non valido. Inserire un valore > 0 kg.",
        )
        self.assertEqual(
            i18n.ui_text("graph.invalid_special_time", parameter="Test", time="25:00"),
            "⚠️ Test: escluso perchè ora '25:00' non valida (usa HH:MM).",
        )
        self.assertEqual(i18n.ui_text("graph.descriptions_popover"), "📖 Descrizioni dettagliate")
        self.assertEqual(i18n.ui_text("graph.warnings_popover"), "⚠️ Avvisi")


if __name__ == "__main__":
    unittest.main()
