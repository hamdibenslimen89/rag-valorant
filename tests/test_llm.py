"""
tests/test_llm.py
Unit tests for models/llm.py — no real API calls.
"""
import os
import unittest
from unittest.mock import MagicMock, patch


class TestLLMClientMock(unittest.TestCase):
    """When GROQ_API_KEY is absent, LLMClient must use MockLLM."""

    def setUp(self):
        os.environ.pop("GROQ_API_KEY", None)

    def test_falls_back_to_mock(self):
        from models.llm import LLMClient, _MockLLM

        client = LLMClient()
        self.assertIsInstance(client._backend, _MockLLM)

    def test_mock_returns_string(self):
        from models.llm import LLMClient

        client = LLMClient()
        reply = client.chat("Hello")
        self.assertIsInstance(reply, str)
        self.assertTrue(len(reply) > 0)

    def test_chat_accepts_temperature_override(self):
        from models.llm import LLMClient

        client = LLMClient(temperature=0.5)
        reply = client.chat("Test", temperature=0.9)
        self.assertIsInstance(reply, str)


class TestLLMClientWithKey(unittest.TestCase):
    """When GROQ_API_KEY is set, LLMClient should use _GroqBackend."""

    def test_uses_groq_backend_when_key_set(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch("groq.Groq") as mock_groq_cls:
                mock_instance = MagicMock()
                mock_groq_cls.return_value = mock_instance

                mock_completion = MagicMock()
                mock_completion.choices[0].message.content = "Mocked reply"
                mock_instance.chat.completions.create.return_value = mock_completion

                from importlib import reload
                import models.llm as llm_module
                reload(llm_module)

                client = llm_module.LLMClient(api_key="test-key")
                from models.llm import _GroqBackend
                self.assertIsInstance(client._backend, _GroqBackend)


if __name__ == "__main__":
    unittest.main()
