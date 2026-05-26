import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy import text

from superset import db
from superset.app import create_app
from superset.security import SupersetSecurityManager


DATABASE_NAME = "Industrial BI PostgreSQL"
SQLALCHEMY_URI = "postgresql+psycopg2://industrial:industrial@postgres:5432/industrial_bi"
DASHBOARD_TITLE = "Industrial BI Cockpit"


PRODUCTION_COLUMNS = [
    ("event_ts", "TIMESTAMP WITH TIME ZONE", True, False),
    ("plant_name", "TEXT", False, True),
    ("region", "TEXT", False, True),
    ("line_name", "TEXT", False, True),
    ("product_family", "TEXT", False, True),
    ("target_units_per_hour", "INTEGER", False, False),
    ("shift_name", "TEXT", False, True),
    ("product_sku", "TEXT", False, True),
    ("planned_units", "INTEGER", False, False),
    ("actual_units", "INTEGER", False, False),
    ("good_units", "INTEGER", False, False),
    ("scrap_units", "INTEGER", False, False),
    ("runtime_minutes", "NUMERIC", False, False),
    ("runtime_hours", "NUMERIC", False, False),
    ("plan_completion", "NUMERIC", False, False),
    ("scrap_rate", "NUMERIC", False, False),
    ("quality", "NUMERIC", False, False),
    ("availability", "NUMERIC", False, False),
    ("performance", "NUMERIC", False, False),
    ("oee", "NUMERIC", False, False),
]

DOWNTIME_COLUMNS = [
    ("started_at", "TIMESTAMP WITH TIME ZONE", True, False),
    ("ended_at", "TIMESTAMP WITH TIME ZONE", True, False),
    ("plant_id", "INTEGER", False, True),
    ("line_id", "INTEGER", False, True),
    ("equipment_id", "INTEGER", False, True),
    ("reason_category", "TEXT", False, True),
    ("reason_detail", "TEXT", False, True),
    ("is_planned", "BOOLEAN", False, True),
]


def get_admin_user():
    security_manager: SupersetSecurityManager = app.appbuilder.sm
    return security_manager.find_user(username="admin")


def get_database():
    database = (
        db.session.query(Database)
        .filter(Database.database_name == DATABASE_NAME)
        .one_or_none()
    )
    if database is None:
        database = Database(database_name=DATABASE_NAME, sqlalchemy_uri=SQLALCHEMY_URI)
        db.session.add(database)
        db.session.flush()
    return database


def sync_table(database, table_name, main_dttm_col, columns, metrics):
    table = (
        db.session.query(SqlaTable)
        .filter(SqlaTable.database_id == database.id, SqlaTable.table_name == table_name)
        .one_or_none()
    )
    if table is None:
        table = SqlaTable(
            table_name=table_name,
            database=database,
            main_dttm_col=main_dttm_col,
            schema=None,
        )
        db.session.add(table)
        db.session.flush()

    table.main_dttm_col = main_dttm_col
    table.database = database

    existing_columns = {column.column_name: column for column in table.columns}
    for name, column_type, is_dttm, groupby in columns:
        column = existing_columns.get(name)
        if column is None:
            column = TableColumn(column_name=name, table=table)
            db.session.add(column)
        column.type = column_type
        column.is_dttm = is_dttm
        column.groupby = groupby
        column.filterable = True
        column.is_active = True

    existing_metrics = {metric.metric_name: metric for metric in table.metrics}
    for name, expression, d3format, description in metrics:
        metric = existing_metrics.get(name)
        if metric is None:
            metric = SqlMetric(metric_name=name, table=table)
            db.session.add(metric)
        metric.expression = expression
        metric.metric_type = "sql"
        metric.d3format = d3format
        metric.description = description

    db.session.flush()
    return table


def chart_params(dataset, viz_type, params):
    base = {
        "datasource": f"{dataset.id}__table",
        "viz_type": viz_type,
        "slice_id": None,
        "time_range": "No filter",
        "adhoc_filters": [],
        "row_limit": 1000,
    }
    base.update(params)
    return json.dumps(base, sort_keys=True)


def upsert_slice(name, dataset, viz_type, params, admin):
    chart = db.session.query(Slice).filter(Slice.slice_name == name).one_or_none()
    if chart is None:
        chart = Slice(slice_name=name)
        db.session.add(chart)
    chart.datasource_id = dataset.id
    chart.datasource_type = "table"
    chart.datasource_name = dataset.table_name
    chart.viz_type = viz_type
    chart.params = chart_params(dataset, viz_type, params)
    chart.query_context = None
    chart.description = "Auto-created for Industrial BI Cockpit video demo."
    chart.certified_by = "Demo bootstrap"
    chart.certification_details = "Generated local demo chart."
    chart.owners = [admin]
    db.session.flush()
    return chart


