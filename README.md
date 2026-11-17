# ai-usage-test

## Run configuration check

```bash
python3 rollup.py
```

The command reads `data/reporting_config.json` and prints the configured Sunday week starts.

## Run tests

```bash
python3 -m unittest -v test_rollup.py
```

## Stage 2: HR scope

The script normalizes employee IDs by trimming whitespace and converting to uppercase. It reads all HR history records, selects the latest `Effective_Date` per normalized ID, and retains only latest records with `Division = ADV`.

The supplied HR file contains 2,445 rows. Its latest records contain 1,507 unique Advisory employees.

## Stage 3: Quill metrics

Quill timestamps are parsed as UTC and assigned to the Sunday that starts their reporting week. Only `generation` events count; `open` and `rating` events are excluded. Activity counts distinct normalized Advisory employees, and exact duplicate rows do not increase counts.

The supplied Quill file contains 94,558 rows. It contains 1,397 exact duplicate rows, 8,455 rows with ID whitespace/case differences, and 1,737 generation rows outside the reporting window. The implementation also separates unknown-HR and non-Advisory events from the Advisory result.
