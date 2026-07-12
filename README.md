# 🤖 Telecom Support Copilot

**A multi-agent RAG support bot that answers billing, plan, and troubleshooting questions grounded in real policy docs — and knows when to hand off to a human.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange)
![Tests](https://img.shields.io/badge/tests-29%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)
![CI](https://github.com/AIstar007/telecom-support-copilot/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)

> Built for **The Talent Hack** (Deutsche Telekom Digital Labs) — AI Engineer track.
> See [`SUBMISSION.md`](./SUBMISSION.md) for the full hackathon write-up and architecture rationale.

---

## What it does

A customer asks a support question. The bot:
1. **Classifies intent** — billing, plan info, troubleshooting, or out of scope
2. **Retrieves** the relevant policy snippet via RAG (grounded, cited answers — no hallucinated policy)
3. **Routes** to a domain-specific agent that answers using *only* that retrieved context
4. **Escalates to a human** automatically if confidence is low, or if the request would mutate account state (refund, plan switch, cancellation) — the bot never executes those itself

```
                         ┌─────────────────────┐
   User message  ─────►  │   Intent Router      │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
          ┌────────────┐   ┌───────────────┐   ┌──────────────────┐
          │  Billing    │   │  Plan Info     │   │  Troubleshooting  │
          │  Agent      │   │  Agent         │   │  Agent            │
          └──────┬──────┘   └───────┬───────┘   └─────────┬─────────┘
                 │                  │                      │
                 └──────────────────┼──────────────────────┘
                                    ▼
                        ┌───────────────────────┐
                        │  RAG Retrieval          │
                        │  (ChromaDB + policy docs)│
                        └───────────┬─────────────┘
                                    ▼
                        ┌───────────────────────┐
                        │  Confidence Gate        │
                        │  (escalate if low-conf   │
                        │   or account-mutating)   │
                        └───────────┬─────────────┘
                          ┌─────────┴─────────┐
                          ▼                   ▼
                  Grounded answer      Escalate to human
                  + source citation    (ticket reference)
```

## Quick Start

```bash
git clone https://github.com/AIstar007/telecom-support-copilot.git
cd telecom-support-copilot
pip install -r requirements.txt

# Ingest the policy docs into the vector store (run once, or whenever docs change)
python -m app.rag.ingest

# Run the server
uvicorn app.main:app --reload
```

Try it:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo", "message": "why is my bill higher this month"}'
```

**Zero setup required to see it work** — every agent falls back to deterministic stub logic if no `OPENAI_API_KEY` is set, so retrieval, routing, and escalation are all real and testable immediately. Drop a key into `.env` (copy `.env.example`) to get real generated answers instead of stub text.

### Run the tests

```bash
pip install -r requirements-dev.txt
pytest tests/ --cov=app --cov-report=term-missing
```
29 tests, 85% coverage — intent classification, retrieval, all three domain agents, the escalation gate, orchestrator error handling, and the actual HTTP API layer (via FastAPI's `TestClient`).

### Docker

```bash
docker build -t telecom-support-copilot .
docker run -p 8000:8000 --env-file .env telecom-support-copilot
```

## Design notes

- **RAG uses a local, dependency-free hashing embedder** (`app/rag/embeddings.py`) instead of downloading a sentence-transformer model — this keeps the project runnable in network-locked environments with zero external calls. It's a real, working embedder (keyword-overlap based), not a semantic one; swap in OpenAI/sentence-transformer embeddings for production-grade semantic search. This trade-off is documented in the module itself.
- **Chunking is section-aware**, not fixed-character-window — splitting on markdown `##` headers keeps each chunk topically coherent, which matters more for retrieval quality than raw chunk size.
- **The escalation gate is deterministic**, not an LLM self-report — mutating requests (refund, cancel, switch plan) are caught by keyword rule, and low-confidence answers are caught by a numeric threshold. The model proposes answers; it never decides on its own that it's "confident enough."
- **Every agent accepts an injectable `llm_call`** — this is what makes the whole pipeline unit-testable without hitting a real API (see `tests/`), and is also how `app/main.py` conditionally wires in the real OpenAI client only when a key is present.

## Project structure

```
app/
├── agents/
│   ├── intent_agent.py         # classifies billing / plan_info / troubleshooting / out_of_scope
│   ├── billing_agent.py        # RAG-grounded billing answers
│   ├── plan_agent.py           # RAG-grounded plan comparisons
│   ├── troubleshooting_agent.py# RAG-grounded troubleshooting steps
│   ├── escalation_agent.py     # deterministic escalation gate
│   └── orchestrator.py         # wires the above into a pipeline, with error handling
├── rag/
│   ├── embeddings.py           # offline hashing embedder
│   ├── ingest.py                # chunk + embed + load policy docs
│   └── retriever.py             # retrieval wrapper, fails soft to []
├── llm.py                       # real OpenAI client wrapper (used only if API key present)
└── main.py                      # FastAPI app
data/policies/                   # sample policy docs (billing, plans, troubleshooting)
tests/                           # 29 tests across all of the above
```

## What's not built yet

- Real DTDL policy corpus (currently sample docs)
- Auth + real account-lookup integration
- Semantic embeddings (currently keyword-overlap based, by design — see Design notes)

## License

MIT
