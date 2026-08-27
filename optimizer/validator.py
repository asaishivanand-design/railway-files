"""
Validation layer for generated railway block plans.
"""

from collections import defaultdict

from optimizer.constraints import (
    time_to_minutes,
    intervals_overlap,
    task_conflicts_with_trains,
)


def validate_plan(
    assignments,
    tasks,
    blocks,
    trains,
):
    """
    Validate a complete maintenance block plan.

    Returns:
        {
            "valid": bool,
            "errors": list,
            "warnings": list
        }
    """

    errors = []
    warnings = []

    task_lookup = {
        task["task_id"]: task
        for task in tasks
    }

    block_lookup = {
        block["block_id"]: block
        for block in blocks
    }

    intervals_by_block = defaultdict(
        list
    )

    for assignment in assignments:

        task_id = assignment[
            "task_id"
        ]

        block_id = assignment[
            "block_id"
        ]

        if task_id not in task_lookup:

            errors.append(
                f"Unknown task: {task_id}"
            )

            continue

        if block_id not in block_lookup:

            errors.append(
                f"Unknown block: {block_id}"
            )

            continue

        task = task_lookup[
            task_id
        ]

        block = block_lookup[
            block_id
        ]

        if (
            task["corridor_id"]
            != block["corridor_id"]
        ):

            errors.append(
                f"{task_id}: corridor mismatch"
            )

        if (
            assignment["date"]
            != block["date"]
        ):

            errors.append(
                f"{task_id}: date mismatch"
            )

        start = time_to_minutes(
            assignment["start_time"]
        )

        end = time_to_minutes(
            assignment["end_time"]
        )

        block_start = time_to_minutes(
            block["start_time"]
        )

        block_end = time_to_minutes(
            block["end_time"]
        )

        if start < block_start:

            errors.append(
                f"{task_id}: starts before block"
            )

        if end > block_end:

            errors.append(
                f"{task_id}: ends after block"
            )

        if end <= start:

            errors.append(
                f"{task_id}: invalid time interval"
            )

        if (
            assignment["date"]
            > task["due_date"]
        ):

            warnings.append(
                f"{task_id}: scheduled after due date"
            )

        if task_conflicts_with_trains(
            start,
            end,
            block["date"],
            block["corridor_id"],
            trains,
        ):

            errors.append(
                f"{task_id}: train conflict"
            )

        for existing in intervals_by_block[
            block_id
        ]:

            if intervals_overlap(
                start,
                end,
                existing["start"],
                existing["end"],
            ):

                errors.append(
                    f"{task_id}: overlaps "
                    f"{existing['task_id']} "
                    f"in {block_id}"
                )

        intervals_by_block[
            block_id
        ].append({

            "task_id":
                task_id,

            "start":
                start,

            "end":
                end,
        })

    # Check duplicate task assignments.

    seen_tasks = set()

    for assignment in assignments:

        task_id = assignment[
            "task_id"
        ]

        if task_id in seen_tasks:

            errors.append(
                f"Task scheduled twice: "
                f"{task_id}"
            )

        seen_tasks.add(
            task_id
        )

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

        "warnings":
            warnings,
    }