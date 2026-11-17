# Implementation Plan

## Working Agreements

- [ ] Work proceeds one stage at a time and only after explicit authorization.
- [ ] Commits stay on `main` and remain local until explicit authorization to push.
- [ ] Do not push anything without permission.
- [ ] Do not commit `data/` or generated ZIP files.
- [ ] Commit the requirement spec or implementation README only when appropriate for the stage.
- [ ] Keep assumptions visible and test the most likely edge cases.
- [ ] Use the reporting configuration as the source of truth.

## Data and Rule Decisions

- [ ] Normalize employee IDs by trimming surrounding whitespace and converting to uppercase.
- [ ] Select each person's latest HR record by `Effective_Date`, then use the latest record for all reporting weeks.
- [ ] Restrict output to employees whose latest HR record has `Division = ADV`.
- [ ] Exclude IDs absent from the latest HR scope and IDs belonging to other divisions.
- [ ] Parse Quill timestamps as UTC and assign events to Sunday-to-Saturday reporting weeks.
- [ ] For Quill WAU, count distinct people with at least one `generation` event at the configured threshold.
- [ ] For Quill WPU, count distinct Advisory people meeting the configured WPU threshold for generation events.
- [ ] Do not count Quill duplicate event rows as additional people.
- [ ] Parse Atlas workbook `Usage` sheets beginning after the title and blank rows.
- [ ] Normalize Atlas `User ID`, `Queries Run`, and `Active Days` values.
- [ ] Map Atlas `Week Ending` to the reporting week start, a Sunday.
- [ ] Select the latest Atlas delivery for each reporting week when redeliveries overlap.
- [ ] Use the configured Atlas WAU and WPU thresholds.
- [ ] Mark a tool unmeasured and leave `wau`, `wpu`, and `wpu_rate` blank when it has no data for a week.
- [ ] Keep measured zero-count tools distinct from unmeasured tools; measured zero results remain `0`.
- [ ] Where `wau = 0`, write `Infinity` for `wpu_rate`, and document a README question about the policy before leadership sharing.
- [ ] Implement `ANY` by unioning distinct active people across measured tools.
- [ ] Implement `ANY` power users by unioning distinct people meeting a power threshold on at least one measured tool.
- [ ] Deduplicate overlap across Quill and Atlas; a person is counted once in `ANY`.
- [ ] Set `ANY.measured = true` only when both tools are measured for the week.
- [ ] When `ANY` is not measured, leave `wau`, `wpu`, and `wpu_rate` blank.
- [ ] Preserve `ANY` as a supplemental portfolio metric and explain that it is a distinct-person-at-least-one-tool measure, not an overlap or usage-quality measure.
- [ ] Document any implementation rule that differs from the exercise or remains an unresolved policy decision.

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
- [ ] Do not push until explicitly authorized.

## Stage 2: Shared Identity and HR Scope

- [x] Implement CSV input loading for `hr_roster.csv`.
- [x] Implement ID normalization and effective-date parsing.
- [x] Select each normalized person's latest HR record.
- [x] Build the set of latest Advisory IDs.
- [x] Record data issue counts for duplicate IDs, missing IDs, and division changes.
- [x] Add focused tests for normalization and latest effective date.
- [x] Update the README with the implementation approach and discovered HR issues.
- [ ] Commit tested shared identity/HR scope code.
- [ ] Do not push until explicitly authorized.

## Stage 3: Quill Metrics

- [x] Implement Quill CSV loading and UTC timestamp parsing.
- [x] Filter events to the reporting window and `generation` event type.
- [x] Assign events to Sunday week starts.
- [x] Count distinct Advisory people for WAU and WPU.
- [x] Add focused tests for UTC boundaries, duplicate events, ID normalization, and thresholds.
- [x] Update the README with Quill handling and observed Quill data issues.
- [x] Commit tested Quill logic.
- [ ] Do not push until explicitly authorized.

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
- [ ] Do not push until explicitly authorized.

## Stage 5: Reporting Table and ANY

- [ ] Produce exactly one row per reporting Sunday for `quill`, `atlas`, and `ANY`.
- [ ] Preserve reporting columns in this order: `week_start, tool_id, wau, wpu, wpu_rate, measured`.
- [ ] Calculate `wpu_rate = wpu / wau` and round to 4 decimal places.
- [ ] Output `Infinity` when a measured row has `wau = 0` and `wpu = 0` until a policy is approved.
- [ ] Leave `wau`, `wpu`, and `wpu_rate` blank for unmeasured rows.
- [ ] Write `true` and `false` for CSV measured values.
- [ ] Union distinct active and power users for `ANY` only from measured tools.
- [ ] Mark `ANY` measured only when both tools are measured.
- [ ] Add focused tests for no-data, measured-zero, redelivery, and `ANY` overlap behavior.
- [ ] Update the README with output format and result policy questions.
- [ ] Commit tested rollup generation.
- [ ] Do not push.

## Stage 6: Tests and Data Issue Summary

- [ ] Run the complete test suite.
- [ ] Validate generated row counts and tool ordering.
- [ ] Compare representative totals against independent calculations.
- [ ] Record approximate counts for duplicate, whitespace/case, unknown-HR, non-ADV, and outside-window records.
- [ ] Disclose confirmed Atlas redelivery behavior.
- [ ] Update the README with confirmed data issues and affected record counts.
- [ ] Commit tests and README data findings.
- [ ] Do not push.

## Stage 7: Leadership Summary and Production Guidance

- [ ] Generate `out/weekly_tool_metrics.csv`.
- [ ] Summarize only confirmed headline numbers for Advisory leaders.
- [ ] Add three concise Head of Advisory bullets.
- [ ] Include one caveat that must not be missed.
- [ ] Add the README question on how `wau = 0` should be handled before leadership sharing.
- [ ] Explain that `ANY` is supplemental and deduplicates overlap.
- [ ] State what would be done next with more time.
- [ ] Add 3-5 production and dashboard safeguards.
- [ ] Commit generated output and final documentation.
- [ ] Do not push.

## Stage 8: Final Repository and ZIP Packaging

- [ ] Verify no `data/` files are tracked or included in the deliverable.
- [ ] Verify the output CSV has the required schema and values.
- [ ] Verify README run instructions work from a clean environment.
- [ ] Verify Git history and `.gitignore` are present.
- [ ] Create a single ZIP containing code, README, output, and `.git/` but not `data/`.
- [ ] Keep the ZIP outside Git or exclude it only if the delivered ZIP is required outside the repository.
- [ ] Review the final repository status.
- [ ] Ask for explicit permission before any push or remote update.
