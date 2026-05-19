"""
agent/policy.py
Stateless safety and response-policy helpers.
"""

NO_INFO_REPLY = "I don't have enough information about that."

_BLOCKED_TERMS = {"hack", "cheat", "exploit", "aimbot", "wallhack"}


def is_context_sufficient(chunks: list[str]) -> bool:
    """Return False when retrieval came back empty."""
    return bool(chunks)


def is_safe_query(query: str) -> bool:
    """Basic keyword blocklist. Returns True when query is acceptable."""
    lower = query.lower()
    return not any(term in lower for term in _BLOCKED_TERMS)


def apply(query: str, chunks: list[str], raw_answer: str) -> str:
    """
    Central policy gate.

    Order:
      1. Safety check on query.
      2. Sufficiency check on retrieved context.
      3. Return raw_answer if everything passes.
    """
    if not is_safe_query(query):
        return "I'm not able to help with that request."

    if not is_context_sufficient(chunks):
        return NO_INFO_REPLY

    return raw_answer.strip()
