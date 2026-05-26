create table if not exists plants (
  plant_id integer primary key,
  plant_name text not null,
  region text not null,
  timezone text not null
);

create table if not exists production_lines (
  line_id integer primary key,
  plant_id integer not null references plants(plant_id),
  line_name text not null,
  product_family text not null,
  target_units_per_hour integer not null
);

create table if not exists equipment (
  equipment_id integer primary key,
  line_id integer not null references production_lines(line_id),
  equipment_name text not null,
  equipment_type text not null,
  criticality text not null
);

create table if not exists shifts (
  shift_id integer primary key,
  plant_id integer not null references plants(plant_id),
  shift_name text not null,
  starts_at time not null,
  ends_at time not null
);

create table if not exists production_events (
  event_id bigserial primary key,
  event_ts timestamptz not null,
  plant_id integer not null references plants(plant_id),
  line_id integer not null references production_lines(line_id),
  shift_id integer not null references shifts(shift_id),
  product_sku text not null,
  planned_units integer not null,
  actual_units integer not null,
  good_units integer not null,
  scrap_units integer not null,
  runtime_minutes numeric(6, 2) not null
);

create table if not exists downtime_events (
  downtime_id bigserial primary key,
  started_at timestamptz not null,
  ended_at timestamptz not null,
  plant_id integer not null references plants(plant_id),
  line_id integer not null references production_lines(line_id),
  equipment_id integer not null references equipment(equipment_id),
  reason_category text not null,
  reason_detail text not null,
  is_planned boolean not null
);

create table if not exists quality_checks (
  check_id bigserial primary key,
  checked_at timestamptz not null,
  plant_id integer not null references plants(plant_id),
  line_id integer not null references production_lines(line_id),
  product_sku text not null,
  batch_id text not null,
  defect_count integer not null,
  sample_size integer not null,
  passed boolean not null
);

create table if not exists maintenance_orders (
  order_id bigserial primary key,
  created_at timestamptz not null,
  closed_at timestamptz,
  plant_id integer not null references plants(plant_id),
  equipment_id integer not null references equipment(equipment_id),
  priority text not null,
  status text not null,
  description text not null
);

create or replace view v_production_hourly as
select
  pe.event_ts,
  p.plant_name,
  p.region,
  pl.line_name,
  pl.product_family,
  pl.target_units_per_hour,
  s.shift_name,
  pe.product_sku,
  pe.planned_units,
  pe.actual_units,
  pe.good_units,
  pe.scrap_units,
  pe.runtime_minutes,
  pe.runtime_minutes / 60.0 as runtime_hours,
  pe.actual_units::numeric / nullif(pe.planned_units, 0) as plan_completion,
  pe.scrap_units::numeric / nullif(pe.actual_units, 0) as scrap_rate,
  pe.good_units::numeric / nullif(pe.actual_units, 0) as quality,
  pe.runtime_minutes::numeric / 60.0 as availability,
  pe.actual_units::numeric / nullif(pl.target_units_per_hour, 0) as performance,
  (pe.runtime_minutes::numeric / 60.0)
    * (pe.actual_units::numeric / nullif(pl.target_units_per_hour, 0))
    * (pe.good_units::numeric / nullif(pe.actual_units, 0)) as oee
from production_events pe
join plants p on p.plant_id = pe.plant_id
join production_lines pl on pl.line_id = pe.line_id
join shifts s on s.shift_id = pe.shift_id;

create index if not exists idx_production_events_ts on production_events(event_ts);
create index if not exists idx_production_events_plant_line on production_events(plant_id, line_id);
create index if not exists idx_downtime_events_started on downtime_events(started_at);
