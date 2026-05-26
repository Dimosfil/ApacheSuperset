-- Dataset target: v_production_hourly
-- Use these expressions as Superset metrics if automatic import is not enabled.

-- Total output
sum(actual_units)

-- Good output
sum(good_units)

-- Plan completion
sum(actual_units)::numeric / nullif(sum(planned_units), 0)

-- Scrap rate
sum(scrap_units)::numeric / nullif(sum(actual_units), 0)

-- Availability
sum(runtime_minutes)::numeric / nullif(count(*) * 60, 0)

-- Performance
sum(actual_units)::numeric / nullif(sum(target_units_per_hour), 0)

-- Quality
sum(good_units)::numeric / nullif(sum(actual_units), 0)

-- OEE
(sum(runtime_minutes)::numeric / nullif(count(*) * 60, 0))
  * (sum(actual_units)::numeric / nullif(sum(target_units_per_hour), 0))
  * (sum(good_units)::numeric / nullif(sum(actual_units), 0))
