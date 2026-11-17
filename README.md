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
