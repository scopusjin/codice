"""Final displays use unrounded scientific bounds and one shared setting."""
import datetime as dt
import unittest
import numpy as np
from app.henssge import calcola_raffreddamento
from app.graphing_cooling import compute_cooling_state
from app.textgen import (build_final_sentence, build_simple_sentence,
    build_final_sentence_simple, build_simple_sentence_no_dt, nota_arrotondamento_orari)
from app.utils_time import round_display_hours, round_display_datetime
from app.language import using_language

class FinalRoundingPolicyTests(unittest.TestCase):
    def test_agreed_example_and_no_successive_rounding(self):
        inspection=dt.datetime(2026,10,26,14,8)
        lower,upper=1.2,6+22/60
        for language in ('it','en'):
            with using_language(language):
                for step,start,end in ((15,'07:45','13:00'),(30,'07:30','13:00'),(6,'07:42','13:00')):
                    for builder in (build_final_sentence,build_simple_sentence):
                        text=builder(lower,upper,inspection,round_minutes=step)
                        self.assertIn(start,text)
                        self.assertIn(end,text)
                        if step==15:
                            self.assertIn('6 ore 30 minuti' if language=='it' else '6 hours 30 minutes',text)
                            self.assertNotIn('07:30',text) # would result from rounded 6h30
                    for builder in (build_final_sentence_simple,build_simple_sentence_no_dt):
                        self.assertTrue(builder(lower,upper,round_minutes=step))

    def test_display_never_extends_beyond_the_examination(self):
        inspection=dt.datetime(2026,10,26,14,8)
        for builder in (build_final_sentence,build_simple_sentence):
            text=builder(.02,2.,inspection)
            self.assertIn('14:08',text)
            self.assertNotIn('14:15',text)

    def test_grid_exactness_and_containment(self):
        for step in (6,15,30):
            for hours in np.linspace(0,48,601):
                low=round_display_hours(hours,step)
                high=round_display_hours(hours,step,upper=True)
                self.assertLessEqual(low,hours+1e-10)
                self.assertGreaterEqual(high,hours-1e-10)
                self.assertLess(high-low,step/60+1e-10)
            for multiple in range(100):
                hours=multiple*step/60
                self.assertAlmostEqual(round_display_hours(hours,step),hours)
                self.assertAlmostEqual(round_display_hours(hours,step,upper=True),hours)

    def test_midnight_and_open_bounds_keep_examination_exact(self):
        inspection=dt.datetime(2026,10,27,2,58)
        text=build_simple_sentence(2,3,inspection)
        self.assertIn('23:45',text)
        self.assertIn('26.10.2026',text)
        self.assertIn('01:00',text)
        for builder in (build_final_sentence,build_simple_sentence):
            text=builder(0,4,dt.datetime(2026,10,26,14,8))
            self.assertIn('10:00',text)
            self.assertIn('14:08',text)
            text=builder(1.2,np.inf,dt.datetime(2026,10,26,14,8))
            self.assertIn('13:00',text)

    def test_cooling_keeps_raw_bounds_independent_of_display_setting(self):
        for prudent in (False,True):
            outputs=[]
            for step in (6,15,30):
                options=dict(henssge_round_minutes=step,stima_cautelativa_beta=prudent,
                             Ta_min_beta=15.,Ta_max_beta=18.,FC_min_beta=1.,FC_max_beta=1.2)
                c=compute_cooling_state(input_rt=30.7,input_ta=15.,input_tm=37.2,
                    input_w=75.,fattore_correzione=1.,data_ora_ispezione=dt.datetime(2026,10,26,14,8),
                    skip_warnings=True,cooling_options=options)
                self.assertIsNone(c.validation_error)
                outputs.append((c.t_min_raff_henssge,c.t_max_raff_henssge,c.t_med_raff_henssge_rounded_raw))
            self.assertEqual(outputs[0],outputs[1]);self.assertEqual(outputs[1],outputs[2])
        med,low,high,raw,q=calcola_raffreddamento(30.7,15.,37.2,75.,1.,round_minutes=None)
        self.assertEqual(med,raw)
        self.assertAlmostEqual(high-low,5.6)

    def test_note_tracks_actual_setting_and_language(self):
        with using_language('it'):
            self.assertIn('al quarto d’ora (per difetto',nota_arrotondamento_orari(15))
            self.assertIn('a 30 minuti',nota_arrotondamento_orari(30))
            self.assertIn('L’ampiezza',nota_arrotondamento_orari())
        with using_language('en'):
            self.assertIn('30-minute increments',nota_arrotondamento_orari(30))
            self.assertNotIn('quarto',nota_arrotondamento_orari(30))

    def test_settings_control_changes_final_outputs_and_note(self):
        from streamlit.testing.v1 import AppTest
        from pathlib import Path
        settings=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'pages/Impostazioni.py')).run()
        self.assertFalse(settings.exception)
        self.assertEqual(settings.session_state['henssge_round_minutes'],15)
        settings.radio[0].set_value('30 minuti').run()
        self.assertEqual(settings.session_state['henssge_round_minutes'],30)
        self.assertTrue(any('per difetto' in c.value for c in settings.caption))
        script='''
import datetime
import streamlit as st
from unittest.mock import patch
from app.graphing import aggiorna_grafico
from app.graphing_cooling import compute_cooling_state
step=st.radio('step',[15,30],key='henssge_round_minutes')
c=compute_cooling_state(input_rt=30.7,input_ta=15.,input_tm=37.2,input_w=75.,fattore_correzione=1.,
 data_ora_ispezione=datetime.datetime(2026,10,26,14,8),skip_warnings=True,cooling_options={})
from dataclasses import replace
c=replace(c,t_min_raff_henssge=1.2,t_max_raff_henssge=6+22/60)
with patch('app.graphing.compute_cooling_state',return_value=c):
 aggiorna_grafico(selettore_macchie='Non valutate',selettore_rigidita='Non valutata',input_rt=30.7,
 input_ta=15.,input_tm=37.2,input_w=75.,fattore_correzione=1.,widgets_parametri_aggiuntivi={},
 usa_orario_custom=True,input_data_rilievo=datetime.date(2026,10,26),input_ora_rilievo='14:08',
 alterazioni_putrefattive=False,skip_warnings=True)
'''
        app=AppTest.from_string(script,default_timeout=30).run()
        for step,start in ((15,'07:45'),(30,'07:30')):
            app.radio[0].set_value(step).run()
            self.assertFalse(app.exception)
            self.assertIn(start,app.session_state['frase_breve'])
            self.assertIn('13:00',app.session_state['frase_breve'])
            detail=app.session_state['__desc_dettagliate_html']
            self.assertIn(start,detail)
            self.assertIn('al quarto d’ora' if step==15 else 'a 30 minuti',detail)
            self.assertIn(start,app.session_state['__word_report_blocks']['conclusion']['text'])
