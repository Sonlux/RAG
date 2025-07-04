import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Strict chapter heading pattern: e.g., 'Chapter 1', 'Chapter 2: Introduction', etc.
CHAPTER_HEADING_PATTERN = r'(?m)^\s*(Chapter\s+\d+(?:[:.\-\s][^\n]*)?)'

def split_text_into_chunks(text, chunk_size=800, overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.create_documents([text])

def split_text_semantic(text, chunk_size=800, overlap=200, page_number=None):
    """
    Advanced chunking: split by strict chapter headings, then by paragraphs, then by overlap.
    Attaches section title and (optionally) page number as metadata to each chunk.
    Only true chapter headings are used for section_title; all other chunks have section_title=None.
    """
    # Strictly match only true chapter headings
    matches = list(re.finditer(CHAPTER_HEADING_PATTERN, text, re.IGNORECASE))
    chunks = []
    if not matches:
        # Fallback: no headings found, treat whole text as one section
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        for doc in splitter.create_documents([text]):
            doc.metadata = {"section_title": None}
            if page_number is not None:
                doc.metadata["page_number"] = page_number
            chunks.append(doc)
        return chunks

    # Split by chapter headings, only assign section_title to true headings
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        section_title = match.group(0).strip()
        section_text = text[start:end].strip()
        if not section_text:
            continue
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        for doc in splitter.create_documents([section_text]):
            # Only assign section_title if this is a true chapter heading
            doc.metadata = {"section_title": section_title}
            if page_number is not None:
                doc.metadata["page_number"] = page_number
            chunks.append(doc)
    return chunks

def split_pdf_by_page_and_section(pages, chunk_size=800, overlap=200):
    """
    pages: list of (page_text, page_number) tuples
    Returns: list of Document objects with section_title and page_number metadata
    """
    all_chunks = []
    for page_text, page_number in pages:
        chunks = split_text_semantic(page_text, chunk_size=chunk_size, overlap=overlap, page_number=page_number)
        all_chunks.extend(chunks)
    return all_chunks
