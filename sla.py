"""
SLA timers
----------
An SLA (service level agreement) is the service desk's promise about how quickly each
priority gets fixed. Every ticket gets a "resolve by" time: when it arrived, plus the
target for its priority. The ticket queue shows how long is left, warns when time is
running out, and records whether completed tickets met their target.

The targets count clock time, 24 hours a day. A real service desk would usually pause
the clock for P3 and P4 tickets outside working hours.

This file doesn't use Flask or the database, so test_sla.py can test it on its own.
"""

from datetime import datetime, timedelta

# How many hours each priority has to be resolved, counted from when the ticket arrived.
# Typical service desk targets: change them here and the whole site follows.
SLA_HOURS = {
    "P1": 4,        # critical: within 4 hours
    "P2": 8,        # high: within a working day
    "P3": 3 * 24,   # medium: within 3 days
    "P4": 5 * 24,   # low: within 5 days
}

# A ticket is "at risk" once less than this share of its time is left (a quarter).
# For a P1 that's the last hour; for a P4 it's the last 30 hours.
AT_RISK_SHARE = 0.25

# The states that need someone's attention, for the queue's "At risk or overdue" filter
NEEDS_ATTENTION = {"at-risk", "overdue", "missed"}


def read_time(value):
    """Turn "2026-10-25 14:05" into a datetime (any seconds are ignored).
    Returns None if the time is missing or can't be read."""
    try:
        return datetime.strptime(str(value or "")[:16], "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def target_words(priority):
    """The target in words, e.g. "4 hours" or "3 days"."""
    hours = SLA_HOURS[priority]
    if hours % 24 == 0:
        days = hours // 24
        return "1 day" if days == 1 else f"{days} days"
    return "1 hour" if hours == 1 else f"{hours} hours"


def how_long(seconds):
    """Turn a number of seconds into short text: "3d 4h", "2h 15m", "40m".
    It works the same for time left and time overdue (the sign is ignored)."""
    minutes = int(abs(seconds)) // 60
    days, minutes = divmod(minutes, 24 * 60)
    hours, minutes = divmod(minutes, 60)
    if days:
        return f"{days}d {hours}h" if hours else f"{days}d"
    if hours:
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    return f"{minutes}m" if minutes else "under 1m"


def sla_status(received, priority, now, completed_at=None):
    """Where a ticket stands against its SLA target.

    Returns a dictionary with:
      state           "on-track", "at-risk" or "overdue" for open tickets,
                      "met" or "missed" for completed ones,
                      or "" if there's no target (no priority yet, or no received time)
      label           short text for the queue, e.g. "Due in 2h 15m" or "Overdue by 40m"
      due             the "resolve by" time (a datetime), or None
      seconds_left    open tickets only: seconds until it's due (below 0 once it's overdue)
      target_seconds  how long this priority allows, in seconds
      took            completed tickets only: how long it took, e.g. "2h 10m"
      late            missed tickets only: how far past the target, e.g. "1h 5m"
    """
    result = {"state": "", "label": "", "due": None, "seconds_left": None,
              "target_seconds": None, "took": "", "late": ""}
    start = read_time(received)
    if start is None or priority not in SLA_HOURS:
        return result

    target = timedelta(hours=SLA_HOURS[priority])
    due = start + target
    result.update(due=due, target_seconds=int(target.total_seconds()))

    finished = read_time(completed_at)
    if finished is not None:                       # completed: did it meet the target?
        result["took"] = how_long((finished - start).total_seconds())
        if finished <= due:
            result.update(state="met", label="Met target")
        else:
            late = how_long((finished - due).total_seconds())
            result.update(state="missed", label=f"Missed by {late}", late=late)
        return result

    seconds_left = int((due - now).total_seconds())  # still open: how long is left?
    result["seconds_left"] = seconds_left
    if seconds_left < 0:
        result.update(state="overdue", label=f"Overdue by {how_long(seconds_left)}")
    elif seconds_left < target.total_seconds() * AT_RISK_SHARE:
        result.update(state="at-risk", label=f"Due in {how_long(seconds_left)}")
    else:
        result.update(state="on-track", label=f"Due in {how_long(seconds_left)}")
    return result
