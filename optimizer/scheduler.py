"""
Automatic Railway Maintenance Block Scheduler.

Version 1.1
Priority-aware greedy scheduling with strict block constraints.

Inputs:
    data/synthetic/maintenance_tasks.csv
    data/synthetic/block_windows.csv
    data/synthetic/train_schedule.csv

Output:
    data/synthetic/optimized_block_plan.csv
"""

import csv
from collections import defaultdict
from pathlib import Path

from optimizer.constraints import (
    time_to_minutes,
    minutes_to_time,
    task_conflicts_with_trains,
)

from optimizer.objective import (
    candidate_score,
    plan_objective,
)

from optimizer.validator import (
    validate_plan,
)


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = (
    BASE_DIR
    / "data"
    / "synthetic"
)

TASK_FILE = (
    DATA_DIR
    / "maintenance_tasks.csv"
)

BLOCK_FILE = (
    DATA_DIR
    / "block_windows.csv"
)

TRAIN_FILE = (
    DATA_DIR
    / "train_schedule.csv"
)

OUTPUT_FILE = (
    DATA_DIR
    / "optimized_block_plan.csv"
)


def load_csv(path):
    """Load a CSV file into a list of dictionaries."""

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


def load_data():

    tasks = load_csv(
        TASK_FILE
    )

    blocks = load_csv(
        BLOCK_FILE
    )

    trains = load_csv(
        TRAIN_FILE
    )

    return (
        tasks,
        blocks,
        trains,
    )


def convert_numeric_fields(tasks):
    """Convert numeric CSV fields to numbers."""

    numeric_fields = [
        "severity",
        "criticality",
        "condition_score",
        "overdue_days",
        "failure_frequency",
        "safety_impact",
        "operational_impact",
        "estimated_duration_minutes",
        "priority_score",
    ]

    for task in tasks:

        for field in numeric_fields:

            task[field] = float(
                task[field]
            )

        task[
            "estimated_duration_minutes"
        ] = int(
            task[
                "estimated_duration_minutes"
            ]
        )

    return tasks


def build_train_index(trains):
    """
    Index train movements by corridor and date.
    """

    index = defaultdict(list)

    for train in trains:

        key = (
            train["corridor_id"],
            train["date"],
        )

        index[key].append(
            train
        )

    return index


def build_block_index(blocks):
    """
    Index block windows by corridor and date.
    """

    index = defaultdict(list)

    for block in blocks:

        key = (
            block["corridor_id"],
            block["date"],
        )

        index[key].append(
            block
        )

    return index


def get_block_intervals(
    block_id,
    scheduled_by_block,
):
    """Return intervals already scheduled in a block."""

    return scheduled_by_block.get(
        block_id,
        [],
    )


def find_free_start(
    block,
    task,
    scheduled_intervals,
    trains,
):
    """
    Find the earliest feasible start time for a task.

    STRICT RULES:
        - Start cannot be before block start.
        - End cannot be after block end.
        - Task duration cannot exceed block duration.
        - Task cannot overlap another maintenance task.
        - Task cannot overlap a train movement.
    """

    block_start = time_to_minutes(
        block["start_time"]
    )

    block_end = time_to_minutes(
        block["end_time"]
    )

    duration = int(
        task[
            "estimated_duration_minutes"
        ]
    )

    block_duration = (
        block_end
        - block_start
    )

    # HARD CONSTRAINT:
    # Task must physically fit inside block.
    if duration > block_duration:
        return None

    # Start with the beginning of the block.
    candidate_starts = {
        block_start
    }

    # A task may begin after an already
    # scheduled maintenance task.
    for interval in scheduled_intervals:

        candidate_starts.add(
            max(
                block_start,
                interval["end"],
            )
        )

    # A task may begin after a train movement,
    # but NEVER before the block starts.
    for train in trains:

        departure = time_to_minutes(
            train["departure_time"]
        )

        if departure >= block_start:
            candidate_starts.add(
                departure
            )

    candidate_starts = sorted(
        candidate_starts
    )

    for start in candidate_starts:

        # HARD CONSTRAINT:
        # Never start before block.
        if start < block_start:
            continue

        end = (
            start
            + duration
        )

        # HARD CONSTRAINT:
        # Never finish after block.
        if end > block_end:
            continue

        # Check maintenance overlap.
        occupied = False

        for interval in scheduled_intervals:

            if (
                start < interval["end"]
                and interval["start"] < end
            ):

                occupied = True
                break

        if occupied:
            continue

        # Check train conflicts.
        if task_conflicts_with_trains(
            start,
            end,
            block["date"],
            block["corridor_id"],
            trains,
        ):
            continue

        return (
            start,
            end,
        )

    return None


