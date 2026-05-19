"""
agent/core.py
Central orchestration: retrieve -> prompt -> LLM -> policy -> reply.
"""
from __future__ import annotations

from typing import Optional

from agent.state import AgentState
from agent.policy import apply as policy_apply


class Agent:
    """
    Parameters
    ----------
    llm          : models.llm.LLMClient  (or any object with .chat(prompt) -> str)
    vectorstore  : models.embeddings.VectorStore (or any object with .query(text, k) -> list[str])
    prompt_templates : dict with at least key "qa" containing a str template
                       with placeholders {context} and {query}.
    top_k        : number of chunks to retrieve (default 4)
    """

    def __init__(
        self,
        llm,
        vectorstore,
        prompt_templates: dict,
        top_k: int = 4,
    ) -> None:
        self.llm = llm
        self.vectorstore = vectorstore
        self.prompt_templates = prompt_templates
        self.top_k = top_k
        self.state = AgentState()

    def answer(self, query: str) -> str:
        """
        Full pipeline:
          1. Retrieve relevant chunks.
          2. Build a prompt from the QA template.
          3. Call the LLM.
          4. Run policy / safety filter.
          5. Persist to state and return.
        """
        self.state.last_query = query

        chunks: list[str] = self._retrieve(query)
        self.state.last_context = chunks

        prompt = self._build_prompt(query, chunks)

        raw = self.llm.chat(prompt)

        final = policy_apply(query, chunks, raw)

        self.state.add("user", query)
        self.state.add("assistant", final)

        return final

    def reset(self) -> None:
        """Clear session state."""
        self.state.reset()

    def _retrieve(self, query: str) -> list[str]:
        try:
            return self.vectorstore.query(query, k=self.top_k)
        except Exception as exc:  # noqa: BLE001
            print(f"[Agent] Retrieval error: {exc}")
            return []

    def _build_prompt(self, query: str, chunks: list[str]) -> str:
        context = "\n\n".join(chunks) if chunks else ""
        template: str = self.prompt_templates.get("qa", _DEFAULT_QA_TEMPLATE)
        return template.format(context=context, query=query)


_DEFAULT_QA_TEMPLATE = (
    "You are a knowledgeable Valorant assistant. "
    "Use ONLY the context below to answer the question.\n\n"
    "Context:\n{context}\n\n"
    "Question: {query}\n\n"
    "Answer concisely and accurately:"
)
