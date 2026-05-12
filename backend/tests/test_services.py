import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
import numpy as np
from fastapi import Request, HTTPException

# Import services to test
from app.services.pdf_service import extract_text_from_pdf
from app.services.ai_service import generate_summary, answer_question_with_context
from app.services.transcription_service import transcribe_media, get_whisper_model
from app.services.vector_service import chunk_text, create_and_save_index, search_index, get_embedding_model
from app.core.streaming import range_requests_response

# --- PDF Service Tests ---
@patch("app.services.pdf_service.PdfReader")
@patch("app.services.pdf_service.os.path.exists")
def test_extract_text_from_pdf(mock_exists, mock_pdf_reader):
    mock_exists.return_value = True
    mock_reader_instance = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Test page text."
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance
    
    text = extract_text_from_pdf("dummy.pdf")
    assert text == "Test page text."

@patch("app.services.pdf_service.os.path.exists")
def test_extract_text_from_pdf_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("missing.pdf")

@patch("app.services.pdf_service.os.path.exists")
@patch("app.services.pdf_service.PdfReader")
def test_extract_text_from_pdf_exception(mock_pdf, mock_exists):
    mock_exists.return_value = True
    mock_pdf.side_effect = Exception("PDF Error")
    with pytest.raises(Exception) as excinfo:
        extract_text_from_pdf("error.pdf")
    assert "Failed to extract text from PDF" in str(excinfo.value)

# --- AI Service Tests ---
@patch("app.services.ai_service.genai.GenerativeModel")
@pytest.mark.asyncio
async def test_generate_summary(mock_model_class):
    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mock AI Summary"
    mock_model_instance.generate_content_async = AsyncMock(return_value=mock_response)
    mock_model_class.return_value = mock_model_instance
    
    summary = await generate_summary("Some long text")
    assert summary == "Mock AI Summary"

@pytest.mark.asyncio
async def test_generate_summary_empty():
    assert await generate_summary("  ") == "No text available to summarize."

@patch("app.services.ai_service.genai.GenerativeModel")
@pytest.mark.asyncio
async def test_generate_summary_exception(mock_model_class):
    mock_model_class.side_effect = Exception("AI Error")
    res = await generate_summary("text")
    assert "An error occurred" in res

@patch("app.services.ai_service.genai.GenerativeModel")
@pytest.mark.asyncio
async def test_answer_question_with_context(mock_model_class):
    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mock Answer"
    mock_model_instance.generate_content_async = AsyncMock(return_value=mock_response)
    mock_model_class.return_value = mock_model_instance
    
    answer = await answer_question_with_context("query", "context")
    assert answer == "Mock Answer"

@pytest.mark.asyncio
async def test_answer_question_empty():
    assert await answer_question_with_context(" ", "context") == "Please provide a question."

@patch("app.services.ai_service.genai.GenerativeModel")
@pytest.mark.asyncio
async def test_answer_question_exception(mock_model_class):
    mock_model_class.side_effect = Exception("AI Error")
    res = await answer_question_with_context("q", "c")
    assert "An error occurred" in res

# --- Transcription Service Tests ---
def test_get_whisper_model():
    with patch("app.services.transcription_service.whisper.load_model") as mock_load:
        mock_load.return_value = MagicMock()
        model = get_whisper_model()
        assert model is not None
        assert mock_load.called

@patch("app.services.transcription_service.get_whisper_model")
@patch("app.services.transcription_service.os.path.exists")
def test_transcribe_media(mock_exists, mock_get_model):
    mock_exists.return_value = True
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {
        "text": "Full text",
        "segments": [{"start": 0, "end": 1, "text": "Full text"}]
    }
    mock_get_model.return_value = mock_model
    
    result = transcribe_media("audio.mp3")
    assert result["full_text"] == "Full text"
    assert len(result["segments"]) == 1

@patch("app.services.transcription_service.os.path.exists")
def test_transcribe_media_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        transcribe_media("missing.mp3")

@patch("app.services.transcription_service.os.path.exists")
@patch("app.services.transcription_service.get_whisper_model")
def test_transcribe_media_exception(mock_get, mock_exists):
    mock_exists.return_value = True
    mock_get.side_effect = Exception("Whisper Error")
    with pytest.raises(Exception) as excinfo:
        transcribe_media("error.mp3")
    assert "Transcription failed" in str(excinfo.value)

# --- Vector Service Tests ---
def test_get_embedding_model():
    with patch("app.services.vector_service.SentenceTransformer") as mock_st:
        mock_st.return_value = MagicMock()
        model = get_embedding_model()
        assert model is not None
        assert mock_st.called

def test_chunk_text():
    text = "A" * 1500
    chunks = chunk_text(text, chunk_size=500)
    assert len(chunks) == 3

def test_chunk_text_empty():
    assert chunk_text("") == []

