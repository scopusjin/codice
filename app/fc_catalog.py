"""Single documentary catalog for the FC panel and the reference page."""

import json
from pathlib import Path

_CATALOG = Path(__file__).resolve().parents[1] / "data/fc_examples.json"


def load_examples():
    """Return fresh records so rendering cannot mutate shared session data."""
    return json.loads(_CATALOG.read_text(encoding="utf-8"))
