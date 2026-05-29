import os
import sys
import json
import importlib.util
from pathlib import Path

from cachelib.redis import RedisCache


SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "change-me-industrial-bi-cockpit-demo-key")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "industrial_bi")
POSTGRES_USER = os.getenv("POSTGRES_USER", "industrial")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "industrial")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
SUPERSET_PUBLIC_HOST = os.getenv("SUPERSET_PUBLIC_HOST", "localhost")
SUPERSET_PUBLIC_PORT = os.getenv("SUPERSET_PUBLIC_PORT", os.getenv("SUPERSET_PORT", "8088"))
SUPERSET_PUBLIC_PROTOCOL = os.getenv("SUPERSET_PUBLIC_PROTOCOL", "http")
SUPERSET_PUBLIC_TUNNEL_HOST_SUFFIX = os.getenv("SUPERSET_PUBLIC_TUNNEL_HOST_SUFFIX", "")
SUPERSET_PUBLIC_BASE_URL = (
    f"{SUPERSET_PUBLIC_PROTOCOL}://{SUPERSET_PUBLIC_HOST}:{SUPERSET_PUBLIC_PORT}"
)
SUPERSET_DEMO_PUBLIC_AUTO_LOGIN = (
    os.getenv("SUPERSET_DEMO_PUBLIC_AUTO_LOGIN", "false").lower() in {"1", "true", "yes", "on"}
)
SUPERSET_DEMO_PUBLIC_AUTO_LOGIN_USER = os.getenv(
    "SUPERSET_DEMO_PUBLIC_AUTO_LOGIN_USER",
    os.getenv("SUPERSET_ADMIN_USERNAME", "admin"),
)
SUPERSET_DEMO_PUBLIC_AUTO_LOGIN_DISABLED_COOKIE = "demo_public_auto_login_disabled"

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "industrial_bi_superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": int(REDIS_PORT),
    "CACHE_REDIS_DB": 1,
}

DATA_CACHE_CONFIG = CACHE_CONFIG
RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    db=2,
    key_prefix="industrial_bi_sql_lab_results_",
)


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    imports = ("superset.sql_lab", "superset.tasks.scheduler")
    worker_prefetch_multiplier = 1
    task_acks_late = True


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ALERT_REPORTS": True,
}

LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "ru": {"flag": "ru", "name": "Russian"},
}
BABEL_DEFAULT_LOCALE = os.getenv("SUPERSET_DEFAULT_LOCALE", "en")
BABEL_DEFAULT_FOLDER = "superset/translations"
SUPERSET_PROJECT_LOCALE = os.getenv("SUPERSET_PROJECT_LOCALE", BABEL_DEFAULT_LOCALE)

SUPERSET_WEBSERVER_TIMEOUT = 120
ENABLE_PROXY_FIX = True
PREFERRED_URL_SCHEME = SUPERSET_PUBLIC_PROTOCOL
WEBDRIVER_BASEURL = SUPERSET_PUBLIC_BASE_URL
WEBDRIVER_BASEURL_USER_FRIENDLY = SUPERSET_PUBLIC_BASE_URL
SQLLAB_TIMEOUT = 120
SQLLAB_CTAS_NO_LIMIT = True
APP_NAME = "Industrial BI Cockpit"

AI_CHART_ASSISTANT_DIR = Path(os.getenv("AI_CHART_ASSISTANT_DIR", "/app/ai-chart-assistant"))


