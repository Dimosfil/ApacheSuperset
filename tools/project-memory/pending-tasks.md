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

### Align localtunnel public host 2026.05.28

Goal: keep the Localtunnel subdomain, Superset public host, and demo docs in
sync so the public Superset URL is predictable.

Planned changes:

- [x] Align `PUBLIC_TUNNEL_SUBDOMAIN` with `SUPERSET_PUBLIC_HOST`.
- [x] Update public demo docs that still reference the previous tunnel host.
- [x] Validate Docker Compose config.

Verification:

- [x] `docker compose config --quiet`
- [x] `public-tunnel` logs show
      `https://apache-superset-demo-fil-20260528.loca.lt`.
- [x] `https://apache-superset-demo-fil-20260528.loca.lt/health` returns
      `200 OK`.
- [x] `https://apache-superset-demo-fil-20260528.loca.lt/chart/list/` returns
      `200`, sets a session cookie, and does not render the login form.

### Docker localtunnel public demo 2026.05.28

Goal: provide an ngrok-like public URL for the local Docker Superset demo using
a simple always-on Docker service.

Planned changes:

- [x] Replace the failed Cloudflare connector path with a `public-tunnel`
      Docker service based on `localtunnel`.
- [x] Remove the temporary Cloudflare DNS proxy file and local Cloudflare
      tunnel token from `.env`.
- [x] Allow demo auto-login for `*.loca.lt` tunnel hosts.
- [x] Restart Superset and the tunnel.

Verification:

- [x] `docker compose config --quiet`
- [x] `https://apache-superset-demo-fil-20260528.loca.lt/health` returns
      `200 OK`.
- [x] `https://apache-superset-demo-fil-20260528.loca.lt/chart/list/` returns
      `200`, sets a session cookie, and does not render the login form.

### Add persistent Cloudflare Tunnel service 2026.05.28

Goal: make the Superset demo reachable through a persistent Cloudflare Tunnel
without committing Cloudflare credentials.

Planned changes:

- [x] Add a Docker Compose `cloudflared` service with restart policy.
- [x] Document the local-only tunnel token variable in `.env.example`.
- [x] Validate Docker Compose config.

Verification:

- [x] `docker compose config --quiet`
- [x] `docker compose --profile public-tunnel config --quiet`
- [x] Verified the provided Cloudflare API token is active.
- [x] Retrieved the connector token for existing tunnel `apache-superset-demo`
      and wrote it to ignored local `.env`.
- [!] Started `cloudflared`, but the connector remains inactive because the
      current network refuses SRV DNS lookups for
      `_v2-origintunneld._tcp.argotunnel.com`.

Notes:

- `cloudflared` service now uses `restart: unless-stopped`, explicit
  Cloudflare DNS resolver entries, and `--protocol http2`.
- Cloudflare API reports tunnel status `inactive` while local DNS blocks edge
  discovery.

### Hide demo shell after logout 2026.05.27

Goal: keep the logged-out login page clean by removing demo shell assets and
the AI Assist widget from unauthenticated/login/logout responses.

Planned changes:

- [x] Restrict Superset shell asset injection to authenticated Superset pages.
- [x] Run focused syntax/config checks.
- [x] Restart Superset and verify public login page has no widget.

Verification:

- [x] `python -m py_compile demo-industrial-bi-cockpit\superset\superset_config.py`
- [x] `docker compose config --quiet`
- [x] Recreated the Superset service.
- [x] After public logout, `/chart/list/` lands on `/login/?next=...` without
      `industrial-bi-home-assist`, `industrial-ai-assist`, or
      `industrial-bi-shell` in the HTML.
- [x] A fresh public session still auto-logins and receives the demo shell
      assets.

### Fix public tunnel logout loop 2026.05.27

Goal: make explicit logout work on the public demo tunnel while keeping the
demo auto-login behavior for fresh visitors.

Planned changes:

