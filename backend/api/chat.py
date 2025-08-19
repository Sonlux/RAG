# Chat endpoint
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from rag_pipeline.rag_chain import answer_question
from rag_pipeline.memory_manager import store_chat, get_history
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    chat_id: str
    library: str
    question: str
    pdf_name: Optional[str] = None  # Make it optional with default None
    chat_mode: str = "library"  # "single_pdf" or "library" (default)

@router.post("/chat/new")
def create_new_chat():
    # Generate a new unique chat_id
    return {"chat_id": str(uuid.uuid4())}

@router.get("/chat/library/{library}/documents")
def get_library_documents(library: str):
    """Get all documents available in a library for chat selection"""
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectordb = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
        
        # Get all documents for this library
        documents = vectordb.get(
            where={"library": library},
            include=["metadatas"]
        )
        
        if not documents or "metadatas" not in documents:
            return {"documents": [], "total_count": 0}
        
        # Extract unique PDF sources
        pdf_sources = set()
        for meta in documents["metadatas"]:
            if meta and "source" in meta:
                source_name = meta["source"].split("/")[-1] if "/" in meta["source"] else meta["source"]
                # Remove file extension for cleaner display
                if source_name.endswith('.pdf'):
                    source_name = source_name[:-4]
                pdf_sources.add(source_name)
        
        return {
            "documents": sorted(list(pdf_sources)),
            "total_count": len(pdf_sources),
            "library": library
        }
    except Exception as e:
        print(f"Error getting library documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/chat")
def chat_with_rag(request: ChatRequest):
    try:
        print(f"Chat request received: chat_id={request.chat_id}, library={request.library}, pdf_name={request.pdf_name}, chat_mode={request.chat_mode}")
        
        # Fetch recent chat history for this chat session
        history = get_history(request.chat_id, limit=5)
        
        # Determine PDF filtering based on chat mode
        if request.chat_mode == "single_pdf":
            # Single PDF mode: must have pdf_name specified
            if not request.pdf_name:
                raise HTTPException(status_code=400, detail="pdf_name is required for single_pdf chat mode")
            pdf_name = request.pdf_name
            chat_context = f"single PDF: {pdf_name}"
        elif request.chat_mode == "library":
            # Library mode: search across all PDFs in the library
            pdf_name = None  # This will search across all PDFs
            chat_context = f"entire library: {request.library}"
        else:
            raise HTTPException(status_code=400, detail="Invalid chat_mode. Use 'single_pdf' or 'library'")
        
        # Pass pdf_name to answer_question to filter results appropriately
        answer = answer_question(
            question=request.question, 
            library=request.library, 
            pdf_name=pdf_name,
            history=history
        )
        
        # Add metadata about search scope to the response
        response_data = {
            "answer": answer,
            "chat_mode": request.chat_mode,
            "search_scope": chat_context,
            "chat_id": request.chat_id
        }
        
        # Store the chat with the pdf_name and chat_mode
        store_chat(
            request.library, 
            request.question, 
            answer, 
            chat_id=request.chat_id, 
            pdf_name=pdf_name,
            metadata={"chat_mode": request.chat_mode, "search_scope": chat_context}
        )
        
        return response_data
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

