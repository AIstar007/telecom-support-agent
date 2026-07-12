"""
Troubleshooting Domain Agent.

Answers connectivity/service issues using RAG over troubleshooting guides.
Distinguishes "here's a self-serve fix" from "this needs a technician" —
the latter still routes through the Escalation Agent via the confidence
gate in the orchestrator, since dispatching a technician is a mutating,
account-level action.
"""
from app.rag.retriever import retrieve

TROUBLESHOOTING_SYSTEM_PROMPT = """You are a technical support agent for a telecom company.
Answer using ONLY the provided context. Give step-by-step self-serve troubleshooting steps
where possible. If the context suggests this needs a technician visit or network-side fix,
say so plainly rather than inventing a fix. Always cite which source doc you used."""


def answer_troubleshooting_query(message: str, llm_call=None) -> dict:
    chunks = retrieve(message, k=3)
    context = "\n\n".join(c["text"] for c in chunks)
    sources = [c["source"] for c in chunks]

    if llm_call is not None:
        prompt = f"Context:\n{context}\n\nIssue: {message}"
        answer = llm_call(TROUBLESHOOTING_SYSTEM_PROMPT, prompt)
        confidence = 0.85 if chunks else 0.2
    else:
        answer = (
            f"[stub] Based on {len(chunks)} matched troubleshooting snippet(s), here are "
            f"steps for: '{message}'"
        )
        confidence = 0.6 if chunks else 0.2

    return {"answer": answer, "sources": sources, "confidence": confidence}
