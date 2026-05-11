import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from app.core.database import get_db

client = TestClient(app)

# Mock DB Dependency to avoid needing a real DB during tests
def override_get_db():
    mock_db = MagicMock()
    try:
        yield mock_db
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

# ---------------------------------------------------------
# Test Health Endpoint
# ---------------------------------------------------------
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "FastAPI engine is running smoothly! 🚀"
    }

# ---------------------------------------------------------
# Test Upload Endpoint
# ---------------------------------------------------------
def test_upload_file_valid(tmp_path):
    file_path = tmp_path / "test.pdf"
    file_path.write_text("dummy content")
    
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    assert "filename" in response.json()
    assert response.json()["content_type"] == "application/pdf"
    assert response.json()["filename"].endswith(".pdf")

def test_upload_file_invalid(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("invalid content")
    
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

# ---------------------------------------------------------
# Test Summarize Endpoint
# ---------------------------------------------------------
@patch("app.api.document.extract_text_from_pdf")
@patch("app.api.document.generate_summary", new_callable=AsyncMock)
@patch("app.api.document.chunk_text")
@patch("app.api.document.create_and_save_index")
@patch("os.path.exists")
def test_summarize_pdf_success(mock_exists, mock_create_index, mock_chunk, mock_generate, mock_extract):
    mock_exists.return_value = True
    mock_extract.return_value = "Sample extracted text from PDF."
    mock_generate.return_value = "This is a mock summary."
    mock_chunk.return_value = ["Sample extracted text from PDF."]
    
    response = client.post(
        "/api/summarize-pdf",
        json={"filename": "fake_test_file.pdf"}
    )
    
    assert response.status_code == 200
    assert response.json()["summary"] == "This is a mock summary."
    assert response.json()["indexed"] is True

@patch("os.path.exists")
def test_summarize_pdf_not_found(mock_exists):
    mock_exists.return_value = False
    
    response = client.post(
        "/api/summarize-pdf",
        json={"filename": "missing.pdf"}
    )
    
    assert response.status_code == 404

# ---------------------------------------------------------
# Test Transcribe Endpoint
# ---------------------------------------------------------
@patch("app.api.media.transcribe_media")
@patch("app.api.media.chunk_text")
@patch("app.api.media.create_and_save_index")
@patch("os.path.exists")
def test_transcribe_media_success(mock_exists, mock_create_index, mock_chunk, mock_transcribe):
    mock_exists.return_value = True
    mock_transcribe.return_value = {
        "full_text": "Hello world.",
        "segments": [{"start": 0.0, "end": 1.0, "text": "Hello world."}]
    }
    
    response = client.post(
        "/api/transcribe-media",
        json={"filename": "audio.mp3"}
    )
    
    assert response.status_code == 200
    assert response.json()["full_text"] == "Hello world."
    assert len(response.json()["segments"]) == 1

@patch("os.path.exists")
def test_transcribe_media_invalid_extension(mock_exists):
    mock_exists.return_value = True
    
    response = client.post(
        "/api/transcribe-media",
        json={"filename": "document.pdf"}
    )
    
    assert response.status_code == 400
    assert "Invalid media format" in response.json()["detail"]

# ---------------------------------------------------------
# Test Chat Endpoint
# ---------------------------------------------------------
@patch("app.api.chat.search_index")
@patch("app.api.chat.answer_question_with_context", new_callable=AsyncMock)
def test_chat_success(mock_answer, mock_search):
    mock_search.return_value = "Mocked context."
    mock_answer.return_value = "Mocked answer based on context."
    
    response = client.post(
        "/api/chat",
        json={"filename": "test.pdf", "query": "What is this about?"}
    )
    
    assert response.status_code == 200
    assert response.json()["answer"] == "Mocked answer based on context."

@patch("app.api.chat.search_index")
def test_chat_file_not_found(mock_search):
    mock_search.side_effect = FileNotFoundError("FAISS index not found.")
    
    response = client.post(
        "/api/chat",
        json={"filename": "missing.pdf", "query": "What is this about?"}
    )
    
    assert response.status_code == 404
