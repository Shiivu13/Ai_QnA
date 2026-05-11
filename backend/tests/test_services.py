import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.pdf_service import extract_text_from_pdf
from app.services.ai_service import generate_summary, answer_question_with_context
from app.services.transcription_service import transcribe_media
from app.services.vector_service import chunk_text, create_and_save_index, search_index

# --- PDF Service Tests ---
@patch("app.services.pdf_service.PdfReader")
def test_extract_text_from_pdf(mock_pdf_reader):
    mock_reader_instance = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Test page text."
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance
    
    text = extract_text_from_pdf("dummy.pdf")
    assert text == "Test page text."

# --- AI Service Tests ---
@patch("app.services.ai_service.model")
@pytest.mark.asyncio
async def test_generate_summary(mock_model):
    mock_response = MagicMock()
    mock_response.text = "Mock AI Summary"
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)
    
    summary = await generate_summary("Some long text")
    assert summary == "Mock AI Summary"

@patch("app.services.ai_service.model")
@pytest.mark.asyncio
async def test_answer_question_with_context(mock_model):
    mock_response = MagicMock()
    mock_response.text = "Mock Answer"
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)
    
    answer = await answer_question_with_context("query", "context")
    assert answer == "Mock Answer"

# --- Transcription Service Tests ---
@patch("app.services.transcription_service.model")
def test_transcribe_media(mock_model):
    mock_model.transcribe.return_value = {
        "text": "Full text",
        "segments": [{"start": 0, "end": 1, "text": "Full text"}]
    }
    
    result = transcribe_media("audio.mp3")
    assert result["full_text"] == "Full text"
    assert len(result["segments"]) == 1

# --- Vector Service Tests ---
def test_chunk_text():
    text = "A" * 1500
    chunks = chunk_text(text, chunk_size=500)
    assert len(chunks) == 3

@patch("app.services.vector_service.os.makedirs")
@patch("app.services.vector_service.faiss.write_index")
@patch("app.services.vector_service.embedding_model")
@patch("app.services.vector_service.np.save")
def test_create_and_save_index(mock_save, mock_embedding, mock_write, mock_makedirs):
    mock_embedding.encode.return_value = [[0.1, 0.2]]
    create_and_save_index(["chunk"], "test.pdf")
    assert mock_embedding.encode.called
    assert mock_write.called
    assert mock_save.called

@patch("app.services.vector_service.faiss.read_index")
@patch("app.services.vector_service.embedding_model")
@patch("app.services.vector_service.np.load")
def test_search_index(mock_load, mock_embedding, mock_read):
    mock_embedding.encode.return_value = [[0.1, 0.2]]
    
    mock_index = MagicMock()
    mock_index.search.return_value = ([[0.1]], [[0]])
    mock_read.return_value = mock_index
    
    mock_load.return_value = ["chunk1"]
    
    context = search_index("query", "test.pdf")
    assert "chunk1" in context
