import functools
import time
from typing import Any, Callable, Dict

# Very simple in-memory cache to replace Redis for local/dev use
class SimpleCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Any:
        item = self._cache.get(key)
        if item:
            if time.time() < item['expires_at']:
                return item['value']
            else:
                # Expired
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        expires_at = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
        
    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

# Global cache instance
cache_instance = SimpleCache()

def cached(ttl: int = 300):
    """
    Decorator for caching function results in memory.
    Useful for DB queries or heavy computations.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key based on func name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_val = cache_instance.get(key)
            if cached_val is not None:
                return cached_val
            
            result = await func(*args, **kwargs)
            cache_instance.set(key, result, ttl)
            return result
            
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_val = cache_instance.get(key)
            if cached_val is not None:
                return cached_val
            
            result = func(*args, **kwargs)
            cache_instance.set(key, result, ttl)
            return result
            
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
