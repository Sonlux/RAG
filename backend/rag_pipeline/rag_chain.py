from .retriever import get_retriever
from .llm_interface import stream_llm
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List, Dict, Any
from ingestion.embed_store import count_unique_chapters, list_chapter_titles
import re

SIMILARITY_THRESHOLD = 0.5  # currently unused but can be used if you add score-based filtering later

def format_prompt(context_docs: List[Document], question: str, history: List[Dict[str, Any]] = None, show_sources: bool = False) -> str:
    # Join context with optional source information
    if show_sources:
        context_parts = []
        for i, doc in enumerate(context_docs):
            source_info = ""
            if doc.metadata:
                source = doc.metadata.get("source", "")
                page = doc.metadata.get("page_number", "")
                if source:
                    source_name = source.split("/")[-1] if "/" in source else source
                    source_info = f" (from {source_name}" + (f", page {page}" if page else "") + ")"
            context_parts.append(f"--- Document Section {i+1}{source_info} ---\n{doc.page_content}")
        context = "\n\n".join(context_parts)
    else:
        context = "\n\n".join([f"--- Document Section {i+1} ---\n{doc.page_content}" for i, doc in enumerate(context_docs)])
    
    history_str = ""
    if history:
        history_str = "\n".join([f"Previous Q: {h['question']}\nPrevious A: {h['answer']}" for h in history])
        history_str = f"\n\n--- Conversation History ---\n{history_str}"

    return f"""You are BookBot, a friendly and conversational AI assistant for a digital library.

CRITICAL RULES - YOU MUST FOLLOW THESE STRICTLY:
1. You can ONLY answer questions using information from the provided document context below.
2. If the question is NOT about the content in the provided context, you MUST say: "I'm sorry, but that question is not related to the content in this document. I can only answer questions about what's in the uploaded PDF."
3. DO NOT use your general knowledge to answer questions outside the document scope.
4. DO NOT answer questions about topics not present in the provided context.
5. If you're unsure whether information is in the context, say you don't have that information.

FORMATTING INSTRUCTIONS:
- NEVER refer to "Context", "Chunks", "Document Sections" or similar technical terms
- Format responses with proper paragraphs, bullet points, and spacing
- Be conversational and friendly, but stay strictly within the document content
- Do not mention where in the document you found information

DOCUMENT CONTENT:
{context}
{history_str}

USER QUESTION: {question}

Remember: If the question is about something NOT in the document content above (like Kubernetes, programming, current events, etc. when the document is about Harry Potter), you MUST refuse politely and remind the user you can only discuss the document's content.
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

def answer_question(question: str, library: str, pdf_name: str = None, history: List[Dict[str, Any]] = None) -> str:
    # Resolve follow-up questions using history
    resolved_question = resolve_followup_question(question, history)
    
    # Special handling: count chapters if question asks for number of chapters
    if re.search(r"how many chapters|number of chapters|total chapters", resolved_question, re.IGNORECASE):
        count = count_unique_chapters(library, pdf_name=pdf_name)
        if count > 0:
            return f"This book has {count} chapters."
        else:
            return "Sorry, I couldn't find chapter information in this book."
            
    # Special handling: list chapters if question asks for chapter titles
    if re.search(r"what( are| were)?( the)? chapters|list chapters|chapter titles|chapters present", resolved_question, re.IGNORECASE):
        titles = list_chapter_titles(library, pdf_name=pdf_name)
        if titles:
            return "The chapters present in this book are:\n" + "\n".join(titles)
        else:
            return "Sorry, I couldn't find chapter titles in this book."
            
    # Get retriever with optional PDF filtering
    try:
        retriever = get_retriever(library=library, question=resolved_question, pdf_name=pdf_name)
        # Use invoke instead of get_relevant_documents to avoid deprecation warning
        docs = retriever.invoke(resolved_question)
    except Exception as e:
        print(f"Error in retriever: {str(e)}")
        # Fallback to a simpler approach
        embedding_fn = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectordb = Chroma(persist_directory="chroma_db", embedding_function=embedding_fn)
        
        # Create a simple filter
        filter_dict = {"library": library}
        docs = vectordb.similarity_search(resolved_question, k=15, filter=filter_dict)
        
        # If pdf_name is provided, filter the results in memory
        if pdf_name and pdf_name != library:
            docs = [doc for doc in docs if pdf_name in doc.metadata.get("source", "")]

    if not docs or len(docs) == 0:
        # Fallback search, but still respect PDF filter if provided
        embedding_fn = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectordb = Chroma(persist_directory="chroma_db", embedding_function=embedding_fn)

        # Create filter that includes library only
        filter_dict = {"library": library}
        all_docs = vectordb.similarity_search("chapter", k=30, filter=filter_dict)
        
        # Filter by PDF name in memory
        if pdf_name and pdf_name != library:
            all_docs = [doc for doc in all_docs if pdf_name in doc.metadata.get("source", "")]
            
        fallback_docs = [doc for doc in all_docs if 'chapter' in doc.page_content.lower()]
        docs = fallback_docs[:5]

    if not docs:
        return "Sorry, I couldn't find any relevant content for this question."

    # Show sources when searching across library (pdf_name is None)
    show_sources = pdf_name is None
    prompt = format_prompt(docs, question, history, show_sources=show_sources)
    return stream_llm(prompt)
