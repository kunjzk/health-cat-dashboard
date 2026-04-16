CREATE OR REPLACE TABLE workspace.gold.readmission_by_diagnosis AS
SELECT
  diag_1,
  COUNT(*) AS total_cases,
  SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmitted_cases,
  CAST(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE) AS readmission_rate
FROM workspace.silver.patient_encounters
WHERE diag_1 IS NOT NULL
GROUP BY diag_1
ORDER BY total_cases DESC, diag_1;
