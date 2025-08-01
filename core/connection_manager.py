"""
Connection Management and Pooling

Implements connection pooling for external APIs to prevent resource leaks
and improve performance.
"""

import asyncio
import aiohttp
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
from contextlib import asynccontextmanager
import logging

@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pools."""
    max_connections: int = 10
    max_idle_time: int = 300  # 5 minutes
    timeout: int = 30
    retry_attempts: int = 3


@dataclass
class ConnectionConfig:
    """Configuration for connection management."""
    default_pool_config: ConnectionPoolConfig = None
    service_specific_configs: Dict[str, ConnectionPoolConfig] = None
    
    def __post_init__(self):
        if self.default_pool_config is None:
            self.default_pool_config = ConnectionPoolConfig()
        if self.service_specific_configs is None:
            self.service_specific_configs = {}


class ConnectionPool:
    """Generic connection pool for HTTP clients."""
    
    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self.pool = []
        self.in_use = set()
        self.created_at = {}
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
    
    async def acquire(self) -> aiohttp.ClientSession:
        """Acquire a connection from the pool."""
        async with self.lock:
            # Clean up expired connections
            await self._cleanup_expired()
            
            # Try to get from pool
            if self.pool:
                session = self.pool.pop()
                self.in_use.add(session)
                return session
            
            # Create new if under limit
            if len(self.in_use) < self.config.max_connections:
                session = await self._create_session()
                self.in_use.add(session)
                self.created_at[session] = time.time()
                return session
            
            # Wait for a connection to be released
            while len(self.in_use) >= self.config.max_connections:
                await asyncio.sleep(0.1)
            
            # Try again
            return await self.acquire()
    
    async def release(self, session: aiohttp.ClientSession):
        """Release a connection back to the pool."""
        async with self.lock:
            if session in self.in_use:
                self.in_use.remove(session)
                if not session.closed:
                    self.pool.append(session)
    
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create a new HTTP session."""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        connector = aiohttp.TCPConnector(limit=self.config.max_connections)
        return aiohttp.ClientSession(timeout=timeout, connector=connector)
    
    async def _cleanup_expired(self):
        """Clean up expired connections."""
        current_time = time.time()
        expired = []
        
        for session in list(self.pool):
            if (current_time - self.created_at.get(session, 0)) > self.config.max_idle_time:
                expired.append(session)
        
        for session in expired:
            self.pool.remove(session)
            if session in self.created_at:
                del self.created_at[session]
            if not session.closed:
                await session.close()
    
    async def close_all(self):
        """Close all connections."""
        all_sessions = list(self.pool) + list(self.in_use)
        for session in all_sessions:
            if not session.closed:
                await session.close()
        
        self.pool.clear()
        self.in_use.clear()
        self.created_at.clear()


class ConnectionManager:
    """Manages connection pools for different services."""
    
    def __init__(self):
        self.pools: Dict[str, ConnectionPool] = {}
        self.configs = {
            'openai': ConnectionPoolConfig(max_connections=5, timeout=60),
            'exa': ConnectionPoolConfig(max_connections=3, timeout=30),
            'slack': ConnectionPoolConfig(max_connections=2, timeout=15),
            'jira': ConnectionPoolConfig(max_connections=2, timeout=30),
            'figma': ConnectionPoolConfig(max_connections=2, timeout=30),
        }
        
        # Initialize pools
        for service, config in self.configs.items():
            self.pools[service] = ConnectionPool(config)
    
    @asynccontextmanager
    async def get_connection(self, service: str):
        """Get a connection for a specific service."""
        if service not in self.pools:
            raise ValueError(f"Unknown service: {service}")
        
        pool = self.pools[service]
        session = await pool.acquire()
        
        try:
            yield session
        finally:
            await pool.release(session)
    
    async def close_all(self):
        """Close all connection pools."""
        for pool in self.pools.values():
            await pool.close_all()


# Global connection manager instance
_global_connection_manager = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    global _global_connection_manager
    if _global_connection_manager is None:
        _global_connection_manager = ConnectionManager()
    return _global_connection_manager


def initialize_connection_manager(config: ConnectionConfig = None) -> ConnectionManager:
    """Initialize the global connection manager with custom config."""
    global _global_connection_manager
    _global_connection_manager = ConnectionManager(config)
    return _global_connection_manager


# Context manager for easy usage
@asynccontextmanager
async def get_http_session(service: str = 'default'):
    """Get an HTTP session for external API calls."""
    connection_manager = get_connection_manager()
    async with connection_manager.get_connection(service) as session:
        yield session
