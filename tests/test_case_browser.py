import json
import unittest

from app.case_browser import consume_open_event
from app.case_file import CaseFileError, MAX_BYTES, encode_case, snapshot_case


class BrowserCaseEventTests(unittest.TestCase):
    def setUp(self):
        self.control = {"instance": "active"}
        self.case = snapshot_case({"case_code": "x26-05", "peso": 82., "rt_val": 30.}, "full")
        self.event = {"instance": "active", "action": "open", "event_id": "one",
                      "data": encode_case(self.case).decode()}

    def test_import_is_validated_and_consumed_once(self):
        self.assertEqual(consume_open_event(self.event, self.control), self.case)
        self.assertIsNone(consume_open_event(self.event, self.control))

    def test_stale_and_unrelated_events_do_not_replace_the_case(self):
        for event in (None, [], {**self.event, "instance": "old"},
                      {**self.event, "action": "save"}, {**self.event, "event_id": []}):
            self.assertIsNone(consume_open_event(event, self.control))
        self.assertNotIn("last_event", self.control)

    def test_corrupt_oversized_and_unsupported_cases_are_rejected(self):
        for raw in (None, "not json", "x" * (MAX_BYTES + 1),
                    json.dumps({**self.case, "schema_version": 999}),
                    json.dumps({**self.case, "inputs": {"unexpected": True}})):
            with self.subTest(raw_type=type(raw)), self.assertRaises(CaseFileError):
                consume_open_event({**self.event, "data": raw}, {"instance": "active"})


if __name__ == "__main__":
    unittest.main()
