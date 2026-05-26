#!/usr/bin/env sh
set -eu

superset db upgrade

superset fab create-admin \
  --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
  --firstname "${SUPERSET_ADMIN_FIRSTNAME:-Demo}" \
  --lastname "${SUPERSET_ADMIN_LASTNAME:-Admin}" \
  --email "${SUPERSET_ADMIN_EMAIL:-admin@example.com}" \
  --password "${SUPERSET_ADMIN_PASSWORD:-admin}" || true

superset init

if superset import-datasources --path /app/assets/database.yaml 2>/tmp/import-datasources.log; then
  echo "Imported datasource assets."
else
  echo "Datasource import skipped; create the industrial database connection manually if needed."
  cat /tmp/import-datasources.log || true
fi

if [ -f /app/assets/README.md ]; then
  echo "Superset assets folder mounted at /app/assets."
fi
