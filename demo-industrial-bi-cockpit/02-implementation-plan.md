# Implementation Plan

## Phase 1: Runnable Superset Stack

- Add Docker Compose with Superset, PostgreSQL, Redis, Celery worker, and Celery
  beat.
- Add local `.env.example` with non-secret demo defaults.
- Add Superset bootstrap script:
  - initialize metadata DB
  - create admin user
  - load examples or skip examples
  - import demo dashboard assets

Acceptance:

- `docker compose up` starts all services.
- Superset login works.
- Health checks are visible in logs.

## Phase 2: Industrial Data Model

- Create synthetic tables:
  - `plants`
  - `production_lines`
  - `equipment`
  - `shifts`
  - `production_events`
  - `downtime_events`
  - `quality_checks`
  - `maintenance_orders`
- Generate at least 90 days of data.
- Include realistic anomalies:
  - planned maintenance
  - unplanned downtime
  - low-quality batches
  - underperforming shifts

Acceptance:

- SQL Lab can query all tables.
- Dataset metrics calculate plausible values.

## Phase 3: Superset Dashboard

- Create dashboard "Industrial BI Cockpit".
- Add native filters:
  - date range
  - plant
  - line
  - shift
  - equipment class
- Add charts:
  - KPI row: OEE, output, downtime hours, scrap rate
  - plan/fact production trend
  - downtime by reason
  - line heatmap by shift
  - incident detail table with drill links

Acceptance:

- Filters affect all relevant charts.
- Dashboard tells a coherent operational story.

## Phase 4: Jinja And Role-Aware Demo

- Add a virtual dataset using Jinja.
- Demonstrate role-aware plant scope:
  - admin sees all plants
  - plant manager sees one plant
- Keep the logic explicit and documented.

Acceptance:

- Two demo users show different scoped results.

## Phase 5: Custom Visualization Plugin

- Add React/TypeScript chart plugin: `OEE Gauge`.
- Inputs:
  - OEE percentage
  - availability
  - performance
  - quality
  - threshold bands
- Output:
  - compact gauge
  - split breakdown
  - threshold color states

Acceptance:

- Plugin builds.
- Plugin appears in Superset chart type selector.
- Dashboard uses the plugin for the main OEE tile.

## Phase 6: Polish For Vacancy Response

- Add screenshots or short GIF.
- Add a concise technical README.
- Add "what I customized" section.
- Add a smoke-test checklist.
- Optional: add a GitHub Actions or GitLab CI sample for lint/build checks.
