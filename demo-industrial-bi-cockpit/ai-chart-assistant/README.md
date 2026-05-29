# AI Chart Assistant

Small proof-of-concept UI/service for catalog-safe text-to-chart generation.

It accepts a user prompt and returns a Superset chart draft. If
`DEEPSEEK_API_KEY` is present, the service asks DeepSeek Chat Completions to map
the prompt to the approved demo catalog. If the key is absent or the API call
fails, it falls back to deterministic rules.

In the main demo, this UI is mounted inside Superset:

```text
http://localhost:8088/ai-chart-assistant/
```

For the current external tunnel configuration:

```text
https://apache-superset-demo-fil-20260528.loca.lt/ai-chart-assistant/
```

## Environment

```powershell
$env:DEEPSEEK_API_KEY = "<your key>"
$env:DEEPSEEK_MODEL = "deepseek-chat"
$env:DEEPSEEK_BASE_URL = "https://api.deepseek.com"
```

Do not commit real API keys.

## Run

```powershell
python app.py --host 127.0.0.1 --port 8099
```

Standalone development mode:

```text
http://localhost:8099
```

Docker Compose keeps the standalone service behind the `standalone-ai` profile.
The normal demo route is served by Superset itself.

By default the Compose service does not pass `DEEPSEEK_API_KEY`, so diagnostic
commands such as `docker compose config` do not print the secret. For a real API
call, run the service locally from a shell that already has `DEEPSEEK_API_KEY`.

## Example

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8099/api/text-to-chart `
  -ContentType 'application/json' `
  -Body '{"prompt":"Покажи простои по причинам за последние 30 дней"}'
```

Supported demo prompts:

- `Покажи простои по причинам за последние 30 дней`
- `Покажи OEE по заводам`
- `Покажи динамику выпуска по дням`
- `Покажи долю брака по линиям`
- `Покажи таблицу инцидентов по оборудованию`

The response includes `superset_params`, which can be used as a draft for a
Superset chart configuration.

## Tests

```powershell
python -m unittest discover -s ai-chart-assistant/tests -v
```

Run the command from the `demo-industrial-bi-cockpit/` folder.

The tests cover the no-JavaScript form submit path, HTML rendering with chart
draft values, escaping of user prompts, and the JSON API fallback path.
