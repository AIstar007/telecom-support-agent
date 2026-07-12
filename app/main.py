"""
Telecom Support Copilot — FastAPI entrypoint.

POST /chat  -> routes a user query through the agent orchestrator and returns
               a grounded answer with source citations, or an escalation flag.
"""
import os

from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.orchestrator import run_pipeline
from app.llm import llm_call as real_llm_call

app = FastAPI(title="Telecom Support Copilot", version="0.1.0")

# Only wire the real model call if a key is actually present — otherwise every
# agent uses its built-in stub logic, so the app runs with zero setup.
ACTIVE_LLM_CALL = real_llm_call if os.environ.get("OPENAI_API_KEY") else None


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    escalated: bool
    intent: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = run_pipeline(req.message, llm_call=ACTIVE_LLM_CALL)
    return ChatResponse(**result)
