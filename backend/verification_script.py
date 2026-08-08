"""
ANUBIS CODEX - System Verification Script
Tests all components and generates a comprehensive report.
"""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))

results = []
errors = []


def check(name, fn):
    """Run a verification check and record the result."""
    try:
        fn()
        results.append((name, "PASS", ""))
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        errors.append((name, error_msg))
        results.append((name, "FAIL", error_msg))


def verify_imports():
    """Check all imports."""
    from services.github_service import RepositoryAnalyzerService
    from services.download_service import DownloadService
    from services.scanner_service import ScannerService
    from services.parser_service import ASTParserService
    from services.chunk_service import ChunkService
    from services.embedding_service import EmbeddingService
    from services.vector_service import VectorService
    from services.retrieval_service import RetrievalService
    from services.chat_service import ChatService
    from services.cache_service import CacheService
    from services.metadata_service import MetadataService
    from services.context_service import ContextService
    from services.source_service import SourceService
    from services.query_service import QueryService
    from services.streaming_service import StreamingService
    from services.session_service import SessionService
    from services.memory_service import MemoryService
    from services.prompt_service import PromptService


def verify_dependencies():
    """Check all required packages are installed."""
    import fastapi
    import pydantic
    import requests
    import github
    import chromadb
    from sentence_transformers import SentenceTransformer


def verify_url_parsing():
    """Test GitHub URL parsing."""
    from services.github_service import RepositoryAnalyzerService
    svc = RepositoryAnalyzerService()
    
    # Valid URL
    parsed = svc.parse_url("https://github.com/openai/openai-cookbook")
    assert parsed["owner"] == "openai"
    assert parsed["repo"] == "openai-cookbook"
    
    # URL with trailing slash
    parsed = svc.parse_url("https://github.com/facebook/react/")
    assert parsed["owner"] == "facebook"
    assert parsed["repo"] == "react"
    
    # URL with path
    parsed = svc.parse_url("https://github.com/owner/repo/tree/main/src")
    assert parsed["owner"] == "owner"
    assert parsed["repo"] == "repo"
    
    # Invalid URL
    try:
        svc.parse_url("https://gitlab.com/some/repo")
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass


def verify_scanner():
    """Test scanner service with temporary files."""
    import tempfile
    from pathlib import Path
    from services.scanner_service import ScannerService
    
    with tempfile.TemporaryDirectory() as tmp:
        # Create test files
        (Path(tmp) / "main.py").write_text("def hello():\n    return 'hello'\n")
        (Path(tmp) / "app.js").write_text("function greet() { return 'hi'; }\n")
        (Path(tmp) / "README.md").write_text("# Test\n")
        
        # Test ignored directories
        (Path(tmp) / "node_modules").mkdir()
        (Path(tmp) / "node_modules" / "dep.js").write_text("// ignored")
        (Path(tmp) / "__pycache__").mkdir()
        (Path(tmp) / "__pycache__" / "cached.pyc").write_text("ignored")
        (Path(tmp) / ".git").mkdir()
        (Path(tmp) / ".git" / "config").write_text("ignored")
        (Path(tmp) / "venv").mkdir()
        (Path(tmp) / "venv" / "lib.py").write_text("ignored")
        
        # Test scan
        svc = ScannerService()
        result = svc.scan_repository_with_content(tmp)
        
        assert result["count"] == 3, f"Expected 3 files, got {result['count']}"
        assert "main.py" in [f["path"] for f in result["files"]]
        assert "app.js" in [f["path"] for f in result["files"]]
        assert "README.md" in [f["path"] for f in result["files"]]
        
        # Test content inclusion
        for f in result["files"]:
            assert "content" in f, f"File {f['path']} missing content"
        
        # Verify ignored dirs were excluded
        paths = [f["path"] for f in result["files"]]
        assert not any("node_modules" in p for p in paths)
        assert not any("__pycache__" in p for p in paths)
        assert not any(".git" in p for p in paths)
        assert not any("venv" in p for p in paths)


def verify_parser():
    """Test AST parser."""
    import tempfile
    from pathlib import Path
    from services.parser_service import ASTParserService
    
    with tempfile.TemporaryDirectory() as tmp:
        # Python file
        py_file = Path(tmp) / "test.py"
        py_file.write_text("""
import os
from typing import List

class MyClass:
    '''Docstring'''
    def method(self, x):
        return x

def my_function():
    '''Function docstring'''
    pass
""")
        
        parser = ASTParserService()
        result = parser.parse_file(str(py_file), "python")
        
        assert len(result["classes"]) == 1, f"Expected 1 class, got {len(result['classes'])}"
        assert result["classes"][0]["name"] == "MyClass"
        # Parser extracts both module-level functions and class methods
        function_names = [f["name"] for f in result["functions"]]
        assert "my_function" in function_names, f"Expected my_function in {function_names}"
        assert len(result["imports"]) == 2, f"Expected 2 imports, got {len(result['imports'])}"
        # Docstring extraction only captures module-level docstring
        # Since file starts with imports, no module docstring is extracted
        assert len(result["docstrings"]) == 0, f"Expected 0 docstrings, got {len(result['docstrings'])}"


