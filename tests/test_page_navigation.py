"""Session navigation regressions: direct FC, tables, references, and sidebar."""

import unittest

from app.page_navigation import (
    FC_VIEW, FULL_PAGE, MSIL_PAGE, TABLES_PAGE, REFERENCES_PAGE, SETTINGS_PAGE,
    back_label, go_back, previous_view, record_page_visit,
)


class PageNavigationTests(unittest.TestCase):
    def test_home_to_tables_has_generic_back(self):
        state = {}
        record_page_visit(state, FULL_PAGE)
        record_page_visit(state, TABLES_PAGE)
        record_page_visit(state, TABLES_PAGE)  # rerun is not a visit
        self.assertEqual(back_label(state, TABLES_PAGE), "← Indietro")
        self.assertEqual(go_back(state, TABLES_PAGE), FULL_PAGE)
        self.assertIsNone(previous_view(state, FULL_PAGE))

    def test_sopralluogo_to_tables_returns_to_sopralluogo(self):
        state = {}
        record_page_visit(state, MSIL_PAGE)
        record_page_visit(state, TABLES_PAGE)
        self.assertEqual(back_label(state, TABLES_PAGE), "← Indietro")
        self.assertEqual(go_back(state, TABLES_PAGE), MSIL_PAGE)

    def test_fc_to_tables_to_references_returns_each_previous_page(self):
        state = {"__fc_active": True, "__fc_home": MSIL_PAGE, "__fc_tables_return": True}
        for view in (MSIL_PAGE, FC_VIEW, TABLES_PAGE, REFERENCES_PAGE):
            record_page_visit(state, view)
        self.assertEqual(back_label(state, REFERENCES_PAGE), "← Indietro")
        self.assertEqual(go_back(state, REFERENCES_PAGE), TABLES_PAGE)
        self.assertEqual(back_label(state, TABLES_PAGE), "← Indietro al FC")
        self.assertEqual(go_back(state, TABLES_PAGE), MSIL_PAGE)
        state["__fc_active"] = False
        record_page_visit(state, MSIL_PAGE)
        self.assertIsNone(previous_view(state, MSIL_PAGE))

    def test_direct_fc_reference_has_fc_back(self):
        state = {"__fc_active": True, "__fc_home": FULL_PAGE}
        for view in (FULL_PAGE, FC_VIEW, REFERENCES_PAGE):
            record_page_visit(state, view)
        self.assertEqual(back_label(state, REFERENCES_PAGE), "← Indietro al FC")
        self.assertEqual(go_back(state, REFERENCES_PAGE), FULL_PAGE)

    def test_settings_is_a_possible_previous_page(self):
        state = {}
        for view in (FULL_PAGE, SETTINGS_PAGE, TABLES_PAGE):
            record_page_visit(state, view)
        self.assertEqual(go_back(state, TABLES_PAGE), SETTINGS_PAGE)
        self.assertEqual(go_back(state, SETTINGS_PAGE), FULL_PAGE)

    def test_direct_link_falls_back_to_home(self):
        state = {}
        record_page_visit(state, REFERENCES_PAGE)
        self.assertEqual(back_label(state, REFERENCES_PAGE), "← Indietro")
        self.assertEqual(go_back(state, REFERENCES_PAGE), FULL_PAGE)

    def test_stale_fc_history_does_not_route_to_closed_editor(self):
        state = {"__fc_active": True, "__fc_home": MSIL_PAGE}
        for view in (MSIL_PAGE, FC_VIEW, TABLES_PAGE):
            record_page_visit(state, view)
        state["__fc_active"] = False
        self.assertEqual(back_label(state, TABLES_PAGE), "← Indietro")
        self.assertEqual(go_back(state, TABLES_PAGE), MSIL_PAGE)
        self.assertIsNone(previous_view(state, MSIL_PAGE))


if __name__ == "__main__":
    unittest.main()
