from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services.vector_service import search_index
from app.services.ai_service import answer_question_with_context
from app.core.database import get_db
from app.models.file_metadata import FileMetadata

router = APIRouter(tags=["AI Chat"])

class ChatRequest(BaseModel):
    filename: str
    query: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest, db: Session = Depends(get_db)):
    """
    RAG-based chatbot endpoint that answers questions about a specific uploaded file.
    It passes retrieved segment metadata (like timestamps for media) to the AI
    so the answer can reference exact times.
    """
    try:
        # 0. Fetch the file metadata to provide a general overview of the file
        db_file = db.query(FileMetadata).filter(FileMetadata.filename == request.filename).first()
        global_context = ""
        if db_file and db_file.extracted_text:
            # Add the first 2000 chars of the full transcript/summary to give general context
            # This helps answer broad questions like "what is this video about?"
            global_context = f"[GLOBAL FILE CONTEXT (First Part)]\n{db_file.extracted_text[:2000]}\n\n"

        # 1. Search the vector index for relevant context
        # search_index now returns context string and a list of matched dicts (with metadata)
        context_str, matched_segments = search_index(request.query, request.filename)
        
        # Format context with timestamps if available
        enriched_context = global_context + "[SPECIFIC RETRIEVED CHUNKS]\n"
        for i, segment in enumerate(matched_segments):
            enriched_context += f"[Segment {i+1}]\n"
            if "start" in segment and "end" in segment:
                enriched_context += f"Timestamp: [{segment['start']}s - {segment['end']}s]\n"
            enriched_context += f"Text: {segment['text']}\n\n"
        
        # 2. Generate answer using Gemini based on the enriched context
        answer = await answer_question_with_context(request.query, enriched_context)
        
        return ChatResponse(answer=answer)
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during chat: {str(e)}"
        )
