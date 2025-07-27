#!/bin/bash
export SUPERSET_DATABASES="""[{"database_name": "Trino_Iceberg",
"sqlalchemy_uri": "${SUPERSET_DATABASE_TRINO_CONN}"}]"""
