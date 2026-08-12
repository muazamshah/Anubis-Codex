"""
ANUBIS CODEX - Centralized Configuration Module

This module provides a single source of truth for all API keys and configuration.
All environment variables are loaded here and exposed through a clean interface.
"""

import os
import tempfile
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Centralized application settings."""
    
    def __init__(self):
        # ==================== LLM CONFIGURATION ====================
        self.LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter")
        self.OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        self.OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo")
        
        # ==================== GITHUB CONFIGURATION ====================
        self.GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
        
        # ==================== EMBEDDING CONFIGURATION ====================
        self.EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
        
        # ==================== VECTOR DATABASE CONFIGURATION ====================
        self.VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "cache/vector_db")
        
        # ==================== CACHE CONFIGURATION ====================
        self.CACHE_DIR: str = os.getenv("CACHE_DIR", os.path.join(tempfile.gettempdir(), "anubis-codex-cache"))
        
        # ==================== API ENDPOINTS ====================
        self.OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
        self.OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
        self.GITHUB_API_URL: str = "https://api.github.com"
        
        # ==================== LLM DEFAULTS ====================
        self.LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))
        self.LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "30"))
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration based on available API keys."""
        config = {
            "provider": self.LLM_PROVIDER,
            "model": self.LLM_MODEL,
            "max_tokens": self.LLM_MAX_TOKENS,
            "temperature": self.LLM_TEMPERATURE,
            "timeout": self.LLM_TIMEOUT,
        }
        
        if self.OPENROUTER_API_KEY:
            config["api_key"] = self.OPENROUTER_API_KEY
            config["api_url"] = self.OPENROUTER_API_URL
            config["provider"] = "openrouter"
        elif self.OPENAI_API_KEY:
            config["api_key"] = self.OPENAI_API_KEY
            config["api_url"] = self.OPENAI_API_URL
            config["provider"] = "openai"
        else:
            config["api_key"] = None
            config["api_url"] = None
            config["provider"] = None
        
        return config
    
    def get_github_config(self) -> dict:
        """Get GitHub configuration."""
        return {
            "token": self.GITHUB_TOKEN,
            "api_url": self.GITHUB_API_URL,
            "has_token": bool(self.GITHUB_TOKEN)
        }
    
    def get_embedding_config(self) -> dict:
        """Get embedding configuration."""
        return {
            "model_name": self.EMBEDDING_MODEL_NAME,
            "provider": "local"  # sentence-transformers is local
        }
    
    def get_vector_db_config(self) -> dict:
        """Get vector database configuration."""
        return {
            "path": self.VECTOR_DB_PATH,
            "provider": "chromadb"  # Local ChromaDB
        }
    
    def validate(self) -> dict:
        """
        Validate configuration and return status.
        
        Returns:
            dict with validation status for each component
        """
        status = {
            "llm": {
                "status": "configured" if (self.OPENROUTER_API_KEY or self.OPENAI_API_KEY) else "missing",
                "provider": self.LLM_PROVIDER,
                "has_openrouter": bool(self.OPENROUTER_API_KEY),
                "has_openai": bool(self.OPENAI_API_KEY),
            },
            "github": {
                "status": "configured" if self.GITHUB_TOKEN else "optional",
                "has_token": bool(self.GITHUB_TOKEN),
            },
            "embedding": {
                "status": "local",
                "model": self.EMBEDDING_MODEL_NAME,
                "api_key_required": False
            },
            "vector_db": {
                "status": "local",
                "provider": "chromadb",
                "path": self.VECTOR_DB_PATH,
                "api_key_required": False
            }
        }
        
        return status
    
    def get_required_apis(self) -> list:
        """Get list of required APIs."""
        apis = []
        
        if self.OPENROUTER_API_KEY or self.OPENAI_API_KEY:
            apis.append({
                "name": "LLM API",
                "status": "REQUIRED",
                "purpose": "Generate AI responses for chat",
                "configuration": ".env",
                "variables": ["OPENROUTER_API_KEY or OPENAI_API_KEY"]
            })
        
        return apis
    
    def get_optional_apis(self) -> list:
        """Get list of optional APIs."""
        apis = []
        
        if self.GITHUB_TOKEN:
            apis.append({
                "name": "GitHub API",
                "status": "OPTIONAL",
                "purpose": "Higher rate limits for repository analysis",
                "configuration": ".env",
                "variables": ["GITHUB_TOKEN"]
            })
        
        return apis
    
    def get_local_services(self) -> list:
        """Get list of local services (no API key required)."""
        return [
            {
                "name": "Embeddings",
                "status": "LOCAL",
                "api_key_required": False,
                "model": self.EMBEDDING_MODEL_NAME,
                "provider": "sentence-transformers"
            },
            {
                "name": "Vector Database",
                "status": "LOCAL",
                "api_key_required": False,
                "provider": "ChromaDB",
                "path": self.VECTOR_DB_PATH
            }
        ]


# Global settings instance
_settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return _settings


# Convenience functions for common access patterns
def get_llm_config() -> dict:
    """Get LLM configuration."""
    return _settings.get_llm_config()


def get_github_config() -> dict:
    """Get GitHub configuration."""
    return _settings.get_github_config()


def get_embedding_config() -> dict:
    """Get embedding configuration."""
    return _settings.get_embedding_config()


def get_vector_db_config() -> dict:
    """Get vector database configuration."""
    return _settings.get_vector_db_config()


def validate_config() -> dict:
    """Validate configuration and return status."""
    return _settings.validate()
