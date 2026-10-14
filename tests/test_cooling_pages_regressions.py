import datetime
import re
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest
import app.decimal_number_input_v2 as decimal_v2

ROOT = Path(__file__).resolve().parents[1]


class CoolingPagesRegressionTests(unittest.TestCase):
    def test_temperature_mode_is_independent_of_fc_range(self):
        for mobile in (False, True):
            with self.subTest(mobile=mobile):
                app = self.start(__full_device_mobile=mobile, stima_cautelativa_beta=True,
                                 __prudent_explicit_ranges_initialized=True,
                                 ambient_temperature_range=False, ta_other_val=28.,
                                 fc_min_val=1.4, fc_other_val=1.8)
                self.assertEqual(app.session_state['Ta_min_beta'], 20.)
                self.assertEqual(app.session_state['Ta_max_beta'], 20.)
                app.checkbox(key='ambient_temperature_range').check().run()
                self.assertFalse(app.exception)
                app.session_state['ta_other_val'] = 24.
                app.run()
                self.assertEqual(app.session_state['Ta_max_beta'], 24.)
                app.checkbox(key='ambient_temperature_range').uncheck().run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state['Ta_max_beta'], 20.)
                self.assertEqual(app.session_state['FC_min_beta'], 1.4)
                self.assertEqual(app.session_state['FC_max_beta'], 1.8)

    def test_temperature_range_can_start_with_single_fc(self):
        app = self.start()
        app.checkbox(key='ambient_temperature_range').check().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['FC_min_beta'], 1.)
        self.assertEqual(app.session_state['FC_max_beta'], 1.)
        app.session_state['ta_other_val'] = 25.
        app.run()
        self.assertEqual(app.session_state['Ta_max_beta'], 25.)

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
            self.assertNotRegex(text, r'<(?:b|strong)\b|font-weight\s*:\s*(?:bold|[6-9]00)')
            results.append(re.sub('<[^>]+>', '', app.session_state['frase_breve']))
            app.switch_page('Stima_epoca_decesso.py').run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['stima_cautelativa_beta'], prudent)
            self.assertEqual(app.session_state['peso_stimato_beta'], prudent)
        self.assertEqual(results[0], results[1])

    def test_detailed_conclusion_distinguishes_one_parameter_from_combined_data(self):
        for with_datetime in (False, True):
            with self.subTest(with_datetime=with_datetime):
                values = dict(input_data_rilievo=datetime.date(2026, 10, 14))
                if with_datetime:
                    values['input_ora_rilievo'] = '11:28'
                app = self.start(**values)
                app.button(key='btn_stima').click().run()
                self.assertFalse(app.exception)
                detail = app.session_state['__desc_dettagliate_html']
                self.assertEqual('La valutazione dei dati disponibili porta a stimare' in detail,
                                 with_datetime)
                self.assertNotIn('La valutazione combinata', detail)
                self.assertIn("Applicando l'equazione di Henssge", detail)
                if with_datetime:
                    conclusion = detail.split('La valutazione dei dati disponibili', 1)[1]
                    self.assertIn('del 14.10.2026', conclusion)
                    self.assertNotIn('prima dei rilievi', conclusion)
                else:
                    self.assertEqual(detail.count('prima dei rilievi effettuati'), 1)
                self.assertNotIn('EPOCA DEL DECESSO STIMATA:', detail)
                self.assertIn('EPOCA DEL DECESSO STIMATA:', app.session_state['frase_breve'])

                app.selectbox[0].select('Parzialmente migrabili').run()
                app.button(key='btn_stima').click().run()
                self.assertFalse(app.exception)
                detail = app.session_state['__desc_dettagliate_html']
                self.assertIn('La valutazione combinata dei dati tanatologici', detail)
                self.assertNotIn('La valutazione dei dati disponibili', detail)

                # The fallback without cooling still has one available parameter.
                app.session_state['rt_val'] = None
                app.run()
                app.button(key='btn_stima').click().run()
                self.assertFalse(app.exception)
                detail = app.session_state['__desc_dettagliate_html']
                self.assertEqual('La valutazione dei dati disponibili porta a stimare' in detail,
                                 with_datetime)
                self.assertNotIn('La valutazione combinata', detail)

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
        self.assertNotRegex(app.session_state['__desc_dettagliate_html'], r'<(?:b|strong)\b')

    def test_missing_rectal_temperature_is_named_in_both_views(self):
        for msil in (False, True):
            with self.subTest(msil=msil):
                app = self.start(rt_val=None)
                if msil:
                    app.switch_page('pages/App_MSIL.py').run()
                app.button(key='btn_stima_mobile' if msil else 'btn_stima').click().run()
                self.assertFalse(app.exception)
                self.assertTrue(any('Manca la temperatura rettale.' in warning.value
                                    for warning in app.warning))
                app.selectbox[0].select(app.selectbox[0].options[1]).run()
                app.button(key='btn_stima_mobile' if msil else 'btn_stima').click().run()
                self.assertFalse(app.exception)
                self.assertIsNotNone(app.session_state['frase_breve'])
                self.assertTrue(any('Manca la temperatura rettale.' in warning.value
                                    for warning in app.warning))

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
                self.assertNotRegex(results[-1][1], r'<(?:b|strong)\b|font-weight\s*:\s*(?:bold|[6-9]00)')
                self.assertIn('<b>', results[-1][0])  # The separate result summary keeps its formatting.
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
