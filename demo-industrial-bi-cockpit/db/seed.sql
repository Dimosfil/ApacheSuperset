truncate table
  maintenance_orders,
  quality_checks,
  downtime_events,
  production_events,
  equipment,
  shifts,
  production_lines,
  plants
restart identity cascade;

insert into plants (plant_id, plant_name, region, timezone)
values
  (1, 'North Plant', 'North-West', 'Europe/Moscow'),
  (2, 'Volga Plant', 'Volga', 'Europe/Moscow'),
  (3, 'Ural Plant', 'Ural', 'Asia/Yekaterinburg'),
  (4, 'Siberia Plant', 'Siberia', 'Asia/Novosibirsk'),
  (5, 'South Plant', 'South', 'Europe/Moscow');

insert into production_lines (line_id, plant_id, line_name, product_family, target_units_per_hour)
select
  row_number() over (order by p.plant_id, lf.line_no) as line_id,
  p.plant_id,
  replace(p.plant_name, ' Plant', '') || ' ' || lf.product_family || ' ' || lf.line_no,
  lf.product_family,
  lf.base_target + p.plant_id * 7 + lf.line_no * 5
from plants p
cross join (
  values
    (1, 'Assembly', 104),
    (2, 'Packaging', 132),
    (3, 'Welding', 86)
) as lf(line_no, product_family, base_target);

insert into equipment (equipment_id, line_id, equipment_name, equipment_type, criticality)
select
  row_number() over (order by pl.line_id, et.equipment_no) as equipment_id,
  pl.line_id,
  et.equipment_type || ' ' || pl.plant_id || '-' || (((pl.line_id - 1) % 3) + 1),
  et.equipment_type,
  et.criticality
from production_lines pl
cross join (
  values
    (1, 'Press', 'high'),
    (2, 'Robot Cell', 'high'),
    (3, 'Conveyor', 'medium'),
    (4, 'Vision Camera', 'medium')
) as et(equipment_no, equipment_type, criticality);

insert into shifts (shift_id, plant_id, shift_name, starts_at, ends_at)
select plant_id * 10 + shift_no, plant_id, shift_name, starts_at::time, ends_at::time
from plants
cross join (
  values
    (1, 'Day', '08:00', '16:00'),
    (2, 'Evening', '16:00', '00:00'),
    (3, 'Night', '00:00', '08:00')
) as shift_template(shift_no, shift_name, starts_at, ends_at);

insert into production_events (
  event_ts,
  plant_id,
  line_id,
  shift_id,
  product_sku,
  planned_units,
  actual_units,
  good_units,
  scrap_units,
  runtime_minutes
)
with hourly as (
  select
    pl.*,
    gs.event_ts,
    extract(day from gs.event_ts)::int as day_no,
    extract(hour from gs.event_ts)::int as hour_no,
    extract(isodow from gs.event_ts)::int as dow_no
  from production_lines pl
  cross join generate_series(
    date_trunc('hour', now() - interval '180 days'),
    date_trunc('hour', now()),
    interval '1 hour'
  ) as gs(event_ts)
),
scored as (
  select
    *,
    case
      when hour_no between 8 and 15 then plant_id * 10 + 1
      when hour_no between 16 and 23 then plant_id * 10 + 2
      else plant_id * 10 + 3
    end as shift_id,
    case when hour_no < 8 then 0.88 else 1.0 end
      * case when dow_no in (6, 7) then 0.93 else 1.0 end
      * case when day_no % 17 = 0 and plant_id = 2 then 0.55 else 1.0 end
      * case when day_no between 8 and 13 and plant_id = 4 and product_family = 'Welding' then 0.68 else 1.0 end
      * case when day_no % 29 = 0 and line_id % 5 = 0 then 0.72 else 1.0 end as output_factor,
    0.012
      + ((hour_no + line_id) % 9) / 250.0
      + case when day_no % 23 = 0 and product_family = 'Assembly' then 0.06 else 0 end
      + case when day_no between 8 and 13 and plant_id = 4 and product_family = 'Welding' then 0.045 else 0 end as scrap_rate
  from hourly
)
select
  event_ts,
  plant_id,
  line_id,
  shift_id,
  ('SKU-' || chr(65 + ((line_id + day_no) % 8)) || (100 + line_id * 10)) as product_sku,
  target_units_per_hour as planned_units,
  actual_units,
  greatest(0, actual_units - scrap_units) as good_units,
  scrap_units,
  runtime_minutes
