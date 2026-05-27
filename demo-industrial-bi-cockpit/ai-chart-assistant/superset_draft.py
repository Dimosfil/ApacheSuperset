from chart_catalog import CHART_TYPES, DATASETS


def _dataset(name):
    return DATASETS.get(name) or DATASETS["v_production_hourly"]


def _safe_metric(dataset_name, metric):
    dataset = _dataset(dataset_name)
    if metric in dataset["metrics"]:
        return metric
    return dataset["default_metric"]


def _safe_dimension(dataset_name, dimension):
    dataset = _dataset(dataset_name)
    if dimension in dataset["dimensions"]:
        return dimension
    return dataset["default_dimension"]


def normalize_plan(plan):
    dataset_name = plan.get("dataset")
    if dataset_name not in DATASETS:
        dataset_name = "v_production_hourly"

    chart_type = plan.get("chart_type") or "bar"
    if chart_type in CHART_TYPES:
        viz_type = CHART_TYPES[chart_type]
    elif chart_type in CHART_TYPES.values():
        viz_type = chart_type
        chart_type = next(key for key, value in CHART_TYPES.items() if value == viz_type)
    else:
        chart_type = "bar"
        viz_type = CHART_TYPES[chart_type]

    metric = _safe_metric(dataset_name, plan.get("metric"))
    dimension = _safe_dimension(dataset_name, plan.get("dimension"))
    dataset = _dataset(dataset_name)
    time_column = plan.get("time_column") or dataset["time_column"]
    if time_column != dataset["time_column"]:
        time_column = dataset["time_column"]

    time_range = plan.get("time_range") or "No filter"
    title = plan.get("title") or f"{metric} by {dimension}"
    explanation = plan.get("explanation") or "Draft generated from the allowed demo catalog."
    confidence = float(plan.get("confidence") or 0.65)
    confidence = max(0.0, min(confidence, 1.0))

    return {
        "title": title,
        "dataset": dataset_name,
        "chart_type": chart_type,
        "viz_type": viz_type,
        "metric": metric,
        "dimension": dimension,
        "time_column": time_column,
        "time_range": time_range,
        "confidence": confidence,
        "explanation": explanation,
    }


def to_superset_params(draft):
    params = {
        "viz_type": draft["viz_type"],
        "datasource": f"{draft['dataset']}__table",
        "time_range": draft["time_range"],
        "row_limit": 1000,
        "adhoc_filters": [],
    }

    if draft["viz_type"] == CHART_TYPES["big_number"]:
        params.update({"metric": draft["metric"]})
    elif draft["viz_type"] == CHART_TYPES["table"]:
        params.update({"all_columns": [draft["time_column"], draft["dimension"]], "metrics": [draft["metric"]]})
    elif draft["viz_type"] == CHART_TYPES["line"]:
        params.update(
            {
                "granularity_sqla": draft["time_column"],
                "metrics": [draft["metric"]],
                "groupby": [draft["dimension"]],
            }
        )
    else:
        params.update(
            {
                "x_axis": draft["dimension"],
                "metrics": [draft["metric"]],
                "groupby": [],
                "columns": [],
                "sort_by_metric": True,
                "order_desc": True,
            }
        )

    return params


def build_response(prompt, plan, provider):
    draft = normalize_plan(plan)
    return {
        "prompt": prompt,
        "provider": provider,
        **draft,
        "superset_params": to_superset_params(draft),
    }
