"""
Intent Router Agent.

Classifies an incoming query into one of a fixed set of intents so the
orchestrator can route to the right domain agent. Kept deterministic-ish via
a constrained LLM call (single-word output, low temperature) rather than a
free-form chat completion — reduces routing drift.
"""
from enum import Enum


class Intent(str, Enum):
    BILLING = "billing"
    PLAN_INFO = "plan_info"
    TROUBLESHOOTING = "troubleshooting"
    OUT_OF_SCOPE = "out_of_scope"

INTENT_SYSTEM_PROMPT = """You are an intent classifier for a telecom support bot.
Classify the user's message into exactly one of: billing, plan_info, troubleshooting, out_of_scope.
Respond with only the label, nothing else."""


def classify_intent(message: str, llm_call=None) -> Intent:
    """
    llm_call: injected callable(system_prompt, user_message) -> str, so this
    is unit-testable without hitting a real model. Falls back to a naive
    keyword classifier if no llm_call is provided (useful for local dev
    without an API key).
    """
    if llm_call is not None:
        raw = llm_call(INTENT_SYSTEM_PROMPT, message).strip().lower()
        try:
            return Intent(raw)
        except ValueError:
            return Intent.OUT_OF_SCOPE

    text = message.lower()
    if any(w in text for w in ["bill", "charge", "invoice", "refund"]):
        return Intent.BILLING
    if any(w in text for w in ["plan", "upgrade", "downgrade", "switch"]):
        return Intent.PLAN_INFO
    if any(w in text for w in ["not working", "no signal", "slow", "down", "error"]):
        return Intent.TROUBLESHOOTING
    return Intent.OUT_OF_SCOPE
