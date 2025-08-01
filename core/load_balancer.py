"""
Agent Load Balancing and Resource Management

Implements intelligent load balancing across multiple agent instances
and manages resource allocation for optimal performance.
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Protocol, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import heapq
import threading
from abc import ABC, abstractmethod

T = TypeVar('T')


class AgentStatus(Enum):
    """Agent status states."""
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


@dataclass
class AgentMetrics:
    """Metrics for an agent instance."""
    id: str
    status: AgentStatus
    current_load: int
    max_load: int
    avg_response_time: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    last_request_time: Optional[float]
    created_at: float
    
    @property
    def load_percentage(self) -> float:
        """Get load as percentage."""
        return (self.current_load / self.max_load) * 100 if self.max_load > 0 else 0
    
    @property
    def success_rate(self) -> float:
        """Get success rate."""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    @property
    def availability_score(self) -> float:
        """Calculate availability score (0-1)."""
        if self.status == AgentStatus.FAILED:
            return 0.0
        if self.status == AgentStatus.MAINTENANCE:
            return 0.0
        if self.status == AgentStatus.OVERLOADED:
            return 0.1
        
        # Score based on load and success rate
        load_score = max(0, 1.0 - (self.load_percentage / 100))
        success_score = self.success_rate
        
        return (load_score * 0.6) + (success_score * 0.4)


class Agent(Protocol):
    """Protocol for agent instances."""
    
    @property
    def id(self) -> str:
        """Agent unique identifier."""
        ...
    
    @property
    def max_load(self) -> int:
        """Maximum concurrent requests this agent can handle."""
        ...
    
    async def process_request(self, request: Any) -> Any:
        """Process a request."""
        ...
    
    def get_current_load(self) -> int:
        """Get current load."""
        ...


@dataclass
class LoadBalancingConfig:
    """Configuration for load balancing."""
    max_agents_per_type: int = 5
    min_agents_per_type: int = 1
    scale_up_threshold: float = 0.8  # Scale up when average load > 80%
    scale_down_threshold: float = 0.3  # Scale down when average load < 30%
    health_check_interval: int = 30  # seconds
    request_timeout: int = 30  # seconds
    max_queue_size: int = 100


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    AVAILABILITY_BASED = "availability_based"


class AgentPool:
    """Pool of agent instances with load balancing."""
    
    def __init__(self, 
                 agent_type: str,
                 config: LoadBalancingConfig,
                 strategy: LoadBalancingStrategy = LoadBalancingStrategy.AVAILABILITY_BASED):
        self.agent_type = agent_type
        self.config = config
        self.strategy = strategy
        
        self.agents: Dict[str, Agent] = {}
        self.metrics: Dict[str, AgentMetrics] = {}
        self.request_queue: deque = deque(maxlen=config.max_queue_size)
        
        # Load balancing state
        self.round_robin_index = 0
        self.active_requests: Dict[str, List[asyncio.Task]] = defaultdict(list)
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.avg_queue_time = 0.0
        
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{__name__}.{agent_type}")
        
        # Start background tasks
        self._start_health_monitor()
    
    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the pool."""
        self.agents[agent.id] = agent
        self.metrics[agent.id] = AgentMetrics(
            id=agent.id,
            status=AgentStatus.IDLE,
            current_load=0,
            max_load=agent.max_load,
            avg_response_time=0.0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            last_request_time=None,
            created_at=time.time()
        )
        self.logger.info(f"Added agent {agent.id} to pool {self.agent_type}")
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the pool."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.metrics[agent_id]
            if agent_id in self.active_requests:
                del self.active_requests[agent_id]
            self.logger.info(f"Removed agent {agent_id} from pool {self.agent_type}")
            return True
        return False
    
    async def get_available_agent(self) -> Optional[Agent]:
        """Get the best available agent based on strategy."""
        async with self.lock:
            available_agents = [
                agent_id for agent_id, metrics in self.metrics.items()
                if metrics.status in [AgentStatus.IDLE, AgentStatus.BUSY] and
                metrics.current_load < metrics.max_load
            ]
            
            if not available_agents:
                return None
            
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                selected_id = self._round_robin_selection(available_agents)
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                selected_id = self._least_connections_selection(available_agents)
            elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                selected_id = self._least_response_time_selection(available_agents)
            else:  # AVAILABILITY_BASED (default)
                selected_id = self._availability_based_selection(available_agents)
            
            return self.agents.get(selected_id)
    
    def _round_robin_selection(self, available_agents: List[str]) -> str:
        """Round robin selection."""
        self.round_robin_index = (self.round_robin_index + 1) % len(available_agents)
        return available_agents[self.round_robin_index]
    
    def _least_connections_selection(self, available_agents: List[str]) -> str:
        """Select agent with least connections."""
        return min(available_agents, key=lambda aid: self.metrics[aid].current_load)
    
    def _least_response_time_selection(self, available_agents: List[str]) -> str:
        """Select agent with least average response time."""
        return min(available_agents, key=lambda aid: self.metrics[aid].avg_response_time)
    
    def _availability_based_selection(self, available_agents: List[str]) -> str:
        """Select agent with highest availability score."""
        return max(available_agents, key=lambda aid: self.metrics[aid].availability_score)
    
    async def process_request(self, request: Any, timeout: Optional[int] = None) -> Any:
        """Process a request using load balancing."""
        start_time = time.time()
        timeout = timeout or self.config.request_timeout
        
        self.total_requests += 1
        
        try:
            # Get available agent
            agent = await self.get_available_agent()
            if not agent:
                # Queue the request if no agents available
                if len(self.request_queue) >= self.config.max_queue_size:
                    raise Exception(f"Request queue full for {self.agent_type}")
                
                # Wait for agent to become available
                for _ in range(timeout):
                    await asyncio.sleep(1)
                    agent = await self.get_available_agent()
                    if agent:
                        break
                else:
                    raise Exception(f"No available agents for {self.agent_type} after {timeout}s")
            
            # Update metrics - request started
            await self._update_agent_metrics_start(agent.id)
            
            try:
                # Process request with timeout
                result = await asyncio.wait_for(
                    agent.process_request(request),
                    timeout=timeout
                )
                
                # Update metrics - request successful
                response_time = time.time() - start_time
                await self._update_agent_metrics_success(agent.id, response_time)
                
                self.successful_requests += 1
                return result
                
            except Exception as e:
                # Update metrics - request failed
                await self._update_agent_metrics_failure(agent.id)
                self.failed_requests += 1
                raise
                
        except Exception as e:
            self.logger.error(f"Request failed for {self.agent_type}: {e}")
            raise
    
    async def _update_agent_metrics_start(self, agent_id: str):
        """Update metrics when request starts."""
        async with self.lock:
            metrics = self.metrics[agent_id]
            metrics.current_load += 1
            metrics.last_request_time = time.time()
            
            # Update status based on load
            if metrics.current_load >= metrics.max_load:
                metrics.status = AgentStatus.OVERLOADED
            elif metrics.current_load > 0:
                metrics.status = AgentStatus.BUSY
            else:
                metrics.status = AgentStatus.IDLE
    
    async def _update_agent_metrics_success(self, agent_id: str, response_time: float):
        """Update metrics when request succeeds."""
        async with self.lock:
            metrics = self.metrics[agent_id]
            metrics.current_load = max(0, metrics.current_load - 1)
            metrics.total_requests += 1
            metrics.successful_requests += 1
            
            # Update average response time
            if metrics.total_requests == 1:
                metrics.avg_response_time = response_time
            else:
                # Exponential moving average
                alpha = 0.1
                metrics.avg_response_time = (alpha * response_time) + ((1 - alpha) * metrics.avg_response_time)
            
            # Update status
            if metrics.current_load == 0:
                metrics.status = AgentStatus.IDLE
            elif metrics.current_load < metrics.max_load:
                metrics.status = AgentStatus.BUSY
            else:
                metrics.status = AgentStatus.OVERLOADED
    
    async def _update_agent_metrics_failure(self, agent_id: str):
        """Update metrics when request fails."""
        async with self.lock:
            metrics = self.metrics[agent_id]
            metrics.current_load = max(0, metrics.current_load - 1)
            metrics.total_requests += 1
            metrics.failed_requests += 1
            
            # Check if agent should be marked as failed
            if metrics.success_rate < 0.5 and metrics.total_requests >= 10:
                metrics.status = AgentStatus.FAILED
                self.logger.warning(f"Agent {agent_id} marked as failed due to low success rate")
            else:
                # Update status based on load
                if metrics.current_load == 0:
                    metrics.status = AgentStatus.IDLE
                elif metrics.current_load < metrics.max_load:
                    metrics.status = AgentStatus.BUSY
                else:
                    metrics.status = AgentStatus.OVERLOADED
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        total_capacity = sum(metrics.max_load for metrics in self.metrics.values())
        current_load = sum(metrics.current_load for metrics in self.metrics.values())
        
        healthy_agents = len([
            m for m in self.metrics.values() 
            if m.status not in [AgentStatus.FAILED, AgentStatus.MAINTENANCE]
        ])
        
        avg_response_time = sum(m.avg_response_time for m in self.metrics.values()) / len(self.metrics) if self.metrics else 0
        
        success_rate = self.successful_requests / self.total_requests if self.total_requests > 0 else 1.0
        
        return {
            "agent_type": self.agent_type,
            "total_agents": len(self.agents),
            "healthy_agents": healthy_agents,
            "total_capacity": total_capacity,
            "current_load": current_load,
            "load_percentage": (current_load / total_capacity * 100) if total_capacity > 0 else 0,
            "avg_response_time": avg_response_time,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "queue_size": len(self.request_queue)
        }
    
    def _start_health_monitor(self):
        """Start background health monitoring."""
        def monitor():
            while True:
                try:
                    asyncio.run(self._health_check())
                    time.sleep(self.config.health_check_interval)
                except Exception as e:
                    self.logger.error(f"Health check failed: {e}")
                    time.sleep(self.config.health_check_interval)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    async def _health_check(self):
        """Perform health check on all agents."""
        current_time = time.time()
        
        async with self.lock:
            for agent_id, metrics in self.metrics.items():
                # Reset failed agents after some time
                if metrics.status == AgentStatus.FAILED:
                    if metrics.last_request_time and (current_time - metrics.last_request_time) > 300:  # 5 minutes
                        metrics.status = AgentStatus.IDLE
                        metrics.failed_requests = 0
                        metrics.successful_requests = 0
                        metrics.total_requests = 0
                        self.logger.info(f"Reset failed agent {agent_id}")


