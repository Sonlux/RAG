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


@router.get("/history/{library}")
def get_chat_history(library: str):
    try:
        history = get_history(library)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{library}")
def delete_chat_history(library: str):
    try:
        result = delete_history(library)
        return {"success": True, "result": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
