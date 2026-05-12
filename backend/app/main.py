import os
from dotenv import load_dotenv

# Load environment variables at the very beginning
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Explicitly import routers
from app.api import upload, document, media, chat
from app.core.database import engine, Base
from app.models import file_metadata

import time

# Retry logic for database initialization (useful for Docker compose startup)
if not os.getenv("TESTING"):
    max_retries = 5
    for i in range(max_retries):
        try:
            # Create database tables
            Base.metadata.create_all(bind=engine)
            print("Successfully connected to the database and created tables.")
            break
        except Exception as e:
            print(f"Database connection failed (attempt {i+1}/{max_retries}): {e}")
            time.sleep(2)
    else:
        print("WARNING: Could not connect to the database after multiple retries.")

app = FastAPI(
    title="AI Document & Multimedia Q&A API",
    description="Production-ready FastAPI backend for document and multimedia Q&A",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with explicit prefixing to prevent 404s
app.include_router(upload.router, prefix="/api", tags=["File Upload"])
app.include_router(document.router, prefix="/api", tags=["Document Analysis"])
app.include_router(media.router, prefix="/api", tags=["Media Analysis"])
app.include_router(chat.router, prefix="/api", tags=["AI Chat"])

from app.core.streaming import range_requests_response
from fastapi import Request

# Serve static files (uploads) for frontend media player
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

from app.core.streaming import range_requests_response

@app.get("/uploads/{filename}")
async def serve_upload(request: Request, filename: str):
    """
    Serve uploaded files with support for HTTP Range Requests.
    Uses custom Response to bypass Uvicorn chunking bugs for HTML5 seeking.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    return range_requests_response(request, file_path)

@app.get("/")
async def root():
    """
    Health check endpoint to verify the API is running smoothly.
    """
    return {
        "status": "success", 
        "message": "FastAPI engine is running smoothly! 🚀"
    }

if __name__ == "__main__":
    import uvicorn
    # Use direct app reference for better uvicorn execution
    uvicorn.run(app, host="127.0.0.1", port=8000)
