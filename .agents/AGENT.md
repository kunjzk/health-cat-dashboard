# Agent Guide: health-cat-dashboard

## Repository purpose

This repository stores Databricks notebooks for local development and version control.

Primary workflow:
1. Pull notebook(s) from Databricks Workspace into this repo (when needed).
2. Edit notebooks locally (`.ipynb`).
3. Deploy to the workspace with `databricks bundle deploy` (see below).

## Environment context

- Workspace host: `https://dbc-e150c196-2b0e.cloud.databricks.com`
- Databricks profile: `kk-dev`
- Bundle deploy root (remote): `/Users/kunal.rox@gmail.com/.bundle/health-cat-dashboard/dev`
- Default notebook (single local source): `notebooks/diabetic-patient-exploration.ipynb`
- Expected notebook path in workspace after deploy: `/Users/kunal.rox@gmail.com/notebooks/diabetic-patient-exploration`

## Key files

- `notebooks/pull_notebooks.sh`: exports a notebook from an arbitrary workspace path to local `.ipynb`.
- `databricks.yml`: Asset Bundle config; deploy uses `sync.paths` so only `notebooks/diabetic-patient-exploration.ipynb` is uploaded.
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

### Deploy notebook (Asset Bundle)

From the repository root:

```bash
databricks bundle validate --profile kk-dev
databricks bundle deploy -t dev --profile kk-dev
```

This uploads only `notebooks/diabetic-patient-exploration.ipynb` to `/Users/kunal.rox@gmail.com/notebooks/` in the workspace.

### Verify notebook exists at expected workspace path

Run this right after deploy:

```bash
databricks workspace list "/Users/kunal.rox@gmail.com/notebooks" --profile kk-dev
```

Expected row:

- `NOTEBOOK ... /Users/kunal.rox@gmail.com/notebooks/diabetic-patient-exploration`

### Pull from an arbitrary workspace path (optional)

```bash
./notebooks/pull_notebooks.sh
```

Custom arguments:

```bash
./notebooks/pull_notebooks.sh "/Users/kunal.rox@gmail.com/notebooks/diabetic-patient-exploration.ipynb" "notebooks/diabetic-patient-exploration.ipynb"
```

Profile override:

```bash
DATABRICKS_PROFILE=kk-dev ./notebooks/pull_notebooks.sh
```

## Direct CLI equivalent (pull only)

```bash
databricks workspace export "/Users/kunal.rox@gmail.com/notebooks/diabetic-patient-exploration.ipynb" \
  --format JUPYTER \
  --file "notebooks/diabetic-patient-exploration.ipynb" \
  --profile kk-dev
```

## Troubleshooting

- If auth shows invalid, rerun:

```bash
databricks auth login --host https://dbc-e150c196-2b0e.cloud.databricks.com --profile kk-dev
```

- If commands return `Forbidden`, verify VPN/network policy and workspace access.
- Always pass `--profile kk-dev` for explicit, repeatable commands.
