import unittest
from app.report_formatting import underline_findings
from app.case_report import plain_text
from app.graphing import _wrap_final
from app.locales import it_henssge, en_henssge


class ReportFormattingTests(unittest.TestCase):
    def test_preserves_prose_and_existing_underlines(self):
        html = ('<ul><li>Il raffreddamento cadaverico; <u>macchie ipostatiche</u>; '
                'rigidità cadaverica; eccitabilità muscolare meccanica residua; '
                'stimolo elettrico.</li></ul>')
        formatted = _wrap_final(html)
        self.assertEqual(plain_text(html), plain_text(formatted))
        for phrase in ('raffreddamento cadaverico', 'macchie ipostatiche',
                       'rigidità cadaverica', 'eccitabilità muscolare meccanica residua',
                       'stimolo elettrico'):
            self.assertIn('<u>' + phrase + '</u>', formatted)
        self.assertNotIn('<u><u>', formatted)
        self.assertEqual(underline_findings(formatted), formatted)

    def test_henssge_is_a_paragraph_in_both_languages(self):
        for locale in (it_henssge, en_henssge):
            with self.subTest(locale=locale.__name__):
                html = _wrap_final(locale.henssge_detail_paragraph('1–8 h'))
                self.assertIn('margin-left:40px;', html)
                self.assertNotIn('<li', html)
                self.assertNotIn('•', plain_text(html))
                self.assertIn('1–8 h', plain_text(html))
