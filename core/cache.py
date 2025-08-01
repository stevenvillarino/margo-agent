"""
Distributed Caching System

Implements multi-level caching with Redis backend and local LRU cache
for improved performance and reduced API calls.
"""

import asyncio
import json
import time
import hashlib
import pickle
import logging
from typing import Dict, Any, Optional, Union, TypeVar, Generic, Callable
from dataclasses import dataclass, asdict
from functools import lru_cache, wraps
from collections import OrderedDict
import threading
from datetime import datetime, timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

T = TypeVar('T')


@dataclass
class CacheConfig:
    """Cache configuration."""
    redis_url: Optional[str] = None
    local_cache_size: int = 128
    default_ttl: int = 3600  # 1 hour
    prefix: str = "vp_design_cache"
    enable_local_cache: bool = True
    enable_redis_cache: bool = True
    serialization_method: str = "json"  # "json" or "pickle"


@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class LRUCache:
    """Thread-safe LRU cache implementation."""
    
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                return value
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache.pop(key)
            elif len(self.cache) >= self.maxsize:
                # Remove least recently used
                self.cache.popitem(last=False)
            
            self.cache[key] = value
    
    def delete(self, key: str) -> bool:
        """Delete item from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from cache."""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            return len(self.cache)
    
    def keys(self) -> list:
        """Get all cache keys."""
        with self.lock:
            return list(self.cache.keys())


