"""Approved removal of desktop preview and temporary suspension of App MSIL."""
from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

class DisabledPageTests(unittest.TestCase):
    def test_only_active_pages_are_discoverable(self):
        names={p.name for p in (ROOT/'pages').glob('*.py')}
        self.assertNotIn('App_MSIL.py',names)
        self.assertNotIn('99_Anteprima desktop.py',names)
        self.assertTrue({'Impostazioni.py','9_Reference.py','2_Tabelle di riferimento.py'} <= names)
        self.assertTrue((ROOT/'disabled_pages/App_MSIL.py').is_file())

    def test_msil_import_does_not_replace_current_case(self):
        app=AppTest.from_string('''
import streamlit as st
from app.case_file import snapshot_case
from app.case_ui import prepare_case_import
st.session_state['case_code']='CURRENT'
st.session_state['__case_pending_import']=snapshot_case({},'msil')
prepare_case_import('Stima_epoca_decesso.py')
assert st.session_state['case_code']=='CURRENT'
''').run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.error),1)
        self.assertIn('temporaneamente disattivata',app.error[0].value)
