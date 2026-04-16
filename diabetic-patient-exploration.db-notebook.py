# Databricks notebook source
import pandas as pd

# COMMAND ----------

# Read from Unity Catalog table and convert to pandas
patient_data_df = spark.table('workspace.default.diabetic_data').toPandas()

# COMMAND ----------

patient_data_df.head()

# COMMAND ----------

from pyspark.sql import functions as F

# Bronze source
bronze_df = spark.table("workspace.default.diabetic_data")

silver_df = (
    bronze_df
    .select(
        F.col("patient_nbr").cast("string").alias("patient_id"),
        F.col("encounter_id").cast("string").alias("encounter_id"),
        F.col("age").cast("string").alias("age"),
        F.col("time_in_hospital").alias("time_in_hospital"),
        F.col("readmitted").cast("string").alias("readmitted"),
        F.col("diag_1").cast("string").alias("diag_1"),
        F.col("admission_type_id").alias("admission_type_id"),
        F.col("discharge_disposition_id").alias("discharge_disposition_id"),
    )
    .withColumn("patient_id", F.trim("patient_id"))
    .withColumn("encounter_id", F.trim("encounter_id"))
    .withColumn("age", F.trim("age"))
    .withColumn("readmitted", F.upper(F.trim("readmitted")))
    .withColumn("diag_1", F.trim("diag_1"))
    .withColumn("patient_id", F.when((F.col("patient_id") == "") | (F.col("patient_id") == "?"), None).otherwise(F.col("patient_id")))
    .withColumn("encounter_id", F.when((F.col("encounter_id") == "") | (F.col("encounter_id") == "?"), None).otherwise(F.col("encounter_id")))
    .withColumn("age", F.when((F.col("age") == "") | (F.col("age") == "?"), None).otherwise(F.col("age")))
    .withColumn("diag_1", F.when((F.col("diag_1") == "") | (F.col("diag_1") == "?"), None).otherwise(F.col("diag_1")))
    .withColumn(
        "age",
        F.when(F.col("age").isNull(), None)
         .otherwise(F.regexp_replace(F.regexp_replace(F.col("age"), r"^\[", ""), r"\)$", ""))
    )
    .withColumn(
        "readmitted",
        F.when(F.col("readmitted").isin("NO", "<30", ">30"), F.col("readmitted")).otherwise(None)
    )
    .withColumn("time_in_hospital", F.col("time_in_hospital").cast("int"))
    .withColumn("admission_type_id", F.col("admission_type_id").cast("int"))
    .withColumn("discharge_disposition_id", F.col("discharge_disposition_id").cast("int"))
    .filter(F.col("patient_id").isNotNull())
    .filter(F.col("encounter_id").isNotNull())
    .filter(F.col("time_in_hospital").isNotNull() & (F.col("time_in_hospital") >= 0))
    .filter(F.col("admission_type_id").isNotNull() & (F.col("admission_type_id") > 0))
    .filter(F.col("discharge_disposition_id").isNotNull() & (F.col("discharge_disposition_id") > 0))
    .dropDuplicates(["encounter_id"])
)

# COMMAND ----------

silver_row_count = silver_df.count()
print(f"Silver dataset row count: {silver_row_count}")
print(f"Silver dataset column count: {len(silver_df.columns)}")

# COMMAND ----------

silver_df.head(10)

# COMMAND ----------

spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.silver")

(
    silver_df
    .write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("workspace.silver.patient_encounters")
)

spark.sql("SELECT COUNT(*) AS row_count FROM workspace.silver.patient_encounters").show()
spark.sql("SELECT DISTINCT readmitted FROM workspace.silver.patient_encounters ORDER BY readmitted").show()
spark.sql("SELECT DISTINCT age FROM workspace.silver.patient_encounters ORDER BY age LIMIT 20").show(truncate=False)
spark.sql("DESCRIBE TABLE workspace.silver.patient_encounters").show(truncate=False)

# COMMAND ----------