def choose_best_block(
    task,
    candidate_blocks,
    scheduled_by_block,
    train_index,
    block_tasks,
):
    """
    Find the best feasible block for a task.
    """

    best = None

    task_duration = int(
        task[
            "estimated_duration_minutes"
        ]
    )

    for block in candidate_blocks:

        block_id = block[
            "block_id"
        ]

        block_start = time_to_minutes(
            block["start_time"]
        )

        block_end = time_to_minutes(
            block["end_time"]
        )

        block_duration = (
            block_end
            - block_start
        )

        # HARD CONSTRAINT:
        # Task must fit inside the block.
        if task_duration > block_duration:
            continue

        scheduled = get_block_intervals(
            block_id,
            scheduled_by_block,
        )

        trains = train_index.get(
            (
                block["corridor_id"],
                block["date"],
            ),
            [],
        )

        result = find_free_start(
            block,
            task,
            scheduled,
            trains,
        )

        if result is None:
            continue

        start, end = result

        remaining = (
            block_end
            - start
        )

        score = candidate_score(
            task,
            block,
            block_tasks.get(
                block_id,
                [],
            ),
            remaining,
        )

        # Prefer blocks on or before the due date.
        if block["date"] <= task["due_date"]:
            date_bonus = 0.05
        else:
            date_bonus = -0.10

        # Encourage multi-department coordination.
        coordination_bonus = 0.0

        if block_tasks.get(
            block_id
        ):

            coordination_bonus = 0.10

        total_score = (
            score
            + date_bonus
            + coordination_bonus
        )

        if (
            best is None
            or total_score
            > best["score"]
        ):

            best = {

                "block":
                    block,

                "start":
                    start,

                "end":
                    end,

                "score":
                    total_score,
            }

    return best


def create_assignment(
    task,
    selected,
):
    """Create one optimized schedule assignment."""

    block = selected[
        "block"
    ]

    return {

        "task_id":
            task["task_id"],

        "block_id":
            block["block_id"],

        "corridor_id":
            block["corridor_id"],

        "date":
            block["date"],

        "start_time":
            minutes_to_time(
                selected["start"]
            ),

        "end_time":
            minutes_to_time(
                selected["end"]
            ),

        "duration_minutes":
            int(
                task[
                    "estimated_duration_minutes"
                ]
            ),

        "department":
            task["department"],

        "maintenance_type":
            task["maintenance_type"],

        "priority_score":
            round(
                task["priority_score"],
                2,
            ),

        "priority_class":
            task["priority_class"],

        "criticality":
            int(
                task["criticality"]
            ),

        "overdue_days":
            int(
                task["overdue_days"]
            ),

        "scheduling_score":
            round(
                selected["score"],
                4,
            ),
    }


def optimize(
    tasks,
    blocks,
    trains,
):
    """
    Main priority-aware greedy optimizer.
    """

    tasks = convert_numeric_fields(
        tasks
    )

    # Highest-priority maintenance first.
    tasks.sort(
        key=lambda task: (
            task["priority_score"],
            task["criticality"],
            task["overdue_days"],
        ),
        reverse=True,
    )

    train_index = build_train_index(
        trains
    )

    block_index = build_block_index(
        blocks
    )

    scheduled_by_block = defaultdict(
        list
    )

    block_tasks = defaultdict(
        list
    )

    assignments = []

    for task in tasks:

        corridor = task[
            "corridor_id"
        ]

        task_due_date = task[
            "due_date"
        ]

        candidate_blocks = []

        # Only inspect blocks on the same corridor
        # and no later than the task due date.
        for (
            (
                block_corridor,
                block_date,
            ),
            corridor_blocks,
        ) in block_index.items():

            if block_corridor != corridor:
                continue

            if block_date > task_due_date:
                continue

            for block in corridor_blocks:

                if block[
                    "availability_status"
                ] != "AVAILABLE":
                    continue

                candidate_blocks.append(
                    block
                )

        if not candidate_blocks:
            continue

        selected = choose_best_block(
            task,
            candidate_blocks,
            scheduled_by_block,
            train_index,
            block_tasks,
        )

        if selected is None:
            continue

        assignment = create_assignment(
            task,
            selected,
        )

        block_id = assignment[
            "block_id"
        ]

        scheduled_by_block[
            block_id
        ].append({

            "task_id":
                task["task_id"],

            "start":
                selected["start"],

            "end":
                selected["end"],
        })

        block_tasks[
            block_id
        ].append(
            assignment
        )

        assignments.append(
            assignment
        )

    return assignments


