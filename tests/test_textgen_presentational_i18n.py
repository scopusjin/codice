# -*- coding: utf-8 -*-

import datetime
import unittest

from app.textgen import (
    avvisi_raffreddamento_henssge,
    frase_qd,
    frase_riepilogo_parametri_usati,
    paragrafo_potente,
    paragrafo_putrefattive,
    paragrafo_raffreddamento_dettaglio,
    paragrafo_raffreddamento_input,
)


class TextgenPresentationalI18nTests(unittest.TestCase):
    def test_putrefactive_paragraph_keeps_current_html(self):
        self.assertIsNone(paragrafo_putrefattive(False))
        self.assertEqual(
            paragrafo_putrefattive(True),
            "<ul><li>Per quanto riguarda i processi trasformativi post-mortali (compresi quelli putrefattivi), "
            "la loro insorgenza è influenzata da numerosi fattori, esogeni (ad esempio temperatura ambientale, "
            "esposizione ai fenomeni meteorologici…) ed endogeni (temperatura corporea, infezioni prima del decesso, "
            "presenza di ferite…). Poiché tali processi possono manifestarsi in un intervallo temporale estremamente "
            "variabile, da poche ore a diverse settimane dopo il decesso, la loro valutazione non permette di formulare "
            "ulteriori precisazioni sull’epoca della morte.</li></ul>",
        )

    def test_parameter_summary_keeps_current_html(self):
        self.assertIsNone(frase_riepilogo_parametri_usati([]))
        self.assertEqual(
            frase_riepilogo_parametri_usati(["Ipostasi"]),
            "<p style='color:blue;font-size:small;'>La stima complessiva si basa sul seguente parametro: ipostasi.</p>",
        )
        self.assertEqual(
            frase_riepilogo_parametri_usati(["Ipostasi", "Rigor"]),
            "<p style='color:blue;font-size:small;'>La stima complessiva si basa sui seguenti parametri: ipostasi e rigor.</p>",
        )
        self.assertEqual(
            frase_riepilogo_parametri_usati(["Ipostasi", "Rigor", "Raffreddamento"]),
            "<p style='color:blue;font-size:small;'>La stima complessiva si basa sui seguenti parametri: ipostasi, rigor e raffreddamento.</p>",
        )

    def test_potente_paragraph_keeps_current_html_and_applicability(self):
        self.assertIsNone(
            paragrafo_potente(
                mt_ore=26.5,
                mt_giorni=1.1,
                qd_val=0.2,
                ta_val=20.0,
                qd_threshold=0.2,
            )
        )
        self.assertEqual(
            paragrafo_potente(
                mt_ore=26.5,
                mt_giorni=1.1,
                qd_val=0.1,
                ta_val=20.0,
                qd_threshold=0.2,
            ),
            "<ul><li>Lo studio di Potente et al. permette di stimare grossolanamente l’intervallo minimo post-mortem quando i dati non consentono di ottenere risultati attendibili con il metodo di Henssge. "
            "Applicandolo al caso specifico, si può ipotizzare che, al momento dell’ispezione legale, fossero trascorse almeno <b>26 ore 30 minuti</b> (≈ 1.1 giorni) dal decesso.</li></ul>",
        )

    def test_cooling_input_paragraph_without_datetime_keeps_current_html(self):
        self.assertEqual(
            paragrafo_raffreddamento_input(
                isp_dt=None,
                ta_val=20.0,
                tr_val=32.5,
                w_val=70.0,
                t0_val=37.2,
                cf_descr="1.0 (nessuna correzione)",
            ),
            "<ul><li>Per quanto attiene la valutazione del raffreddamento cadaverico, sono stati considerati gli elementi di seguito indicati."
            "<ul>"
            "<li>Temperature misurate nel corso dell’ispezione legale:"
            "<ul>"
            "<li>Temperatura ambientale: 20.0 °C.</li>"
            "<li>Temperatura rettale: 32.5 °C.</li>"
            "</ul>"
            "</li>"
            "<li>Peso del cadavere misurato: 70.0 kg.</li>"
            "<li>Temperatura corporea ipotizzata al momento della morte: 37.2 °C.</li>"
            "<li>Fattore di correzione ipotizzato in base alle condizioni ambientali (per quanto noto): 1.0 (nessuna correzione).</li>"
            "</ul>"
            "</li></ul>",
        )

    def test_cooling_input_paragraph_with_datetime_and_missing_value_keeps_current_html(self):
        self.assertEqual(
            paragrafo_raffreddamento_input(
                isp_dt=datetime.datetime(2026, 8, 21, 14, 30),
                ta_val=20.0,
                tr_val=None,
                w_val=70.0,
                t0_val=37.2,
                cf_descr="1.0 (nessuna correzione)",
            ),
            "<ul><li>Per quanto attiene la valutazione del raffreddamento cadaverico, sono stati considerati gli elementi di seguito indicati."
            "<ul>"
            "<li>Temperature misurate nel corso dell’ispezione legale verso le ore 14:30 del 21.08.2026:"
            "<ul>"
            "<li>Temperatura ambientale: 20.0 °C.</li>"
            "<li>Temperatura rettale: — °C.</li>"
            "</ul>"
            "</li>"
            "<li>Peso del cadavere misurato: 70.0 kg.</li>"
            "<li>Temperatura corporea ipotizzata al momento della morte: 37.2 °C.</li>"
            "<li>Fattore di correzione ipotizzato in base alle condizioni ambientali (per quanto noto): 1.0 (nessuna correzione).</li>"
            "</ul>"
            "</li></ul>",
        )

    def test_henssge_detail_qd_at_or_below_point_two_keeps_current_html(self):
        self.assertEqual(
            paragrafo_raffreddamento_dettaglio(
                t_min_visual=2.0,
                t_max_visual=5.0,
                t_med_round=10.0,
                qd_val=0.2,
                ta_val=20.0,
            ),
            "<ul><li>Applicando l'equazione di Henssge, è stimabile che il decesso sia avvenuto, all'incirca, tra 2 e 5 ore prima dei rilievi effettuati al momento dell’ispezione legale. "
            "<b>I valori ottenuti sono al di fuori dell'intervallo ottimale di applicazione dell'equazione.</b> "
            "La stima ottenuta non ha una solida base statistica e deve quindi essere considerata con cautela. "
            "Per la stima dell'epoca del decesso è opportuno basarsi soprattutto sugli altri dati tanatologici disponibili.</li></ul>",
        )

    def test_henssge_detail_qd_between_point_two_and_point_three_keeps_current_html(self):
        self.assertEqual(
            paragrafo_raffreddamento_dettaglio(
                t_min_visual=2.0,
                t_max_visual=5.0,
                t_med_round=10.0,
                qd_val=0.25,
                ta_val=20.0,
            ),
            "<ul><li>Applicando l'equazione di Henssge, è stimabile che il decesso sia avvenuto, all'incirca, tra 2 e 5 ore prima dei rilievi effettuati al momento dell’ispezione legale. "
            "<b>Alcuni dei valori rilevati sono al di fuori dell'intervallo ottimale di applicazione dell'equazione.</b> "
            "La stima ottenuta non ha una solida base statistica e deve quindi essere considerata con cautela. "
            "Per la stima dell'epoca del decesso è opportuno basarsi soprattutto sugli altri dati tanatologici disponibili.</li></ul>",
        )

    def test_henssge_detail_qd_at_point_three_has_no_qd_warning(self):
        self.assertEqual(
            paragrafo_raffreddamento_dettaglio(
                t_min_visual=2.0,
                t_max_visual=5.0,
                t_med_round=10.0,
                qd_val=0.3,
                ta_val=20.0,
            ),
            "<ul><li>Applicando l'equazione di Henssge, è stimabile che il decesso sia avvenuto, all'incirca, tra 2 e 5 ore prima dei rilievi effettuati al momento dell’ispezione legale.</li></ul>",
        )

    def test_henssge_detail_over_thirty_hours_keeps_current_warning(self):
        self.assertEqual(
            paragrafo_raffreddamento_dettaglio(
                t_min_visual=28.0,
                t_max_visual=34.0,
                t_med_round=31.0,
                qd_val=0.3,
                ta_val=20.0,
            ),
            "<ul><li>Applicando l'equazione di Henssge, è stimabile che il decesso sia avvenuto, all'incirca, tra 28 e 34 ore prima dei rilievi effettuati al momento dell’ispezione legale. "
            "La stima media ottenuta dal raffreddamento cadaverico (31.0 h) è superiore alle 30 ore. "
            "L'affidabilità del metodo di Henssge diminuisce significativamente oltre questo intervallo.</li></ul>",
        )

    def test_henssge_warning_list_keeps_strict_over_thirty_boundary(self):
        self.assertEqual(avvisi_raffreddamento_henssge(t_med_round=30.0, qd_val=0.1), [])
        self.assertEqual(
            avvisi_raffreddamento_henssge(t_med_round=30.1, qd_val=0.1),
            [
                "La stima media ottenuta dal raffreddamento cadaverico (30.1 h) è superiore alle 30 ore. "
                "L'affidabilità del metodo di Henssge diminuisce significativamente oltre questo intervallo."
            ],
        )

    def test_qd_summary_keeps_temperature_dependent_thresholds(self):
        self.assertIsNone(frase_qd(None, 20.0))
        self.assertEqual(
            frase_qd(0.19, 23.0),
            "<p style='color:blue;font-size:small;'> Nel caso in esame, l'equazione di Henssge per il raffreddamento cadaverico ha Qd = 0.190. "
            "Tale parametro è inferiore ai limiti ottimali per applicare l'equazione (per T. amb ≤ 23 °C, Qd deve essere superiore a 0.2).</p>",
        )
        self.assertEqual(
            frase_qd(0.2, 23.0),
            "<p style='color:blue;font-size:small;'> Nel caso in esame, l'equazione di Henssge per il raffreddamento cadaverico ha Qd = 0.200. "
            "Tale parametro rientra nei limiti ottimali per applicare l'equazione (per T. amb ≤ 23 °C, Qd deve essere superiore a 0.2).</p>",
        )
        self.assertEqual(
            frase_qd(0.49, 24.0),
            "<p style='color:blue;font-size:small;'> Nel caso in esame, l'equazione di Henssge per il raffreddamento cadaverico ha Qd = 0.490. "
            "Tale parametro è inferiore ai limiti ottimali per applicare l'equazione (per T. amb > 23 °C, Qd deve essere superiore a 0.5).</p>",
        )
        self.assertEqual(
            frase_qd(0.5, 24.0),
            "<p style='color:blue;font-size:small;'> Nel caso in esame, l'equazione di Henssge per il raffreddamento cadaverico ha Qd = 0.500. "
            "Tale parametro rientra nei limiti ottimali per applicare l'equazione (per T. amb > 23 °C, Qd deve essere superiore a 0.5).</p>",
        )


if __name__ == "__main__":
    unittest.main()
