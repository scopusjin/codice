from copy import deepcopy
from pathlib import Path
import unittest

from app.late_changes import build_late_report
from app.case_file import snapshot_case, encode_case, decode_case, restored_inputs, CaseFileError
from app.case_report import capture_report


class LateChangesTests(unittest.TestCase):
    def state(self, **extra):
        return dict(late_changes_enabled=True, late_changes_observed=['gas', 'liquefaction'],
                    late_insects_observed=['larvae', 'empty_puparia'], late_conclusion='days', **extra)

    def test_multiple_observations_and_puparia_wording(self):
        report = build_late_report(self.state())
        for text in ('enfisema putrefattivo', 'colliquazione', 'larve', 'pupari vuoti',
                     'fuoriuscita dell’insetto adulto', 'almeno diversi giorni prima del rinvenimento'):
            self.assertIn(text, report['html'])
        self.assertNotIn('non risultano utilizzabili', report['html'])
        report = build_late_report(self.state(henssge_non_applicabile=True,
            selettore_macchie_id='livor_unreliable', selettore_rigidita_id='rigor_full'))
        intro = report['html'].split('</p>')[0]
        self.assertIn('raffreddamento', intro)
        self.assertIn('ipostatiche', intro)
        self.assertNotIn('rigidità', intro)

    def test_no_automatic_timing_or_empty_puparia_claim(self):
        state = self.state()
        state.update(late_conclusion='unspecified', late_insects_observed=['larvae'])
        report = build_late_report(state)
        self.assertNotIn('diversi giorni', report['html'])
        self.assertNotIn('fuoriuscita', report['html'])
        self.assertIn('non risulta ulteriormente precisabile', report['brief'])
        state['late_insects_observed'] = ['empty_puparia']
        self.assertNotIn('diversi giorni', build_late_report(state)['html'])
        state.update(late_conclusion='custom', late_conclusion_custom='Dato personale <script>')
        self.assertIn('&lt;script&gt;', build_late_report(state)['html'])
        state['late_changes_enabled'] = False
        self.assertIsNone(build_late_report(state))

    def test_preservative_changes_and_english(self):
        state = self.state()
        state.update(late_changes_observed=['mummification', 'adipocere'], late_insects_observed=[])
        report = build_late_report(state)
        self.assertNotIn('infezioni', report['html'])
        self.assertNotIn('entomofauna', report['html'])
        report = build_late_report(state, 'en')
        self.assertIn('mummification and adipocere', report['html'])
        self.assertIn('at least several days', report['brief'])

    def test_json_roundtrip_and_stale_report(self):
        state = self.state(show_results=True)
        state['__desc_dettagliate_html'] = build_late_report(state)['html']
        capture_report(state, 'full')
        case = decode_case(encode_case(snapshot_case(state, 'full')))
        restored = restored_inputs(case)
        for key in ('late_changes_enabled', 'late_changes_observed', 'late_insects_observed', 'late_conclusion'):
            self.assertEqual(restored[key], state[key])
        self.assertIn('pupari vuoti', case['report']['detailed_text'])
        state['late_insects_observed'] = ['larvae']
        self.assertIsNone(snapshot_case(state, 'full')['report'])
        bad = deepcopy(case)
        bad['inputs']['late_changes_observed'] = ['invented']
        with self.assertRaises(CaseFileError):
            encode_case(bad)

    def test_full_page_late_only_and_mixed_export(self):
        from streamlit.testing.v1 import AppTest
        import app.decimal_number_input_v2 as decimal_v2
        decimal_v2._renderer = None
        page = str(Path(__file__).resolve().parents[1] / 'Stima_epoca_decesso.py')
        app = AppTest.from_file(page, default_timeout=30).run()
        for key, value in self.state(henssge_non_applicabile=True).items():
            app.session_state[key] = value
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.multiselect), 2)
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        case = snapshot_case(app.session_state._state.filtered_state, 'full')
        self.assertIsNotNone(case['report'])
        self.assertIn('pupari vuoti', case['report']['detailed_text'])
        self.assertIn('fuoriuscita', case['report']['word_blocks']['putrefaction']['text'])
        self.assertNotIn('arrotondat', case['report']['detailed_text'])
        self.assertFalse(app.get('pyplot'))
        app.session_state['selettore_macchie'] = 'Fisse'
        app.session_state['selettore_macchie_ui'] = 'Fisse'
        app.run()
        self.assertFalse(app.session_state['show_results'])
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        html = app.session_state['__desc_dettagliate_html']
        self.assertIn('pupari vuoti', html)
        self.assertIn('macchie ipostatiche', html)
        self.assertIn('arrotondat', html)


if __name__ == '__main__':
    unittest.main()
