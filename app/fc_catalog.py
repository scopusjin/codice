"""Documentary FC examples and reviewed contextual comparisons (no FC rules)."""
import json
from pathlib import Path

_DATA = Path(__file__).resolve().parents[1] / "data"


def load_examples():
    """Return fresh records with review metadata, retaining source values verbatim."""
    examples = json.loads((_DATA / "fc_examples.json").read_text(encoding="utf-8"))
    review = json.loads((_DATA / "fc_example_review.json").read_text(encoding="utf-8"))
    for example in examples:
        entry = review["entries"][example["id"]]
        example["contextualReview"] = dict(entry)
        if entry.get("profile"):
            example["contextualReview"]["criteria"] = review["profiles"][entry["profile"]]
    return examples
