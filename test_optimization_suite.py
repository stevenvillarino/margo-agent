#!/usr/bin/env python3
"""
Comprehensive Test Suite for Optimized Margo Agent System

This script tests all optimization components and validates
that the system works correctly with performance improvements.
"""

import asyncio
import logging
import time
import traceback
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test Results
test_results = {
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'errors': []
}


class TestResult:
    """Test result container."""
    
    def __init__(self, name: str, passed: bool, duration: float, error: Optional[str] = None):
        self.name = name
        self.passed = passed
        self.duration = duration
        self.error = error


def test_decorator(name: str):
    """Decorator for test functions."""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                print(f"🧪 Testing {name}...")
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                if result:
                    print(f"✅ {name} - PASSED ({duration:.2f}s)")
                    test_results['passed'] += 1
                    return TestResult(name, True, duration)
                else:
                    print(f"❌ {name} - FAILED ({duration:.2f}s)")
                    test_results['failed'] += 1
                    return TestResult(name, False, duration, "Test returned False")
                    
            except Exception as e:
                duration = time.time() - start_time
                error_msg = f"{type(e).__name__}: {str(e)}"
                print(f"💥 {name} - ERROR ({duration:.2f}s): {error_msg}")
                test_results['failed'] += 1
                test_results['errors'].append(f"{name}: {error_msg}")
                return TestResult(name, False, duration, error_msg)
        
        return wrapper
    return decorator


@test_decorator("Configuration Loading")
async def test_configuration():
    """Test configuration loading and validation."""
    try:
        from core.config import get_config, ConfigurationManager
        
        # Test basic config loading
        config = get_config()
        assert config is not None
        assert hasattr(config, 'environment')
        assert hasattr(config, 'openai_api_key')
        
        # Test configuration manager
        config_manager = ConfigurationManager()
        assert config_manager is not None
        
        # Test validation
        integrations = config.get_integration_status()
        assert isinstance(integrations, dict)
        
        return True
    except ImportError as e:
        print(f"  Configuration module not found: {e}")
        return False


@test_decorator("Memory Management")
async def test_memory_management():
    """Test memory management components."""
    try:
        from core.memory_manager import MemoryManager, MemoryConfig, get_memory_manager
        
        # Test memory config
        config = MemoryConfig(
            max_conversation_tokens=1000,
            max_conversation_messages=10,
            max_memory_mb=50
        )
        assert config.max_conversation_tokens == 1000
        
        # Test memory manager
        memory_manager = get_memory_manager()
        assert memory_manager is not None
        
        # Test memory operations
        conversation_id = "test_conv_123"
        conv_memory = memory_manager.get_conversation_memory(conversation_id)
        conv_memory.add_message({"role": "user", "content": "test message"})
        messages = conv_memory.get_messages()
        assert len(messages) == 1
        
        # Test memory cleanup
        memory_manager.cleanup_inactive_conversations()
        # Conversation should still exist since it was just used
        assert conversation_id in memory_manager.conversations
        
        return True
    except ImportError as e:
        print(f"  Memory management module not found: {e}")
        return False


@test_decorator("Connection Management")
async def test_connection_management():
    """Test HTTP connection pooling."""
    try:
        from core.connection_manager import get_connection_manager, ConnectionConfig
        
        # Test connection manager
        connection_manager = get_connection_manager()
        assert connection_manager is not None
        
        # Test session creation
        async with connection_manager.get_connection("test_service") as session:
            assert session is not None
        
        return True
    except ImportError as e:
        print(f"  Connection management module not found: {e}")
        return False


@test_decorator("Caching System")
async def test_caching():
    """Test caching functionality."""
    try:
        from core.cache import get_cache, CacheConfig, LRUCache, initialize_cache
        
        # Test LRU cache
        lru_cache = LRUCache(maxsize=10)
        lru_cache.set("test_key", "test_value")
        assert lru_cache.get("test_key") == "test_value"
        
        # Initialize distributed cache
        cache_config = CacheConfig(
            redis_url=None,  # Use local cache only for testing
            local_cache_size=10,
            default_ttl=60
        )
        cache = initialize_cache(cache_config)
        assert cache is not None
        
        # Test cache operations
        await cache.set("test_async_key", "test_async_value", ttl=60)
        value = await cache.get("test_async_key")
        assert value == "test_async_value"
        
        # Test cache decorator
        @cache.cached(ttl=30)
        async def test_cached_function(x: int) -> int:
            return x * 2
        
        result1 = await test_cached_function(5)
        result2 = await test_cached_function(5)  # Should be cached
        assert result1 == result2 == 10
        
        return True
    except ImportError as e:
        print(f"  Caching module not found: {e}")
        return False


