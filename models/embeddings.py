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
    """

    def __init__(self, model_name: str = _EMBED_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self._model_name = model_name

    def name(self) -> str:
        """Return a unique name for this embedding function."""
        return f"sentence-transformers-{self._model_name.split('/')[-1]}"

    def __call__(self, input: List[str]) -> List[List[float]]:  # noqa: A002
        """Embed multiple texts."""
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

        self._ef = EmbeddingFunction()
        self._client = chromadb.PersistentClient(path=db_path)
        # Get or create collection with embedding function
        try:
            self._collection = self._client.get_collection(name=collection)
        except ValueError:
            # Collection doesn't exist, create it with embedding function
            self._collection = self._client.create_collection(
                name=collection,
                embedding_function=self._ef,  # type: ignore[arg-type]
            )

    def query(self, text: str, k: int = 4) -> List[str]:
        """Return up to *k* most-relevant document strings."""
        n = min(k, self._collection.count())
        if n == 0:
            return []
        # Compute embedding manually and pass to query
        query_embedding = self._ef([text])[0]
        results = self._collection.query(
            query_embeddings=[query_embedding],
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
