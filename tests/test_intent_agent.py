from app.agents.intent_agent import classify_intent, Intent


def test_billing_keywords_classified_as_billing():
    assert classify_intent("why is my bill so high this month") == Intent.BILLING
    assert classify_intent("I need a refund for last month's charge") == Intent.BILLING


def test_plan_keywords_classified_as_plan_info():
    assert classify_intent("can I upgrade my plan") == Intent.PLAN_INFO
    assert classify_intent("what plans do you offer") == Intent.PLAN_INFO


def test_troubleshooting_keywords_classified_correctly():
    assert classify_intent("my internet is not working") == Intent.TROUBLESHOOTING
    assert classify_intent("getting no signal since this morning") == Intent.TROUBLESHOOTING


def test_unrelated_query_classified_out_of_scope():
    assert classify_intent("what's the weather like today") == Intent.OUT_OF_SCOPE


def test_llm_call_is_used_when_provided():
    calls = []

    def fake_llm_call(system_prompt, user_message):
        calls.append((system_prompt, user_message))
        return "billing"

    result = classify_intent("some message", llm_call=fake_llm_call)
    assert result == Intent.BILLING
    assert len(calls) == 1


def test_llm_call_invalid_response_falls_back_to_out_of_scope():
    result = classify_intent("some message", llm_call=lambda s, m: "not_a_real_intent")
    assert result == Intent.OUT_OF_SCOPE
