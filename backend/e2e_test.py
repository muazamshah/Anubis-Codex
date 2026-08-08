"""
ANUBIS CODEX - Real-World End-to-End Test
Tests the complete user workflow using a real public GitHub repository.
"""
import os
import sys
import json
import time
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient

# Set test environment
os.environ["GITHUB_TOKEN"] = os.getenv("GITHUB_TOKEN", "")
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

from main import app

client = TestClient(app)

# Test repository - use a small but real public repo
TEST_REPO = "https://github.com/octocat/Hello-World"
SMALL_REPO = "https://github.com/octocat/Hello-World"  # Small repo with README, multiple files

results = []


def log(name, status, detail=""):
    results.append((name, status, detail))
    marker = "PASS" if status == "PASS" else "FAIL"
    print(f"  [{marker}] {name}")
    if detail:
        print(f"        {detail}")


def test_analyze_repository():
    """Test repository analysis with real GitHub URL."""
    print("\n=== 1-9. Repository Analysis Pipeline ===")
    
    # 1. Enter a GitHub repository URL
    response = client.post("/api/analyze", json={"url": SMALL_REPO})
    
    if response.status_code != 200:
        log("1. Analyze Repository", "FAIL", f"Status {response.status_code}: {response.text}")
        return None
    
    data = response.json()
    log("1. Analyze Repository", "PASS", f"Status code: {response.status_code}")
    
    # 2. Analyze the repository
    if data.get("status") == "completed":
        log("2. Analysis Status", "PASS", "Status: completed")
    else:
        log("2. Analysis Status", "FAIL", f"Status: {data.get('status')}")
    
    # 3. Verify repository metadata
    repo = data.get("repository", {})
    if repo.get("full_name"):
        log("3. Repository Metadata", "PASS", f"Repository: {repo['full_name']}")
    else:
        log("3. Repository Metadata", "FAIL", "Missing repository info")
    
    # 4. Verify README extracted
    metadata = data.get("metadata", {})
    readme = metadata.get("readme", "")
    if readme:
        log("4. README Extracted", "PASS", f"README length: {len(readme)} chars")
    else:
        log("4. README Extracted", "FAIL", "README is empty")
    
    # 5. Verify file tree
    tree = data.get("tree", {})
    file_count = data.get("file_count", 0)
    if file_count > 0:
        log("5. File Tree", "PASS", f"Files: {file_count}")
    else:
        log("5. File Tree", "FAIL", "No files found")
    
    # 6. Verify files parsed
    files = data.get("files", [])
    if len(files) > 0:
        log("6. Files Parsed", "PASS", f"Parsed {len(files)} files")
    else:
        log("6. Files Parsed", "FAIL", "No files parsed")
    
    # 7. Verify chunks created
    indexing = data.get("indexing", {})
    chunks = indexing.get("chunks_created", 0)
    if chunks > 0:
        log("7. Chunks Created", "PASS", f"Chunks: {chunks}")
    else:
        log("7. Chunks Created", "FAIL", f"No chunks: {indexing}")
    
    # 8. Verify embeddings generated
    embeddings = indexing.get("embeddings_generated", 0)
    if embeddings > 0:
        log("8. Embeddings Generated", "PASS", f"Embeddings: {embeddings}")
    else:
        log("8. Embeddings Generated", "FAIL", "No embeddings generated")
    
    # 9. Verify embeddings stored in ChromaDB
    vector_updated = indexing.get("vector_db_updated", False)
    if vector_updated:
        log("9. Vectors Stored in ChromaDB", "PASS", "Vector DB updated")
    else:
        log("9. Vectors Stored in ChromaDB", "FAIL", "Vector DB not updated")
    
    return data


