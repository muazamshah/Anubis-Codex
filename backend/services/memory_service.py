from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import os


class MemoryService:
    """Memory engine for Phase 3 chat system."""
    
    def __init__(self, storage_dir: str = "cache/sessions"):
        self.storage_dir = storage_dir
        self._initialize()
    
    def _initialize(self):
        """Initialize storage directories."""
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _get_session_path(self, session_id: str) -> str:
        """Get session file path."""
        return os.path.join(self.storage_dir, f"{session_id}.json")
    
    def save_message(self, session_id: str, role: str, content: str, 
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save a message to session history."""
        try:
            session_path = self._get_session_path(session_id)
            
            # Load existing history
            history = self.load_history(session_id) or []
            
            # Add new message
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            history.append(message)
            
            # Save back
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": session_id,
                    "messages": history,
                    "updated_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def load_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load conversation history for a session."""
        try:
            session_path = self._get_session_path(session_id)
            if not os.path.exists(session_path):
                return None
            
            with open(session_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("messages", [])
        except Exception:
            return None
    
    def summarize_history(self, session_id: str, max_messages: int = 10) -> str:
        """Summarize conversation history."""
        history = self.load_history(session_id)
        if not history:
            return "No conversation history."
        
        # Get last N messages
        recent = history[-max_messages:]
        
        summary_parts = []
        for msg in recent:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            summary_parts.append(f"{role}: {content[:100]}")
        
        return "\n".join(summary_parts)
    
    def delete_history(self, session_id: str) -> bool:
        """Delete session history."""
        try:
            session_path = self._get_session_path(session_id)
            if os.path.exists(session_path):
                os.remove(session_path)
            return True
        except Exception:
            return False
    
    def clear_memory(self) -> bool:
        """Clear all session memories."""
        try:
            for filename in os.listdir(self.storage_dir):
                file_path = os.path.join(self.storage_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            return True
        except Exception:
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        try:
            session_path = self._get_session_path(session_id)
            if not os.path.exists(session_path):
                return None
            
            with open(session_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            messages = data.get("messages", [])
            return {
                "session_id": session_id,
                "message_count": len(messages),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "last_message": messages[-1] if messages else None
            }
        except Exception:
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions."""
        sessions = []
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    session_id = filename[:-5]
                    info = self.get_session_info(session_id)
                    if info:
                        sessions.append(info)
        except Exception:
            pass
        return sessions