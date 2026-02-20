"""
Simple in-memory caching for expensive operations
Reduces redundant LLM calls and improves response times
"""

import time
import hashlib
from typing import Any, Optional, Dict, Callable
from functools import wraps


class SimpleCache:
    """Thread-safe simple cache with TTL support"""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._ttl = ttl
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired"""
        return time.time() - timestamp > self._ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if not self._is_expired(timestamp):
                return value
            # Remove expired entry
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        self._cache[key] = (value, time.time())
    
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if self._is_expired(timestamp)
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = len(self._cache)
        expired = sum(1 for _, (_, ts) in self._cache.items() if self._is_expired(ts))
        return {
            "total_entries": total,
            "active_entries": total - expired,
            "expired_entries": expired
        }


# Global caches
bias_detection_cache = SimpleCache(ttl=7200)  # 2 hours for bias detection
skill_matching_cache = SimpleCache(ttl=1800)  # 30 min for skill matching
resume_parsing_cache = SimpleCache(ttl=3600)  # 1 hour for resume parsing


def cache_result(cache: SimpleCache, key_fn: Optional[Callable] = None):
    """
    Decorator to cache function results
    
    Args:
        cache: Cache instance to use
        key_fn: Optional function to generate cache key from args
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_fn:
                cache_key = key_fn(*args, **kwargs)
            else:
                # Default: hash the arguments
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Compute and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator


# Convenience functions for caching specific operations
def cache_bias_detection(job_description: str) -> str:
    """Generate cache key for bias detection"""
    return hashlib.md5(job_description.encode()).hexdigest()


def cache_skill_match(resume_text: str, job_description: str) -> str:
    """Generate cache key for skill matching"""
    combined = f"{resume_text[:500]}||{job_description[:500]}"
    return hashlib.md5(combined.encode()).hexdigest()


def get_all_cache_stats() -> Dict[str, Dict]:
    """Get stats for all caches"""
    return {
        "bias_detection": bias_detection_cache.stats(),
        "skill_matching": skill_matching_cache.stats(),
        "resume_parsing": resume_parsing_cache.stats()
    }


# Export all
__all__ = [
    'SimpleCache',
    'cache_result',
    'bias_detection_cache',
    'skill_matching_cache',
    'resume_parsing_cache',
    'cache_bias_detection',
    'cache_skill_match',
    'get_all_cache_stats',
]
