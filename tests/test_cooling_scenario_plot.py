import datetime
import unittest

import matplotlib.pyplot as plt
import numpy as np

from app.graphing_cooling import compute_cooling_state, _potente_limit_for_combination
from app.henssge import calcola_raffreddamento
from app.language import using_language
from app.plotting import compute_plot_data, render_ranges_plot


class CoolingScenarioPlotTests(unittest.TestCase):
    def test_mixed_methods_use_each_scenarios_original_inputs_and_estimated_weight(self):
        scenarios = [
            dict(temperature=11., range=[.7, .7], description="corpo asciutto"),
            dict(temperature=15., range=[1.2, 1.4], description="corpo coperto"),
        ]
        options = dict(stima_cautelativa_beta=True, peso_stimato_beta=True,
                       Ta_min_beta=11., Ta_max_beta=15., FC_min_beta=.7, FC_max_beta=1.4,
                       __fc_applied_choice=dict(range=[.7, 1.4], weight=85., scenarios=scenarios))
        state = compute_cooling_state(input_rt=17.1, input_ta=11., input_tm=37.2,
            input_w=85., fattore_correzione=.7, data_ora_ispezione=datetime.datetime(2026, 11, 21),
            skip_warnings=True, cooling_options=options)
        finite = [calcola_raffreddamento(17.1, 11., 37.2, w, .7, round_minutes=None) for w in range(82, 89)]
        minimum = min(_potente_limit_for_combination(15., fc, w)
                      for fc in (1.2, 1.25, 1.3, 1.35, 1.4) for w in range(82, 89))
        self.assertEqual(state.scenario_ranges, (
            (min(result[1] for result in finite), max(result[2] for result in finite)),
            (minimum, np.inf),
        ))
        self.assertEqual(state.scenario_ranges[0], (state.t_min_raff_henssge, state.t_max_raff_henssge))
        self.assertEqual(minimum, state.potente_min_ore)

    def test_plot_draws_only_each_scenarios_interval_on_its_own_row(self):
        for second in ((9., 16.), (20., 26.), (6., 12.), (40., np.inf), None):
            with self.subTest(second=second), using_language("en"):
                open_end = second is not None and np.isinf(second[1])
                extras = [{"label": "Body cooling", "start": 6., "end": np.inf, "is_potente": True}] if open_end else []
                extras.append({"label": "Other", "start": 1., "end": 4.})
                data = compute_plot_data(macchie_range=(0., 6.), macchie_medi_range=None,
                    rigidita_range=(np.nan, np.nan), rigidita_medi_range=None,
                    raffreddamento_calcolabile=not open_end, t_min_raff_henssge=6., t_max_raff_henssge=12.,
                    t_med_raff_henssge_rounded_raw=9., Qd_val_check=.8, mt_ore=None, INF_HOURS=200.,
                    qd_threshold=.2, extra_params=extras, scenario_ranges=((6., 12.), second))
                fig = render_ranges_plot(data)
                try:
                    ax = fig.axes[0]
                    rows = list(data["scenario_rows"])
                    labels = [tick.get_text() for tick in ax.get_yticklabels()]
                    self.assertEqual(labels[rows[0]-1:rows[0]+1], ["Body cooling", "Scenario 1 (6–12 h)"])
                    self.assertEqual(labels[data["extra_rows"][-1]], "Other\n(1–4 h)")
                    lines = {segment[0, 1]: (tuple(segment[:, 0]), line.get_linestyles()[0][1])
                             for line in ax.collections for segment in line.get_segments()}
                    self.assertNotIn(rows[0] - 1, lines)
                    self.assertEqual(lines[rows[0]], ((6., 12.), None))
                    if second is None:
                        self.assertEqual(labels[rows[1]], "Scenario 2 (no estimate)")
                        self.assertNotIn(rows[1], lines)
                    elif open_end:
                        self.assertEqual(labels[rows[1]], "Scenario 2 (≥ 40 h)")
                        self.assertEqual(lines[rows[1]][0], (40., ax.get_xlim()[1]))
                        self.assertGreater(ax.get_xlim()[1], 40.)
                        self.assertIsNotNone(lines[rows[1]][1])
                    else:
                        self.assertEqual(lines[rows[1]], (second, None))
                finally:
                    plt.close(fig)
