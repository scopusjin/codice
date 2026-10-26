# -*- coding: utf-8 -*-

import unittest

import numpy as np

from app import i18n
from app.plotting import compute_plot_data


class PlottingItalianTextCompatibilityTests(unittest.TestCase):
    def test_plot_labels_keep_current_italian_text(self):
        self.assertEqual(i18n.ui_text("plot.livor"), "Ipostasi")
        self.assertEqual(i18n.ui_text("plot.rigor"), "Rigor")
        self.assertEqual(i18n.ui_text("plot.cooling"), "Raffreddamento")
        self.assertEqual(i18n.ui_text("plot.generic_parameter"), "Parametro")
        self.assertEqual(i18n.ui_text("plot.hours_since_death"), "Ore dal decesso")

    def test_compute_plot_data_keeps_current_base_labels(self):
        data = compute_plot_data(
            macchie_range=(0.0, 6.0),
            macchie_medi_range=None,
            rigidita_range=(2.0, 96.0),
            rigidita_medi_range=None,
            raffreddamento_calcolabile=True,
            t_min_raff_henssge=3.0,
            t_max_raff_henssge=8.0,
            t_med_raff_henssge_rounded_raw=5.5,
            Qd_val_check=0.5,
            mt_ore=None,
            INF_HOURS=200.0,
            qd_threshold=0.2,
        )
        self.assertEqual(data["labels"][0], "Ipostasi\n(0–6 h)")
        self.assertEqual(data["labels"][1], "Rigor\n(2–96 h)")
        self.assertEqual(data["labels"][2], "Raffreddamento\n(3–8 h)")

    def test_generic_extra_label_keeps_current_fallback(self):
        data = compute_plot_data(
            macchie_range=(np.nan, np.nan),
            macchie_medi_range=None,
            rigidita_range=(np.nan, np.nan),
            rigidita_medi_range=None,
            raffreddamento_calcolabile=False,
            t_min_raff_henssge=np.nan,
            t_max_raff_henssge=np.nan,
            t_med_raff_henssge_rounded_raw=np.nan,
            Qd_val_check=np.nan,
            mt_ore=None,
            INF_HOURS=200.0,
            qd_threshold=0.2,
            extra_params=[{"start": 2.0, "end": 4.0}],
        )
        self.assertEqual(data["labels"], ["Parametro\n(2–4 h)"])


if __name__ == "__main__":
    unittest.main()
