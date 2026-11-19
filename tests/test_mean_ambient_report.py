"""The app documents means; Word alone can supply the measured ambient value."""
from html.parser import HTMLParser
import unittest

from streamlit.testing.v1 import AppTest
from app.case_file import decode_case, encode_case, snapshot_case
from app.case_report import plain_text
from app.language import using_language
from app.textgen import paragrafo_raffreddamento_input


class MeanItems(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.items = []
        self.current = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'li' and attrs.get('class') == 'mortem-ambient-mean':
            self.current = {'attrs': attrs, 'text': ''}
            self.items.append(self.current)

    def handle_data(self, data):
        if self.current is not None:
            self.current['text'] += data

    def handle_endtag(self, tag):
        if tag == 'li':
            self.current = None


class MeanAmbientReportTests(unittest.TestCase):
    def test_thermal_equilibrium_export_keeps_examination_context_without_repeating_temperature(self):
        for language, equilibrium, context in (
            ('it', 'l’equilibrio termico con l’ambiente', 'al momento dell’ispezione legale'),
            ('en', 'thermal equilibrium with its surroundings', 'at the time of the medico-legal examination'),
        ):
            for temperature in (20., 25.):
                with self.subTest(language=language, temperature=temperature):
                    script = f'''
import datetime
import streamlit as st
from app.graphing import aggiorna_grafico
st.session_state.update(mortem_language={language!r}, show_results=True,
    peso=70., rt_val={temperature}, ta_base_val={temperature})
aggiorna_grafico(selettore_macchie="Non valutate", selettore_rigidita="Non valutata",
    input_rt={temperature}, input_ta={temperature}, input_tm=37.2, input_w=70., fattore_correzione=1.,
    widgets_parametri_aggiuntivi={{}}, usa_orario_custom=True,
    input_data_rilievo=datetime.date(2026,11,7), input_ora_rilievo="11:30",
    alterazioni_putrefattive=False, skip_warnings=True, cooling_options={{}})
'''
                    app = AppTest.from_string(script, default_timeout=30).run()
                    self.assertFalse(app.exception)
                    with using_language(language):
                        report = decode_case(encode_case(snapshot_case(
                            app.session_state._state.filtered_state, 'full')))['report']
                    for html in (report['detailed_html'], report['word_blocks']['cooling']['html']):
                        self.assertEqual(html.count(equilibrium), 1)
                        self.assertIn(context, html)
                        self.assertIn('Henssge', html)
                        self.assertIn('Potente', html)
                        self.assertNotIn('{temperature}', html)
                    self.assertNotIn(f'{temperature:.1f} °C', report['word_blocks']['cooling']['text'])
                    self.assertIn(f'{temperature:.1f} °C',
                                  report['word_blocks']['ambient_temperature']['text'])

    def test_standard_report_labels_only_the_mean_and_keeps_water_qualification(self):
        for language in ('it', 'en'):
            for temperature in (-2.5, 0., 20.):
                with self.subTest(language=language, temperature=temperature), using_language(language):
                    html = paragrafo_raffreddamento_input(
                        isp_dt=None, ta_val=temperature, tr_val=32.5, w_val=70.,
                        t0_val=37.2, cf_descr='1.00',
                        ambient_temperature_text=f'{temperature:.1f} °C (water)')
                    items = MeanItems(html).items
                    self.assertEqual(len(items), 1)
                    self.assertEqual(items[0]['attrs']['lang'], language)
                    self.assertEqual(items[0]['attrs']['data-mortem-range'], '0')
                    self.assertIn(f'{temperature:.1f} °C (water)', items[0]['text'])
                    self.assertIn('32.5 °C', html)
                    self.assertIn('37.2 °C', html)
                    self.assertNotIn('Temperatura ambientale:', html)
                    self.assertNotIn('Ambient temperature:', html)

    def test_export_preserves_mean_or_range_in_both_languages(self):
        for language in ('it', 'en'):
            for lower, upper in ((20., 20.), (15., 20.)):
                with self.subTest(language=language, temperatures=(lower, upper)):
                    script = f'''
import datetime
import streamlit as st
from app.graphing import aggiorna_grafico
st.session_state.update(mortem_language={language!r}, show_results=True,
    peso=70., ta_base_val={lower}, ta_other_val={upper})
aggiorna_grafico(selettore_macchie="Non valutate", selettore_rigidita="Non valutata",
    input_rt=30., input_ta=22., input_tm=37.2, input_w=70., fattore_correzione=1.,
    widgets_parametri_aggiuntivi={{}}, usa_orario_custom=False,
    input_data_rilievo=datetime.date(2026,11,6), input_ora_rilievo=None,
    alterazioni_putrefattive=False, skip_warnings=True,
    cooling_options=dict(stima_cautelativa_beta=True, Ta_min_beta={lower}, Ta_max_beta={upper},
                         FC_min_beta=1., FC_max_beta=1.2))
'''
                    app = AppTest.from_string(script, default_timeout=30).run()
                    self.assertFalse(app.exception)
                    state = app.session_state._state.filtered_state
                    with using_language(language):
                        report = decode_case(encode_case(snapshot_case(state, 'full')))['report']
                    html = report['detailed_html']
                    items = MeanItems(html).items
                    self.assertEqual(len(items), 1)
                    self.assertEqual(items[0]['attrs']['lang'], language)
                    self.assertEqual(items[0]['attrs']['data-mortem-range'], str(int(lower != upper)))
                    self.assertIn('20.0', items[0]['text'])
                    if lower != upper:
                        self.assertIn('15.0', items[0]['text'])
                    for text in (report['detailed_text'], plain_text(html),
                                 report['word_blocks']['ambient_temperature']['text']):
                        self.assertNotIn('22.0', text)
                        self.assertNotIn('Temperatura ambientale:', text)
                        self.assertNotIn('Ambient temperature:', text)
                    self.assertIn('30.0 °C', report['detailed_text'])
                    self.assertIn('37.2 °C', report['detailed_text'])


if __name__ == '__main__':
    unittest.main()