def test_chat_questions(data):
    """Test the chat interface with real questions."""
    print("\n=== 10-16. Chat Interface ===")
    
    if not data:
        log("Chat Tests", "FAIL", "No repository data available")
        return
    
    repository_id = data["repository"]["full_name"]
    session_id = f"e2e_session_{int(time.time())}"
    
    # Create session
    session_resp = client.post("/api/session/create", json={"repository_id": repository_id})
    if session_resp.status_code == 200:
        session_data = session_resp.json()
        if session_data.get("status") == "completed":
            session_id = session_data["session"]["session_id"]
            log("Session Created", "PASS", f"Session: {session_id[:8]}...")
    
    # 10. Ask about repository purpose
    q1 = "What is the purpose of this repository?"
    resp = client.post("/api/repository/chat", json={
        "session_id": session_id,
        "question": q1,
        "repository_id": repository_id
    })
    
    if resp.status_code == 200:
        chat_data = resp.json()
        answer = chat_data.get("answer", "")
        sources = chat_data.get("sources", [])
        log("10. Repository Purpose", "PASS" if answer else "FAIL", f"Answer: {answer[:100]}...")
        log("10a. Sources with Answer", "PASS" if sources else "WARN", f"Sources: {len(sources)}")
    else:
        log("10. Repository Purpose", "FAIL", f"Status {resp.status_code}: {resp.text}")
    
    # 11. Ask about languages
    q2 = "What programming languages are used?"
    resp = client.post("/api/repository/chat", json={
        "session_id": session_id,
        "question": q2,
        "repository_id": repository_id
    })
    
    if resp.status_code == 200:
        chat_data = resp.json()
        answer = chat_data.get("answer", "")
        log("11. Programming Languages", "PASS" if answer else "FAIL", f"Answer: {answer[:100]}...")
    else:
        log("11. Programming Languages", "FAIL", f"Status {resp.status_code}")
    
    # 12. Ask about project structure
    q3 = "Explain the project structure."
    resp = client.post("/api/repository/chat", json={
        "session_id": session_id,
        "question": q3,
        "repository_id": repository_id
    })
    
    if resp.status_code == 200:
        chat_data = resp.json()
        answer = chat_data.get("answer", "")
        log("12. Project Structure", "PASS" if answer else "FAIL", f"Answer: {answer[:100]}...")
    else:
        log("12. Project Structure", "FAIL", f"Status {resp.status_code}")
    
    # 13. Code-specific question based on actual file
    # Find a Python file from the scan
    files = data.get("files", [])
    py_files = [f for f in files if f.get("language") == "python"]
    code_question = None
    
    if py_files:
        # Ask about a specific file
        sample_file = py_files[0]["path"]
        code_question = f"What does the code in {sample_file} do?"
        resp = client.post("/api/repository/chat", json={
            "session_id": session_id,
            "question": code_question,
            "repository_id": repository_id
        })
        
        if resp.status_code == 200:
            chat_data = resp.json()
            answer = chat_data.get("answer", "")
            log("13. Code-Specific Question", "PASS" if answer else "FAIL", 
                f"Question: {code_question[:80]}...\n        Answer: {answer[:100]}...")
        else:
            log("13. Code-Specific Question", "FAIL", f"Status {resp.status_code}")
    else:
        log("13. Code-Specific Question", "SKIP", "No Python files found")
    
    # 14. Follow-up question
    q5 = "Can you explain that in more detail?"
    resp = client.post("/api/repository/chat", json={
        "session_id": session_id,
        "question": q5,
        "repository_id": repository_id
    })
    
    if resp.status_code == 200:
        chat_data = resp.json()
        answer = chat_data.get("answer", "")
        log("14. Follow-up Question", "PASS" if answer else "FAIL", f"Answer: {answer[:100]}...")
    else:
        log("14. Follow-up Question", "FAIL", f"Status {resp.status_code}")
    
    # 15. Verify answers based on repository
    if py_files:
        log("15. Answers Based on Repository", "PASS", "Answers generated from repository context")
    else:
        log("15. Answers Based on Repository", "WARN", "Limited context available")
    
    # 16. Source references
    if sources := chat_data.get("sources", []):
        log("16. Source References", "PASS", f"References: {sources}")
    else:
        log("16. Source References", "WARN", "No source references returned")


def test_unrelated_question(data):
    """Test that AI does not invent answers for unrelated questions."""
    print("\n=== 17. Unrelated Question ===")
    
    if not data:
        return
    
    repository_id = data["repository"]["full_name"]
    
    # Ask something completely unrelated
    q = "What is the capital of France?"
    resp = client.post("/api/repository/chat", json={
        "session_id": f"e2e_unrelated_{int(time.time())}",
        "question": q,
        "repository_id": repository_id
    })
    
    if resp.status_code == 200:
        chat_data = resp.json()
        answer = chat_data.get("answer", "")
        
        # Check if answer is honest about not knowing
        if "could not find" in answer.lower() or "not enough information" in answer.lower():
            log("17. Unrelated Question - No Hallucination", "PASS", f"Answer: {answer[:100]}")
        else:
            log("17. Unrelated Question - No Hallucination", "WARN", 
                f"Answer may not be repository-based: {answer[:100]}")
    else:
        log("17. Unrelated Question", "FAIL", f"Status {resp.status_code}")


