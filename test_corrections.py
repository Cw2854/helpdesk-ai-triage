"""Tests that the priority rules correct the AI when it gets the priority wrong.

Each test gives validate() a made-up AI answer (no real AI is called, so these run
on GitHub in seconds) and checks the final priority, the AI's own guess, and
whether a person is asked to check it.
"""

from triage import build_summary, validate


def ai_answer(**changes):
    """A typical AI answer for a minor issue. Each test changes only what it's testing."""
    answer = {"issue_summary": "Test ticket", "category": "Hardware",
              "people_affected": "one", "can_work": "yes", "deadline": "none",
              "security_risk": "none", "ticket_type": "problem", "enough_info": True,
              "priority": "P4", "confidence": 0.9, "reason": "Test.",
              "suggested_fix": "1. Check the device", "draft_reply": "Hi, thanks for getting in touch."}
    answer.update(changes)
    return answer


# --- The rules raise tickets the AI under-prioritised -------------------------

def test_phishing_with_password_typed_in_is_raised_to_p1():
    # Like TST-002 in the test set: the AI said P2, but a password typed into a
    # fake site is an active security incident, so it must be P1
    result = validate(ai_answer(category="Security / Phishing", security_risk="active",
                                can_work="no", priority="P2"))
    assert result["priority"] == "P1"
    assert result["ai_priority"] == "P2"


def test_client_meeting_in_20_minutes_is_raised_to_p2():
    # Like TST-013: the AI said P3, but it's needed within hours
    result = validate(ai_answer(deadline="hours", can_work="workaround", priority="P3"))
    assert result["priority"] == "P2"
    assert result["ai_priority"] == "P3"


def test_new_starter_next_week_is_raised_to_p3():
    # Like TST-022: the AI said P4, but a starter on Monday is time-sensitive
    result = validate(ai_answer(category="Starter / Leaver", ticket_type="request",
                                deadline="days", priority="P4"))
    assert result["priority"] == "P3"


def test_vague_ticket_is_raised_to_p3_and_flagged():
    # "playing up again": too vague to judge, so P3 until someone checks
    result = validate(ai_answer(enough_info=False, priority="P4"))
    assert result["priority"] == "P3"
    assert "not enough detail" in result["review_reason"]


# --- When the rules lower a ticket, a person is always asked to check ----------

def test_urgent_sounding_minor_ticket_is_lowered_but_flagged():
    # "URGENT!!! F7 key sticking": the AI said P2, the facts say it's minor
    result = validate(ai_answer(priority="P2"))
    assert result["priority"] == "P4"
    assert result["needs_human_review"] == "Yes"
    assert "the AI thought P2 but the rules gave P4" in result["review_reason"]


# --- No correction needed --------------------------------------------------------

def test_agreement_is_not_flagged():
    result = validate(ai_answer(can_work="no", priority="P2"))
    assert result["priority"] == "P2"
    assert result["needs_human_review"] == "No"


def test_the_reasoning_names_the_rule_used():
    result = validate(ai_answer(can_work="no", priority="P3"))
    assert result["priority_rule"] == "someone can't work"
    assert "Rule: someone can't work, so P2." in result["ai_reason"]


# --- If the AI's facts are broken, nothing is quietly changed --------------------

def test_broken_facts_keep_the_ai_guess_and_flag_it():
    result = validate(ai_answer(can_work="maybe", priority="P2"))
    assert result["priority"] == "P2"
    assert result["needs_human_review"] == "Yes"


# --- The summary counts corrections correctly -----------------------------------

def test_summary_counts_raised_and_lowered():
    results = [
        validate(ai_answer(can_work="no", priority="P3")),   # raised P3 -> P2
        validate(ai_answer(priority="P2")),                  # lowered P2 -> P4
        validate(ai_answer(can_work="no", priority="P2")),   # agreed on P2
    ]
    stats = build_summary(results)
    assert stats["rules_raised"] == 1
    assert stats["rules_lowered"] == 1
