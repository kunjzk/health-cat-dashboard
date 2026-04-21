#!/usr/bin/env bash
set -euo pipefail

# Pull a notebook from Databricks workspace to local repo as .ipynb.
PROFILE="${DATABRICKS_PROFILE:-kk-dev}"
# Default matches Asset Bundle deploy: root_path + notebooks/ (see databricks.yml).
WORKSPACE_PATH="${1:-/Users/kunal.rox@gmail.com/notebooks/diabetic-patient-exploration.ipynb}"
OUTPUT_FILE="${2:-notebooks/diabetic-patient-exploration.ipynb}"

if ! command -v databricks >/dev/null 2>&1; then
  echo "Error: databricks CLI not found on PATH."
  exit 1
fi

echo "Pulling notebook from Databricks..."
echo "  Profile: ${PROFILE}"
echo "  Workspace path: ${WORKSPACE_PATH}"
echo "  Local output: ${OUTPUT_FILE}"

databricks workspace export "${WORKSPACE_PATH}" \
  --format JUPYTER \
  --file "${OUTPUT_FILE}" \
  --profile "${PROFILE}"

echo "Done: ${OUTPUT_FILE}"
