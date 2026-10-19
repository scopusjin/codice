import unittest
from app.word_launch import launch_values


class WordLaunchTests(unittest.TestCase):
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
