"""
Synthetic Railway Maintenance Data Generator
=============================================

Generates synthetic data for the Automatic Railway
Maintenance Block Planning project.

Datasets:
    assets.csv
    asset_history.csv
    train_schedule.csv
    block_windows.csv
    maintenance_tasks.csv
    block_requests.csv
    maintenance_outcomes.csv

Random seed:
    42
"""

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42
rng = random.Random(SEED)

OUTPUT_DIR = Path("data") / "synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = date(2026, 9, 1)
END_DATE = date(2026, 9, 30)

NUM_CORRIDORS = 20
NUM_ASSETS = 500
NUM_MAINTENANCE_TASKS = 5000
NUM_TRAINS = 10000
NUM_BLOCKS = 3000
NUM_BLOCK_REQUESTS = 5000
NUM_OUTCOMES = 5000

DEPARTMENTS = [
    "ENGINEERING",
    "S&T",
    "TRD",
]

CORRIDORS = [
    f"C{i:02d}"
    for i in range(1, NUM_CORRIDORS + 1)
]

ASSET_TYPES = {
    "ENGINEERING": [
        "TRACK",
        "BRIDGE",
        "POINT_MACHINE",
    ],
    "S&T": [
        "SIGNAL",
        "RELAY",
        "AXLE_COUNTER",
    ],
    "TRD": [
        "OHE",
        "FEEDER",
        "TRANSFORMER",
    ],
}

MAINTENANCE_TYPES = {
    "ENGINEERING": [
        "PREVENTIVE",
        "CORRECTIVE",
        "INSPECTION",
        "REPAIR",
    ],
    "S&T": [
        "PREVENTIVE",
        "CORRECTIVE",
        "INSPECTION",
        "SIGNAL_REPAIR",
    ],
    "TRD": [
        "PREVENTIVE",
        "CORRECTIVE",
        "INSPECTION",
        "OHE_REPAIR",
    ],
}

DEFECT_TYPES = {
    "ENGINEERING": [
        "RAIL_CRACK",
        "TRACK_GEOMETRY",
        "BALLAST_DEFECT",
        "POINT_DEFECT",
        "STRUCTURAL_DEFECT",
    ],
    "S&T": [
        "SIGNAL_FAILURE",
        "RELAY_FAULT",
        "AXLE_COUNTER_FAULT",
        "CABLE_FAULT",
        "INTERLOCKING_FAULT",
    ],
    "TRD": [
        "OHE_DAMAGE",
        "CONTACT_WIRE_DEFECT",
        "FEEDER_FAULT",
        "INSULATOR_FAILURE",
        "TRANSFORMER_FAULT",
    ],
}

TRAIN_TYPES = [
    "PASSENGER",
    "EXPRESS",
    "SUPERFAST",
    "GOODS",
]

