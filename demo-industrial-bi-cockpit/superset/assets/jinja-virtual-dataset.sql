-- Sprint 1 reference query. Sprint 2 can wire this into a role-aware dataset.

select
  event_ts,
  plant_name,
  region,
  line_name,
  product_family,
  shift_name,
  product_sku,
  planned_units,
  actual_units,
  good_units,
  scrap_units,
  runtime_minutes,
  plan_completion,
  scrap_rate,
  availability,
  performance,
  quality,
  oee
from v_production_hourly
where 1 = 1
{% if filter_values('plant_name') %}
  and plant_name in {{ filter_values('plant_name') | where_in }}
{% endif %}
{% if filter_values('line_name') %}
  and line_name in {{ filter_values('line_name') | where_in }}
{% endif %}
