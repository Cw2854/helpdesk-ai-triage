from triage import decide_priority


def facts(**changes):
    """Facts for a minor issue. Each test changes only the facts it's testing."""
    base = {"people_affected": "one", "can_work": "yes", "deadline": "none",
            "security_risk": "none", "ticket_type": "problem", "enough_info": True}
    base.update(changes)
    return base


def test_active_security_incident_is_p1():
    priority, rule = decide_priority(facts(security_risk="active"), "Security / Phishing")
    assert priority == "P1"


def test_minor_issue_is_p4():
    priority, rule = decide_priority(facts(), "Hardware")
    assert priority == "P4"

def test_whole_team_cant_work_is_p1():
    priority, rule = decide_priority(facts(people_affected="many", can_work="no"), "Email")
    assert priority == "P1"

def test_whole_office_with_workaround_is_p3():
    # Lots of people affected, but they can still work, so it's not critical
    priority, rule = decide_priority(facts(people_affected="many", can_work="workaround"), "Printing")
    assert priority == "P3"


def test_one_person_cant_work_is_p2():
    priority, rule = decide_priority(facts(can_work="no"), "Hardware")
    assert priority == "P2"


def test_lost_work_phone_is_p2():
    # A lost device could lead to a breach
    priority, rule = decide_priority(facts(security_risk="possible"), "Mobile Device")
    assert priority == "P2"


def test_needed_within_hours_is_p2():
    priority, rule = decide_priority(facts(deadline="hours"), "Hardware")
    assert priority == "P2"


def test_broken_with_workaround_is_p3():
    priority, rule = decide_priority(facts(can_work="workaround"), "Software")
    assert priority == "P3"


def test_starter_next_week_is_p3():
    priority, rule = decide_priority(facts(ticket_type="request", deadline="days"), "Starter / Leaver")
    assert priority == "P3"


def test_question_about_leaver_process_is_p4():
    # Only asking how the process works, so nothing needs doing yet
    priority, rule = decide_priority(facts(ticket_type="question"), "Starter / Leaver")
    assert priority == "P4"


def test_reported_phishing_nothing_clicked_is_p3():
    # Security reports are never low priority, even if nobody clicked
    priority, rule = decide_priority(facts(), "Security / Phishing")
    assert priority == "P3"


def test_too_vague_to_judge_is_p3():
    # Not enough detail, so it's P3 until a person checks
    priority, rule = decide_priority(facts(enough_info=False), "Other")
    assert priority == "P3"
