from typing import List, Optional
import os
import json

from config import get_settings


class EmbeddingService:
    """Embedding engine for Phase 2 RAG system."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, model_name: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = None):
        if not EmbeddingService._initialized:
            # Use central config if no model_name provided
            if model_name is None:
                settings = get_settings()
                self.model_name = settings.EMBEDDING_MODEL_NAME
            else:
                self.model_name = model_name
            
            self.model = None
            self._load_model()
            EmbeddingService._initialized = True
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except Exception:
            self.model = None
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text."""
        if not self.model:
            return self._fallback_embedding(text)
        
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception:
            return self._fallback_embedding(text)
    
    def generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts."""
        if not self.model:
            return [self._fallback_embedding(text) for text in texts]
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
            return [emb.tolist() for emb in embeddings]
        except Exception:
            return [self._fallback_embedding(text) for text in texts]
    
    def save_embedding(self, chunk_id: str, embedding: List[float], cache_dir: str = "cache/embeddings") -> bool:
        """Save embedding to cache."""
        try:
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, f"{chunk_id}.json")
            with open(cache_file, 'w') as f:
                json.dump({"embedding": embedding}, f)
            return True
        except Exception:
            return False
    
    def load_embedding(self, chunk_id: str, cache_dir: str = "cache/embeddings") -> Optional[List[float]]:
        """Load embedding from cache."""
        try:
            cache_file = os.path.join(cache_dir, f"{chunk_id}.json")
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r') as f:
                data = json.load(f)
            return data.get("embedding")
        except Exception:
            return None
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """Fallback embedding when model is not available."""
        # Simple hash-based embedding
        import hashlib
        
        # Create a deterministic embedding from text hash
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 384-dimensional vector (same as all-MiniLM-L6-v2)
        embedding = []
        for i in range(384):
            byte_val = hash_bytes[i % len(hash_bytes)]
            embedding.append((byte_val / 255.0) * 2 - 1)
        
        return embedding
    
    def is_available(self) -> bool:
        """Check if the embedding model is available."""
        return self.model is not None