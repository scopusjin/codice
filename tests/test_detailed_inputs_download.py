import re
import unittest
from streamlit.testing.v1 import AppTest
from test_mixed_cooling_description import SCRIPT
from app.case_file import decode_case, encode_case, snapshot_case
from app.case_report import plain_text


class DetailedInputsDownloadTests(unittest.TestCase):
    def test_qd_range_is_display_only_and_exported_conclusion_has_two_gaps(self):
        script = '''
import datetime
import streamlit as st
from app.graphing import aggiorna_grafico
st.session_state.update(show_results=True, case_code="X26.123", peso=70.)
aggiorna_grafico(selettore_macchie="Fisse", selettore_rigidita="Presente, intensa e generalizzata",
    input_rt=26.4, input_ta=15., input_tm=37.2, input_w=70., fattore_correzione=1.,
    widgets_parametri_aggiuntivi={}, usa_orario_custom=True,
    input_data_rilievo=datetime.date(2026,11,4), input_ora_rilievo="11:45",
    alterazioni_putrefattive=False, skip_warnings=True,
    cooling_options=dict(stima_cautelativa_beta=True, Ta_min_beta=15., Ta_max_beta=16.5,
                         FC_min_beta=1., FC_max_beta=1.))
'''
        app = AppTest.from_string(script, default_timeout=30).run()
        self.assertFalse(app.exception)
        shown = '\n'.join(m.value for m in app.markdown)
        self.assertIn('il valore di Qd varia da 0.478 a 0.514', shown)
        report = decode_case(encode_case(snapshot_case(app.session_state._state.filtered_state, 'full')))['report']
        for output in (report['detailed_html'], report['detailed_text'], str(report['word_blocks'])):
            self.assertNotIn('Il parametro Qd esprime', output)
            self.assertNotIn('il valore di Qd varia', output)
        for html in (report['detailed_html'], report['word_blocks']['conclusion']['html']):
            paragraphs = re.findall(r'<p\b[^>]*>(.*?)</p>', html, re.S)
            index = next(i for i, p in enumerate(paragraphs) if p.startswith('La valutazione combinata'))
            self.assertEqual(paragraphs[index-1], '&nbsp;')
            self.assertEqual(paragraphs[index+1], '&nbsp;')
            self.assertTrue(paragraphs[index+2].startswith('<i>Va ricordato'))
            self.assertTrue(paragraphs[index+3].startswith('<i>La stima dell’epoca'))
        self.assertRegex(report['detailed_text'], r'\n\nLa valutazione combinata[^\n]+\n\nVa ricordato')

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
