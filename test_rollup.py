import unittest
from pathlib import Path

from rollup import load_config, reporting_weeks


class ReportingWindowTests(unittest.TestCase):
    def test_real_reporting_window(self):
        config = load_config(Path("data/reporting_config.json"))

        weeks = reporting_weeks(config)

        self.assertEqual(weeks[0].isoformat(), "2026-08-09")
        self.assertEqual(weeks[-1].isoformat(), "2026-09-27")
        self.assertEqual(len(weeks), 8)


if __name__ == "__main__":
    unittest.main()
