import re
import unittest
from streamlit.testing.v1 import AppTest


SCRIPT = '''
import datetime
import streamlit as st
from app.graphing import aggiorna_grafico
options = dict(stima_cautelativa_beta=True, Ta_min_beta=11., Ta_max_beta=15.,
               FC_min_beta=.7, FC_max_beta=1.4,
               __fc_applied_choice=dict(range=[.7, 1.4], weight=85., scenarios=[
                   dict(temperature=11., range=[.7,.7], description="corpo asciutto"),
                   dict(temperature=15., range=[1.2,1.4], description="corpo asciutto")]))
aggiorna_grafico(selettore_macchie="Non valutate", selettore_rigidita="Non valutata",
    input_rt=17.1, input_ta=11., input_tm=37.2, input_w=85., fattore_correzione=.7,
    widgets_parametri_aggiuntivi={}, usa_orario_custom=False,
    input_data_rilievo=datetime.date(2026,10,17), input_ora_rilievo=None,
    alterazioni_putrefattive=False, cooling_options=options, skip_warnings=True)
'''


class MixedCoolingDescriptionTests(unittest.TestCase):
    def test_english_report_keeps_open_minimum_and_word_blocks(self):
        script = SCRIPT.replace('import streamlit as st',
                                'import streamlit as st\nst.session_state["mortem_language"] = "en"')
        app = AppTest.from_string(script, default_timeout=30).run()
        self.assertFalse(app.exception)
        from app.case_report import plain_text
        report = plain_text(app.session_state['__desc_dettagliate_html'])
        self.assertIn('only some parameter combinations', report)
        self.assertIn('The combined estimate at examination is more than 16 hours 30 minutes since death.', report)
        self.assertIn('Potente’s method gives a minimum of 43 hours before the medico-legal examination.', report)
        blocks = app.session_state['__word_report_blocks']
        self.assertIn('more than 16 hours 30 minutes since death', blocks['cooling']['text'])
        self.assertNotIn('43 hours', blocks['cooling']['text'])
        self.assertEqual(blocks['ambient_temperature']['insert_when'], 'different_from_msil')
        self.assertIn('1.40', blocks['correction_factor']['text'])

    def test_report_uses_graph_minimum_and_moves_potente_to_blue_note(self):
        app = AppTest.from_string(SCRIPT, default_timeout=30).run()
        self.assertFalse(app.exception)
        html = app.session_state['__desc_dettagliate_html']
        self.assertIn('più di 16 ore e 30 minuti dal decesso', html)
        self.assertIn('risultati sufficientemente attendibili soltanto per una parte', html)
        self.assertNotIn("Applicando l'equazione di Henssge", html)
        self.assertNotIn('30 ore 30 minuti', html)
        self.assertNotIn('fossero trascorse almeno 43', html)
        note = re.search(r"<p[^>]*color:blue[^>]*>Nel caso in esame, per le condizioni.*?</p>", html)
        self.assertIsNotNone(note)
        self.assertIn('43 ore prima', note.group())
        self.assertGreater(note.start(), html.index('Il parametro Qd'))
        self.assertIn('16 ore', app.session_state['frase_breve'])

    def test_combined_conclusion_keeps_livor_upper_limit(self):
        script = SCRIPT.replace('selettore_macchie="Non valutate"',
                                'selettore_macchie="Migrabili perlomeno parzialmente"')
        app = AppTest.from_string(script, default_timeout=30).run()
        self.assertFalse(app.exception)
        html = app.session_state['__desc_dettagliate_html']
        self.assertIn('più di 16 ore e 30 minuti dal decesso', html)
        self.assertIn('24 ore', app.session_state['frase_breve'])
        self.assertIn('16 ore', app.session_state['frase_breve'])


if __name__ == '__main__':
    unittest.main()
