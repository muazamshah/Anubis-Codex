import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.download_service import DownloadService
from services.github_service import RepositoryAnalyzerService
from services.metadata_service import MetadataService
from services.scanner_service import ScannerService
from services.parser_service import ASTParserService
from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService
from services.cache_service import CacheService

router = APIRouter(prefix="/api", tags=["repository"])


class RepositoryRequest(BaseModel):
    url: str


class RepositoryChatRequest(BaseModel):
    session_id: str
    question: str
    repository_id: str


# Initialize services
scanner_service = ScannerService()
parser_service = ASTParserService()
chunk_service = ChunkService()
metadata_service = MetadataService()
embedding_service = EmbeddingService()
vector_service = VectorService()
cache_service = CacheService()


@router.post("/analyze")
def analyze_repository(payload: RepositoryRequest) -> Dict[str, Any]:
    """
    Complete repository analysis pipeline.
    
    Steps:
    1. Parse GitHub URL
    2. Download repository
    3. Scan files with content
    4. Extract metadata
    5. Parse files (AST)
    6. Chunk files
    7. Generate embeddings
    8. Store in vector database
    """
    try:
        analyzer = RepositoryAnalyzerService()
        download_service = DownloadService()

        # Step 1: Parse URL
        parsed = analyzer.parse_url(payload.url)
        repository_id = f"{parsed['owner']}/{parsed['repo']}"

        # Step 2: Download repository
        repo_path = download_service.download_repository(parsed["owner"], parsed["repo"])

        # Step 3: Scan repository with content
        scan_result = scanner_service.scan_repository_with_content(repo_path)

        # Step 4: Extract metadata
        github_metadata = analyzer.analyze_repository(payload.url)
        metadata = metadata_service.extract_metadata(repo_path, github_metadata)

        # Step 5-8: Create embeddings and store in vector database
        indexing_result = {
            "chunks_created": 0,
            "embeddings_generated": 0,
            "vector_db_updated": False,
        }

        try:
            # Parse and chunk files
            all_chunks = []
            for file_data in scan_result["files"]:
                if file_data.get("content"):
                    # Parse file (use full path)
                    full_path = os.path.join(repo_path, file_data["path"])
                    parsed_data = parser_service.parse_file(
                        full_path, 
                        file_data["language"]
                    )
                    
                    # Chunk file
                    file_chunks = chunk_service.chunk_file(file_data, repository_id)
                    all_chunks.extend(file_chunks)

            indexing_result["chunks_created"] = len(all_chunks)

            # Generate embeddings
            if all_chunks:
                texts = [chunk.get("content", "") for chunk in all_chunks]
                embeddings = embedding_service.generate_embeddings(texts)
                indexing_result["embeddings_generated"] = len(embeddings)

                # Store in vector database
                success = vector_service.add_documents(all_chunks, embeddings)
                indexing_result["vector_db_updated"] = success

                # Cache embeddings
                for chunk, embedding in zip(all_chunks, embeddings):
                    chunk_id = chunk.get("chunk_id", "")
                    if chunk_id:
                        cache_service.cache_embeddings(chunk_id, embedding)

        except Exception as e:
            # Don't fail the entire analysis if indexing fails
            indexing_result["error"] = str(e)

        return {
            "status": "completed",
            "repository": {
                "url": payload.url,
                "owner": parsed["owner"],
                "name": parsed["repo"],
                "full_name": repository_id,
            },
            "metadata": metadata,
            "files": scan_result["files"],
            "file_count": scan_result["count"],
            "languages": scan_result["languages"],
            "tree": scan_result["tree"],
            "indexing": indexing_result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository analysis failed: {str(e)}")


@router.get("/repository/status")
def get_repository_status(repository_id: str) -> Dict[str, Any]:
    """Get the analysis and indexing status of a repository."""
    try:
        # Check vector database for repository chunks
        vector_stats = vector_service.get_collection_stats()
        
        # Try to get repository-specific stats
        try:
            # Query for any chunks from this repository
            results = vector_service.search_documents(
                query_embedding=embedding_service.generate_embedding("test"),
                n_results=1,
                filters={"repository_id": repository_id}
            )
            has_vectors = len(results) > 0
        except Exception:
            has_vectors = False

        return {
            "status": "active",
            "repository_id": repository_id,
            "indexed": has_vectors,
            "vector_db_status": vector_stats,
            "message": "Repository is indexed and ready for chat" if has_vectors else "Repository not indexed yet"
        }

    except Exception as e:
        return {
            "status": "error",
            "repository_id": repository_id,
            "indexed": False,
            "error": str(e)
        }


@router.post("/repository/chat")
def repository_chat(payload: RepositoryChatRequest) -> Dict[str, Any]:
    """
    Chat with a specific repository.
    
    This endpoint automatically uses the repository context without requiring
    the user to specify repository_id in the chat service.
    """
    try:
        from services.chat_service import ChatService
        from services.retrieval_service import RetrievalService
        from services.context_service import ContextService

        # Use global services to avoid duplicate model loading
        chat_service = ChatService()
        retrieval_service = RetrievalService(vector_service, embedding_service)
        context_service = ContextService(retrieval_service)

        # Get session
        session = chat_service.session_service.get_session(payload.session_id)
        if not session:
            session = chat_service.create_session(payload.repository_id)
            session_id = session["session_id"]
        else:
            session_id = payload.session_id

        # Load chat history
        chat_history = chat_service.memory_service.load_history(session_id) or []

        # Validate and optimize query
        query_result = chat_service.query_service.validate_query(payload.question)
        if not query_result["valid"]:
            return {
                "answer": "Invalid question. Please ask a valid question.",
                "sources": [],
                "session_id": session_id
            }

        optimized_question = query_result["optimized"]
        final_question = chat_service.query_service.rewrite_ambiguous_question(
            optimized_question, 
            chat_history
        )

        # Build context with repository filter
        context_result = context_service.build_context(
            question=final_question,
            repository_id=payload.repository_id,
            chat_history=chat_history
        )

        context = context_result.get("context", "")
        sources = context_result.get("sources", [])
        chunks = context_result.get("chunks", [])
        has_relevant_info = context_result.get("has_relevant_info", False)

        # Build prompt
        repository_info = {
            "name": payload.repository_id,
            "description": "Repository analysis"
        }

        prompt = chat_service.prompt_service.build_prompt(
            question=final_question,
            context=context,
            chat_history=chat_history,
            repository_info=repository_info
        )

        # Generate response
        if has_relevant_info:
            answer = chat_service._call_llm(prompt)
        else:
            answer = "I could not find enough information inside the repository to answer your question."

        # Save messages to memory
        chat_service.memory_service.save_message(session_id, "user", payload.question)
        chat_service.memory_service.save_message(session_id, "assistant", answer, {
            "sources": sources,
            "chunks": chunks
        })

        # Update session
        chat_service.session_service.increment_message_count(session_id)

        # Format sources
        formatted_sources = chat_service.source_service.format_sources_list(chunks)

        return {
            "status": "completed",
            "answer": answer,
            "sources": formatted_sources,
            "session_id": session_id,
            "question": payload.question,
            "repository_id": payload.repository_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository chat failed: {str(e)}")
