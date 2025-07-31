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