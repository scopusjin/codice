import unittest
from streamlit.testing.v1 import AppTest
from test_mixed_cooling_description import SCRIPT
from app.case_file import snapshot_case
from app.case_report import plain_text


class DetailedInputsDownloadTests(unittest.TestCase):
    def test_range_includes_measured_values_and_current_download(self):
        script = SCRIPT.replace('options = dict(', '''st.session_state.update(show_results=True, case_code="X26.123", peso=85.,
    __word_return={"case_code":"X26.123", "request_id":"a"*32})
options = dict(''')
        app = AppTest.from_string(script, default_timeout=30).run()
        self.assertFalse(app.exception)
        html = app.session_state['__desc_dettagliate_html']
        text = plain_text(html)
        for value in ('Temperatura ambientale: 11.0 °C', 'Temperatura rettale: 17.1 °C',
                      'Peso del cadavere misurato in sala autoptica: 85 kg',
                      'Temperatura corporea ipotizzata al momento della morte: 37.2 °C',
                      'Range di temperature ambientali medie'):
            self.assertIn(value, text)
        self.assertEqual(text.count('Peso del cadavere'), 1)
        self.assertEqual([b.proto.label for b in app.get('download_button')], ['Scarica caso'])
        self.assertTrue(any('stessa cartella del documento Word' in c.value for c in app.caption))
        case = snapshot_case(app.session_state._state.filtered_state, 'full')
        self.assertEqual(case['report']['detailed_html'], html)
        self.assertIn('1.40', case['report']['word_blocks']['correction_factor']['text'])

    def test_normal_launch_has_download_without_word_hint(self):
        app = AppTest.from_string(SCRIPT, default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('download_button')), 1)
        self.assertFalse(any('stessa cartella' in c.value for c in app.caption))

    def test_single_values_title_has_no_time(self):
        from datetime import datetime
        from app.textgen import paragrafo_raffreddamento_input
        html = paragrafo_raffreddamento_input(isp_dt=datetime(2026,8,7,11,50),
            ta_val=25.5, tr_val=33.9, w_val=72, t0_val=37.2, cf_descr='1.00')
        self.assertIn('Temperature misurate nel corso dell’ispezione legale:', html)
        self.assertNotIn('11:50', html)
