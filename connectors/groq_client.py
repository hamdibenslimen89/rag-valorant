"""
connectors/groq_client.py
Low-level adapter for the Groq API.
models/llm.py builds on top of this; you can also use it directly.
"""
from __future__ import annotations

import os
from typing import Optional


class GroqClient:
    """
    Direct Groq connector — separated from LLMClient so the transport
    layer can be swapped (e.g. async, streaming) without touching model logic.
    """

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3-8b-8192",
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model

        if not self.api_key:
            raise EnvironmentError(
                "GROQ_API_KEY is not set. "
                "Export it or pass api_key= explicitly."
            )

    def complete(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """
        Send a list of OpenAI-style messages and return the reply text.
        """
        import json
        import urllib.request

        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        ).encode()

        req = urllib.request.Request(
            self.BASE_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())

        return data["choices"][0]["message"]["content"]