- [x] Add a logout-aware opt-out for demo public auto-login.
- [x] Run focused syntax/config checks.
- [x] Restart Superset and verify logout no longer immediately logs back in.

Verification:

- [x] `python -m py_compile demo-industrial-bi-cockpit\superset\superset_config.py`
- [x] `docker compose config --quiet`
- [x] Recreated the Superset service.
- [x] Public session logout sets `demo_public_auto_login_disabled=1`; the next
      `/chart/list/` request redirects to `/login/?next=...` instead of
      auto-logging in.
- [x] A fresh browser session still auto-logins to `/chart/list/`.

### Set up Cloudflare tunnel for Superset demo 2026.05.27

Goal: replace the fragile temporary localtunnel endpoint with a Cloudflare
Tunnel path for the Superset demo without storing secrets in the repository.

Planned changes:

- [x] Install a project-local `cloudflared` binary.
- [x] Verify the provided Cloudflare token can access the needed account.
- [!] Start or prepare a tunnel for `192.168.3.55:8088`.
- [x] Verify the existing public Superset route returns 200.

Notes:

- `cloudflared` 2026.5.2 was installed under ignored `tools/bin/`.
- After updating token resources, the token sees account
  `6704a7ccd4419faa316c293646fde2bf` but no zones.
- Created Cloudflare named tunnel `apache-superset-demo`
  (`20de5046-4f7b-4154-8670-20a5d4d5617c`) via API. Its connector remains
  inactive because local `cloudflared` cannot connect to Cloudflare edge from
  this network.
- Accountless Quick Tunnel generated `trycloudflare.com` URLs, but the connector
  could not establish an edge connection. System DNS resolves `argotunnel.com`
  to a private/intercept range, and direct edge attempts failed TLS/HTTP2
  handshake despite TCP reachability.
- Attempts with `--protocol http2`, `--dns-resolver-addrs`, direct `--edge`
  addresses, and `--edge-bind-address 192.168.3.55` still failed.
- Existing `localtunnel` endpoint still works:
  `https://small-webs-jog.loca.lt/chart/list/` returns 200 without the Sign in
  form.

### Fix public tunnel demo login 2026.05.27

Goal: make the remote `small-webs-jog.loca.lt` demo open directly in Superset
instead of showing the login form because the LAN cookie is not shared with the
public tunnel domain.

Planned changes:

- [x] Add a demo-only public-host auto-login switch to Superset config.
- [x] Enable the switch in the local demo `.env` and Compose environment.
- [x] Restart Superset and verify public `/chart/list/` reaches the app as an
      authenticated demo user.

Verification:

- [x] `python -m py_compile demo-industrial-bi-cockpit\superset\superset_config.py`
- [x] `docker compose config --quiet`
- [x] Recreated the Superset container.
- [x] Restarted `localtunnel` after Superset recreation.
- [x] `https://small-webs-jog.loca.lt/chart/list/` returned `200`, did not
      contain the Sign in form, and set a `session` cookie for the public host.
- [x] Public chart APIs in the same session returned `200`:
      `/api/v1/chart/_info?q=(keys:!(permissions))` and
      `/api/v1/chart/?q=(order_column:changed_on_delta_humanized,order_direction:desc,page:0,page_size:25)`.

Notes:

- The login screen on the public tunnel was expected after switching hostnames:
  the LAN session cookie from `192.168.3.55` is not shared with
  `small-webs-jog.loca.lt`.
- The fix is demo-only and gated by `SUPERSET_DEMO_PUBLIC_AUTO_LOGIN=true`.

### Restore Superset localtunnel 2026.05.27

Goal: restore the public `small-webs-jog.loca.lt` tunnel after Chrome showed
`503 - Tunnel Unavailable` for `/chart/list/`.

Planned changes:

- [x] Record the tunnel failure pattern and current binding details as project
      experience.
