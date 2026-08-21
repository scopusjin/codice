# -*- coding: utf-8 -*-

import unittest

from app.textgen import paragrafo_putrefattive, frase_riepilogo_parametri_usati


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


if __name__ == "__main__":
    unittest.main()
