CREATE OR REPLACE TABLE workspace.gold.readmission_by_admission_type AS
SELECT
  COALESCE(m.description, 'Unknown') AS admission_type,
  COUNT(*) AS total_cases,
  SUM(CASE WHEN f.readmitted = '<30' THEN 1 ELSE 0 END) AS readmitted_cases,
  CAST(SUM(CASE WHEN f.readmitted = '<30' THEN 1 ELSE 0 END) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE) AS readmission_rate
FROM workspace.silver.patient_encounters f
LEFT JOIN workspace.silver.admission_type_mapping m
  ON f.admission_type_id = m.admission_type_id
GROUP BY COALESCE(m.description, 'Unknown')
ORDER BY total_cases DESC, admission_type;
