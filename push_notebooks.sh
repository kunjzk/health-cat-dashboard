#!/usr/bin/env bash
set -euo pipefail

# Push a local notebook to Databricks as a NOTEBOOK object (never as FILE).
PROFILE="${DATABRICKS_PROFILE:-kk-dev}"
LOCAL_FILE="${1:-diabetic-patient-exploration.ipynb}"
WORKSPACE_PATH="${2:-/Users/kunal.rox@gmail.com/Diabetic patient exploration}"

if ! command -v databricks >/dev/null 2>&1; then
  echo "Error: databricks CLI not found on PATH."
  exit 1
fi

if [[ ! -f "${LOCAL_FILE}" ]]; then
  echo "Error: local file not found: ${LOCAL_FILE}"
  exit 1
fi

echo "Pushing notebook to Databricks..."
echo "  Profile: ${PROFILE}"
echo "  Local file: ${LOCAL_FILE}"
echo "  Workspace path: ${WORKSPACE_PATH}"

IMPORT_FILE="${LOCAL_FILE}"
IMPORT_FORMAT="SOURCE"
IMPORT_LANGUAGE="PYTHON"
TMP_SOURCE_FILE=""

# Databricks CLI can ingest .ipynb as a FILE object in some flows.
# To force NOTEBOOK object creation, convert .ipynb -> Databricks SOURCE .py.
if [[ "${LOCAL_FILE}" == *.ipynb ]]; then
  TMP_SOURCE_FILE="$(mktemp "${TMPDIR:-/tmp}/db-notebook-XXXXXX.py")"
  python3 - <<'PY' "${LOCAL_FILE}" "${TMP_SOURCE_FILE}"
import json
import sys
from pathlib import Path

src_path = Path(sys.argv[1])
dst_path = Path(sys.argv[2])
nb = json.loads(src_path.read_text(encoding="utf-8"))

parts = ["# Databricks notebook source\n"]
for cell in nb.get("cells", []):
    if cell.get("cell_type") != "code":
        continue
    source = "".join(cell.get("source", []))
    parts.append(source.rstrip() + "\n")
    parts.append("\n# COMMAND ----------\n\n")

dst_path.write_text("".join(parts), encoding="utf-8")
PY
  IMPORT_FILE="${TMP_SOURCE_FILE}"
fi

trap '[[ -n "${TMP_SOURCE_FILE}" && -f "${TMP_SOURCE_FILE}" ]] && rm -f "${TMP_SOURCE_FILE}"' EXIT

databricks workspace import "${WORKSPACE_PATH}" \
  --file "${IMPORT_FILE}" \
  --format "${IMPORT_FORMAT}" \
  --language "${IMPORT_LANGUAGE}" \
  --overwrite \
  --profile "${PROFILE}"

echo "Done: ${WORKSPACE_PATH}"
