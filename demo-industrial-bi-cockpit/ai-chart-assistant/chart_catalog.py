DATASETS = {
    "v_production_hourly": {
        "label": "Production hourly facts",
        "description": "Hourly production, quality, OEE, plant, line, shift, and product metrics.",
        "time_column": "event_ts",
        "metrics": {
            "OEE": "Overall equipment effectiveness.",
            "Total Output": "Produced units.",
            "Planned Output": "Planned production units.",
            "Scrap Rate": "Scrap units divided by actual units.",
        },
        "dimensions": {
            "plant_name": "Plant name.",
            "line_name": "Production line.",
            "shift_name": "Shift.",
            "product_family": "Product family.",
            "region": "Plant region.",
        },
        "default_metric": "OEE",
        "default_dimension": "plant_name",
    },
    "downtime_events": {
        "label": "Downtime events",
        "description": "Equipment downtime incidents with reason, duration, plant, line, and equipment context.",
        "time_column": "started_at",
        "metrics": {
            "Downtime Hours": "Total downtime duration in hours.",
        },
        "dimensions": {
            "reason_category": "High-level downtime reason.",
            "reason_detail": "Detailed downtime reason.",
            "plant_id": "Plant identifier.",
            "line_id": "Line identifier.",
            "equipment_id": "Equipment identifier.",
            "is_planned": "Whether downtime was planned.",
        },
        "default_metric": "Downtime Hours",
        "default_dimension": "reason_category",
    },
}

CHART_TYPES = {
    "bar": "echarts_timeseries_bar",
    "line": "echarts_timeseries_line",
    "table": "table",
    "big_number": "big_number_total",
}
