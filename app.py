import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI

class ChatGPTStyleInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Valorant AI Companion")
        self.root.geometry("900x650")
        self.root.configure(bg="#202123")
        
        self.db = None
        self.client = None
        
        # --- CHAT WRAPPERS ---
        self.canvas = tk.Canvas(self.root, bg="#343541", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#343541")
        
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=860)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom Input Area
        bottom_box = tk.Frame(self.root, bg="#343541")
        bottom_box.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        self.entry_input = tk.Text(bottom_box, height=2, font=("Arial", 11), bg="#40414f", fg="#ffffff", insertbackground="#ffffff", bd=0, padx=10, pady=8)
        self.entry_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry_input.bind("<Return>", self.hit_enter_signal)
        
        self.btn_send = tk.Button(bottom_box, text="Send", font=("Arial", 10, "bold"), bg="#10a37f", fg="#ffffff", activebackground="#1a7f64", bd=0, padx=25, cursor="hand2", command=self.process_chat)
        self.btn_send.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.post_bubble("System", "Chat window ready. Connected to your standalone database folder.")
        
        # Mount your pre-built terminal data instantly
        threading.Thread(target=self.mount_prebuilt_db, daemon=True).start()

    def post_bubble(self, user, text):
        bg = "#343541" if user == "You" else "#444654"
        fg = "#ffffff" if user == "You" else "#ececf1"
        header = "👤 You:\n" if user == "You" else "🤖 Assistant:\n"
        
        row_frame = tk.Frame(self.scroll_frame, bg=bg, padx=25, pady=15)
        row_frame.pack(fill=tk.X, anchor="w")
        
        lbl = tk.Label(row_frame, text=f"{header}{text}", font=("Arial", 11), bg=bg, fg=fg, justify="left", anchor="w", wraplength=800)
        lbl.pack(fill=tk.X, anchor="w")
        
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def hit_enter_signal(self, event):
        self.process_chat()
        return "break"

    def mount_prebuilt_db(self):
        if not os.path.exists("db"):
            messagebox.showerror("Database Error", "No 'db' folder detected! Run 'python rag.py' in your terminal first to build it.")
            return
        
        try:
            emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.db = Chroma(persist_directory="db", embedding_function=emb)
            self.client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to hook database configs: {e}")

    def process_chat(self):
        query = self.entry_input.get("1.0", tk.END).strip()
        if not query or not self.db: return
        
        self.entry_input.delete("1.0", tk.END)
        self.post_bubble("You", query)
        
        def run_inference():
            try:
                results = self.db.similarity_search(query, k=6)
                context = "\n\n".join([r.page_content for r in results])
                prompt = f"""You are a Valorant expert assistant.\nUse the context below to answer the question as accurately as possible.\nIf the answer is not in the context, say "I don't have enough information about that."\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"""
                
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                self.root.after(0, lambda: self.post_bubble("Assistant", response.choices[0].message.content))
            except Exception as e:
                self.root.after(0, lambda: self.post_bubble("Assistant", f"Inference pipeline crash: {e}"))
                
        threading.Thread(target=run_inference, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGPTStyleInterface(root)
    root.mainloop()