import os
import random
from datetime import datetime, timedelta, timezone

import psycopg


DSN = (
    f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
    f"port={os.getenv('POSTGRES_PORT', '5432')} "
    f"dbname={os.getenv('POSTGRES_DB', 'industrial_bi')} "
    f"user={os.getenv('POSTGRES_USER', 'industrial')} "
    f"password={os.getenv('POSTGRES_PASSWORD', 'industrial')}"
)

random.seed(int(os.getenv("SEED_RANDOM", "42")))
DAYS_TO_SEED = int(os.getenv("SEED_DAYS", "180"))


PLANTS = [
    (1, "North Plant", "North-West", "Europe/Moscow"),
    (2, "Volga Plant", "Volga", "Europe/Moscow"),
    (3, "Ural Plant", "Ural", "Asia/Yekaterinburg"),
    (4, "Siberia Plant", "Siberia", "Asia/Novosibirsk"),
    (5, "South Plant", "South", "Europe/Moscow"),
]

LINE_FAMILIES = [
    ("Assembly", 104),
    ("Packaging", 132),
    ("Welding", 86),
]

PRODUCTS = [
    "SKU-A100",
    "SKU-A120",
    "SKU-B220",
    "SKU-B260",
    "SKU-C310",
    "SKU-C355",
    "SKU-D480",
    "SKU-D520",
    "SKU-E610",
    "SKU-F730",
    "SKU-G840",
    "SKU-H900",
]

REASONS = [
    ("Maintenance", "planned inspection", True),
    ("Material", "late material supply", False),
    ("Equipment", "press vibration alarm", False),
    ("Equipment", "conveyor jam", False),
    ("Quality", "batch rework", False),
    ("Changeover", "product changeover", True),
    ("Energy", "compressed air pressure drop", False),
    ("Staffing", "operator shortage", False),
    ("IT", "scanner integration outage", False),
]

MAINTENANCE_DESCRIPTIONS = [
    "Scheduled maintenance window",
    "Bearing replacement",
    "Vision sensor calibration",
    "Robot arm preventive service",
    "Conveyor belt alignment",
    "Safety interlock inspection",
]


def execute_many(cur, sql, rows):
    if rows:
        cur.executemany(sql, rows)


def reset_tables(cur):
    cur.execute(
        """
        truncate table
          maintenance_orders,
          quality_checks,
          downtime_events,
          production_events,
          equipment,
          shifts,
          production_lines,
          plants
        restart identity cascade
        """
    )


def seed_dimensions(cur):
    execute_many(
        cur,
        "insert into plants (plant_id, plant_name, region, timezone) values (%s, %s, %s, %s)",
        PLANTS,
    )

    lines = []
    equipment = []
    shifts = []
    line_id = 1
    equipment_id = 1

    for plant_id, plant_name, _, _ in PLANTS:
        plant_slug = plant_name.replace(" Plant", "")
        for idx, (family, base_target) in enumerate(LINE_FAMILIES, start=1):
            target = base_target + plant_id * 7 + idx * 5
            line_name = f"{plant_slug} {family} {idx}"
            lines.append((line_id, plant_id, line_name, family, target))
            line_suffix = f"{plant_id}-{idx}"
            equipment.extend(
                [
                    (equipment_id, line_id, f"Press {line_suffix}", "Press", "high"),
                    (equipment_id + 1, line_id, f"Robot Cell {line_suffix}", "Robot", "high"),
                    (equipment_id + 2, line_id, f"Conveyor {line_suffix}", "Conveyor", "medium"),
                    (equipment_id + 3, line_id, f"Vision Camera {line_suffix}", "Quality Gate", "medium"),
                ]
            )
            equipment_id += 4
            line_id += 1

        shifts.extend(
            [
                (plant_id * 10 + 1, plant_id, "Day", "08:00", "16:00"),
                (plant_id * 10 + 2, plant_id, "Evening", "16:00", "00:00"),
                (plant_id * 10 + 3, plant_id, "Night", "00:00", "08:00"),
            ]
        )

    execute_many(
        cur,
        """
        insert into production_lines
          (line_id, plant_id, line_name, product_family, target_units_per_hour)
        values (%s, %s, %s, %s, %s)
        """,
        lines,
    )
    execute_many(
        cur,
        """
        insert into equipment
          (equipment_id, line_id, equipment_name, equipment_type, criticality)
        values (%s, %s, %s, %s, %s)
        """,
        equipment,
    )
    execute_many(
        cur,
        """
        insert into shifts
          (shift_id, plant_id, shift_name, starts_at, ends_at)
        values (%s, %s, %s, %s, %s)
        """,
        shifts,
    )
    return lines, equipment, shifts


