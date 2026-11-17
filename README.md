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

- Quill weekly WAU ranged from 381 to 641 people; Quill WPU ranged from 135 to 231 people.
- Atlas weekly WAU ranged from 229 to 312 people in measured weeks; Atlas WPU ranged from 60 to 84 people.
- `ANY` represents the number of unique people active on either Quill or Atlas. A person active on both tools is counted once. It reached 791 people in the week starting 2026-09-27.
- Caveat: 2026-09-20 Atlas and `ANY` values are unknown because no Atlas data was delivered; they must not be interpreted as zero.

## Leadership Policy Question

A measured tool with `wau = 0` would produce `wpu_rate = Infinity`. Before sharing a result with leaders, agree on whether this should remain `Infinity`, become blank, or be handled as a different defined state.

## What to Do Next

- Add independent source reconciliation and expected-row controls.
- Add a repeatable data-quality report for rejected, unknown, and duplicate records.
- Add automated end-to-end validation of every reporting week and tool row.
- Clarify and document the leadership presentation rule for `ANY` and zero active users.

## Running in Production

- Run on a schedule from an immutable reporting window and source snapshot.
- Store source deliveries and processing outputs with timestamps and extract lineage.
- Fail closed on missing required columns, thresholds, or reporting-window data; do not publish partial results.
- Validate distinct-person counts, week coverage, re-delivery selection, and CSV schema before publication.
- Add alerts for source gaps, unexpected duplicate rates, and leadership-dashboard refresh failures.
