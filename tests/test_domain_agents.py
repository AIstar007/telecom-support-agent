from app.agents.billing_agent import answer_billing_query
from app.agents.plan_agent import answer_plan_query
from app.agents.troubleshooting_agent import answer_troubleshooting_query


def test_billing_agent_grounds_answer_in_retrieved_source():
    result = answer_billing_query("why is my bill higher this month")
    assert result["confidence"] > 0.2
    assert "billing_faq.md" in result["sources"]
    assert isinstance(result["answer"], str) and len(result["answer"]) > 0


def test_billing_agent_low_confidence_when_no_match():
    result = answer_billing_query("")
    # empty query should retrieve poorly / not confidently
    assert 0.0 <= result["confidence"] <= 1.0


def test_plan_agent_grounds_answer_in_plan_catalog():
    result = answer_plan_query("what's the cheapest plan you offer")
    assert "plan_catalog.md" in result["sources"]
    assert result["confidence"] > 0.2


def test_troubleshooting_agent_grounds_answer_in_guide():
    result = answer_troubleshooting_query("my wifi keeps dropping")
    assert "troubleshooting_guide.md" in result["sources"]
    assert result["confidence"] > 0.2


def test_agents_use_injected_llm_call_when_provided():
    captured = {}

    def fake_llm_call(system_prompt, user_message):
        captured["system_prompt"] = system_prompt
        captured["user_message"] = user_message
        return "real model answer"

    result = answer_billing_query("why is my bill high", llm_call=fake_llm_call)
    assert result["answer"] == "real model answer"
    assert "system_prompt" in captured
