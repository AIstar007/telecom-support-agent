from app.agents.escalation_agent import needs_escalation, escalate


def test_mutating_request_always_escalates_regardless_of_confidence():
    assert needs_escalation("please cancel my subscription", confidence=0.99) is True
    assert needs_escalation("issue a refund for my last bill", confidence=1.0) is True
    assert needs_escalation("change my plan to Family Max", confidence=0.9) is True


def test_low_confidence_answer_escalates():
    assert needs_escalation("some ambiguous question", confidence=0.2) is True


def test_high_confidence_non_mutating_does_not_escalate():
    assert needs_escalation("why did my bill increase", confidence=0.9) is False


def test_escalate_returns_expected_shape():
    result = escalate("cancel my plan", reason="mutation")
    assert result["escalated"] is True
    assert result["sources"] == []
    assert "reason" in result
    assert isinstance(result["answer"], str) and len(result["answer"]) > 0
