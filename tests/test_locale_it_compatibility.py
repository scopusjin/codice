# -*- coding: utf-8 -*-

import unittest

import app.locales.it as locale_it
import app.tanatology_texts_it as legacy_it


class ItalianLocaleCompatibilityTests(unittest.TestCase):
    def test_legacy_module_reexports_exact_locale_objects(self):
        self.assertEqual(tuple(legacy_it.__all__), tuple(locale_it.__all__))
        for name in locale_it.__all__:
            self.assertIs(
                getattr(legacy_it, name),
                getattr(locale_it, name),
                msg=f"Legacy export differs for {name}",
            )


if __name__ == "__main__":
    unittest.main()