def FLASK_APP_MUTATOR(app):
    from flask import Blueprint, Response, g, jsonify, request, send_from_directory

    assistant_path = str(AI_CHART_ASSISTANT_DIR)
    if assistant_path not in sys.path:
        sys.path.insert(0, assistant_path)

    module_spec = importlib.util.spec_from_file_location(
        "industrial_bi_ai_chart_assistant_app",
        AI_CHART_ASSISTANT_DIR / "app.py",
    )
    assistant_module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(assistant_module)
    generate_chart_draft = assistant_module.generate_chart_draft
    generate_import_payload = assistant_module.generate_import_payload
    from chart_catalog import CHART_TYPES, DATASETS
    from ui_renderer import render_index

    blueprint = Blueprint("ai_chart_assistant", __name__, url_prefix="/ai-chart-assistant")
    static_dir = AI_CHART_ASSISTANT_DIR / "static"

    def _is_public_demo_host():
        host = request.host.split(":", 1)[0].lower()
        tunnel_suffix = SUPERSET_PUBLIC_TUNNEL_HOST_SUFFIX.lower()
        return host == SUPERSET_PUBLIC_HOST.lower() or (
            tunnel_suffix and host.endswith(tunnel_suffix)
        )

    def _is_logout_request():
        return request.path.rstrip("/").lower().endswith("/logout")

    def _is_login_request():
        path = request.path.rstrip("/").lower()
        return path.endswith("/login")

    @app.before_request
    def demo_public_auto_login():
        if not SUPERSET_DEMO_PUBLIC_AUTO_LOGIN:
            return None

        if not _is_public_demo_host():
            return None

        if _is_logout_request():
            return None

        if request.cookies.get(SUPERSET_DEMO_PUBLIC_AUTO_LOGIN_DISABLED_COOKIE) == "1":
            return None

        from flask_login import current_user, login_user

        if getattr(current_user, "is_authenticated", False):
            return None

        user = app.appbuilder.sm.find_user(username=SUPERSET_DEMO_PUBLIC_AUTO_LOGIN_USER)
        if user:
            login_user(user, remember=False)
            g.user = user
        return None

    @app.after_request
    def demo_public_logout_disables_auto_login(response):
        if (
            SUPERSET_DEMO_PUBLIC_AUTO_LOGIN
            and _is_public_demo_host()
            and _is_logout_request()
        ):
            response.set_cookie(
                SUPERSET_DEMO_PUBLIC_AUTO_LOGIN_DISABLED_COOKIE,
                "1",
                max_age=24 * 60 * 60,
                secure=request.scheme == "https",
                httponly=True,
                samesite="Lax",
            )
        return response

    @blueprint.get("/")
    def assistant_index():
        prompt = str(request.args.get("prompt", "")).strip()
        nonce_func = app.jinja_env.globals.get("csp_nonce")
        csp_nonce = nonce_func() if nonce_func else ""
        response = Response(
            render_index(prompt=prompt, csp_nonce=csp_nonce),
            mimetype="text/html",
        )
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @blueprint.get("/static/<path:filename>")
    def assistant_static(filename):
        return send_from_directory(static_dir, filename)

    @blueprint.get("/health")
    def assistant_health():
        return jsonify({"status": "ok", "mounted_in": "superset"})

    @blueprint.get("/api/datasets")
    def assistant_datasets():
        return jsonify({"datasets": DATASETS, "chart_types": CHART_TYPES})

    def _chart_response_from_prompt(prompt):
        prompt = str(prompt or "").strip()
        if not prompt:
            return jsonify({"error": "prompt is required"}), 400
        return jsonify(generate_chart_draft(prompt))

    @blueprint.get("/api/text-to-chart")
    def assistant_text_to_chart_get():
        return _chart_response_from_prompt(request.args.get("prompt", ""))

    @blueprint.post("/api/text-to-chart")
    def assistant_text_to_chart():
        payload = request.get_json(silent=True) or {}
        return _chart_response_from_prompt(payload.get("prompt", ""))

    def _create_chart_from_payload(payload):
        from superset import db
        from superset.connectors.sqla.models import SqlaTable
        from superset.models.slice import Slice

        draft = payload.get("draft") or {}
        prompt = str(payload.get("prompt") or draft.get("prompt") or "").strip()
        if not draft:
            if not prompt:
                return {"error": "prompt or draft is required"}, 400
            draft = generate_chart_draft(prompt)

        dataset_name = str(draft.get("dataset") or "").strip()
        if dataset_name not in DATASETS:
            return {"error": f"unknown dataset: {dataset_name}"}, 400

        table = db.session.query(SqlaTable).filter_by(table_name=dataset_name).first()
        if not table:
            return {"error": f"dataset is not registered in Superset: {dataset_name}"}, 404

        params = dict(draft.get("superset_params") or {})
        params["datasource"] = f"{table.id}__table"
        params["slice_id"] = None
        viz_type = str(draft.get("viz_type") or params.get("viz_type") or "").strip()
        if not viz_type:
            return {"error": "draft is missing viz_type"}, 400
        params["viz_type"] = viz_type

        title = str(draft.get("title") or "AI chart draft").strip()[:250]
        chart = Slice(
            slice_name=title,
            viz_type=viz_type,
            datasource_id=table.id,
            datasource_type="table",
            params=json.dumps(params, ensure_ascii=False, sort_keys=True),
            description=str(draft.get("explanation") or ""),
        )
        user = getattr(g, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            chart.owners = [user]

        db.session.add(chart)
        db.session.commit()

        explore_url = f"/superset/explore/table/{table.id}/?slice_id={chart.id}"
        return {
            "id": chart.id,
            "url": explore_url,
            "list_url": "/chart/list/",
            "slice_name": chart.slice_name,
        }, 200

    @blueprint.post("/api/create-chart")
    def assistant_create_chart():
        payload = request.get_json(silent=True) or {}
        chart_payload, status = _create_chart_from_payload(payload)
        return jsonify(chart_payload), status

    @blueprint.post("/api/import-data")
    def assistant_import_data():
        from sqlalchemy import text
        from superset import db

        payload = request.get_json(silent=True) or {}
        import_payload = generate_import_payload(payload.get("prompt", ""))
        rows = import_payload["rows"]
        with db.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    create table if not exists ai_generated_imports (
                      id bigserial primary key,
                      created_at timestamptz not null default now(),
                      source_prompt text not null,
                      plant text not null,
                      metric text not null,
                      value numeric not null,
                      unit text not null,
                      import_note text not null
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    insert into ai_generated_imports (
                      source_prompt, plant, metric, value, unit, import_note
                    ) values (
                      :source_prompt, :plant, :metric, :value, :unit, :import_note
                    )
                    """
                ),
                [
                    {
                        "source_prompt": import_payload["prompt"],
                        "plant": row["plant"],
                        "metric": row["metric"],
                        "value": row["value"],
                        "unit": row["unit"],
                        "import_note": row["note"],
                    }
                    for row in rows
                ],
            )

        chart_payload, chart_status = _create_chart_from_payload(payload)
        if chart_status >= 400:
            import_payload["status"] = "imported_chart_failed"
            import_payload["rows_imported"] = len(rows)
            import_payload["message"] = "AI generated rows imported, but chart creation failed."
            import_payload["chart_error"] = chart_payload.get("error", "chart creation failed")
            return jsonify(import_payload), chart_status

        import_payload["status"] = "imported"
        import_payload["rows_imported"] = len(rows)
        import_payload["message"] = "AI generated rows imported and chart created."
        import_payload["chart"] = chart_payload
        import_payload["list_url"] = chart_payload.get("list_url", import_payload["list_url"])
        return jsonify(import_payload)

    csrf = app.extensions.get("csrf")
    if csrf:
        csrf.exempt(blueprint)
    app.register_blueprint(blueprint)

    @app.after_request
    def add_industrial_shell_styles(response):
        content_type = response.headers.get("Content-Type", "")
        if response.direct_passthrough or "text/html" not in content_type:
            return response

        from flask_login import current_user

        if (
            _is_login_request()
            or _is_logout_request()
            or request.path.startswith("/ai-chart-assistant")
            or not getattr(current_user, "is_authenticated", False)
        ):
            return response

        stylesheet = "/static/industrial-bi-shell.css?v=20260527-3"
        script_src = "/static/industrial-bi-home-assist.js?v=20260527-3"
        try:
            html = response.get_data(as_text=True)
        except RuntimeError:
            return response
        if stylesheet in html and script_src in html:
            return response

        head_end = html.lower().find("</head>")
        if head_end == -1:
            return response

        tags = []
        if stylesheet not in html:
            tags.append(f'<link rel="stylesheet" href="{stylesheet}">')
        if script_src not in html:
            nonce_func = app.jinja_env.globals.get("csp_nonce")
            csp_nonce = nonce_func() if nonce_func else ""
            nonce_attr = f' nonce="{csp_nonce}"' if csp_nonce else ""
            tags.append(f'<script src="{script_src}" defer{nonce_attr}></script>')
        html = f"{html[:head_end]}{''.join(tags)}{html[head_end:]}"
        response.set_data(html)
        response.headers["Content-Length"] = str(len(response.get_data()))
        return response

    return app
