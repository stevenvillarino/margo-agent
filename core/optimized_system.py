"""
Optimized Agent System Integration

Integrates all core optimizations into the existing agent system
with backward compatibility and enhanced performance.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Type
from dataclasses import dataclass
from datetime import datetime
import time

# Import core optimizations
from core.config import SystemConfig, get_config
from core.memory_manager import MemoryManager, BoundedConversationMemory
from core.connection_manager import ConnectionManager, get_http_session
from core.resilience import CircuitBreakerManager, ErrorHandler, with_circuit_breaker, resilient_call
from core.load_balancer import LoadBalancer, AgentPool, Agent as LoadBalancerAgent
from core.cache import DistributedCache, cached, get_cache
from core.prompt_manager import PromptManager, get_prompt_manager
from core.event_bus import EventBus, EventSubscriber, EventType, get_event_bus
from core.monitoring import MonitoringSystem, get_monitoring, record_request_metric, record_error_metric

# Import existing agents
from agents.design_reviewer import DesignReviewAgent
from agents.enhanced_system import EnhancedDesignReviewSystem
from agents.advanced_workflow_system import AdvancedWorkflowSystem


@dataclass
class OptimizedAgentConfig:
    """Configuration for optimized agents."""
    enable_caching: bool = True
    enable_load_balancing: bool = True
    enable_circuit_breaker: bool = True
    enable_memory_optimization: bool = True
    enable_prompt_optimization: bool = True
    enable_event_bus: bool = True
    enable_monitoring: bool = True


class OptimizedAgentWrapper:
    """Wrapper that adds optimizations to existing agents."""
    
    def __init__(self, 
                 agent_instance: Any,
                 agent_type: str,
                 config: OptimizedAgentConfig = None):
        self.agent_instance = agent_instance
        self.agent_type = agent_type
        self.config = config or OptimizedAgentConfig()
        self.agent_id = f"{agent_type}_{id(agent_instance)}"
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{agent_type}")
        
        # Initialize optimizations
        self._setup_memory_management()
        self._setup_caching()
        self._setup_monitoring()
    
    def _setup_memory_management(self):
        """Setup memory management for the agent."""
        if self.config.enable_memory_optimization:
            from core.memory_manager import get_memory_manager
            memory_manager = get_memory_manager()
            self.memory = memory_manager.get_conversation_memory(self.agent_id)
        else:
            self.memory = None
    
    def _setup_caching(self):
        """Setup caching for the agent."""
        if self.config.enable_caching:
            self.cache = get_cache()
        else:
            self.cache = None
    
    def _setup_monitoring(self):
        """Setup monitoring for the agent."""
        if self.config.enable_monitoring:
            self.monitoring = get_monitoring()
        else:
            self.monitoring = None
    
    @with_circuit_breaker("agent_review")
    async def review_with_optimizations(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute agent review with all optimizations."""
        start_time = time.time()
        
        try:
            # Generate cache key
            cache_key = None
            if self.cache:
                cache_key = self._generate_cache_key(*args, **kwargs)
                
                # Try to get from cache
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    self.logger.debug(f"Cache hit for agent {self.agent_type}")
                    return cached_result
            
            # Execute original review method
            if hasattr(self.agent_instance, 'review'):
                if asyncio.iscoroutinefunction(self.agent_instance.review):
                    result = await self.agent_instance.review(*args, **kwargs)
                else:
                    result = self.agent_instance.review(*args, **kwargs)
            else:
                # Fallback for different method names
                method_names = ['process_request', 'analyze', 'evaluate']
                method = None
                for name in method_names:
                    if hasattr(self.agent_instance, name):
                        method = getattr(self.agent_instance, name)
                        break
                
                if method:
                    if asyncio.iscoroutinefunction(method):
                        result = await method(*args, **kwargs)
                    else:
                        result = method(*args, **kwargs)
                else:
                    raise AttributeError(f"No review method found on {self.agent_type}")
            
            # Cache the result
            if self.cache and cache_key and result:
                await self.cache.set(cache_key, result, ttl=3600)
            
            # Store in conversation memory
            if self.memory:
                self.memory.add_message({
                    'type': 'review_request',
                    'agent_type': self.agent_type,
                    'timestamp': datetime.now().isoformat(),
                    'duration': time.time() - start_time,
                    'success': True
                })
            
            # Record metrics
            duration = time.time() - start_time
            record_request_metric(self.agent_type, duration, True)
            
            return result
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            record_request_metric(self.agent_type, duration, False)
            record_error_metric("agent_review_error", self.agent_type)
            
            # Store error in memory
            if self.memory:
                self.memory.add_message({
                    'type': 'review_error',
                    'agent_type': self.agent_type,
                    'timestamp': datetime.now().isoformat(),
                    'duration': duration,
                    'error': str(e),
                    'success': False
                })
            
            self.logger.error(f"Agent {self.agent_type} review failed: {e}")
            raise
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key for review request."""
        import hashlib
        import json
        
        # Create a deterministic key from arguments
        key_data = {
            'agent_type': self.agent_type,
            'args': str(args),
            'kwargs': {k: str(v) for k, v in kwargs.items()}
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this agent."""
        stats = {
            'agent_type': self.agent_type,
            'agent_id': self.agent_id,
            'memory_stats': None,
            'cache_available': self.cache is not None,
            'monitoring_enabled': self.monitoring is not None
        }
        
        if self.memory:
            stats['memory_stats'] = self.memory.get_stats()
        
        return stats


