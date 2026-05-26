# Superset Customizations

## Must-Have

### Config Overrides

File target:

```text
superset/superset_config.py
```

Planned content:

- PostgreSQL SQLAlchemy URI from environment variables
- Redis cache configuration
- Celery broker/result backend
- selected feature flags for dashboard filtering and embedding experiments
- optional branding title

### Dataset And Dashboard Import

File targets:

```text
superset/bootstrap/import-assets.sh
superset/assets/
```

Planned content:

- database connection definition
- datasets
- metrics
- dashboard export
- roles/users bootstrap script

### Jinja Virtual Dataset

Purpose: prove SQL/Jinja confidence.

Example idea:

```sql
select *
from production_events
where 1 = 1
{% if filter_values('plant_name') %}
  and plant_name in {{ filter_values('plant_name') | where_in }}
{% endif %}
```

For role-aware filtering, keep the demo explicit and documented. Avoid hiding
too much logic in magic.

## Custom Chart Plugin

Plugin name:

```text
superset-plugin-chart-oee-gauge
```

Chart behavior:

- renders OEE as the primary value
- shows availability, performance, and quality as three compact bars
- supports thresholds:
  - critical
  - warning
  - healthy
- has Explore controls for threshold values and unit display

Why it matters:

- proves React/TypeScript work inside the Superset visualization system
- demonstrates more than no-code dashboard assembly
- maps directly to industrial KPI use cases

## Optional Custom Filter

Add a "Plant Scope" filter preset:

- all plants for admin
- fixed plant for plant manager
- optional line-level narrowing

This can be implemented as role/data configuration first. Only build custom UI
if the reviewer explicitly values frontend customization over delivery speed.

## Smoke Checks

- Superset web starts.
- Worker connects to Redis.
- PostgreSQL demo data exists.
- Dashboard imports without manual clicks.
- Native filters update charts.
- Custom OEE chart renders.
- SQL Lab Jinja query returns scoped results.
