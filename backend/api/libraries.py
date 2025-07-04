from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import os
import json
from ingestion.embed_store import get_existing_libraries, delete_library
from typing import List
from datetime import datetime

router = APIRouter()

class LibraryCreate(BaseModel):
    name: str
    description: str = ""

LIBRARIES_FILE = os.path.join(os.path.dirname(__file__), "../db/libraries.json")

def load_libraries():
    if not os.path.exists(LIBRARIES_FILE):
        return []
    with open(LIBRARIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_libraries(libraries):
    with open(LIBRARIES_FILE, "w", encoding="utf-8") as f:
        json.dump(libraries, f, indent=2)

@router.get("/libraries", response_model=List[dict])
def list_libraries():
    """
    Get all available libraries with correct doc_count from vector store
    """
    try:
        # Get libraries from JSON file
        libraries = load_libraries()
        # Get doc counts from vector store
        from ingestion.embed_store import get_existing_libraries
        vector_libs = {lib["name"]: lib for lib in get_existing_libraries()}
        # Merge doc_count into libraries
        for lib in libraries:
            if lib["name"] in vector_libs:
                lib["doc_count"] = vector_libs[lib["name"]]["doc_count"]
            else:
                lib["doc_count"] = 0
        return libraries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/libraries")
def create_library(library: LibraryCreate):
    """
    Create a new library
    """
    try:
        libraries = load_libraries()
        if any(lib["name"] == library.name for lib in libraries):
            raise HTTPException(status_code=400, detail=f"Library '{library.name}' already exists")
        new_lib = {
            "name": library.name,
            "description": library.description,
            "doc_count": 0,
            "created_at": datetime.now().isoformat()
        }
        libraries.append(new_lib)
        save_libraries(libraries)
        return new_lib
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/libraries/{name}")
def delete_library_endpoint(name: str):
    """
    Delete a library and all its documents
    """
    try:
        libraries = load_libraries()
        new_libraries = [lib for lib in libraries if lib["name"] != name]
        save_libraries(new_libraries)
        # Also delete from vector store
        deleted = delete_library(name)
        return {"message": f"Library '{name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/libraries/{name}/pdfs")
def list_pdfs(name: str):
    """
    List all PDFs for a given library.
    """
    from ingestion.embed_store import get_pdfs_for_library
    return get_pdfs_for_library(name)