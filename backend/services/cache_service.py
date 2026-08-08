import os
import json
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


class CacheService:
    """Cache layer for Phase 2 RAG system."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.subdirs = {
            "repositories": os.path.join(cache_dir, "repositories"),
            "embeddings": os.path.join(cache_dir, "embeddings"),
            "search": os.path.join(cache_dir, "search"),
            "metadata": os.path.join(cache_dir, "metadata"),
        }
        self._initialize()
    
    def _initialize(self):
        """Initialize cache directories."""
        for subdir in self.subdirs.values():
            os.makedirs(subdir, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache file name from key."""
        return hashlib.md5(key.encode()).hexdigest() + ".json"
    
    def _get_cache_path(self, category: str, key: str) -> str:
        """Get full cache file path."""
        if category not in self.subdirs:
            raise ValueError(f"Invalid cache category: {category}")
        return os.path.join(self.subdirs[category], self._get_cache_key(key))
    
    def get(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        """Get item from cache."""
        try:
            cache_path = self._get_cache_path(category, key)
            if not os.path.exists(cache_path):
                return None
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if expired
            if data.get("expires_at"):
                expires_at = datetime.fromisoformat(data["expires_at"])
                if datetime.now() > expires_at:
                    self.delete(category, key)
                    return None
            
            return data.get("value")
        except Exception:
            return None
    
    def set(self, category: str, key: str, value: Any, ttl_hours: int = 24) -> bool:
        """Set item in cache with TTL."""
        try:
            cache_path = self._get_cache_path(category, key)
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
            
            data = {
                "key": key,
                "created_at": datetime.now().isoformat(),
                "expires_at": expires_at.isoformat(),
                "value": value
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def delete(self, category: str, key: str) -> bool:
        """Delete item from cache."""
        try:
            cache_path = self._get_cache_path(category, key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return True
        except Exception:
            return False
    
    def clear_category(self, category: str) -> bool:
        """Clear all items in a category."""
        try:
            if category not in self.subdirs:
                return False
            
            subdir = self.subdirs[category]
            for filename in os.listdir(subdir):
                file_path = os.path.join(subdir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            return True
        except Exception:
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache."""
        try:
            for subdir in self.subdirs.values():
                for filename in os.listdir(subdir):
                    file_path = os.path.join(subdir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {}
        for category, subdir in self.subdirs.items():
            try:
                count = len([f for f in os.listdir(subdir) if os.path.isfile(os.path.join(subdir, f))])
                stats[category] = count
            except Exception:
                stats[category] = 0
        
        return {
            "categories": stats,
            "total": sum(stats.values()),
            "cache_dir": self.cache_dir
        }
    
    # Specialized methods for Phase 2
    
    def cache_repository(self, repo_url: str, repo_data: Dict[str, Any], ttl_hours: int = 168) -> bool:
        """Cache repository analysis results (default 7 days)."""
        return self.set("repositories", repo_url, repo_data, ttl_hours=ttl_hours)
    
    def get_repository(self, repo_url: str) -> Optional[Dict[str, Any]]:
        """Get cached repository analysis."""
        return self.get("repositories", repo_url)
    
    def cache_embeddings(self, chunk_id: str, embedding: List[float], ttl_hours: int = 168) -> bool:
        """Cache embeddings (default 7 days)."""
        return self.set("embeddings", chunk_id, embedding, ttl_hours=ttl_hours)
    
    def get_embeddings(self, chunk_id: str) -> Optional[List[float]]:
        """Get cached embeddings."""
        return self.get("embeddings", chunk_id)
    
    def cache_search_results(self, query_hash: str, results: List[Dict[str, Any]], ttl_hours: int = 1) -> bool:
        """Cache search results (default 1 hour)."""
        return self.set("search", query_hash, results, ttl_hours=ttl_hours)
    
    def get_search_results(self, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results."""
        return self.get("search", query_hash)
    
    def cache_metadata(self, repo_id: str, metadata: Dict[str, Any], ttl_hours: int = 168) -> bool:
        """Cache repository metadata (default 7 days)."""
        return self.set("metadata", repo_id, metadata, ttl_hours=ttl_hours)
    
    def get_metadata(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get cached metadata."""
        return self.get("metadata", repo_id)
    
    def generate_query_hash(self, query: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """Generate hash for query caching."""
        filter_str = json.dumps(filters, sort_keys=True) if filters else ""
        combined = f"{query}:{filter_str}"
        return hashlib.md5(combined.encode()).hexdigest()