"""
Billing Domain Agent.

Answers billing questions using RAG over policy docs plus a read-only
account-lookup tool. Never mutates state (no refund issuance, no plan
changes) — those get handed to the Escalation Agent by the orchestrator.
"""
from app.rag.retriever import retrieve

BILLING_SYSTEM_PROMPT = """You are a billing support agent for a telecom company.
Answer using ONLY the provided context. If the context doesn't cover the question,
say you're not sure and recommend escalation. Always cite which source doc you used."""


def mock_account_lookup(account_id: str) -> dict:
    """Placeholder for a real billing-system API call."""
    return {"account_id": account_id, "current_bill": 799, "plan": "Unlimited 5G", "last_payment": "2026-06-15"}


def answer_billing_query(message: str, llm_call=None) -> dict:
    chunks = retrieve(message, k=3)
    context = "\n\n".join(c["text"] for c in chunks)
    sources = [c["source"] for c in chunks]

    if llm_call is not None:
        prompt = f"Context:\n{context}\n\nQuestion: {message}"
        answer = llm_call(BILLING_SYSTEM_PROMPT, prompt)
        confidence = 0.85 if chunks else 0.2
    else:
        answer = (
            f"[stub] Based on {len(chunks)} matched policy snippet(s), here is the billing "
            f"explanation for: '{message}'"
        )
        confidence = 0.6 if chunks else 0.2

    return {"answer": answer, "sources": sources, "confidence": confidence}
