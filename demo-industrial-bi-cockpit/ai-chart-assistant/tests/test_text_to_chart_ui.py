import json
import os
import socket
import sys
import threading
import time
import unittest
import urllib.parse
import urllib.request
from pathlib import Path


ASSISTANT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ASSISTANT_DIR))

from app import Handler
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

    def test_renderer_outputs_no_javascript_submit_form_and_draft_values(self):
        draft = generate_rule_based_draft("Show downtime by reason for the last 30 days")
        html = render_index(prompt="Show downtime by reason for the last 30 days", draft=draft)

        self.assertIn('method="get"', html)
        self.assertIn('action="/ai-chart-assistant/"', html)
        self.assertIn("<script", html)
        self.assertIn("Генерация...", html)
        self.assertIn("Show downtime by reason for the last 30 days", html)
        self.assertIn("downtime_events", html)
        self.assertIn("Downtime Hours", html)
        self.assertIn("reason_category", html)
        self.assertIn("echarts_timeseries_bar", html)
        self.assertIn("/ai-chart-assistant/api/text-to-chart?prompt=Show%20downtime", html)

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

    def test_get_prompt_route_returns_rendered_chart_draft_html(self):
        query = urllib.parse.urlencode({"prompt": "Show downtime by reason for the last 30 days"})
        with urllib.request.urlopen(f"{self.base_url}/?{query}", timeout=10) as response:
            html = response.read().decode("utf-8")

        self.assertEqual(response.status, 200)
        self.assertIn("downtime_events", html)
        self.assertIn("Downtime Hours", html)
        self.assertIn("echarts_timeseries_bar", html)

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
