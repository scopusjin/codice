"""Selected documentary examples for contextual FC explanations.

The complete maintenance archive is private and is not distributed with the app."""

import json
from pathlib import Path

_CATALOG = Path(__file__).resolve().parents[1] / "data/fc_examples.json"


def load_examples():
    """Return fresh records so rendering cannot mutate shared session data."""
    return json.loads(_CATALOG.read_text(encoding="utf-8"))
