# Embedding and storage logic will go here
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
import os
import chromadb
from typing import List, Dict
import uuid
from datetime import datetime
import torch
import re

def get_device():
    return "cuda" if torch.cuda.is_available() else "cpu"

def sanitize_metadata(meta):
    """
    Recursively filter metadata to only allow str, int, float, bool, or None values (ChromaDB-compatible).
    Lists and dicts are converted to str, except empty lists which become None.
    """
    if isinstance(meta, dict):
        return {k: sanitize_metadata(v) for k, v in meta.items() if sanitize_metadata(v) is not None}
    elif isinstance(meta, list):
        if not meta:
            return None
        # Convert non-empty lists to comma-separated string
        return ", ".join(str(sanitize_metadata(v)) for v in meta if sanitize_metadata(v) is not None)
    elif isinstance(meta, (str, int, float, bool)) or meta is None:
        return meta
    else:
        return str(meta)

def embed_and_store(docs, persist_path="chroma_db", metadata={}):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": get_device()})
    vectordb = Chroma(persist_directory=persist_path, embedding_function=embeddings)

    # Attach metadata (sanitize for ChromaDB)
    for doc in docs:
        doc.metadata.update(metadata)
        doc.metadata = sanitize_metadata(doc.metadata)

    vectordb.add_documents(docs)
    vectordb.persist()
    return vectordb

def get_existing_libraries(persist_path="chroma_db") -> List[Dict]:
    """
    Get all existing libraries from the vector store
    """
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": get_device()})
        vectordb = Chroma(persist_directory=persist_path, embedding_function=embeddings)
        
        # Try to get all metadata
        all_metadata = vectordb._collection.get(include=["metadatas"])
        libraries = set()
        if all_metadata and "metadatas" in all_metadata:
            for metadata in all_metadata["metadatas"]:
                if metadata and "library" in metadata:
                    libraries.add(metadata["library"])
        
        # Format response
        result = []
        for lib in libraries:
            # Count unique PDF sources in this library, not document chunks
            unique_sources = set()
            if all_metadata and "metadatas" in all_metadata:
                for m in all_metadata["metadatas"]:
                    if m and "library" in m and m["library"] == lib and "source" in m:
                        unique_sources.add(m["source"])
            
            doc_count = len(unique_sources)
            
            result.append({
                "name": lib,
                "description": "",  # We don't store descriptions currently
                "doc_count": doc_count,
                "created_at": datetime.now().isoformat()  # Placeholder since we don't track creation time
            })
        
        # If no libraries found, return an empty list
        return result
    except Exception as e:
        print(f"Error retrieving libraries: {str(e)}")
        return []

def delete_library(library_name: str, persist_path="chroma_db") -> bool:
    """
    Delete all documents belonging to a library from the vector store.
    Returns True if any documents were deleted, False otherwise.
    """
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": get_device()})
        vectordb = Chroma(persist_directory=persist_path, embedding_function=embeddings)
        all_metadata = vectordb._collection.get(include=["metadatas"])
        ids_to_delete = []
        if all_metadata and "metadatas" in all_metadata and "ids" in all_metadata:
            for meta, doc_id in zip(all_metadata["metadatas"], all_metadata["ids"]):
                if meta and "library" in meta and meta["library"] == library_name:
                    ids_to_delete.append(doc_id)
        if ids_to_delete:
            vectordb._collection.delete(ids=ids_to_delete)
            vectordb.persist()
            return True
        return False
    except Exception as e:
        print(f"Error deleting library: {str(e)}")
        return False

def get_pdfs_for_library(library_name: str, persist_path="chroma_db"):
    """
    Return a list of unique PDFs (with metadata) for a given library.
    """
    import os
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": get_device()})
    vectordb = Chroma(persist_directory=persist_path, embedding_function=embeddings)
    all_metadata = vectordb._collection.get(include=["metadatas"])
    pdfs = {}
    if all_metadata and "metadatas" in all_metadata:
        for meta in all_metadata["metadatas"]:
            if meta and "library" in meta and meta["library"] == library_name:
                source = meta.get("source", None)
                if source and source not in pdfs:
                    pdfs[source] = {
                        "id": source,
                        "name": os.path.basename(source),
                        "size": meta.get("size", 0),
                        "tags": meta.get("tags", []),
                        "uploadedAt": meta.get("uploadedAt", ""),
                        "status": "ready"
                    }
    return list(pdfs.values())

def count_unique_chapters(library_name: str, pdf_name: str = None, persist_path="chroma_db") -> int:
    """
    Count unique chapters in the vector store for a given library by scanning section_title metadata.
    If pdf_name is provided, only count chapters from that specific PDF.
    Returns the number of unique chapters (case-insensitive, e.g., 'Chapter 1', 'chapter 1' are the same).
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": get_device()})
    vectordb = Chroma(persist_directory=persist_path, embedding_function=embeddings)
    all_metadata = vectordb._collection.get(include=["metadatas"])
    chapters = set()
    if all_metadata and "metadatas" in all_metadata:
        for meta in all_metadata["metadatas"]:
            # Check if this document belongs to the specified library and PDF (if provided)
            if meta and "library" in meta and meta["library"] == library_name:
                # If pdf_name is provided, check if this document is from that PDF
                if pdf_name and pdf_name != library_name:
                    source = meta.get("source", "")
                    if not source or pdf_name not in source:
                        continue
                
                section = meta.get("section_title", "")
                if section and section.lower().startswith("chapter"):
                    # Normalize to just 'chapter X' (ignore trailing text)
                    match = re.match(r"chapter\s+\d+", section, re.IGNORECASE)
                    if match:
                        chapters.add(match.group(0).lower())
    return len(chapters)

def list_chapter_titles(library_name: str, pdf_name: str = None, persist_path="chroma_db") -> list:
    """
    Return a sorted list of unique chapter headings for a given library.
    If pdf_name is provided, only list chapters from that specific PDF.
    Only includes lines that look like real chapter headings (e.g., 'Chapter 1: ...', 'Chapter 2. ...').
    """
    import re
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": get_device()})
    vectordb = Chroma(persist_directory=persist_path, embedding_function=embeddings)
    all_metadata = vectordb._collection.get(include=["metadatas"])
    chapters = set()
    chapter_heading_pattern = re.compile(r"^Chapter\s+\d+([\.:\s-]+.+)?$", re.IGNORECASE)
    if all_metadata and "metadatas" in all_metadata:
        for meta in all_metadata["metadatas"]:
            # Check if this document belongs to the specified library and PDF (if provided)
            if meta and "library" in meta and meta["library"] == library_name:
                # If pdf_name is provided, check if this document is from that PDF
                if pdf_name and pdf_name != library_name:
                    source = meta.get("source", "")
                    if not source or pdf_name not in source:
                        continue
                        
                section = meta.get("section_title", "")
                if section and chapter_heading_pattern.match(section.strip()):
                    chapters.add(section.strip())
    # Sort by chapter number if possible
    def chapter_sort_key(title):
        m = re.match(r"^Chapter\s+(\d+)", title, re.IGNORECASE)
        return int(m.group(1)) if m else 9999
    return sorted(chapters, key=chapter_sort_key)
