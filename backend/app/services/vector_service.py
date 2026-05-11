import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer

# Initialize the free local embedding model lazily
# all-MiniLM-L6-v2 is fast and efficient for local use
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model

# Configuration for vector store paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """
    Splits long text into smaller segments of approximately chunk_size characters.
    """
    if not text:
        return []
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def create_and_save_index(chunks: list[str], filename: str, metadata: list[dict] = None):
    """
    Generates embeddings for chunks, creates a FAISS index,
    and saves both to the vector_store directory.
    Optionally saves metadata (e.g. timestamps) alongside each chunk.
    """
    if not chunks:
        return

    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

    # 1. Generate embeddings
    embeddings = get_embedding_model().encode(chunks)
    embeddings = np.array(embeddings).astype('float32')

    # 2. Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # 3. Save index
    index_path = os.path.join(VECTOR_STORE_DIR, f"{filename}.index")
    faiss.write_index(index, index_path)

    # 4. Save chunks (text) with optional metadata
    store = []
    for i, chunk in enumerate(chunks):
        entry = {"text": chunk}
        if metadata and i < len(metadata):
            entry.update(metadata[i])
        store.append(entry)

    chunks_path = os.path.join(VECTOR_STORE_DIR, f"{filename}.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=4)

def search_index(query: str, filename: str, top_k: int = 3) -> tuple[str, list[dict]]:
    """
    Loads the index and chunks, searches for top_k closest segments,
    and returns:
      - combined text as context (str)
      - list of matched entries with text + optional metadata (list[dict])
    """
    index_path = os.path.join(VECTOR_STORE_DIR, f"{filename}.index")
    chunks_path = os.path.join(VECTOR_STORE_DIR, f"{filename}.json")

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        raise FileNotFoundError(f"Vector index for '{filename}' not found. Please process the file first.")

    # 1. Load index and store
    index = faiss.read_index(index_path)
    with open(chunks_path, "r", encoding="utf-8") as f:
        store = json.load(f)

    # Handle old format (plain list of strings) gracefully
    if store and isinstance(store[0], str):
        store = [{"text": s} for s in store]

    # 2. Generate embedding for the query
    query_embedding = get_embedding_model().encode([query])
    query_embedding = np.array(query_embedding).astype('float32')

    # 3. Search index
    distances, indices = index.search(query_embedding, top_k)

    # 4. Gather matched entries
    matched = [store[i] for i in indices[0] if i < len(store)]
    context = "\n\n".join([m["text"] for m in matched])

    return context, matched