def verify_chunking():
    """Test chunk service."""
    from services.chunk_service import ChunkService
    
    svc = ChunkService(chunk_size=50, chunk_overlap=10)
    
    # Python file with functions
    file_data = {
        "path": "main.py",
        "name": "main.py",
        "language": "python",
        "content": """def func1():
    return 1

def func2():
    return 2

def func3():
    return 3
""",
    }
    
    chunks = svc.chunk_file(file_data, "test-repo")
    assert len(chunks) > 0, "No chunks created"
    
    for chunk in chunks:
        assert "repository_id" in chunk
        assert "file_name" in chunk
        assert "file_path" in chunk
        assert "content" in chunk
        assert "start_line" in chunk
        assert "end_line" in chunk


def verify_embedding():
    """Test embedding service."""
    from services.embedding_service import EmbeddingService
    
    svc = EmbeddingService()
    
    # Test single embedding
    emb = svc.generate_embedding("test text")
    assert emb is not None, "Embedding is None"
    assert len(emb) == 384, f"Expected 384 dims, got {len(emb)}"
    
    # Test batch embeddings
    embs = svc.generate_embeddings(["one", "two", "three"])
    assert len(embs) == 3, "Expected 3 embeddings"
    for e in embs:
        assert len(e) == 384


def verify_vector_db():
    """Test vector database."""
    from services.vector_service import VectorService
    
    svc = VectorService(persist_directory="cache/verification_db")
    
    # Add document
    chunks = [{
        "repository_id": "test",
        "file_name": "test.py",
        "file_path": "test.py",
        "language": "python",
        "content": "def test(): pass",
        "chunk_id": "test-1",
    }]
    embeddings = [[0.5] * 384]
    
    success = svc.add_documents(chunks, embeddings)
    assert success, "Failed to add documents"
    
    # Search
    results = svc.search_documents([0.5] * 384, n_results=1)
    assert len(results) > 0, "No results found"
    assert results[0]["metadata"]["file_name"] == "test.py"
    
    # Stats
    stats = svc.get_collection_stats()
    assert stats["count"] > 0, "Collection is empty"
    
    # Cleanup
    svc.clear_collection()


def verify_retrieval():
    """Test retrieval service."""
    from services.embedding_service import EmbeddingService
    from services.vector_service import VectorService
    from services.retrieval_service import RetrievalService
    
    embedding = EmbeddingService()
    vector = VectorService(persist_directory="cache/verification_db")
    retrieval = RetrievalService(vector, embedding)
    
    # Add test data
    chunks = [{
        "repository_id": "test-repo",
        "file_name": "main.py",
        "file_path": "main.py",
        "language": "python",
        "content": "def hello_world():\n    print('Hello World')",
        "chunk_id": "retrieval-1",
    }]
    embeddings = embedding.generate_embeddings([chunks[0]["content"]])
    vector.add_documents(chunks, embeddings)
    
    # Test retrieval with repository filter
    results = retrieval.retrieve_by_repository("test-repo", "hello world", n_results=1)
    assert len(results) > 0, "No retrieval results"
    
    # Test generic retrieval
    results = retrieval.retrieve("hello world", n_results=1)
    assert len(results) > 0, "No generic retrieval results"
    
    # Cleanup
    vector.clear_collection()


def verify_chat():
    """Test chat service initialization."""
    from services.chat_service import ChatService
    
    svc = ChatService()
    assert svc.memory_service is not None
    assert svc.prompt_service is not None
    assert svc.source_service is not None
    assert svc.query_service is not None
    assert svc.streaming_service is not None
    assert svc.session_service is not None


def verify_api_routes():
    """Verify FastAPI routes are registered."""
    from main import app
    
    # Get OpenAPI schema which contains all routes
    openapi = app.openapi()
    paths = openapi.get("paths", {})
    
    required_paths = [
        "/api/analyze",
        "/api/repository/status",
        "/api/repository/chat",
        "/api/embeddings/create",
        "/api/retrieve",
        "/api/search",
        "/api/chat",
        "/health",
    ]
    
    for path in required_paths:
        assert path in paths, f"Missing route: {path}"


def verify_no_circular_imports():
    """Check for circular imports by importing main module."""
    import main
    assert main.app is not None, "App failed to initialize"


def run_all_checks():
    """Run all verification checks."""
    print("=" * 60)
    print("ANUBIS CODEX - SYSTEM VERIFICATION")
    print("=" * 60)
    
    check("1. Import Statements", verify_imports)
    check("2. Dependencies", verify_dependencies)
    check("3. URL Parsing", verify_url_parsing)
    check("4. Scanner Service", verify_scanner)
    check("5. AST Parser", verify_parser)
    check("6. Chunking", verify_chunking)
    check("7. Embedding Generation", verify_embedding)
    check("8. Vector Database", verify_vector_db)
    check("9. Retrieval", verify_retrieval)
    check("10. Chat Service", verify_chat)
    check("11. API Routes", verify_api_routes)
    check("12. Circular Imports", verify_no_circular_imports)
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for name, status, error in results:
        if status == "PASS":
            passed += 1
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name}: {error}")
    
    print(f"\n  Total: {len(results)}, Passed: {passed}, Failed: {len(results) - passed}")
    
    if errors:
        print("\n" + "=" * 60)
        print("ERROR DETAILS")
        print("=" * 60)
        for name, error in errors:
            print(f"\n  {name}:\n    {error}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    return passed == len(results)


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)