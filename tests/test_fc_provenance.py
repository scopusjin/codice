import unittest

from app.case_file import decode_case, encode_case, restored_inputs, snapshot_case
from app.fc_page import FULL_PAGE, MSIL_PAGE, _current_fc_draft
from app.fc_selection import apply_choice, normalize_fc_input, refresh_fc_for_weight


class FCProvenanceTests(unittest.TestCase):
    def test_initial_default_and_deliberately_entered_one_are_distinct(self):
        state = {"fattore_correzione": 1.0, "peso": 70.0}
        draft = _current_fc_draft(state, FULL_PAGE)
        self.assertTrue(draft["preset"])
        self.assertFalse(draft["manual"])
        normalize_fc_input(state, "fattore_correzione")
        draft = _current_fc_draft(state, FULL_PAGE)
        self.assertFalse(draft["preset"])
        self.assertTrue(draft["manual"])

    def test_preset_survives_apply_weight_change_export_and_reopening(self):
        for home, view, values in ((FULL_PAGE, "full", [1., 1.]), (MSIL_PAGE, "msil", [.9, 1.1])):
            with self.subTest(view=view):
                state = {"fattore_correzione": 1., "peso": 70.,
                         "FC_min_beta": values[0], "FC_max_beta": values[1]}
                draft = _current_fc_draft(state, home)
                self.assertTrue(draft["preset"])
                apply_choice(state, {"range": values, "base_range": values, "weight": 70.,
                                     "manual": False, "draft": draft}, msil=view == "msil")
                state["peso"] = 100.
                refresh_fc_for_weight(state, msil=view == "msil")
                restored = restored_inputs(decode_case(encode_case(snapshot_case(state, view))))
                reopened = _current_fc_draft(restored, home)
                self.assertTrue(reopened["preset"])
                self.assertFalse(reopened["manual"])
                self.assertEqual([float(reopened["lo"]), float(reopened["hi"])], values)

    def test_legacy_manual_one_is_not_reclassified_as_a_default(self):
        state = {"fattore_correzione": 1., "peso": 70., "__fc_applied_choice": {
            "range": [1., 1.], "base_range": [1., 1.], "weight": 70., "manual": True}}
        draft = _current_fc_draft(state, FULL_PAGE)
        self.assertFalse(draft["preset"])
        self.assertTrue(draft["manual"])
