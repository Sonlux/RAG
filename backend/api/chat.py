# Chat endpoint
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from rag_pipeline.rag_chain import answer_question
from rag_pipeline.memory_manager import store_chat, get_history

router = APIRouter()

class ChatRequest(BaseModel):
    library: str
    question: str

@router.post("/chat")
def chat_with_rag(request: ChatRequest):
    try:
        # Fetch recent chat history for this library
        history = get_history(request.library, limit=5)
        answer = answer_question(request.question, request.library, history=history)
        store_chat(request.library, request.question, answer, pdf_name=request.library)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

