# Agent Guide: health-cat-dashboard

## Repository purpose

This repository stores Databricks notebooks for local development and version control.

Primary workflow:
1. Pull notebook(s) from Databricks Workspace into this repo.
2. Edit notebooks locally (`.ipynb`).
3. Push notebook(s) back to Databricks Workspace.

## Environment context

- Workspace host: `https://dbc-e150c196-2b0e.cloud.databricks.com`
- Databricks profile: `kk-dev`
- Default notebook path (remote): `/Users/kunal.rox@gmail.com/Diabetic patient exploration`
- Default notebook file (local): `diabetic-patient-exploration.ipynb`

## Key files

- `pull_notebooks.sh`: exports notebook from Databricks to local file.
- `push_notebooks.sh`: imports local notebook to Databricks (`--overwrite`).
- `README.md`: human-facing usage and key commands.

## Notebook authoring pattern

When creating or updating analysis/ETL notebook sections, use this execution order:

1. Explore data
2. Process/clean data
3. Verify processed output
4. Write to storage (Unity Catalog/Delta tables)
5. Read back and verify persisted data

This pattern is required for new medallion-layer notebook logic in this repository.

## Agent command checklist

### Verify CLI and auth

```bash
databricks --version
databricks auth profiles
databricks current-user me --profile kk-dev
```

### List workspace paths

```bash
databricks workspace list / --profile kk-dev
databricks workspace list /Users --profile kk-dev
databricks workspace list /Users/kunal.rox@gmail.com --profile kk-dev
```

### Pull/push via helper scripts

```bash
./pull_notebooks.sh
./push_notebooks.sh
```

Custom arguments:

```bash
./pull_notebooks.sh "/Users/kunal.rox@gmail.com/Some Notebook" "some-notebook.ipynb"
./push_notebooks.sh "some-notebook.ipynb" "/Users/kunal.rox@gmail.com/Some Notebook"
```

Profile override:

```bash
DATABRICKS_PROFILE=kk-dev ./pull_notebooks.sh
DATABRICKS_PROFILE=kk-dev ./push_notebooks.sh
```

## Direct CLI equivalents

```bash
databricks workspace export "/Users/kunal.rox@gmail.com/Diabetic patient exploration" \
  --format JUPYTER \
  --file "diabetic-patient-exploration.ipynb" \
  --profile kk-dev

databricks workspace import "diabetic-patient-exploration.ipynb" "/Users/kunal.rox@gmail.com/Diabetic patient exploration" \
  --format JUPYTER \
  --overwrite \
  --profile kk-dev
```

## Troubleshooting

- If auth shows invalid, rerun:

```bash
databricks auth login --host https://dbc-e150c196-2b0e.cloud.databricks.com --profile kk-dev
```

- If commands return `Forbidden`, verify VPN/network policy and workspace access.
- Always pass `--profile kk-dev` for explicit, repeatable commands.
