"""
models/llm.py
Thin wrapper around the Groq chat-completion API.
Falls back to MockLLM when GROQ_API_KEY is absent (useful for tests / CI).
"""
from __future__ import annotations

import os
from typing import Optional


class LLMClient:
    """
    Parameters
    ----------
    model       : Groq model id (default: llama3-8b-8192)
    temperature : sampling temperature
    api_key     : overrides GROQ_API_KEY env var
    """

    DEFAULT_MODEL = "llama3-8b-8192"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.2,
        api_key: Optional[str] = None,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self._api_key = api_key or os.getenv("GROQ_API_KEY", "")

        if not self._api_key:
            print("[LLMClient] GROQ_API_KEY not set — using MockLLM.")
            self._backend = _MockLLM()
        else:
            self._backend = _GroqBackend(
                api_key=self._api_key,
                model=self.model,
                temperature=self.temperature,
            )

    def chat(self, prompt: str, temperature: Optional[float] = None) -> str:
        """Send *prompt* and return the assistant reply as a plain string."""
        temp = temperature if temperature is not None else self.temperature
        return self._backend.chat(prompt, temp)


class _GroqBackend:
    def __init__(self, api_key: str, model: str, temperature: float) -> None:
        from groq import Groq  # lazy import so tests work without groq installed
        self._client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def chat(self, prompt: str, temperature: float) -> str:
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return completion.choices[0].message.content or ""


class _MockLLM:
    """Returns a canned response — zero external deps, perfect for tests."""

    CANNED = (
        "[MockLLM] GROQ_API_KEY is not configured. "
        "This is a placeholder response for local testing."
    )

    def chat(self, prompt: str, temperature: float = 0.2) -> str:  # noqa: ARG002
        return self.CANNED
