"""Integration checks run separately from legacy process-global UI wrappers."""
from datetime import date
from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest
from streamlit.proto.WidgetStates_pb2 import WidgetStates
from app.case_file import snapshot_case, encode_case, decode_case
import app.decimal_number_input_v2 as decimal

ROOT=Path(__file__).resolve().parents[1]

def browser_run(app, *, language=None, click=None):
    if language is not None:
        next(group for group in app.get('button_group') if group.key=='mortem_language_widget').set_value(language)
    if click:app.button(key=click).click()
    app.run()
    return app

class LanguagePageTests(unittest.TestCase):
    def start(self, mobile=False, msil=False, language='it', extra=None):
        decimal._renderer=None
        app=AppTest.from_file(str(ROOT/('pages/App_MSIL.py' if msil else 'Stima_epoca_decesso.py')),default_timeout=40)
        seed={'__full_device_mobile':mobile,'mortem_language':language,'rt_val':30.,'ta_base_val':15.,'peso':70.,'fattore_correzione':1.}
        seed.update(extra or {})
        for key,value in seed.items():app.session_state[key]=value
        app.run();self.assertEqual(list(app.exception),[])
        return app

    def test_roundtrip_and_old_case_import_preserve_inputs_and_reports(self):
        for mobile,msil in ((False,False),(True,False),(True,True)):
            with self.subTest(mobile=mobile,msil=msil):
                app=self.start(mobile,msil)
                button='btn_stima_mobile' if msil else 'btn_stima'
                view='msil' if msil else 'full'
                browser_run(app,click=button);self.assertEqual(list(app.exception),[])
                italian=app.session_state['__desc_dettagliate_html']
                saved=decode_case(encode_case(snapshot_case(app.session_state._state.filtered_state,view)))
                browser_run(app,language='en');self.assertEqual(list(app.exception),[])
                self.assertEqual(app.session_state['mortem_language'],'en')
                current=snapshot_case(app.session_state._state.filtered_state,view)
                for key in ('inputs','signs','fc_choice'):self.assertEqual(current[key],saved[key],key)
                self.assertIn("Henssge’s method",app.session_state['__desc_dettagliate_html'])
                self.assertIn('corrective factor',app.session_state['__word_report_blocks']['correction_factor']['text'].lower())
                self.assertIn('ambient temperature',app.session_state['__word_report_blocks']['ambient_temperature']['text'].lower())
                browser_run(app,language='it');self.assertEqual(list(app.exception),[])
                self.assertEqual(app.session_state['__desc_dettagliate_html'],italian)
                browser_run(app,language='en')
                app.session_state['__case_pending_import']=saved
                browser_run(app);self.assertEqual(list(app.exception),[])
                self.assertEqual(app.session_state['mortem_language'],'en')
                browser_run(app,click=button);self.assertIn("Henssge’s method",app.session_state['__desc_dettagliate_html'])

    def test_combined_findings_and_different_observation_times(self):
        app=self.start(language='en',extra={
            'mostra_parametri_aggiuntivi':True,'usa_orario_custom':True,
            'input_data_rilievo':date(2026,10,22),'input_ora_rilievo':'15:30',
            'selettore_macchie_ui':'Parzialmente migrabili','selettore_macchie':'Parzialmente migrabili',
            'selettore_rigidita_ui':'Presente, in aumento','selettore_rigidita':'In via di formazione',
            'livor_digitopressione':'complete_fading','rigor_reformation':'yes',
            'Eccitabilità muscolare meccanica_selector':'Tumefazione reversibile',
            'Eccitabilità muscolare meccanica_diversa':True,
            'Eccitabilità muscolare meccanica_ora':'14:30',
            'Eccitabilità muscolare meccanica_ora__manual':True,
        })
        browser_run(app,click='btn_stima');self.assertEqual(list(app.exception),[])
        report=app.session_state['__desc_dettagliate_html']
        for text in ['incomplete shifting','blanched completely','between 4 and 20 hours','re-established','between 30 minutes and 19 hours','at 14:30 on 22.10.2026','temperature measurements at 15:30 on 22.10.2026']:
            self.assertIn(text,report)
        self.assertIn('before temperature measurement at 15:30',report)
        blocks=app.session_state['__word_report_blocks']
        self.assertIn('<u>Postmortem lividity</u>',blocks['livor']['html'])
        self.assertIn('<u>Rigor mortis</u>',blocks['rigor']['html'])
        self.assertIn('before temperature measurement at 15:30',blocks['cooling']['text'])
        self.assertNotIn('Rigor mortis mortis',report)
        self.assertNotIn('valutazioni del',report)
        from app.presentation_translation import translate
        choice=app.selectbox(key='Eccitabilità muscolare meccanica_selector')
        choice.select(translate('Nessuna reazione','en')).run()
        self.assertEqual(list(app.exception),[])
        self.assertEqual(app.session_state['Eccitabilità muscolare meccanica_selector'],'Nessuna reazione')
        browser_run(app,click='btn_stima');self.assertEqual(list(app.exception),[])
        self.assertIn('accounting for their different observation times',app.session_state['__desc_dettagliate_html'])
        for key in ('livor','rigor','additional'):self.assertTrue(app.session_state['__word_report_blocks'][key])

    def test_subpages_share_language_and_keep_reference_links(self):
        for filename in ('Impostazioni.py','2_Tabelle di riferimento.py','9_Reference.py'):
            decimal._renderer=None
            app=AppTest.from_file(str(ROOT/'pages'/filename),default_timeout=40)
            app.session_state['mortem_language']='en';app.run()
            self.assertEqual(list(app.exception),[])
            self.assertEqual(app.get('button_group')[0].value,'en')
            if filename=='Impostazioni.py':
                self.assertEqual(app.radio[0].options,['6 minutes','15 minutes','30 minutes'])
                app.radio[0].set_value('15 minutes').run()
                self.assertEqual(list(app.exception),[])
                self.assertEqual(app.session_state['henssge_round_minutes'],15)
                self.assertEqual(app.radio[0].value,'15 minuti')
            if filename=='9_Reference.py':
                text='\n'.join(item.value for item in app.markdown)
                self.assertIn('https://doi.org/10.1007/s004149900089',text)
                self.assertNotIn('above.',text)

    def test_scrolling_footer_and_compact_labels_survive_language_switches(self):
        for mobile in (False, True):
            with self.subTest(mobile=mobile):
                app=self.start(mobile=mobile,language='en',extra={'mostra_parametri_aggiuntivi':True})
                for language in ('en','it','en'):
                    browser_run(app,language=language)
                    self.assertEqual(list(app.exception),[])
                    headings='\n'.join(item.value for item in app.markdown if 'section-title' in item.value and '<style' not in item.value)
                    if language=='en':
                        self.assertNotIn('Ecc.',headings)
                        self.assertIn('Electrical excitability — supraciliary',headings)
                        self.assertIn('Electrical excitability — perioral',headings)
                    else:
                        self.assertIn('Ecc. elettrica sopraciliare',headings)
                    # Ordinary content footer, after the form; no pinned bottom root.
                    footer=app.main.get('button_group')[-1]
                    self.assertEqual(footer.key,'mortem_language_widget')
                    self.assertEqual(footer.value,language)
                    self.assertEqual(footer.options,['IT','EN'])
                    self.assertNotIn(3,app._tree.children)
                    title='\n'.join(item.proto.body for kind in ('html','markdown') for item in app.main.get(kind))
                    self.assertIn('TIME SINCE DEATH ESTIMATION' if language=='en' else 'STIMA EPOCA DECESSO',title)
                from app.presentation_translation import translate
                self.assertEqual(translate('T. amb. media','en'),'Mean amb. T.')

    def test_footer_survives_fc_route_and_missing_data_stop(self):
        for mobile,msil in ((False,False),(True,False),(True,True)):
            app=self.start(mobile,msil,extra={'__fc_active':True,'__fc_instance':'footer-check'})
            self.assertEqual(app.main.get('button_group')[-1].key,'mortem_language_widget')
            self.assertNotIn(3,app._tree.children)
            browser_run(app,language='en')
            self.assertEqual(list(app.exception),[])
            self.assertEqual(app.session_state['mortem_language'],'en')
        app=self.start(extra={'rt_val':None})
        browser_run(app,click='btn_stima')
        self.assertEqual(list(app.exception),[])
        self.assertEqual(app.main.get('button_group')[-1].key,'mortem_language_widget')

if __name__=='__main__':unittest.main()
