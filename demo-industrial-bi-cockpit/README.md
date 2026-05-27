# Industrial BI Cockpit Demo

Purpose: a compact Apache Superset full-stack demo for an industrial holding.
It shows that we can customize Superset beyond ordinary dashboard assembly:
backend configuration, frontend/plugin work, SQL/Jinja, Docker deployment, and
operational thinking around Redis/Celery/PostgreSQL.

## Demo Story

The company has several plants and wants a self-service BI cockpit for
production efficiency:

- plan/fact production output
- OEE and downtime tracking
- shift-level performance
- equipment incidents
- role-aware filtering by plant
- one custom visualization that is not available out of the box

The demo should feel like a small real BI product, not a generic chart gallery.

## Main Deliverable

A reproducible local stack:

- Apache Superset
- PostgreSQL with rich synthetic industrial data
- Redis and Celery for async/cache background capabilities
- Superset config overrides
- seeded mock industrial objects, dashboard dataset, metrics, and filters
- optional custom React/TypeScript visualization plugin

## Quick Start

```powershell
Copy-Item .env.example .env
docker compose up
```

Then open:

```text
http://217.25.238.103:8088
```

The Docker service still binds on the host LAN address configured with
`SUPERSET_BIND_HOST`, for example `192.168.3.55`. For a local-only run, set
`SUPERSET_BIND_HOST=0.0.0.0` and `SUPERSET_PUBLIC_HOST=localhost` in `.env`,
then open `http://localhost:8088`.

Login:

```text
admin / admin
```

Localization:

- the Superset UI exposes English and Russian;
- default locale is controlled by `SUPERSET_DEFAULT_LOCALE` in `.env` (`en` or
  `ru`);
- project demo assets use `SUPERSET_PROJECT_LOCALE`; if it is not set, they use
  `SUPERSET_DEFAULT_LOCALE`;
- bootstrap keeps one stable project dashboard and rewrites its seeded titles,
  charts, and metrics for the selected project locale. User-created content is
  left exactly as users entered it.

The database seed is intentionally dense enough for screen recording: 5 plants,
15 production lines, 60 equipment assets, 180 days of hourly production events,
downtime, quality checks, and maintenance orders.

If the stack was already started before the mock data was expanded, rerun the
Python reseed path against local PostgreSQL:

```powershell
make seed-local
```

Or recreate the PostgreSQL volume and let Docker run `db/init.sql` and
`db/seed.sql` again:

```powershell
docker compose down -v
docker compose up
```

If the dashboard list is empty after startup, create the demo dashboard objects:

```powershell
docker compose exec superset python /app/bootstrap/create-demo-dashboard.py
```

Detailed reviewer flow: [docs/reviewer-quickstart.md](./docs/reviewer-quickstart.md).
Dashboard MVP: [docs/dashboard-mvp.md](./docs/dashboard-mvp.md).
Manual dashboard fallback:
[docs/manual-dashboard-build.md](./docs/manual-dashboard-build.md).
Sprint 1 acceptance:
[docs/acceptance-report.md](./docs/acceptance-report.md).

## Sprint Plan

- [Sprint 1: Runnable Industrial BI foundation](./sprint-01.md)

## Why This Fits The Vacancy

The vacancy asks for Apache Superset backend/frontend work, customization of
visualizations, charts and filters, SQL/Jinja, Docker, CI/CD, PostgreSQL, Redis,
and Celery. This demo touches each of those areas in a visible, reviewable way.

## Project Layout

Sprint 1 already contains the runnable-demo structure:

```text
docker-compose.yml
.env.example
Makefile
superset/
  superset_config.py
  bootstrap/
  assets/
db/
  init.sql
  seed.sql
  seed.py
docs/
  reviewer-quickstart.md
  dashboard-mvp.md
  manual-dashboard-build.md
  smoke-checklist.md
```

## Success Criteria

- Reviewer can run the stack locally with one command.
- Dashboard opens with meaningful data without manual setup.
- At least one part proves real Superset customization, not just dashboard use.
- README explains exactly what was customized and where.

## Current Status

Sprint 1 is file-complete. Runtime container startup is intentionally paused;
see [docs/acceptance-report.md](./docs/acceptance-report.md) for verified and
pending checks.
