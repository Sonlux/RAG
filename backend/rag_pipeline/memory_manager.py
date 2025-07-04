# Memory management for RAG
from db.supabase_client import supabase
from datetime import datetime
from collections import defaultdict

def store_chat(library, question, answer, pdf_name=None):
    if not pdf_name:
        meta = get_metadata_for_library(library)
        pdf_name = meta.get("pdf_name") or meta.get("source") or library
    chat_data = {
        "library": library,
        "question": question,
        "answer": answer,
        "timestamp": datetime.utcnow().isoformat(),
        "pdf_name": pdf_name
    }
    supabase.table("chat_history").insert(chat_data).execute()

def get_history(library, limit=5):
    """
    Fetches the most recent chat history for a given library, limited by the `limit` parameter.
    """
    response = supabase.table("chat_history") \
        .select("question, answer") \
        .eq("library", library) \
        .order("timestamp", desc=True) \
        .limit(limit) \
        .execute()
    
    # The API returns the most recent messages first, so we reverse them to maintain chronological order for the prompt.
    return list(reversed(response.data)) if response.data else []

def get_all_history():
    """
    Fetches all chat histories, processes them, and returns them in a format
    suitable for the frontend history page, including the PDF name if available.
    """
    response = supabase.table("chat_history").select("*",).order("timestamp", desc=True).execute()

    if not response.data:
        return []

    # Group chats by library
    from collections import defaultdict
    chats_by_library = defaultdict(list)
    for chat in response.data:
        chats_by_library[chat['library']].append(chat)

    # Process each library's history
    processed_history = []
    for library_name, chats in chats_by_library.items():
        # Sort chats by timestamp to correctly identify the first and last message
        chats.sort(key=lambda x: x['timestamp'])
        if not chats:
            continue
        first_chat = chats[0]
        last_chat = chats[-1]
        # Try to get the PDF name from the first chat's metadata if available
        pdf_name = first_chat.get('pdf_name') or library_name
        processed_history.append({
            "id": library_name,
            "libraryName": library_name,
            "libraryId": library_name,
            "title": pdf_name,  # Use PDF name as title
            "lastMessage": last_chat.get('answer') if last_chat.get('answer') else last_chat['question'],
            "messageCount": len(chats),
            "timestamp": last_chat['timestamp'],
            "status": "active"
        })
    # Sort the final list by the most recent timestamp so newest conversations appear first
    processed_history.sort(key=lambda x: x['timestamp'], reverse=True)
    return processed_history

def get_metadata_for_library(library: str):
    """
    Fetch the most recent document metadata for a given library from the vector store.
    Returns a dict with at least 'pdf_name' if available.
    """
    from langchain_community.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    all_metadata = vectordb._collection.get(include=["metadatas"])
    if all_metadata and "metadatas" in all_metadata:
        for meta in all_metadata["metadatas"]:
            if meta and meta.get("library") == library:
                return meta
    return {}

def delete_history(library: str):
    """
    Deletes all chat history for a given library.
    """
    from db.supabase_client import supabase
    response = supabase.table("chat_history").delete().eq("library", library).execute()
    return response
