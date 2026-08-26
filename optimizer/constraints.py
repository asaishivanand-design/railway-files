"""
Hard constraints for railway maintenance block planning.

These functions define what a valid maintenance assignment is.
"""

from datetime import datetime


def time_to_minutes(time_string):
    """Convert HH:MM into minutes since midnight."""

    hour, minute = map(
        int,
        time_string.split(":"),
    )

    return hour * 60 + minute


def minutes_to_time(minutes):
    """Convert minutes since midnight into HH:MM."""

    minutes = int(minutes) % 1440

    hour = minutes // 60
    minute = minutes % 60

    return f"{hour:02d}:{minute:02d}"


def intervals_overlap(
    start_a,
    end_a,
    start_b,
    end_b,
):
    """Return True if two time intervals overlap."""

    return (
        start_a < end_b
        and start_b < end_a
    )


def task_fits_block(
    task,
    block,
    scheduled_intervals=None,
):
    """
    Check whether a maintenance task can physically
    fit inside a block.
    """

    if task["corridor_id"] != block["corridor_id"]:
        return False

    if block["availability_status"] != "AVAILABLE":
        return False

    duration = int(
        task["estimated_duration_minutes"]
    )

    block_duration = int(
        block["duration_minutes"]
    )

    if duration > block_duration:
        return False

    due_date = task.get("due_date")

    block_date = block.get("date")

    if due_date and block_date:
        if block_date > due_date:
            return False

    if scheduled_intervals is None:
        scheduled_intervals = []

    block_start = time_to_minutes(
        block["start_time"]
    )

    block_end = time_to_minutes(
        block["end_time"]
    )

    for interval in scheduled_intervals:

        if intervals_overlap(
            block_start,
            block_end,
            interval["start"],
            interval["end"],
        ):
            return False

    return True


def task_conflicts_with_trains(
    task_start,
    task_end,
    block_date,
    corridor_id,
    trains,
):
    """
    Return True if the proposed maintenance interval
    conflicts with a train movement on the same corridor.
    """

    for train in trains:

        if train["corridor_id"] != corridor_id:
            continue

        if train["date"] != block_date:
            continue

        train_start = time_to_minutes(
            train["arrival_time"]
        )

        train_end = time_to_minutes(
            train["departure_time"]
        )

        if intervals_overlap(
            task_start,
            task_end,
            train_start,
            train_end,
        ):
            return True

    return False


def assignment_is_valid(
    assignment,
    task,
    block,
    trains,
    scheduled_intervals=None,
):
    """
    Validate a proposed maintenance assignment.
    """

    if task["corridor_id"] != block["corridor_id"]:
        return False

    if assignment["date"] != block["date"]:
        return False

    if assignment["start_time"] < block["start_time"]:
        return False

    if assignment["end_time"] > block["end_time"]:
        return False

    start = time_to_minutes(
        assignment["start_time"]
    )

    end = time_to_minutes(
        assignment["end_time"]
    )

    if end <= start:
        return False

    if task_conflicts_with_trains(
        start,
        end,
        block["date"],
        block["corridor_id"],
        trains,
    ):
        return False

    if scheduled_intervals:

        for interval in scheduled_intervals:

            if intervals_overlap(
                start,
                end,
                interval["start"],
                interval["end"],
            ):
                return False

    return True