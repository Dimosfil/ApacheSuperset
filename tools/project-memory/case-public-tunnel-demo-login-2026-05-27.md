# Public tunnel demo login case 2026-05-27

## Summary

After restoring `https://small-webs-jog.loca.lt`, the public Superset UI showed
the Sign in page even though the local/LAN Superset UI was already logged in.
The AI Assist widget still appeared because it is injected into Superset HTML
regardless of whether the main Superset route is authenticated.

## Cause

Browser sessions are scoped by host. A valid local session cookie for
`192.168.3.55` is not sent to `small-webs-jog.loca.lt`, so the public tunnel
domain starts as a fresh unauthenticated browser context.

## Repair

Added a demo-only Superset config switch:

```text
SUPERSET_DEMO_PUBLIC_AUTO_LOGIN=true
SUPERSET_DEMO_PUBLIC_AUTO_LOGIN_USER=admin
```

When enabled, `superset_config.py` auto-logins the configured demo user only
when the request host matches `SUPERSET_PUBLIC_HOST`. For this environment that
host is `small-webs-jog.loca.lt`.

This keeps the behavior explicit and scoped to the public demo host.

## Verification

Verified on 2026-05-27:

- Superset config compiles.
- Docker Compose config validates.
- Superset was recreated.
- `localtunnel` was restarted after Superset recreation.
- `https://small-webs-jog.loca.lt/chart/list/` returned `200`, did not contain
  the Sign in form, and set a `session` cookie for the public host.
- Public chart list APIs returned `200` in the same session.

## Reuse Notes

- If the public tunnel shows Sign in while the local UI is logged in, do not
  debug this as a Superset backend failure first. Check host-scoped cookies.
- For a temporary remote demo, use the explicit demo auto-login switch.
- Do not enable this pattern outside disposable/local demo environments.
