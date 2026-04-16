CREATE OR REPLACE TABLE workspace.gold.readmissions_summary AS
SELECT
  COUNT(DISTINCT patient_id) AS total_patients,
  COUNT(*) AS total_encounters,
  AVG(CAST(time_in_hospital AS DOUBLE)) AS avg_length_of_stay,
  AVG(CASE WHEN readmitted = '<30' THEN 1.0 ELSE 0.0 END) AS readmission_rate_30d
FROM workspace.silver.patient_encounters;