def seed_facts(cur, lines, equipment, shifts):
    start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) - timedelta(days=DAYS_TO_SEED)
    production_rows = []
    downtime_rows = []
    quality_rows = []
    maintenance_rows = []

    equipment_by_line = {}
    for item in equipment:
        equipment_by_line.setdefault(item[1], []).append(item)

    shifts_by_plant = {}
    for shift in shifts:
        shifts_by_plant.setdefault(shift[1], []).append(shift)

    for day in range(DAYS_TO_SEED):
        for line_id, plant_id, _, family, target in lines:
            for hour in range(24):
                ts = start + timedelta(days=day, hours=hour)
                shift = shifts_by_plant[plant_id][0 if 8 <= hour < 16 else 1 if 16 <= hour else 2]
                planned = target
                anomaly = 1.0
                if day % 17 == 0 and plant_id == 2:
                    anomaly *= 0.55
                if 38 <= day <= 43 and plant_id == 4 and family == "Welding":
                    anomaly *= 0.68
                if day % 29 == 0 and line_id % 5 == 0:
                    anomaly *= 0.72
                night_factor = 0.88 if shift[2] == "Night" else 1.0
                weekday_factor = 0.93 if ts.weekday() >= 5 else 1.0
                actual = max(0, int(planned * random.uniform(0.78, 1.1) * anomaly * night_factor * weekday_factor))
                scrap_rate = random.uniform(0.01, 0.055)
                if day % 23 == 0 and family == "Assembly":
                    scrap_rate += 0.06
                if 38 <= day <= 43 and plant_id == 4 and family == "Welding":
                    scrap_rate += 0.045
                scrap = min(actual, int(actual * scrap_rate))
                good = actual - scrap
                runtime = random.uniform(48, 60)
                if anomaly < 1:
                    runtime = random.uniform(30, 48)

                production_rows.append(
                    (ts, plant_id, line_id, shift[0], random.choice(PRODUCTS), planned, actual, good, scrap, round(runtime, 2))
                )

                if random.random() < 0.07 or anomaly < 1 and random.random() < 0.25:
                    reason_category, reason_detail, is_planned = random.choice(REASONS)
                    duration = random.randint(12, 95 if not is_planned else 45)
                    equipment_id = random.choice(equipment_by_line[line_id])[0]
                    downtime_rows.append(
                        (
                            ts + timedelta(minutes=random.randint(0, 40)),
                            ts + timedelta(minutes=random.randint(41, 59) + duration),
                            plant_id,
                            line_id,
                            equipment_id,
                            reason_category,
                            reason_detail,
                            is_planned,
                        )
                    )

                if hour in (10, 18, 2):
                    sample_size = random.choice([50, 80, 100])
                    defects = min(sample_size, int(sample_size * scrap_rate * random.uniform(0.5, 1.4)))
                    quality_rows.append(
                        (
                            ts + timedelta(minutes=30),
                            plant_id,
                            line_id,
                            random.choice(PRODUCTS),
                            f"B{day:03d}-{line_id}-{hour}",
                            defects,
                            sample_size,
                            defects / sample_size <= 0.05,
                        )
                    )

            if day % 10 == 0:
                equipment_id = random.choice(equipment_by_line[line_id])[0]
                created = start + timedelta(days=day, hours=9)
                is_recent = day >= DAYS_TO_SEED - 12
                status = random.choice(["open", "in_progress"]) if is_recent and random.random() < 0.35 else "closed"
                closed = None if status != "closed" else created + timedelta(hours=random.randint(2, 20))
                maintenance_rows.append(
                    (
                        created,
                        closed,
                        plant_id,
                        equipment_id,
                        random.choice(["low", "medium", "high", "critical"]),
                        status,
                        random.choice(MAINTENANCE_DESCRIPTIONS),
                    )
                )

    execute_many(
        cur,
        """
        insert into production_events
          (event_ts, plant_id, line_id, shift_id, product_sku, planned_units,
           actual_units, good_units, scrap_units, runtime_minutes)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        production_rows,
    )
    execute_many(
        cur,
        """
        insert into downtime_events
          (started_at, ended_at, plant_id, line_id, equipment_id, reason_category,
           reason_detail, is_planned)
        values (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        downtime_rows,
    )
    execute_many(
        cur,
        """
        insert into quality_checks
          (checked_at, plant_id, line_id, product_sku, batch_id, defect_count,
           sample_size, passed)
        values (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        quality_rows,
    )
    execute_many(
        cur,
        """
        insert into maintenance_orders
          (created_at, closed_at, plant_id, equipment_id, priority, status, description)
        values (%s, %s, %s, %s, %s, %s, %s)
        """,
        maintenance_rows,
    )
    return {
        "production_events": len(production_rows),
        "downtime_events": len(downtime_rows),
        "quality_checks": len(quality_rows),
        "maintenance_orders": len(maintenance_rows),
    }


def main():
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            reset_tables(cur)
            lines, equipment, shifts = seed_dimensions(cur)
            fact_counts = seed_facts(cur, lines, equipment, shifts)
        conn.commit()
    print(
        "Seeded Industrial BI demo data: "
        f"{len(PLANTS)} plants, {len(lines)} lines, {len(equipment)} equipment assets, "
        + ", ".join(f"{name}={count}" for name, count in fact_counts.items())
        + "."
    )


if __name__ == "__main__":
    main()
