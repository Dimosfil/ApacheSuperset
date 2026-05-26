# Future File Map

This is the target implementation layout after the planning folder turns into a
runnable demo.

```text
demo-industrial-bi-cockpit/
  README.md
  docker-compose.yml
  .env.example
  Makefile
  .gitignore

  db/
    init.sql
    seed.sql
    seed.py
    requirements.txt

  superset/
    Dockerfile
    superset_config.py
    bootstrap/
      init-superset.sh
      import-assets.sh
      create-users.sh
    assets/
      database.yaml
      datasets/
      dashboards/

  plugins/
    superset-plugin-chart-oee-gauge/
      package.json
      src/
      test/

  docs/
    screenshots/
    acceptance-report.md
    dashboard-mvp.md
    manual-dashboard-build.md
    reviewer-quickstart.md
    smoke-checklist.md
    implementation-notes.md
```

## Minimal First Build

If time is short, implement only:

- `docker-compose.yml`
- `db/init.sql`
- `db/seed.py`
- `superset/superset_config.py`
- dashboard export
- `docs/smoke-checklist.md`

Then add the custom plugin as the second proof point.
