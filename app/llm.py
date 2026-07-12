"""
Real LLM call wrapper — uses the OpenAI-compatible chat completions API.
Works with plain OpenAI (set OPENAI_API_KEY) or Azure OpenAI (set
AZURE_OPENAI_* vars and swap the client below).

If no API key is set, returns None so callers fall back to their stub logic
(every agent in this project already supports llm_call=None) — meaning the
app runs end-to-end with zero setup, and produces real model answers the
moment you add a key.

If a key IS set but the call fails (rate limit, timeout, outage), this also
returns None rather than raising, so a live API outage degrades to stub
answers / escalation instead of a 500 to the customer.
"""
import logging
import os

logger = logging.getLogger("copilot.llm")

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        from openai import OpenAI
        _client = OpenAI(api_key=api_key, timeout=10.0)
    return _client


def llm_call(system_prompt: str, user_message: str, model: str = "gpt-4o-mini") -> str | None:
    client = _get_client()
    if client is None:
        return None
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception:
        logger.exception("LLM call failed — falling back to stub logic")
        return None
