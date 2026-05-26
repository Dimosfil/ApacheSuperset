# Data Model

## Entities

### plants

Industrial sites.

Columns:

- `plant_id`
- `plant_name`
- `region`
- `timezone`

### production_lines

Lines inside plants.

Columns:

- `line_id`
- `plant_id`
- `line_name`
- `product_family`
- `target_units_per_hour`

### equipment

Machines or equipment groups.

Columns:

- `equipment_id`
- `line_id`
- `equipment_name`
- `equipment_type`
- `criticality`

### shifts

Operational shifts.

Columns:

- `shift_id`
- `plant_id`
- `shift_name`
- `starts_at`
- `ends_at`

### production_events

Aggregated production facts by hour, line, and shift.

Columns:

- `event_ts`
- `plant_id`
- `line_id`
- `shift_id`
- `product_sku`
- `planned_units`
- `actual_units`
- `good_units`
- `scrap_units`
- `runtime_minutes`

### downtime_events

Machine downtime intervals.

Columns:

- `downtime_id`
- `started_at`
- `ended_at`
- `plant_id`
- `line_id`
- `equipment_id`
- `reason_category`
- `reason_detail`
- `is_planned`

### quality_checks

Batch quality measurements.

Columns:

- `check_id`
- `checked_at`
- `plant_id`
- `line_id`
- `product_sku`
- `batch_id`
- `defect_count`
- `sample_size`
- `passed`

### maintenance_orders

Maintenance events.

Columns:

- `order_id`
- `created_at`
- `closed_at`
- `plant_id`
- `equipment_id`
- `priority`
- `status`
- `description`

## Core Metrics

### Plan Completion

```sql
sum(actual_units) / nullif(sum(planned_units), 0)
```

### Scrap Rate

```sql
sum(scrap_units) / nullif(sum(actual_units), 0)
```

### Availability

```sql
sum(runtime_minutes) / nullif(count(distinct event_ts) * 60, 0)
```

### Quality

```sql
sum(good_units) / nullif(sum(actual_units), 0)
```

### Performance

```sql
sum(actual_units) / nullif(sum(target_units_per_hour), 0)
```

### OEE

```sql
availability * performance * quality
```

In implementation, OEE should be expressed through Superset metrics or a
virtual dataset so it is visible in the semantic layer.
