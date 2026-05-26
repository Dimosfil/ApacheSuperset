# Sprint 1: Runnable Industrial BI Foundation

## Sprint Goal

Create the first usable version of the Industrial BI Cockpit demo: a local
Apache Superset stack with PostgreSQL demo data and a coherent production
analytics dashboard plan. By the end of the sprint, we should have a foundation
that can be shown as real work, even before the custom chart plugin is added.

## Duration

Recommended scope: 2-3 focused work days.

## Outcome

Sprint 1 should produce:

- runnable Docker Compose stack
- PostgreSQL database with synthetic industrial data
- Superset config for Postgres, Redis, and Celery
- initial datasets and metrics plan
- first dashboard layout
- smoke checklist
- short README section for reviewers

## Not In Sprint 1

- custom React/TypeScript chart plugin
- embedded analytics/guest token flow
- full CI/CD pipeline
- production-grade authentication
- large visual polish pass

These are better as Sprint 2+ items after the base environment works.

## Backlog

### 1. Project Skeleton

Create implementation folders:

```text
db/
superset/
superset/bootstrap/
superset/assets/
docs/
```

Add placeholder files:

- `docker-compose.yml`
- `.env.example`
- `db/init.sql`
- `db/seed.py`
- `superset/superset_config.py`
- `superset/bootstrap/init-superset.sh`
- `docs/smoke-checklist.md`

Acceptance:

- file layout matches the planned runnable demo structure
- README explains how Sprint 1 files fit together

### 2. Docker Compose Baseline

Define services:

- `postgres`
- `redis`
- `superset`
- `superset-worker`
- optional `superset-beat`

Acceptance:

- stack starts locally
- Superset web container can reach Postgres and Redis
- worker container starts without connection errors

### 3. Synthetic Industrial Data

Create deterministic demo data for:

- plants
- production lines
- equipment
- shifts
- production events
- downtime events
- quality checks

Acceptance:

- data loads into PostgreSQL from a clean run
- at least 90 days of data are available
- generated data has visible variance and anomalies

### 4. Superset Bootstrap

Add bootstrap script for:

- metadata initialization
- admin user creation
- database connection registration if practical
- basic dataset/dashboard import hooks

Acceptance:

- fresh stack can be initialized with one documented command
- admin login details are demo-only and stored in `.env.example`

### 5. Dashboard MVP

Define or create dashboard "Industrial BI Cockpit" with:

- KPI row: OEE, output, downtime, scrap rate
- plan/fact trend
- downtime by reason
- line/shift heatmap
- incident table
- native filters: date, plant, line, shift

Acceptance:

- charts use the synthetic data model
- filters are mapped to relevant charts
- dashboard tells a clear production-performance story

### 6. Documentation And Smoke Check

Add reviewer-oriented docs:

- quick start
- what is customized
- what is intentionally left for Sprint 2
- smoke checklist

Acceptance:

- reviewer can understand the demo without asking for context
- smoke checklist covers service startup, data load, dashboard access, and basic
  filtering

## Definition Of Done

- `docker compose up` path is documented.
- No secrets are committed.
- Demo data is synthetic.
- Superset opens locally.
- PostgreSQL contains industrial demo tables.
- README gives a concise reviewer path.
- Sprint 2 scope is obvious from remaining work.

## Demo Script

1. Start stack.
2. Open Superset.
3. Show connected industrial database.
4. Open dashboard layout.
5. Use date and plant filters.
6. Open SQL Lab and show one metric query.
7. Explain next sprint: Jinja role scoping and custom OEE chart plugin.

## Sprint 2 Candidate Scope

- Jinja virtual dataset with scoped plant access.
- Demo users and roles.
- Custom React/TypeScript OEE gauge plugin.
- Dashboard export/import automation hardening.
- Screenshots or short GIF for portfolio/response.
