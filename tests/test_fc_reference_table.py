"""Check source-chart column alignment in the actual reference-table renderer."""

import ast
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
import unittest

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


if __name__ == '__main__':
    unittest.main()
