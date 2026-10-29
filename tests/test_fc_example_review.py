"""Review coverage and lossless documentary metadata transfer."""
import json
from collections import Counter
from pathlib import Path
import subprocess
import unittest
from app.fc_catalog import load_examples
from app.locales.en_runtime import TEXT

ROOT=Path(__file__).resolve().parents[1]


class ExampleReviewTests(unittest.TestCase):
    def test_all_152_records_reviewed_without_rewriting_source_data(self):
        raw=json.loads((ROOT/'data/fc_examples.json').read_text())
        review=json.loads((ROOT/'data/fc_example_review.json').read_text())
        self.assertEqual(set(review['entries']),{e['id'] for e in raw})
        self.assertEqual(Counter(e['status'] for e in review['entries'].values()),
                         {'retained':41,'comparison':107,'archive':4})
        for original, loaded in zip(raw,load_examples(),strict=True):
            metadata=loaded.pop('contextualReview')
            self.assertEqual(original,loaded)
            self.assertTrue(metadata['reason'])
            if metadata['status']=='comparison':self.assertTrue(metadata['criteria'])
        for profile in review['profiles'].values():
            self.assertIn(profile['note'],TEXT)
            self.assertNotEqual(TEXT[profile['note']],profile['note'])

    def test_reachable_examples_support_boundaries_and_display(self):
        subprocess.run(['node','tests/test_fc_reviewed_examples.cjs'],cwd=ROOT,check=True)
