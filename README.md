# health-cat-dashboard

Databricks notebook workflow for local development in this repo and sync to/from Databricks Workspace.

## Prerequisites

- Databricks CLI installed (`databricks --version`)
- Authenticated profile (`kk-dev`)
- Workspace host: `https://dbc-e150c196-2b0e.cloud.databricks.com`

## Current Notebook

- Databricks path: `/Users/kunal.rox@gmail.com/Diabetic patient exploration`
- Local file: `diabetic-patient-exploration.ipynb`

## Key Commands

### Authentication and verification

```bash
databricks auth profiles
databricks current-user me --profile kk-dev
databricks workspace list / --profile kk-dev
```

### Pull notebook from Databricks to local repo

```bash
./pull_notebooks.sh
```

Custom pull:

```bash
./pull_notebooks.sh "/Users/kunal.rox@gmail.com/Some Notebook" "some-notebook.ipynb"
```

### Push local notebook back to Databricks

```bash
./push_notebooks.sh
```

Custom push:

```bash
./push_notebooks.sh "some-notebook.ipynb" "/Users/kunal.rox@gmail.com/Some Notebook"
```

### Override profile per command

```bash
DATABRICKS_PROFILE=kk-dev ./pull_notebooks.sh
DATABRICKS_PROFILE=kk-dev ./push_notebooks.sh
```

## Notes

- Scripts use `--format JUPYTER` and `--overwrite` on push.
- If a command returns `Forbidden`, re-check VPN/network policy and run login again:

```bash
databricks auth login --host https://dbc-e150c196-2b0e.cloud.databricks.com --profile kk-dev
```

## AI-agent development workflow

This repo includes helpers for running code against Databricks while keeping notebook/code local.

### 1) Create local environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 2) Set defaults

```bash
export DATABRICKS_PROFILE=kk-dev
export DATABRICKS_CLUSTER_ID="<your-all-purpose-cluster-id>"
```

### 3) Iterative remote execution (stateful context)

Use this for agent loops (run code -> inspect result -> rerun):

```bash
python scripts/agent_exec.py --command "print('hello from cluster')"
```

Or send a larger command block:

```bash
python scripts/agent_exec.py --command-file prompt_code.py
```

### 4) Reproducible notebook run as one-time job

```bash
python scripts/run_notebook_job.py \
  --notebook-path "/Users/kunal.rox@gmail.com/Diabetic patient exploration" \
  --cluster-id "<your-all-purpose-cluster-id>"
```

With notebook parameters:

```bash
python scripts/run_notebook_job.py \
  --notebook-path "/Users/kunal.rox@gmail.com/Diabetic patient exploration" \
  --cluster-id "<your-all-purpose-cluster-id>" \
  --param start_date=2026-01-01 \
  --param end_date=2026-01-31
```

### 5) Notebook sync + execution loop

```bash
./pull_notebooks.sh
# edit .ipynb locally with AI agent support
./push_notebooks.sh
python scripts/run_notebook_job.py --notebook-path "/Users/kunal.rox@gmail.com/Diabetic patient exploration" --cluster-id "<cluster-id>"
```
