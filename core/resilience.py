"""
Circuit Breaker Pattern and Error Handling

Implements circuit breaker pattern for resilient external API calls
and comprehensive error handling strategies.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable, Union, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager
import functools
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type,
    RetryError
)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    timeout_seconds: int = 60
    recovery_timeout: int = 30
    success_threshold: int = 2  # For half-open state


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics."""
    state: CircuitState
    failure_count: int
    success_count: int
    last_failure_time: Optional[float]
    total_requests: int
    successful_requests: int
    failed_requests: int


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker implementation for external service calls."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        self.total_requests += 1
        
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._move_to_half_open()
            else:
                self.logger.warning(f"Circuit breaker {self.name} is OPEN, blocking call")
                raise CircuitBreakerError(f"Circuit breaker {self.name} is open")
        
        try:
            # Execute the function
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Handle success
            self._on_success()
            return result
            
        except Exception as e:
            # Handle failure
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit."""
        if self.last_failure_time is None:
            return True
        
        return (time.time() - self.last_failure_time) >= self.config.timeout_seconds
    
    def _move_to_half_open(self):
        """Move circuit to half-open state."""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.logger.info(f"Circuit breaker {self.name} moved to HALF_OPEN")
    
    def _on_success(self):
        """Handle successful call."""
        self.successful_requests += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._reset()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0  # Reset failure count on success
    
    def _on_failure(self):
        """Handle failed call."""
        self.failed_requests += 1
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._trip()
        elif self.state == CircuitState.HALF_OPEN:
            self._trip()
    
    def _trip(self):
        """Trip the circuit breaker to open state."""
        self.state = CircuitState.OPEN
        self.logger.warning(f"Circuit breaker {self.name} TRIPPED to OPEN state")
    
    def _reset(self):
        """Reset circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.logger.info(f"Circuit breaker {self.name} RESET to CLOSED state")
    
    def get_stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        return CircuitBreakerStats(
            state=self.state,
            failure_count=self.failure_count,
            success_count=self.success_count,
            last_failure_time=self.last_failure_time,
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests
        )
    
    def force_open(self):
        """Force circuit breaker to open state."""
        self.state = CircuitState.OPEN
        self.last_failure_time = time.time()
        self.logger.warning(f"Circuit breaker {self.name} FORCED to OPEN state")
    
    def force_closed(self):
        """Force circuit breaker to closed state."""
        self._reset()
        self.logger.info(f"Circuit breaker {self.name} FORCED to CLOSED state")


class CircuitBreakerManager:
    """Manages multiple circuit breakers."""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.configs: Dict[str, CircuitBreakerConfig] = {
            'openai': CircuitBreakerConfig(failure_threshold=3, timeout_seconds=60),
            'exa': CircuitBreakerConfig(failure_threshold=5, timeout_seconds=30),
            'slack': CircuitBreakerConfig(failure_threshold=3, timeout_seconds=30),
            'jira': CircuitBreakerConfig(failure_threshold=5, timeout_seconds=60),
            'figma': CircuitBreakerConfig(failure_threshold=3, timeout_seconds=30),
        }
    
    def get_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        if service not in self.breakers:
            config = self.configs.get(service, CircuitBreakerConfig())
            self.breakers[service] = CircuitBreaker(service, config)
        return self.breakers[service]
    
    async def call_with_breaker(self, service: str, func: Callable[..., T], *args, **kwargs) -> T:
        """Call function with circuit breaker protection."""
        breaker = self.get_breaker(service)
        return await breaker.call(func, *args, **kwargs)
    
    def get_all_stats(self) -> Dict[str, CircuitBreakerStats]:
        """Get statistics for all circuit breakers."""
        return {name: breaker.get_stats() for name, breaker in self.breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers."""
        for breaker in self.breakers.values():
            breaker.force_closed()


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()


class RetryConfig:
    """Configuration for retry mechanisms."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        min_wait: float = 1.0,
        max_wait: float = 10.0,
        multiplier: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.multiplier = multiplier
        self.exceptions = exceptions


def with_retry(config: RetryConfig = None):
    """Decorator for adding retry logic to functions."""
    if config is None:
        config = RetryConfig()
    
    def decorator(func):
        @retry(
            stop=stop_after_attempt(config.max_attempts),
            wait=wait_exponential(
                multiplier=config.multiplier,
                min=config.min_wait,
                max=config.max_wait
            ),
            retry=retry_if_exception_type(config.exceptions),
            reraise=True
        )
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        @retry(
            stop=stop_after_attempt(config.max_attempts),
            wait=wait_exponential(
                multiplier=config.multiplier,
                min=config.min_wait,
                max=config.max_wait
            ),
            retry=retry_if_exception_type(config.exceptions),
            reraise=True
        )
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class ErrorHandler:
    """Centralized error handling with categorization and logging."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_counts: Dict[str, int] = {}
    
    @asynccontextmanager
    async def handle_errors(self, operation: str, service: str = None):
        """Context manager for comprehensive error handling."""
        start_time = time.time()
        
        try:
            yield
            
        except CircuitBreakerError as e:
            self._log_error("circuit_breaker", operation, e, service)
            raise
            
        except RetryError as e:
            self._log_error("retry_exhausted", operation, e, service)
            raise
            
        except asyncio.TimeoutError as e:
            self._log_error("timeout", operation, e, service)
            raise
            
        except ConnectionError as e:
            self._log_error("connection", operation, e, service)
            raise
            
        except ValueError as e:
            self._log_error("validation", operation, e, service)
            raise
            
        except Exception as e:
            self._log_error("unknown", operation, e, service)
            raise
            
        finally:
            duration = time.time() - start_time
            self.logger.debug(f"Operation {operation} completed in {duration:.2f}s")
    
    def _log_error(self, error_type: str, operation: str, error: Exception, service: str = None):
        """Log error with categorization."""
        error_key = f"{error_type}_{operation}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        log_data = {
            "error_type": error_type,
            "operation": operation,
            "service": service,
            "error_message": str(error),
            "count": self.error_counts[error_key]
        }
        
        if error_type in ["circuit_breaker", "retry_exhausted", "timeout"]:
            self.logger.warning(f"Error in {operation}: {log_data}")
        else:
            self.logger.error(f"Error in {operation}: {log_data}")
    
    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics."""
        return self.error_counts.copy()
    
    def reset_stats(self):
        """Reset error statistics."""
        self.error_counts.clear()


# Global error handler
error_handler = ErrorHandler()


# Convenience decorators and functions
def with_circuit_breaker(service: str):
    """Decorator to add circuit breaker protection."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await circuit_breaker_manager.call_with_breaker(service, func, *args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we'll use a simpler approach
            breaker = circuit_breaker_manager.get_breaker(service)
            return asyncio.run(breaker.call(func, *args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@asynccontextmanager
async def resilient_call(operation: str, service: str = None):
    """Context manager combining error handling and circuit breaker."""
    async with error_handler.handle_errors(operation, service):
        yield
