from typing import Any, Dict, List, Optional
import uuid
import json
import os
from datetime import datetime


class SessionService:
    """Session manager for Phase 3 chat system."""
    
    def __init__(self, storage_dir: str = "cache/sessions"):
        self.storage_dir = storage_dir
        self.sessions = {}
        self._initialize()
    
    def _initialize(self):
        """Initialize storage."""
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _get_session_path(self, session_id: str) -> str:
        """Get session file path."""
        return os.path.join(self.storage_dir, f"{session_id}.json")
    
    def create_session(self, 
                       repository_id: str = "default",
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new session.
        
        Returns:
        - session_id: Unique session identifier
        - session: Session data
        """
        session_id = str(uuid.uuid4())
        
        session = {
            "session_id": session_id,
            "repository_id": repository_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "message_count": 0,
            "status": "active"
        }
        
        self.sessions[session_id] = session
        self._save_session(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        # Check memory first
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Check disk
        session_path = self._get_session_path(session_id)
        if os.path.exists(session_path):
            try:
                with open(session_path, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                self.sessions[session_id] = session
                return session
            except Exception:
                return None
        
        return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.update(updates)
        session["updated_at"] = datetime.now().isoformat()
        
        self.sessions[session_id] = session
        self._save_session(session)
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            # Remove from memory
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            # Remove from disk
            session_path = self._get_session_path(session_id)
            if os.path.exists(session_path):
                os.remove(session_path)
            
            return True
        except Exception:
            return False
    
    def restore_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Restore a session from disk."""
        return self.get_session(session_id)
    
    def list_sessions(self, repository_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all sessions.
        
        Args:
            repository_id: Filter by repository ID
        """
        sessions = []
        
        # Check memory
        for session in self.sessions.values():
            if repository_id is None or session.get("repository_id") == repository_id:
                sessions.append(session)
        
        # Check disk
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    session_path = os.path.join(self.storage_dir, filename)
                    try:
                        with open(session_path, 'r', encoding='utf-8') as f:
                            session = json.load(f)
                        if repository_id is None or session.get("repository_id") == repository_id:
                            if session.get("session_id") not in self.sessions:
                                sessions.append(session)
                    except Exception:
                        continue
        except Exception:
            pass
        
        # Sort by updated_at
        sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        
        return sessions
    
    def get_sessions_by_repository(self, repository_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a repository."""
        return self.list_sessions(repository_id=repository_id)
    
    def increment_message_count(self, session_id: str) -> bool:
        """Increment message count for a session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session["message_count"] = session.get("message_count", 0) + 1
        session["updated_at"] = datetime.now().isoformat()
        
        self.sessions[session_id] = session
        self._save_session(session)
        
        return True
    
    def _save_session(self, session: Dict[str, Any]):
        """Save session to disk."""
        try:
            session_id = session.get("session_id")
            if not session_id:
                return
            
            session_path = self._get_session_path(session_id)
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def clear_all_sessions(self) -> bool:
        """Clear all sessions."""
        try:
            # Clear memory
            self.sessions.clear()
            
            # Clear disk
            for filename in os.listdir(self.storage_dir):
                file_path = os.path.join(self.storage_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            return True
        except Exception:
            return False
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        total_sessions = len(self.sessions)
        repositories = {}
        
        for session in self.sessions.values():
            repo_id = session.get("repository_id", "unknown")
            repositories[repo_id] = repositories.get(repo_id, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "repositories": repositories,
            "active_sessions": sum(1 for s in self.sessions.values() if s.get("status") == "active")
        }