"""
agent/state.py
Holds all mutable state for a single agent session.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Message:
    role: str          # "user" | "assistant" | "system"
    content: str


@dataclass
class AgentState:
    """Accumulates history and last-retrieved context for one session."""
    history: List[Message] = field(default_factory=list)
    last_context: List[str] = field(default_factory=list)
    last_query: Optional[str] = None

    def add(self, role: str, content: str) -> None:
        self.history.append(Message(role=role, content=content))

    def reset(self) -> None:
        self.history.clear()
        self.last_context.clear()
        self.last_query = None
