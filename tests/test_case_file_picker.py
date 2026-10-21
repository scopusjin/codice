import unittest

from app.case_file import CaseFileError, encode_case, snapshot_case
from app.case_file_picker import consume_file_event


class CaseFilePickerTests(unittest.TestCase):
    def test_event_is_bound_to_current_case_and_consumed_once(self):
        raw = encode_case(snapshot_case({"case_code": "X26.117"}, "full")).decode("utf-8")
        event = {"action": "open", "instance": "current", "event_id": "selected", "data": raw}
        state = {}
        self.assertIsNone(consume_file_event(event, "another", state))
        self.assertEqual(state, {})
        self.assertEqual(consume_file_event(event, "current", state)["case_code"], "X26.117")
        self.assertIsNone(consume_file_event(event, "current", state))

    def test_invalid_file_is_rejected_and_can_be_replaced(self):
        state = {}
        event = {"action": "open", "instance": "", "event_id": "bad", "data": "not json"}
        with self.assertRaises(CaseFileError):
            consume_file_event(event, "", state)
        self.assertIsNone(consume_file_event(event, "", state))
        event.update(event_id="valid", data=encode_case(snapshot_case({}, "full")).decode("utf-8"))
        self.assertIsNotNone(consume_file_event(event, "", state))
