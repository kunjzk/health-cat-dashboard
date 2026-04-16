# AGENTS

## Notebook workflow standard

For notebook development in this repository, agents should follow this sequence:

1. Explore data
2. Process/clean data
3. Verify processed output
4. Write to storage (Unity Catalog/Delta)
5. Read back and verify persisted output

Apply this pattern to new medallion-layer sections (Bronze -> Silver -> Gold).

## CRITICAL: Databricks notebook format safety

- VERY IMPORTANT: never push `.ipynb` directly with `--format JUPYTER` for this repo workflow.
- Always push notebooks as Databricks SOURCE notebook objects (`# Databricks notebook source` + `# COMMAND ----------` cells) so workspace type stays `NOTEBOOK` (not `FILE`).
- After every notebook push, verify object type with:
  - `databricks workspace list /Users/kunal.rox@gmail.com --profile kk-dev`
- If a `.ipynb` FILE appears in workspace, immediately restore/overwrite the canonical notebook path as a `NOTEBOOK` object.
