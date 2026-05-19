"""
Interactive chat interface with the Valorant agent.
Type your questions and get answers in real-time.
"""
from agent.core import Agent
from models.llm import LLMClient
from models.embeddings import VectorStore
from prompts.templates import TEMPLATES

def main():
    print("=" * 70)
    print("🎮 VALORANT AGENT - INTERACTIVE CHAT")
    print("=" * 70)
    print("\n[Loading agent...]")
    
    agent = Agent(
        llm=LLMClient(),
        vectorstore=VectorStore(),
        prompt_templates=TEMPLATES
    )
    
    print("[Agent ready!]\n")
    print("💬 Type your questions about Valorant. Type 'exit' or 'quit' to end.\n")
    print("-" * 70)
    
    while True:
        try:
            # Get user input
            user_input = input("\n❓ You: ").strip()
            
            # Exit conditions
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            # Skip empty input
            if not user_input:
                print("(Please ask a question)")
                continue
            
            # Get agent response
            print("\n🤖 Agent: ", end="", flush=True)
            response = agent.answer(user_input)
            print(response)
            print("-" * 70)
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat ended.\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
