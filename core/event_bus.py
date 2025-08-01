"""
Event-Driven Agent Architecture

Implements an event bus system for decoupled agent communication
and workflow orchestration.
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Protocol
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import uuid
from datetime import datetime, timedelta


class EventType(Enum):
    """Types of events in the system."""
    # Workflow events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    
    # Agent events
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    AGENT_REVIEW_STARTED = "agent_review_started"
    AGENT_REVIEW_COMPLETED = "agent_review_completed"
    AGENT_REVIEW_FAILED = "agent_review_failed"
    
    # Communication events
    KNOWLEDGE_REQUEST = "knowledge_request"
    KNOWLEDGE_RESPONSE = "knowledge_response"
    ESCALATION_CREATED = "escalation_created"
    ESCALATION_RESOLVED = "escalation_resolved"
    
    # System events
    SYSTEM_HEALTH_CHECK = "system_health_check"
    PERFORMANCE_ALERT = "performance_alert"
    ERROR_OCCURRED = "error_occurred"
    
    # Custom events
    CUSTOM = "custom"


class Priority(Enum):
    """Event priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Event:
    """Base event class."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.CUSTOM
    source: str = ""
    target: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "target": self.target,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "correlation_id": self.correlation_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=EventType(data.get("type", "custom")),
            source=data.get("source", ""),
            target=data.get("target"),
            priority=Priority(data.get("priority", 2)),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            data=data.get("data", {}),
            correlation_id=data.get("correlation_id"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3)
        )


class EventHandler(Protocol):
    """Protocol for event handlers."""
    
    async def handle_event(self, event: Event) -> bool:
        """Handle an event. Return True if handled successfully."""
        ...


class EventSubscriber(ABC):
    """Base class for event subscribers."""
    
    def __init__(self, subscriber_id: str):
        self.subscriber_id = subscriber_id
        self.subscriptions: List[EventType] = []
    
    @abstractmethod
    async def handle_event(self, event: Event) -> bool:
        """Handle an event."""
        pass
    
    def subscribe_to(self, event_types: Union[EventType, List[EventType]]) -> None:
        """Subscribe to event types."""
        if isinstance(event_types, EventType):
            event_types = [event_types]
        
        for event_type in event_types:
            if event_type not in self.subscriptions:
                self.subscriptions.append(event_type)


@dataclass
class EventBusConfig:
    """Configuration for event bus."""
    max_event_history: int = 10000
    retry_delay_seconds: float = 1.0
    max_concurrent_handlers: int = 50
    enable_persistence: bool = False
    dead_letter_queue_size: int = 1000


class EventBus:
    """Event-driven messaging system for agent communication."""
    
    def __init__(self, config: EventBusConfig = None):
        self.config = config or EventBusConfig()
        
        # Event storage
        self.event_history: deque = deque(maxlen=self.config.max_event_history)
        self.dead_letter_queue: deque = deque(maxlen=self.config.dead_letter_queue_size)
        
        # Subscribers
        self.subscribers: Dict[EventType, List[EventSubscriber]] = defaultdict(list)
        self.subscriber_registry: Dict[str, EventSubscriber] = {}
        
        # Processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing_semaphore = asyncio.Semaphore(self.config.max_concurrent_handlers)
        self.is_running = False
        
        # Statistics
        self.stats = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "events_retried": 0,
            "subscribers_count": 0
        }
        
        self.logger = logging.getLogger(__name__)
    
    async def start(self) -> None:
        """Start the event bus."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start event processing task
        asyncio.create_task(self._process_events())
        
        self.logger.info("Event bus started")
    
    async def stop(self) -> None:
        """Stop the event bus."""
        self.is_running = False
        self.logger.info("Event bus stopped")
    
    def subscribe(self, subscriber: EventSubscriber, event_types: Union[EventType, List[EventType]]) -> None:
        """Subscribe a handler to event types."""
        if isinstance(event_types, EventType):
            event_types = [event_types]
        
        # Register subscriber
        self.subscriber_registry[subscriber.subscriber_id] = subscriber
        
        # Add to event type subscriptions
        for event_type in event_types:
            if subscriber not in self.subscribers[event_type]:
                self.subscribers[event_type].append(subscriber)
                subscriber.subscribe_to(event_type)
        
        self.stats["subscribers_count"] = len(self.subscriber_registry)
        self.logger.info(f"Subscriber {subscriber.subscriber_id} registered for {len(event_types)} event types")
    
    def unsubscribe(self, subscriber_id: str, event_types: Union[EventType, List[EventType]] = None) -> bool:
        """Unsubscribe a handler from event types."""
        if subscriber_id not in self.subscriber_registry:
            return False
        
        subscriber = self.subscriber_registry[subscriber_id]
        
        if event_types is None:
            # Unsubscribe from all
            event_types = list(self.subscribers.keys())
        elif isinstance(event_types, EventType):
            event_types = [event_types]
        
        # Remove from subscriptions
        for event_type in event_types:
            if subscriber in self.subscribers[event_type]:
                self.subscribers[event_type].remove(subscriber)
        
        # If no subscriptions left, remove from registry
        has_subscriptions = any(
            subscriber in subscribers 
            for subscribers in self.subscribers.values()
        )
        
        if not has_subscriptions:
            del self.subscriber_registry[subscriber_id]
        
        self.stats["subscribers_count"] = len(self.subscriber_registry)
        return True
    
    async def publish(self, event: Event) -> str:
        """Publish an event to the bus."""
        self.stats["events_published"] += 1
        
        # Add to history
        self.event_history.append(event)
        
        # Queue for processing
        await self.event_queue.put(event)
        
        self.logger.debug(f"Published event {event.id} of type {event.type.value}")
        return event.id
    
    async def publish_and_wait(self, event: Event, timeout: float = 30.0) -> List[bool]:
        """Publish event and wait for all handlers to complete."""
        # Get relevant subscribers
        subscribers = self.subscribers.get(event.type, [])
        
        if not subscribers:
            return []
        
        # Process handlers concurrently
        tasks = []
        for subscriber in subscribers:
            if self._should_deliver_event(event, subscriber):
                task = asyncio.create_task(self._handle_event_safely(event, subscriber))
                tasks.append(task)
        
        if not tasks:
            return []
        
        # Wait for all handlers
        try:
            results = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout)
            return [isinstance(result, bool) and result for result in results]
        except asyncio.TimeoutError:
            self.logger.warning(f"Event {event.id} handlers timed out")
            return [False] * len(tasks)
    
    async def _process_events(self) -> None:
        """Process events from the queue."""
        while self.is_running:
            try:
                # Get event from queue
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # Process event
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing events: {e}")
    
    async def _handle_event(self, event: Event) -> None:
        """Handle a single event."""
        subscribers = self.subscribers.get(event.type, [])
        
        if not subscribers:
            self.logger.debug(f"No subscribers for event type {event.type.value}")
            return
        
        # Filter subscribers that should receive this event
        eligible_subscribers = [
            subscriber for subscriber in subscribers
            if self._should_deliver_event(event, subscriber)
        ]
        
        if not eligible_subscribers:
            return
        
        # Process subscribers concurrently with semaphore
        tasks = []
        for subscriber in eligible_subscribers:
            async with self.processing_semaphore:
                task = asyncio.create_task(self._handle_event_safely(event, subscriber))
                tasks.append(task)
        
        # Wait for all handlers
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        success_count = sum(1 for result in results if isinstance(result, bool) and result)
        failure_count = len(results) - success_count
        
        self.stats["events_processed"] += success_count
        self.stats["events_failed"] += failure_count
        
        # Handle failures
        if failure_count > 0:
            await self._handle_event_failures(event, failure_count)
    
    async def _handle_event_safely(self, event: Event, subscriber: EventSubscriber) -> bool:
        """Handle event with error protection."""
        try:
            return await subscriber.handle_event(event)
        except Exception as e:
            self.logger.error(f"Subscriber {subscriber.subscriber_id} failed to handle event {event.id}: {e}")
            return False
    
    def _should_deliver_event(self, event: Event, subscriber: EventSubscriber) -> bool:
        """Check if event should be delivered to subscriber."""
        # Check if targeted
        if event.target and event.target != subscriber.subscriber_id:
            return False
        
        # Check if subscriber handles this event type
        return event.type in subscriber.subscriptions
    
    async def _handle_event_failures(self, event: Event, failure_count: int) -> None:
        """Handle event processing failures."""
        if event.retry_count < event.max_retries:
            # Retry event
            event.retry_count += 1
            self.stats["events_retried"] += 1
            
            # Delay before retry
            await asyncio.sleep(self.config.retry_delay_seconds * event.retry_count)
            
            # Re-queue event
            await self.event_queue.put(event)
            
            self.logger.warning(f"Retrying event {event.id} (attempt {event.retry_count}/{event.max_retries})")
        else:
            # Move to dead letter queue
            self.dead_letter_queue.append(event)
            self.logger.error(f"Event {event.id} moved to dead letter queue after {event.max_retries} retries")
    
    def get_event_history(self, 
                         event_type: Optional[EventType] = None, 
                         source: Optional[str] = None, 
                         limit: int = 100) -> List[Event]:
        """Get event history with filtering."""
        events = list(self.event_history)
        
        # Apply filters
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        if source:
            events = [e for e in events if e.source == source]
        
        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            **self.stats,
            "queue_size": self.event_queue.qsize(),
            "dead_letter_queue_size": len(self.dead_letter_queue),
            "event_history_size": len(self.event_history),
            "event_types_with_subscribers": len([
                event_type for event_type, subscribers in self.subscribers.items()
                if subscribers
            ])
        }
    
    def get_subscribers_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all subscribers."""
        return {
            subscriber_id: {
                "subscriptions": [event_type.value for event_type in subscriber.subscriptions],
                "subscription_count": len(subscriber.subscriptions)
            }
            for subscriber_id, subscriber in self.subscriber_registry.items()
        }


class WorkflowEventSubscriber(EventSubscriber):
    """Event subscriber for workflow-related events."""
    
    def __init__(self, subscriber_id: str):
        super().__init__(subscriber_id)
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{subscriber_id}")
    
    async def handle_event(self, event: Event) -> bool:
        """Handle workflow events."""
        try:
            if event.type == EventType.WORKFLOW_STARTED:
                await self._handle_workflow_started(event)
            elif event.type == EventType.WORKFLOW_COMPLETED:
                await self._handle_workflow_completed(event)
            elif event.type == EventType.WORKFLOW_FAILED:
                await self._handle_workflow_failed(event)
            else:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling event {event.id}: {e}")
            return False
    
    async def _handle_workflow_started(self, event: Event) -> None:
        """Handle workflow started event."""
        workflow_id = event.data.get("workflow_id")
        if workflow_id:
            self.active_workflows[workflow_id] = {
                "started_at": event.timestamp,
                "status": "running",
                "events": [event.id]
            }
            self.logger.info(f"Tracking workflow {workflow_id}")
    
    async def _handle_workflow_completed(self, event: Event) -> None:
        """Handle workflow completed event."""
        workflow_id = event.data.get("workflow_id")
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["completed_at"] = event.timestamp
            self.active_workflows[workflow_id]["events"].append(event.id)
            self.logger.info(f"Workflow {workflow_id} completed")
    
    async def _handle_workflow_failed(self, event: Event) -> None:
        """Handle workflow failed event."""
        workflow_id = event.data.get("workflow_id")
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["failed_at"] = event.timestamp
            self.active_workflows[workflow_id]["error"] = event.data.get("error", "Unknown error")
            self.active_workflows[workflow_id]["events"].append(event.id)
            self.logger.error(f"Workflow {workflow_id} failed: {event.data.get('error')}")


# Global event bus instance
global_event_bus: Optional[EventBus] = None


async def initialize_event_bus(config: EventBusConfig = None) -> EventBus:
    """Initialize global event bus."""
    global global_event_bus
    global_event_bus = EventBus(config)
    await global_event_bus.start()
    return global_event_bus


def get_event_bus() -> Optional[EventBus]:
    """Get global event bus instance."""
    return global_event_bus


# Convenience functions for common events
async def publish_workflow_event(event_type: EventType, workflow_id: str, data: Dict[str, Any] = None) -> str:
    """Publish a workflow-related event."""
    if not global_event_bus:
        raise RuntimeError("Event bus not initialized")
    
    event_data = {"workflow_id": workflow_id}
    if data:
        event_data.update(data)
    
    event = Event(
        type=event_type,
        source="workflow_system",
        data=event_data,
        priority=Priority.MEDIUM
    )
    
    return await global_event_bus.publish(event)


async def publish_agent_event(event_type: EventType, agent_id: str, data: Dict[str, Any] = None) -> str:
    """Publish an agent-related event."""
    if not global_event_bus:
        raise RuntimeError("Event bus not initialized")
    
    event_data = {"agent_id": agent_id}
    if data:
        event_data.update(data)
    
    event = Event(
        type=event_type,
        source=agent_id,
        data=event_data,
        priority=Priority.MEDIUM
    )
    
    return await global_event_bus.publish(event)