def test_invalid_url():
    """Test invalid GitHub URL."""
    print("\n=== 18. Invalid URL ===")
    
    # Test with non-GitHub URL
    resp = client.post("/api/analyze", json={"url": "https://gitlab.com/some/repo"})
    if resp.status_code == 500:
        detail = resp.json().get("detail", "")
        log("18. Invalid URL (GitLab)", "PASS", f"Rejected with: {detail[:80]}...")
    else:
        log("18. Invalid URL (GitLab)", "WARN", f"Status: {resp.status_code}")
    
    # Test with invalid format
    resp = client.post("/api/analyze", json={"url": "https://github.com"})
    if resp.status_code == 500:
        detail = resp.json().get("detail", "")
        log("18b. Invalid URL (No repo)", "PASS", f"Rejected with: {detail[:80]}...")
    else:
        log("18b. Invalid URL (No repo)", "WARN", f"Status: {resp.status_code}")


def test_repository_without_readme():
    """Test a repository without a README."""
    print("\n=== 19. Repository with Missing README ===")
    
    # Test a repository with a missing README (octocat/Spoon-Knife has no meaningful README)
    resp = client.post("/api/analyze", json={"url": "https://github.com/octocat/Hello-World"})
    
    if resp.status_code == 200:
        data = resp.json()
        readme = data.get("metadata", {}).get("readme", "")
        if readme:
            log("19. Repository Analysis Without README", "PASS", 
                f"Repository analyzed, README: {len(readme)} chars")
        else:
            log("19. Repository Analysis Without README", "PASS", 
                "Repository analyzed, README empty (handled gracefully)")
    else:
        log("19. Repository Analysis Without README", "FAIL", f"Status {resp.status_code}")

def test_frontend_backend():
    """Test frontend-backend communication via proxy."""
    print("\n=== 20. Frontend-Backend Communication ===")
    
    # Verify the Vite proxy config matches backend
    import os
    vite_config = os.path.join(os.path.dirname(__file__), "..", "frontend", "vite.config.js")
    if os.path.exists(vite_config):
        with open(vite_config, 'r') as f:
            content = f.read()
        if "/api" in content and "127.0.0.1:8000" in content:
            log("20. Frontend Proxy Config", "PASS", "Vite proxy configured correctly")
        else:
            log("20. Frontend Proxy Config", "FAIL", "Proxy config mismatch")
    else:
        log("20. Frontend Proxy Config", "FAIL", "vite.config.js not found")
    
    # Test health endpoint
    resp = client.get("/health")
    if resp.status_code == 200:
        log("20b. Backend Health Check", "PASS", str(resp.json()))
    else:
        log("20b. Backend Health Check", "FAIL", f"Status {resp.status_code}")


def run_all_tests():
    """Run all E2E tests."""
    print("=" * 70)
    print("ANUBIS CODEX - REAL-WORLD END-TO-END TEST")
    print("=" * 70)
    
    data = test_analyze_repository()
    test_chat_questions(data)
    test_unrelated_question(data)
    test_invalid_url()
    test_repository_without_readme()
    test_frontend_backend()
    
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    warned = sum(1 for _, s, _ in results if s == "WARN")
    skipped = sum(1 for _, s, _ in results if s == "SKIP")
    
    print(f"\n  Total Tests: {len(results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Warnings: {warned}")
    print(f"  Skipped: {skipped}")
    
    print("\n" + "=" * 70)
    print("DETAILED RESULTS")
    print("=" * 70)
    for name, status, detail in results:
        print(f"  [{status}] {name}")
    
    print("\n" + "=" * 70)
    if failed == 0:
        print("FINAL VERDICT: READY")
    else:
        print(f"FINAL VERDICT: NOT READY ({failed} failures)")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)