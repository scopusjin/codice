"""Run app integration checks in isolation from legacy global Streamlit wrappers."""
import subprocess
import sys
import unittest
from pathlib import Path


class FCPageIntegrationTests(unittest.TestCase):
    def test_streamlit_integration(self):
        # app.__init__ installs process-global presentation wrappers. Keep these
        # synthetic desktop/MSIL sessions separate from the existing mobile suite.
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'fc_page_checks.py', '-v'],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
