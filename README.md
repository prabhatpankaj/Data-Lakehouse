# Data-Lakehouse

project-root/
├── docker-compose.yaml
├── .env
└── config/
    ├── trino/
    │    └── catalog/
    │         └── nessie.properties
    └── superset/
         └── superset_env.sh


* .env

AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1

NESSIE_URI=http://nessie:19120/api/v1
WAREHOUSE=s3a://your-iceberg-bucket/

# Superset-specific variables
SUPERSET_DATABASE_TRINO_CONN=trino://trino@trino:8080/nessie/main

MongoDB/MySQL
       ↓
    Airbyte (connectors, mapping, sync logic)
       ↓
S3 Iceberg tables (tracked via Nes­sie catalog)
       ↓
Trino / Dremio / Superset for query & dashboards