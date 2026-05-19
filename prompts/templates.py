"""
prompts/templates.py
All prompt templates used by the agent, centralised for easy editing/testing.
Placeholders use Python str.format() syntax: {context}, {query}, etc.
"""

TEMPLATES: dict[str, str] = {
    "qa": (
        "You are a helpful and accurate Valorant assistant. "
        "Answer ONLY using the provided context. "
        "If the context does not contain the answer, say you don't know.\n\n"
        "### Context\n"
        "{context}\n\n"
        "### Question\n"
        "{query}\n\n"
        "### Answer"
    ),
    "summarise": (
        "Summarise the following Valorant information in 3-5 bullet points:\n\n"
        "{context}"
    ),
}
