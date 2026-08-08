from typing import Any, Dict, List, Optional, AsyncGenerator
import asyncio
import json


class StreamingService:
    """Streaming engine for Phase 3 chat system."""
    
    def __init__(self):
        self.active_streams = {}
        self.is_streaming = False
    
    async def stream_response(self, 
                              response_generator,
                              session_id: str) -> AsyncGenerator[str, None]:
        """
        Stream response tokens.
        
        Args:
            response_generator: Function that yields response tokens
            session_id: Session identifier
        """
        self.is_streaming = True
        self.active_streams[session_id] = True
        
        try:
            async for token in response_generator:
                if not self.active_streams.get(session_id, False):
                    break
                yield token
        finally:
            self.active_streams[session_id] = False
            if all(not v for v in self.active_streams.values()):
                self.is_streaming = False
    
    def stop_stream(self, session_id: str) -> bool:
        """Stop streaming for a session."""
        if session_id in self.active_streams:
            self.active_streams[session_id] = False
            return True
        return False
    
    def pause_stream(self, session_id: str) -> bool:
        """Pause streaming for a session."""
        # Implementation for pause functionality
        if session_id in self.active_streams:
            self.active_streams[session_id] = False
            return True
        return False
    
    def resume_stream(self, session_id: str) -> bool:
        """Resume streaming for a session."""
        if session_id in self.active_streams:
            self.active_streams[session_id] = True
            return True
        return False
    
    def is_active(self, session_id: str) -> bool:
        """Check if stream is active for a session."""
        return self.active_streams.get(session_id, False)
    
    def format_sse(self, data: Dict[str, Any]) -> str:
        """Format data as Server-Sent Event."""
        return f"data: {json.dumps(data)}\n\n"
    
    def format_token(self, token: str) -> str:
        """Format token for streaming."""
        return self.format_sse({"token": token})
    
    def format_done(self) -> str:
        """Format stream completion event."""
        return self.format_sse({"done": True})
    
    def format_error(self, error: str) -> str:
        """Format error event."""
        return self.format_sse({"error": error})
    
    async def stream_from_llm(self, 
                              llm_callable,
                              session_id: str,
                              **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream response from LLM.
        
        Args:
            llm_callable: Async function that calls LLM
            session_id: Session identifier
            **kwargs: Arguments for LLM call
        """
        try:
            async for token in llm_callable(**kwargs):
                if not self.active_streams.get(session_id, False):
                    break
                yield token
        except Exception as e:
            yield self.format_error(str(e))
        finally:
            yield self.format_done()
    
    def clear_all_streams(self):
        """Clear all active streams."""
        for session_id in self.active_streams:
            self.active_streams[session_id] = False
        self.active_streams.clear()
        self.is_streaming = False