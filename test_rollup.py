import unittest
from pathlib import Path

from rollup import (
    advisory_ids,
    get_tool_config,
    load_latest_hr,
    load_config,
    load_quill_metrics,
    normalize_id,
    quill_week_start,
    reporting_weeks,
)


class ConfigurationTests(unittest.TestCase):
    def test_get_tool_config(self):
        config = {"tools": [{"tool_id": "quill", "wau_threshold": 1}]}

        self.assertEqual(get_tool_config(config, "quill"), config["tools"][0])

        with self.assertRaisesRegex(ValueError, "atlas"):
            get_tool_config(config, "atlas")


class ReportingWindowTests(unittest.TestCase):
    def test_real_reporting_window(self):
        config = load_config(Path("data/reporting_config.json"))

        weeks = reporting_weeks(config)

        self.assertEqual(weeks[0].isoformat(), "2026-08-09")
        self.assertEqual(weeks[-1].isoformat(), "2026-09-27")
        self.assertEqual(len(weeks), 8)


class QuillMetricsTests(unittest.TestCase):
    def test_saturday_and_sunday_use_expected_week_start(self):
        from datetime import datetime

        saturday = datetime.fromisoformat("2026-08-15T23:59:59+00:00")
        sunday = datetime.fromisoformat("2026-08-16T00:00:00+00:00")

        self.assertEqual(quill_week_start(saturday).isoformat(), "2026-08-09")
        self.assertEqual(quill_week_start(sunday).isoformat(), "2026-08-16")

    def test_duplicate_rows_and_power_threshold(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "quill_events.csv"
            rows = [
                "user_id,event_time_utc,event_type,client",
                *[
                    f" E123 ,2026-08-{day:02d}T12:00:00Z,generation,desktop"
                    for day in range(9, 16)
                    if False
                ],
            ]

            for minute in range(12):
                rows.append(
                    f"E123,2026-08-10T12:{minute:02d}:00Z,generation,desktop"
                )
            rows.extend([
                "E123,2026-08-10T12:00:00Z,generation,desktop",
                "E456,2026-08-11T12:00:00Z,generation,desktop",
                "E456,2026-08-12T12:00:00Z,open,desktop",
                "E789,2026-08-11T12:00:00Z,generation,desktop",
            ])

            path.write_text("\n".join(rows) + "\n", encoding="utf-8")

            week = reporting_weeks(load_config(Path("data/reporting_config.json")))[:1]
            metrics, stats = load_quill_metrics(
                path,
                {"E123", "E456", "E789"},
                {"E123", "E456"},
                week,
                wau_threshold=1,
                wpu_threshold=12,
            )

        self.assertEqual(metrics[week[0]]["wau"], {"E123", "E456"})
        self.assertEqual(metrics[week[0]]["wpu"], {"E123"})
        self.assertEqual(stats["exact_duplicate_rows_removed"], 1)


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
