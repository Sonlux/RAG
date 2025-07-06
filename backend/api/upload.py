# File upload endpoint
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
from ingestion.pdf_loader import extract_pdf_flexibly
from ingestion.chunker import split_text_into_chunks, split_text_semantic, split_pdf_by_page_and_section
from ingestion.embed_store import embed_and_store
import tempfile
from datetime import datetime
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

# Directory to store uploaded PDFs for preview
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_pdf(library: str = Form(...), file: UploadFile = File(...)):
    try:
        # Save file temporarily
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            temp_path = tmp.name

        # Process PDF
        docs = extract_pdf_flexibly(temp_path)
        # Get file size
        file_size = os.path.getsize(temp_path)
        # Create complete metadata
        metadata = {
            "library": library,
            "source": file.filename,  # Original filename
            "size": file_size,
            "uploadedAt": datetime.now().isoformat(),
            "tags": []
        }
        # Metadata-aware chunking: chunk each page, attach section title and page number
        pages = [(doc.page_content, doc.metadata.get("page", None)) for doc in docs]
        advanced_chunks = split_pdf_by_page_and_section(pages)
        for chunk in advanced_chunks:
            if not hasattr(chunk, 'metadata'):
                chunk.metadata = {}
            chunk.metadata.update(metadata)
        embed_and_store(advanced_chunks, metadata=metadata)
        
        # Save a copy of the PDF for preview
        pdf_path = UPLOAD_DIR / file.filename
        with open(pdf_path, "wb") as f:
            # Reset the file pointer to the beginning
            with open(temp_path, "rb") as src:
                f.write(src.read())

        os.remove(temp_path)
        return {"message": f"{file.filename} uploaded and indexed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pdf/{filename}")
async def get_pdf(filename: str):
    """Serve PDF files for preview"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF {filename} not found")
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )
