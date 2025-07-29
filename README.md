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