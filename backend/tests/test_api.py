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

@patch("app.api.upload.os.makedirs")
def test_upload_exception(mock_makedirs):
    mock_makedirs.side_effect = Exception("Upload Error")
    response = client.post(
        "/api/upload",
        files={"file": ("test.pdf", b"content", "application/pdf")}
    )
    assert response.status_code == 500
    assert "Upload Error" in response.json()["detail"]

# ---------------------------------------------------------
# Test Summarize Endpoint
# ---------------------------------------------------------
@patch("app.api.document.extract_text_from_pdf")
@patch("app.api.document.generate_summary", new_callable=AsyncMock)
@patch("app.api.document.chunk_text")
@patch("app.api.document.create_and_save_index")
@patch("app.api.document.os.path.exists")
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

@patch("app.api.document.os.path.exists")
def test_summarize_pdf_not_found(mock_exists):
    mock_exists.return_value = False
    
    response = client.post(
        "/api/summarize-pdf",
        json={"filename": "missing.pdf"}
    )
    
    assert response.status_code == 404

@patch("app.api.document.os.path.exists")
@patch("app.api.document.extract_text_from_pdf")
def test_summarize_pdf_exception(mock_extract, mock_exists):
    mock_exists.return_value = True
    mock_extract.side_effect = Exception("General Error")
    response = client.post(
        "/api/summarize-pdf",
        json={"filename": "test.pdf"}
    )
    assert response.status_code == 500

@patch("app.api.document.os.path.exists")
@patch("app.api.document.extract_text_from_pdf")
@patch("app.api.document.chunk_text")
@patch("app.api.document.generate_summary", new_callable=AsyncMock)
def test_summarize_pdf_non_fatal_errors(mock_gen, mock_chunk, mock_ext, mock_exists):
    mock_exists.return_value = True
    mock_ext.return_value = "text"
    mock_chunk.side_effect = Exception("Indexing Error")
    mock_gen.return_value = "summary"
    
    # We also mock db.add to fail
    with patch("app.api.document.FileMetadata") as mock_meta:
        mock_meta.side_effect = Exception("DB Error")
        response = client.post(
            "/api/summarize-pdf",
            json={"filename": "test.pdf"}
        )
        assert response.status_code == 200
        assert response.json()["indexed"] == False

# ---------------------------------------------------------
# Test Transcribe Endpoint
# ---------------------------------------------------------
@patch("app.api.media.transcribe_media")
@patch("app.api.media.chunk_text")
@patch("app.api.media.create_and_save_index")
@patch("app.api.media.os.path.exists")
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

@patch("app.api.media.os.path.exists")
def test_transcribe_media_not_found(mock_exists):
    mock_exists.return_value = False
    response = client.post(
        "/api/transcribe-media",
        json={"filename": "missing.mp3"}
    )
    assert response.status_code == 404

@patch("app.api.media.os.path.exists")
def test_transcribe_media_invalid_extension(mock_exists):
    mock_exists.return_value = True
    response = client.post(
        "/api/transcribe-media",
        json={"filename": "document.pdf"}
    )
    assert response.status_code == 400

@patch("app.api.media.os.path.exists")
@patch("app.api.media.transcribe_media")
def test_transcribe_media_exception(mock_transcribe, mock_exists):
    mock_exists.return_value = True
    mock_transcribe.side_effect = Exception("General Error")
    response = client.post(
        "/api/transcribe-media",
        json={"filename": "audio.mp3"}
    )
    assert response.status_code == 500

@patch("app.api.media.os.path.exists")
@patch("app.api.media.transcribe_media")
@patch("app.api.media.generate_summary", new_callable=AsyncMock)
@patch("app.api.media.create_and_save_index")
def test_transcribe_media_non_fatal_errors(mock_index, mock_gen, mock_trans, mock_exists):
    mock_exists.return_value = True
    mock_trans.return_value = {"full_text": "text", "segments": []} # empty segments triggers fallback
    mock_gen.side_effect = Exception("Summary Error")
    mock_index.side_effect = Exception("Indexing Error")
    
    with patch("app.api.media.FileMetadata") as mock_meta:
        mock_meta.side_effect = Exception("DB Error")
        response = client.post(
            "/api/transcribe-media",
            json={"filename": "audio.mp3"}
        )
        assert response.status_code == 200
        assert response.json()["summary"] is None

# ---------------------------------------------------------
# Test Chat Endpoint
# ---------------------------------------------------------
@patch("app.api.chat.search_index")
@patch("app.api.chat.answer_question_with_context", new_callable=AsyncMock)
def test_chat_success(mock_answer, mock_search):
    mock_search.return_value = ("Mocked context.", [{"text": "Mocked context.", "start": 0, "end": 1}])
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

@patch("app.api.chat.search_index")
def test_chat_exception(mock_search):
    mock_search.side_effect = Exception("General Error")
    response = client.post(
        "/api/chat",
        json={"filename": "test.pdf", "query": "q"}
    )
    assert response.status_code == 500

# ---------------------------------------------------------
# Test Streaming / Uploads Endpoint
# ---------------------------------------------------------
@patch("app.main.range_requests_response")
@patch("app.main.os.path.exists")
def test_serve_upload(mock_exists, mock_range):
    mock_exists.return_value = True
    mock_range.return_value = MagicMock()
    
    response = client.get("/uploads/test.mp4")
    assert response.status_code == 200

@patch("app.main.os.path.exists")
def test_serve_upload_not_found(mock_exists):
    mock_exists.return_value = False
    response = client.get("/uploads/missing.mp4")
    assert response.status_code == 404
