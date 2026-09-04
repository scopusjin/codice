# -*- coding: utf-8 -*-

import unittest

from app import i18n


class FullUiTextCompatibilityTests(unittest.TestCase):
    def test_general_labels_match_current_ui(self):
        expected = {
            "full.title": "STIMA EPOCA DECESSO",
            "full.add_datetime": "Aggiungi data/ora rilievi tanatologici",
            "full.inspection_date": "Data ispezione legale:",
            "full.inspection_time": "Ora ispezione legale (HH:MM):",
            "full.livor_heading": "Ipostasi",
            "full.livor_select_label": "Macchie ipostatiche:",
            "full.rigor_heading": "Rigidità cadaverica",
            "full.rigor_select_label": "Rigidità cadaverica:",
            "full.cooling_heading": "Raffreddamento cadaverico",
            "full.add_special_data": "Aggiungi dati tanatologici speciali",
            "full.assessed_different_time": "Valutato ad un'ora diversa?",
            "full.measurement_date": "Data rilievo:",
            "full.measurement_time": "Ora rilievo:",
            "full.measurement_time_input": "Ora rilievo (HH:MM):",
            "full.putrefactive_changes": "Alterazioni putrefattive?",
            "full.estimate_button": "Procedi con la stima",
            "full.no_data_warning": "Nessun dato inserito per la stima",
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(i18n.ui_text(key), value)

    def test_henssge_labels_and_help_match_current_ui(self):
        self.assertEqual(i18n.ui_text("full.prudent_toggle"), "Condizioni variabili?")
        self.assertEqual(
            i18n.ui_text("full.henssge_not_applicable"),
            "Henssge non applicabile",
        )
        self.assertEqual(
            i18n.ui_text("full.henssge_not_applicable_help"),
            "Il metodo di Henssge non può essere applicato nelle seguenti circostanze:\n"
            "• Non è possibile stabilire che il luogo di rinvenimento del corpo coincida con il luogo del decesso.\n"
            "• Presenza di una fonte di calore nelle immediate vicinanze del corpo.\n"
            "• Presenza di riscaldamento a pavimento sotto il corpo.\n"
            "• Ipotermia accertata o sospetta (temperatura corporea iniziale < 35 °C).\n"
            "• Impossibilità di determinare la temperatura ambientale media.\n"
            "• Impossibilità di stimare il fattore correttivo di Henssge.\n"
            "• Aumento significativo della temperatura ambientale (da valori bassi a elevati).",
        )
        self.assertEqual(
            i18n.ui_text("full.henssge_incoherent_warning"),
            "Non è stato possibile applicare il metodo di Henssge "
            "(temperature incoerenti o fuori range).",
        )

    def test_prudent_note_matches_current_html(self):
        self.assertEqual(
            i18n.ui_text("full.prudent_default_note"),
            "<div style='font-size:0.9rem; color:#444; padding:6px 8px; "
            "border-left:4px solid #bbb; background:#f7f7f7; margin-bottom:8px;'>"
            "Usa questa modalità quando la temperatura ambientale media e il fattore di correzione "
            "potrebbero essere cambiati nel tempo o sono incerti. Per ciascun parametro, inserisci "
            "i due estremi plausibili dell’intervallo, cioè il valore minimo e il valore massimo da "
            "considerare nel calcolo. Per il fattore di correzione, «Consiglia» aiuta a individuare "
            "il valore da associare a ciascun estremo."
            "</div>",
        )
        self.assertEqual(
            i18n.ui_text("full.special_datetime_hint"),
            "<div style='font-size:0.9rem; color:#666; padding:6px 8px; "
            "border-left:4px solid #bbb; background:#f7f7f7; margin-bottom:8px;'>"
            "Per specificare orari dei rilievi, attiva in alto "
            "<b>“Aggiungi data/ora rilievi”</b>."
            "</div>",
        )

    def test_factor_panel_labels_match_current_ui(self):
        ta_help = (
            "<span title='Considera la temperatura ambientale media alla quale il corpo può essere stato esposto "
            "tra il decesso e l’ispezione. Non corrisponde necessariamente alla temperatura misurata al momento "
            "del rilievo, soprattutto se il cadavere si trova all’aperto.'>ⓘ</span>"
        )
        expected = {
            "full.specify_range": "Specifica range",
            "full.ta_mean_label": f"T. ambientale media (°C): {ta_help}",
            "full.ta_range_label": f"Range di T. ambientale media (°C): {ta_help}",
            "full.fc_label": "Fattore di correzione (FC):",
            "full.fc_range_label": "Range del fattore di correzione (FC):",
            "full.rectal_temp_label": "T. rettale (°C):",
            "full.antemortem_temp_label": "T. ante-mortem (°C):",
            "full.antemortem_temp_estimated_label": "T. ante-mortem stimata (°C):",
            "full.weight_label": "Peso (kg):",
            "full.weight_label_standard": "Peso  (kg):",
            "full.weight_uncertainty": "±3 kg",
            "full.ta_input_label": "T. ambientale (°C):",
            "full.ta_base_input": "TA base",
            "full.ta_other_input": "TA altro estremo",
            "full.fc_input_label": "Fattore di correzione:",
            "full.fc_min_input": "FC min",
            "full.fc_max_input": "FC max",
            "full.fc_input": "FC",
            "full.suggest_fc": "Suggerisci FC",
            "full.use_this_factor": "✅ Usa questo fattore",
            "full.add_to_fc_range": "➕ Aggiungi a range FC",
            "full.clothed_covered": "Vestito/coperto?",
            "full.count_column": "Numero?",
            "full.support_surface": "Superficie di appoggio",
            "full.air_currents": "Correnti d'aria presenti?",
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(i18n.ui_text(key), value)

    def test_dynamic_factor_box_text_matches_current_ui(self):
        self.assertEqual(
            i18n.ui_text("full.fc_suggested", value=1.25),
            "Fattore di correzione suggerito: 1.25",
        )
        self.assertEqual(
            i18n.ui_text("full.fc_adjusted_for_weight", weight=82.4, base=1.10),
            "Adattato per 82.4 kg (valore per 70 kg: 1.10)",
        )


class MSILUiTextCompatibilityTests(unittest.TestCase):
    def test_msil_labels_match_current_ui(self):
        expected = {
            "msil.page_title": "STIMA EPOCA DECESSO - MSIL",
            "msil.no_description": "<p style='opacity:.7'>Nessuna descrizione disponibile.</p>",
            "msil.add_datetime": "Aggiungi data/ora rilievi tanatologici",
            "msil.inspection_date": "Data ispezione legale",
            "msil.inspection_time": "Ora ispezione legale (HH:MM)",
            "msil.livor_select_label": "Macchie ipostatiche",
            "msil.rigor_select_label": "Rigidità cadaverica",
            "msil.rectal_temp": "T. rettale (°C)",
            "msil.ta_mean": "T. ambientale media (°C)",
            "msil.weight": "Peso (kg)",
            "msil.fc_label": "Fattore di correzione (FC)",
            "msil.suggest_fc": "Suggerisci FC",
            "msil.clothed_covered": "Vestiti/coperte su addome/bacino?",
            "msil.item_column": "Voce",
            "msil.count_column": "Numero?",
            "msil.support_surface": "Superficie di appoggio",
            "msil.air_currents": "Correnti d'aria presenti?",
            "msil.estimate_button": "STIMA EPOCA DECESSO",
            "msil.recommendations_button": "ℹ️ Raccomandazioni",
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(i18n.ui_text(key), value)

    def test_msil_recommendations_keep_current_content(self):
        text = i18n.ui_text("msil.recommendations_html")
        self.assertIn("LA VALUTAZIONE DEL RAFFREDDAMENTO CADAVERICO NON È APPLICABILE SE:", text)
        self.assertIn("Migrabilità ≠ improntabilità", text)
        self.assertIn("±1 °C", text)
        self.assertIn("± 0.1", text)
        self.assertIn("±3 kg", text)


class UiTextErrorsTests(unittest.TestCase):
    def test_unknown_ui_key_raises_key_error(self):
        with self.assertRaises(KeyError):
            i18n.ui_text("full.unknown")


if __name__ == "__main__":
    unittest.main()
