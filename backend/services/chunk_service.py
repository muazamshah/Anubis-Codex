from typing import Any, Dict, List


class ChunkService:
    """Chunking engine for Phase 2 RAG system."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_file(self, file_data: Dict[str, Any], repository_id: str) -> List[Dict[str, Any]]:
        """Chunk a single file into logical sections."""
        content = file_data.get("content", "")
        if not content:
            return []
        
        language = file_data.get("language", "text")
        file_path = file_data.get("file_path", "")
        file_name = file_data.get("file_name", "")
        
        # For Python files, use AST-aware chunking
        if language == "python":
            return self._chunk_python(content, file_path, file_name, language, repository_id)
        else:
            return self._chunk_generic(content, file_path, file_name, language, repository_id)
    
    def _chunk_python(self, content: str, file_path: str, file_name: str, language: str, repository_id: str) -> List[Dict[str, Any]]:
        """Chunk Python files using AST-aware splitting."""
        chunks = []
        lines = content.split('\n')
        
        # Try to parse with AST
        try:
            import ast
            tree = ast.parse(content)
            
            # Extract top-level definitions
            definitions = []
            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    start_line = node.lineno
                    end_line = self._get_end_line(node)
                    definitions.append({
                        "type": "class" if isinstance(node, ast.ClassDef) else "function",
                        "name": node.name,
                        "start": start_line,
                        "end": end_line,
                    })
            
            # Create chunks based on definitions
            if definitions:
                for i, defn in enumerate(definitions):
                    chunk_content = '\n'.join(lines[defn["start"]-1:defn["end"]])
                    
                    # Get class/function context
                    class_name = defn["name"] if defn["type"] == "class" else ""
                    function_name = defn["name"] if defn["type"] == "function" else ""
                    
                    # If it's a method, find the parent class
                    if defn["type"] == "function":
                        for prev_defn in reversed(definitions[:i]):
                            if prev_defn["type"] == "class" and prev_defn["end"] >= defn["start"]:
                                class_name = prev_defn["name"]
                                break
                    
                    chunks.append({
                        "repository_id": repository_id,
                        "file_name": file_name,
                        "file_path": file_path,
                        "language": language,
                        "class_name": class_name,
                        "function_name": function_name,
                        "content": chunk_content,
                        "start_line": defn["start"],
                        "end_line": defn["end"],
                    })
                
                return chunks
        except SyntaxError:
            pass
        
        # Fallback to generic chunking
        return self._chunk_generic(content, file_path, file_name, language, repository_id)
    
    def _chunk_generic(self, content: str, file_path: str, file_name: str, language: str, repository_id: str) -> List[Dict[str, Any]]:
        """Generic chunking for non-Python files."""
        chunks = []
        lines = content.split('\n')
        
        # Split by lines with overlap
        start = 0
        chunk_index = 0
        
        while start < len(lines):
            end = min(start + self.chunk_size, len(lines))
            chunk_content = '\n'.join(lines[start:end])
            
            chunks.append({
                "repository_id": repository_id,
                "file_name": file_name,
                "file_path": file_path,
                "language": language,
                "class_name": "",
                "function_name": "",
                "content": chunk_content,
                "start_line": start + 1,
                "end_line": end,
                "chunk_index": chunk_index,
            })
            
            chunk_index += 1
            start += self.chunk_size - self.chunk_overlap
            
            if start >= len(lines):
                break
        
        return chunks
    
    def _get_end_line(self, node) -> int:
        """Get the end line of an AST node."""
        import ast
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno
        
        # Fallback: estimate based on body
        if hasattr(node, 'body') and node.body:
            last_node = node.body[-1]
            return self._get_end_line(last_node)
        return node.lineno + 10  # Default fallback
    
    def chunk_repository(self, files: List[Dict[str, Any]], repository_id: str) -> List[Dict[str, Any]]:
        """Chunk all files in a repository."""
        all_chunks = []
        
        for file_data in files:
            file_chunks = self.chunk_file(file_data, repository_id)
            all_chunks.extend(file_chunks)
        
        return all_chunks