# Pending Tasks

Use this file for active project-wide plans and multi-step work.

Keep entries concise and task-relevant. Do not store full diffs, large logs,
generated outputs, secrets, credentials, or private production data.

## Status Markers

- `[ ]` not started
- `[~]` in progress
- `[x]` done
- `[!]` blocked or needs attention

## Tasks

### Fix Superset downtime chart viz type 2026.05.27

Goal: fix the dashboard data error caused by unregistered `dist_bar` chart type.

Planned changes:

- [x] Replace legacy `dist_bar` seeded chart metadata with a registered Superset chart type.
- [x] Re-run the Superset dashboard bootstrap against the running stack.
- [x] Verify the chart metadata and Superset health/API response.

### Instruction kit update 2026.05.27.1

Goal: apply the GI config-service/task-manager discovery migration.

Planned changes:

- [x] Update local instructions for config-service aliases and task-manager
      service discovery.
- [x] Add project task-manager config without runtime URLs.
- [x] Record the applied instruction-kit migration.
- [x] Verify update status and git state.

### Superset RU/EN localization

Goal: add Russian and English localization support to the local Superset demo.

Planned changes:

- [x] Enable Superset locale settings for English and Russian.
- [x] Add localized dashboard/chart metadata for the seeded demo objects.
- [x] Document the default locale setting and how to switch it.
- [x] Run syntax/config checks.

Verification:

- [x] `python -m py_compile superset\superset_config.py superset\bootstrap\create-demo-dashboard.py`
- [x] `docker compose config`
- [x] Ran dashboard bootstrap in the running Superset container.
- [x] Restarted Superset services and verified `http://127.0.0.1:8088/health`.
- [x] Reworked seeded project localization to keep one stable dashboard slug
      and sync project-created chart/dashboard names to the selected locale.
- [x] Verified current metadata has one project dashboard:
      `Производственный BI-кокпит` at slug `industrial-bi-cockpit`.
- [x] Verified current Demo bootstrap charts are Russian-localized.
- [x] Added image-build generation for Superset frontend `messages.json`
      language packs from bundled `.po` files.
- [x] Rebuilt `industrial-bi-superset:local` and verified the Russian pack
      contains UI strings such as `Dashboards`, `Charts`, `Settings`, and
      `Bulk select`.

### Demo mock data enrichment

Goal: enrich the Industrial BI Cockpit demo with enough mock entities and fact
rows for video recording.

Planned changes:

- [x] Expand seeded industrial dimensions and facts.
- [x] Keep SQL init data and optional Python reseed path aligned.
- [x] Document how to reload data in an existing local stack.
- [x] Run syntax/config checks that do not require broad runtime changes.
- [x] Create Superset demo dataset, charts, and dashboard objects.
- [x] Wire dashboard creation into Superset bootstrap.

Verification:

- [x] `python -m py_compile demo-industrial-bi-cockpit\db\seed.py`
- [x] `docker compose config`
- [x] Reseeded the running PostgreSQL container with `db/seed.sql`.
- [x] Verified row counts and Superset health endpoint.
- [x] Created `Industrial BI Cockpit` dashboard with 7 charts.
- [x] Verified dashboard, chart, dataset, and favorite metadata rows.

Risks or dependencies:

- [x] Existing Docker volumes do not rerun `db/seed.sql`; reseed requires the
      Python script or volume recreation.

### Runtime launch fix

Goal: launch the Industrial BI Cockpit Docker stack locally.

Planned changes:

- [x] Add missing Superset PostgreSQL driver support if required by runtime.
- [x] Recreate the affected Docker services.
- [x] Verify Superset responds on `http://localhost:8088`.

Verification:

- [x] `docker compose ps`
- [x] HTTP check for Superset login page

Notes:

- First runtime attempt failed because the Superset image did not include
  `psycopg2`, while `superset_config.py` uses `postgresql+psycopg2`.

### Sprint 1 execution

Goal: execute Sprint 1 for the Industrial BI Cockpit demo, one backlog item at
a time.

Planned changes:

- [x] 1. Project skeleton.
- [x] 2. Docker Compose baseline.
- [x] 3. Synthetic industrial data.
- [x] 4. Superset bootstrap.
- [x] 5. Dashboard MVP.
- [x] 6. Documentation and smoke check.

Execution order:

- [x] Create folders and placeholder files.
- [x] Fill service definitions and config.
- [x] Fill database schema and seed script.
- [x] Fill Superset initialization scripts.
- [x] Fill dashboard/dataset planning assets.
- [x] Verify syntax and file layout.

Risks or dependencies:

- [x] Docker image pulls may require network access when running the stack.

Verification:

- [x] Check generated file list.
- [x] Run syntax checks for scripts where possible.
- [x] Optionally run Docker Compose config validation.

Notes:

- Docker runtime startup is intentionally paused by user request. Continue by
  finishing project files and documentation only.

### Sprint 1 planning

Goal: formalize the Industrial BI Cockpit demo as the first implementation
sprint.

Planned changes:

- [x] Create Sprint 1 scope document.
- [x] Define deliverables, backlog, acceptance criteria, and demo script.
- [x] Link Sprint 1 from the demo README.

Execution order:

- [x] Draft sprint document.
- [x] Update README navigation.
- [x] Verify files.

Risks or dependencies:

- [x] Sprint is documentation-only for now; no external services required.

Verification:

- [x] Review Sprint 1 file and README link.

### Demo proposal files

Goal: create a separate folder with a file-by-file Superset demo concept for a
full-stack Apache Superset vacancy response.

Planned changes:

- [x] Add demo specification folder.
- [x] Split idea into README, architecture, implementation plan, data model,
  Superset customization notes, and response pitch.

Execution order:

- [x] Restore local instruction context.
- [x] Create proposal files.
- [x] Verify created file list.

Risks or dependencies:

- [x] No runtime dependencies needed; this is documentation/spec work.

Verification:

- [x] List created files and spot-check key content.
