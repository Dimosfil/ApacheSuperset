# Smoke Checklist

## Startup

- Copy `.env.example` to `.env`.
- Start the stack with `docker compose up`.
- Confirm `postgres`, `redis`, `superset`, and `superset-worker` are running.
- Open `http://localhost:8088`.
- Log in with `admin` / `admin`.

## Data

- Run the seed script after Postgres is healthy.
- Confirm these tables exist:
  - `plants`
  - `production_lines`
  - `equipment`
  - `shifts`
  - `production_events`
  - `downtime_events`
  - `quality_checks`
  - `maintenance_orders`
- Confirm `v_production_hourly` returns rows.

## Superset

- Confirm Superset uses the demo title "Industrial BI Cockpit".
- Add the PostgreSQL analytics database if it is not imported automatically.
- Create a dataset from `v_production_hourly`.
- Create or open the "Industrial BI Cockpit" dashboard.

## Dashboard

- Date filter changes charts.
- Plant filter changes charts.
- KPI values are non-empty.
- Downtime chart shows planned and unplanned events.
- SQL Lab can query `v_production_hourly`.
