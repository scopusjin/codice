"""Check source-chart column alignment in the actual reference-table renderer."""

import ast
import re
from contextlib import nullcontext
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
import unittest

from app.parameters import INF_HOURS, dati_parametri_aggiuntivi, opzioni_rigidita

ROOT = Path(__file__).resolve().parents[1]


def _isolated_reference_renderer(path, constants, renderer, html, captions):
    """Compile the real renderer with its real bibliography dependencies."""
    tree = ast.parse(path.read_text(encoding='utf-8'))
    constants = set(constants) | {'_CITATION_PATTERN'}
    functions = {renderer, '_reference_link', '_reference_caption', '_reference_numbers_html'}
    nodes = [
        node for node in tree.body
        if (isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in constants
            for target in node.targets
        )) or (isinstance(node, ast.FunctionDef) and node.name in functions)
    ]
    namespace = {
        're': re,
        'escape': escape,
        'st': SimpleNamespace(
            markdown=lambda text, **kwargs: html.append(text),
            caption=lambda text, **kwargs: captions.append(text),
        ),
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


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
        # Keep navigation and unrelated Streamlit page code out of this test.
        output, captions = [], []
        namespace = _isolated_reference_renderer(
            path,
            {'_HENSSGE_WEIGHT_TABLE_TEXT', '_HENSSGE_WEIGHT_REFERENCE'},
            '_render_henssge_weight_table',
            output, captions,
        )
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


    def test_reference_navigation_bridge_runs_directly_in_page(self):
        path = ROOT / 'pages/2_Tabelle di riferimento.py'
        source = path.read_text(encoding='utf-8')
        tree = ast.parse(source)
        # Execute only the actual navigation bridge with a minimal Streamlit
        # stand-in, not the page setup or any other application state.
        bridge = [
            node for node in tree.body if isinstance(node, ast.With)
            and any(
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == 'st'
                and call.func.attr == 'html'
                for call in ast.walk(node)
            )
        ]
        self.assertEqual(len(bridge), 1)
        self.assertNotIn('components.html(', source)
        for scroll in (False, True):
            with self.subTest(scroll=scroll):
                embedded = []
                st_stub = SimpleNamespace(
                    container=lambda **kwargs: nullcontext(),
                    html=lambda html, **kwargs: embedded.append((html, kwargs)),
                )
                exec(compile(ast.Module(body=bridge, type_ignores=[]),
                             str(path), 'exec'),
                     {'st': st_stub, '_scroll_to_fc': scroll})
                self.assertEqual(len(embedded), 1)
                html, options = embedded[0]
                self.assertEqual(options, {'unsafe_allow_javascript': True})
                self.assertIn("const host = window;", html)
                self.assertNotIn("window.parent", html)
                self.assertIn("doc.addEventListener('click', host.mortemReferenceClick, true)", html)
                self.assertIn("doc.querySelector('.st-key-tables_reference_nav button')", html)
                self.assertIn("host.requestAnimationFrame(scroll)", html)
                self.assertIn(f"if ({str(scroll).lower()})", html)
                self.assertNotIn('SCROLL_TO_FC', html)


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
        cls.html, cls.captions = [], []
        tree = ast.parse(path.read_text(encoding='utf-8'))
        combined_constants = {
            target.id for node in tree.body if isinstance(node, ast.Assign)
            for target in node.targets if isinstance(target, ast.Name)
            and target.id.startswith('_COMBINED_')
        }
        cls.namespace = _isolated_reference_renderer(
            path, combined_constants, '_render_combined_table',
            cls.html, cls.captions,
        )

    def render(self, language):
        self.html.clear()
        self.captions.clear()
        self.namespace['_render_combined_table'](language)
        self.assertEqual(len(self.html), 1)
        self.assertIn('href="Reference" target="_self"', self.html[0])
        self.assertTrue(any('href="Reference"' in caption for caption in self.captions))
        parser = CombinedRows()
        parser.feed(self.html[0])
        self.assertEqual(len(parser.rows), 23)
        text = self.namespace['_COMBINED_TABLE_TEXT'][language]
        return {key: parser.rows[label] for key, label in text.items() if label in parser.rows}

    def interval(self, rows, answers):
        lower, upper = 0, INF_HOURS
        for key, yes in answers:
            bound = rows[key][0 if yes else 1]
            self.assertNotRegex(bound, r'\d,\d')
            if bound == '—':
                continue
            match = re.fullmatch(r'([≥≤]) (\d+(?:\.\d+)?)(?: \[\d+\])?', bound)
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

    def test_updated_reestablishment_bound_has_its_own_source_reference(self):
        # Anders et al., Int J Legal Med 2013: observed re-establishment up to 19 h.
        for language in ('it', 'en'):
            rows = self.render(language)
            self.assertEqual(self.interval(rows, [('reestablishment', True)]), (0, 19))
            self.assertEqual(self.interval(rows, [('reestablishment', False)]), (2, INF_HOURS))
            self.assertTrue(rows['reestablishment'][0].endswith('[4]'))
            # The table now links its abbreviated [4] citation to the full
            # internal bibliography; the DOI belongs to that destination.
            self.assertTrue(any(
                'Anders et al., 2013' in note and 'href="Reference"' in note
                for note in self.captions
            ))
            bibliography = ROOT / 'pages/9_Reference.py'
            self.assertIn('10.1007/s00414-011-0632-z',
                          bibliography.read_text(encoding='utf-8'))
            self.assertEqual(rows['muscle_response'], ('≤ 11', '≥ 3'))

    def test_mechanical_criteria_keep_compound_method_bounds_distinct_from_descriptive_phases(self):
        # Henssge et al. (2000), Table 1: propagated response and local
        # idiomuscular contraction are distinct criteria. The reference table
        # must not be forced to reproduce the application's descriptive states.
        for language in ('it', 'en'):
            rows = self.render(language)
            self.assertEqual(rows['whole_muscle'], ('≤ 2.5', '—'))
            self.assertEqual(rows['mechanical_response'], ('≤ 13', '≥ 1.5'))
            self.assertNotIn('reversible_swelling', rows)
            self.assertEqual(self.interval(rows, [('whole_muscle', False)]), (0, INF_HOURS))


if __name__ == '__main__':
    unittest.main()
