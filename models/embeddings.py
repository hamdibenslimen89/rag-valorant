"""
models/embeddings.py
Wraps sentence-transformers embeddings and a Chroma collection behind
a single VectorStore interface used by the agent.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_DEFAULT_DB_PATH = str(Path(__file__).parent.parent / "db")
_DEFAULT_COLLECTION = "valorant"


class EmbeddingFunction:
    """
    Chroma-compatible embedding function backed by sentence-transformers.
    Can also be called standalone: ef(["text1", "text2"]) -> list[list[float]]
    """

    def __init__(self, model_name: str = _EMBED_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def __call__(self, input: List[str]) -> List[List[float]]:  # noqa: A002
        return self._model.encode(input, convert_to_numpy=True).tolist()


class VectorStore:
    """
    Thin wrapper around a persisted Chroma collection.
    """

    def __init__(
        self,
        db_path: str = _DEFAULT_DB_PATH,
        collection: str = _DEFAULT_COLLECTION,
    ) -> None:
        import chromadb
        from chromadb.config import Settings

        self._ef = EmbeddingFunction()
        self._client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=collection,
            embedding_function=self._ef,  # type: ignore[arg-type]
        )

    def query(self, text: str, k: int = 4) -> List[str]:
        """Return up to *k* most-relevant document strings."""
        n = min(k, self._collection.count())
        if n == 0:
            return []
        results = self._collection.query(
            query_texts=[text],
            n_results=n,
        )
        docs = results.get("documents", [[]])[0]
        return [d for d in docs if d]

    def add(
        self,
        documents: List[str],
        ids: List[str],
        metadatas: List[dict] | None = None,
    ) -> None:
        """Upsert *documents* into the collection."""
        kwargs: dict = {"documents": documents, "ids": ids}
        if metadatas:
            kwargs["metadatas"] = metadatas
        self._collection.upsert(**kwargs)

    def count(self) -> int:
        return self._collection.count()
