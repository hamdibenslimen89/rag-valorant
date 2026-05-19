"""
Quick agent demo - run with: python run_agent_demo.py
"""
from agent.core import Agent
from models.llm import LLMClient
from models.embeddings import VectorStore
from prompts.templates import TEMPLATES

print("\n[Agent] Initializing...")
agent = Agent(llm=LLMClient(), vectorstore=VectorStore(), prompt_templates=TEMPLATES)
print("[Agent] Ready!\n")

queries = [
    "What is Jett?",
    "Tell me about Sage",
    "What are the game modes?"
]

for query in queries:
    print(f"❓ Query: {query}")
    response = agent.answer(query)
    print(f"🤖 Response: {response}\n")
    print("-" * 80)
