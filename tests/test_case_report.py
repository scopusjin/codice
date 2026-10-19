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
        self.assertTrue(app.get('download_button'))
        self.assertFalse(any(c.proto.component_name.endswith('mortem_browser_cases')
                             for c in app.get('component_instance')))
        payload = decode_case(encode_case(snapshot_case(app.session_state._state.filtered_state, 'full')))
        self.assertEqual(payload['report']['detailed_html'], app.session_state['__desc_dettagliate_html'])
        self.assertIn('ipostatiche', payload['report']['detailed_text'])

    def test_mixed_word_blocks_and_underlining(self):
        from test_mixed_cooling_description import SCRIPT
        from streamlit.testing.v1 import AppTest
        script = SCRIPT.replace('selettore_macchie="Non valutate"',
            'selettore_macchie="Migrabili perlomeno parzialmente"').replace(
            'selettore_rigidita="Non valutata"', 'selettore_rigidita="Presente, intensa e generalizzata"')
        app = AppTest.from_string(script, default_timeout=30).run()
        self.assertFalse(app.exception)
        blocks = app.session_state['__word_report_blocks']
        self.assertEqual(set(blocks), {'ambient_temperature', 'correction_factor', 'cooling', 'livor', 'rigor', 'conclusion'})
        self.assertEqual(blocks['ambient_temperature']['insert_when'], 'different_from_msil')
        self.assertIn('11.0', blocks['ambient_temperature']['text'])
        self.assertIn('1.40', blocks['correction_factor']['text'])
        self.assertIn('più di 16 ore e 30 minuti', blocks['cooling']['text'])
        self.assertIn('<u>macchie ipostatiche</u>', blocks['livor']['html'])
        self.assertIn('<u>rigidità cadaverica</u>', blocks['rigor']['html'])
        self.assertTrue(blocks['conclusion']['html'].startswith('<p>&nbsp;</p><p>'))
        self.assertNotIn('<li>', blocks['conclusion']['html'])
        self.assertNotIn('43 ore', str(blocks))
        self.assertNotIn('Il parametro Qd', str(blocks))

    def test_optional_word_blocks_round_trip(self):
        from app.case_report import build_word_blocks
        from app.textgen import paragrafo_putrefattive
        blocks = build_word_blocks(input_html="", cooling_html="", livor="", rigor="",
            conclusion="Conclusione", additional_html="<ul><li>Primo dato.</li><li>Secondo dato.</li></ul>",
            putrefaction_html=paragrafo_putrefattive(True))
        self.assertEqual(blocks['additional']['text'].count('•'), 2)
        self.assertIn('putref', blocks['putrefaction']['text'].lower())
        state = {'show_results': True, '__desc_dettagliate_html': '<p>Descrizioni.</p>',
                 '__word_report_blocks': blocks}
        capture_report(state, 'full')
        case = decode_case(encode_case(snapshot_case(state, 'full')))
        self.assertEqual(case['report']['word_blocks'], blocks)
