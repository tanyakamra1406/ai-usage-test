import unittest
from datetime import date
from pathlib import Path

from openpyxl import Workbook

from rollup import atlas_week_start, load_atlas_metrics
from src.reporting import build_reporting_rows


class RedeliveryTest(unittest.TestCase):
    def test_latest_delivery_replaces_earlier_delivery(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            atlas_dir = Path(directory)

            first = Workbook()
            first.active.title = "Usage"
            first.active.append(["User ID", "Week Ending", "Queries Run", "Active Days"])
            first.active.append(["E123", date(2026, 8, 22), 10, 5])
            first.save(atlas_dir / "atlas_usage_20260817.xlsx")

            later = Workbook()
            later.active.title = "Usage"
            later.active.append(["User ID", "Week Ending", "Queries Run", "Active Days"])
            later.active.append(["E123", date(2026, 8, 22), 30, 3])
            later.save(atlas_dir / "atlas_usage_20260824.xlsx")

            week = date(2026, 8, 16)
            metrics, stats = load_atlas_metrics(
                atlas_dir,
                {"E123"},
                {"E123"},
                [week],
                wau_threshold=1,
                wpu_threshold=25,
            )

        self.assertEqual(atlas_week_start(date(2026, 8, 22)), week)
        self.assertEqual(metrics[week]["wau"], {"E123"})
        self.assertEqual(metrics[week]["wpu"], {"E123"})
        self.assertEqual(stats["atlas_replacements"], 1)


class AnyTest(unittest.TestCase):
    def test_any_counts_overlapping_person_once(self):
        week = date(2026, 8, 9)
        quill = {"wau": {"E123", "E456"}, "wpu": {"E123"}}
        atlas = {"wau": {"E456", "E789"}, "wpu": {"E789"}}

        rows = build_reporting_rows(
            [week],
            {week: quill},
            {week: atlas},
            {week: True},
            {week: True},
        )

        any_row = next(row for row in rows if row["tool_id"] == "ANY")
        self.assertEqual(any_row["wau"], 3)
        self.assertEqual(any_row["wpu"], 2)


if __name__ == "__main__":
    unittest.main()
