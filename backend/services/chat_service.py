from typing import Any, Dict, List, Optional, AsyncGenerator
import json
import os
from datetime import datetime

from services.memory_service import MemoryService
from services.prompt_service import PromptService
from services.context_service import ContextService
from services.source_service import SourceService
from services.query_service import QueryService
from services.streaming_service import StreamingService
from services.session_service import SessionService
from services.retrieval_service import RetrievalService
from services.embedding_service import EmbeddingService
from config import get_settings


class ChatService:
    """Chat engine for Phase 3."""
    
    def __init__(self):
        self.memory_service = MemoryService()
        self.prompt_service = PromptService()
        self.context_service = None
        self.source_service = SourceService()
        self.query_service = QueryService()
        self.streaming_service = StreamingService()
        self.session_service = SessionService()
        self.retrieval_service = None
        self.embedding_service = None
        self.vector_service = None
        
        # Load configuration from central config
        settings = get_settings()
        llm_config = settings.get_llm_config()
        
        self.llm_provider = llm_config["provider"]
        self.openrouter_api_key = llm_config.get("api_key") if llm_config["provider"] == "openrouter" else None
        self.openai_api_key = llm_config.get("api_key") if llm_config["provider"] == "openai" else None
        self.llm_model = llm_config["model"]
        self.llm_max_tokens = llm_config["max_tokens"]
        self.llm_temperature = llm_config["temperature"]
        self.llm_timeout = llm_config["timeout"]
    
    def _initialize_services(self, repository_id: str):
        """Initialize services for a repository."""
        if not self.embedding_service:
            self.embedding_service = EmbeddingService()
        
        if not self.vector_service:
            from services.vector_service import VectorService
            self.vector_service = VectorService()
        
        if not self.retrieval_service:
            self.retrieval_service = RetrievalService(self.vector_service, self.embedding_service)
        
        self.context_service = ContextService(self.retrieval_service)
    
    def create_session(self, repository_id: str = "default") -> Dict[str, Any]:
        """Create a new chat session."""
        return self.session_service.create_session(repository_id=repository_id)
    
    def send_message(self, 
                     session_id: str, 
                     question: str,
                     repository_id: str = "default") -> Dict[str, Any]:
        """
        Send a message and get a response.
        
        Returns:
        - answer: Generated answer
        - sources: Source references
        - session_id: Session identifier
        """
        try:
            # Initialize services
            self._initialize_services(repository_id)
            
            # Get session
            session = self.session_service.get_session(session_id)
            if not session:
                session = self.create_session(repository_id)
                session_id = session["session_id"]
            
            # Load chat history
            chat_history = self.memory_service.load_history(session_id) or []
            
            # Validate and optimize query
            query_result = self.query_service.validate_query(question)
            if not query_result["valid"]:
                return {
                    "answer": "Invalid question. Please ask a valid question.",
                    "sources": [],
                    "session_id": session_id
                }
            
            optimized_question = query_result["optimized"]
            
            # Rewrite ambiguous questions
            final_question = self.query_service.rewrite_ambiguous_question(
                optimized_question, 
                chat_history
            )
            
            # Build context
            context_result = self.context_service.build_context(
                question=final_question,
                repository_id=repository_id,
                chat_history=chat_history
            )
            
            context = context_result.get("context", "")
            sources = context_result.get("sources", [])
            chunks = context_result.get("chunks", [])
            has_relevant_info = context_result.get("has_relevant_info", False)
            
            # Build prompt
            repository_info = {
                "name": repository_id,
                "description": "Repository analysis"
            }
            
            prompt = self.prompt_service.build_prompt(
                question=final_question,
                context=context,
                chat_history=chat_history,
                repository_info=repository_info
            )
            
            # Generate response
            if has_relevant_info:
                answer = self._call_llm(prompt)
            else:
                answer = "I could not find enough information inside the repository."
            
            # Save messages to memory
            self.memory_service.save_message(session_id, "user", question)
            self.memory_service.save_message(session_id, "assistant", answer, {
                "sources": sources,
                "chunks": chunks
            })
            
            # Update session
            self.session_service.increment_message_count(session_id)
            
            # Format sources
            formatted_sources = self.source_service.format_sources_list(chunks)
            
            return {
                "answer": answer,
                "sources": formatted_sources,
                "session_id": session_id,
                "question": question,
                "optimized_question": final_question if final_question != question else None
            }
            
        except Exception as e:
            return {
                "answer": f"Error processing message: {str(e)}",
                "sources": [],
                "session_id": session_id,
                "error": str(e)
            }
    
    async def stream_message(self, 
                            session_id: str, 
                            question: str,
                            repository_id: str = "default") -> AsyncGenerator[str, None]:
        """Stream a message response."""
        try:
            # Initialize services
            self._initialize_services(repository_id)
            
            # Get session
            session = self.session_service.get_session(session_id)
            if not session:
                session = self.create_session(repository_id)
                session_id = session["session_id"]
            
            # Load chat history
            chat_history = self.memory_service.load_history(session_id) or []
            
            # Validate and optimize query
            query_result = self.query_service.validate_query(question)
            if not query_result["valid"]:
                yield self.streaming_service.format_sse({
                    "token": "Invalid question. Please ask a valid question.",
                    "done": True
                })
                return
            
            optimized_question = query_result["optimized"]
            final_question = self.query_service.rewrite_ambiguous_question(
                optimized_question, 
                chat_history
            )
            
            # Build context
            context_result = self.context_service.build_context(
                question=final_question,
                repository_id=repository_id,
                chat_history=chat_history
            )
            
            context = context_result.get("context", "")
            sources = context_result.get("sources", [])
            chunks = context_result.get("chunks", [])
            has_relevant_info = context_result.get("has_relevant_info", False)
            
            # Build prompt
            repository_info = {
                "name": repository_id,
                "description": "Repository analysis"
            }
            
            prompt = self.prompt_service.build_prompt(
                question=final_question,
                context=context,
                chat_history=chat_history,
                repository_info=repository_info
            )
            
            # Generate response
            if has_relevant_info:
                response_text = self._call_llm(prompt)
            else:
                response_text = "I could not find enough information inside the repository."
            
            # Stream response token by token
            tokens = response_text.split()
            for token in tokens:
                yield self.streaming_service.format_sse({"token": token + " "})
            
            # Save messages
            self.memory_service.save_message(session_id, "user", question)
            self.memory_service.save_message(session_id, "assistant", response_text, {
                "sources": sources,
                "chunks": chunks
            })
            
            # Update session
            self.session_service.increment_message_count(session_id)
            
            # Send final event with sources
            formatted_sources = self.source_service.format_sources_list(chunks)
            yield self.streaming_service.format_sse({
                "done": True,
                "sources": formatted_sources,
                "session_id": session_id
            })
            
        except Exception as e:
            yield self.streaming_service.format_error(str(e))
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session."""
        return self.memory_service.delete_history(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session completely."""
        return self.session_service.delete_session(session_id)
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.memory_service.load_history(session_id) or []
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM to generate response.
        
        This is a simplified implementation. In production, you would:
        1. Use OpenRouter API
        2. Use OpenAI API
        3. Use local LLM (Ollama, etc.)
        """
        # Try OpenRouter first
        if self.openrouter_api_key:
            return self._call_openrouter(prompt)
        # Try OpenAI
        elif self.openai_api_key:
            return self._call_openai(prompt)
        # Fallback
        else:
            return self._fallback_response(prompt)
    
    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API."""
        try:
            import requests
            settings = get_settings()
            
            response = requests.post(
                settings.OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.llm_model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": self.llm_max_tokens,
                    "temperature": self.llm_temperature
                },
                timeout=self.llm_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"LLM API error: {response.status_code}"
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        try:
            import requests
            settings = get_settings()
            
            response = requests.post(
                settings.OPENAI_API_URL,
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": self.llm_max_tokens,
                    "temperature": self.llm_temperature
                },
                timeout=self.llm_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"LLM API error: {response.status_code}"
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    def _fallback_response(self, prompt: str) -> str:
        """Generate fallback response when no LLM is available."""
        return """
I need an LLM API key to generate intelligent responses. 

To enable AI chat:
1. Add OPENROUTER_API_KEY or OPENAI_API_KEY to your .env file
2. Restart the backend server

For now, I can help you with:
- Repository analysis
- Code search
- File structure exploration

Please configure an API key to enable the full chat experience.
"""
    
    def is_available(self) -> bool:
        """Check if chat service is available."""
        settings = get_settings()
        return bool(settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY)
