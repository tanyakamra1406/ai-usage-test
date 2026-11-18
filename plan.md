# Implementation Plan

## Working Agreements

- [x] Work proceeds one stage at a time and only after explicit authorization.
- [x] Commits stay on `main` and remain local until explicit authorization to push.
- [x] Do not push anything without permission.
- [x] Do not commit `data/` or generated ZIP files.
- [x] Commit the requirement spec or implementation README only when appropriate for the stage.
- [x] Keep assumptions visible and test the most likely edge cases.
- [x] Use the reporting configuration as the source of truth.

## Data and Rule Decisions

- [x] Normalize employee IDs by trimming surrounding whitespace and converting to uppercase.
- [x] Select each person's latest HR record by `Effective_Date`, then use the latest record for all reporting weeks.
- [x] Restrict output to employees whose latest HR record has `Division = ADV`.
- [x] Exclude IDs absent from the latest HR scope and IDs belonging to other divisions.
- [x] Parse Quill timestamps as UTC and assign events to Sunday-to-Saturday reporting weeks.
- [x] For Quill WAU, count distinct people with at least one `generation` event at the configured threshold.
- [x] For Quill WPU, count distinct Advisory people meeting the configured WPU threshold for generation events.
- [x] Do not count Quill duplicate event rows as additional people.
- [x] Parse Atlas workbook `Usage` sheets beginning after the title and blank rows.
- [x] Normalize Atlas `User ID`, `Queries Run`, and `Active Days` values.
- [x] Map Atlas `Week Ending` to the reporting week start, a Sunday.
- [x] Select the latest Atlas delivery for each reporting week when redeliveries overlap.
- [x] Use the configured Atlas WAU and WPU thresholds.
- [x] Mark a tool unmeasured and leave `wau`, `wpu`, and `wpu_rate` blank when it has no data for a week.
- [x] Keep measured zero-count tools distinct from unmeasured tools; measured zero results remain `0`.
- [x] Where `wau = 0`, write `Infinity` for `wpu_rate`, and document a README question about the policy before leadership sharing.
- [x] Implement `ANY` by unioning distinct active people across measured tools.
- [x] Implement `ANY` power users by unioning distinct people meeting a power threshold on at least one measured tool.
- [x] Deduplicate overlap across Quill and Atlas; a person is counted once in `ANY`.
- [x] Set `ANY.measured = true` only when both tools are measured for the week.
- [x] When `ANY` is not measured, leave `wau`, `wpu`, and `wpu_rate` blank.
- [x] Preserve `ANY` as a supplemental portfolio metric and explain it as unique people active on either measured tool.
- [x] Document unresolved implementation policy decisions in the README.

## Stage 0: Repository Baseline

- [x] Verify `main` and the `origin` remote.
- [x] Keep `.gitignore` limited to `/data/` unless a real generated file first requires another ignore rule.
- [x] Commit repository setup to `main` only after the baseline is confirmed.
- [x] Push the reconciled baseline and implementation plan only after authorization.
- [ ] Do not update the README in this stage unless repository setup explicitly requires it.

## Stage 1: Project Structure and Configuration

- [x] Add the Python entrypoint and supporting modules or functions.
- [x] Add `requirements.txt` or a dependency declaration only for libraries actually required.
- [x] Load and validate `data/reporting_config.json`.
- [x] Validate the reporting window and required tool definitions.
- [x] Build the ordered list of Sunday week starts in the reporting window.
- [x] Add a documented run command to the README.
- [x] Run a narrow configuration/scaffolding validation.
- [x] Commit the stage changes to `main`.
- [x] Push only after explicit authorization.

## Stage 2: Shared Identity and HR Scope

- [x] Implement CSV input loading for `hr_roster.csv`.
- [x] Implement ID normalization and effective-date parsing.
- [x] Select each normalized person's latest HR record.
- [x] Build the set of latest Advisory IDs.
- [x] Record data issue counts for duplicate IDs, missing IDs, and division changes.
- [x] Add focused tests for normalization and latest effective date.
- [x] Update the README with the implementation approach and discovered HR issues.
- [x] Commit tested shared identity/HR scope code.
- [x] Push only after explicit authorization.

