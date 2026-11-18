# AI Tool Adoption Weekly Rollup

## Run

Python 3.10 or later is required.

```bash
python3 -m pip install -r requirements.txt
python3 rollup.py
python3 -m unittest -v test_rollup.py
```

The command reads `data/` and writes `out/weekly_tool_metrics.csv`.

## Data Issues Found

- HR: 2,445 rows contained 45 repeated normalized employee IDs requiring latest-effective-date selection. The latest HR records identified 1,507 unique Advisory employees; 1,522 IDs appeared in at least one ADV row historically, but 15 of them have since moved to another division and are excluded from the latest-scope count.
- Identity: 8,455 Quill rows contained employee IDs with surrounding whitespace or letter-case differences.
- Quill: 94,558 source rows included 1,397 exact duplicate rows, 2,064 unknown-HR rows, 31,546 non-Advisory rows, and 1,737 generation rows outside the reporting window.
- Atlas: 4,682 data rows were present across eight deliveries. No blank IDs or missing metric values were found.
- Atlas re-delivery: The `20260907` and `20260913` deliveries covered the same reporting week. The later `20260913` extract replaced the earlier delivery.
- Atlas coverage: No Atlas delivery covered the reporting week starting 2026-09-20, so that week's Atlas and `ANY` values are unknown rather than zero.

## Head of Advisory

- Quill averaged 532.9 WAU (35.4% of Advisory) and 199.0 WPU (13.2%) per week. Usage peaked in the week starting 2026-09-20 at 641 WAU (42.5%) and 231 WPU (15.3%), and was lowest in the week starting 2026-09-13 at 381 WAU (25.3%) and 135 WPU (9.0%).
- Atlas averaged 264.9 WAU (17.6% of Advisory) and 70.4 WPU (4.7%) across measured weeks. Usage was highest in the week starting 2026-09-27 at 312 WAU (20.7%) and 84 WPU (5.6%), and lowest in the week starting 2026-08-16 at 229 WAU (15.2%) and 60 WPU (4.0%).
- `ANY` reached 791 unique users in the week starting 2026-09-27 (52.5% of Advisory). A person active on both tools is counted once.
- Caveat: 2026-09-20 Atlas and `ANY` values are unknown because no Atlas data was delivered; they must not be interpreted as a drop or as zero.

## Leadership Policy Question

If a measured tool has `wau = 0`, `wpu_rate = Infinity`; leadership should agree before release whether to show `Infinity`, leave it blank, or use a defined alternative.

## What to Do Next

- Retrieve Quill and Atlas data directly from their source APIs instead of files.
- Use `out/weekly_tool_metrics.csv` in a dashboard tool to visualize weekly WAU, WPU, WPU rate, and `ANY` trends for leadership.
- Clarify and document the leadership presentation rule for `ANY` and zero active users.

## Running in Production

- Agree on delivery timelines with both vendors, then schedule the rollup only after the source data is due and available.
- Retrieve data from source APIs and retain copies of each delivery or extract for traceability.
- Send an email or alert if the rollup or CSV generation fails.
- Stop publication if required fields, thresholds, or reporting weeks are missing, and revalidate results before refreshing the dashboard.
