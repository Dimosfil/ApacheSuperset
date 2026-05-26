# Manual Dashboard Build

Use this when Superset asset import differs between versions. It keeps the demo
rebuildable even if the export format changes.

## 1. Add Database

Name:

```text
Industrial BI PostgreSQL
```

SQLAlchemy URI:

```text
postgresql+psycopg2://industrial:industrial@postgres:5432/industrial_bi
```

Enable:

- SQL Lab
- async queries if available
- CTAS/CVAS for demo exploration if desired

## 2. Create Datasets

Create dataset:

```text
v_production_hourly
```

Optional secondary datasets:

```text
downtime_events
quality_checks
maintenance_orders
```

## 3. Add Metrics

Use [superset/assets/dataset-metrics.sql](../superset/assets/dataset-metrics.sql)
as the source of metric expressions.

Suggested metric names:

- `Total Output`
- `Good Output`
- `Plan Completion`
- `Scrap Rate`
- `Availability`
- `Performance`
- `Quality`
- `OEE`

## 4. Build Dashboard

Create dashboard:

```text
Industrial BI Cockpit
```

Follow [dashboard-mvp.md](./dashboard-mvp.md) for:

- filters
- chart list
- metric expressions
- layout

## 5. Save And Export

After the dashboard is working:

1. Export the dashboard from Superset.
2. Place exported assets under `superset/assets/exported/`.
3. Update `superset/bootstrap/init-superset.sh` to import the exported bundle.
4. Keep this manual guide as the fallback.
