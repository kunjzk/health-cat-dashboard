CREATE OR REPLACE TABLE workspace.gold.readmission_by_los AS
WITH bucketed AS (
  SELECT
    CASE
      WHEN time_in_hospital BETWEEN 1 AND 3 THEN '1-3 days'
      WHEN time_in_hospital BETWEEN 4 AND 7 THEN '4-7 days'
      ELSE '8+ days'
    END AS los_bucket,
    readmitted
  FROM workspace.silver.patient_encounters
  WHERE time_in_hospital IS NOT NULL
)
SELECT
  los_bucket,
  COUNT(*) AS total_cases,
  SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS readmitted_cases,
  CAST(SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE) AS readmission_rate
FROM bucketed
GROUP BY los_bucket
ORDER BY CASE los_bucket
  WHEN '1-3 days' THEN 1
  WHEN '4-7 days' THEN 2
  ELSE 3
END;
