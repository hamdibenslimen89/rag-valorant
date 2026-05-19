"""
rag.py
Ingestion pipeline: PDF -> chunks -> embeddings -> Chroma DB.
Run once (or whenever the source PDF changes):
    python rag.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from models.embeddings import VectorStore
from tools.pdf_loader import load_pdf, chunk_text

PDF_PATH = Path("data/valorant_knowledge.pdf")
DB_PATH = "db"
COLLECTION = "valorant"
CHUNK_SIZE = 500
OVERLAP = 50


def ingest(
    pdf_path: Path = PDF_PATH,
    db_path: str = DB_PATH,
    collection: str = COLLECTION,
) -> int:
    """
    Load *pdf_path*, chunk it, and upsert into Chroma.
    Returns the total number of chunks stored.
    """
    if not pdf_path.exists():
        print(f"[rag] PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"[rag] Loading {pdf_path} …")
    pages = load_pdf(pdf_path)
    chunks = chunk_text(pages, chunk_size=CHUNK_SIZE, overlap=OVERLAP)
    print(f"[rag] {len(pages)} pages -> {len(chunks)} chunks")

    vs = VectorStore(db_path=db_path, collection=collection)
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    vs.add(documents=chunks, ids=ids)

    total = vs.count()
    print(f"[rag] Done. Collection '{collection}' now has {total} documents.")
    return total


if __name__ == "__main__":
    ingest()
