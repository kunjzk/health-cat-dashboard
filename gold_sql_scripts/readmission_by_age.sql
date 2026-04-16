CREATE OR REPLACE TABLE workspace.gold.readmission_by_age AS
SELECT
  age AS age_bucket,
  COUNT(*) AS total_cases,
  SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmitted_cases,
  CAST(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE) AS readmission_rate
FROM workspace.silver.patient_encounters
WHERE age IS NOT NULL
GROUP BY age
ORDER BY age;