- [x] Verify the local Superset endpoint on the bound LAN address.
- [x] Restart `localtunnel` against the correct local host.
- [x] Verify the public `/chart/list/` route.

Notes:

- Superset is bound by Compose to `192.168.3.55:8088`, not
  `127.0.0.1:8088`; tunnel restarts should use `--local-host 192.168.3.55`.
- `503 - Tunnel Unavailable` from `*.loca.lt` usually means the local tunnel
  process is down, disconnected, or pointing at the wrong local host/port.
- Recovery command used from `demo-industrial-bi-cockpit`:
  `npx --yes localtunnel --port 8088 --local-host 192.168.3.55 --subdomain small-webs-jog`.

Verification:

- [x] `http://192.168.3.55:8088/health` returned `200 OK`.
- [x] `http://192.168.3.55:8088/chart/list/` returned `200`.
- [x] `https://small-webs-jog.loca.lt/chart/list/` returned `200` after
      restarting `localtunnel`.

### Fix Superset home left-edge clipping 2026.05.27

Goal: restore safe left spacing on the Superset shell/home page so labels and
section toggles are not clipped against the viewport edge.

Planned changes:

- [x] Add a small Superset static CSS override and load it from the Flask app mutator.
- [x] Run focused syntax/config checks and note restart needs.

Verification:

- [x] `python -m py_compile .\demo-industrial-bi-cockpit\superset\superset_config.py`
- [x] `docker compose config --quiet`
- [x] Recreated the Superset service and verified `/health`, the static CSS,
      and HTML stylesheet injection on `http://192.168.3.55:8088/`.

### Fix AI chart assistant chart creation flow 2026.05.27

Goal: avoid the failed manual Superset JSON import from `/ai-chart-assistant/`
by letting the mounted assistant create a chart draft inside Superset.

Planned changes:

- [x] Add a Superset-mounted API endpoint that creates a Slice from an assistant draft.
- [x] Add a UI action that calls the endpoint and opens the created chart.
- [x] Run focused regression and syntax checks, then restart/verify Superset.

Verification:

- [x] `python -m unittest discover -s .\demo-industrial-bi-cockpit\ai-chart-assistant\tests -v`
- [x] Syntax parsed in the Superset container without writing `.pyc`.
- [x] Restarted Superset and verified `/ai-chart-assistant/` renders the create action.
- [x] Created chart id 14 through `/ai-chart-assistant/api/create-chart`.
- [x] After a blank external Explore screen, changed created chart links to
      `/superset/explore/table/<dataset_id>/?slice_id=<chart_id>` and added a
      `/chart/list/` fallback link; verified chart id 16 returns the new URL.
- [x] Added a mounted no-op `/static/service-worker.js` to remove the missing
      service-worker console error; verified local and tunnel static assets
      return 200 after recreating Superset.

### Fix AI chart assistant refresh hang 2026.05.27

Goal: find and fix the long reload/request delay and broken generate button
state after repeated refreshes on `/ai-chart-assistant/`.

Planned changes:

- [x] Inspect assistant route and client-side submit/reload logic.
- [x] Apply the smallest scoped fix for stale/slow loading state.
- [x] Run focused syntax/regression checks.

Verification:

- [x] `python -m unittest discover -s .\demo-industrial-bi-cockpit\ai-chart-assistant\tests -v`
- [x] `python -m compileall -q demo-industrial-bi-cockpit\superset\superset_config.py demo-industrial-bi-cockpit\ai-chart-assistant`
- [x] Restarted Superset and checked local/public assistant GET routes return 200 quickly.

### Add DeepSeek text-to-chart PoC 2026.05.27

Goal: add a small AI-assisted text-to-chart draft service for the Superset demo.

Planned changes:

- [x] Add a catalog-based chart draft generator with rule fallback.
- [x] Add optional DeepSeek Chat API integration through environment variables.
- [x] Add a small HTTP endpoint and demo documentation.
- [x] Run syntax and smoke checks without exposing secrets.

