import re
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest
import app.decimal_number_input_v2 as decimal_v2

ROOT = Path(__file__).resolve().parents[1]


class CoolingPagesRegressionTests(unittest.TestCase):
    def start(self, **values):
        decimal_v2._renderer = None
        app = AppTest.from_file(str(ROOT / 'Stima_epoca_decesso.py'), default_timeout=30)
        defaults = dict(__full_device_mobile=False, rt_val=30., ta_base_val=20.,
                        tm_val=37.2, peso=70., fattore_correzione=1.)
        for key, value in {**defaults, **values}.items():
            app.session_state[key] = value
        app.run()
        self.assertFalse(app.exception)
        return app

    def test_sopralluogo_calculation_is_independent_of_full_mode(self):
        results = []
        for prudent in (False, True):
            app = self.start(stima_cautelativa_beta=prudent, peso_stimato_beta=prudent)
            app.switch_page('pages/App_MSIL.py').run()
            app.button(key='btn_stima_mobile').click().run()
            self.assertFalse(app.exception)
            text = app.session_state['__desc_dettagliate_html']
            self.assertIn('19.0', text)
            self.assertIn('67', text)
            results.append(re.sub('<[^>]+>', '', app.session_state['frase_breve']))
            app.switch_page('Stima_epoca_decesso.py').run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['stima_cautelativa_beta'], prudent)
            self.assertEqual(app.session_state['peso_stimato_beta'], prudent)
        self.assertEqual(results[0], results[1])

    def test_empty_fc_max_excludes_cooling_but_keeps_other_parameters(self):
        app = self.start(stima_cautelativa_beta=True,
                         __prudent_explicit_ranges_initialized=True,
                         fc_min_val=1.4, fc_other_val=None, ta_other_val=20.)
        app.selectbox[0].select(app.selectbox[0].options[1]).run()
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('FC' in warning.value for warning in app.warning))
        self.assertIsNotNone(app.session_state['frase_breve'])
        self.assertNotIn('Applicando l’equazione', app.session_state['__desc_dettagliate_html'])
        self.assertNotIn("Applicando l'equazione", app.session_state['__desc_dettagliate_html'])

    def test_temperature_order_is_invariant_in_full_results(self):
        results = []
        for first, second in [(20., 35.), (35., 20.)]:
            app = self.start(stima_cautelativa_beta=True,
                             __prudent_explicit_ranges_initialized=True,
                             ta_base_val=first, ta_other_val=second)
            app.button(key='btn_stima').click().run()
            self.assertFalse(app.exception)
            results.append((app.session_state['frase_breve'],
                            app.session_state['__desc_dettagliate_html']))
        self.assertEqual(results[0], results[1])

    def test_explicit_intervals_and_results_match_on_desktop_and_mobile(self):
        results = []
        for mobile in (False, True):
            with self.subTest(mobile=mobile):
                app = self.start(__full_device_mobile=mobile,
                                 stima_cautelativa_beta=True,
                                 __prudent_explicit_ranges_initialized=True,
                                 ta_base_val=20., ta_other_val=18.,
                                 fc_min_val=1.3, fc_other_val=1.1)
                app.button(key='btn_stima').click().run()
                self.assertFalse(app.exception)
                self.assertEqual(
                    tuple(app.session_state[key] for key in
                          ('Ta_min_beta', 'Ta_max_beta', 'FC_min_beta', 'FC_max_beta')),
                    (18., 20., 1.1, 1.3),
                )
                # Ordering the calculation bounds must not reorder the inputs.
                self.assertEqual(
                    tuple(app.session_state[key] for key in
                          ('ta_base_val', 'ta_other_val', 'fc_min_val', 'fc_other_val')),
                    (20., 18., 1.3, 1.1),
                )
                results.append((app.session_state['frase_breve'],
                                app.session_state['__desc_dettagliate_html']))
                self.assertIsNotNone(results[-1][0])
        self.assertEqual(results[0], results[1])

    def test_cleared_interval_endpoint_removes_old_bounds_in_both_layouts(self):
        fields = {'ta_base_val': 20., 'ta_other_val': 18.,
                  'fc_min_val': 1.3, 'fc_other_val': 1.1}
        for mobile in (False, True):
            app = self.start(__full_device_mobile=mobile,
                             stima_cautelativa_beta=True,
                             __prudent_explicit_ranges_initialized=True, **fields)
            for field, value in fields.items():
                with self.subTest(mobile=mobile, field=field):
                    output_keys = (('Ta_min_beta', 'Ta_max_beta')
                                   if field.startswith('ta_')
                                   else ('FC_min_beta', 'FC_max_beta'))
                    app.session_state[field] = None
                    app.run()
                    self.assertFalse(app.exception)
                    for key in output_keys:
                        self.assertNotIn(key, app.session_state)
                    app.session_state[field] = value
                    app.run()
                    self.assertFalse(app.exception)
                    self.assertEqual(
                        tuple(app.session_state[key] for key in output_keys),
                        (18., 20.) if field.startswith('ta_') else (1.1, 1.3),
                    )

    def test_estimated_weight_containing_zero_shows_warning(self):
        app = self.start(peso=2., stima_cautelativa_beta=True, peso_stimato_beta=True)
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('peso' in warning.value.lower() for warning in app.warning))

    def test_empty_temperature_max_does_not_invent_an_interval(self):
        app = self.start(stima_cautelativa_beta=True,
                         __prudent_explicit_ranges_initialized=True, ta_other_val=None)
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('temperatura' in warning.value for warning in app.warning))
        self.assertIsNone(app.session_state['frase_breve'])

    def test_zero_fc_shows_warning_without_crashing(self):
        app = self.start()
        app.session_state['fattore_correzione'] = 0.
        app.run()
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('FC' in warning.value for warning in app.warning))
