from copy import deepcopy
import unittest
from app.case_file import snapshot_case, encode_case, decode_case, restored_inputs
from app.case_report import capture_report


class ReportTests(unittest.TestCase):
    def test_round_trip_formatting_old_files_and_stale_results(self):
        for view, active in [('full', 'show_results'), ('msil', 'run_stima_mobile')]:
            state = {active: True, 'peso': 85., '__desc_dettagliate_html':
                     '<p>Parametri &amp; condizioni</p><ul><li>Più di 16 ore.</li></ul><p style="color:blue">Nota.</p>'}
            capture_report(state, view)
            case = decode_case(encode_case(snapshot_case(state, view)))
            self.assertIn('• Più di 16 ore.', case['report']['detailed_text'])
            self.assertIn('color:blue', case['report']['detailed_html'])
            self.assertNotIn('__case_report', restored_inputs(case))
            old = deepcopy(case)
            del old['report']
            decode_case(encode_case(old))
            state['case_code'] = 'X26.123'
            self.assertIsNotNone(snapshot_case(state, view)['report'])
            state['peso'] = 90.
            self.assertIsNone(snapshot_case(state, view)['report'])
            state['peso'] = 85.
            state[active] = False
            self.assertIsNone(snapshot_case(state, view)['report'])

    def test_real_full_page_export(self):
        from pathlib import Path
        from streamlit.testing.v1 import AppTest
        import app.decimal_number_input_v2 as decimal_v2
        decimal_v2._renderer = None
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'Stima_epoca_decesso.py'), default_timeout=30)
        app.run()
        app.session_state['selettore_macchie'] = 'Fisse'
        app.session_state['selettore_macchie_ui'] = 'Fisse'
        app.run()
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        app.button(key='case_menu').click().run()
        self.assertFalse(app.exception)
        import json
        component = next(c for c in app.get('component_instance') if c.proto.component_name.endswith('mortem_browser_cases'))
        args = json.loads(component.proto.json_args)
        # The actual browser/download payload must contain the displayed report.
        payload = next(json.loads(v) for v in args.values() if isinstance(v, str) and v.startswith('{') and 'mortem-case' in v)
        self.assertEqual(payload['report']['detailed_html'], app.session_state['__desc_dettagliate_html'])
        self.assertIn('ipostatiche', payload['report']['detailed_text'])
