# Databricks Notebook Development Skill

Use this guide when iterating on notebooks locally and executing them in Databricks.

## 1) Uploading notebooks with a DAB

- Use `databricks bundle deploy -t dev --profile kk-dev` from repo root.
- Keep `sync.paths` in `databricks.yml` scoped to the notebook file(s) you want to publish.
- If notebook rendering fails in Databricks, first validate local JSON shape and footer metadata (see section below), then redeploy.

### Critical lesson learned (do not skip)

- In prior runs for this project, when notebook cell outputs were left in the `.ipynb`, Databricks treated the uploaded object as a file (or failed to open it as a notebook).
- After clearing all cell outputs and execution counts, then redeploying, Databricks registered the upload as a notebook again.
- Treat output stripping as a required pre-deploy step for notebook-format preservation in this repo.

### Notebook format-preservation notes

- Remove all code-cell outputs before deploy:
  - set each code cell `outputs: []`
  - set each code cell `execution_count: null`
- Keep notebook JSON valid (`nbformat: 4`, `nbformat_minor: 0`).
- Keep Databricks notebook footer metadata in this shape:

```json
"metadata": {
  "application/vnd.databricks.v1+notebook": {
    "computePreferences": null,
    "dashboards": [],
    "environmentMetadata": null,
    "inputWidgetPreferences": null,
    "language": "python",
    "notebookMetadata": {
      "pythonIndentUnit": 4
    },
    "notebookName": "Diabetic patient exploration",
    "widgets": {}
  },
  "language_info": {
    "name": "python"
  }
},
"nbformat": 4,
"nbformat_minor": 0
```

## 2) Running an uploaded notebook using Jobs

- Validate and deploy first:
  - `databricks bundle validate -t dev --profile kk-dev`
  - `databricks bundle deploy -t dev --profile kk-dev`
- Run the bundle job resource:
  - `databricks bundle run diabetic_serverless_job -t dev --profile kk-dev`
- Success criteria:
  - CLI reaches `TERMINATED SUCCESS`
  - Run URL is printed in terminal
- If run fails with notebook path errors:
  - confirm the task path matches the actual workspace notebook object path
  - for this repo, notebook task should use:
    - `${workspace.file_path}/notebooks/diabetic-patient-exploration`
    - `source: WORKSPACE`

## 3) Inspecting output of a notebook run

- `bundle run` prints the `dbutils.notebook.exit(...)` payload directly when present.
- To fetch output explicitly from Jobs API:
  1. Get parent run ID (from Run URL, `.../run/<PARENT_RUN_ID>`).
  2. Resolve task run ID:
    - `databricks jobs get-run <PARENT_RUN_ID> --profile kk-dev -o json`
    - read `tasks[0].run_id`
  3. Fetch task output:
    - `databricks jobs get-run-output <TASK_RUN_ID> --profile kk-dev -o json`
- Expected payload shape in this project:
  - `notebook_output.result` is a JSON string with keys:
    - `ok`, `message`, `table`, `preview`, `previews`
- Quick parse example:
  - `python3 -c "import json,sys; d=json.load(sys.stdin); print(json.loads(d['notebook_output']['result'])['ok'])"`

### JSON schema details for `dbutils.notebook.exit(...)`

- The notebook should call `dbutils.notebook.exit(json.dumps(payload))` once at the end.
- `payload` should be a JSON object with this minimal shape:

```json
{
  "ok": true,
  "message": "Notebook finished successfully.",
  "table": "workspace.silver.patient_encounters",
  "preview": {
    "source_cell": "cell_11",
    "columns": ["col1", "col2"],
    "rows": [{"col1": "v1", "col2": "v2"}]
  },
  "previews": {
    "cell_5": {
      "type": "dataframe",
      "columns": ["..."],
      "rows": [{"...": "..."}],
      "truncated": true
    },
    "cell_8": {
      "type": "repr",
      "value": "short repr output..."
    },
    "cell_9": {
      "type": "error",
      "message": "error text..."
    }
  }
}
```

- Field notes:
  - `ok`: boolean success flag for agent decision-making.
  - `message`: short run summary.
  - `table`: main output table (or `null` if none).
  - `preview`: optional top-level quick preview (typically first useful dataframe preview).
  - `previews`: per-cell collected previews keyed by `cell_<execution_count>`.
- Keep payload small to stay under Jobs API output limits:
  - cap dataframe previews (for example 5 rows, limited columns).
  - truncate long strings/repr output.
  - if payload gets too large, keep only the most recent N previews.

### Validation checklist (run output contract)

- `notebook_output.result` exists and is valid JSON.
- `ok` is present and boolean.
- `message` is present and non-empty.
- `table` is present (`null` allowed for exploratory runs).
- `previews` is present and is an object (empty object is acceptable).
- If `preview` is not `null`, it includes `columns` and `rows`.
- Dataframe previews are capped (small row/column count) and may set `truncated: true`.
- On failed runs, set `ok: false` and include a clear failure `message`.

## Quick demo command sequence (copy/paste)

```bash
# 1) Deploy and run
databricks bundle validate -t dev --profile kk-dev
databricks bundle deploy -t dev --profile kk-dev
databricks bundle run diabetic_serverless_job -t dev --profile kk-dev

# 2) Replace with parent run id from Run URL printed above
PARENT_RUN_ID="<paste_run_id>"

# 3) Resolve task run id
TASK_RUN_ID=$(databricks jobs get-run "$PARENT_RUN_ID" --profile kk-dev -o json \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['tasks'][0]['run_id'])")
echo "TASK_RUN_ID=$TASK_RUN_ID"

# 4) Fetch output JSON
databricks jobs get-run-output "$TASK_RUN_ID" --profile kk-dev -o json > run_output.json

# 5) Parse notebook exit payload
python3 notebooks/scripts/parse_notebook_output.py run_output.json
# (optional full payload)
python3 notebooks/scripts/parse_notebook_output.py run_output.json --pretty
```

