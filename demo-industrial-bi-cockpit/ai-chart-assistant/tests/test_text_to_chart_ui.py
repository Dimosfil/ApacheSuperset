import json
import os
import socket
import sys
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ASSISTANT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ASSISTANT_DIR))

from app import Handler, generate_import_payload
from http.server import ThreadingHTTPServer
from prompt_parser import generate_rule_based_draft
from ui_renderer import render_index


class TextToChartUiTest(unittest.TestCase):
    def setUp(self):
        self.previous_key = os.environ.pop("DEEPSEEK_API_KEY", None)

    def tearDown(self):
        if self.previous_key is not None:
            os.environ["DEEPSEEK_API_KEY"] = self.previous_key

    def test_rule_fallback_maps_downtime_prompt_to_superset_draft(self):
        draft = generate_rule_based_draft("Show downtime by reason for the last 30 days")

        self.assertEqual(draft["provider"], "rules")
        self.assertEqual(draft["dataset"], "downtime_events")
        self.assertEqual(draft["metric"], "Downtime Hours")
        self.assertEqual(draft["dimension"], "reason_category")
        self.assertEqual(draft["viz_type"], "echarts_timeseries_bar")
        self.assertEqual(draft["time_range"], "Last 30 days")

    def test_import_payload_prepares_ai_generated_rows(self):
        payload = generate_import_payload("maintenance risk import")

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["target_table"], "ai_generated_imports")
        self.assertEqual(payload["list_url"], "/chart/list/")
        self.assertEqual(payload["prompt"], "maintenance risk import")
        self.assertGreaterEqual(len(payload["rows"]), 1)
        self.assertEqual(payload["rows"][0]["plant"], "North Plant")

    def test_renderer_outputs_no_javascript_submit_form_and_draft_values(self):
        draft = generate_rule_based_draft("Show downtime by reason for the last 30 days")
        html = render_index(prompt="Show downtime by reason for the last 30 days", draft=draft)

        self.assertIn('method="get"', html)
        self.assertIn('action="/ai-chart-assistant/"', html)
        self.assertIn("<script", html)
        self.assertIn("Сгенерить", html)
        self.assertIn('id="import-data-button"', html)
        self.assertIn("/api/import-data", html)
        self.assertIn("<summary>Примеры запросов</summary>", html)
        self.assertIn("Это примеры.", html)
        self.assertNotIn('id="create-chart-button"', html)
        self.assertNotIn("Открыть JSON", html)
        self.assertNotIn("Open Superset", html)
        self.assertNotIn("Dataset catalog", html)
        self.assertIn("Show downtime by reason for the last 30 days", html)
        self.assertIn("downtime_events", html)
        self.assertIn("Downtime Hours", html)
        self.assertIn("reason_category", html)
        self.assertIn("echarts_timeseries_bar", html)

    def test_renderer_adds_csp_nonce_to_loading_script_when_provided(self):
        html = render_index(csp_nonce="abc123")

        self.assertIn('<script nonce="abc123">', html)

    def test_renderer_escapes_prompt_before_placing_it_in_html(self):
        html = render_index(prompt='<script>alert("x")</script>')

        self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", html)
        self.assertNotIn('<script>alert("x")</script>', html)


class StandaloneHttpFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_key = os.environ.pop("DEEPSEEK_API_KEY", None)
        cls.server = ThreadingHTTPServer(("127.0.0.1", _free_port()), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_address[1]}"
        _wait_for_server(cls.base_url)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()
        if cls.previous_key is not None:
            os.environ["DEEPSEEK_API_KEY"] = cls.previous_key

    def test_get_prompt_route_returns_shell_without_blocking_on_generation(self):
        query = urllib.parse.urlencode({"prompt": "Show downtime by reason for the last 30 days"})
        with urllib.request.urlopen(f"{self.base_url}/?{query}", timeout=10) as response:
            html = response.read().decode("utf-8")

        self.assertEqual(response.status, 200)
        self.assertIn("Show downtime by reason for the last 30 days", html)
        self.assertIn("/api/text-to-chart", html)
        self.assertIn("fetch(`${routeBase}/api/text-to-chart`", html)
        self.assertNotIn("downtime_events", html)

    def test_post_api_still_returns_json_draft(self):
        body = json.dumps({"prompt": "Show downtime by reason for the last 30 days"}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/text-to-chart",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["dataset"], "downtime_events")
        self.assertEqual(payload["metric"], "Downtime Hours")
        self.assertEqual(payload["viz_type"], "echarts_timeseries_bar")

    def test_get_api_returns_json_draft_for_json_link(self):
        query = urllib.parse.urlencode({"prompt": "Show downtime by reason for the last 30 days"})
        with urllib.request.urlopen(f"{self.base_url}/api/text-to-chart?{query}", timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["dataset"], "downtime_events")
        self.assertEqual(payload["metric"], "Downtime Hours")

    def test_standalone_create_chart_route_explains_mount_requirement(self):
        request = urllib.request.Request(
            f"{self.base_url}/api/create-chart",
            data=json.dumps({"prompt": "Show downtime by reason"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(request, timeout=10)

        payload = json.loads(context.exception.read().decode("utf-8"))
        context.exception.close()
        self.assertEqual(context.exception.code, 501)
        self.assertIn("mounted inside Superset", payload["error"])

    def test_standalone_import_data_returns_preview_without_database_write(self):
        request = urllib.request.Request(
            f"{self.base_url}/api/import-data",
            data=json.dumps({"prompt": "maintenance risk import"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["target_table"], "ai_generated_imports")
        self.assertEqual(payload["list_url"], "/chart/list/")
        self.assertEqual(payload["rows_imported"], 0)
        self.assertIn("Run inside Superset", payload["message"])


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_server(base_url):
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=1):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("test server did not start")


if __name__ == "__main__":
    unittest.main()