from (
  select
    *,
    greatest(
      0,
      (target_units_per_hour * output_factor * (0.82 + ((hour_no + line_id) % 9) / 30.0))::int
    ) as actual_units,
    least(
      greatest(
        0,
        (target_units_per_hour * output_factor * (0.82 + ((hour_no + line_id) % 9) / 30.0))::int
      ),
      greatest(0, (target_units_per_hour * scrap_rate)::int)
    ) as scrap_units,
    (
      52
      + ((hour_no + line_id) % 8)
      - case when output_factor < 0.8 then 16 else 0 end
    )::numeric(6, 2) as runtime_minutes
  from scored
) as calculated;

insert into downtime_events (
  started_at,
  ended_at,
  plant_id,
  line_id,
  equipment_id,
  reason_category,
  reason_detail,
  is_planned
)
select
  date_trunc('hour', now() - interval '180 days') + (n || ' hours')::interval + interval '15 minutes',
  date_trunc('hour', now() - interval '180 days') + (n || ' hours')::interval
    + ((20 + (n % 75)) || ' minutes')::interval,
  pl.plant_id,
  pl.line_id,
  e.equipment_id,
  reason.reason_category,
  reason.reason_detail,
  reason.is_planned
from generate_series(1, 4320, 7) as seq(n)
join production_lines pl on pl.line_id = ((seq.n % 15) + 1)
join equipment e on e.line_id = pl.line_id and e.equipment_id = (
  select min(e2.equipment_id) + (seq.n % 4)
  from equipment e2
  where e2.line_id = pl.line_id
)
join lateral (
  select *
  from (
    values
      (0, 'Maintenance', 'planned inspection', true),
      (1, 'Material', 'late material supply', false),
      (2, 'Equipment', 'press vibration alarm', false),
      (3, 'Equipment', 'conveyor jam', false),
      (4, 'Quality', 'batch rework', false),
      (5, 'Changeover', 'product changeover', true),
      (6, 'Energy', 'compressed air pressure drop', false),
      (7, 'Staffing', 'operator shortage', false),
      (8, 'IT', 'scanner integration outage', false)
  ) as r(reason_no, reason_category, reason_detail, is_planned)
  where r.reason_no = seq.n % 9
) as reason on true;

insert into quality_checks (
  checked_at,
  plant_id,
  line_id,
  product_sku,
  batch_id,
  defect_count,
  sample_size,
  passed
)
select
  pe.event_ts + interval '30 minutes',
  pe.plant_id,
  pe.line_id,
  pe.product_sku,
  'B' || to_char(pe.event_ts, 'YYYYMMDDHH24') || '-' || pe.line_id,
  greatest(0, (pe.scrap_units / 2)::int),
  case when pe.line_id % 3 = 0 then 80 else 100 end,
  (pe.scrap_units / 2)::int <= case when pe.line_id % 3 = 0 then 4 else 5 end
from production_events pe
where extract(hour from pe.event_ts) in (2, 10, 18);

insert into maintenance_orders (
  created_at,
  closed_at,
  plant_id,
  equipment_id,
  priority,
  status,
  description
)
select
  date_trunc('day', now() - interval '180 days') + (n || ' days')::interval + interval '9 hours',
  case when n >= 170 and n % 3 <> 0 then null else date_trunc('day', now() - interval '180 days') + (n || ' days')::interval + interval '17 hours' end,
  pl.plant_id,
  e.equipment_id,
  case n % 4 when 0 then 'critical' when 1 then 'high' when 2 then 'medium' else 'low' end,
  case when n >= 170 and n % 3 <> 0 then case when n % 2 = 0 then 'open' else 'in_progress' end else 'closed' end,
  case n % 6
    when 0 then 'Scheduled maintenance window'
    when 1 then 'Bearing replacement'
    when 2 then 'Vision sensor calibration'
    when 3 then 'Robot arm preventive service'
    when 4 then 'Conveyor belt alignment'
    else 'Safety interlock inspection'
  end
from generate_series(0, 179, 10) as seq(n)
join production_lines pl on true
join equipment e on e.line_id = pl.line_id and e.equipment_id = (
  select min(e2.equipment_id) + (seq.n % 4)
  from equipment e2
  where e2.line_id = pl.line_id
);
