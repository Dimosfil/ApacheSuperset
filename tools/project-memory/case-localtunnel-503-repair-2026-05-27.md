# Localtunnel 503 repair case 2026-05-27

## Summary

Chrome showed `503 - Tunnel Unavailable` for:

```text
https://small-webs-jog.loca.lt/chart/list/
```

The Superset container was healthy, so the issue was the public tunnel, not the
Superset application.

## Environment

- Project: Apache Superset demo workspace.
- Compose service: `industrial-bi-cockpit-superset-1`.
- Superset container port: `8088`.
- Host binding observed during repair: `192.168.3.55:8088->8088/tcp`.
- Public tunnel host: `small-webs-jog.loca.lt`.

## Root Cause

`localtunnel` was unavailable or disconnected. A naive tunnel restart against
`127.0.0.1:8088` would not work in this environment because Superset was bound
to the LAN address `192.168.3.55:8088`.

## Repair

Start the tunnel from `demo-industrial-bi-cockpit` with the explicit local host:

```powershell
npx --yes localtunnel --port 8088 --local-host 192.168.3.55 --subdomain small-webs-jog
```

For background launch on Windows, use `Start-Process` with
`-WindowStyle Hidden` and redirect stdout/stderr to a project-local runtime log
if logs are needed.

## Verification

The repair was verified on 2026-05-27 19:31 +03:00:

- `http://192.168.3.55:8088/health` returned `200 OK`.
- `http://192.168.3.55:8088/chart/list/` returned `200`.
- `https://small-webs-jog.loca.lt/health` returned `200 OK`.
- `https://small-webs-jog.loca.lt/chart/list/` returned `200`.

## Reuse Notes

- If `*.loca.lt` returns `503 - Tunnel Unavailable`, first check whether the
  local app is healthy on the actual Compose bind host and port.
- Then check whether a `localtunnel` process exists for the expected subdomain.
- Restart `localtunnel` with the same local host that Docker Compose exposes,
  not an assumed localhost address.
- Keep this as operational memory; do not store secrets or public credentials in
  this note.
