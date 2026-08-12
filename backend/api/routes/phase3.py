from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.chat_service import ChatService
from services.memory_service import MemoryService
from services.session_service import SessionService
from config import validate_config

router = APIRouter(prefix="/api", tags=["phase3"])

# Initialize services
chat_service = ChatService()
memory_service = MemoryService()
session_service = SessionService()


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    question: str
    repository_id: str = "default"


class SessionCreateRequest(BaseModel):
    repository_id: str = "default"
    metadata: Optional[Dict[str, Any]] = None


class SessionDeleteRequest(BaseModel):
    session_id: str


@router.post("/chat")
def chat(payload: ChatRequest) -> Dict[str, Any]:
    """Send a chat message and get a response."""
    try:
        session_id = payload.session_id or "default"
        
        result = chat_service.send_message(
            session_id=session_id,
            question=payload.question,
            repository_id=payload.repository_id
        )
        
        return {
            "status": "completed",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


from fastapi.responses import StreamingResponse
import json

@router.post("/chat/stream")
def chat_stream(payload: ChatRequest):
    """Stream a chat response."""
    try:
        session_id = payload.session_id or "default"
        
        async def generate():
            async for token in chat_service.stream_message(
                session_id=session_id,
                question=payload.question,
                repository_id=payload.repository_id
            ):
                yield token
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")


@router.post("/session/create")
def create_session(payload: SessionCreateRequest) -> Dict[str, Any]:
    """Create a new chat session."""
    try:
        session = chat_service.create_session(
            repository_id=payload.repository_id
        )
        
        return {
            "status": "completed",
            "session": session
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")


@router.post("/session/delete")
def delete_session(payload: SessionDeleteRequest) -> Dict[str, Any]:
    """Delete a session."""
    try:
        success = chat_service.delete_session(payload.session_id)
        
        return {
            "status": "completed" if success else "failed",
            "message": "Session deleted successfully" if success else "Failed to delete session"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session deletion failed: {str(e)}")


@router.get("/history")
def get_history(session_id: str) -> Dict[str, Any]:
    """Get conversation history."""
    try:
        history = chat_service.get_history(session_id)
        
        return {
            "status": "completed",
            "session_id": session_id,
            "history": history,
            "message_count": len(history)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@router.delete("/history/clear")
def clear_history(session_id: str) -> Dict[str, Any]:
    """Clear conversation history."""
    try:
        success = chat_service.clear_session(session_id)
        
        return {
            "status": "completed" if success else "failed",
            "message": "History cleared successfully" if success else "Failed to clear history"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History clear failed: {str(e)}")


@router.get("/sessions")
def list_sessions(repository_id: Optional[str] = None) -> Dict[str, Any]:
    """List all sessions."""
    try:
        sessions = session_service.list_sessions(repository_id=repository_id)
        
        return {
            "status": "completed",
            "sessions": sessions,
            "count": len(sessions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session listing failed: {str(e)}")


@router.get("/status")
def get_chat_status() -> Dict[str, Any]:
    """Get Phase 3 system status."""
    try:
        # Session statistics
        session_stats = session_service.get_session_statistics()
        
        # Chat service availability
        chat_available = chat_service.is_available()
        
        return {
            "status": "active",
            "phase": "Phase 3 - AI Chat Engine",
            "chat_service_available": chat_available,
            "sessions": session_stats
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/config/status")
def get_config_status() -> Dict[str, Any]:
    """
    Get configuration status.
    
    Returns the status of all APIs and services without exposing actual API keys.
    """
    try:
        return validate_config()
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
