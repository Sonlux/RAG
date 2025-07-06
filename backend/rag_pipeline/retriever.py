from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import re

def parse_metadata_filter(question: str):
    """
    Returns a metadata filter dict if the question references a specific page/chapter/section, else None.
    Only triggers for queries like 'chapter 5', 'chapter: Introduction', 'section 2.3', 'page 432'.
    """
    # Page number: e.g., "page 432"
    page_match = re.search(r"page\s*(\d{1,4})\b", question, re.IGNORECASE)
    if page_match:
        return {"page_number": int(page_match.group(1))}
    # Chapter: e.g., "chapter 5" or "chapter: Introduction"
    chapter_match = re.search(r"chapter\s*([\d]+|:[^\n]+)", question, re.IGNORECASE)
    if chapter_match:
        chapter_val = chapter_match.group(1).strip().lstrip(':').strip()
        return {"section_title": {"$contains": f"chapter {chapter_val}"}}
    # Section: e.g., "section 2.3"
    section_match = re.search(r"section\s*([\d\.]+|:[^\n]+)", question, re.IGNORECASE)
    if section_match:
        section_val = section_match.group(1).strip().lstrip(':').strip()
        return {"section_title": {"$contains": f"section {section_val}"}}
    return None

def get_retriever(library: str, question: str = None, pdf_name: str = None, persist_path="chroma_db"):
    embedding_fn = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=persist_path, embedding_function=embedding_fn)
    
    # Always filter by library
    base_filter = {"library": library}
    
    # If pdf_name is provided, use a simple filter instead of nested $contains
    if pdf_name and pdf_name != library:
        # Try a simpler approach - just search for documents with matching source
        documents = vectordb.get(
            where={"library": library},
            include=["metadatas"]
        )
        
        if documents and "metadatas" in documents:
            # Find document IDs that match the PDF name
            matching_ids = []
            for i, meta in enumerate(documents["metadatas"]):
                if meta and "source" in meta and pdf_name in meta["source"]:
                    if "ids" in documents:
                        matching_ids.append(documents["ids"][i])
            
            # If we found matching documents, create a retriever with those IDs
            if matching_ids:
                retriever = vectordb.as_retriever(
                    search_kwargs={
                        "k": 15,
                        "filter": {"library": library},
                        "document_ids": matching_ids
                    }
                )
                return retriever
    
    # If question is provided, try to add metadata filter
    if question:
        meta_filter = parse_metadata_filter(question)
        if meta_filter:
            base_filter.update(meta_filter)
            
    retriever = vectordb.as_retriever(
        search_kwargs={"k": 15, "filter": base_filter}
    )
    return retriever

