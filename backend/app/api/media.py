import os
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.services.transcription_service import transcribe_media
from app.services.vector_service import chunk_text, create_and_save_index
from app.services.ai_service import generate_summary
from app.core.database import get_db
from app.models.file_metadata import FileMetadata

router = APIRouter(tags=["Media Analysis"])

# Configuration for file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Allowed media extensions
ALLOWED_MEDIA_EXTENSIONS = {".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".webm"}

class TranscribeRequest(BaseModel):
    filename: str

class Segment(BaseModel):
    start: float
    end: float
    text: str

class TranscribeResponse(BaseModel):
    filename: str
    full_text: str
    segments: List[Segment]
    summary: Optional[str] = None
    indexed: bool

@router.post("/transcribe-media", response_model=TranscribeResponse)
async def transcribe_media_endpoint(request: TranscribeRequest, db: Session = Depends(get_db)):
    """
    Transcribes a previously uploaded audio or video file.
    Returns the full text, timestamped segments, and an AI-generated summary.
    Also creates a FAISS vector index so the file is ready for chat-based Q&A
    with timestamp-aware retrieval.
    """
    # 1. Construct and verify file path
    file_path = os.path.join(UPLOAD_DIR, request.filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{request.filename}' not found in the uploads directory."
        )

    # 2. Validate media extension
    file_ext = os.path.splitext(request.filename)[1].lower()
    if file_ext not in ALLOWED_MEDIA_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid media format. Allowed: {', '.join(ALLOWED_MEDIA_EXTENSIONS)}"
        )

    # 3. Transcribe media
    try:
        transcription_result = transcribe_media(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe media: {str(e)}"
        )

    # 4. Generate AI summary of the transcript
    summary = None
    try:
        summary = await generate_summary(transcription_result["full_text"])
    except Exception as e:
        print(f"[WARN] Could not generate summary for '{request.filename}': {e}")

    # 5. Build FAISS vector index with timestamp metadata per segment
    indexed = False
    try:
        segments = transcription_result.get("segments", [])
        if segments:
            # Use each segment as a chunk; store start/end as metadata for timestamp linking
            segment_texts = [seg["text"] for seg in segments]
            segment_metadata = [{"start": seg["start"], "end": seg["end"]} for seg in segments]
            create_and_save_index(segment_texts, request.filename, metadata=segment_metadata)
        else:
            # Fall back to chunking full text (no timestamp metadata)
            chunks = chunk_text(transcription_result["full_text"])
            create_and_save_index(chunks, request.filename)
        indexed = True
    except Exception as e:
        print(f"[WARN] Could not create vector index for '{request.filename}': {e}")

    # 6. Save to database
    try:
        db_file = FileMetadata(
            filename=request.filename,
            file_type=file_ext.replace('.', ''),
            extracted_text=transcription_result["full_text"]
        )
        db.add(db_file)
        db.commit()
    except Exception as e:
        print(f"[ERROR] Failed to save metadata to DB: {e}")
        db.rollback()

    return TranscribeResponse(
        filename=request.filename,
        full_text=transcription_result["full_text"],
        segments=transcription_result["segments"],
        summary=summary,
        indexed=indexed
    )
