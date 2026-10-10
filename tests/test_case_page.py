import subprocess
import sys
import unittest
from pathlib import Path


class CasePageIntegrationTests(unittest.TestCase):
    def test_case_streamlit_integration(self):
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests",
                                 "-p", "case_page_checks.py", "-v"],
                                cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