class LoadBalancer:
    """Main load balancer managing multiple agent pools."""
    
    def __init__(self, config: LoadBalancingConfig = None):
        self.config = config or LoadBalancingConfig()
        self.pools: Dict[str, AgentPool] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_pool(self, 
                   agent_type: str, 
                   strategy: LoadBalancingStrategy = LoadBalancingStrategy.AVAILABILITY_BASED) -> AgentPool:
        """Create a new agent pool."""
        if agent_type in self.pools:
            raise ValueError(f"Pool for {agent_type} already exists")
        
        pool = AgentPool(agent_type, self.config, strategy)
        self.pools[agent_type] = pool
        
        self.logger.info(f"Created pool for {agent_type} with strategy {strategy.value}")
        return pool
    
    def get_pool(self, agent_type: str) -> Optional[AgentPool]:
        """Get agent pool by type."""
        return self.pools.get(agent_type)
    
    def add_agent(self, agent_type: str, agent: Agent) -> bool:
        """Add agent to pool."""
        pool = self.pools.get(agent_type)
        if not pool:
            self.logger.warning(f"No pool found for agent type {agent_type}")
            return False
        
        pool.add_agent(agent)
        return True
    
    async def process_request(self, agent_type: str, request: Any, timeout: Optional[int] = None) -> Any:
        """Process request using appropriate agent pool."""
        pool = self.pools.get(agent_type)
        if not pool:
            raise ValueError(f"No pool configured for agent type: {agent_type}")
        
        return await pool.process_request(request, timeout)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all pools."""
        return {
            pool_name: pool.get_pool_stats() 
            for pool_name, pool in self.pools.items()
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        all_stats = self.get_all_stats()
        
        total_agents = sum(stats['total_agents'] for stats in all_stats.values())
        total_requests = sum(stats['total_requests'] for stats in all_stats.values())
        total_successful = sum(stats['successful_requests'] for stats in all_stats.values())
        
        return {
            "total_pools": len(self.pools),
            "total_agents": total_agents,
            "total_requests": total_requests,
            "total_successful_requests": total_successful,
            "overall_success_rate": total_successful / total_requests if total_requests > 0 else 1.0,
            "pool_stats": all_stats
        }


# Global load balancer instance
_global_load_balancer = None


def get_load_balancer() -> LoadBalancer:
    """Get the global load balancer instance."""
    global _global_load_balancer
    if _global_load_balancer is None:
        _global_load_balancer = LoadBalancer()
    return _global_load_balancer


def initialize_load_balancer(config=None) -> LoadBalancer:
    """Initialize the global load balancer with custom config."""
    global _global_load_balancer
    _global_load_balancer = LoadBalancer()
    return _global_load_balancer
