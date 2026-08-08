import os
import json
import uuid
from typing import Any, Dict, List, Optional


class VectorService:
    """Vector database layer for Phase 2 RAG system."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, persist_directory: str = "cache/vector_db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, persist_directory: str = "cache/vector_db"):
        if not VectorService._initialized:
            self.persist_directory = persist_directory
            self.client = None
            self.collection = None
            self._initialize()
            VectorService._initialized = True
    
    def _initialize(self):
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            self.collection = self.client.get_or_create_collection(
                name="repository_chunks",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            self.client = None
            self.collection = None
    
    def create_collection(self, collection_name: str) -> bool:
        """Create a new collection."""
        try:
            if not self.client:
                return False
            
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception:
            return False
    
    def add_documents(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """Add documents with embeddings to the vector database."""
        if not self.collection or not chunks or not embeddings:
            return False
        
        try:
            ids = [str(uuid.uuid4()) for _ in chunks]
            documents = [chunk.get("content", "") for chunk in chunks]
            metadatas = [
                {
                    "repository_id": chunk.get("repository_id", ""),
                    "chunk_id": chunk.get("chunk_id", ""),
                    "file_name": chunk.get("file_name", ""),
                    "file_path": chunk.get("file_path", ""),
                    "language": chunk.get("language", ""),
                    "class_name": chunk.get("class_name", ""),
                    "function_name": chunk.get("function_name", ""),
                    "start_line": chunk.get("start_line", 0),
                    "end_line": chunk.get("end_line", 0),
                }
                for chunk in chunks
            ]
            
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            return True
        except Exception:
            return False
    
    def search_documents(self, query_embedding: List[float], n_results: int = 10, 
                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self.collection:
            return []
        
        try:
            where_clause = {}
            if filters:
                if "repository_id" in filters:
                    where_clause["repository_id"] = filters["repository_id"]
                if "language" in filters:
                    where_clause["language"] = filters["language"]
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=["documents", "embeddings", "metadatas", "distances"]
            )
            
            formatted_results = []
            if results and results.get("documents"):
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else 0.0,
                        "score": 1.0 - (results["distances"][0][i] if results.get("distances") else 0.0),
                    })
            
            return formatted_results
        except Exception:
            return []
    
    def delete_documents(self, chunk_ids: List[str]) -> bool:
        """Delete documents by chunk IDs."""
        if not self.collection:
            return False
        
        try:
            self.collection.delete(ids=chunk_ids)
            return True
        except Exception:
            return False
    
    def update_documents(self, chunk_ids: List[str], chunks: List[Dict[str, Any]], 
                        embeddings: List[List[float]]) -> bool:
        """Update existing documents."""
        if not self.collection:
            return False
        
        try:
            documents = [chunk.get("content", "") for chunk in chunks]
            metadatas = [
                {
                    "repository_id": chunk.get("repository_id", ""),
                    "chunk_id": chunk.get("chunk_id", ""),
                    "file_name": chunk.get("file_name", ""),
                    "file_path": chunk.get("file_path", ""),
                    "language": chunk.get("language", ""),
                    "class_name": chunk.get("class_name", ""),
                    "function_name": chunk.get("function_name", ""),
                    "start_line": chunk.get("start_line", 0),
                    "end_line": chunk.get("end_line", 0),
                }
                for chunk in chunks
            ]
            
            self.collection.update(
                ids=chunk_ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            return True
        except Exception:
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        if not self.collection:
            return {"count": 0, "status": "unavailable"}
        
        try:
            count = self.collection.count()
            return {
                "count": count,
                "status": "active",
                "name": "repository_chunks"
            }
        except Exception:
            return {"count": 0, "status": "error"}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        if not self.collection:
            return False
        
        try:
            # Get all IDs and delete them
            results = self.collection.get()
            if results and results.get("ids"):
                self.collection.delete(ids=results["ids"])
            return True
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """Check if vector database is available."""
        return self.collection is not None