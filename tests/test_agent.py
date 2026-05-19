"""
tests/test_agent.py
Unit tests for agent/core.py — LLM and VectorStore are mocked.
"""
import unittest
from unittest.mock import MagicMock

from agent.core import Agent
from agent.policy import NO_INFO_REPLY
from prompts.templates import TEMPLATES


def _make_agent(chunks=None, llm_reply="Test answer."):
    mock_llm = MagicMock()
    mock_llm.chat.return_value = llm_reply

    mock_vs = MagicMock()
    mock_vs.query.return_value = chunks if chunks is not None else ["Jett is a duelist."]

    return Agent(llm=mock_llm, vectorstore=mock_vs, prompt_templates=TEMPLATES)


class TestAgentAnswer(unittest.TestCase):

    def test_returns_string(self):
        agent = _make_agent()
        result = agent.answer("Who is Jett?")
        self.assertIsInstance(result, str)

    def test_calls_llm_once(self):
        agent = _make_agent()
        agent.answer("Who is Jett?")
        agent.llm.chat.assert_called_once()

    def test_retrieval_called_with_query(self):
        agent = _make_agent()
        agent.answer("Tell me about Sage")
        agent.vectorstore.query.assert_called_once_with("Tell me about Sage", k=4)

    def test_empty_context_returns_no_info(self):
        agent = _make_agent(chunks=[])
        result = agent.answer("Random question")
        self.assertEqual(result, NO_INFO_REPLY)

    def test_history_updated(self):
        agent = _make_agent()
        agent.answer("Who is Omen?")
        self.assertEqual(len(agent.state.history), 2)
        self.assertEqual(agent.state.history[0].role, "user")
        self.assertEqual(agent.state.history[1].role, "assistant")

    def test_reset_clears_history(self):
        agent = _make_agent()
        agent.answer("Who is Omen?")
        agent.reset()
        self.assertEqual(len(agent.state.history), 0)

    def test_blocked_query_returns_safe_reply(self):
        agent = _make_agent(chunks=["some context"])
        result = agent.answer("how to aimbot in valorant")
        self.assertIn("not able to help", result.lower())


class TestAgentPromptBuilding(unittest.TestCase):

    def test_prompt_contains_query_and_context(self):
        agent = _make_agent(chunks=["Reyna heals on kills."])
        captured = {}

        def capture(prompt, **_):
            captured["prompt"] = prompt
            return "answer"

        agent.llm.chat.side_effect = capture
        agent.answer("What does Reyna do?")

        self.assertIn("Reyna heals on kills.", captured["prompt"])
        self.assertIn("What does Reyna do?", captured["prompt"])


if __name__ == "__main__":
    unittest.main()
