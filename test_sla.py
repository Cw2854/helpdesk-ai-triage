"""Tests for the SLA timers in sla.py.

Every test uses a fixed "now", so the results are the same whenever the tests run.
"""

from datetime import datetime

from sla import how_long, sla_status, target_words

NOW = datetime(2026, 10, 25, 12, 0)


# --- Open tickets: on track, at risk, overdue ------------------------------------

def test_p1_received_one_hour_ago_is_on_track():
    # P1 target is 4 hours: received 11:00, so due 15:00, 3 hours left
    status = sla_status("2026-10-25 11:00", "P1", NOW)
    assert status["state"] == "on-track"
    assert status["due"] == datetime(2026, 10, 25, 15, 0)
    assert status["label"] == "Due in 3h"


def test_p1_with_under_an_hour_left_is_at_risk():
    # Due 12:30, so 30 minutes left: under a quarter of the 4 hours
    status = sla_status("2026-10-25 08:30", "P1", NOW)
    assert status["state"] == "at-risk"
    assert status["label"] == "Due in 30m"


def test_p1_past_its_target_is_overdue():
    # Received 07:15, due 11:15, so 45 minutes overdue
    status = sla_status("2026-10-25 07:15", "P1", NOW)
    assert status["state"] == "overdue"
    assert status["label"] == "Overdue by 45m"
    assert status["seconds_left"] == -45 * 60


def test_each_priority_gets_its_own_target():
    # The same arrival time is fine for a P4 (5 days) but overdue for a P1 (4 hours)
    assert sla_status("2026-10-24 12:00", "P1", NOW)["state"] == "overdue"
    assert sla_status("2026-10-24 12:00", "P2", NOW)["state"] == "overdue"
    assert sla_status("2026-10-24 12:00", "P3", NOW)["state"] == "on-track"
    assert sla_status("2026-10-24 12:00", "P4", NOW)["state"] == "on-track"


def test_exactly_on_the_deadline_is_not_yet_overdue():
    status = sla_status("2026-10-25 08:00", "P1", NOW)
    assert status["state"] == "at-risk"
    assert status["label"] == "Due in under 1m"


# --- Completed tickets: met or missed --------------------------------------------

def test_completed_in_time_met_the_target():
    status = sla_status("2026-10-25 09:00", "P1", NOW, completed_at="2026-10-25 11:10:42")
    assert status["state"] == "met"
    assert status["took"] == "2h 10m"


def test_completed_late_missed_the_target():
    # P2 target is 8 hours: due 17:00, completed 18:05
    status = sla_status("2026-10-25 09:00", "P2", NOW, completed_at="2026-10-25 18:05:00")
    assert status["state"] == "missed"
    assert status["label"] == "Missed by 1h 5m"
    assert status["late"] == "1h 5m"


# --- No target ------------------------------------------------------------------

def test_no_priority_means_no_timer():
    # e.g. the AI failed and nobody has set a priority yet
    assert sla_status("2026-10-25 11:00", "", NOW)["state"] == ""


def test_missing_received_time_means_no_timer():
    assert sla_status("", "P1", NOW)["state"] == ""


# --- Wording ----------------------------------------------------------------------

def test_how_long_wording():
    assert how_long(40 * 60) == "40m"
    assert how_long(2 * 3600 + 15 * 60) == "2h 15m"
    assert how_long(3 * 86400 + 4 * 3600) == "3d 4h"
    assert how_long(-90 * 60) == "1h 30m"        # overdue time reads the same way


def test_target_words():
    assert target_words("P1") == "4 hours"
    assert target_words("P3") == "3 days"
