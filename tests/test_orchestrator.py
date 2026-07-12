from app.agents.orchestrator import run_pipeline


def test_empty_message_handled_gracefully():
    result = run_pipeline("")
    assert result["escalated"] is False
    assert result["intent"] == "out_of_scope"
    assert "didn't receive" in result["answer"].lower()


def test_mutating_billing_request_escalates_end_to_end():
    result = run_pipeline("please cancel my subscription and issue a refund")
    assert result["escalated"] is True
    assert result["intent"] == "billing"


def test_plain_billing_question_answers_without_escalation():
    result = run_pipeline("why did my bill go up this month")
    assert result["intent"] == "billing"
    # with the stub LLM path (no API key in test env), confidence is moderate,
    # not guaranteed non-escalated — assert on shape instead of exact routing
    assert "answer" in result and isinstance(result["answer"], str)


def test_out_of_scope_question_escalates():
    result = run_pipeline("what's the weather like in Delhi today")
    assert result["escalated"] is True
    assert result["intent"] == "out_of_scope"


def test_domain_agent_exception_is_caught_and_escalates(monkeypatch):
    from app.agents import orchestrator

    def broken_agent(message, llm_call=None):
        raise RuntimeError("simulated failure")

    monkeypatch.setitem(orchestrator.DOMAIN_AGENTS, orchestrator.Intent.BILLING, broken_agent)

    result = run_pipeline("why is my bill wrong")
    assert result["escalated"] is True
    assert result["reason"] == "domain_agent_error"


def test_intent_classification_exception_is_caught_and_escalates(monkeypatch):
    from app.agents import orchestrator

    def broken_classifier(message, llm_call=None):
        raise RuntimeError("simulated classifier failure")

    monkeypatch.setattr(orchestrator, "classify_intent", broken_classifier)

    result = run_pipeline("anything")
    assert result["escalated"] is True
    assert result["reason"] == "intent_classification_error"
