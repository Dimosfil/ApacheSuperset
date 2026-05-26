# Architecture

## Components

```text
Browser
  |
  v
Apache Superset web
  |-- Superset metadata DB
  |-- PostgreSQL analytics DB
  |-- Redis cache/broker
  `-- Celery worker/beat
```

## Services

- `superset`: web UI, SQL Lab, dashboards, Explore, REST API.
- `superset-worker`: Celery worker for async queries, reports, thumbnails, and
  future scheduled work.
- `superset-beat`: optional scheduler for recurring jobs.
- `postgres`: stores demo analytics tables and can also be used as Superset
  metadata storage in a local demo.
- `redis`: cache and Celery broker.

## Customization Layers

1. Superset config
   - feature flags
   - cache settings
   - security manager hooks if needed
   - theme/branding entries where supported

2. Semantic layer
   - certified datasets
   - calculated columns
   - reusable metrics: OEE, downtime rate, plan completion

3. SQL/Jinja
   - dynamic plant filtering
   - role-aware queries
   - time grain presets

4. Frontend
   - custom chart plugin: OEE gauge with availability/performance/quality split
   - optional Explore control extension for threshold bands

5. Operations
   - Docker Compose
   - deterministic seed data
   - short smoke checklist

## Review Path

The reviewer should be able to inspect:

- `docker-compose.yml` for deployment understanding
- `superset/superset_config.py` for platform configuration
- `db/init.sql` or `db/seed.py` for data modeling
- dashboard export JSON/YAML for BI setup
- plugin source for React/TypeScript customization
