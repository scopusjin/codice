from copy import deepcopy
from pathlib import Path
import unittest

from app.late_changes import build_late_report, late_hours_conflict
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
        self.assertIn('non permettono di avanzare precisazioni', report['brief'])
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
        self.assertIn('mummification and areas showing adipocere', report['html'])
        self.assertIn('at least several days', report['brief'])

    def test_user_template_and_word_only_definitions(self):
        report = build_late_report(self.state(henssge_non_applicabile=True))
        self.assertIn('fenomeni post-mortali consecutivi normalmente presi in considerazione', report['html'])
        self.assertIn('in quanto il cadavere si trovava ormai in una fase avanzata', report['html'])
        self.assertIn('Gli unici elementi', report['html'])
        self.assertIn('Poiché tali processi possono manifestarsi in un intervallo temporale estremamente variabile', report['html'])
        self.assertIn('il loro grado di sviluppo permette unicamente di ritenere', report['html'])
        self.assertIn('quantomeno vari giorni prima del rinvenimento', report['html'])
        self.assertIn('Anche questo elemento risulta pertanto compatibile', report['html'])
        self.assertNotIn('risulta pertanto compatibile', report['conflict_html'])
        state = self.state(show_results=True)
        state.update(__desc_dettagliate_html=report['html'], __word_footnotes=report['word_footnotes'])
        capture_report(state, 'full')
        case = decode_case(encode_case(snapshot_case(state, 'full')))
        self.assertEqual(case['report']['word_footnotes'], report['word_footnotes'])
        bad = deepcopy(case)
        bad['report']['word_footnotes'][0]['anchor'] = 'not found'
        with self.assertRaises(CaseFileError):
            encode_case(bad)
        state = self.state()
        state.update(late_changes_observed=['mummification'], late_insects_observed=[])
        self.assertEqual(build_late_report(state)['word_footnotes'], [])

    def test_independent_assessments_and_brief_wording(self):
        state = self.state(show_results=True)
        state.update(late_transform_conclusion='weeks', late_entomo_conclusion='few_days',
                     late_insects_observed=['full_puparia'], late_entomo_automatic=False)
        report = build_late_report(state)
        self.assertIn('La presenza di alterazioni trasformative post-mortali consente unicamente di ritenere', report['brief'])
        self.assertIn('alcune settimane prima del rinvenimento', report['brief'])
        self.assertIn('La presenza di pupari pieni riferibili alla colonizzazione del cadavere', report['brief'])
        self.assertIn('almeno alcuni giorni prima del rinvenimento', report['brief'])
        self.assertEqual(len(report['brief'].splitlines()), 2)
        self.assertIn('La presenza di alterazioni', report['brief'].splitlines()[0])
        state.update(__desc_dettagliate_html=report['html'], __word_footnotes=report['word_footnotes'])
        capture_report(state, 'full')
        case = decode_case(encode_case(snapshot_case(state, 'full')))
        restored = restored_inputs(case)
        self.assertEqual(restored['late_transform_conclusion'], 'weeks')
        self.assertEqual(restored['late_entomo_conclusion'], 'few_days')
        self.assertFalse(restored['late_entomo_automatic'])
        state.update(late_changes_observed=[], late_transform_conclusion='months')
        report = build_late_report(state)
        warning = late_hours_conflict(report, [('Ipostasi', 3)])
        self.assertIn('valutazione dell’entomofauna', warning)
        self.assertNotIn('valutazione dei fenomeni trasformativi', warning)
        state.update(late_entomo_conclusion='unspecified', late_insects_observed=['eggs', 'larvae'])
        report = build_late_report(state)
        self.assertIn('non permettono di avanzare precisazioni', report['brief'])
        self.assertNotIn('giorni', report['brief'])
        self.assertFalse(late_hours_conflict(report, [('Ipostasi', 3)]))
        state.update(late_changes_observed=['gas'], late_transform_conclusion='days', late_entomo_conclusion='days')
        self.assertEqual(build_late_report(state)['brief'].count('almeno diversi giorni'), 1)

    def test_entomo_presets_and_manual_override_in_page(self):
        from streamlit.testing.v1 import AppTest
        import app.decimal_number_input_v2 as decimal_v2
        decimal_v2._renderer = None
        page = str(Path(__file__).resolve().parents[1] / 'Stima_epoca_decesso.py')
        app = AppTest.from_file(page, default_timeout=30).run()
        app.session_state['late_changes_enabled'] = True
        app.run()
        self.assertEqual(app.selectbox(key='late_transform_conclusion').label, 'Valutazione prudente epoca del decesso:')
        self.assertEqual(app.selectbox(key='late_entomo_conclusion').label, 'Valutazione prudente epoca del decesso:')
        self.assertNotIn('Alcune settimane prima del rinvenimento', app.selectbox(key='late_entomo_conclusion').options)
        self.assertNotIn('Alcuni mesi prima del rinvenimento', app.selectbox(key='late_entomo_conclusion').options)
        app.checkbox(key='late_insects_observed__check_eggs').check().run()
        self.assertEqual(app.session_state['late_entomo_conclusion'], 'unspecified')
        app.checkbox(key='late_insects_observed__check_full_puparia').check().run()
        self.assertEqual(app.session_state['late_entomo_conclusion'], 'few_days')
        # Simulate an older/imported case retaining the full-puparia preset.
        app.session_state['late_entomo_automatic'] = False
        app.checkbox(key='late_insects_observed__check_empty_puparia').check().run()
        self.assertEqual(app.session_state['late_entomo_conclusion'], 'days')
        self.assertTrue(app.session_state['late_entomo_automatic'])
        app.selectbox(key='late_entomo_conclusion').select('custom').run()
        app.text_area(key='late_entomo_custom').input('valutazione entomologica personale').run()
        app.checkbox(key='late_insects_observed__check_empty_puparia').uncheck().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.session_state['late_entomo_automatic'])
        self.assertEqual(app.session_state['late_entomo_conclusion'], 'custom')
        self.assertEqual(app.session_state['late_transform_conclusion'], 'unspecified')
        app.checkbox(key='late_changes_observed__check_gas').check().run()
        app.selectbox(key='late_transform_conclusion').select('months').run()
        self.assertEqual(app.session_state['late_entomo_conclusion'], 'custom')
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        case = snapshot_case(app.session_state._state.filtered_state, 'full')
        self.assertIn('alcuni mesi', app.session_state['frase_breve'])
        self.assertIn('valutazione entomologica personale', app.session_state['frase_breve'])
        self.assertEqual(case['inputs']['late_transform_conclusion'], 'months')
        self.assertEqual(case['inputs']['late_entomo_conclusion'], 'custom')

    def test_extent_options_keep_legacy_observations_and_word_notes(self):
        state = self.state(show_results=True)
        state['late_changes_observed'] = ['liquefaction_partial', 'liquefaction_diffuse',
            'mummification_partial', 'mummification_diffuse', 'skeletonisation_partial',
            'skeletonisation_diffuse', 'adipocere']
        report = build_late_report(state)
        for text in ('aree di parziale colliquazione', 'diffusa colliquazione di porzioni corporee',
                     'aree di parziale mummificazione', 'diffusa scheletrizzazione di porzioni corporee',
                     'aree caratterizzate da presenza di adipocera'):
            self.assertIn(text, report['html'])
        self.assertEqual(report['word_footnotes'][0]['anchor'], 'putrefattivi')
        case = decode_case(encode_case(snapshot_case(state, 'full')))
        self.assertEqual(restored_inputs(case)['late_changes_observed'], state['late_changes_observed'])
        state['late_changes_observed'] = ['liquefaction']
        self.assertIn('colliquazione.', build_late_report(state)['html'])
        self.assertNotIn('parziale colliquazione', build_late_report(state)['html'])

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

    def test_hours_conflict_checks_each_parameter_without_building_late_range(self):
        for choice in ('days', 'weeks', 'months'):
            state = self.state()
            state['late_conclusion'] = choice
            report = build_late_report(state)
            warning = late_hours_conflict(report, [('Rigidità', 192), ('Ipostasi', 3), ('Raffreddamento', float('nan'))])
            self.assertIn('ipostasi', warning)
            self.assertNotIn('rigidità', warning)
            self.assertNotIn('raffreddamento', warning)
            self.assertIn('non è stata inclusa nel calcolo', warning)
            self.assertNotIn('range', report)
            self.assertNotIn('non risulta in contrasto', report['conflict_html'])
            self.assertNotIn('quantificare un intervallo minimo', report['html'])
            self.assertFalse(late_hours_conflict(report, [('ipostasi', 24), ('rigidità', float('inf'))]))
        for choice in ('unspecified', 'custom'):
            self.assertFalse(late_hours_conflict({'choice': choice}, [('ipostasi', 3)]))
        self.assertIn('Potential inconsistency', late_hours_conflict({'choice': 'days'}, [('lividity', 3)], 'en'))

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
        self.assertEqual(len(app.multiselect), 0)
        self.assertTrue(any('Pupari vuoti' in p.proto.popover.label for p in app.get('popover')))
        self.assertFalse(any(p.proto.popover.label == 'Scegli reperti' for p in app.get('popover')))
        self.assertFalse(any('non generano automaticamente' in c.value for c in app.caption))
        self.assertTrue(app.checkbox(key='late_changes_observed__check_gas').value)
        self.assertTrue(app.checkbox(key='late_insects_observed__check_empty_puparia').value)
        self.assertTrue(any('Valutazione prudente' in field.label for field in app.selectbox))
        self.assertEqual(sum('da verificare e modificare se necessario' in m.value for m in app.markdown), 0)
        self.assertFalse(any('Formula una' in m.value for m in app.markdown))
        self.assertTrue(any('Enfisema putrefattivo' in p.proto.popover.label for p in app.get('popover')))
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        case = snapshot_case(app.session_state._state.filtered_state, 'full')
        self.assertIsNotNone(case['report'])
        self.assertIn('pupari vuoti', case['report']['detailed_text'])
        self.assertIn('fuoriuscita', case['report']['word_blocks']['putrefaction']['text'])
        self.assertEqual([n['anchor'] for n in case['report']['word_footnotes']], ['putrefattivi', 'entomofauna'])
        self.assertIn('Per putrefazione si intende', case['report']['word_footnotes'][0]['text'])
        self.assertNotIn('Per putrefazione si intende', case['report']['detailed_text'])
        self.assertNotIn('[1]', case['report']['detailed_text'])
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
        app.session_state['selettore_macchie'] = 'Non ancora comparse'
        app.session_state['selettore_macchie_ui'] = 'Non ancora comparse'
        app.run()
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('Possibile incoerenza' in w.value for w in app.warning))
        case = snapshot_case(app.session_state._state.filtered_state, 'full')
        self.assertIn('Possibile incoerenza', case['report']['detailed_text'])
        self.assertIn('Possibile incoerenza', case['report']['word_blocks']['putrefaction']['text'])
        self.assertNotIn('almeno diversi giorni', app.session_state['frase_breve'])
        app.checkbox(key='late_insects_observed__check_larvae').uncheck().run()
        self.assertFalse(app.session_state['show_results'])
        self.assertNotIn('larvae', app.session_state['late_insects_observed'])
        app.button(key='btn_stima').click().run()
        self.assertFalse(app.exception)
        case = decode_case(encode_case(snapshot_case(app.session_state._state.filtered_state, 'full')))
        self.assertNotIn('larve', case['report']['detailed_text'])
        self.assertEqual(case['inputs']['late_insects_observed'], ['empty_puparia'])


if __name__ == '__main__':
    unittest.main()