def write_plan(assignments):

    fieldnames = [

        "task_id",

        "block_id",

        "corridor_id",

        "date",

        "start_time",

        "end_time",

        "duration_minutes",

        "department",

        "maintenance_type",

        "priority_score",

        "priority_class",

        "criticality",

        "overdue_days",

        "scheduling_score",
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            assignments
        )


def print_summary(
    assignments,
    tasks,
    blocks,
    validation,
):
    """Print optimizer performance summary."""

    total_tasks = len(
        tasks
    )

    scheduled_tasks = len(
        assignments
    )

    scheduled_ratio = (
        scheduled_tasks
        / max(
            total_tasks,
            1,
        )
    )

    departments = {
        assignment["department"]
        for assignment in assignments
    }

    blocks_used = {
        assignment["block_id"]
        for assignment in assignments
    }

    by_block = defaultdict(
        set
    )

    for assignment in assignments:

        by_block[
            assignment["block_id"]
        ].add(
            assignment["department"]
        )

    coordinated_blocks = 0

    for department_set in by_block.values():

        if len(department_set) >= 2:
            coordinated_blocks += 1

    objective = plan_objective(
        assignments,
        tasks,
    )

    print()
    print("=" * 60)
    print(
        "AUTOMATIC BLOCK PLANNING RESULT"
    )
    print("=" * 60)

    print()

    print(
        f"Total maintenance tasks: "
        f"{total_tasks:,}"
    )

    print(
        f"Scheduled tasks:          "
        f"{scheduled_tasks:,}"
    )

    print(
        f"Scheduled ratio:          "
        f"{scheduled_ratio:.2%}"
    )

    print(
        f"Blocks used:              "
        f"{len(blocks_used):,}"
    )

    print(
        f"Coordinated blocks:       "
        f"{coordinated_blocks:,}"
    )

    print(
        f"Departments represented:  "
        f"{len(departments)}"
    )

    print(
        f"Objective score:          "
        f"{objective:.4f}"
    )

    print()

    print(
        f"Validation valid:         "
        f"{validation['valid']}"
    )

    print(
        f"Validation errors:        "
        f"{len(validation['errors'])}"
    )

    print(
        f"Validation warnings:      "
        f"{len(validation['warnings'])}"
    )

    print()

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print("=" * 60)


def main():

    print("=" * 60)
    print(
        "AUTOMATIC RAILWAY BLOCK OPTIMIZER"
    )
    print("=" * 60)

    print()

    print(
        "Loading datasets..."
    )

    tasks, blocks, trains = load_data()

    print(
        f"Maintenance tasks: "
        f"{len(tasks):,}"
    )

    print(
        f"Block windows:      "
        f"{len(blocks):,}"
    )

    print(
        f"Train movements:    "
        f"{len(trains):,}"
    )

    print()

    print(
        "Running priority-aware scheduling..."
    )

    assignments = optimize(
        tasks,
        blocks,
        trains,
    )

    print(
        f"Generated assignments: "
        f"{len(assignments):,}"
    )

    print()

    print(
        "Validating schedule..."
    )

    validation = validate_plan(
        assignments,
        tasks,
        blocks,
        trains,
    )

    write_plan(
        assignments
    )

    print_summary(
        assignments,
        tasks,
        blocks,
        validation,
    )

    if not validation["valid"]:

        print()
        print(
            "FIRST VALIDATION ERRORS:"
        )

        for error in validation[
            "errors"
        ][:10]:

            print(
                f"  - {error}"
            )


if __name__ == "__main__":

    main()