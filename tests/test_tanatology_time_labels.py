"""The detailed report always dates separate tanatological observations."""

import datetime
from pathlib import Path
import unittest

from app.tanatology_times import format_tanatology_measurement_datetime

ROOT = Path(__file__).resolve().parents[1]


class TanatologyDateDescriptionsTests(unittest.TestCase):
    def test_different_hours_same_day_both_include_the_date(self):
        inspection = datetime.datetime(2026, 10, 15, 19, 30)
        measurement = datetime.datetime(2026, 10, 15, 20, 10)
        self.assertEqual(format_tanatology_measurement_datetime(measurement),
                         "alle ore 20:10 del 15.10.2026")
        self.assertEqual(format_tanatology_measurement_datetime(inspection),
                         "alle ore 19:30 del 15.10.2026")

    def test_different_days_keep_full_dates(self):
        inspection = datetime.datetime(2026, 10, 15, 23, 45)
        measurement = datetime.datetime(2026, 10, 16, 0, 30)
        self.assertEqual(format_tanatology_measurement_datetime(measurement),
                         "alle ore 00:30 del 16.10.2026")
        self.assertEqual(format_tanatology_measurement_datetime(inspection),
                         "alle ore 23:45 del 15.10.2026")

    def test_description_uses_date_formatter_without_modifying_offset(self):
        source = (ROOT / "app/graphing.py").read_text(encoding="utf-8")
        self.assertIn("diff_h = (data_ora_param - data_ora_ispezione_raw).total_seconds() / 3600.0", source)
        self.assertIn("if diff_h != 0:", source)
        self.assertIn("measurement_when = format_tanatology_measurement_datetime(data_ora_param)", source)
        self.assertIn("reference_when = format_tanatology_measurement_datetime(data_ora_ispezione_raw)", source)
        self.assertNotIn("include_date = data_ora_param.date()", source)


if __name__ == "__main__":
    unittest.main()