## Stage 3: Quill Metrics

- [x] Implement Quill CSV loading and UTC timestamp parsing.
- [x] Filter events to the reporting window and `generation` event type.
- [x] Assign events to Sunday week starts.
- [x] Count distinct Advisory people for WAU and WPU.
- [x] Add focused tests for UTC boundaries, duplicate events, ID normalization, and thresholds.
- [x] Update the README with Quill handling and observed Quill data issues.
- [x] Commit tested Quill logic.
- [x] Push only after explicit authorization.

## Stage 4: Atlas Metrics and Re-delivery

- [x] Implement workbook discovery and `Usage` sheet parsing.
- [x] Locate the real header rather than assuming it is in worksheet row 1.
- [x] Parse and normalize `User ID`, `Week Ending`, `Queries Run`, and `Active Days`.
- [x] Assign Atlas rows to reporting week starts.
- [x] Replace earlier records with the latest extract for each reporting week.
- [x] Count distinct Advisory people for Atlas WAU and WPU.
- [x] Add focused tests for workbook layout, week mapping, thresholds, and re-delivery replacement.
- [x] Update the README with Atlas handling and observed workbook/data issues.
- [x] Commit the modular refactor and tested Atlas logic.
- [x] Push only after explicit authorization.

## Stage 5: Reporting Table and ANY

- [x] Produce exactly one row per reporting Sunday for `quill`, `atlas`, and `ANY`.
- [x] Preserve reporting columns in this order: `week_start, tool_id, wau, wpu, wpu_rate, measured`.
- [x] Calculate `wpu_rate = wpu / wau` and round to 4 decimal places.
- [x] Output `Infinity` when a measured row has `wau = 0` and `wpu = 0` until a policy is approved.
- [x] Leave `wau`, `wpu`, and `wpu_rate` blank for unmeasured rows.
- [x] Write `true` and `false` for CSV measured values.
- [x] Union distinct active and power users for `ANY` only from measured tools.
- [x] Mark `ANY` measured only when both tools are measured.
- [x] Add focused tests for no-data, measured-zero, redelivery, and `ANY` overlap behavior.
- [x] Update the README with output format and result policy questions.
- [x] Commit tested rollup generation.
- [x] Push Stage 5 after explicit authorization.

## Stage 6: Tests and Data Issue Summary

- [x] Run targeted tests for re-delivery replacement and `ANY` overlap/deduplication.
- [x] Validate generated row counts and tool ordering.
- [x] Compare representative totals against independent calculations.
- [x] Record approximate counts for duplicate, whitespace/case, unknown-HR, non-ADV, and outside-window records.
- [x] Disclose confirmed Atlas redelivery behavior.
- [x] Update the README with confirmed data issues and affected record counts.
- [x] Commit targeted tests and README data findings.
- [ ] Push Stage 6 only after explicit authorization.

## Stage 7: Leadership Summary and Production Guidance

- [x] Generate `out/weekly_tool_metrics.csv`.
- [x] Summarize only confirmed headline numbers for Advisory leaders.
- [x] Add three concise Head of Advisory bullets.
- [x] Include one caveat that must not be missed.
- [x] Add the README question on how `wau = 0` should be handled before leadership sharing.
- [x] Explain that `ANY` counts unique people active on either measured tool.
- [x] State what would be done next with more time.
- [x] Add 3-5 production and dashboard safeguards.
- [x] Commit generated output and final documentation.
- [ ] Do not push.

## Stage 8: Final Repository and ZIP Packaging

- [x] Verify no `data/` files are tracked or included in the deliverable.
- [x] Verify the output CSV has the required schema and values.
- [x] Verify README run instructions work.
- [x] Verify Git history and `.gitignore` are present.
- [x] Create a single ZIP containing code, README, output, and `.git/` but not `data/`.
- [x] Keep the ZIP outside Git.
- [x] Review the final repository status.
- [x] Ask for explicit permission before any push or remote update.
