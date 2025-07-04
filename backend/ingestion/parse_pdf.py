from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain_core.documents import Document

def extract_documents_with_pypdf(pdf_path: str) -> List[Document]:
    """
    Uses PyPDFLoader to parse the PDF into structured LangChain Document objects.
    Each Document contains text and metadata.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return documents
