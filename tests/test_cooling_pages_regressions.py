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
                self.toggle_range(app, mobile)
                self.assertFalse(app.exception)
                app.session_state['ta_other_val'] = 24.
                app.run()
                self.assertEqual(app.session_state['Ta_max_beta'], 24.)
                self.toggle_range(app, mobile)
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state['Ta_max_beta'], 20.)
                self.assertEqual(app.session_state['FC_min_beta'], 1.4)
                self.assertEqual(app.session_state['FC_max_beta'], 1.8)

    def test_temperature_range_can_start_with_single_fc(self):
        app = self.start()
        app.button(key='ambient_temperature_range_toggle').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['FC_min_beta'], 1.)
        self.assertEqual(app.session_state['FC_max_beta'], 1.)
        app.session_state['ta_other_val'] = 25.
        app.run()
        self.assertEqual(app.session_state['Ta_max_beta'], 25.)

    def test_scenario_temperatures_control_range_and_disable_manual_mode(self):
        from test_fc_scenarios import temperature_payload
        for mobile in (False, True):
            for same_temperature in (False, True):
                with self.subTest(mobile=mobile, same_temperature=same_temperature):
                    choice = temperature_payload()
                    if same_temperature:
                        choice['scenarios'][1]['temperature'] = 20.
                        choice['scenarios'][1]['draft']['temperature'] = '20.0'
                    app = self.start(__full_device_mobile=mobile,
                                     stima_cautelativa_beta=True,
                                     __prudent_explicit_ranges_initialized=True,
                                     __fc_applied_choice=choice,
                                     fc_min_val=1.35, fc_other_val=1.4)
                    if same_temperature and not mobile:
                        self.assertTrue(app.button(key='ambient_temperature_range_toggle').disabled)
                    else:
                        self.assertFalse(any(button.key == 'ambient_temperature_range_toggle' for button in app.button))
                    self.assertEqual(app.session_state['ambient_temperature_range'], not same_temperature)
                    self.assertEqual(app.session_state['Ta_min_beta'], 20. if same_temperature else 8.)
                    self.assertEqual(app.session_state['Ta_max_beta'], 20.)

    def toggle_range(self, app, mobile):
        if mobile:
            from app.ambient_temperature import toggle_temperature_mode
            self.assertFalse(any(button.key == 'ambient_temperature_range_toggle' for button in app.button))
            toggle_temperature_mode(app.session_state)
            app.run()
        else:
            app.button(key='ambient_temperature_range_toggle').click().run()

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

    def test_home_temperature_action_preserves_fc_mode_without_fc_button(self):
        for mobile in (False, True):
            for fc_range in (False, True):
                with self.subTest(mobile=mobile, fc_range=fc_range):
                    app = self.start(__full_device_mobile=mobile,
                                     stima_cautelativa_beta=fc_range,
                                     __prudent_explicit_ranges_initialized=True,
                                     ambient_temperature_range=False,
                                     fc_input_range=fc_range,
                                     fc_min_val=1., fc_other_val=1.4 if fc_range else 1.)
                    self.assertFalse(any(b.key == 'fc_range_toggle' for b in app.button))
                    for _ in range(2):
                        self.toggle_range(app, mobile)
                        self.assertEqual(app.session_state['fc_input_range'], fc_range)
                        self.assertEqual(app.session_state['FC_min_beta'], 1.)
                        self.assertEqual(app.session_state['FC_max_beta'], 1.4 if fc_range else 1.)
                        self.assertFalse(any(b.key == 'fc_range_toggle' for b in app.button))

    def test_scenarios_hide_fc_mode_action_and_preserve_bounds(self):
        from test_fc_scenarios import temperature_payload
        app = self.start(__fc_applied_choice=temperature_payload(),
                         stima_cautelativa_beta=True,
                         __prudent_explicit_ranges_initialized=True,
                         fc_min_val=1.35, fc_other_val=1.4)
        self.assertTrue(app.session_state['fc_input_range'])
        self.assertFalse(any(b.key == 'fc_range_toggle' for b in app.button))
        app.run()
        self.assertTrue(app.session_state['fc_input_range'])
        self.assertEqual(app.session_state['FC_min_beta'], 1.35)
        self.assertEqual(app.session_state['FC_max_beta'], 1.4)

    def test_sopralluogo_is_not_an_active_page(self):
        # Its scientific helpers remain tested separately; navigation is suspended.
        self.assertFalse((ROOT / 'pages/App_MSIL.py').exists())
        self.assertTrue((ROOT / 'disabled_pages/App_MSIL.py').is_file())

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

                app.session_state['selettore_macchie_ui'] = 'Parzialmente migrabili'
                app.run()
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
        # With independent FC intervals, exercise the missing upper endpoint
        # explicitly. A valid inspection time isolates cooling validation.
        app = self.start(stima_cautelativa_beta=True,
                         __prudent_explicit_ranges_initialized=True,
                         fc_input_range=True,
                         input_ora_rilievo='11:28',
                         input_ora_rilievo_native='11:28',
                         fc_min_val=1.4, fc_other_val=None, ta_other_val=20.)
        app.session_state['selettore_macchie_ui'] = 'Parzialmente migrabili'
        app.run()
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('fattore di correzione' in warning.value.lower()
                            for warning in app.markdown),
                        [warning.value for warning in app.markdown])
        self.assertIsNotNone(app.session_state['frase_breve'])
        self.assertNotIn('Applicando l’equazione', app.session_state['__desc_dettagliate_html'])
        self.assertNotIn("Applicando l'equazione", app.session_state['__desc_dettagliate_html'])
        self.assertNotRegex(app.session_state['__desc_dettagliate_html'], r'<(?:b|strong)\b')

    def test_missing_rectal_temperature_is_named_in_final_note_in_both_layouts(self):
        for mobile in (False, True):
            with self.subTest(mobile=mobile):
                app = self.start(rt_val=None, __full_device_mobile=mobile,
                                 input_ora_rilievo='11:28',
                                 input_ora_rilievo_native='11:28',
                                 selettore_macchie_ui='Parzialmente migrabili')
                app.button(key='btn_stima').click().run()
                self.assertFalse(app.exception)
                self.assertIsNotNone(app.session_state['frase_breve'])
                notes = [item.value for item in app.markdown
                         if 'Raffreddamento non calcolato' in item.value]
                self.assertEqual(len(notes), 1)
                self.assertIn('temperatura rettale', notes[0])
                self.assertIn('#a66b00', notes[0])
                self.assertIn('font-size:8pt', notes[0])

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
        self.assertTrue(any('peso' in warning.value.lower() for warning in app.markdown))

    def test_empty_temperature_max_does_not_invent_an_interval(self):
        app = self.start(stima_cautelativa_beta=True,
                         __prudent_explicit_ranges_initialized=True, ta_other_val=None)
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('temperatura' in warning.value for warning in app.markdown))
        self.assertIsNone(app.session_state['frase_breve'])

    def test_zero_fc_shows_warning_without_crashing(self):
        app = self.start()
        app.session_state['fattore_correzione'] = 0.
        app.run()
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('FC' in warning.value for warning in app.markdown))
