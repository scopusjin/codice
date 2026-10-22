"""Language changes must not change scientific inputs or widget identities."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from app.language import current_language, using_language, presentation_i18n
from app.presentation_translation import catalogue, translate, translate_display_message

ROOT=Path(__file__).resolve().parents[1]

class LanguagePresentationTests(unittest.TestCase):
    def test_widget_indices_values_and_ids_are_unchanged(self):
        message=ForwardMsg()
        widget=message.delta.new_element.selectbox
        widget.id='stable-italian-id';widget.label='Rigidità cadaverica'
        widget.options.extend(['Non valutata','Presente, in aumento','Risolta'])
        widget.default=1
        with using_language('en'):translate_display_message(message)
        self.assertEqual(widget.id,'stable-italian-id');self.assertEqual(widget.default,1)
        self.assertEqual(widget.label,'Rigor mortis');self.assertEqual(list(widget.options),['Not assessed','Present, increasing in intensity and extent','Resolved'])
        user=ForwardMsg();user.delta.new_element.text_input.id='case_code';user.delta.new_element.text_input.label='Sigla / numero del caso';user.delta.new_element.text_input.default='Caso Data FC'
        with using_language('en'):translate_display_message(user)
        self.assertEqual(user.delta.new_element.text_input.default,'Caso Data FC')

    def test_markup_urls_numbers_and_english_are_preserved(self):
        text='<a href="https://example.org/Data/FC/1.4" title="Orario del rilievo">Ipostasi</a><script>const label="Ipostasi";</script>'
        translated=translate(text,'en')
        self.assertIn('href="https://example.org/Data/FC/1.4"',translated)
        self.assertIn('title="Time of observation"',translated)
        self.assertIn('>Lividity</a>',translated);self.assertIn('const label="Ipostasi"',translated)
        reference='Henssge C. 1992;54:51–66. [DOI](https://doi.org/10.1016/0379-0738(92)90080-G)'
        self.assertEqual(translate(reference,'en'),reference)
        self.assertEqual(translate('Rigor mortis','en'),'Rigor mortis')
        self.assertNotIn('.',catalogue())
        self.assertNotIn('Condizioni variabili',catalogue())

    def test_language_is_execution_local(self):
        def render(language):
            with using_language(language):
                return current_language(),presentation_i18n.ui_text('full.estimate_button')
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(list(pool.map(render,['it','en'])),[('it','Procedi con la stima'),('en','Estimate time since death')])
        self.assertEqual(current_language(),'it')

    def test_multiple_scenarios_keep_the_same_cooling_bounds(self):
        from datetime import datetime
        from test_fc_scenarios import temperature_payload
        from app.fc_selection import apply_choice
        from app.graphing_cooling import compute_cooling_state
        state={};apply_choice(state,temperature_payload())
        args=dict(input_rt=30.,input_ta=8.,input_tm=37.2,input_w=70.,fattore_correzione=1.35,
                  data_ora_ispezione=datetime(2026,10,22,12),skip_warnings=False,cooling_options=state)
        with using_language('it'):italian=compute_cooling_state(**args)
        with using_language('en'):
            english=compute_cooling_state(**args)
            report=translate(''.join(english.detail_blocks))
        for field in ('t_min_raff_henssge','t_max_raff_henssge','Qd_min','Qd_max','qd_range_status','qd_status_counts'):
            self.assertEqual(getattr(english,field),getattr(italian,field),field)
        for text in ('8.0 °C (water temperature)','20.0 °C','Estimated range of corrective factors','1.35 (dry body)','1.40 (wet body, moving air)'):
            self.assertIn(text,report)

    def test_cf_frontend_preserves_engine_and_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'dictionary.json';path.write_text(json.dumps(catalogue(),ensure_ascii=False))
            result=subprocess.run(['node','tests/test_fc_language.cjs',str(path)],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=='__main__':unittest.main()
