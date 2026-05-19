"""
ui/app.py
Thin Gradio GUI — imports Agent and delegates all logic to it.
Run with:
    python ui/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make sure project root is on sys.path when launched directly
sys.path.insert(0, str(Path(__file__).parent.parent))

import gradio as gr

from agent.core import Agent
from models.llm import LLMClient
from models.embeddings import VectorStore
from prompts.templates import TEMPLATES


def _build_agent() -> Agent:
    llm = LLMClient()
    vs = VectorStore()
    return Agent(llm=llm, vectorstore=vs, prompt_templates=TEMPLATES)


_agent = _build_agent()


def respond(message: str, history: list) -> str:
    if not message.strip():
        return ""
    return _agent.answer(message)


with gr.Blocks(title="Valorant Agent") as demo:
    gr.Markdown(
        "## 🎮 Valorant Knowledge Agent\n"
        "Ask anything about agents, maps, weapons, or mechanics."
    )

    chatbot = gr.ChatInterface(
        fn=respond,
        chatbot=gr.Chatbot(height=450),
        textbox=gr.Textbox(
            placeholder="e.g. What does Jett's Tailwind do?",
            container=False,
        ),
        retry_btn=None,
        undo_btn=None,
    )

    with gr.Row():
        gr.Button("🗑 Reset session").click(
            fn=lambda: _agent.reset() or "Session reset.",
            outputs=gr.Textbox(visible=False),
        )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
