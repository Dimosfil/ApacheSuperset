from superset_draft import build_response


def rule_based_plan(prompt):
    text = prompt.lower()

    if any(
        word in text
        for word in (
            "простой",
            "простои",
            "простоя",
            "простоев",
            "downtime",
            "incident",
            "инцидент",
            "авари",
            "причин",
        )
    ):
        dataset = "downtime_events"
        metric = "Downtime Hours"
        dimension = "reason_category"
        title = "Downtime by reason"
    else:
        dataset = "v_production_hourly"
        metric = "OEE"
        dimension = "plant_name"
        title = "OEE by plant"

    if any(word in text for word in ("линия", "линиям", "line")):
        dimension = "line_name" if dataset == "v_production_hourly" else "line_id"
    elif any(word in text for word in ("смен", "shift")) and dataset == "v_production_hourly":
        dimension = "shift_name"
    elif any(word in text for word in ("завод", "plant")) and dataset == "v_production_hourly":
        dimension = "plant_name"
    elif any(word in text for word in ("оборуд", "equipment")) and dataset == "downtime_events":
        dimension = "equipment_id"
    elif any(word in text for word in ("детал", "detail")) and dataset == "downtime_events":
        dimension = "reason_detail"

    if any(word in text for word in ("выпуск", "output", "production")):
        dataset = "v_production_hourly"
        metric = "Total Output"
        title = "Output by plant"
    elif any(word in text for word in ("брак", "scrap", "quality")):
        dataset = "v_production_hourly"
        metric = "Scrap Rate"
        title = "Scrap rate by plant"
    elif "oee" in text or "эффектив" in text:
        dataset = "v_production_hourly"
        metric = "OEE"
        title = "OEE by plant"

    if any(word in text for word in ("динами", "trend", "по дням", "по дат", "daily")):
        chart_type = "line"
    elif any(word in text for word in ("таблиц", "table", "детали")):
        chart_type = "table"
    elif any(word in text for word in ("kpi", "число", "total", "итого")):
        chart_type = "big_number"
    else:
        chart_type = "bar"

    if any(word in text for word in ("30", "месяц", "month")):
        time_range = "Last 30 days"
    elif any(word in text for word in ("90", "кварт", "quarter")):
        time_range = "Last quarter"
    elif any(word in text for word in ("7", "недел", "week")):
        time_range = "Last week"
    else:
        time_range = "No filter"

    return {
        "title": title,
        "dataset": dataset,
        "chart_type": chart_type,
        "metric": metric,
        "dimension": dimension,
        "time_range": time_range,
        "confidence": 0.62,
        "explanation": "Rule fallback matched the prompt against the approved demo dataset catalog.",
    }


def generate_rule_based_draft(prompt):
    return build_response(prompt, rule_based_plan(prompt), "rules")
