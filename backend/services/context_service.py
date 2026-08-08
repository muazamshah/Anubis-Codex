from typing import Any, Dict, List, Optional


class ContextService:
    """Context manager for Phase 3 chat system."""
    
    def __init__(self, retrieval_service):
        self.retrieval_service = retrieval_service
        self.max_context_length = 4000  # tokens
        self.max_chunks = 5
    
    def build_context(self, 
                      question: str, 
                      repository_id: Optional[str] = None,
                      chat_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Build context for a question.
        
        Returns:
        - context: Formatted context string
        - sources: List of source files
        - chunks: Retrieved chunks
        """
        # Get context from retrieval service
        if repository_id:
            retrieval_result = self.retrieval_service.retrieve_by_repository(
                repository_id=repository_id,
                query=question,
                n_results=self.max_chunks
            )
            # Format results into context
            context_text = self._format_retrieval_results(retrieval_result)
            sources = []
            for result in retrieval_result:
                metadata = result.get("metadata", {})
                file_path = metadata.get("file_path", "")
                if file_path and file_path not in sources:
                    sources.append(file_path)
            chunks = retrieval_result
        else:
            retrieval_result = self.retrieval_service.get_context_for_query(
                query=question,
                max_chunks=self.max_chunks
            )
            context_text = retrieval_result.get("context_text", "")
            sources = retrieval_result.get("sources", [])
            chunks = retrieval_result.get("chunks", [])
        
        # Filter and clean context
        cleaned_context = self._clean_context(context_text)
        
        # Truncate if too long
        if len(cleaned_context) > self.max_context_length:
            cleaned_context = cleaned_context[:self.max_context_length] + "..."
        
        return {
            "context": cleaned_context,
            "sources": sources,
            "chunks": chunks,
            "has_relevant_info": len(chunks) > 0
        }
    
    def _format_retrieval_results(self, results: List[Dict[str, Any]]) -> str:
        """Format retrieval results into context text."""
        if not results:
            return "No relevant information found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            file_path = metadata.get("file_path", "")
            score = result.get("score", 0.0)
            
            context_parts.append(
                f"[Source {i}: {file_path} (relevance: {score:.2f})]\n{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _clean_context(self, context: str) -> str:
        """Clean and format context."""
        if not context:
            return "No relevant information found."
        
        # Remove excessive whitespace
        lines = context.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = ' '.join(line.split())
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def merge_contexts(self, contexts: List[str]) -> str:
        """Merge multiple contexts without duplicates."""
        seen = set()
        merged = []
        
        for context in contexts:
            lines = context.split('\n')
            for line in lines:
                line_hash = hash(line.strip())
                if line_hash not in seen:
                    seen.add(line_hash)
                    merged.append(line)
        
        return '\n'.join(merged)
    
    def remove_duplicates(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate chunks based on content similarity."""
        unique_chunks = []
        seen_content = set()
        
        for chunk in chunks:
            content = chunk.get("content", "")[:200]  # First 200 chars
            content_hash = hash(content)
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def prioritize_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize chunks based on relevance and file importance."""
        priority_files = [
            "readme.md",
            "requirements.txt",
            "package.json",
            "main.py",
            "app.py",
            "index.js",
            "index.ts",
        ]
        
        def get_priority(chunk):
            metadata = chunk.get("metadata", {})
            file_path = metadata.get("file_path", "").lower()
            score = chunk.get("score", 0.0)
            
            # Boost priority for important files
            for priority_file in priority_files:
                if file_path.endswith(priority_file):
                    return score + 0.2
            
            return score
        
        chunks.sort(key=get_priority, reverse=True)
        return chunks
    
    def format_context_with_sources(self, chunks: List[Dict[str, Any]]) -> str:
        """Format context with source references."""
        if not chunks:
            return "No relevant information found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
            file_path = metadata.get("file_path", "")
            start_line = metadata.get("start_line", 0)
            end_line = metadata.get("end_line", 0)
            score = chunk.get("score", 0.0)
            
            context_parts.append(
                f"[Source {i}: {file_path} (lines {start_line}-{end_line}, relevance: {score:.2f})]\n{content}\n"
            )
        
        return "\n".join(context_parts)