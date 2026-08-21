# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch

import app.i18n as i18n
import app.locales.it as locale_it
import app.tanatology_texts_it as legacy_it


class ItalianLocaleCompatibilityTests(unittest.TestCase):
    def test_legacy_module_preserves_public_exports(self):
        self.assertEqual(tuple(legacy_it.__all__), tuple(locale_it.__all__))

        routed = {"livor_description_it", "rigor_description_it"}
        for name in locale_it.__all__:
            if name in routed:
                continue
            self.assertIs(
                getattr(legacy_it, name),
                getattr(locale_it, name),
                msg=f"Legacy export differs for {name}",
            )

    def test_routed_base_descriptions_match_locale_exactly(self):
        for state_id in locale_it.LIVOR_DESCRIPTION_IT_BY_ID:
            self.assertEqual(
                legacy_it.livor_description_it(state_id),
                locale_it.livor_description_it(state_id),
            )
        for state_id in locale_it.RIGOR_DESCRIPTION_IT_BY_ID:
            self.assertEqual(
                legacy_it.rigor_description_it(state_id),
                locale_it.rigor_description_it(state_id),
            )

        self.assertEqual(legacy_it.livor_description_it("unknown"), None)
        self.assertEqual(legacy_it.rigor_description_it("unknown"), None)

    def test_legacy_base_description_helpers_route_through_i18n(self):
        with patch.object(i18n, "livor_description", return_value="livor-marker"):
            self.assertEqual(legacy_it.livor_description_it("any"), "livor-marker")

        with patch.object(i18n, "rigor_description", return_value="rigor-marker"):
            self.assertEqual(legacy_it.rigor_description_it("any"), "rigor-marker")


if __name__ == "__main__":
    unittest.main()
