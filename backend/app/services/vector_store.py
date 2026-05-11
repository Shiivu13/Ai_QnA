import faiss
import numpy as np
import os
import pickle

class VectorStore:
    def __init__(self, dimension=768): # Default for many models, adjust as needed
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = {}
        self.current_id = 0

    def add_vectors(self, vectors, metadata_list):
        """
        Adds vectors to the index and stores metadata.
        vectors: np.array of shape (n, dimension)
        metadata_list: list of dicts
        """
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension mismatch. Expected {self.dimension}, got {vectors.shape[1]}")
        
        start_id = self.current_id
        self.index.add(vectors.astype('float32'))
        
        for i, meta in enumerate(metadata_list):
            self.metadata[start_id + i] = meta
            self.current_id += 1
            
        return list(range(start_id, self.current_id))

    def search(self, query_vector, k=5):
        """
        Searches the index for the top k nearest neighbors.
        """
        if query_vector.shape[1] != self.dimension:
            raise ValueError(f"Query vector dimension mismatch.")
            
        distances, indices = self.index.search(query_vector.astype('float32'), k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx in self.metadata:
                results.append({
                    "distance": float(dist),
                    "metadata": self.metadata[idx]
                })
        return results

    def save(self, path):
        faiss.write_index(self.index, f"{path}.index")
        with open(f"{path}.meta", 'wb') as f:
            pickle.dump(self.metadata, f)

    def load(self, path):
        if os.path.exists(f"{path}.index"):
            self.index = faiss.read_index(f"{path}.index")
            with open(f"{path}.meta", 'rb') as f:
                self.metadata = pickle.load(f)
            self.current_id = self.index.ntotal

vector_store = VectorStore()
