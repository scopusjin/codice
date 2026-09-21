"""Catalog consistency across the Python reference table and the JS panel."""

import ast
import json
from pathlib import Path
import subprocess
import sys
import unittest

from app.fc_catalog import load_examples
from app.fc_reference_cases import case_rows

ROOT = Path(__file__).resolve().parents[1]


class FCCatalogTests(unittest.TestCase):
    def test_examples_have_unique_ids_and_independent_records(self):
        examples = load_examples()
        self.assertEqual(len({e['id'] for e in examples}), len(examples))
        for example in examples:
            for key in ('id', 'type', 'title', 'conditions', 'sourceText'):
                self.assertTrue(example[key])
            self.assertTrue(example.get('observations') or example.get('fc'))
        examples[0]['title'] = 'modified in one session'
        self.assertNotEqual(load_examples()[0]['title'], examples[0]['title'])

    def test_frontend_matchers_cover_catalog_and_render_same_values(self):
        script = """
const {api}=require('./tests/fc_panel_harness.cjs');
console.log(JSON.stringify({ids:Object.keys(api.EXAMPLE_MATCHERS),
 rows:api.EXAMPLES.map(e=>({conditions:api.exampleConditions(e),fc:api.exampleFCText(e)}))}));
"""
        data = json.loads(subprocess.check_output(['node', '-e', script], cwd=ROOT, text=True))
        self.assertEqual(data['ids'], [e['id'] for e in load_examples()])
        for row, js_row in zip(case_rows(), data['rows'], strict=True):
            self.assertEqual(row['Condizioni'], js_row['conditions'])
            self.assertEqual(row['FC'], js_row['fc'].removeprefix('FC: '))

    def test_description_import_does_not_load_old_engine(self):
        subprocess.run([sys.executable, '-c', """
import sys
from app.fc_description import build_cf_description
assert build_cf_description(1.4, None, manual_override=True) == '1.40'
assert 'app.factor_calc' not in sys.modules
assert 'numpy' not in sys.modules
assert 'pandas' not in sys.modules
"""], cwd=ROOT, check=True)

    def test_application_has_no_import_of_old_engine(self):
        paths = [ROOT / 'Stima_epoca_decesso.py', *ROOT.glob('app/**/*.py'), *ROOT.glob('pages/*.py')]
        for path in paths:
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                if isinstance(node, ast.ImportFrom):
                    self.assertNotEqual(node.module, 'app.factor_calc', str(path))
                    if node.module == 'app':
                        self.assertNotIn('factor_calc', [n.name for n in node.names], str(path))
                elif isinstance(node, ast.Import):
                    self.assertNotIn('app.factor_calc', [n.name for n in node.names], str(path))
