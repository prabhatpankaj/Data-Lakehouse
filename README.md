# Running Trino with the Iceberg Connector

```
S3 (Iceberg Tables)
  ├── Bronze: Raw data (from Airbyte/Olake)
  ├── Silver: Cleaned, flattened (via Glue or Trino + dbt)
  └── Gold: Aggregated, masked, etc (via dbt + Trino)

                   ↓
             Query Engine
                 Trino
                   ↓
               Superset
               Dashboards

dbt → runs SQL models → Trino → writes to Iceberg Gold layer → Superset users query same Gold layer

```

## to track the cdc and last run happned 
```
aws dynamodb create-table \
  --table-name glue_job_tracking \
  --attribute-definitions AttributeName=job_name,AttributeType=S \
  --key-schema AttributeName=job_name,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --tags Key=Environment,Value=prod

```

```

aws iam create-role \
  --role-name AWSGlueServiceRole-Default \
  --assume-role-policy-document file://glue-trust-policy.json


aws iam attach-role-policy \
  --role-name AWSGlueServiceRole-Default \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole

aws iam attach-role-policy \
  --role-name AWSGlueServiceRole-Default \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

aws iam put-role-policy \
  --role-name AWSGlueServiceRole-Default \
  --policy-name GlueS3DynamoCustomAccess \
  --policy-document file://glue-inline-policy.json


```

```
aws s3 cp scripts/silver_comments_transform_job.py s3://aws-glue-assets-277707128056-ap-south-1/scripts/silver_comments_transform_job.py

aws glue create-job \
  --name "glue_silver_comments_job" \
  --role "arn:aws:iam::277707128056:role/AWSGlueServiceRole-Default" \
  --command '{
    "Name": "glueetl",
    "ScriptLocation": "s3://aws-glue-assets-277707128056-ap-south-1/scripts/silver_comments_transform_job.py",
    "PythonVersion": "3"
  }' \
  --glue-version "5.0" \
  --number-of-workers 2 \
  --worker-type "G.1X" \
  --default-arguments '{
    "--job-language": "python",
    "--enable-glue-datacatalog": "true",
    "--spark.sql.defaultCatalog": "glue_catalog",
    "--spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    "--spark.sql.catalog.glue_catalog": "org.apache.iceberg.spark.SparkCatalog",
    "--spark.sql.catalog.glue_catalog.warehouse": "s3://olaketest123/",
    "--spark.sql.catalog.glue_catalog.catalog-impl": "org.apache.iceberg.aws.glue.GlueCatalog",
    "--spark.sql.catalog.glue_catalog.io-impl": "org.apache.iceberg.aws.s3.S3FileIO",
    "--JOB_NAME": "glue_silver_comments_job",
    "--DYNAMODB_TABLE": "glue_job_tracking",
    "--CATALOG_NAME": "glue_catalog"
  }'


```