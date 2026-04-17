# health-cat-dashboard

## Introduction

- Goal: build Databricks dashboards to explore the UCI Diabetes 130-US hospitals dataset: [UCI dataset page](https://archive.ics.uci.edu/dataset/296/diabetes+130+us+hospitals+for+years+1999+2008).
- Code explanation: this repo contains Python and SQL scripts that use the Databricks CLI to transform, analyze, and prepare data products on Databricks for dashboarding.

## Installation and setup

### 1) Install Databricks CLI

Install and verify:

```bash
databricks --version
```

### 2) Authenticate against your Databricks workspace

```bash
databricks auth login --host https://dbc-e150c196-2b0e.cloud.databricks.com --profile kk-dev
databricks auth profiles
```

### 3) Python virtual environment setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## What else?

For reviewers, two short additions are usually helpful:

- **Repository layout:** notebooks and helpers are under `notebooks/`; Gold SQL definitions are under `gold_sql_scripts/`.
- **Execution order:** Bronze -> Silver -> Gold, with notebook pattern: explore -> process -> verify -> write -> verify.
