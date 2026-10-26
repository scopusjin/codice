import unittest
from app.word_launch import launch_values


class WordLaunchTests(unittest.TestCase):
    def test_invalid_export_does_not_stop_the_page(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_string('''
import streamlit as st
from app.case_ui import render_case_menu
st.session_state.update(case_code="X26.117", __word_return={"case_code":"X26.117"},
    __fc_applied_choice={"draft":{"unexpected":True}})
render_case_menu("Stima_epoca_decesso.py")
st.button("Procedi con la stima")
''').run()
        next(b for b in app.button if b.label == "Caso").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertTrue(any(b.label == "Procedi con la stima" for b in app.button))

    def test_example_and_missing_data(self):
        v = launch_values(dict(mt_open='1', mt_case='X26.115', mt_date='17.10.2026',
            mt_time='14:25', mt_weight='85', mt_ta='11', mt_tr='17.1'))
        self.assertEqual(v['peso'], 85)
        self.assertEqual(v['input_data_rilievo'].isoformat(), '2026-10-17')
        self.assertEqual(v['rt_val'], 17.1)
        self.assertEqual(launch_values(dict(mt_open='1', mt_case='X26.115')),
                         dict(case_code='X26.115', usa_orario_custom=False))
        for extra in ({'mt_weight':'NaN'}, {'mt_date':'31.02.2026'}, {'mt_time':'99:00'}, {'mt_case':'bad'}):
            with self.assertRaises(ValueError):
                launch_values(dict(mt_open='1', **({'mt_case':'X26.115'} | extra)))

    def test_actual_page_prefill(self):
        from pathlib import Path
        from streamlit.testing.v1 import AppTest
        import app.decimal_number_input_v2 as decimal_v2
        decimal_v2._renderer = None
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'Stima_epoca_decesso.py'), default_timeout=30)
        app.query_params.update(mt_open='1', mt_case='X26.115', mt_weight='85', mt_ta='11', mt_tr='17.1',
                                mt_date='17.10.2026', mt_time='14:25')
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['case_code'], 'X26.115')
        self.assertEqual(app.session_state['peso'], 85)
        self.assertEqual(app.session_state['rt_val'], 17.1)
        self.assertEqual(app.session_state['input_ora_rilievo'], '14:25')
        self.assertNotIn('mt_open', app.query_params)

    def test_word_result_binding_stale_inputs_and_normal_open(self):
        from app.word_launch import word_result
        from app.case_report import capture_report
        from app.case_file import decode_case, restored_inputs, CaseFileError
        token = 'a' * 32
        state = {'case_code': 'X26.115', 'peso':85, 'show_results':True,
                 '__desc_dettagliate_html':'<p>Risultato.</p>',
                 '__word_report_blocks':{'cooling':{'html':'<p>Risultato.</p>', 'text':'Risultato.', 'insert_when':'always'}}}
        capture_report(state, 'full')
        self.assertIsNone(word_result(state, 'full'))
        state['__word_return'] = {'request_id':token, 'case_code':'X26.115'}
        raw, filename = word_result(state, 'full')
        case = decode_case(raw)
        self.assertEqual(filename, 'stimaX26.115.json')
        self.assertEqual(case['word_return']['request_id'], token)
        self.assertNotIn('__word_return', restored_inputs(case))
        state['peso'] = 90
        self.assertIsNone(word_result(state, 'full'))
        state['case_code'] = 'X26.116'
        self.assertIsNone(word_result(state, 'full'))
        for invalid in ('../bad', 'a'*33):
            with self.assertRaises(ValueError):
                launch_values(dict(mt_open='1', mt_case='X26.115', mt_request=invalid))

    def test_normal_case_download_contains_report_in_word_session(self):
        from pathlib import Path
        from unittest.mock import patch
        from streamlit.testing.v1 import AppTest
        from app.case_file import encode_case
        import app.decimal_number_input_v2 as decimal_v2
        decimal_v2._renderer = None
        path = str(Path(__file__).resolve().parents[1] / 'Stima_epoca_decesso.py')
        app = AppTest.from_file(path, default_timeout=30).run()
        self.assertFalse(app.exception)
        with self.assertRaises(KeyError):
            app.session_state['__word_return']
        app.query_params.update(mt_open='1', mt_case='X26.115', mt_request='b'*32)
        app.run()
        self.assertEqual(app.session_state['__word_return']['request_id'], 'b'*32)
        app.session_state['selettore_macchie'] = 'Fisse'
        app.session_state['selettore_macchie_ui'] = 'Fisse'
        app.run()
        app.button(key='btn_stima').click().run()
        next(b for b in app.button if b.label == 'Caso').click()
        captured=[]
        def export(case):
            captured.append(case)
            return encode_case(case)
        with patch('app.case_ui.encode_case',side_effect=export):
            app.run()
        self.assertFalse(app.exception)
        self.assertTrue(captured)
        self.assertTrue(captured[-1]['report']['word_blocks'])
        labels=[b.proto.label for b in app.get('download_button')]
        self.assertIn('Scarica caso',labels)
        self.assertNotIn('Scarica riepilogo per Word',labels)
