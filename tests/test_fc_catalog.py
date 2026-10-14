"""Selected contextual examples, source precision and frontend transfer."""

import ast
import json
import re
from pathlib import Path
import subprocess
import sys
import unittest

from app.fc_catalog import load_examples

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
 rows:api.EXAMPLES.map(e=>({id:e.id,conditions:api.exampleConditions(e),fc:api.exampleFCText(e)}))}));
"""
        data = json.loads(subprocess.check_output(['node', '-e', script], cwd=ROOT, text=True))
        examples = load_examples()
        self.assertEqual(data['ids'], [e['id'] for e in examples])
        self.assertFalse(any(e.get('referenceOnly') for e in examples))
        for row, js_row in zip(examples, data['rows'], strict=True):
            self.assertEqual(row['id'], js_row['id'])
            conditions = row['conditions'].replace('aria mobile', 'correnti d’aria').replace('aria ferma', 'assenza di correnti d’aria')
            self.assertEqual(re.sub(r'(\d),(\d)', r'\1.\2', conditions), js_row['conditions'])
            expected = row.get('observations') or (
                f"FC iniziale: {row['fc']}; a {row['weight']:.1f} kg: {row['adjustedFc']}."
                if row.get('weightNote') else 'FC: ' + row['fc'])
            self.assertEqual(expected, js_row['fc'])

    def test_description_import_does_not_load_old_engine(self):
        subprocess.run([sys.executable, '-c', """
import sys
from app.fc_description import build_cf_description
assert build_cf_description(1.4, None, manual_override=True) == '1.40'
assert 'app.factor_calc' not in sys.modules
assert 'numpy' not in sys.modules
assert 'pandas' not in sys.modules
"""], cwd=ROOT, check=True)

    def test_documentary_weights_and_case_limits_are_retained(self):
        rows = {row['title']: row for row in load_examples()}
        self.assertEqual(rows['Casi 51 e 44']['weights'], [69.5, 65])
        self.assertIn('69.5 kg', rows['Casi 51 e 44']['observations'])
        self.assertEqual(rows['Caso H15']['weight'], 67.5)
        self.assertEqual(rows['Caso B54']['weight'], 63.5)
        self.assertEqual(rows['Caso 33']['weight'], 62)
        self.assertIn('41.6', rows['Caso 33']['conditions'])
        self.assertIn('Metodo non applicato', rows['Caso 33']['notes'])
        self.assertIn('non verificato', rows['Caso 6']['notes'])
        self.assertEqual(sum(e['type'] == 'Caso operativo' for e in load_examples()), 6)
        self.assertEqual(sum(e['type'] in ('Esperimento', 'Esperimenti') for e in load_examples()), 20)
        self.assertEqual(sum(e['type'] == 'Simulatore' for e in load_examples()), 9)
        for row in rows.values():
            self.assertTrue(row.get('weight') or row.get('weights') or row.get('virtualWeight'))

    def test_new_case_references_require_relevant_conditions(self):
        script = """
const {api}=require('./tests/fc_panel_harness.cjs');
const wet={state:'Bagnato',air:'continuous',surf:1,s:2,p:0,m:0,h:0,wetCase:true};
const bed={state:'Asciutto',air:'still',surf:2,s:0,p:0,m:0,h:0};
console.log(JSON.stringify([
 api.EXAMPLE_MATCHERS['case-22'](wet),
 api.EXAMPLE_MATCHERS['case-22']({...wet,wetCase:false}),
 api.EXAMPLE_MATCHERS['case-22']({...wet,air:'intermittent'}),
 api.EXAMPLE_MATCHERS['case-62'](bed),
 api.EXAMPLE_MATCHERS['case-62']({...bed,state:'Bagnato'}),
 api.EXAMPLE_MATCHERS['case-62']({...bed,m:1}),
 api.EXAMPLE_MATCHERS['case-62']({...bed,surf:0})]));
"""
        results = json.loads(subprocess.check_output(['node', '-e', script], cwd=ROOT, text=True))
        self.assertEqual(results, [True, False, False, True, False, False, False])

    def test_contextual_examples_render_with_sources(self):
        subprocess.run(['node', 'tests/test_fc_contextual_examples.cjs'], cwd=ROOT, check=True)

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
