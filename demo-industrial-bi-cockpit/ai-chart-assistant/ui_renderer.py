import html
import json
import urllib.parse
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "static" / "index.html"


def _escape(value):
    return html.escape(str(value or ""), quote=True)


def _params_json(draft):
    return json.dumps(draft.get("superset_params", {}), ensure_ascii=False, indent=2)


def render_index(prompt="", draft=None, error="", csp_nonce=""):
    draft = draft or {}
    params_json = _params_json(draft)
    provider = draft.get("provider") or "Готово"
    if draft.get("fallback_used"):
        provider = "Fallback rules"
    if error:
        provider = "Error"

    api_url = "/ai-chart-assistant/api/text-to-chart"
    if prompt:
        encoded_prompt = urllib.parse.quote(prompt)
        api_url = f"/ai-chart-assistant/api/text-to-chart?prompt={encoded_prompt}"

    replacements = {
        "{{ prompt }}": _escape(prompt or "Покажи простои по причинам за последние 30 дней"),
        "{{ provider }}": _escape(provider),
        "{{ confidence }}": _escape(
            f"Уверенность {round(float(draft.get('confidence', 0)) * 100)}%"
            if draft.get("confidence")
            else ""
        ),
        "{{ title }}": _escape(draft.get("title") or "Черновик чарта"),
        "{{ dataset }}": _escape(draft.get("dataset") or "-"),
        "{{ chart_type }}": _escape(draft.get("viz_type") or draft.get("chart_type") or "-"),
        "{{ metric }}": _escape(draft.get("metric") or "-"),
        "{{ dimension }}": _escape(draft.get("dimension") or "-"),
        "{{ time_range }}": _escape(draft.get("time_range") or "-"),
        "{{ explanation }}": _escape(error or draft.get("explanation") or ""),
        "{{ params_json }}": _escape(params_json),
        "{{ api_url }}": _escape(api_url),
        "{{ csp_nonce_attr }}": f' nonce="{_escape(csp_nonce)}"' if csp_nonce else "",
    }

    content = INDEX_PATH.read_text(encoding="utf-8")
    for token, value in replacements.items():
        content = content.replace(token, value)
    return content
