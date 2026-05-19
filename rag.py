import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI
import shutil
import time

# -----------------------------
# 1. LOAD PDF
# -----------------------------
pdf_path = "data/valorant_knowledge.pdf"
if not os.path.exists(pdf_path):
    print(f"[RAG Error] {pdf_path} not found! Run 'python scraper.py' first.")
    exit(1)

loader = PyPDFLoader(pdf_path)
documents = loader.load()
print(f"[RAG] Loaded {len(documents)} pages from PDF")

# -----------------------------
# 2. CHUNKING
# -----------------------------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,   
    chunk_overlap=150  
)
chunks = splitter.split_documents(documents)
print(f"[RAG] Split into {len(chunks)} chunks")

# -----------------------------
# 3. EMBEDDINGS MODEL
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# 4. VECTOR DATABASE (With Windows Safe-Purge)
# -----------------------------
if os.path.exists("db"):
    print("[RAG] Wiping old vector directory safely...")
    try:
        shutil.rmtree("db")
    except PermissionError:
        # If Windows holds a file lock, wait a second and clear it cleanly
        time.sleep(1.0)
        shutil.rmtree("db", ignore_errors=True)

db = Chroma.from_documents(
    chunks,
    embedding_model,
    persist_directory="db"
)
print(f"[RAG] Vector DB built with {len(chunks)} chunks\n")

# -----------------------------
# 5. LLM CLIENT INITIALIZATION
# -----------------------------
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

print("=" * 50)
print("Valorant RAG Assistant — type 'exit' to quit")
print("=" * 50)

# -----------------------------
# REPETITIVE INTERACTIVE LOOP
# -----------------------------
while True:
    query = input("\nYour question:\n> ").strip()
    if query.lower() in ("exit", "quit"):
        break
    if not query:
        continue

    # -----------------------------
    # 6. RETRIEVAL
    # -----------------------------
    results = db.similarity_search(query, k=6)

    if not results:
        print("\n[!] No relevant chunks found.")
        continue

    context = "\n\n".join([r.page_content for r in results])

    # -----------------------------
    # 7. PROMPT
    # -----------------------------
    prompt = f"""You are a Valorant expert assistant.
Use the context below to answer the question as accurately as possible.
If the answer is not in the context, say "I don't have enough information about that."

Context:
{context}

Question: {query}

Answer:"""

    # -----------------------------
    # 8. LLM RESPONSE
    # -----------------------------
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2  
        )

        print("\n--- ANSWER ---")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"\n[!] Error calling API: {e}")