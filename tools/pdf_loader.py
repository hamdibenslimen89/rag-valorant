"""
tools/pdf_loader.py
Loads a PDF and returns a list of page-level text strings.
Used by rag.py during ingestion.
"""
from __future__ import annotations

from pathlib import Path


def load_pdf(path: str | Path) -> list[str]:
    """
    Return a list of strings, one per page.
    Requires: pypdf  (pip install pypdf)
    """
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError("Install pypdf: pip install pypdf") from exc

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append(text)
    return pages


def chunk_text(
    pages: list[str],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Split page texts into overlapping chunks of *chunk_size* characters.
    Simple character-level splitter — no external dependency.
    """
    full_text = "\n\n".join(pages)
    chunks, start = [], 0
    while start < len(full_text):
        end = start + chunk_size
        chunks.append(full_text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]
