"""
Plan Info Domain Agent.

Answers questions about current/available plans using RAG over the plan
catalog. Can recommend a switch but never executes one — same
read-only-until-confirmed pattern as the billing agent.
"""
from app.rag.retriever import retrieve

PLAN_SYSTEM_PROMPT = """You are a plans specialist for a telecom company.
Answer using ONLY the provided context about plans and pricing. If asked to recommend a plan,
explain the trade-offs (price vs data vs features) rather than just naming one. Never claim
you've switched the customer's plan — only a human or a confirmed action can do that.
Always cite which source doc you used."""


def answer_plan_query(message: str, llm_call=None) -> dict:
    chunks = retrieve(message, k=3)
    context = "\n\n".join(c["text"] for c in chunks)
    sources = [c["source"] for c in chunks]

    if llm_call is not None:
        prompt = f"Context:\n{context}\n\nQuestion: {message}"
        answer = llm_call(PLAN_SYSTEM_PROMPT, prompt)
        confidence = 0.85 if chunks else 0.2
    else:
        answer = (
            f"[stub] Based on {len(chunks)} matched plan snippet(s), here is the plan "
            f"info for: '{message}'"
        )
        confidence = 0.6 if chunks else 0.2

    return {"answer": answer, "sources": sources, "confidence": confidence}
