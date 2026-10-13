"""Check source-chart column alignment in the actual reference-table renderer."""

import ast
import re
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
import unittest

from app.parameters import INF_HOURS, dati_parametri_aggiuntivi, opzioni_rigidita

ROOT = Path(__file__).resolve().parents[1]


class WeightRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = False

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        elif tag == 'td':
            self.cell = 'rowspan' not in dict(attrs)

    def handle_data(self, text):
        if self.cell and text.strip():
            self.row.append(float(text))

    def handle_endtag(self, tag):
        if tag == 'td':
            self.cell = False
        elif tag == 'tr' and self.row:
            self.rows.append(self.row)


class FCReferenceTableTests(unittest.TestCase):
    def test_reference_weights_stay_in_the_source_columns_in_both_languages(self):
        path = ROOT / 'pages/2_Tabelle di riferimento.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        # Isolate the unmodified renderer from page navigation and session state.
        nodes = [node for node in tree.body if
                 (isinstance(node, ast.Assign) and any(
                     isinstance(target, ast.Name) and target.id in
                     {'_HENSSGE_WEIGHT_TABLE_TEXT', '_HENSSGE_WEIGHT_REFERENCE'}
                     for target in node.targets)) or
                 (isinstance(node, ast.FunctionDef) and
                  node.name == '_render_henssge_weight_table')]
        output = []
        namespace = {'st': SimpleNamespace(
            markdown=lambda html, **kwargs: output.append(html), caption=lambda text: None)}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
        # Source: Madea, 3rd ed. (2016), Table 6.20. Anchors at 40/70/150 kg
        # detect the previous left shift and the loss of values at high weights.
        expected = [(1.4, 1.4, 1.2), (1.6, 1.6, 1.3), (2.1, 1.8, 1.4),
                    (2.4, 2.0, 1.5), (2.8, 2.2, 1.6), (3.2, 2.4, 1.6),
                    (3.6, 2.6, 1.7), (3.9, 2.8, 1.7), (4.3, 3.0, 1.8)]
        for language in ('it', 'en'):
            output.clear()
            namespace['_render_henssge_weight_table'](language)
            parser = WeightRows()
            parser.feed(output[0])
            self.assertEqual(len(parser.rows), 9)
            for row, anchors in zip(parser.rows, expected, strict=True):
                self.assertEqual(len(row), 18)
                self.assertEqual((row[6], row[9], row[17]), anchors)


class CombinedRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = {}
        self.cells = []
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.cells = []
        elif tag == 'td':
            self.cell = []

    def handle_data(self, text):
        if self.cell is not None:
            self.cell.append(text)

    def handle_endtag(self, tag):
        if tag == 'td':
            self.cells.append(''.join(self.cell).strip())
            self.cell = None
        elif tag == 'tr' and self.cells:
            criterion, yes, no = self.cells
            self.rows[criterion] = (yes, no)


class CombinedReferenceTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'pages/2_Tabelle di riferimento.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        nodes = [node for node in tree.body if
                 (isinstance(node, ast.Assign) and any(
                     isinstance(target, ast.Name) and target.id.startswith('_COMBINED_')
                     for target in node.targets)) or
                 (isinstance(node, ast.FunctionDef) and node.name == '_render_combined_table')]
        cls.html, cls.captions = [], []
        cls.namespace = {'st': SimpleNamespace(
            markdown=lambda html, **kwargs: cls.html.append(html),
            caption=lambda text: cls.captions.append(text))}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), cls.namespace)

    def render(self, language):
        self.html.clear()
        self.captions.clear()
        self.namespace['_render_combined_table'](language)
        self.assertEqual(len(self.html), 1)
        parser = CombinedRows()
        parser.feed(self.html[0])
        self.assertEqual(len(parser.rows), 24)
        text = self.namespace['_COMBINED_TABLE_TEXT'][language]
        return {key: parser.rows[label] for key, label in text.items() if label in parser.rows}

    def interval(self, rows, answers):
        lower, upper = 0, INF_HOURS
        for key, yes in answers:
            bound = rows[key][0 if yes else 1]
            self.assertNotRegex(bound, r'\d,\d')
            if bound == '—':
                continue
            match = re.fullmatch(r'([≥≤]) (\d+(?:\.\d+)?)[*†]?', bound)
            self.assertIsNotNone(match, bound)
            sign, number = match.groups()
            if sign == '≥':
                lower = max(lower, float(number))
            else:
                upper = min(upper, float(number))
        return lower, upper

    def test_cumulative_supraciliary_answers_match_observed_extent_intervals(self):
        keys = ('supra_cheek', 'supra_forehead', 'supra_lower_lid',
                'supra_whole_upper_lid', 'supra_partial_upper_lid', 'supra_nasal')
        grades = ('Fase VI', 'Fase V', 'Fase IV', 'Fase III', 'Fase II', 'Fase I', 'Nessuna reazione')
        expected = dati_parametri_aggiuntivi['Eccitabilità elettrica sopraciliare']['range']
        for language in ('it', 'en'):
            rows = self.render(language)
            for first_positive, grade in enumerate(grades):
                with self.subTest(language=language, grade=grade):
                    answers = [(key, index >= first_positive) for index, key in enumerate(keys)]
                    self.assertEqual(self.interval(rows, answers), expected[grade])

    def test_progression_questions_reproduce_the_five_rigor_stages(self):
        stages = {
            'Non ancora apprezzabile': [('rigor_beginning', False)],
            'Presente e in via di intensificazione e generalizzazione':
                [('rigor_beginning', True), ('rigor_complete', False)],
            'Presente, intensa e generalizzata':
                [('rigor_complete', True), ('rigor_persistence', False)],
            'In via di risoluzione': [('rigor_persistence', True), ('rigor_resolution', False)],
            'Risolta': [('rigor_resolution', True)],
        }
        for language in ('it', 'en'):
            rows = self.render(language)
            for stage, answers in stages.items():
                with self.subTest(language=language, stage=stage):
                    self.assertEqual(self.interval(rows, answers), opzioni_rigidita[stage])

    def test_updated_reestablishment_bound_has_its_own_source_and_note(self):
        # Anders et al., Int J Legal Med 2013: observed re-establishment up to 19 h.
        for language in ('it', 'en'):
            rows = self.render(language)
            self.assertEqual(self.interval(rows, [('reestablishment', True)]), (0, 19))
            self.assertEqual(self.interval(rows, [('reestablishment', False)]), (2, INF_HOURS))
            self.assertTrue(rows['reestablishment'][0].endswith('*'))
            self.assertTrue(any('Anders et al., 2013' in note and note.startswith('*')
                                for note in self.captions))
            self.assertTrue(any('10.1007/s00414-011-0632-z' in note for note in self.captions))
            self.assertEqual(rows['muscle_response'], ('≤ 11', '≥ 3'))

    def test_mechanical_response_questions_match_app_states_without_false_negative_bounds(self):
        expected = dati_parametri_aggiuntivi['Eccitabilità muscolare meccanica']['range']
        states = {
            'Contrazione dell’intero muscolo':
                [('whole_muscle', True), ('reversible_swelling', False), ('mechanical_response', True)],
            'Tumefazione reversibile':
                [('whole_muscle', False), ('reversible_swelling', True), ('mechanical_response', True)],
            'Piccola tumefazione persistente':
                [('whole_muscle', False), ('reversible_swelling', False), ('mechanical_response', True)],
            'Nessuna reazione':
                [('whole_muscle', False), ('reversible_swelling', False), ('mechanical_response', False)],
        }
        for language in ('it', 'en'):
            rows = self.render(language)
            for state, answers in states.items():
                with self.subTest(language=language, state=state):
                    self.assertEqual(self.interval(rows, answers), expected[state])


if __name__ == '__main__':
    unittest.main()
