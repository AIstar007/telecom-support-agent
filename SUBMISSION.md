# Telecom Support Copilot
**Role target: AI Engineer **

## Problem
DTDL's products span billing, plans, WiFi/mobile services, and OTT — each with its own
FAQ/policy corpus and backend. Customers bounce between IVR, chat, and human agents to get
a straight answer on things like "why is my bill higher this month" or "can I switch plans
mid-cycle." That's slow for the customer and expensive to staff.

## What it does
A multi-agent support copilot that answers billing/plan/troubleshooting questions grounded in
DTDL's own policy documents, and escalates to a human when it's not confident or the request
needs an account mutation (refund, plan change).

## Architecture
```
User query
   │
   ▼
[Intent Router Agent] ──► classifies: billing | plan_info | troubleshooting | out_of_scope
   │
   ▼
[RAG Retriever] ──► ChromaDB vector store of policy docs, plan catalogs, T&Cs
   │
   ▼
[Domain Agent] ──► Billing Agent / Plan Agent / Troubleshooting Agent
   │  (each has its own system prompt + tool access, e.g. billing lookup, plan comparison)
   ▼
[Confidence Gate] ──► if low confidence or mutating action → Escalation Agent (hands off to human)
   │
   ▼
Response + citations to source policy doc
```

- **Orchestration**: LangGraph state machine (router → retriever → domain agent → gate), not a
  single monolithic prompt — keeps each agent's responsibility narrow and testable.
- **RAG**: chunked policy PDFs/markdown → embeddings → ChromaDB, top-k retrieval with source
  citation returned alongside the answer (so support agents can audit it).
- **Guardrails**: domain agents can only *read* account data via tools; anything that mutates
  state (refund, plan switch) is routed to the Escalation Agent, never auto-executed.

## Tech stack
Python · FastAPI · LangGraph/LangChain · ChromaDB · OpenAI/Azure OpenAI · Docker

## What's in this scaffold
- `app/main.py` — FastAPI entrypoint, `/chat` endpoint
- `app/agents/orchestrator.py` — LangGraph-style state machine wiring the agents together
- `app/agents/intent_agent.py`, `billing_agent.py`, `escalation_agent.py` — domain agents
- `app/rag/ingest.py` — chunk + embed + load policy docs into ChromaDB
- `app/rag/retriever.py` — retrieval wrapper with citation metadata
- `requirements.txt`, `Dockerfile`, `.env.example`

## Not yet built (next steps if advanced to build round)
- Real DTDL policy corpus (scaffold uses sample docs in `data/`)
- Auth + real account-lookup tool integration
- Eval harness for answer groundedness (see Senior AI Engineer submission for that pattern)
