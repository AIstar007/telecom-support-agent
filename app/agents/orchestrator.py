"""
Orchestrator — the state machine wiring intent routing, domain agents, and
escalation together.

Kept as a plain Python function graph for scaffold clarity; a production
version would use LangGraph's StateGraph so state transitions are explicit
and traceable (see the Senior AI Engineer submission for that pattern).
"""
import logging

from app.agents.intent_agent import classify_intent, Intent
from app.agents.billing_agent import answer_billing_query
from app.agents.plan_agent import answer_plan_query
from app.agents.troubleshooting_agent import answer_troubleshooting_query
from app.agents.escalation_agent import needs_escalation, escalate

logger = logging.getLogger("copilot.orchestrator")

DOMAIN_AGENTS = {
    Intent.BILLING: answer_billing_query,
    Intent.PLAN_INFO: answer_plan_query,
    Intent.TROUBLESHOOTING: answer_troubleshooting_query,
}


def run_pipeline(message: str, llm_call=None) -> dict:
    if not message or not message.strip():
        return {
            "answer": "I didn't receive a question — could you tell me what you need help with?",
            "sources": [],
            "escalated": False,
            "intent": "out_of_scope",
        }

    try:
        intent = classify_intent(message, llm_call=llm_call)
    except Exception:
        logger.exception("Intent classification failed, defaulting to escalation")
        result = escalate(message, reason="intent_classification_error")
        result["intent"] = "out_of_scope"
        return result

    if intent == Intent.OUT_OF_SCOPE:
        result = escalate(message, reason="out_of_scope")
        result["intent"] = intent.value
        return result

    domain_fn = DOMAIN_AGENTS[intent]
    try:
        domain_result = domain_fn(message, llm_call=llm_call)
    except Exception:
        logger.exception("Domain agent '%s' failed", intent.value)
        result = escalate(message, reason="domain_agent_error")
        result["intent"] = intent.value
        return result

    if needs_escalation(message, domain_result["confidence"]):
        result = escalate(message, reason="low_confidence_or_mutation")
        result["intent"] = intent.value
        return result

    return {
        "answer": domain_result["answer"],
        "sources": domain_result["sources"],
        "escalated": False,
        "intent": intent.value,
    }
