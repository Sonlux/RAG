# Chat endpoint
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from rag_pipeline.rag_chain import answer_question
from rag_pipeline.memory_manager import store_chat, get_history
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    chat_id: str
    library: str
    question: str
    pdf_name: str = None  # Make it optional with default None

@router.post("/chat/new")
def create_new_chat():
    # Generate a new unique chat_id
    return {"chat_id": str(uuid.uuid4())}

@router.post("/chat")
def chat_with_rag(request: ChatRequest):
    try:
        # Fetch recent chat history for this chat session
        history = get_history(request.chat_id, limit=5)
        answer = answer_question(request.question, request.library, history=history)
        # Use the provided pdf_name if available, otherwise default to library name
        pdf_name = request.pdf_name if request.pdf_name else request.library
        store_chat(request.library, request.question, answer, chat_id=request.chat_id, pdf_name=pdf_name)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

