import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

# Configuration for upload directory - resolved dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Ensure the directory exists immediately on load or in the endpoint
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".mp3", ".wav", ".mp4"}

class UploadResponse(BaseModel):
    filename: str
    saved_path: str
    content_type: str
    message: str

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Securely uploads and saves PDF, MP3, WAV, and MP4 files.
    """
    # Bulletproof check for directory existence
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 1. Extract and validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. Generate a unique filename using UUID
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # DEBUG LOG: Verify path resolution
    print(f"[DEBUG] Saving upload to: {file_path}")

    # 3. Save the file to the uploads directory
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving the file: {str(e)}"
        )
    finally:
        file.file.close()

    return UploadResponse(
        filename=unique_filename, # Return the unique filename for subsequent processing
        saved_path=file_path,
        content_type=file.content_type,
        message="File uploaded and saved successfully! 🚀"
    )
