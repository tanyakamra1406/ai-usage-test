import argparse
from pathlib import Path

from src.config import get_tool_config, load_config, reporting_weeks
from src.hr import advisory_ids, load_latest_hr
from src.quill import load_quill_metrics
from src.atlas import load_atlas_metrics
from src.reporting import build_reporting_rows, write_weekly_metrics


DEFAULT_DATA_DIR = Path("data")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the weekly AI tool adoption rollup")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="directory containing reporting_config.json and source files",
    )
    args = parser.parse_args()

    config = load_config(args.data_dir / "reporting_config.json")
    weeks = reporting_weeks(config)

    latest_hr, hr_stats = load_latest_hr(args.data_dir / "hr_roster.csv")
    advisory = advisory_ids(latest_hr)

    quill_config = get_tool_config(config, "quill")
    quill_metrics, quill_stats = load_quill_metrics(
        args.data_dir / "quill_events.csv",
        set(latest_hr),
        advisory,
        weeks,
        int(quill_config["wau_threshold"]),
        int(quill_config["wpu_threshold"]),
    )

    atlas_config = get_tool_config(config, "atlas")
    atlas_metrics, atlas_stats = load_atlas_metrics(
        args.data_dir / "atlas",
        set(latest_hr),
        advisory,
        weeks,
        int(atlas_config["wau_threshold"]),
        int(atlas_config["wpu_threshold"]),
    )

    print("\n".join(week.isoformat() for week in weeks))
    print(f"latest_advisory_ids={len(advisory)}")
    print(f"hr_rows={hr_stats['hr_rows']}")
    for week in weeks:
        metrics = quill_metrics[week]
        print(
            f"quill {week.isoformat()} "
            f"wau={len(metrics['wau'])} wpu={len(metrics['wpu'])}"
        )
    print(f"quill_rows={quill_stats['quill_rows']}")
    print(f"exact_duplicate_rows_removed={quill_stats['exact_duplicate_rows_removed']}")
    print(f"unknown_hr_rows={quill_stats['unknown_hr_rows']}")
    print(f"non_advisory_rows={quill_stats['non_advisory_rows']}")
    for week in weeks:
        metrics = atlas_metrics[week]
        print(
            f"atlas {week.isoformat()} "
            f"wau={len(metrics['wau'])} wpu={len(metrics['wpu'])}"
        )
    print(f"atlas_files={atlas_stats['atlas_files']}")
    print(f"atlas_replacements={atlas_stats['atlas_replacements']}")

    quill_measured = {
        week: week in quill_stats["measured_weeks"]
        for week in weeks
    }
    atlas_measured = {
        week: week in atlas_stats["measured_weeks"]
        for week in weeks
    }
    rows = build_reporting_rows(
        weeks,
        quill_metrics,
        atlas_metrics,
        quill_measured,
        atlas_measured,
    )
    write_weekly_metrics(Path("out/weekly_tool_metrics.csv"), rows)


if __name__ == "__main__":
    main()
