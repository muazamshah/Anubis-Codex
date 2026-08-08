from typing import Any, Dict, List, Optional


class RetrievalService:
    """Retrieval engine for Phase 2 RAG system."""
    
    def __init__(self, vector_service, embedding_service):
        self.vector_service = vector_service
        self.embedding_service = embedding_service
    
    def retrieve(self, query: str, n_results: int = 10, 
                 filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Workflow:
        1. Generate query embedding
        2. Search vector database
        3. Return ranked results
        """
        if not self.embedding_service or not self.vector_service:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        if not query_embedding:
            return []
        
        # Search vector database
        results = self.vector_service.search_documents(
            query_embedding=query_embedding,
            n_results=n_results,
            filters=filters
        )
        
        # Rerank results
        reranked_results = self.rerank(results, query)
        
        # Filter results
        filtered_results = self.filter_results(reranked_results)
        
        return filtered_results
    
    def rerank(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Rerank results based on multiple factors:
        - Similarity score
        - File importance (README, main files)
        - Repository relevance
        """
        if not results:
            return []
        
        # Priority files that should be ranked higher
        priority_files = [
            "readme.md",
            "requirements.txt",
            "package.json",
            "main.py",
            "app.py",
            "index.js",
            "index.ts",
        ]
        
        for result in results:
            metadata = result.get("metadata", {})
            file_path = metadata.get("file_path", "").lower()
            base_score = result.get("score", 0.0)
            
            # Boost score for priority files
            boost = 0.0
            for priority_file in priority_files:
                if file_path.endswith(priority_file):
                    boost = 0.2
                    break
            
            # Apply boost
            result["score"] = min(base_score + boost, 1.0)
            result["original_score"] = base_score
            result["boosted"] = boost > 0
        
        # Sort by score descending
        results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        return results
    
    def filter_results(self, results: List[Dict[str, Any]], 
                       min_score: float = 0.3,
                       max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Filter results based on:
        - Minimum similarity score
        - Maximum number of results
        - Remove duplicates
        """
        # Filter by minimum score
        filtered = [r for r in results if r.get("score", 0.0) >= min_score]
        
        # Remove duplicates based on file_path and content similarity
        seen = set()
        unique_results = []
        for result in filtered:
            metadata = result.get("metadata", {})
            file_path = metadata.get("file_path", "")
            content = result.get("content", "")[:100]  # First 100 chars
            
            key = f"{file_path}:{content}"
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Limit to max_results
        return unique_results[:max_results]
    
    def retrieve_by_repository(self, repository_id: str, query: str, 
                               n_results: int = 10) -> List[Dict[str, Any]]:
        """Retrieve chunks from a specific repository."""
        filters = {"repository_id": repository_id}
        return self.retrieve(query, n_results=n_results, filters=filters)
    
    def retrieve_by_language(self, language: str, query: str, 
                            n_results: int = 10) -> List[Dict[str, Any]]:
        """Retrieve chunks from a specific language."""
        filters = {"language": language}
        return self.retrieve(query, n_results=n_results, filters=filters)
    
    def get_context_for_query(self, query: str, max_chunks: int = 5) -> Dict[str, Any]:
        """
        Get formatted context for a query.
        
        Returns:
        - chunks: List of relevant chunks
        - sources: List of source files
        - context_text: Formatted context string
        """
        results = self.retrieve(query, n_results=max_chunks)
        
        if not results:
            return {
                "chunks": [],
                "sources": [],
                "context_text": "No relevant information found."
            }
        
        # Extract sources
        sources = []
        for result in results:
            metadata = result.get("metadata", {})
            file_path = metadata.get("file_path", "")
            if file_path and file_path not in sources:
                sources.append(file_path)
        
        # Format context text
        context_parts = []
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            file_path = metadata.get("file_path", "")
            score = result.get("score", 0.0)
            
            context_parts.append(
                f"[Source {i}: {file_path} (relevance: {score:.2f})]\n{content}\n"
            )
        
        context_text = "\n".join(context_parts)
        
        return {
            "chunks": results,
            "sources": sources,
            "context_text": context_text
        }