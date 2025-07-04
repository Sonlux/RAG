# History endpoint
from fastapi import APIRouter, HTTPException
from rag_pipeline.memory_manager import get_history, get_all_history, delete_history

router = APIRouter()

@router.get("/history")
def get_all_chat_histories():
    try:
        history = get_all_history()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{chat_id}")
def get_chat_history(chat_id: str):
    try:
        history = get_history(chat_id)
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
