# Dashboard MVP

Dashboard name: `Industrial BI Cockpit`

Dataset: `v_production_hourly`

## Native Filters

- Date range: `event_ts`
- Plant: `plant_name`
- Line: `line_name`
- Shift: `shift_name`
- Product family: `product_family`

## Charts

### KPI: OEE

Chart type: Big Number

Metric:

```sql
(sum(runtime_minutes)::numeric / nullif(count(*) * 60, 0))
  * (sum(actual_units)::numeric / nullif(sum(target_units_per_hour), 0))
  * (sum(good_units)::numeric / nullif(sum(actual_units), 0))
```

### KPI: Output

Chart type: Big Number

Metric:

```sql
sum(actual_units)
```

### KPI: Downtime Hours

Dataset: `downtime_events`

Metric:

```sql
sum(extract(epoch from ended_at - started_at)) / 3600
```

### KPI: Scrap Rate

Chart type: Big Number

Metric:

```sql
sum(scrap_units)::numeric / nullif(sum(actual_units), 0)
```

### Plan/Fact Trend

Chart type: Time-series Line Chart

Time column: `event_ts`

Metrics:

- `sum(planned_units)`
- `sum(actual_units)`

Group by:

- `plant_name` or `line_name`

### Downtime By Reason

Dataset: `downtime_events`

Chart type: Bar Chart

Dimension:

- `reason_category`

Metric:

```sql
sum(extract(epoch from ended_at - started_at)) / 3600
```

### Line And Shift Heatmap

Chart type: Pivot Table or Heatmap

Rows:

- `line_name`

Columns:

- `shift_name`

Metric:

```sql
avg(oee)
```

### Incident Detail Table

Dataset: `downtime_events`

Chart type: Table

Columns:

- `started_at`
- `ended_at`
- `plant_id`
- `line_id`
- `equipment_id`
- `reason_category`
- `reason_detail`
- `is_planned`

## Layout

```text
[ Date | Plant | Line | Shift | Product family ]

[ OEE ] [ Output ] [ Downtime hours ] [ Scrap rate ]

[ Plan/Fact trend                         ]
[ Downtime by reason ] [ Line/Shift heatmap ]
[ Incident detail table                   ]
```

## Sprint 1 Acceptance

- The dashboard can be created from the documented datasets and metrics.
- All chart definitions are backed by seeded data.
- The native filters have a clear target column.
- The layout is demo-friendly and can be rebuilt quickly if exported assets
  differ across Superset versions.
