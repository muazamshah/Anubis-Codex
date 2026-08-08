"""
Integration tests for the complete repository analysis pipeline.
Tests the end-to-end flow from URL parsing to vector storage.
"""
import os
import tempfile
import pytest
from pathlib import Path

# Set test environment
os.environ["GITHUB_TOKEN"] = os.getenv("GITHUB_TOKEN", "")
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

from backend.services.github_service import RepositoryAnalyzerService
from backend.services.download_service import DownloadService
from backend.services.scanner_service import ScannerService
from backend.services.parser_service import ASTParserService
from backend.services.chunk_service import ChunkService
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_service import VectorService
from backend.services.cache_service import CacheService


class TestRepositoryAnalysisPipeline:
    """Test the complete repository analysis pipeline."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository with sample files."""
        temp_dir = tempfile.mkdtemp()
        
        # Create sample Python file
        py_file = Path(temp_dir) / "main.py"
        py_file.write_text("""
def hello_world():
    '''Print hello world.'''
    print("Hello, World!")

class Calculator:
    '''A simple calculator class.'''
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
""")
        
        # Create sample JavaScript file
        js_file = Path(temp_dir) / "app.js"
        js_file.write_text("""
function greet(name) {
    return `Hello, ${name}!`;
}

class User {
    constructor(name) {
        this.name = name;
    }
    
    getName() {
        return this.name;
    }
}
""")
        
        # Create README
        readme = Path(temp_dir) / "README.md"
        readme.write_text("""
# Test Repository

This is a test repository for integration testing.

## Features

- Python code
- JavaScript code
- Documentation
""")
        
        yield temp_dir
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_url_parsing(self):
        """Test GitHub URL parsing."""
        service = RepositoryAnalyzerService()
        
        # Valid URLs
        payload = service.parse_url("https://github.com/openai/openai-cookbook")
        assert payload["owner"] == "openai"
        assert payload["repo"] == "openai-cookbook"
        assert payload["is_github"] is True
        
        # URL with trailing slash
        payload = service.parse_url("https://github.com/facebook/react/")
        assert payload["owner"] == "facebook"
        assert payload["repo"] == "react"
        
        # Invalid URL
        with pytest.raises(ValueError):
            service.parse_url("https://gitlab.com/some/repo")
    
    def test_scanner_with_content(self, temp_repo):
        """Test scanner service with file content reading."""
        scanner = ScannerService()
        result = scanner.scan_repository_with_content(temp_repo)
        
        assert result["count"] == 3
        assert len(result["files"]) == 3
        assert result["languages"] == ["javascript", "markdown", "python"]
        
        # Check file contents are included
        for file_info in result["files"]:
            assert "content" in file_info
            if file_info["name"] == "main.py":
                assert "def hello_world" in file_info["content"]
            elif file_info["name"] == "README.md":
                assert "# Test Repository" in file_info["content"]
    
    def test_parser_python(self, temp_repo):
        """Test Python file parsing."""
        parser = ASTParserService()
        
        py_file = Path(temp_repo) / "main.py"
        result = parser.parse_file(str(py_file), "python")
        
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "Calculator"

        # Parser extracts all functions including class methods via AST walk
        function_names = [f["name"] for f in result["functions"]]
        assert "hello_world" in function_names
        assert "add" in function_names
        assert "subtract" in function_names
        
        assert len(result["imports"]) == 0  # No imports in sample
        # File starts with function def, not module docstring
        assert len(result["docstrings"]) == 0
    
    def test_parser_javascript(self, temp_repo):
        """Test JavaScript file parsing."""
        parser = ASTParserService()
        
        js_file = Path(temp_repo) / "app.js"
        result = parser.parse_file(str(js_file), "javascript")
        
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "User"
        
        assert len(result["functions"]) >= 1
        function_names = [f["name"] for f in result["functions"]]
        assert "greet" in function_names
    
    def test_chunk_service(self, temp_repo):
        """Test chunking service."""
        chunk_service = ChunkService(chunk_size=100, chunk_overlap=20)
        
        # Test Python chunking
        py_file = Path(temp_repo) / "main.py"
        content = py_file.read_text()
        file_data = {
            "path": "main.py",
            "name": "main.py",
            "language": "python",
            "content": content,
        }
        
        chunks = chunk_service.chunk_file(file_data, "test-repo")
        assert len(chunks) > 0
        
        # Check chunk structure
        for chunk in chunks:
            assert "repository_id" in chunk
            assert "file_name" in chunk
            assert "content" in chunk
            assert chunk["repository_id"] == "test-repo"
    
    def test_embedding_service(self):
        """Test embedding generation."""
        embedding_service = EmbeddingService()
        
        # Test single embedding
        text = "Hello, world!"
        embedding = embedding_service.generate_embedding(text)
        
        assert embedding is not None
        assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
        
        # Test multiple embeddings
        texts = ["Hello", "World", "Test"]
        embeddings = embedding_service.generate_embeddings(texts)
        
        assert len(embeddings) == 3
        for emb in embeddings:
            assert len(emb) == 384
    
    def test_vector_service(self):
        """Test vector database operations."""
        vector_service = VectorService(persist_directory="cache/test_vector_db")
        
        # Test availability
        assert vector_service.is_available()
        
        # Test adding documents
        chunks = [
            {
                "repository_id": "test-repo",
                "file_name": "test.py",
                "file_path": "test.py",
                "language": "python",
                "content": "def test(): pass",
                "chunk_id": "test-1",
            }
        ]
        
        embeddings = [[0.1] * 384]
        success = vector_service.add_documents(chunks, embeddings)
        assert success
        
        # Test search
        query_embedding = [0.1] * 384
        results = vector_service.search_documents(query_embedding, n_results=1)
        assert len(results) > 0
        assert results[0]["metadata"]["file_name"] == "test.py"
        
        # Cleanup
        vector_service.clear_collection()
    
    def test_cache_service(self):
        """Test caching service."""
        cache_service = CacheService(cache_dir="cache/test_cache")
        
        # Test caching embeddings
        test_embedding = [0.1] * 384
        success = cache_service.cache_embeddings("test-chunk", test_embedding)
        assert success
        
        # Test loading embeddings
        loaded = cache_service.get_embeddings("test-chunk")
        assert loaded is not None
        assert len(loaded) == 384
        
        # Cleanup
        cache_service.clear_all()
    
    def test_full_pipeline(self, temp_repo):
        """Test the complete analysis pipeline."""
        # Initialize services
        scanner = ScannerService()
        parser = ASTParserService()
        chunk_service = ChunkService()
        embedding_service = EmbeddingService()
        vector_service = VectorService(persist_directory="cache/test_integration_db")
        cache_service = CacheService(cache_dir="cache/test_integration_cache")
        
        # Step 1: Scan repository
        scan_result = scanner.scan_repository_with_content(temp_repo)
        assert scan_result["count"] > 0
        
        # Step 2: Parse and chunk files
        repository_id = "test-repo"
        all_chunks = []
        
        for file_data in scan_result["files"]:
            if file_data.get("content"):
                # Parse file (use full path)
                full_path = os.path.join(temp_repo, file_data["path"])
                parsed = parser.parse_file(full_path, file_data["language"])
                
                # Chunk file
                chunks = chunk_service.chunk_file(file_data, repository_id)
                all_chunks.extend(chunks)
        
        assert len(all_chunks) > 0
        
        # Step 3: Generate embeddings
        texts = [chunk.get("content", "") for chunk in all_chunks]
        embeddings = embedding_service.generate_embeddings(texts)
        
        assert len(embeddings) == len(all_chunks)
        
        # Step 4: Store in vector database
        success = vector_service.add_documents(all_chunks, embeddings)
        assert success
        
        # Step 5: Verify storage
        stats = vector_service.get_collection_stats()
        assert stats["count"] > 0
        
        # Step 6: Test retrieval
        query = "hello world function"
        query_embedding = embedding_service.generate_embedding(query)
        results = vector_service.search_documents(query_embedding, n_results=3)
        
        assert len(results) > 0
        assert results[0]["metadata"]["repository_id"] == repository_id
        
        # Cleanup
        vector_service.clear_collection()
        cache_service.clear_all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])