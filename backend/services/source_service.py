from typing import Any, Dict, List, Optional


class SourceService:
    """Source manager for Phase 3 chat system."""
    
    def __init__(self):
        self.sources = {}
    
    def track_source(self, 
                     chunk_id: str, 
                     file_path: str, 
                     start_line: int, 
                     end_line: int,
                     repository_id: str,
                     score: float) -> Dict[str, Any]:
        """Track a source reference."""
        source = {
            "chunk_id": chunk_id,
            "file_path": file_path,
            "start_line": start_line,
            "end_line": end_line,
            "repository_id": repository_id,
            "score": score,
            "timestamp": None,
        }
        
        self.sources[chunk_id] = source
        return source
    
    def get_source(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get source information by chunk ID."""
        return self.sources.get(chunk_id)
    
    def get_sources_by_repository(self, repository_id: str) -> List[Dict[str, Any]]:
        """Get all sources for a repository."""
        return [
            source for source in self.sources.values()
            if source.get("repository_id") == repository_id
        ]
    
    def format_source_reference(self, chunk_id: str) -> str:
        """Format source reference for display."""
        source = self.get_source(chunk_id)
        if not source:
            return "Unknown source"
        
        file_path = source.get("file_path", "unknown")
        start_line = source.get("start_line", 0)
        end_line = source.get("end_line", 0)
        score = source.get("score", 0.0)
        
        return f"{file_path} (lines {start_line}-{end_line}, score: {score:.2f})"
    
    def format_sources_list(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format a list of sources from chunks."""
        sources = []
        seen_files = set()
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            file_path = metadata.get("file_path", "")
            
            # Avoid duplicate file references
            if file_path in seen_files:
                continue
            seen_files.add(file_path)
            
            source = {
                "file": file_path,
                "language": metadata.get("language", ""),
                "start_line": metadata.get("start_line", 0),
                "end_line": metadata.get("end_line", 0),
                "class_name": metadata.get("class_name", ""),
                "function_name": metadata.get("function_name", ""),
                "score": chunk.get("score", 0.0),
            }
            sources.append(source)
        
        return sources
    
    def build_citation(self, chunk: Dict[str, Any]) -> str:
        """Build citation string for a chunk."""
        metadata = chunk.get("metadata", {})
        file_path = metadata.get("file_path", "unknown")
        start_line = metadata.get("start_line", 0)
        end_line = metadata.get("end_line", 0)
        
        return f"[Source: {file_path}, lines {start_line}-{end_line}]"
    
    def build_citations_list(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Build list of citations for multiple chunks."""
        citations = []
        for chunk in chunks:
            citation = self.build_citation(chunk)
            if citation not in citations:
                citations.append(citation)
        return citations
    
    def clear_sources(self):
        """Clear all tracked sources."""
        self.sources.clear()
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """Get statistics about tracked sources."""
        repositories = {}
        for source in self.sources.values():
            repo_id = source.get("repository_id", "unknown")
            if repo_id not in repositories:
                repositories[repo_id] = 0
            repositories[repo_id] += 1
        
        return {
            "total_sources": len(self.sources),
            "repositories": repositories,
            "unique_files": len(set(s.get("file_path") for s in self.sources.values()))
        }