def dashboard_layout(charts):
    rows = []
    chart_nodes = {}
    for index, chart in enumerate(charts):
        chart_id = f"CHART-{chart.id}"
        chart_nodes[chart_id] = {
            "type": "CHART",
            "id": chart_id,
            "children": [],
            "meta": {
                "chartId": chart.id,
                "height": 50 if index < 4 else 64,
                "width": 3 if index < 4 else 6,
            },
        }

    chart_ids = list(chart_nodes)
    row_groups = [chart_ids[:4], chart_ids[4:6], chart_ids[6:]]
    for idx, children in enumerate(row_groups, start=1):
        row_id = f"ROW-{idx}"
        rows.append(row_id)
        chart_nodes[row_id] = {
            "type": "ROW",
            "id": row_id,
            "children": children,
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }

    return json.dumps(
        {
            "DASHBOARD_VERSION_KEY": "v2",
            "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
            "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": rows},
            **chart_nodes,
        },
        sort_keys=True,
    )


def favorite_dashboard(admin, dashboard):
    db.session.execute(
        text(
            """
            delete from favstar
            where user_id = :user_id and class_name = 'Dashboard' and obj_id = :dashboard_id
            """
        ),
        {"user_id": admin.id, "dashboard_id": dashboard.id},
    )
    db.session.execute(
        text(
            """
            insert into favstar (user_id, class_name, obj_id, dttm, uuid)
            values (:user_id, 'Dashboard', :dashboard_id, :dttm, :uuid)
            """
        ),
        {
            "user_id": admin.id,
            "dashboard_id": dashboard.id,
            "dttm": datetime.utcnow(),
            "uuid": str(uuid4()),
        },
    )


def main():
    global Dashboard, Database, Slice, SqlaTable, SqlMetric, TableColumn

    from superset.connectors.sqla.models import SqlaTable, SqlMetric, TableColumn
    from superset.models.core import Database
    from superset.models.dashboard import Dashboard
    from superset.models.slice import Slice

    admin = get_admin_user()
    if admin is None:
        raise RuntimeError("Admin user not found. Run Superset bootstrap first.")

    database = get_database()
    production = sync_table(
        database,
        "v_production_hourly",
        "event_ts",
        PRODUCTION_COLUMNS,
        [
            ("Total Output", "sum(actual_units)", ",.0f", "Produced units."),
            ("Planned Output", "sum(planned_units)", ",.0f", "Planned units."),
            ("Scrap Rate", "sum(scrap_units)::numeric / nullif(sum(actual_units), 0)", ".1%", "Scrap share."),
            (
                "OEE",
                "(sum(runtime_minutes)::numeric / nullif(count(*) * 60, 0))"
                " * (sum(actual_units)::numeric / nullif(sum(target_units_per_hour), 0))"
                " * (sum(good_units)::numeric / nullif(sum(actual_units), 0))",
                ".1%",
                "Overall equipment effectiveness.",
            ),
        ],
    )
    downtime = sync_table(
        database,
        "downtime_events",
        "started_at",
        DOWNTIME_COLUMNS,
        [
            (
                "Downtime Hours",
                "sum(extract(epoch from ended_at - started_at)) / 3600",
                ",.1f",
                "Downtime duration in hours.",
            )
        ],
    )

    charts = [
        upsert_slice("OEE", production, "big_number_total", {"metric": "OEE"}, admin),
        upsert_slice("Output", production, "big_number_total", {"metric": "Total Output"}, admin),
        upsert_slice("Scrap Rate", production, "big_number_total", {"metric": "Scrap Rate"}, admin),
        upsert_slice("Downtime Hours", downtime, "big_number_total", {"metric": "Downtime Hours"}, admin),
        upsert_slice(
            "Plan vs Fact",
            production,
            "echarts_timeseries_line",
            {
                "granularity_sqla": "event_ts",
                "metrics": ["Planned Output", "Total Output"],
                "groupby": ["plant_name"],
            },
            admin,
        ),
        upsert_slice(
            "Downtime By Reason",
            downtime,
            "dist_bar",
            {"groupby": ["reason_category"], "metrics": ["Downtime Hours"], "columns": []},
            admin,
        ),
        upsert_slice(
            "Incident Details",
            downtime,
            "table",
            {
                "all_columns": [
                    "started_at",
                    "ended_at",
                    "plant_id",
                    "line_id",
                    "equipment_id",
                    "reason_category",
                    "reason_detail",
                    "is_planned",
                ],
                "order_desc": True,
                "page_length": 15,
            },
            admin,
        ),
    ]

    dashboard = (
        db.session.query(Dashboard)
        .filter(Dashboard.dashboard_title == DASHBOARD_TITLE)
        .one_or_none()
    )
    if dashboard is None:
        dashboard = Dashboard(dashboard_title=DASHBOARD_TITLE)
        db.session.add(dashboard)
    dashboard.slug = "industrial-bi-cockpit"
    dashboard.description = "Production efficiency cockpit for the local video demo."
    dashboard.published = True
    dashboard.certified_by = "Demo bootstrap"
    dashboard.certification_details = "Auto-created demo dashboard."
    dashboard.owners = [admin]
    dashboard.slices = charts
    db.session.flush()
    dashboard.position_json = dashboard_layout(charts)
    favorite_dashboard(admin, dashboard)

    db.session.commit()
    print(
        f"Demo dashboard ready: {dashboard.dashboard_title} "
        f"({len(charts)} charts, dashboard_id={dashboard.id})."
    )


app = create_app()
with app.app_context():
    main()
