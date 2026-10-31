import base64
import json
import unittest
from copy import deepcopy
from app.case_file import CaseFileError, snapshot_case, encode_case, restored_inputs
from app.word_resume import resume_case

class WordResumeTests(unittest.TestCase):
    def setUp(self):
        self.params = {'mt_case':'X26.84','mt_request':'a'*32}
        self.case = snapshot_case({'case_code':'X26.84','peso':72.,'rt_val':33.9,
            'ta_base_val':25.5, 'fc_input_range':True, 'fc_min_val':0.9,
            'fc_other_val':1.2, 'mostra_parametri_aggiuntivi':True,
            'selettore_macchie_ui':'Fisse'}, 'full', include_report=False)

    def event(self, case=None):
        return {'token':'a'*32,'data':base64.b64encode(encode_case(case or self.case)).decode()}

    def test_current_word_measurements_override_saved_values_only(self):
        from app.word_launch import apply_word_measurements
        original = deepcopy(self.case)
        updated = apply_word_measurements(self.case, {'peso':80., 'rt_val':30., 'ta_base_val':20.})
        state = restored_inputs(updated)
        self.assertEqual([state[k] for k in ('peso','rt_val','ta_base_val')], [80.,30.,20.])
        self.assertEqual(state['__full_standard_ta_base_val'],20.)
        self.assertEqual(state['fc_min_val'],.9)
        self.assertEqual(state['fc_other_val'],1.2)
        self.assertEqual(updated['signs'],original['signs'])
        self.assertEqual(self.case,original)
        self.assertNotIn('report',updated)
        self.assertEqual(apply_word_measurements(self.case,{})['inputs']['peso'],72.)

    def test_complete_restore_keeps_every_serialized_field(self):
        restored = resume_case(self.event(), self.params)
        self.assertEqual(restored, self.case)
        inputs = restored_inputs(restored)
        self.assertEqual(inputs['peso'],72.)
        self.assertEqual(inputs['fc_other_val'],1.2)
        self.assertTrue(inputs['mostra_parametri_aggiuntivi'])

    def test_wait_does_not_import_empty_case(self):
        self.assertIsNone(resume_case(None,self.params))

    def test_wrong_case_token_format_and_oversized_payload_are_rejected(self):
        wrong = deepcopy(self.case); wrong['case_code']='X26.85'
        for event in [self.event(wrong), {'token':'b'*32,'data':self.event()['data']},
                      {'token':'a'*32,'data':'!!!'}, {'token':'a'*32,'data':'a'*1400000}]:
            with self.assertRaises(CaseFileError):resume_case(event,self.params)

    def test_word_launch_routes_full_case_through_existing_import(self):
        from streamlit.testing.v1 import AppTest
        from unittest.mock import patch
        app = AppTest.from_string("""
import streamlit as st
from app.word_launch import prepare_word_launch
from app.case_ui import prepare_case_import
prepare_word_launch()
prepare_case_import('Stima_epoca_decesso.py')
st.text('ready')
""")
        app.query_params.update(mt_open='1',mt_case='X26.84',mt_request='a'*32,mt_resume='1',mt_weight='999')
        with patch('app.word_resume.render_word_resume',return_value=self.case):
            app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['peso'],999.)
        self.assertEqual(app.session_state['fc_other_val'],1.2)
        self.assertEqual(app.session_state['__word_return']['request_id'],'a'*32)
        self.assertNotIn('mt_resume',app.query_params)

    def test_waiting_preserves_existing_state(self):
        from streamlit.testing.v1 import AppTest
        from unittest.mock import patch
        app=AppTest.from_string("""
import streamlit as st
from app.word_launch import prepare_word_launch
st.session_state.setdefault('peso',88.)
prepare_word_launch()
st.text('ready')
""")
        app.query_params.update(mt_open='1',mt_case='X26.84',mt_request='a'*32,mt_resume='1')
        with patch('app.word_resume.render_word_resume',return_value=None):
            app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['peso'],88.)
        self.assertIn('1', app.query_params['mt_resume'])

    def test_standalone_open_ignores_resume_parameter_without_word_launch(self):
        from streamlit.testing.v1 import AppTest
        from unittest.mock import patch
        app=AppTest.from_string("""
import streamlit as st
from app.word_launch import prepare_word_launch
st.session_state.setdefault('peso',88.)
prepare_word_launch()
st.button('Procedi con la stima')
""")
        app.query_params.update(mt_resume='1')
        with patch('app.word_resume.render_word_resume') as resume:
            app.run()
        resume.assert_not_called()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['peso'],88.)
        self.assertEqual(app.button[0].label,'Procedi con la stima')