class OptimizedDesignReviewAgent(OptimizedAgentWrapper):
    """Optimized version of DesignReviewAgent."""
    
    def __init__(self, model_name: str = "gpt-4-vision-preview", config: OptimizedAgentConfig = None):
        # Create original agent
        original_agent = DesignReviewAgent(model_name)
        
        # Initialize wrapper
        super().__init__(original_agent, "design_reviewer", config)
    
    async def review_design(self, file, review_type: str = "General Design", 
                          detail_level: int = 3, include_suggestions: bool = True) -> Dict[str, Any]:
        """Optimized design review method."""
        return await self.review_with_optimizations(
            file, review_type, detail_level, include_suggestions
        )


class OptimizedWorkflowSystem:
    """Optimized version of AdvancedWorkflowSystem with all enhancements."""
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize optimization components
        self._initialize_components()
        
        # Create optimized agents
        self.agents: Dict[str, OptimizedAgentWrapper] = {}
        self._initialize_agents()
        
        # Setup event subscriptions
        self._setup_event_subscriptions()
    
    def _initialize_components(self):
        """Initialize all optimization components."""
        # Memory manager
        from core.memory_manager import get_memory_manager
        self.memory_manager = get_memory_manager()
        
        # Connection manager
        from core.connection_manager import get_connection_manager
        self.connection_manager = get_connection_manager()
        
        # Load balancer
        from core.load_balancer import get_load_balancer
        self.load_balancer = get_load_balancer()
        
        # Cache
        self.cache = get_cache()
        
        # Prompt manager
        self.prompt_manager = get_prompt_manager()
        
        # Event bus
        self.event_bus = get_event_bus()
        
        # Monitoring
        self.monitoring = get_monitoring()
        
        self.logger.info("Optimization components initialized")
    
    def _initialize_agents(self):
        """Initialize optimized agents."""
        agent_config = OptimizedAgentConfig()
        
        # Design reviewer
        design_agent = OptimizedDesignReviewAgent(config=agent_config)
        self.agents["design_reviewer"] = design_agent
        
        # Add to load balancer
        if self.load_balancer:
            pool = self.load_balancer.create_pool("design_reviewer")
            # Note: Would need to adapt LoadBalancerAgent protocol for actual integration
        
        self.logger.info(f"Initialized {len(self.agents)} optimized agents")
    
    def _setup_event_subscriptions(self):
        """Setup event bus subscriptions."""
        if not self.event_bus:
            return
        
        # Create workflow event subscriber
        workflow_subscriber = WorkflowEventSubscriber("optimized_workflow_system")
        
        # Subscribe to relevant events
        self.event_bus.subscribe(workflow_subscriber, [
            EventType.WORKFLOW_STARTED,
            EventType.WORKFLOW_COMPLETED,
            EventType.WORKFLOW_FAILED,
            EventType.AGENT_REVIEW_COMPLETED
        ])
        
        self.logger.info("Event subscriptions configured")
    
    async def process_design_review(self, 
                                  submission: Dict[str, Any],
                                  workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Process design review with all optimizations."""
        workflow_id = workflow_id or f"workflow_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Publish workflow started event
            if self.event_bus:
                from core.event_bus import publish_workflow_event
                await publish_workflow_event(
                    EventType.WORKFLOW_STARTED,
                    workflow_id,
                    {"submission": submission}
                )
            
            # Get design reviewer agent
            design_agent = self.agents.get("design_reviewer")
            if not design_agent:
                raise RuntimeError("Design reviewer agent not available")
            
            # Process with optimizations
            async with resilient_call("design_review", "design_reviewer"):
                result = await design_agent.review_with_optimizations(
                    submission.get("file"),
                    submission.get("review_type", "General Design"),
                    submission.get("detail_level", 3),
                    submission.get("include_suggestions", True)
                )
            
            # Enhance result with workflow metadata
            enhanced_result = {
                "workflow_id": workflow_id,
                "review_result": result,
                "processing_time": time.time() - start_time,
                "optimizations_applied": {
                    "caching": design_agent.cache is not None,
                    "memory_management": design_agent.memory is not None,
                    "circuit_breaker": True,
                    "monitoring": design_agent.monitoring is not None
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Publish completion event
            if self.event_bus:
                await publish_workflow_event(
                    EventType.WORKFLOW_COMPLETED,
                    workflow_id,
                    {"result": enhanced_result}
                )
            
            return enhanced_result
            
        except Exception as e:
            # Publish failure event
            if self.event_bus:
                await publish_workflow_event(
                    EventType.WORKFLOW_FAILED,
                    workflow_id,
                    {"error": str(e), "processing_time": time.time() - start_time}
                )
            
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        agent_stats = {}
        for agent_id, agent in self.agents.items():
            agent_stats[agent_id] = agent.get_performance_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "config": self.config.to_dict(),
            "agents": agent_stats,
            "memory_manager_stats": self.memory_manager.get_system_stats() if self.memory_manager else None,
            "cache_stats": self.cache.get_stats() if self.cache else None,
            "monitoring_status": self.monitoring.get_system_status() if self.monitoring else None,
            "event_bus_stats": self.event_bus.get_statistics() if self.event_bus else None
        }


class WorkflowEventSubscriber(EventSubscriber):
    """Event subscriber for workflow events."""
    
    def __init__(self, subscriber_id: str):
        super().__init__(subscriber_id)
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{subscriber_id}")
    
    async def handle_event(self, event) -> bool:
        """Handle workflow events."""
        try:
            if event.type == EventType.WORKFLOW_STARTED:
                workflow_id = event.data.get("workflow_id")
                self.active_workflows[workflow_id] = {
                    "started_at": event.timestamp,
                    "status": "running"
                }
                self.logger.info(f"Tracking workflow {workflow_id}")
                
            elif event.type == EventType.WORKFLOW_COMPLETED:
                workflow_id = event.data.get("workflow_id")
                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id]["status"] = "completed"
                    self.active_workflows[workflow_id]["completed_at"] = event.timestamp
                    
            elif event.type == EventType.WORKFLOW_FAILED:
                workflow_id = event.data.get("workflow_id")
                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id]["status"] = "failed"
                    self.active_workflows[workflow_id]["error"] = event.data.get("error")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling event {event.id}: {e}")
            return False


# Factory function for creating optimized system
async def create_optimized_system(config: SystemConfig = None) -> OptimizedWorkflowSystem:
    """Create fully optimized workflow system."""
    
    # Initialize all core systems
    from core.config import get_config
    from core.memory_manager import get_memory_manager
    from core.connection_manager import get_connection_manager
    from core.cache import initialize_cache, CacheConfig
    from core.prompt_manager import initialize_prompt_manager, PromptOptimization
    from core.event_bus import initialize_event_bus, EventBusConfig, get_event_bus
    from core.monitoring import initialize_monitoring, MetricConfig, get_monitoring
    
    # Load configuration
    if config is None:
        config = get_config()
    
    # Initialize subsystems
    cache_config = config.get_cache_config()
    initialize_cache(cache_config)
    
    prompt_optimization = PromptOptimization(
        max_length=4000,
        compression_enabled=True,
        cache_enabled=True
    )
    initialize_prompt_manager(prompt_optimization)
    
    event_bus_config = EventBusConfig(
        max_event_history=10000,
        max_concurrent_handlers=50
    )
    # Only initialize if not already initialized
    if not get_event_bus():
        await initialize_event_bus(event_bus_config)
    
    monitoring_config = config.get_monitoring_config()
    # Only initialize if not already initialized
    if not get_monitoring():
        await initialize_monitoring(monitoring_config)
    
    # Create optimized system
    system = OptimizedWorkflowSystem(config)
    
    return system


# Compatibility function for existing code
def create_enhanced_design_review_system(*args, **kwargs) -> OptimizedWorkflowSystem:
    """Create optimized system with backward compatibility."""
    return asyncio.run(create_optimized_system())


# Export optimized versions
__all__ = [
    'OptimizedDesignReviewAgent',
    'OptimizedWorkflowSystem',
    'create_optimized_system',
    'create_enhanced_design_review_system'
]
