# Valorant Knowledge Agent

A modular RAG (Retrieval-Augmented Generation) agent that answers questions
about Valorant using a local Chroma vector database and the Groq LLM API.

## Project Structure

```
rag-valorant-main/
├── agent/                  # Core orchestration
│   ├── core.py             #   Agent class: retrieve → prompt → LLM → policy
│   ├── policy.py           #   Safety filter & response policy
│   └── state.py            #   Session state (history, last context)
├── connectors/
│   └── groq_client.py      # Low-level Groq HTTP adapter
├── models/
│   ├── embeddings.py       # EmbeddingFunction + VectorStore (Chroma)
│   └── llm.py              # LLMClient (Groq) with MockLLM fallback
├── prompts/
│   └── templates.py        # Prompt templates
├── tools/
│   ├── pdf_loader.py       # PDF → pages → chunks
│   └── search.py           # Web search helper
├── ui/
│   └── app.py              # Gradio GUI entrypoint
├── data/                   # Source data assets
│   └── valorant_knowledge.pdf
├── db/                     # Persisted Chroma vector DB
├── tests/                  # Unit tests
│   ├── test_llm.py
│   ├── test_agent.py
│   └── test_policy.py
├── rag.py                  # Ingestion pipeline: PDF → Chroma
├── scraper.py              # Standalone web scraper
├── requirements.txt
├── .env.example
└── README.md
```

## Quickstart

### 1 — Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2 — Configure environment

```bash
copy .env.example .env
```

Edit `.env` and set `GROQ_API_KEY`.

> If you do not set `GROQ_API_KEY`, the app still runs in local test mode with a
> `MockLLM` response.

### 3 — Ingest the knowledge base

Place `data/valorant_knowledge.pdf` into `data/`, then run:

```bash
python rag.py
```

This creates or updates the local `db/` directory.

### 4 — Launch the UI

```bash
python ui\app.py
```

Then open `http://localhost:7860` in your browser.

## Running tests

```bash
python -m pytest tests/ -v
```

## Notes

- `rag.py` builds the vector store from PDF content.
- `ui/app.py` is the current user-facing interface.
- Root `app.py` remains as the original Tkinter GUI.
- `models/llm.py` uses `MockLLM` if `GROQ_API_KEY` is missing.