@patch("app.services.vector_service.os.makedirs")
@patch("app.services.vector_service.faiss.write_index")
@patch("app.services.vector_service.get_embedding_model")
@patch("app.services.vector_service.np.save")
@patch("app.services.vector_service.open", new_callable=MagicMock)
def test_create_and_save_index(mock_open, mock_save, mock_get_embedding, mock_write, mock_makedirs):
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1, 0.2]])
    mock_get_embedding.return_value = mock_model
    
    create_and_save_index(["chunk"], "test.pdf")
    assert mock_model.encode.called
    assert mock_write.called

def test_create_and_save_index_empty():
    assert create_and_save_index([], "test.pdf") is None

@patch("app.services.vector_service.faiss.read_index")
@patch("app.services.vector_service.get_embedding_model")
@patch("app.services.vector_service.os.path.exists")
@patch("app.services.vector_service.open", new_callable=MagicMock)
@patch("app.services.vector_service.json.load")
def test_search_index(mock_json_load, mock_open, mock_exists, mock_get_embedding, mock_read):
    mock_exists.return_value = True
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1, 0.2]])
    mock_get_embedding.return_value = mock_model
    
    mock_index = MagicMock()
    mock_index.search.return_value = (np.array([[0.1]]), np.array([[0]]))
    mock_read.return_value = mock_index
    
    mock_json_load.return_value = [{"text": "chunk1"}]
    
    context, matched = search_index("query", "test.pdf")
    assert "chunk1" in context
    assert len(matched) == 1

@patch("app.services.vector_service.os.path.exists")
def test_search_index_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        search_index("q", "missing.pdf")

# --- Core Service Tests ---
def test_get_db():
    from app.core.database import get_db
    gen = get_db()
    db = next(gen)
    assert db is not None
    try:
        next(gen)
    except StopIteration:
        pass

@patch("app.core.streaming.os.path.isfile")
@patch("app.core.streaming.os.path.getsize")
@patch("app.core.streaming.mimetypes.guess_type")
@patch("app.core.streaming.open", new_callable=MagicMock)
def test_range_requests_response(mock_open, mock_guess, mock_getsize, mock_isfile):
    mock_isfile.return_value = True
    mock_getsize.return_value = 1000
    mock_guess.return_value = ("video/mp4", None)
    mock_file = MagicMock()
    mock_file.read.return_value = b"some data"
    mock_open.return_value.__enter__.return_value = mock_file
    
    # Mock request with Range header
    request = MagicMock(spec=Request)
    request.headers = {"range": "bytes=0-100"}
    
    response = range_requests_response(request, "test.mp4")
    assert response.status_code == 206
    assert response.headers["Content-Range"] == "bytes 0-100/1000"

@patch("app.core.streaming.os.path.isfile")
@patch("app.core.streaming.os.path.getsize")
@patch("app.core.streaming.mimetypes.guess_type")
def test_range_requests_response_no_range(mock_guess, mock_getsize, mock_isfile):
    mock_isfile.return_value = True
    mock_getsize.return_value = 1000
    mock_guess.return_value = ("video/mp4", None)
    request = MagicMock(spec=Request)
    request.headers = {}
    
    with patch("fastapi.responses.FileResponse") as mock_file_response:
        range_requests_response(request, "test.mp4")
        assert mock_file_response.called

@patch("app.core.streaming.os.path.isfile")
def test_range_requests_response_not_found(mock_isfile):
    mock_isfile.return_value = False
    request = MagicMock(spec=Request)
    with pytest.raises(HTTPException) as excinfo:
        range_requests_response(request, "missing.mp4")
    assert excinfo.value.status_code == 404

@patch("app.core.streaming.os.path.isfile")
@patch("app.core.streaming.os.path.getsize")
@patch("app.core.streaming.mimetypes.guess_type")
def test_range_requests_response_invalid_range(mock_guess, mock_getsize, mock_isfile):
    mock_isfile.return_value = True
    mock_getsize.return_value = 1000
    mock_guess.return_value = ("video/mp4", None)
    request = MagicMock(spec=Request)
    request.headers = {"range": "bytes=abc-def"}
    with pytest.raises(HTTPException) as excinfo:
        range_requests_response(request, "test.mp4")
    assert excinfo.value.status_code == 400

@patch("app.core.streaming.os.path.isfile")
@patch("app.core.streaming.os.path.getsize")
@patch("app.core.streaming.mimetypes.guess_type")
def test_range_requests_response_range_not_satisfiable(mock_guess, mock_getsize, mock_isfile):
    mock_isfile.return_value = True
    mock_getsize.return_value = 1000
    mock_guess.return_value = ("video/mp4", None)
    request = MagicMock(spec=Request)
    request.headers = {"range": "bytes=2000-3000"}
    with pytest.raises(HTTPException) as excinfo:
        range_requests_response(request, "test.mp4")
    assert excinfo.value.status_code == 416
