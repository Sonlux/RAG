import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat, upload, history, libraries, auth
from ingestion.pdf_loader import extract_pdf_flexibly
from ingestion.chunker import split_text_into_chunks
from ingestion.embed_store import embed_and_store
from rag_pipeline.rag_chain import answer_question
from rag_pipeline.memory_manager import store_chat, get_history
from fastapi.staticfiles import StaticFiles
from pathlib import Path

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="BookBot API",
    description="A RAG-based PDF QA system API",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://localhost:5173"],  # Allow frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Register routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(history.router, tags=["History"])
app.include_router(libraries.router, tags=["Libraries"])
app.include_router(auth.router, tags=["Authentication"])

# Mount static files for PDF preview
app.mount("/pdf", StaticFiles(directory="uploads"), name="pdf")

# CLI functions below kept for backward compatibility
def ingest_pdf(file_path: str, library: str):
    print(f"\n📥 Ingesting PDF: {file_path} into library: {library}")
    docs = extract_pdf_flexibly(file_path)
    print(f"✅ Extracted {len(docs)} document chunks.")
    embed_and_store(docs, metadata={"library": library})
    print(f"✅ Embedded and stored in ChromaDB.")

def chat_loop(library: str):
    print(f"\n💬 Entering chat mode for library: {library}")
    while True:
        query = input("❓ You: ")
        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting chat.")
            break

        # Get history before answering
        history = get_history(library)

        print("🤖 Bot: ", end="", flush=True)
        # Pass history to the RAG chain
        answer = answer_question(query, library, history)
        print()  # For newline after stream output
        store_chat(library, query, answer)

def show_history(library: str):
    print(f"\n📜 Chat History for Library: {library}")
    history = get_history(library)
    if not history:
        print("No history yet.")
    for chat in history:
        print(f"🗨️ Q: {chat['question']}")
        print(f"   A: {chat['answer']}\n")

def main():
    print("=== 📚 BookBot CLI ===")
    while True:
        print("\nOptions:")
        print("1. Ingest PDF")
        print("2. Chat with Library")
        print("3. View History")
        print("4. Exit")

        choice = input("Select an option (1–4): ").strip()

        if choice == "1":
            path = input("Enter path to PDF: ").strip()
            lib = input("Enter library name: ").strip()
            ingest_pdf(path, lib)

        elif choice == "2":
            lib = input("Enter library name: ").strip()
            chat_loop(lib)

        elif choice == "3":
            lib = input("Enter library name: ").strip()
            show_history(lib)

        elif choice == "4":
            print("🚪 Goodbye!")
            break

        else:
            print("⚠️ Invalid option. Try again.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
