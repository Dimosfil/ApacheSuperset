# Reviewer Quickstart

## Start

```powershell
Copy-Item .env.example .env
docker compose up
```

Open:

```text
http://localhost:8088
```

Login:

```text
admin / admin
```

## Data

PostgreSQL initializes the schema from:

```text
db/init.sql
db/seed.sql
```

The main analytical view is:

```text
v_production_hourly
```

## Superset Setup

If datasource import succeeds during startup, use:

```text
Industrial BI PostgreSQL
```

If import is skipped by the Superset image version, add a database manually:

```text
postgresql+psycopg2://industrial:industrial@postgres:5432/industrial_bi
```

Then create a dataset from:

```text
v_production_hourly
```

## Dashboard

Build the Sprint 1 dashboard from:

```text
docs/dashboard-mvp.md
superset/assets/dataset-metrics.sql
```

## What Is Already Customized

- Superset config is project-specific.
- Redis cache and Celery are wired.
- PostgreSQL contains an industrial demo schema and 90 days of data.
- Dataset metrics and Jinja query examples are included.

## What Comes Next

Sprint 2 should add:

- role-aware Jinja dataset
- demo users and roles
- custom React/TypeScript OEE gauge chart plugin
- exported dashboard asset after the MVP is created once in Superset
