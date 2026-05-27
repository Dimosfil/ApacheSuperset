import argparse
import json
import mimetypes
import urllib.parse
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from chart_catalog import CHART_TYPES, DATASETS
from deepseek_client import call_deepseek, deepseek_enabled
from prompt_parser import generate_rule_based_draft, rule_based_plan
from superset_draft import build_response
from ui_renderer import render_index

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def generate_chart_draft(prompt):
    if deepseek_enabled():
        try:
            plan = call_deepseek(prompt)
            response = build_response(prompt, plan, "deepseek")
            response["fallback_used"] = False
            return response
        except Exception as error:
            response = build_response(prompt, rule_based_plan(prompt), "rules")
            response["fallback_used"] = True
            response["provider_error"] = str(error)
            return response

    response = generate_rule_based_draft(prompt)
    response["fallback_used"] = False
    return response


class Handler(BaseHTTPRequestHandler):
    server_version = "IndustrialBIChartAssistant/0.1"

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_file(self, path):
        if not path.exists() or not path.is_file():
            self._send_json(404, {"error": "not_found"})
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            query = urllib.parse.parse_qs(parsed.query)
            prompt = str(query.get("prompt", [""])[0]).strip()
            body = render_index(prompt=prompt).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path.startswith("/static/"):
            requested = (STATIC_DIR / parsed.path.removeprefix("/static/")).resolve()
            if STATIC_DIR.resolve() not in requested.parents:
                self._send_json(403, {"error": "forbidden"})
                return
            self._send_file(requested)
        elif parsed.path == "/health":
            self._send_json(200, {"status": "ok", "deepseek_enabled": deepseek_enabled()})
        elif parsed.path == "/api/datasets":
            self._send_json(200, {"datasets": DATASETS, "chart_types": CHART_TYPES})
        elif parsed.path == "/api/text-to-chart":
            query = urllib.parse.parse_qs(parsed.query)
            prompt = str(query.get("prompt", [""])[0]).strip()
            if not prompt:
                self._send_json(400, {"error": "prompt is required"})
                return
            self._send_json(200, generate_chart_draft(prompt))
        else:
            self._send_json(
                200,
                {
                    "service": "Industrial BI text-to-chart assistant",
                    "endpoints": ["GET /health", "GET /api/datasets", "POST /api/text-to-chart"],
                },
            )

    def do_POST(self):
        if self.path == "/api/create-chart":
            self._send_json(
                501,
                {
                    "error": (
                        "Chart creation is available only when the assistant is "
                        "mounted inside Superset at /ai-chart-assistant/."
                    )
                },
            )
            return

        if self.path != "/api/text-to-chart":
            self._send_json(404, {"error": "not_found"})
            return

        try:
            payload = self._read_json()
            prompt = str(payload.get("prompt", "")).strip()
            if not prompt:
                self._send_json(400, {"error": "prompt is required"})
                return
            self._send_json(200, generate_chart_draft(prompt))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid_json"})
        except Exception as error:
            self._send_json(500, {"error": str(error)})

    def log_message(self, format, *args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8099)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Text-to-chart assistant listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
