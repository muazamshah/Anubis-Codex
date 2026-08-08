from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.cache_service import CacheService
from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.retrieval_service import RetrievalService
from services.vector_service import VectorService

router = APIRouter(prefix="/api", tags=["phase2"])

# Initialize services
cache_service = CacheService()
chunk_service = ChunkService()
embedding_service = EmbeddingService()
vector_service = VectorService()
retrieval_service = RetrievalService(vector_service, embedding_service)


class EmbeddingRequest(BaseModel):
    repository_id: str
    files: List[Dict[str, Any]]


class RetrieveRequest(BaseModel):
    query: str
    n_results: int = 10
    repository_id: Optional[str] = None
    language: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    n_results: int = 10


@router.post("/embeddings/create")
def create_embeddings(payload: EmbeddingRequest) -> Dict[str, Any]:
    """Create embeddings for repository files."""
    try:
        repository_id = payload.repository_id
        files = payload.files
        
        # Generate chunks
        chunks = chunk_service.chunk_repository(files, repository_id)
        
        if not chunks:
            return {
                "status": "completed",
                "chunks_created": 0,
                "embeddings_generated": 0,
                "message": "No chunks created from files"
            }
        
        # Generate embeddings
        texts = [chunk.get("content", "") for chunk in chunks]
        embeddings = embedding_service.generate_embeddings(texts)
        
        # Add to vector database
        success = vector_service.add_documents(chunks, embeddings)
        
        # Cache embeddings
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = chunk.get("chunk_id", "")
            if chunk_id:
                cache_service.cache_embeddings(chunk_id, embedding)
        
        return {
            "status": "completed",
            "chunks_created": len(chunks),
            "embeddings_generated": len(embeddings),
            "vector_db_updated": success,
            "repository_id": repository_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding creation failed: {str(e)}")


@router.post("/retrieve")
def retrieve_chunks(payload: RetrieveRequest) -> Dict[str, Any]:
    """Retrieve relevant chunks for a query."""
    try:
        query = payload.query
        n_results = payload.n_results
        
        # Build filters
        filters = {}
        if payload.repository_id:
            filters["repository_id"] = payload.repository_id
        if payload.language:
            filters["language"] = payload.language
        
        # Retrieve chunks
        results = retrieval_service.retrieve(
            query=query,
            n_results=n_results,
            filters=filters if filters else None
        )
        
        # Get formatted context
        context = retrieval_service.get_context_for_query(query, max_chunks=n_results)
        
        return {
            "status": "completed",
            "query": query,
            "results_count": len(results),
            "results": results,
            "context": context
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@router.post("/search")
def search_repositories(payload: SearchRequest) -> Dict[str, Any]:
    """Search across repositories."""
    try:
        query = payload.query
        n_results = payload.n_results
        filters = payload.filters
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(query)
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        # Search vector database
        results = vector_service.search_documents(
            query_embedding=query_embedding,
            n_results=n_results,
            filters=filters
        )
        
        # Rerank and filter
        reranked = retrieval_service.rerank(results, query)
        filtered = retrieval_service.filter_results(reranked)
        
        return {
            "status": "completed",
            "query": query,
            "results_count": len(filtered),
            "results": filtered
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/status")
def get_status() -> Dict[str, Any]:
    """Get Phase 2 system status."""
    try:
        # Vector database stats
        vector_stats = vector_service.get_collection_stats()
        
        # Cache stats
        cache_stats = cache_service.get_stats()
        
        # Service availability
        services_status = {
            "embedding_service": embedding_service.is_available(),
            "vector_service": vector_service.is_available(),
            "cache_service": True,
            "retrieval_service": True,
        }
        
        return {
            "status": "active",
            "phase": "Phase 2 - RAG and Vector Search Engine",
            "services": services_status,
            "vector_database": vector_stats,
            "cache": cache_stats
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.delete("/cache/clear")
def clear_cache() -> Dict[str, Any]:
    """Clear all cache."""
    try:
        success = cache_service.clear_all()
        return {
            "status": "completed" if success else "failed",
            "message": "Cache cleared successfully" if success else "Failed to clear cache"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")


@router.delete("/vector/clear")
def clear_vector_db() -> Dict[str, Any]:
    """Clear vector database."""
    try:
        success = vector_service.clear_collection()
        return {
            "status": "completed" if success else "failed",
            "message": "Vector database cleared successfully" if success else "Failed to clear vector database"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector database clear failed: {str(e)}")