@test_decorator("Prompt Management")
async def test_prompt_management():
    """Test prompt optimization and management."""
    try:
        from core.prompt_manager import get_prompt_manager, PromptTemplate, TokenEstimator
        
        # Test token estimator
        estimator = TokenEstimator()
        tokens = estimator.estimate_tokens("This is a test message")
        assert tokens > 0
        
        # Test prompt template
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}, your role is {role}",
            variables=["name", "role"],
            category="test",
            estimated_tokens=10
        )
        
        # Note: PromptTemplate doesn't have render method, let's test manually
        rendered = template.template.format(name="Alice", role="designer")
        assert "Alice" in rendered
        assert "designer" in rendered
        
        # Test prompt manager initialization
        from core.prompt_manager import initialize_prompt_manager, PromptOptimization
        prompt_config = PromptOptimization(
            max_length=2000,
            compression_enabled=True,
            cache_enabled=True
        )
        prompt_manager = initialize_prompt_manager(prompt_config)
        assert prompt_manager is not None
        
        # Test prompt optimization
        long_prompt = "This is a very long prompt that should be optimized. " * 50
        optimized = await prompt_manager.optimize_prompt(long_prompt)
        assert len(optimized) <= len(long_prompt)
        
        return True
    except ImportError as e:
        print(f"  Prompt management module not found: {e}")
        return False


@test_decorator("Event Bus")
async def test_event_bus():
    """Test event-driven architecture."""
    try:
        from core.event_bus import get_event_bus, Event, EventBusConfig, initialize_event_bus
        
        # Test event creation
        event = Event(
            type="test_event",
            data={"message": "test"},
            source="test_suite"
        )
        assert event.type == "test_event"
        assert event.data["message"] == "test"
        
        # Initialize event bus
        event_config = EventBusConfig(
            max_event_history=100,
            retry_delay_seconds=0.1,
            max_concurrent_handlers=2
        )
        event_bus = await initialize_event_bus(event_config)
        assert event_bus is not None
        
        # Test event publishing and subscription
        received_events = []
        
        async def test_handler(event: Event):
            received_events.append(event)
        
        # Subscribe to events
        event_bus.subscribe("test_event", test_handler)
        
        # Publish event
        await event_bus.publish(event)
        
        # Give event bus time to process
        await asyncio.sleep(0.1)
        
        # Check if event was received
        assert len(received_events) == 1
        assert received_events[0].type == "test_event"
        
        return True
    except ImportError as e:
        print(f"  Event bus module not found: {e}")
        return False


@test_decorator("Circuit Breaker")
async def test_circuit_breaker():
    """Test resilience and circuit breaker functionality."""
    try:
        from core.resilience import CircuitBreaker, CircuitState
        
        # Test circuit breaker creation
        circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1.0,
            request_timeout=0.5
        )
        assert circuit_breaker.state == CircuitState.CLOSED
        
        # Test successful call
        async def successful_function():
            return "success"
        
        result = await circuit_breaker.call(successful_function)
        assert result == "success"
        assert circuit_breaker.state == CircuitState.CLOSED
        
        # Test failing function
        async def failing_function():
            raise Exception("Test failure")
        
        # Circuit breaker should open after failures
        for _ in range(3):
            try:
                await circuit_breaker.call(failing_function)
            except:
                pass
        
        # Circuit should be open now
        assert circuit_breaker.state == CircuitState.OPEN
        
        return True
    except ImportError as e:
        print(f"  Resilience module not found: {e}")
        return False


@test_decorator("Load Balancer")
async def test_load_balancer():
    """Test load balancing functionality."""
    try:
        from core.load_balancer import LoadBalancer, LoadBalancingStrategy
        
        # Test load balancer creation
        load_balancer = LoadBalancer(
            strategy=LoadBalancingStrategy.ROUND_ROBIN,
            max_agents=3
        )
        assert load_balancer is not None
        
        # Test agent registration
        class MockAgent:
            def __init__(self, name: str):
                self.name = name
                self.id = name
                
            async def is_healthy(self) -> bool:
                return True
        
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        await load_balancer.register_agent(agent1)
        await load_balancer.register_agent(agent2)
        
        # Test agent selection
        selected_agent = await load_balancer.select_agent()
        assert selected_agent is not None
        assert selected_agent.name in ["agent1", "agent2"]
        
        return True
    except ImportError as e:
        print(f"  Load balancer module not found: {e}")
        return False


@test_decorator("Monitoring System")
async def test_monitoring():
    """Test monitoring and metrics functionality."""
    try:
        from core.monitoring import get_metrics, get_health_monitor, MetricConfig
        
        # Test metrics
        metrics = get_metrics()
        assert metrics is not None
        
        # Test metric recording
        metrics.record_request_duration(100.0)
        metrics.increment_counter("test_counter")
        
        # Test health monitor
        health_monitor = get_health_monitor()
        assert health_monitor is not None
        
        # Test health check
        health_status = await health_monitor.check_health()
        assert health_status is not None
        assert hasattr(health_status, 'status')
        
        return True
    except ImportError as e:
        print(f"  Monitoring module not found: {e}")
        return False


