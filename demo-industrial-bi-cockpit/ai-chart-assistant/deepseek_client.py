import json
import os
import urllib.error
import urllib.request

from chart_catalog import CHART_TYPES, DATASETS


SYSTEM_PROMPT = """You generate Apache Superset chart drafts for a fixed demo catalog.
Return only strict JSON with these keys:
title, dataset, chart_type, metric, dimension, time_range, confidence, explanation.
Use only allowed datasets, metrics, dimensions, and chart_type keys from the catalog.
Prefer simple, reviewable chart drafts over clever guesses."""


def _chat_url():
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    return f"{base_url}/chat/completions"


def deepseek_enabled():
    return bool(os.getenv("DEEPSEEK_API_KEY"))


def call_deepseek(prompt):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")

    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "prompt": prompt,
                        "catalog": DATASETS,
                        "chart_types": CHART_TYPES,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        _chat_url(),
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API returned HTTP {error.code}: {details}") from error

    content = body["choices"][0]["message"]["content"]
    return json.loads(content)
