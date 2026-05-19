from agent.core import Agent
from models.llm import LLMClient
from models.embeddings import VectorStore
from prompts.templates import TEMPLATES

print("[Agent] Initializing...")
agent = Agent(llm=LLMClient(), vectorstore=VectorStore(), prompt_templates=TEMPLATES)
print("[Agent] Ready!\n")

query = "who won vct champions 2025"
print(f"❓ Query: {query}")
response = agent.answer(query)
print(f"🤖 Response: {response}\n")