Verification:

- [x] `python -m py_compile ai-chart-assistant\*.py`
- [x] `docker compose config` checked after removing secret passthrough from
      the service config.
- [x] Rule fallback returned a Superset draft for a downtime prompt.
- [x] Live DeepSeek call returned a Superset draft for English and UTF-8 Russian
      downtime prompts.
- [x] Local HTTP endpoint returned a DeepSeek-backed draft at
      `http://127.0.0.1:8099/api/text-to-chart`.

Follow-up: add a simple browser UI.

- [x] Serve a first-page web UI from the assistant service.
- [x] Wire prompt submission to `POST /api/text-to-chart`.
- [x] Restart the local assistant service and smoke-check UI/API.

Follow-up: mount assistant into the main Superset site.

- [x] Add a Superset Flask route at `/ai-chart-assistant/`.
- [x] Mount assistant files into the Superset container.
- [x] Keep the standalone assistant as an optional Compose profile.
- [x] Restart Superset and verify the public-path route.

Verification:

- [x] `python -m py_compile superset\superset_config.py ai-chart-assistant\*.py`
- [x] `docker compose config --quiet`
- [x] Local unified route returned the UI:
      `http://192.168.3.55:8088/ai-chart-assistant/`
- [x] Local unified POST route returned a DeepSeek draft:
      `http://192.168.3.55:8088/ai-chart-assistant/api/text-to-chart`
- [x] External unified route returned the UI:
      `https://small-webs-jog.loca.lt/ai-chart-assistant/`
- [x] External unified POST route returned a DeepSeek draft:
      `https://small-webs-jog.loca.lt/ai-chart-assistant/api/text-to-chart`

Follow-up: add regression tests for the no-JavaScript submit flow.

- [x] Add focused unittest coverage for rendered form and chart draft HTML.
- [x] Add standalone HTTP regression coverage for `?prompt=...`.
- [x] Run tests and syntax checks.

Verification:

- [x] `python -m unittest discover -s .\ai-chart-assistant\tests -v`
- [x] `python -m py_compile superset\superset_config.py ai-chart-assistant\*.py ai-chart-assistant\tests\test_text_to_chart_ui.py`

### Investigate Superset home loading delay 2026.05.27

Goal: find why the Superset home page skeleton loaders stay visible for about
10-15 seconds.

Planned checks:

- [x] Measure Superset home and API response times.
- [x] Inspect targeted Superset logs for slow requests or backend errors.
- [x] Identify likely bottleneck and recommend/fix the smallest scoped change.

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

### Main screen AI assist entry

Goal: surface the existing AI Chart Assistant from the Superset main screen and
add an AI data import action for the demo.

Planned changes:

- [x] Inject a small Superset-side AI assist launcher into HTML pages.
- [x] Add a data import action wired to an assistant API endpoint.
- [x] Style the launcher so it works on desktop and mobile.
- [x] Cover the injected assets and API with focused tests.

Verification:

- [x] Run the AI assistant unittest suite.

### AI assist simplified controls

Goal: simplify AI assist controls to generation, import, and a compact examples
dropdown.

Planned changes:

- [x] Leave only Generate and Import actions on the assistant page.
- [x] Make Import redirect to the Superset chart list after the API succeeds.
- [x] Convert example prompts into a dropdown with a short note.
- [x] Align the main-screen AI widget labels and import redirect behavior.

Verification:

- [x] Run syntax checks and AI assistant tests.

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

### Static external Superset address

Goal: make the demo stack bind Superset to the LAN/static host address
`192.168.3.55:8088` for external router port forwarding.

Planned changes:

- [x] Add explicit external host/port environment defaults.
- [x] Bind the Superset Compose port mapping to the configured host address.
- [x] Configure Superset external base URLs and proxy handling.
- [x] Document the LAN URL in the quick start.

Verification:

- [x] Validate the Docker Compose configuration.
