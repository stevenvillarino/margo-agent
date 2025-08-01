"""
Memory Management and Bounded Conversation System

Implements memory-bounded conversation history and efficient state management
to prevent memory leaks and optimize performance.
"""

import json
import time
import threading
from collections import deque
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import psutil
import gc


@dataclass
class MemoryConfig:
    """Configuration for memory management."""
    max_conversation_tokens: int = 4000
    max_conversation_messages: int = 50
    max_memory_mb: int = 512
    cleanup_interval_seconds: int = 300  # 5 minutes
    token_estimation_ratio: float = 0.75  # chars to tokens ratio


class TokenCounter:
    """Efficient token counting for conversations."""
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count from text length."""
        # Rough estimation: ~0.75 tokens per character for English
        return int(len(text) * 0.75)
    
    @staticmethod
    def count_message_tokens(message: Dict[str, Any]) -> int:
        """Count tokens in a message."""
        if isinstance(message, dict):
            text = json.dumps(message)
        else:
            text = str(message)
        return TokenCounter.estimate_tokens(text)


class BoundedConversationMemory:
    """Memory-bounded conversation history with automatic cleanup."""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.messages = deque(maxlen=config.max_conversation_messages)
        self.total_tokens = 0
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message with automatic memory management."""
        with self.lock:
            message_tokens = TokenCounter.count_message_tokens(message)
            
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = datetime.now().isoformat()
            
            # Add message
            self.messages.append(message)
            self.total_tokens += message_tokens
            
            # Cleanup if over limits
            self._cleanup_if_needed()
    
    def get_messages(self, max_tokens: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get messages within token limit."""
        with self.lock:
            if max_tokens is None:
                return list(self.messages)
            
            result = []
            token_count = 0
            
            # Start from most recent messages
            for message in reversed(self.messages):
                msg_tokens = TokenCounter.count_message_tokens(message)
                if token_count + msg_tokens > max_tokens:
                    break
                result.insert(0, message)
                token_count += msg_tokens
            
            return result
    
    def get_recent_messages(self, count: int) -> List[Dict[str, Any]]:
        """Get the most recent N messages."""
        with self.lock:
            return list(self.messages)[-count:] if count <= len(self.messages) else list(self.messages)
    
    def clear_old_messages(self, older_than_hours: int = 24) -> int:
        """Clear messages older than specified hours."""
        with self.lock:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            initial_count = len(self.messages)
            
            # Filter out old messages
            filtered_messages = deque(maxlen=self.config.max_conversation_messages)
            total_tokens = 0
            
            for message in self.messages:
                msg_time = datetime.fromisoformat(message.get('timestamp', '2000-01-01'))
                if msg_time > cutoff_time:
                    filtered_messages.append(message)
                    total_tokens += TokenCounter.count_message_tokens(message)
            
            self.messages = filtered_messages
            self.total_tokens = total_tokens
            
            removed_count = initial_count - len(self.messages)
            if removed_count > 0:
                self.logger.info(f"Cleared {removed_count} old messages")
            
            return removed_count
    
    def _cleanup_if_needed(self) -> None:
        """Clean up messages if over limits."""
        # Remove oldest messages if over token limit
        while self.total_tokens > self.config.max_conversation_tokens and self.messages:
            removed_message = self.messages.popleft()
            self.total_tokens -= TokenCounter.count_message_tokens(removed_message)
        
        # Messages are automatically limited by deque maxlen
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        with self.lock:
            return {
                'message_count': len(self.messages),
                'total_tokens': self.total_tokens,
                'max_tokens': self.config.max_conversation_tokens,
                'max_messages': self.config.max_conversation_messages,
                'token_utilization': self.total_tokens / self.config.max_conversation_tokens,
                'message_utilization': len(self.messages) / self.config.max_conversation_messages
            }


class MemoryMonitor:
    """System memory monitoring and cleanup."""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.last_cleanup = time.time()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    
    def should_cleanup(self) -> bool:
        """Check if cleanup is needed."""
        current_time = time.time()
        memory_usage = self.get_memory_usage()
        
        # Time-based cleanup
        if current_time - self.last_cleanup > self.config.cleanup_interval_seconds:
            return True
        
        # Memory-based cleanup
        if memory_usage['rss_mb'] > self.config.max_memory_mb:
            return True
        
        return False
    
    def perform_cleanup(self) -> Dict[str, Any]:
        """Perform memory cleanup."""
        initial_memory = self.get_memory_usage()
        
        # Force garbage collection
        collected = gc.collect()
        
        # Update last cleanup time
        self.last_cleanup = time.time()
        
        final_memory = self.get_memory_usage()
        
        cleanup_stats = {
            'collected_objects': collected,
            'memory_before_mb': initial_memory['rss_mb'],
            'memory_after_mb': final_memory['rss_mb'],
            'memory_saved_mb': initial_memory['rss_mb'] - final_memory['rss_mb'],
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Memory cleanup completed: {cleanup_stats}")
        return cleanup_stats


class MemoryManager:
    """Central memory management for the entire system."""
    
    def __init__(self, config: MemoryConfig = None):
        self.config = config or MemoryConfig()
        self.conversations: Dict[str, BoundedConversationMemory] = {}
        self.monitor = MemoryMonitor(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Start background cleanup
        self._start_background_cleanup()
    
    def get_conversation_memory(self, conversation_id: str) -> BoundedConversationMemory:
        """Get or create conversation memory for an ID."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = BoundedConversationMemory(self.config)
        return self.conversations[conversation_id]
    
    def cleanup_inactive_conversations(self, inactive_hours: int = 24) -> int:
        """Remove inactive conversations."""
        cutoff_time = datetime.now() - timedelta(hours=inactive_hours)
        inactive_ids = []
        
        for conv_id, memory in self.conversations.items():
            if not memory.messages:
                inactive_ids.append(conv_id)
                continue
            
            # Check last message timestamp
            last_message = memory.messages[-1]
            last_time = datetime.fromisoformat(last_message.get('timestamp', '2000-01-01'))
            
            if last_time < cutoff_time:
                inactive_ids.append(conv_id)
        
        # Remove inactive conversations
        for conv_id in inactive_ids:
            del self.conversations[conv_id]
        
        if inactive_ids:
            self.logger.info(f"Cleaned up {len(inactive_ids)} inactive conversations")
        
        return len(inactive_ids)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system memory statistics."""
        memory_usage = self.monitor.get_memory_usage()
        
        conversation_stats = {
            'total_conversations': len(self.conversations),
            'total_messages': sum(len(conv.messages) for conv in self.conversations.values()),
            'total_tokens': sum(conv.total_tokens for conv in self.conversations.values())
        }
        
        return {
            'memory_usage': memory_usage,
            'conversations': conversation_stats,
            'config': asdict(self.config),
            'timestamp': datetime.now().isoformat()
        }
    
    def _start_background_cleanup(self):
        """Start background cleanup process."""
        def cleanup_worker():
            while True:
                try:
                    if self.monitor.should_cleanup():
                        # Perform memory cleanup
                        self.monitor.perform_cleanup()
                        
                        # Clean up old conversations
                        self.cleanup_inactive_conversations()
                        
                        # Clean up old messages in active conversations
                        for memory in self.conversations.values():
                            memory.clear_old_messages()
                    
                    time.sleep(60)  # Check every minute
                
                except Exception as e:
                    self.logger.error(f"Error in background cleanup: {e}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()


# Global memory manager instance
_global_memory_manager = None


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryManager()
    return _global_memory_manager


def initialize_memory_manager(config: MemoryConfig = None) -> MemoryManager:
    """Initialize the global memory manager with custom config."""
    global _global_memory_manager
    _global_memory_manager = MemoryManager(config)
    return _global_memory_manager
