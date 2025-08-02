import sys
import boto3
from pyspark.context import SparkContext
from pyspark.sql.functions import concat_ws, col, max as spark_max
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job

# --- Initialize Spark and Glue Context ---
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# --- Resolve job parameters ---
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'DYNAMODB_TABLE', 'CATALOG_NAME'])
job_name = args['JOB_NAME']
dynamodb_table = args['DYNAMODB_TABLE']
catalog_name = args['CATALOG_NAME']

# Initialize Glue Job for commit handling
job = Job(glueContext)
job.init(job_name, args)

# --- Helper: Get last processed timestamp from DynamoDB ---
def get_last_ts():
    ddb = boto3.client("dynamodb")
    try:
        response = ddb.get_item(
            TableName=dynamodb_table,
            Key={"job_name": {"S": job_name}}
        )
        if "Item" in response and "last_processed_timestamp" in response["Item"]:
            ts = response["Item"]["last_processed_timestamp"]["S"]
            print(f"✅ Last processed timestamp: {ts}")
            return ts
        else:
            print(f"ℹ️ No previous timestamp found. Defaulting to start of time.")
            return "2000-01-01T00:00:00.000Z"
    except Exception as e:
        print(f"⚠️ Error accessing DynamoDB: {e}. Defaulting timestamp.")
        return "2000-01-01T00:00:00.000Z"

# --- Helper: Update timestamp in DynamoDB ---
def update_last_ts(ts):
    ddb = boto3.client("dynamodb")
    try:
        ddb.put_item(
            TableName=dynamodb_table,
            Item={
                "job_name": {"S": job_name},
                "last_processed_timestamp": {"S": str(ts)}
            }
        )
        print(f"✅ Updated last_processed_timestamp to: {ts}")
    except Exception as e:
        print(f"❌ Failed to update DynamoDB: {e}")
        raise e

# --- Main Logic ---
print("🚀 Job started.")
last_ts = get_last_ts()

# Source table (Iceberg Bronze)
source_table = f"{catalog_name}.bronze.comments"
print(f"📥 Reading from: {source_table}")
df = spark.table(source_table)

# Incremental filter
df_incremental = df.filter(col("_cdc_timestamp") > last_ts)
df_incremental.cache()
count = df_incremental.count()

if count == 0:
    print("✅ No new records to process. Exiting gracefully.")
    job.commit()
    sys.exit(0)

print(f"📊 Found {count} new records to process.")

# Clean & enrich
columns_to_drop = ["_olake_id", "_cdc_timestamp", "_olake_timestamp", "_op_type", "_db"]
df_cleaned = df_incremental.drop(*columns_to_drop)
df_final = df_cleaned.withColumn("name_text", concat_ws(" - ", col("name"), col("text")))

# Destination table (Iceberg Silver)
destination_table = f"{catalog_name}.silver.silver_comments"
print(f"📤 Writing to: {destination_table}")
df_final.writeTo(destination_table).append()

# Update watermark
max_ts_row = df_incremental.select(spark_max(col("_cdc_timestamp"))).first()
if max_ts_row and max_ts_row[0]:
    new_high_ts = max_ts_row[0].isoformat()
    update_last_ts(new_high_ts)
else:
    print("⚠️ Unable to find latest timestamp. Not updating watermark.")

df_incremental.unpersist()
job.commit()
print("🏁 Job completed successfully.")
