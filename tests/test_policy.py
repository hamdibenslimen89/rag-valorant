"""
tests/test_policy.py
Unit tests for agent/policy.py — pure functions, no mocks needed.
"""
import unittest
from agent.policy import apply, is_context_sufficient, is_safe_query, NO_INFO_REPLY


class TestIsSafe(unittest.TestCase):
    def test_normal_query_is_safe(self):
        self.assertTrue(is_safe_query("What are Jett's abilities?"))

    def test_blocked_term(self):
        self.assertFalse(is_safe_query("how to use aimbot"))

    def test_case_insensitive(self):
        self.assertFalse(is_safe_query("WALLHACK guide"))


class TestIsContextSufficient(unittest.TestCase):
    def test_non_empty_is_sufficient(self):
        self.assertTrue(is_context_sufficient(["chunk"]))

    def test_empty_is_not_sufficient(self):
        self.assertFalse(is_context_sufficient([]))


class TestApply(unittest.TestCase):
    def test_passes_through_clean_answer(self):
        result = apply("Who is Sage?", ["Sage heals."], "Sage is a healer.")
        self.assertEqual(result, "Sage is a healer.")

    def test_no_info_when_empty_context(self):
        result = apply("Who is Sage?", [], "Sage is a healer.")
        self.assertEqual(result, NO_INFO_REPLY)

    def test_blocked_query_overrides_context(self):
        result = apply("aimbot tips", ["lots of context"], "here you go")
        self.assertIn("not able to help", result.lower())

    def test_strips_whitespace(self):
        result = apply("Q?", ["ctx"], "  Answer.  ")
        self.assertEqual(result, "Answer.")


if __name__ == "__main__":
    unittest.main()
