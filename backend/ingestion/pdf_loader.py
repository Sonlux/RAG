from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from typing import List

def extract_pdf_flexibly(path: str) -> List[Document]:
    """
    Parses a PDF using PyPDFLoader and returns LangChain Document objects.
    """
    print(f"[INFO] Parsing '{path}' using PyPDFLoader...")
    return PyPDFLoader(path).load()
