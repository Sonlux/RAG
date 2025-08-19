from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List, Any
import re

class PDFFilteredRetriever:
    """Custom retriever that filters results by PDF name after retrieval and uses hybrid search"""
    
    def __init__(self, vectordb, library: str, pdf_name: str = None, k: int = 15):
        self.vectordb = vectordb
        self.library = library
        self.pdf_name = pdf_name
        self.k = k
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        # Try hybrid search: keyword + semantic
        docs = self._hybrid_search(query)
        
        # Filter by PDF name if specified
        if self.pdf_name and self.pdf_name != self.library:
            filtered_docs = []
            for doc in docs:
                source = doc.metadata.get("source", "")
                if self.pdf_name in source:
                    filtered_docs.append(doc)
            docs = filtered_docs[:self.k]  # Limit to requested number
        
        return docs[:self.k]
    
    def _hybrid_search(self, query: str) -> List[Document]:
        """Hybrid search combining keyword matching and semantic search"""
        # Extract potential keywords from the query
        keywords = self._extract_keywords(query)
        
        # First try keyword-based search if we have good keywords
        if keywords:
            keyword_docs = self._keyword_search(keywords)
            if keyword_docs:
                return keyword_docs
        
        # Fall back to semantic search
        return self.vectordb.similarity_search(
            query, 
            k=self.k * 2,  # Get more docs to account for filtering
            filter={"library": self.library}
        )
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract potential keywords from the query"""
        # Look for names, specific terms, etc.
        import re
        
        # Extract capitalized words (likely names) but filter out common question words
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', query)
        capitalized_words = [w for w in capitalized_words if w.lower() not in ['who', 'what', 'where', 'when', 'why', 'how', 'is', 'are', 'the', 'a', 'an']]
        
        # Extract quoted terms
        quoted_terms = re.findall(r'"([^"]*)"', query)
        
        # Extract specific question patterns - get the name/subject being asked about
        name_patterns = re.findall(r'(?:who is|about|tell me about)\s+([A-Za-z\s]+)', query, re.IGNORECASE)
        
        keywords = capitalized_words + quoted_terms
        if name_patterns:
            # Clean up the extracted names
            for name in name_patterns:
                clean_name = name.strip().rstrip('?').strip()
                if clean_name and len(clean_name) > 2:
                    keywords.append(clean_name)
            
        return [kw.strip() for kw in keywords if len(kw.strip()) > 2]
    
    def _keyword_search(self, keywords: List[str]) -> List[Document]:
        """Search for documents containing the keywords"""
        try:
            # Get all documents in the library
            all_docs = self.vectordb.get(
                where={"library": self.library}, 
                include=["metadatas", "documents"]
            )
            
            if not all_docs or "documents" not in all_docs:
                return []
            
            # Score documents based on keyword matches
            doc_scores = []
            for i, doc_content in enumerate(all_docs["documents"]):
                content_lower = doc_content.lower()
                score = 0
                matched_keywords = []
                
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower in content_lower:
                        # Higher score for longer, more specific keywords
                        keyword_score = len(keyword) * content_lower.count(keyword_lower)
                        score += keyword_score
                        matched_keywords.append(keyword)
                
                if score > 0:
                    doc_scores.append((score, i, matched_keywords))
            
            # Sort by score (highest first)
            doc_scores.sort(key=lambda x: x[0], reverse=True)
            
            # Create Document objects for top matches
            matching_docs = []
            for score, i, matched_keywords in doc_scores[:self.k]:
                doc = Document(
                    page_content=all_docs["documents"][i],
                    metadata=all_docs["metadatas"][i]
                )
                matching_docs.append(doc)
            
            return matching_docs
            
        except Exception as e:
            print(f"Keyword search error: {e}")
            return []
    
    def invoke(self, query: str, config=None) -> List[Document]:
        """Invoke method for compatibility with LangChain's retriever interface"""
        return self._get_relevant_documents(query)

def parse_metadata_filter(question: str):
    """
    Parse the question to extract metadata filters for specific chapters, sections, or pages.
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
    
    # Use the custom PDFFilteredRetriever for better PDF filtering
    return PDFFilteredRetriever(
        vectordb=vectordb,
        library=library, 
        pdf_name=pdf_name,
        k=15
    )

