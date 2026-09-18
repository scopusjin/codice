import datetime as dt
import json
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest
from streamlit.proto.WidgetStates_pb2 import WidgetStates
import app.decimal_number_input_v2 as decimal_v2
from app.henssge import calcola_raffreddamento

ROOT = Path(__file__).resolve().parents[1]


class AuditPagesRegressionTests(unittest.TestCase):
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

    def edit_fc(self, app, key, value):
        candidates = [e for e in app.get('component_instance')
                      if json.loads(e.proto.json_args).get('key') in
                      ('mortem_decimal_' + key, 'mortem_decimal_' + key + '_range')]
        if candidates:
            element = candidates[0]
            data = json.loads(element.proto.json_args)
            payload = value
        else:
            element = next(e for e in app.get('bidi_component')
                           if e.proto.id.endswith('-mortem_decimal_' + key + '-v2'))
            data = json.loads(element.proto.json)
            payload = {'value': value}
        self.assertEqual(data['step'], .05)
        states = WidgetStates()
        widget = states.widgets.add()
        widget.id = element.proto.id
        widget.json_value = json.dumps(payload)
        app._run(states)
        self.assertFalse(app.exception)

    def test_auxiliary_pages_return_to_existing_main_page(self):
        app = self.start()
        for page in ('Impostazioni', '9_Reference', 'Raccomandazioni'):
            with self.subTest(page=page):
                app.switch_page(f'pages/{page}.py').run()
                app.button(key='back_home').click().run()
                self.assertFalse(app.exception)
                self.assertIsNotNone(app.button(key='btn_stima'))

    def test_manual_fc_rounding_survives_rerun_in_both_modes(self):
        app = self.start()
        self.edit_fc(app, 'fattore_correzione', 1.23)
        app.run()
        self.assertEqual(app.session_state['fattore_correzione'], 1.25)
        app.switch_page('pages/App_MSIL.py').run()
        self.edit_fc(app, 'fattore_correzione', 1.28)
        app.run()
        self.assertEqual(app.session_state['fattore_correzione'], 1.30)
        self.assertEqual(app.session_state['FC_max_beta'], 1.40)

    def test_both_full_range_endpoints_round_on_manual_input(self):
        app = self.start(stima_cautelativa_beta=True, range_unico_beta=True)
        self.edit_fc(app, 'fc_min_val', 1.23)
        self.edit_fc(app, 'fc_other_val', 1.43)
        app.run()
        self.assertEqual((app.session_state['FC_min_beta'], app.session_state['FC_max_beta']),
                         (1.25, 1.45))

    def test_weight_notice_clears_after_manual_fc_review(self):
        app = self.start(__fc_applied_choice={'range': [1., 1.], 'weight': 60.})
        self.assertTrue(any('Peso modificato' in w.value for w in app.warning))
        self.edit_fc(app, 'fattore_correzione', 1.23)
        self.assertFalse(any('Peso modificato' in w.value for w in app.warning))
        app.session_state['peso'] = 80.
        app.run()
        self.assertTrue(any('Peso modificato' in w.value for w in app.warning))
        app.switch_page('pages/App_MSIL.py').run()
        self.assertTrue(any('Peso modificato' in w.value for w in app.warning))

    def test_result_uses_actual_inspection_minute_and_settings_invalidate_it(self):
        app = self.start(input_data_rilievo=dt.date(2026, 1, 2), input_ora_rilievo='12:07',
                         input_ora_rilievo__manual=True, input_ora_rilievo_native='12:07',
                         henssge_round_minutes=6)
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        times = calcola_raffreddamento(30, 20, 37.2, 70, 1, round_minutes=6)
        inspection = dt.datetime(2026, 1, 2, 12, 7)
        for hours in (times[1], times[2]):
            self.assertIn((inspection - dt.timedelta(hours=hours)).strftime('%H:%M'),
                          app.session_state['frase_breve'])
        app.session_state['henssge_round_minutes'] = 15
        app.run()
        self.assertFalse(app.session_state['show_results'])

    def test_invalid_weight_fc_domain_reports_without_crashing(self):
        app = self.start(peso=150., fattore_correzione=3.)
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('combinazione di FC e peso' in w.value for w in app.warning))
        self.assertIsNone(app.session_state['frase_breve'])
