insert into plants (plant_id, plant_name, region, timezone)
values
  (1, 'North Plant', 'North-West', 'Europe/Moscow'),
  (2, 'Volga Plant', 'Volga', 'Europe/Moscow'),
  (3, 'Ural Plant', 'Ural', 'Asia/Yekaterinburg')
on conflict do nothing;

insert into production_lines (line_id, plant_id, line_name, product_family, target_units_per_hour)
values
  (1, 1, 'Line 1-1', 'Assembly', 110),
  (2, 1, 'Line 1-2', 'Packaging', 124),
  (3, 2, 'Line 2-1', 'Assembly', 118),
  (4, 2, 'Line 2-2', 'Packaging', 132),
  (5, 3, 'Line 3-1', 'Assembly', 126),
  (6, 3, 'Line 3-2', 'Packaging', 140)
on conflict do nothing;

insert into equipment (equipment_id, line_id, equipment_name, equipment_type, criticality)
values
  (1, 1, 'Press 1-1', 'Press', 'high'),
  (2, 1, 'Conveyor 1-1', 'Conveyor', 'medium'),
  (3, 2, 'Press 1-2', 'Press', 'high'),
  (4, 2, 'Conveyor 1-2', 'Conveyor', 'medium'),
  (5, 3, 'Press 2-1', 'Press', 'high'),
  (6, 3, 'Conveyor 2-1', 'Conveyor', 'medium'),
  (7, 4, 'Press 2-2', 'Press', 'high'),
  (8, 4, 'Conveyor 2-2', 'Conveyor', 'medium'),
  (9, 5, 'Press 3-1', 'Press', 'high'),
  (10, 5, 'Conveyor 3-1', 'Conveyor', 'medium'),
  (11, 6, 'Press 3-2', 'Press', 'high'),
  (12, 6, 'Conveyor 3-2', 'Conveyor', 'medium')
on conflict do nothing;

insert into shifts (shift_id, plant_id, shift_name, starts_at, ends_at)
select plant_id * 10 + shift_no, plant_id, shift_name, starts_at::time, ends_at::time
from plants
cross join (
  values
    (1, 'Day', '08:00', '16:00'),
    (2, 'Evening', '16:00', '00:00'),
    (3, 'Night', '00:00', '08:00')
) as shift_template(shift_no, shift_name, starts_at, ends_at)
on conflict do nothing;

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
select
  gs.event_ts,
  pl.plant_id,
  pl.line_id,
  case
    when extract(hour from gs.event_ts) between 8 and 15 then pl.plant_id * 10 + 1
    when extract(hour from gs.event_ts) between 16 and 23 then pl.plant_id * 10 + 2
    else pl.plant_id * 10 + 3
  end as shift_id,
  ('SKU-' || chr(65 + ((pl.line_id + extract(day from gs.event_ts)::int) % 4)) || (100 + pl.line_id * 10)) as product_sku,
  pl.target_units_per_hour as planned_units,
  greatest(
    0,
    (
      pl.target_units_per_hour
      * case when extract(hour from gs.event_ts) < 8 then 0.88 else 1.0 end
      * case when extract(day from gs.event_ts)::int % 17 = 0 and pl.plant_id = 2 then 0.58 else 1.0 end
      * (0.82 + ((extract(hour from gs.event_ts)::int + pl.line_id) % 9) / 30.0)
    )::int
  ) as actual_units,
  greatest(
    0,
    (
      pl.target_units_per_hour
      * case when extract(hour from gs.event_ts) < 8 then 0.88 else 1.0 end
      * case when extract(day from gs.event_ts)::int % 17 = 0 and pl.plant_id = 2 then 0.58 else 1.0 end
      * (0.82 + ((extract(hour from gs.event_ts)::int + pl.line_id) % 9) / 30.0)
      * (0.94 - case when extract(day from gs.event_ts)::int % 23 = 0 and pl.product_family = 'Assembly' then 0.07 else 0 end)
    )::int
  ) as good_units,
  greatest(
    0,
    (
      pl.target_units_per_hour
      * case when extract(day from gs.event_ts)::int % 23 = 0 and pl.product_family = 'Assembly' then 0.09 else 0.025 end
    )::int
  ) as scrap_units,
  (
    52
    + ((extract(hour from gs.event_ts)::int + pl.line_id) % 8)
    - case when extract(day from gs.event_ts)::int % 17 = 0 and pl.plant_id = 2 then 16 else 0 end
  )::numeric(6, 2) as runtime_minutes
from production_lines pl
cross join generate_series(
  date_trunc('hour', now() - interval '90 days'),
  date_trunc('hour', now()),
  interval '1 hour'
) as gs(event_ts);

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
  date_trunc('hour', now() - interval '90 days') + (n || ' hours')::interval + interval '15 minutes',
  date_trunc('hour', now() - interval '90 days') + (n || ' hours')::interval
    + ((20 + (n % 75)) || ' minutes')::interval,
  pl.plant_id,
  pl.line_id,
  e.equipment_id,
  case n % 6
    when 0 then 'Maintenance'
    when 1 then 'Material'
    when 2 then 'Equipment'
    when 3 then 'Equipment'
    when 4 then 'Quality'
    else 'Changeover'
  end,
  case n % 6
    when 0 then 'planned inspection'
    when 1 then 'late material supply'
    when 2 then 'press vibration alarm'
    when 3 then 'conveyor jam'
    when 4 then 'batch rework'
    else 'product changeover'
  end,
  n % 6 in (0, 5)
from generate_series(1, 2160, 13) as seq(n)
join production_lines pl on pl.line_id = ((seq.n % 6) + 1)
join equipment e on e.line_id = pl.line_id and e.equipment_id = (
  select min(e2.equipment_id)
  from equipment e2
  where e2.line_id = pl.line_id
);

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
  100,
  (pe.scrap_units / 2)::int <= 5
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
  date_trunc('day', now() - interval '90 days') + (n || ' days')::interval + interval '9 hours',
  date_trunc('day', now() - interval '90 days') + (n || ' days')::interval + interval '17 hours',
  pl.plant_id,
  e.equipment_id,
  case n % 3 when 0 then 'high' when 1 then 'medium' else 'low' end,
  'closed',
  'Scheduled maintenance window'
from generate_series(0, 89, 14) as seq(n)
join production_lines pl on pl.line_id = ((seq.n % 6) + 1)
join equipment e on e.line_id = pl.line_id and e.equipment_id = (
  select min(e2.equipment_id)
  from equipment e2
  where e2.line_id = pl.line_id
);
