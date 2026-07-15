"""
Real LLM call wrapper using Azure OpenAI.

If the required Azure OpenAI environment variables are not set,
returns None so callers fall back to their stub logic.

If Azure OpenAI is configured but the call fails (timeout, rate limit,
service outage, etc.), this also returns None rather than raising,
allowing the application to degrade gracefully.
"""

import logging
import os

from openai import AzureOpenAI

logger = logging.getLogger("copilot.llm")

_client = None


def _get_client():
    global _client

    if _client is None:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")

        if not all([api_key, endpoint, api_version]):
            return None

        _client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
            timeout=10.0,
        )

    return _client


def llm_call(
    system_prompt: str,
    user_message: str,
    model: str = "gpt-4o-mini",
) -> str | None:
    """
    Execute a chat completion using Azure OpenAI.

    The 'model' argument is retained for backward compatibility.
    Azure uses deployment names, so AZURE_OPENAI_DEPLOYMENT takes
    precedence if it is configured.
    """

    client = _get_client()

    if client is None:
        return None

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", model)

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content

    except Exception:
        logger.exception(
            "Azure OpenAI call failed — falling back to stub logic"
        )
        return None
