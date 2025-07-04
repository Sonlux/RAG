from .retriever import get_retriever
from .llm_interface import stream_llm
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List, Dict, Any
from ingestion.embed_store import count_unique_chapters, list_chapter_titles
import re

SIMILARITY_THRESHOLD = 0.5  # currently unused but can be used if you add score-based filtering later

def format_prompt(context_docs: List[Document], question: str, history: List[Dict[str, Any]] = None) -> str:
    context = "\n\n".join([f"--- Context Chunk {i+1} ---\n{doc.page_content}" for i, doc in enumerate(context_docs)])
    
    history_str = ""
    if history:
        history_str = "\n".join([f"Previous Q: {h['question']}\nPrevious A: {h['answer']}" for h in history])
        history_str = f"\n\n--- Conversation History ---\n{history_str}"

    return f"""You are BookBot, a friendly and conversational AI assistant for the digital library.
Your main goal is to provide clear and helpful answers based on the context from the library's books.

When the provided context is brief, like a table of contents, use your own knowledge to explain the topic in a friendly, easy-to-understand way.
For example, if the context only says "Chapter 3: Data Preprocessing," you should start by saying something like, "Well, Chapter 3 covers Data Preprocessing, which is a crucial step in any data project. It generally involves..." and then explain the concept.

Here is the context from the library:
{context}
{history_str}

Based on this context, your own knowledge, and the conversation history, please answer the question below.
If the question is unrelated to the document's content, answer it using your general knowledge, but mention that it's outside the scope of the library.
Question: {question}

If you cannot find the answer in the context and don't have relevant knowledge, please say:
"I'm sorry, but I couldn't find enough information in the library to answer that question."
"""

def resolve_followup_question(question: str, history: List[Dict[str, Any]]) -> str:
    """
    If the question is a follow-up (e.g., 'can you name them'), try to resolve pronouns using the last Q&A in history.
    """
    if not history or not question:
        return question
    last_qa = history[-1]
    last_q = last_qa.get('question', '').lower()
    last_a = last_qa.get('answer', '').lower()
    # If the last answer was about chapters, and the current question is 'can you name them', rewrite it
    if re.search(r'chapter', last_q) or re.search(r'chapter', last_a):
        if re.search(r'\b(them|those|these|it|names)\b', question, re.IGNORECASE):
            return 'What are the chapters present in this book?'
    # Add more rules as needed for other follow-up types
    return question

def answer_question(question: str, library: str, history: List[Dict[str, Any]] = None) -> str:
    # Resolve follow-up questions using history
    resolved_question = resolve_followup_question(question, history)
    # Special handling: count chapters if question asks for number of chapters
    if re.search(r"how many chapters|number of chapters|total chapters", resolved_question, re.IGNORECASE):
        count = count_unique_chapters(library)
        if count > 0:
            return f"This book has {count} chapters."
        else:
            return "Sorry, I couldn't find chapter information in this book."
    # Special handling: list chapters if question asks for chapter titles
    if re.search(r"what( are| were)?( the)? chapters|list chapters|chapter titles|chapters present", resolved_question, re.IGNORECASE):
        titles = list_chapter_titles(library)
        if titles:
            return "The chapters present in this book are:\n" + "\n".join(titles)
        else:
            return "Sorry, I couldn't find chapter titles in this book."
    retriever = get_retriever(library=library, question=resolved_question)
    docs = retriever.get_relevant_documents(resolved_question)
    # print(f"[DEBUG] Retrieved {len(docs)} context documents.")

    if not docs or len(docs) == 0:
        # print("[DEBUG] No context found. Performing keyword fallback.")

        embedding_fn = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectordb = Chroma(persist_directory="chroma_db", embedding_function=embedding_fn)

        all_docs = vectordb.similarity_search("chapter", k=30, filter={"library": library})
        fallback_docs = [doc for doc in all_docs if 'chapter' in doc.page_content.lower()]
        docs = fallback_docs[:5]
        # print(f"[DEBUG] Fallback found {len(docs)} chapter-related docs.")

    if not docs:
        return "Sorry, I couldn't find any relevant content for this question."

    # Optional: Show retrieved context chunks for debugging
    # for i, doc in enumerate(docs[:3]):
    #     print(f"\n--- Context Chunk {i+1} ---\n{doc.page_content[:300]}...\n")

    prompt = format_prompt(docs, question, history)
    # print("\n🤖 Bot: ", end="", flush=True)
    return stream_llm(prompt)
