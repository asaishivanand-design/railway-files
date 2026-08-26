"""
Objective functions for railway maintenance block planning.

Higher scores represent better maintenance-block assignments.
"""


def priority_value(task):
    """Return normalized maintenance priority."""

    return float(
        task["priority_score"]
    ) / 100.0


def urgency_value(task):
    """Estimate urgency from overdue maintenance."""

    overdue_days = float(
        task.get("overdue_days", 0)
    )

    return min(
        overdue_days / 30.0,
        1.0,
    )


def utilization_value(
    task_duration,
    available_duration,
):
    """Measure how efficiently a block is used."""

    if available_duration <= 0:
        return 0.0

    return min(
        task_duration
        / available_duration,
        1.0,
    )


def department_coordination_bonus(
    task,
    existing_tasks,
):
    """
    Reward using one block for multiple departments.

    The purpose is to encourage coordinated
    Engineering + S&T + TRD maintenance.
    """

    if not existing_tasks:
        return 0.0

    departments = {
        item["department"]
        for item in existing_tasks
    }

    if task["department"] in departments:
        return 0.05

    new_department_count = (
        len(departments) + 1
    )

    if new_department_count >= 3:
        return 0.30

    if new_department_count == 2:
        return 0.18

    return 0.0


def candidate_score(
    task,
    block,
    existing_tasks,
    remaining_minutes,
):
    """
    Calculate the score of placing a task
    inside a particular block.
    """

    priority = priority_value(
        task
    )

    urgency = urgency_value(
        task
    )

    duration = float(
        task["estimated_duration_minutes"]
    )

    utilization = utilization_value(
        duration,
        max(
            remaining_minutes,
            duration,
        ),
    )

    coordination = (
        department_coordination_bonus(
            task,
            existing_tasks,
        )
    )

    criticality = (
        float(
            task["criticality"]
        ) / 5.0
    )

    safety = float(
        task["safety_impact"]
    )

    operational = float(
        task["operational_impact"]
    )

    # Main objective:
    # prioritize important maintenance.
    score = (
        0.45 * priority
        + 0.15 * urgency
        + 0.10 * criticality
        + 0.10 * safety
        + 0.08 * operational
        + 0.07 * utilization
        + 0.05 * coordination
    )

    return score


def plan_objective(
    assignments,
    tasks,
):
    """
    Calculate an overall objective score
    for a generated block plan.
    """

    if not assignments:
        return 0.0

    task_lookup = {
        task["task_id"]: task
        for task in tasks
    }

    total_priority = 0.0
    total_utilization = 0.0
    coordinated_blocks = 0

    block_departments = {}

    for assignment in assignments:

        task = task_lookup[
            assignment["task_id"]
        ]

        total_priority += (
            float(
                task["priority_score"]
            )
            / 100.0
        )

        block_id = assignment[
            "block_id"
        ]

        block_departments.setdefault(
            block_id,
            set(),
        )

        block_departments[
            block_id
        ].add(
            task["department"]
        )

    for departments in block_departments.values():

        if len(departments) >= 2:
            coordinated_blocks += 1

    total_tasks = len(
        assignments
    )

    average_priority = (
        total_priority
        / total_tasks
    )

    coordination_ratio = (
        coordinated_blocks
        / max(
            len(block_departments),
            1,
        )
    )

    return (
        0.75 * average_priority
        + 0.25 * coordination_ratio
    )