TRAIN_TYPE_WEIGHTS = [
    0.35,
    0.25,
    0.20,
    0.20,
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date(start_date, end_date):
    """Return a random date between two dates."""

    days = (end_date - start_date).days

    return start_date + timedelta(
        days=rng.randint(0, days)
    )


def random_time():
    """Return random minutes since midnight."""

    return rng.randint(0, 1439)


def format_time(minutes):
    """Convert minutes since midnight to HH:MM."""

    minutes = minutes % 1440

    hour = minutes // 60
    minute = minutes % 60

    return f"{hour:02d}:{minute:02d}"


def sigmoid(x):
    """Numerically stable sigmoid."""

    if x >= 0:

        z = math.exp(-x)

        return 1 / (1 + z)

    z = math.exp(x)

    return z / (1 + z)


def clamp(value, low, high):
    """Clamp a value between low and high."""

    return max(
        low,
        min(high, value),
    )


def weighted_choice(items, weights):
    """Weighted random choice."""

    return rng.choices(
        items,
        weights=weights,
        k=1,
    )[0]


def write_csv(
    filename,
    rows,
    fieldnames,
):
    """Write records to CSV."""

    path = OUTPUT_DIR / filename

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(rows)

    print(
        f"Created {path} "
        f"({len(rows):,} rows)"
    )


# ============================================================
# 1. ASSETS
# ============================================================

def generate_assets():

    assets = []

    for i in range(
        1,
        NUM_ASSETS + 1,
    ):

        department = rng.choice(
            DEPARTMENTS
        )

        asset_type = rng.choice(
            ASSET_TYPES[department]
        )

        corridor_id = rng.choice(
            CORRIDORS
        )

        installation_year = rng.randint(
            2005,
            2023,
        )

        age = 2026 - installation_year

        base_condition = (
            0.95
            - age * 0.018
        )

        condition_score = clamp(
            base_condition
            + rng.gauss(0, 0.08),
            0.20,
            1.00,
        )

        criticality = rng.choices(
            [1, 2, 3, 4, 5],
            weights=[
                0.05,
                0.15,
                0.30,
                0.30,
                0.20,
            ],
            k=1,
        )[0]

        location_km = round(
            rng.uniform(0, 250),
            2,
        )

        assets.append({

            "asset_id":
                f"AST-{i:05d}",

            "asset_type":
                asset_type,

            "department":
                department,

            "corridor_id":
                corridor_id,

            "location_km":
                location_km,

            "criticality":
                criticality,

            "installation_year":
                installation_year,

            "condition_score":
                round(
                    condition_score,
                    3,
                ),
        })

    return assets


# ============================================================
# 2. ASSET HISTORY
# ============================================================

def generate_asset_history(assets):

    history = []

    history_id = 1

    for asset in assets:

        for _ in range(4):

            inspection_date = random_date(
                date(2024, 1, 1),
                date(2026, 8, 31),
            )

            condition = clamp(
                asset["condition_score"]
                + rng.gauss(0, 0.10),
                0.10,
                1.00,
            )

            failure_probability = clamp(
                0.02
                + (
                    1
                    - condition
                ) * 0.20
                + asset["criticality"] * 0.01,
                0,
                0.60,
            )

            failure_event = (
                rng.random()
                < failure_probability
            )

            repair_duration = (
                rng.randint(30, 240)
                if failure_event
                else 0
            )

            downtime_hours = round(
                repair_duration / 60,
                2,
            )

            history.append({

                "history_id":
                    f"H-{history_id:06d}",

                "asset_id":
                    asset["asset_id"],

                "inspection_date":
                    inspection_date.isoformat(),

                "condition_score":
                    round(
                        condition,
                        3,
                    ),

                "failure_event":
                    int(failure_event),

                "repair_duration_minutes":
                    repair_duration,

                "downtime_hours":
                    downtime_hours,
            })

            history_id += 1

    return history


# ============================================================
# 3. TRAIN SCHEDULE
# ============================================================

def generate_trains():

    trains = []

    for i in range(
        1,
        NUM_TRAINS + 1,
    ):

        train_type = weighted_choice(
            TRAIN_TYPES,
            TRAIN_TYPE_WEIGHTS,
        )

        corridor_id = rng.choice(
            CORRIDORS
        )

        train_date = random_date(
            START_DATE,
            END_DATE,
        )

        start_minute = random_time()

        if train_type == "GOODS":

            duration = rng.randint(
                25,
                60,
            )

            priority = "MEDIUM"

        elif train_type == "PASSENGER":

            duration = rng.randint(
                10,
                25,
            )

            priority = "HIGH"

        else:

            duration = rng.randint(
                10,
                30,
            )

            priority = "HIGH"

        end_minute = (
            start_minute
            + duration
        )

        trains.append({

            "train_id":
                f"TRN-{i:06d}",

            "train_type":
                train_type,

            "corridor_id":
                corridor_id,

            "date":
                train_date.isoformat(),

            "arrival_time":
                format_time(
                    start_minute
                ),

            "departure_time":
                format_time(
                    end_minute
                ),

            "priority":
                priority,

            "forecast_source":
                (
                    "GOODS_FORECAST"
                    if train_type == "GOODS"
                    else "TIMETABLE"
                ),
        })

    return trains


# ============================================================
# 4. BLOCK WINDOWS
# ============================================================

def generate_blocks():

    blocks = []

    for i in range(
        1,
        NUM_BLOCKS + 1,
    ):

        corridor_id = rng.choice(
            CORRIDORS
        )

        block_date = random_date(
            START_DATE,
            END_DATE,
        )

        start_minute = random_time()

        duration = rng.choice([
            30,
            45,
            60,
            90,
            120,
            150,
            180,
        ])

        end_minute = (
            start_minute
            + duration
        )

        blocks.append({

            "block_id":
                f"BLK-{i:05d}",

            "corridor_id":
                corridor_id,

            "date":
                block_date.isoformat(),

            "start_time":
                format_time(
                    start_minute
                ),

            "end_time":
                format_time(
                    end_minute
                ),

            "duration_minutes":
                duration,

            "availability_status":
                "AVAILABLE",
        })

    return blocks


# ============================================================
# 5. MAINTENANCE TASKS
# ============================================================

def generate_maintenance_tasks(
    assets,
    trains,
):

    tasks = []

    train_density = {
        corridor: 0
        for corridor in CORRIDORS
    }

    for train in trains:

        train_density[
            train["corridor_id"]
        ] += 1

    for i in range(
        1,
        NUM_MAINTENANCE_TASKS + 1,
    ):

        asset = rng.choice(
            assets
        )

        department = asset[
            "department"
        ]

        maintenance_type = rng.choice(
            MAINTENANCE_TYPES[
                department
            ]
        )

        defect_type = rng.choice(
            DEFECT_TYPES[
                department
            ]
        )

        severity = rng.choices(
            [1, 2, 3, 4, 5],
            weights=[
                0.10,
                0.20,
                0.30,
                0.25,
                0.15,
            ],
            k=1,
        )[0]

        overdue_days = max(
            0,
            int(
                rng.gauss(
                    10,
                    12,
                )
            ),
        )

        failure_frequency = clamp(
            rng.random()
            + (
                1
                - asset[
                    "condition_score"
                ]
            ) * 1.5,
            0,
            3,
        )

        safety_impact = clamp(
            0.20
            + severity * 0.10
            + rng.gauss(
                0,
                0.12,
            ),
            0,
            1,
        )

        corridor_density = (
            train_density[
                asset["corridor_id"]
            ]
            / 600
        )

        operational_impact = clamp(
            0.15
            + asset["criticality"] * 0.08
            + corridor_density
            + rng.gauss(
                0,
                0.10,
            ),
            0,
            1,
        )

        base_duration = {

            "PREVENTIVE": 60,

            "CORRECTIVE": 90,

            "INSPECTION": 45,

            "REPAIR": 120,

            "SIGNAL_REPAIR": 90,

            "OHE_REPAIR": 120,

        }.get(
            maintenance_type,
            90,
        )

        estimated_duration = int(
            base_duration
            + severity * 10
            + rng.gauss(
                0,
                15,
            )
        )

        estimated_duration = int(
            clamp(
                estimated_duration,
                30,
                240,
            )
        )

        due_date = random_date(
            START_DATE,
            END_DATE,
        )

        # ====================================================
        # MULTI-FACTOR LATENT PRIORITY MODEL
        # ====================================================

        risk_signal = (

            # Defect / maintenance severity
            0.65 * severity

            # Nonlinear severity effect
            + 0.05 * severity ** 2

            # Asset criticality
            + 0.70 * asset[
                "criticality"
            ]

            # Asset condition
            + 1.20 * (
                1
                - asset[
                    "condition_score"
                ]
            )

            # Maintenance urgency
            + 0.045 * overdue_days

            # Historical failure frequency
            + 0.75 * failure_frequency

            # Safety impact
            + 1.15 * safety_impact

            # Operational impact
            + 1.10 * operational_impact

            # Estimated maintenance duration
            + 0.004 * estimated_duration

            # Severity × safety interaction
            + 0.25
            * severity
            * safety_impact

            # Criticality × poor condition
            + 0.30
            * asset[
                "criticality"
            ]
            * (
                1
                - asset[
                    "condition_score"
                ]
            )

            # Operational impact × duration
            + 0.20
            * operational_impact
            * (
                estimated_duration
                / 120
            )

            # Random uncertainty
            + rng.gauss(
                0,
                0.65,
            )
        )

        # ====================================================
        # CALIBRATED PRIORITY SCORE
        # ====================================================

        priority_score = (
            100
            * sigmoid(
                (
                    risk_signal
                    - 8.5
                )
                / 2.4
            )
        )

        priority_score = clamp(
            priority_score,
            0,
            100,
        )

        if priority_score >= 80:

            priority_class = "CRITICAL"

        elif priority_score >= 60:

            priority_class = "HIGH"

        elif priority_score >= 40:

            priority_class = "MEDIUM"

        else:

            priority_class = "LOW"

        status = rng.choices(
            [
                "OPEN",
                "OVERDUE",
                "SCHEDULED",
            ],
            weights=[
                0.45,
                0.35,
                0.20,
            ],
            k=1,
        )[0]

        tasks.append({

            "task_id":
                f"MT-{i:06d}",

            "asset_id":
                asset["asset_id"],

            "department":
                department,

            "corridor_id":
                asset["corridor_id"],

            "maintenance_type":
                maintenance_type,

            "defect_type":
                defect_type,

            "severity":
                severity,

            "criticality":
                asset["criticality"],

            "condition_score":
                round(
                    asset[
                        "condition_score"
                    ],
                    3,
                ),

            "overdue_days":
                overdue_days,

            "failure_frequency":
                round(
                    failure_frequency,
                    3,
                ),

            "safety_impact":
                round(
                    safety_impact,
                    3,
                ),

            "operational_impact":
                round(
                    operational_impact,
                    3,
                ),

            "estimated_duration_minutes":
                estimated_duration,

            "due_date":
                due_date.isoformat(),

            "status":
                status,

            "priority_score":
                round(
                    priority_score,
                    2,
                ),

            "priority_class":
                priority_class,
        })

    return tasks


# ============================================================
# 6. BLOCK REQUESTS
# ============================================================

def generate_block_requests(
    tasks,
    blocks,
):

    requests = []

    for i in range(
        1,
        NUM_BLOCK_REQUESTS + 1,
    ):

        task = rng.choice(
            tasks
        )

        block = rng.choice(
            blocks
        )

        department = task[
            "department"
        ]

        requested_duration = int(
            clamp(
                task[
                    "estimated_duration_minutes"
                ]
                + rng.randint(
                    -15,
                    30,
                ),
                30,
                240,
            )
        )

        requested_start = (
            block["start_time"]
        )

        start_parts = (
            requested_start.split(":")
        )

        start_minutes = (
            int(start_parts[0]) * 60
            + int(start_parts[1])
        )

        requested_end_minutes = (
            start_minutes
            + requested_duration
        )

        requested_end = format_time(
            requested_end_minutes
        )

        status = rng.choices(
            [
                "PENDING",
                "APPROVED",
                "REJECTED",
            ],
            weights=[
                0.45,
                0.40,
                0.15,
            ],
            k=1,
        )[0]

        requests.append({

            "request_id":
                f"REQ-{i:06d}",

            "task_id":
                task["task_id"],

            "department":
                department,

            "corridor_id":
                task["corridor_id"],

            "requested_date":
                block["date"],

            "requested_start":
                requested_start,

            "requested_end":
                requested_end,

            "requested_duration_minutes":
                requested_duration,

            "block_id":
                block["block_id"],

            "status":
                status,
        })

    return requests


# ============================================================
# 7. MAINTENANCE OUTCOMES
# ============================================================

def generate_maintenance_outcomes(
    tasks,
):

    outcomes = []

    sampled_tasks = rng.sample(
        tasks,
        min(
            NUM_OUTCOMES,
            len(tasks),
        ),
    )

    for i, task in enumerate(
        sampled_tasks,
        start=1,
    ):

        estimated = task[
            "estimated_duration_minutes"
        ]

        duration_multiplier = (

            1.0

            + rng.gauss(
                0,
                0.12,
            )

            + task["severity"]
            * 0.015

            + (
                1
                - task[
                    "condition_score"
                ]
            )
            * 0.10
        )

        actual_duration = int(
            clamp(
                estimated
                * duration_multiplier,
                20,
                360,
            )
        )

        delay_probability = sigmoid(
            -2.5
            + 0.35
            * task["severity"]
            + 0.80
            * task["operational_impact"]
            + 0.02
            * task["overdue_days"]
        )

        delay_caused = (
            rng.random()
            < delay_probability
        )

        downtime_hours = round(
            actual_duration / 60,
            2,
        )

        completion_probability = clamp(
            0.98
            - 0.03
            * task["severity"]
            / 5,
            0.80,
            0.99,
        )

        completed = (
            rng.random()
            < completion_probability
        )

        outcomes.append({

            "outcome_id":
                f"OUT-{i:06d}",

            "task_id":
                task["task_id"],

            "actual_duration_minutes":
                actual_duration,

            "delay_caused":
                int(delay_caused),

            "downtime_hours":
                downtime_hours,

            "completed":
                int(completed),

            "safety_incident":
                0,
        })

    return outcomes


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(
        "SYNTHETIC RAILWAY DATA GENERATOR"
    )
    print("=" * 60)

    print(
        f"Random seed: {SEED}"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    print()

    print(
        "Generating assets..."
    )

    assets = generate_assets()

    print(
        "Generating asset history..."
    )

    asset_history = (
        generate_asset_history(
            assets
        )
    )

    print(
        "Generating train schedule..."
    )

    trains = generate_trains()

    print(
        "Generating block windows..."
    )

    blocks = generate_blocks()

    print(
        "Generating maintenance tasks..."
    )

    tasks = (
        generate_maintenance_tasks(
            assets,
            trains,
        )
    )

    print(
        "Generating block requests..."
    )

    block_requests = (
        generate_block_requests(
            tasks,
            blocks,
        )
    )

    print(
        "Generating maintenance outcomes..."
    )

    outcomes = (
        generate_maintenance_outcomes(
            tasks
        )
    )

    # ========================================================
    # WRITE DATASETS
    # ========================================================

    write_csv(
        "assets.csv",
        assets,
        [
            "asset_id",
            "asset_type",
            "department",
            "corridor_id",
            "location_km",
            "criticality",
            "installation_year",
            "condition_score",
        ],
    )

    write_csv(
        "asset_history.csv",
        asset_history,
        [
            "history_id",
            "asset_id",
            "inspection_date",
            "condition_score",
            "failure_event",
            "repair_duration_minutes",
            "downtime_hours",
        ],
    )

    write_csv(
        "train_schedule.csv",
        trains,
        [
            "train_id",
            "train_type",
            "corridor_id",
            "date",
            "arrival_time",
            "departure_time",
            "priority",
            "forecast_source",
        ],
    )

    write_csv(
        "block_windows.csv",
        blocks,
        [
            "block_id",
            "corridor_id",
            "date",
            "start_time",
            "end_time",
            "duration_minutes",
            "availability_status",
        ],
    )

    write_csv(
        "maintenance_tasks.csv",
        tasks,
        [
            "task_id",
            "asset_id",
            "department",
            "corridor_id",
            "maintenance_type",
            "defect_type",
            "severity",
            "criticality",
            "condition_score",
            "overdue_days",
            "failure_frequency",
            "safety_impact",
            "operational_impact",
            "estimated_duration_minutes",
            "due_date",
            "status",
            "priority_score",
            "priority_class",
        ],
    )

    write_csv(
        "block_requests.csv",
        block_requests,
        [
            "request_id",
            "task_id",
            "department",
            "corridor_id",
            "requested_date",
            "requested_start",
            "requested_end",
            "requested_duration_minutes",
            "block_id",
            "status",
        ],
    )

    write_csv(
        "maintenance_outcomes.csv",
        outcomes,
        [
            "outcome_id",
            "task_id",
            "actual_duration_minutes",
            "delay_caused",
            "downtime_hours",
            "completed",
            "safety_incident",
        ],
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 60)
    print(
        "DATA GENERATION COMPLETE"
    )
    print("=" * 60)

    print()

    print(
        f"Assets:               {len(assets):,}"
    )

    print(
        f"Asset history:        {len(asset_history):,}"
    )

    print(
        f"Maintenance tasks:    {len(tasks):,}"
    )

    print(
        f"Train movements:      {len(trains):,}"
    )

    print(
        f"Block windows:        {len(blocks):,}"
    )

    print(
        f"Block requests:       {len(block_requests):,}"
    )

    print(
        f"Maintenance outcomes: {len(outcomes):,}"
    )

    print()

    print(
        "Files available in:"
    )

    print(
        OUTPUT_DIR.resolve()
    )


if __name__ == "__main__":
    main()