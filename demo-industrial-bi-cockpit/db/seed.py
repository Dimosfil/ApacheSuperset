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

random.seed(42)


PLANTS = [
    (1, "North Plant", "North-West", "Europe/Moscow"),
    (2, "Volga Plant", "Volga", "Europe/Moscow"),
    (3, "Ural Plant", "Ural", "Asia/Yekaterinburg"),
]

PRODUCTS = ["SKU-A100", "SKU-B220", "SKU-C310", "SKU-D480"]
REASONS = [
    ("Maintenance", "planned inspection", True),
    ("Material", "late material supply", False),
    ("Equipment", "press vibration alarm", False),
    ("Equipment", "conveyor jam", False),
    ("Quality", "batch rework", False),
    ("Changeover", "product changeover", True),
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

    for plant_id, _, _, _ in PLANTS:
        for idx, family in enumerate(["Assembly", "Packaging"], start=1):
            target = 90 + plant_id * 8 + idx * 12
            lines.append((line_id, plant_id, f"Line {plant_id}-{idx}", family, target))
            equipment.append((equipment_id, line_id, f"Press {plant_id}-{idx}", "Press", "high"))
            equipment_id += 1
            equipment.append((equipment_id, line_id, f"Conveyor {plant_id}-{idx}", "Conveyor", "medium"))
            equipment_id += 1
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
    start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) - timedelta(days=90)
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

    for day in range(90):
        for line_id, plant_id, _, family, target in lines:
            for hour in range(24):
                ts = start + timedelta(days=day, hours=hour)
                shift = shifts_by_plant[plant_id][0 if 8 <= hour < 16 else 1 if 16 <= hour else 2]
                planned = target
                anomaly = 0.55 if day % 17 == 0 and plant_id == 2 else 1.0
                night_factor = 0.88 if shift[2] == "Night" else 1.0
                actual = max(0, int(planned * random.uniform(0.78, 1.08) * anomaly * night_factor))
                scrap_rate = random.uniform(0.01, 0.055)
                if day % 23 == 0 and family == "Assembly":
                    scrap_rate += 0.06
                scrap = min(actual, int(actual * scrap_rate))
                good = actual - scrap
                runtime = random.uniform(48, 60)
                if anomaly < 1:
                    runtime = random.uniform(30, 48)

                production_rows.append(
                    (ts, plant_id, line_id, shift[0], random.choice(PRODUCTS), planned, actual, good, scrap, round(runtime, 2))
                )

                if random.random() < 0.055 or anomaly < 1 and random.random() < 0.2:
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

            if day % 14 == 0:
                equipment_id = random.choice(equipment_by_line[line_id])[0]
                created = start + timedelta(days=day, hours=9)
                maintenance_rows.append(
                    (
                        created,
                        created + timedelta(hours=random.randint(2, 20)),
                        plant_id,
                        equipment_id,
                        random.choice(["low", "medium", "high"]),
                        "closed",
                        "Scheduled maintenance window",
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


def main():
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            reset_tables(cur)
            lines, equipment, shifts = seed_dimensions(cur)
            seed_facts(cur, lines, equipment, shifts)
        conn.commit()
    print("Seeded Industrial BI demo data.")


if __name__ == "__main__":
    main()
