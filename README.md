# 🧠 AI Document & Multimedia Q&A Platform

A production-ready, full-stack application that provides AI-powered intelligence over your documents and multimedia files. Upload PDFs, MP3s, or MP4s to instantly get beautifully formatted executive summaries or timestamped transcripts, and interactively chat with your content using a local RAG (Retrieval-Augmented Generation) engine.

---

## 🌟 Key Features

- **Document Analysis**: Instantly extracts text from PDFs and generates high-level executive summaries.
- **Media Intelligence**: Transcribes audio and video files locally using Whisper, generating precise timestamped segments.
- **RAG Chat Engine**: Ask questions directly against your uploaded files. Uses local FAISS vector embeddings to ground the Gemini AI's answers in your specific context.
- **Interactive Multimedia Player**: Click on any timestamp in the transcript or chat interface to instantly seek the video/audio player to that exact moment.
- **Premium UI**: Features a custom-built, highly polished light-theme React interface with Framer Motion animations, interactive blobs, and a dynamic custom cursor.
- **PostgreSQL Persistence**: Saves all metadata and extracted intelligence locally to a PostgreSQL database.

---

## 🏗️ Architecture & Tech Stack

### Frontend
- **Framework**: React.js (Vite)
- **Styling**: Tailwind CSS, Vanilla CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **API Client**: Axios

### Backend
- **Framework**: FastAPI (Python 3.10)
- **AI/LLM**: Google Gemini (3.1 Flash)
- **Transcription**: OpenAI Whisper (Local)
- **Vector Search**: FAISS (Local) & SentenceTransformers (`all-MiniLM-L6-v2`)
- **Database ORM**: SQLAlchemy
- **PDF Processing**: `pypdf`

### DevOps & Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 15
- **CI/CD**: GitHub Actions (Pytest)

---

## 🚀 Local Setup Instructions

The entire stack is containerized for a zero-friction setup.

### Prerequisites
- Docker & Docker Compose installed.
- A free Gemini API key from Google AI Studio.

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd ai-qna-app
   ```

2. **Configure Environment Variables**:
   In the `backend/` directory, create a `.env` file and add your Gemini key:
   ```env
   GEMINI_API_KEY=your_actual_key_here
   DATABASE_URL=postgresql://user:password@db:5432/ai_qna_db
   ```

3. **Spin up the stack**:
   Run the following from the root directory:
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**:
   - **Frontend UI**: [http://localhost:5173](http://localhost:5173)
   - **Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing

The backend is fully covered by automated tests using `pytest`, `pytest-cov`, and `httpx`. Heavy AI dependencies and database operations are mocked for speed and stability.

To run tests locally:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing tests/
```

## 🔄 CI/CD Pipeline

This repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`). 
On every `push` and `pull_request` to the `main` branch, the pipeline automatically:
1. Sets up an Ubuntu runner with Python 3.10.
2. Installs backend dependencies.
3. Executes the full `pytest` suite.
4. Generates an XML coverage report.

---

## 📖 API Documentation

### `POST /api/upload`
Uploads a `.pdf`, `.mp3`, `.wav`, or `.mp4` file and saves it locally.

### `POST /api/summarize-pdf`
Extracts text from a previously uploaded PDF, generates a summary using Gemini, indexes the text into FAISS, and saves metadata to PostgreSQL.

### `POST /api/transcribe-media`
Transcribes a previously uploaded audio/video file using local Whisper, generates timestamped segments, indexes them into FAISS, and saves metadata to PostgreSQL.

### `POST /api/chat`
Performs a semantic vector search over the FAISS index to find relevant context from the document, and passes it to Gemini to answer the user's question.
