# Memory management for RAG
from db.supabase_client import supabase
from datetime import datetime
from collections import defaultdict

def store_chat(library, question, answer, chat_id, pdf_name=None):
    if not pdf_name:
        meta = get_metadata_for_library(library)
        pdf_name = meta.get("pdf_name") or meta.get("source") or library
    chat_data = {
        # "chat_id": chat_id,  # This column doesn't exist in the database
        "library": library,    # Use library as the chat identifier
        "question": question,
        "answer": answer,
        "timestamp": datetime.utcnow().isoformat(),
        "pdf_name": pdf_name
    }
    supabase.table("chat_history").insert(chat_data).execute()

def get_history(chat_id, limit=5):
    """
    Fetches the most recent chat history for a given chat session and pdf,
    limited by the `limit` parameter.
    """
    try:
        response = supabase.table("chat_history") \
            .select("question, answer, timestamp, pdf_name") \
            .eq("library", chat_id) \
            .order("timestamp", desc=True) \
            .limit(limit) \
            .execute()
        
        # The API returns the most recent messages first, so we reverse them to maintain chronological order for the prompt.
        return list(reversed(response.data)) if response.data else []
    except Exception as e:
        print(f"Error fetching history for library {chat_id}: {str(e)}")
        return []

def get_all_history():
    """
    Fetches all chat histories, processes them, and returns them in a format
    suitable for the frontend history page, including the PDF name if available.
    """
    response = supabase.table("chat_history").select("*",).order("timestamp", desc=True).execute()

    if not response.data:
        return []

    # Group chats by library
    chats_by_library = defaultdict(list)
    for chat in response.data:
        if chat.get('library'):
            chats_by_library[chat['library']].append(chat)

    # Process each chat session's history
    processed_history = []
    for library, chats in chats_by_library.items():
        # Sort chats by timestamp to correctly identify the first and last message
        chats.sort(key=lambda x: x['timestamp'])
        if not chats:
            continue
        first_chat = chats[0]
        last_chat = chats[-1]
        library_name = first_chat.get('library', '')
        pdf_name = first_chat.get('pdf_name') or library_name
        processed_history.append({
            "id": library,  # Use library as the ID
            "libraryName": library_name,
            "libraryId": library,  # Use library as the libraryId
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

def delete_history(chat_id: str):
    """
    Deletes all chat history for a given library.
    """
    from db.supabase_client import supabase
    response = supabase.table("chat_history").delete().eq("library", chat_id).execute()
    return response
