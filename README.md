<div align="center">

# 🤖 Telecom Support Agent

### Multi-Agent · RAG-Grounded · Confidence-Gated Escalation

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B35?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com/)
[![Tests](https://img.shields.io/badge/Tests-29_Passing-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](./tests/)
[![Coverage](https://img.shields.io/badge/Coverage-85%25-22C55E?style=for-the-badge&logo=codecov&logoColor=white)](./tests/)
[![CI](https://img.shields.io/github/actions/workflow/status/AIstar007/telecom-support-agent/ci.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=CI)](https://github.com/AIstar007/telecom-support-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-6366F1?style=for-the-badge)](LICENSE)

<br/>

> **Answers billing, plan, and troubleshooting questions grounded in real policy docs —**  
> **and knows exactly when to hand off to a human.**

<br/>

> 🏆 Built for **[The Talent Hack](https://www.hackerearth.com/)** · Deutsche Telekom Digital Labs · AI Engineer Track  
> See [`SUBMISSION.md`](./SUBMISSION.md) for the full hackathon write-up and architecture rationale.

<br/>

[🚀 Quick Start](#-quick-start) · [🏗️ Architecture](#️-architecture) · [🔄 Agent Pipeline](#-agent-pipeline) · [🧪 Testing](#-testing) · [📂 Project Structure](#-project-structure) · [🎨 Design Notes](#-design-notes)

---

</div>

## ✨ How It Works

A customer sends a support message. The system:

| Step | Agent | Action |
|---|---|---|
| 1️⃣ | **Intent Router** | Classifies as billing / plan info / troubleshooting / out-of-scope |
| 2️⃣ | **Domain Agent** | Retrieves the relevant policy snippet via RAG — cited, grounded, no hallucination |
| 3️⃣ | **Confidence Gate** | Scores the answer; escalates automatically if confidence is low |
| 4️⃣ | **Escalation Guard** | Detects account-mutating requests (refund, plan switch, cancellation) — never executes them |
| 5️⃣ | **Response** | Returns grounded answer + source citation, or escalation ticket reference |

> 🔒 **The bot never mutates account state.** Refunds, plan switches, and cancellations are always escalated to a human agent.

---

## 🏗️ Architecture

```
                      ┌──────────────────────┐
  User message ──────▶│    Intent Router      │
                      └──────────┬───────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐
       │   Billing    │   │  Plan Info   │   │   Troubleshooting   │
       │   Agent      │   │  Agent       │   │   Agent             │
       └──────┬───────┘   └──────┬───────┘   └──────────┬──────────┘
              │                  │                       │
              └──────────────────┼───────────────────────┘
                                 ▼
                     ┌───────────────────────┐
                     │    RAG Retrieval       │
                     │  ChromaDB + Policy Docs │
                     └───────────┬────────────┘
                                 ▼
                     ┌───────────────────────┐
                     │   Confidence Gate      │
                     │  low-conf → escalate   │
                     │  mutating → escalate   │
                     └───────────┬────────────┘
                        ┌────────┴────────┐
                        ▼                 ▼
               Grounded Answer      Escalate to Human
               + Source Citation    (ticket reference)
```

---

## 🚀 Quick Start

### 1 · Clone & Install

```bash
git clone https://github.com/AIstar007/telecom-support-agent.git
cd telecom-support-agent
pip install -r requirements.txt
```

### 2 · Ingest Policy Docs

```bash
# Run once — or whenever your policy docs change
python -m app.rag.ingest
```

### 3 · Start the Server

```bash
uvicorn app.main:app --reload
```

### 4 · Try It

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo", "message": "why is my bill higher this month"}'
```

### 5 · (Optional) Add OpenAI Key

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

> ✅ **Zero setup required to see it work** — every agent falls back to deterministic stub logic when no `OPENAI_API_KEY` is set. Routing, retrieval, and escalation are all real and testable immediately. Drop a key in `.env` to get real LLM-generated answers.

### Docker

```bash
docker build -t telecom-support-agent .
docker run -p 8000:8000 --env-file .env telecom-support-agent
```

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
pytest tests/ --cov=app --cov-report=term-missing
```

**29 tests · 85% coverage** across:

| Test Area | Coverage |
|---|---|
| Intent classification | ✅ |
| RAG retrieval | ✅ |
| Billing agent | ✅ |
| Plan info agent | ✅ |
| Troubleshooting agent | ✅ |
| Escalation gate | ✅ |
| Orchestrator error handling | ✅ |
| HTTP API layer (FastAPI `TestClient`) | ✅ |

---

## 📂 Project Structure

```
telecom-support-agent/
│
├── 📁 app/
│   ├── 📁 agents/
│   │   ├── intent_agent.py           # billing / plan_info / troubleshooting / out_of_scope
│   │   ├── billing_agent.py          # RAG-grounded billing answers
│   │   ├── plan_agent.py             # RAG-grounded plan comparisons
│   │   ├── troubleshooting_agent.py  # RAG-grounded troubleshooting steps
│   │   ├── escalation_agent.py       # deterministic escalation gate
│   │   └── orchestrator.py           # full pipeline wiring + error handling
│   │
│   ├── 📁 rag/
│   │   ├── embeddings.py             # offline hashing embedder (no model download)
│   │   ├── ingest.py                 # chunk + embed + load policy docs
│   │   └── retriever.py              # retrieval wrapper, fails soft to []
│   │
│   ├── llm.py                        # OpenAI client (only wired in when key is present)
│   └── main.py                       # FastAPI app
│
├── 📁 data/policies/                 # sample billing, plan, troubleshooting docs
├── 📁 tests/                         # 29 tests across all layers
├── SUBMISSION.md                     # Hackathon write-up + architecture rationale
└── Dockerfile
```

---

## 🎨 Design Notes

### Embedder: Offline Hashing, No Model Download
`app/rag/embeddings.py` uses a keyword-overlap based hashing embedder — no `sentence-transformers`, no external calls. The project runs immediately in network-locked environments. This is a deliberate trade-off documented in the module; swap in OpenAI or sentence-transformer embeddings for production-grade semantic search.

### Section-Aware Chunking
Chunks split on markdown `##` headers — not fixed character windows. Topical coherence per chunk matters more for retrieval quality than raw chunk size.

### Deterministic Escalation Gate
The confidence gate is **not** an LLM self-report. Mutating requests (refund / cancel / switch plan) are caught by keyword rule; low-confidence answers are caught by a numeric threshold. The model proposes answers — it never decides on its own that it's "confident enough."

### Fully Injectable LLM Calls
Every agent accepts an injectable `llm_call` parameter. This is what makes the entire pipeline unit-testable without hitting a real API, and how `app/main.py` conditionally wires in the real OpenAI client only when a key is present.

---

## 🗺️ Roadmap

| Feature | Status |
|---|---|
| Real DTDL policy corpus | 🔜 Planned |
| Auth + real account-lookup integration | 🔜 Planned |
| Semantic embeddings (OpenAI / sentence-transformers) | 🔜 Planned (see Design Notes) |
| Streaming responses | 🔜 Planned |

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| API Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Vector Store | [ChromaDB](https://www.trychroma.com/) |
| LLM | [OpenAI](https://openai.com/) (optional — stubs work without it) |
| Embeddings | Offline hashing embedder (swap-ready for semantic) |
| Testing | [pytest](https://pytest.org/) + FastAPI `TestClient` |
| CI | GitHub Actions |
| Containerization | Docker |

---

<div align="center">

Built with ❤️ for Deutsche Telekom Digital Labs · The Talent Hack

[⭐ Star this repo](https://github.com/AIstar007/telecom-support-agent) · [🐛 Report an Issue](https://github.com/AIstar007/telecom-support-agent/issues) · [📄 Submission Write-up](./SUBMISSION.md)

</div>
