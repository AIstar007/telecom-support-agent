"""
Escalation Agent.

Terminal node for anything the domain agents can't confidently or safely
handle: low-confidence answers, mutating requests (refunds, plan changes),
or out-of-scope queries. In production this would open a ticket / hand off
to a live-chat queue with the conversation transcript attached.
"""

MUTATING_KEYWORDS = ["cancel my", "issue a refund", "change my plan to", "switch me to"]


def needs_escalation(message: str, confidence: float, threshold: float = 0.5) -> bool:
    text = message.lower()
    if any(k in text for k in MUTATING_KEYWORDS):
        return True
    return confidence < threshold


def escalate(message: str, reason: str) -> dict:
    # Placeholder: in production this creates a ticket via the support-desk API
    ticket_id = "ESC-DEMO-0001"
    return {
        "answer": (
            "I've routed this to a human specialist since it needs account changes or "
            "I'm not confident enough to answer directly. "
            f"Reference: {ticket_id}."
        ),
        "sources": [],
        "escalated": True,
        "reason": reason,
    }
