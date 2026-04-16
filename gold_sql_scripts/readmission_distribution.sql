CREATE OR REPLACE TABLE workspace.gold.readmission_distribution AS
WITH counts AS (
  SELECT
    readmitted,
    COUNT(*) AS total_cases
  FROM workspace.silver.patient_encounters
  WHERE readmitted IN ('NO', '<30', '>30')
  GROUP BY readmitted
),
totals AS (
  SELECT SUM(total_cases) AS grand_total
  FROM counts
)
SELECT
  c.readmitted,
  c.total_cases,
  CAST(c.total_cases AS DOUBLE) / CAST(t.grand_total AS DOUBLE) AS percentage
FROM counts c
CROSS JOIN totals t
ORDER BY c.readmitted;
