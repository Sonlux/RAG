# History endpoint
from fastapi import APIRouter, HTTPException, Query
from rag_pipeline.memory_manager import get_history, get_all_history, delete_history

router = APIRouter()

@router.get("/history")
def get_all_chat_histories():
    try:
        history = get_all_history()
        return history
    except Exception as e:
        print(f"Error in get_all_chat_histories: {str(e)}")
        return []


@router.get("/history/{chat_id}")
def get_chat_history(
    chat_id: str,
    pdf_name: str = Query(None, description="Optional PDF name to filter history")
):
    try:
        history = get_history(chat_id)
        
        # If pdf_name is provided, filter the history to only include messages for that PDF
        if pdf_name:
            history = [msg for msg in history if msg.get('pdf_name') == pdf_name]
            
        return {"history": history}
    except Exception as e:
        print(f"Error in get_chat_history for chat_id {chat_id}: {str(e)}")
        # Return empty history instead of raising an exception
        return {"history": []}


@router.delete("/history/{chat_id}")
def delete_chat_history(chat_id: str):
    try:
        result = delete_history(chat_id)
        return {"success": True, "result": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
