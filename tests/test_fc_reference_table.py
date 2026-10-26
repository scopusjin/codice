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


class ObservedRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = {}
        self.all_rows = []
        self.cell = None
        self.cells = []

    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.cells = []
        if tag == 'td': self.cell = []

    def handle_data(self, text):
        if self.cell is not None: self.cell.append(text)

    def handle_endtag(self, tag):
        if tag == 'td':
            self.cells.append(''.join(self.cell).strip())
            self.cell = None
        if tag == 'tr' and len(self.cells) == 2:
            self.rows[self.cells[0]] = self.cells[1]
            self.all_rows.append(tuple(self.cells))


class CombinedReferenceTableTests(unittest.TestCase):
    def render(self, language):
        html, captions = [], []
        namespace = _isolated_reference_renderer(
            ROOT / 'pages/2_Tabelle di riferimento.py',
            {'_COMBINED_TABLE_TEXT', '_COMBINED_BIBLIOGRAPHY'}, '_render_combined_table', html, captions)
        namespace['_render_combined_table'](language)
        self.assertEqual(len(html), 1)
        parser = ObservedRows()
        parser.feed(html[0])
        self.assertEqual(len(parser.all_rows), 35)
        self.assertIn('href="Reference"', html[0])
        self.assertTrue(any('Anders et al., 2013' in note for note in captions))
        self.observed_rows = parser.all_rows
        return parser.rows

    def test_observed_rigor_intervals_match_engine_in_both_languages(self):
        labels = {
            'it': ('Non ancora apprezzabile', 'Presente, in via di intensificazione e generalizzazione',
                   'Presente, intensa e generalizzata', 'In via di risoluzione', 'Completamente risolta'),
            'en': ('Not yet appreciable', 'Present, developing and spreading',
                   'Present, intense and generalized', 'Resolving', 'Completely resolved')}
        for language in labels:
            rows = self.render(language)
            self.assertEqual([rows[label] for label in labels[language]],
                             ['0–7', '0.5–20', '2–96', '24–192', '≥ 24'])

    def test_anatomical_supraciliary_descriptions_keep_all_time_intervals(self):
        for language in ('it', 'en'):
            rows = self.render(language)
            values = [value for label, value in self.observed_rows
                      if ('allo stimolo elettrico' in label if language == 'it'
                          else 'following electrical stimulation' in label)]
            self.assertEqual(values[:7], ['0–6', '1–7', '2–8', '3–13', '3.5–16', '5–22', '≥ 5'])

    def test_reestablishment_has_updated_bound_and_bibliography(self):
        for language, label in (('it', 'Si riforma dopo essere stata vinta'),
                                ('en', 'Re-establishes after being broken')):
            self.assertEqual(self.render(language)[label], '≤ 19 [4]')
        self.assertIn('10.1007/s00414-011-0632-z',
                      (ROOT / 'pages/9_Reference.py').read_text())

    def test_mechanical_observations_preserve_distinct_descriptive_phases(self):
        rows = self.render('it')
        self.assertEqual(rows['Contrazione dell’intero muscolo alla percussione'], '0–2.5')
        self.assertEqual(rows['Tumefazione reversibile alla percussione'], '0–5')
        self.assertEqual(rows['Piccola tumefazione persistente alla percussione'], '0–13')
        self.assertEqual(rows['Nessuna reazione alla percussione'], '≥ 1.5')


if __name__ == '__main__':
    unittest.main()
