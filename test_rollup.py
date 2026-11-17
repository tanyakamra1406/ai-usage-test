import unittest
from pathlib import Path

from rollup import advisory_ids, load_latest_hr, load_config, normalize_id, reporting_weeks


class ReportingWindowTests(unittest.TestCase):
    def test_real_reporting_window(self):
        config = load_config(Path("data/reporting_config.json"))

        weeks = reporting_weeks(config)

        self.assertEqual(weeks[0].isoformat(), "2026-08-09")
        self.assertEqual(weeks[-1].isoformat(), "2026-09-27")
        self.assertEqual(len(weeks), 8)


class HrScopeTests(unittest.TestCase):
    def test_normalize_id(self):
        self.assertEqual(normalize_id("  e123  "), "E123")
        self.assertEqual(normalize_id(None), "")

    def test_latest_hr_and_advisory_scope(self):
        with __import__("tempfile").TemporaryDirectory() as directory:
            path = Path(directory) / "hr_roster.csv"
            path.write_text(
                "Employee_ID,Division,Department,Region,Job_Level,Effective_Date\n"
                " e123 ,ADV,One,AMER,L1,2025-01-01\n"
                "E123,ADV,Two,AMER,L2,2026-01-01\n"
                "E456,TAX,Tax,AMER,L3,2026-01-01\n",
                encoding="utf-8",
            )

            latest, stats = load_latest_hr(path)

        self.assertEqual(latest["E123"]["Department"], "Two")
        self.assertEqual(advisory_ids(latest), {"E123"})
        self.assertEqual(stats["hr_rows"], 3)
        self.assertEqual(stats["normalized_whitespace_or_case_rows"], 1)
        self.assertEqual(stats["duplicate_normalized_ids"], 1)


if __name__ == "__main__":
    unittest.main()
