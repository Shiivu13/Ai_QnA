import os
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services.pdf_service import extract_text_from_pdf
from app.services.ai_service import generate_summary
from app.services.vector_service import chunk_text, create_and_save_index
from app.core.database import get_db
from app.models.file_metadata import FileMetadata

router = APIRouter(tags=["Document Analysis"])

# Configuration for file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

class SummarizeRequest(BaseModel):
    filename: str

class SummarizeResponse(BaseModel):
    filename: str
    summary: str
    indexed: bool

@router.post("/summarize-pdf", response_model=SummarizeResponse)
async def summarize_pdf(request: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Summarizes a previously uploaded PDF document.
    Also automatically creates a FAISS vector index so the file
    is immediately ready for chat-based Q&A.
    """
    # 1. Construct and verify file path
    file_path = os.path.join(UPLOAD_DIR, request.filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{request.filename}' not found in the uploads directory."
        )

    # 2. Extract text from PDF
    try:
        extracted_text = extract_text_from_pdf(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )

    # 3. Automatically build FAISS vector index for Q&A
    indexed = False
    try:
        chunks = chunk_text(extracted_text)
        create_and_save_index(chunks, request.filename)
        indexed = True
    except Exception as e:
        # Non-fatal: indexing failure shouldn't block the summary response
        print(f"[WARN] Could not create vector index for '{request.filename}': {e}")

    # 4. Generate summary using Gemini
    summary = await generate_summary(extracted_text)

    # 5. Save to database
    try:
        db_file = FileMetadata(
            filename=request.filename,
            file_type="pdf",
            extracted_text=summary
        )
        db.add(db_file)
        db.commit()
    except Exception as e:
        print(f"[ERROR] Failed to save metadata to DB: {e}")
        db.rollback()

    return SummarizeResponse(
        filename=request.filename,
        summary=summary,
        indexed=indexed
    )