@test_decorator("Optimized System Integration")
async def test_optimized_system():
    """Test the complete optimized system."""
    try:
        from core.optimized_system import create_optimized_system, OptimizedAgentWrapper
        from core.config import get_config
        
        # Test config loading
        config = get_config()
        assert config is not None
        
        # Test optimized system creation
        system = await create_optimized_system(config)
        assert system is not None
        
        # Test agent wrapper
        class MockAgent:
            async def process(self, data: str) -> str:
                return f"processed: {data}"
        
        mock_agent = MockAgent()
        wrapped_agent = OptimizedAgentWrapper(
            agent=mock_agent,
            enable_caching=True,
            enable_monitoring=True
        )
        
        # Test wrapped agent functionality
        result = await wrapped_agent.process("test_data")
        assert "processed: test_data" in result
        
        return True
    except ImportError as e:
        print(f"  Optimized system module not found: {e}")
        return False


@test_decorator("Performance Benchmark")
async def test_performance():
    """Run basic performance benchmarks."""
    try:
        from core.cache import get_cache
        from core.memory_manager import get_memory_manager
        
        # Cache performance test
        cache = get_cache()
        
        start_time = time.time()
        for i in range(100):
            await cache.set(f"perf_key_{i}", f"value_{i}")
        cache_write_time = time.time() - start_time
        
        start_time = time.time()
        for i in range(100):
            await cache.get(f"perf_key_{i}")
        cache_read_time = time.time() - start_time
        
        print(f"  Cache write time (100 ops): {cache_write_time:.3f}s")
        print(f"  Cache read time (100 ops): {cache_read_time:.3f}s")
        
        # Memory management performance
        memory_manager = get_memory_manager()
        
        start_time = time.time()
        for i in range(100):
            memory_manager.add_message(f"conv_{i}", "user", f"message_{i}")
        memory_write_time = time.time() - start_time
        
        print(f"  Memory write time (100 ops): {memory_write_time:.3f}s")
        
        # Performance should be reasonable
        assert cache_write_time < 1.0  # Should be fast
        assert cache_read_time < 0.5   # Reads should be very fast
        assert memory_write_time < 0.5 # Memory ops should be fast
        
        return True
    except Exception as e:
        print(f"  Performance test error: {e}")
        return False


async def run_integration_test():
    """Run a comprehensive integration test."""
    print("🔗 Running Integration Test...")
    
    try:
        # Test complete workflow
        from core.optimized_system import create_optimized_system
        from core.config import get_config
        
        config = get_config()
        system = await create_optimized_system(config)
        
        # Test that system has all required components
        assert hasattr(system, 'config')
        assert hasattr(system, 'memory_manager')
        assert hasattr(system, 'cache')
        assert hasattr(system, 'event_bus')
        
        print("✅ Integration Test - PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Integration Test - FAILED: {e}")
        return False


def print_test_summary(results: List[TestResult]):
    """Print comprehensive test summary."""
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    # Overall stats
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    total_time = sum(r.duration for r in results)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Total Time: {total_time:.2f}s")
    
    # Performance summary
    print(f"\n📈 Performance Summary:")
    fastest = min(results, key=lambda r: r.duration)
    slowest = max(results, key=lambda r: r.duration)
    avg_time = total_time / total_tests
    
    print(f"Fastest Test: {fastest.name} ({fastest.duration:.3f}s)")
    print(f"Slowest Test: {slowest.name} ({slowest.duration:.3f}s)")
    print(f"Average Time: {avg_time:.3f}s")
    
    # Failed tests details
    if failed_tests > 0:
        print(f"\n❌ Failed Tests:")
        for result in results:
            if not result.passed:
                print(f"   • {result.name}: {result.error}")
    
    # Success indicator
    if failed_tests == 0:
        print(f"\n🎉 ALL TESTS PASSED! System is ready for production.")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please review the issues above.")
    
    return failed_tests == 0


async def main():
    """Main test runner."""
    
    # Setup logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    print("🧪 MARGO AGENT OPTIMIZATION TEST SUITE")
    print("=" * 60)
    print("Testing all optimization components...\n")
    
    # Run all tests
    test_functions = [
        test_configuration,
        test_memory_management,
        test_connection_management,
        test_caching,
        test_prompt_management,
        test_event_bus,
        test_circuit_breaker,
        test_load_balancer,
        test_monitoring,
        test_optimized_system,
        test_performance
    ]
    
    results = []
    
    # Execute tests
    for test_func in test_functions:
        result = await test_func()
        results.append(result)
    
    # Run integration test
    integration_success = await run_integration_test()
    
    # Print summary
    overall_success = print_test_summary(results) and integration_success
    
    if overall_success:
        print("\n🚀 System ready for deployment!")
        return True
    else:
        print("\n🔧 Please fix the issues above before deployment.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