class CacheKey:
    """Utility for generating cache keys."""
    
    @staticmethod
    def generate(prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        # Create a unique key from arguments
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # Hash complex objects
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        # Add keyword arguments (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}:{v}")
            else:
                key_parts.append(f"{k}:{hashlib.md5(str(v).encode()).hexdigest()[:8]}")
        
        return ":".join(key_parts)
    
    @staticmethod
    def hash_content(content: Union[str, bytes, dict]) -> str:
        """Generate hash for content-based caching."""
        if isinstance(content, dict):
            content = json.dumps(content, sort_keys=True)
        elif isinstance(content, str):
            content = content.encode()
        
        return hashlib.sha256(content).hexdigest()[:16]


class DistributedCache:
    """Multi-level distributed cache with Redis and local LRU."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.stats = CacheStats()
        self.logger = logging.getLogger(__name__)
        
        # Initialize local cache
        if config.enable_local_cache:
            self.local_cache = LRUCache(config.local_cache_size)
        else:
            self.local_cache = None
        
        # Initialize Redis cache
        self.redis_client = None
        if config.enable_redis_cache and config.redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(config.redis_url, decode_responses=False)
                self.logger.info("Redis cache initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Redis: {e}")
                self.redis_client = None
        
        # Serialization methods
        self.serializers = {
            "json": (self._json_serialize, self._json_deserialize),
            "pickle": (self._pickle_serialize, self._pickle_deserialize)
        }
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache (checks local first, then Redis)."""
        full_key = f"{self.config.prefix}:{key}"
        
        # L1 Cache: Local LRU
        if self.local_cache:
            value = self.local_cache.get(full_key)
            if value is not None:
                self.stats.hits += 1
                return value
        
        # L2 Cache: Redis
        if self.redis_client:
            try:
                value = await self._get_from_redis(full_key)
                if value is not None:
                    # Store in local cache for faster access
                    if self.local_cache:
                        self.local_cache.set(full_key, value)
                    self.stats.hits += 1
                    return value
            except Exception as e:
                self.logger.error(f"Redis get error for key {key}: {e}")
                self.stats.errors += 1
        
        self.stats.misses += 1
        return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        full_key = f"{self.config.prefix}:{key}"
        ttl = ttl or self.config.default_ttl
        
        try:
            # Store in local cache
            if self.local_cache:
                self.local_cache.set(full_key, value)
            
            # Store in Redis
            if self.redis_client:
                await self._set_in_redis(full_key, value, ttl)
            
            self.stats.sets += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set error for key {key}: {e}")
            self.stats.errors += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        full_key = f"{self.config.prefix}:{key}"
        
        deleted = False
        
        # Delete from local cache
        if self.local_cache:
            deleted = self.local_cache.delete(full_key) or deleted
        
        # Delete from Redis
        if self.redis_client:
            try:
                result = await self.redis_client.delete(full_key)
                deleted = (result > 0) or deleted
            except Exception as e:
                self.logger.error(f"Redis delete error for key {key}: {e}")
                self.stats.errors += 1
        
        if deleted:
            self.stats.deletes += 1
        
        return deleted
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries."""
        cleared = 0
        
        if pattern:
            pattern = f"{self.config.prefix}:{pattern}"
        else:
            pattern = f"{self.config.prefix}:*"
        
        # Clear local cache
        if self.local_cache:
            if pattern == f"{self.config.prefix}:*":
                self.local_cache.clear()
                cleared += 1
            else:
                # Pattern-based clearing for local cache
                keys_to_delete = [k for k in self.local_cache.keys() if self._match_pattern(k, pattern)]
                for key in keys_to_delete:
                    self.local_cache.delete(key)
                cleared += len(keys_to_delete)
        
        # Clear Redis
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    deleted = await self.redis_client.delete(*keys)
                    cleared += deleted
            except Exception as e:
                self.logger.error(f"Redis clear error: {e}")
                self.stats.errors += 1
        
        return cleared
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        full_key = f"{self.config.prefix}:{key}"
        
        # Check local cache first
        if self.local_cache and self.local_cache.get(full_key) is not None:
            return True
        
        # Check Redis
        if self.redis_client:
            try:
                return await self.redis_client.exists(full_key) > 0
            except Exception as e:
                self.logger.error(f"Redis exists error for key {key}: {e}")
                self.stats.errors += 1
        
        return False
    
    async def get_or_set(self, key: str, factory: Callable, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function."""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Generate value using factory
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        # Store in cache
        await self.set(key, value, ttl)
        return value
    
    async def _get_from_redis(self, key: str) -> Any:
        """Get value from Redis."""
        raw_value = await self.redis_client.get(key)
        if raw_value is None:
            return None
        
        serialize, deserialize = self.serializers[self.config.serialization_method]
        return deserialize(raw_value)
    
    async def _set_in_redis(self, key: str, value: Any, ttl: int) -> None:
        """Set value in Redis."""
        serialize, deserialize = self.serializers[self.config.serialization_method]
        raw_value = serialize(value)
        await self.redis_client.setex(key, ttl, raw_value)
    
    def _json_serialize(self, value: Any) -> bytes:
        """Serialize value using JSON."""
        return json.dumps(value, default=str).encode()
    
    def _json_deserialize(self, value: bytes) -> Any:
        """Deserialize value using JSON."""
        return json.loads(value.decode())
    
    def _pickle_serialize(self, value: Any) -> bytes:
        """Serialize value using pickle."""
        return pickle.dumps(value)
    
    def _pickle_deserialize(self, value: bytes) -> Any:
        """Deserialize value using pickle."""
        return pickle.loads(value)
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for cache keys."""
        if pattern.endswith('*'):
            return key.startswith(pattern[:-1])
        return key == pattern
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats_dict = asdict(self.stats)
        
        local_stats = {}
        if self.local_cache:
            local_stats = {
                "size": self.local_cache.size(),
                "max_size": self.local_cache.maxsize
            }
        
        return {
            "stats": stats_dict,
            "local_cache": local_stats,
            "redis_enabled": self.redis_client is not None,
            "config": asdict(self.config)
        }


# Decorator for caching function results
def cached(ttl: int = 3600, key_prefix: str = "func", cache_instance: Optional[DistributedCache] = None):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Use global cache if none provided
            cache = cache_instance or global_cache
            if not cache:
                # No cache available, call function directly
                return await func(*args, **kwargs)
            
            # Generate cache key
            key = CacheKey.generate(f"{key_prefix}:{func.__name__}", *args, **kwargs)
            
            # Try to get from cache
            result = await cache.get(key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we'll use asyncio to handle cache operations
            cache = cache_instance or global_cache
            if not cache:
                return func(*args, **kwargs)
            
            key = CacheKey.generate(f"{key_prefix}:{func.__name__}", *args, **kwargs)
            
            # Try to get from cache (sync)
            try:
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(cache.get(key))
                if result is not None:
                    return result
            except:
                pass
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result (async)
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(cache.set(key, result, ttl))
            except:
                pass
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global cache instance (will be initialized by system)
global_cache: Optional[DistributedCache] = None


def initialize_cache(config: CacheConfig) -> DistributedCache:
    """Initialize global cache instance."""
    global global_cache
    global_cache = DistributedCache(config)
    return global_cache


def get_cache() -> Optional[DistributedCache]:
    """Get global cache instance."""
    return global_cache
