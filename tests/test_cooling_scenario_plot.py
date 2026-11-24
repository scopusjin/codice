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

    def test_scenarios_share_one_row_and_legend_below_the_axis(self):
        for second in ((9., 16.), (20., 26.), (6., 12.), (40., np.inf), None):
            with self.subTest(second=second), using_language("en"):
                open_end = second is not None and np.isinf(second[1])
                overall_end = max(12., second[1]) if second is not None else 12.
                extras = [{"label": "Body cooling", "start": 6., "end": np.inf, "is_potente": True}] if open_end else []
                extras.append({"label": "Other", "start": 1., "end": 4.})
                data = compute_plot_data(macchie_range=(0., 6.), macchie_medi_range=None,
                    rigidita_range=(2., 20.), rigidita_medi_range=(4., 8.),
                    raffreddamento_calcolabile=not open_end, t_min_raff_henssge=6., t_max_raff_henssge=overall_end,
                    t_med_raff_henssge_rounded_raw=9., Qd_val_check=.8, mt_ore=None, INF_HOURS=200.,
                    qd_threshold=.2, extra_params=extras, scenario_ranges=((6., 12.), second))
                for mobile in (False, True):
                    with self.subTest(mobile=mobile):
                        temperatures = (20., 20.) if second == (6., 12.) else (20., 18.25)
                        scenarios = [dict(range=[1., 1.], temperature=temperatures[0]),
                                     dict(range=[1.2, 1.3], temperature=temperatures[1])]
                        fig = render_ranges_plot(data, mobile=mobile, scenarios=scenarios,
                                                 common_range=(6., 9.) if open_end else None)
                        try:
                            fig.canvas.draw()
                            ax = fig.axes[0]
                            row = data["scenario_row"]
                            labels = [tick.get_text() for tick in ax.get_yticklabels()]
                            self.assertEqual(len(labels), 4)
                            summary = "≥ 6 h" if open_end else f"6–{overall_end:g} h"
                            self.assertEqual(labels[row], f"({summary})")
                            self.assertEqual(ax.texts[row].get_text(), "Body cooling")
                            aggregate = [(tuple(segment[:, 0]), line.get_linewidths()[0])
                                         for line in ax.collections for segment in line.get_segments()
                                         if (segment[:, 1] == row).all()]
                            self.assertEqual(aggregate[0][0][0], 6.)
                            end = ax.get_xlim()[1] if open_end else overall_end
                            self.assertEqual(aggregate[-1][0][1], end)
                            self.assertTrue(all(width == data["style_flags"]["line_w"] for _, width in aggregate))
                            if open_end:
                                self.assertEqual(aggregate[0][0][1], aggregate[-1][0][0])
                            self.assertEqual(labels[data["extra_rows"][-1]], "(1–4 h)")
                            self.assertEqual(ax.texts[data["extra_rows"][-1]].get_text(), "Other")
                            legend = fig.legends[0]
                            names = [item.get_text() for item in legend.texts]
                            self.assertLess(legend.get_window_extent().y1, ax.xaxis.label.get_window_extent().y0)
                            self.assertTrue(fig.bbox.contains(*legend.get_window_extent().min))
                            self.assertTrue(fig.bbox.contains(*legend.get_window_extent().max))
                            self.assertEqual(names[0], "Limits used for the estimate")
                            shared = temperatures[0] == temperatures[1]
                            self.assertEqual(names[1], "Body cooling – CF 1.00" + (
                                "" if shared else " · Ambient temp. 20.0 °C"))
                            second_name = "Body cooling – CF 1.20–1.30" + (
                                "" if shared else " · Ambient temp. 18.25 °C")
                            if second is None:
                                second_name += ("\n" if mobile else " ") + "(no estimate)"
                            self.assertEqual(names[2], second_name)
                            self.assertEqual([t.get_text() for t in ax.texts[len(labels):]], ["Common interval"] if open_end else [])
                            self.assertEqual(len(names), 3)
                            first, other = (line for line in ax.lines if line.get_label() in names)
                            self.assertEqual(tuple(first.get_xdata()), (6., 12.))
                            self.assertEqual(tuple(first.get_ydata()), (row, row))
                            center = ax.transData.transform((0, row))[1]
                            top_scenario = first.get_transform().transform((0, row))[1]
                            self.assertGreater((center - top_scenario) * 72 / fig.dpi,
                                               (aggregate[0][1] + first.get_linewidth()) / 2)
                            self.assertGreater(aggregate[0][1], first.get_linewidth())
                            if second is None:
                                self.assertEqual(len(other.get_xdata()), 0)
                                continue
                            self.assertEqual(tuple(other.get_ydata()), (row, row))
                            gap = first.get_transform().transform((0, row))[1] - other.get_transform().transform((0, row))[1]
                            self.assertGreater(gap * 72 / fig.dpi, first.get_linewidth())
                            self.assertLess(gap * 72 / fig.dpi, 6.)
                            if open_end:
                                self.assertEqual(tuple(other.get_xdata()), (40., ax.get_xlim()[1]))
                                self.assertGreater(ax.get_xlim()[1], 40.)
                                self.assertTrue(other.is_dashed())
                            else:
                                self.assertEqual(tuple(other.get_xdata()), second)
                                self.assertFalse(other.is_dashed())
                        finally:
                            plt.close(fig)
