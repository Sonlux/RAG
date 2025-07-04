# File upload endpoint
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
from ingestion.pdf_loader import extract_pdf_flexibly
from ingestion.chunker import split_text_into_chunks, split_text_semantic, split_pdf_by_page_and_section
from ingestion.embed_store import embed_and_store
import tempfile
from datetime import datetime

router = APIRouter()

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

        os.remove(temp_path)
        return {"message": f"{file.filename} uploaded and indexed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
