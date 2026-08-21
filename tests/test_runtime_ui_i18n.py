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

    def test_remaining_graph_runtime_messages_keep_current_text(self):
        self.assertEqual(
            i18n.ui_text("graph.missing_special_description", state="Positiva"),
            "Descrizione non trovata per 'Positiva'.",
        )
        self.assertEqual(
            i18n.ui_text("graph.special_without_range", parameter="Parametro", state="Stato"),
            "Parametro (Stato) senza range definito.",
        )
        self.assertEqual(
            i18n.ui_text("graph.no_useful_data"),
            "Mancanza di dati utili per la stima",
        )
        self.assertEqual(
            i18n.ui_text("graph.shifted_ranges_note"),
            'Alcuni parametri sono stati rilevati in orari diversi; i range indicati con "*" sono stati traslati per renderli confrontabili.',
        )
        self.assertEqual(
            i18n.ui_text("graph.henssge_missing_invalid"),
            "Non è stato possibile applicare il metodo di Henssge per il raffreddamento cadaverico: dati mancanti o non validi.",
        )
        self.assertEqual(
            i18n.ui_text("graph.henssge_incoherent"),
            "Non è stato possibile applicare il metodo di Henssge per il raffreddamento cadaverico: dati incoerenti o fuori range",
        )
        self.assertEqual(
            i18n.ui_text("graph.high_ambient_factor_warning"),
            "Per temperature ambientali &gt; 25 °C, variazioni del fattore di correzione possono influenzare notevolmente i risultati.",
        )
        self.assertEqual(
            i18n.ui_text("graph.low_ambient_factor_warning"),
            "Per temperature ambientali &lt; 18 °C, la scelta di un fattore di correzione diverso da 1 potrebbe influenzare notevolmente i risultati.",
        )
        self.assertEqual(
            i18n.ui_text("graph.thermal_equilibrium_warning"),
            "Essendo minima la differenza tra temperatura rettale e ambientale, è possibile che il cadavere fosse ormai in equilibrio termico con l'ambiente. La stima ottenuta dal raffreddamento cadaverico va interpretata con attenzione.",
        )
        self.assertEqual(
            i18n.ui_text("graph.plateau_warning"),
            "Considerato che la T rettale è molto simile alla T ante-mortem stimata, è verosimile che il raffreddamento corporeo non fosse ancora iniziato e/o si trovasse nella fase di plateau. In tale fase, la precisione del metodo è ridotta.",
        )


if __name__ == "__main__":
    unittest.main()
