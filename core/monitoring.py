"""
Comprehensive Monitoring and Observability System

Implements metrics collection, tracing, and system health monitoring
for production-ready observability.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import psutil
import gc

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Summary, 
        CollectorRegistry, generate_latest,
        start_http_server, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # Mock prometheus classes if not available
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
    
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
    
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def dec(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
    
    PROMETHEUS_AVAILABLE = False


@dataclass
class MetricConfig:
    """Configuration for metrics collection."""
    enable_prometheus: bool = True
    metrics_port: int = 8080
    collection_interval: int = 60  # seconds
    retention_hours: int = 24
    enable_system_metrics: bool = True
    enable_custom_metrics: bool = True


@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    check_function: Callable[[], bool]
    timeout: float = 5.0
    critical: bool = False
    interval: int = 30  # seconds


class SystemMetrics:
    """System-level metrics collector."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            # System metrics
            self.cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
            self.memory_usage = Gauge('system_memory_usage_bytes', 'Memory usage in bytes')
            self.memory_usage_percent = Gauge('system_memory_usage_percent', 'Memory usage percentage')
            self.disk_usage = Gauge('system_disk_usage_percent', 'Disk usage percentage')
            
            # Application metrics
            self.active_agents = Gauge('vp_design_active_agents_total', 'Number of active agents', ['agent_type'])
            self.request_count = Counter('vp_design_requests_total', 'Total requests', ['agent_type', 'status'])
            self.request_duration = Histogram('vp_design_request_duration_seconds', 'Request duration', ['agent_type'])
            self.cache_hits = Counter('vp_design_cache_hits_total', 'Cache hits', ['cache_type'])
            self.cache_misses = Counter('vp_design_cache_misses_total', 'Cache misses', ['cache_type'])
            
            # Event metrics
            self.events_published = Counter('vp_design_events_published_total', 'Events published', ['event_type'])
            self.events_processed = Counter('vp_design_events_processed_total', 'Events processed', ['event_type'])
            
            # Error metrics
            self.errors_total = Counter('vp_design_errors_total', 'Total errors', ['error_type', 'component'])
            self.circuit_breaker_trips = Counter('vp_design_circuit_breaker_trips_total', 'Circuit breaker trips', ['service'])
        
        # Internal metrics storage
        self.metrics_history: deque = deque(maxlen=10000)
        self.collection_enabled = True
    
    def record_request(self, agent_type: str, duration: float, success: bool):
        """Record a request metric."""
        if PROMETHEUS_AVAILABLE:
            status = 'success' if success else 'error'
            self.request_count.labels(agent_type=agent_type, status=status).inc()
            self.request_duration.labels(agent_type=agent_type).observe(duration)
    
    def record_cache_operation(self, cache_type: str, hit: bool):
        """Record cache operation."""
        if PROMETHEUS_AVAILABLE:
            if hit:
                self.cache_hits.labels(cache_type=cache_type).inc()
            else:
                self.cache_misses.labels(cache_type=cache_type).inc()
    
    def record_event(self, event_type: str, processed: bool = True):
        """Record event metric."""
        if PROMETHEUS_AVAILABLE:
            self.events_published.labels(event_type=event_type).inc()
            if processed:
                self.events_processed.labels(event_type=event_type).inc()
    
    def record_error(self, error_type: str, component: str):
        """Record error metric."""
        if PROMETHEUS_AVAILABLE:
            self.errors_total.labels(error_type=error_type, component=component).inc()
    
    def record_circuit_breaker_trip(self, service: str):
        """Record circuit breaker trip."""
        if PROMETHEUS_AVAILABLE:
            self.circuit_breaker_trips.labels(service=service).inc()
    
    def update_agent_count(self, agent_type: str, count: int):
        """Update active agent count."""
        if PROMETHEUS_AVAILABLE:
            self.active_agents.labels(agent_type=agent_type).set(count)
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                self.cpu_usage.set(cpu_percent)
                self.memory_usage.set(memory.used)
                self.memory_usage_percent.set(memory.percent)
                self.disk_usage.set(disk.percent)
            
            # Store in history
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_used_bytes': memory.used,
                'memory_percent': memory.percent,
                'memory_available_bytes': memory.available,
                'disk_percent': disk.percent,
                'disk_free_bytes': disk.free,
                'process_count': len(psutil.pids())
            }
            
            self.metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        # Calculate averages
        avg_cpu = sum(m['cpu_percent'] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m['memory_percent'] for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m['disk_percent'] for m in recent_metrics) / len(recent_metrics)
        
        return {
            'time_range_hours': hours,
            'sample_count': len(recent_metrics),
            'avg_cpu_percent': avg_cpu,
            'avg_memory_percent': avg_memory,
            'avg_disk_percent': avg_disk,
            'current_memory_gb': recent_metrics[-1]['memory_used_bytes'] / (1024**3),
            'current_disk_free_gb': recent_metrics[-1]['disk_free_bytes'] / (1024**3)
        }


class HealthMonitor:
    """System health monitoring."""
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.is_monitoring = False
        self.logger = logging.getLogger(__name__)
    
    def register_health_check(self, health_check: HealthCheck):
        """Register a health check."""
        self.health_checks[health_check.name] = health_check
        self.health_status[health_check.name] = {
            'status': 'unknown',
            'last_check': None,
            'last_success': None,
            'failure_count': 0,
            'error_message': None
        }
        self.logger.info(f"Registered health check: {health_check.name}")
    
    async def start_monitoring(self):
        """Start health monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        # Start monitoring task for each health check
        for name, check in self.health_checks.items():
            asyncio.create_task(self._monitor_health_check(name, check))
        
        self.logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring."""
        self.is_monitoring = False
        self.logger.info("Health monitoring stopped")
    
    async def _monitor_health_check(self, name: str, check: HealthCheck):
        """Monitor a single health check."""
        while self.is_monitoring:
            try:
                # Run health check with timeout
                start_time = time.time()
                
                try:
                    is_healthy = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, check.check_function
                        ),
                        timeout=check.timeout
                    )
                    
                    duration = time.time() - start_time
                    
                    # Update status
                    self.health_status[name].update({
                        'status': 'healthy' if is_healthy else 'unhealthy',
                        'last_check': datetime.now().isoformat(),
                        'duration': duration,
                        'error_message': None
                    })
                    
                    if is_healthy:
                        self.health_status[name]['last_success'] = datetime.now().isoformat()
                        self.health_status[name]['failure_count'] = 0
                    else:
                        self.health_status[name]['failure_count'] += 1
                
                except asyncio.TimeoutError:
                    self.health_status[name].update({
                        'status': 'timeout',
                        'last_check': datetime.now().isoformat(),
                        'error_message': f'Health check timed out after {check.timeout}s',
                        'failure_count': self.health_status[name]['failure_count'] + 1
                    })
                
                except Exception as e:
                    self.health_status[name].update({
                        'status': 'error',
                        'last_check': datetime.now().isoformat(),
                        'error_message': str(e),
                        'failure_count': self.health_status[name]['failure_count'] + 1
                    })
                
                # Wait before next check
                await asyncio.sleep(check.interval)
                
            except Exception as e:
                self.logger.error(f"Error in health check monitor {name}: {e}")
                await asyncio.sleep(check.interval)
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self.health_status:
            return {'status': 'unknown', 'message': 'No health checks configured'}
        
        critical_checks = [
            name for name, check in self.health_checks.items()
            if check.critical
        ]
        
        critical_failures = [
            name for name in critical_checks
            if self.health_status[name]['status'] not in ['healthy', 'unknown']
        ]
        
        if critical_failures:
            return {
                'status': 'critical',
                'message': f'Critical health checks failing: {", ".join(critical_failures)}',
                'failed_checks': critical_failures
            }
        
        unhealthy_checks = [
            name for name, status in self.health_status.items()
            if status['status'] not in ['healthy', 'unknown']
        ]
        
        if unhealthy_checks:
            return {
                'status': 'degraded',
                'message': f'Some health checks failing: {", ".join(unhealthy_checks)}',
                'failed_checks': unhealthy_checks
            }
        
        return {
            'status': 'healthy',
            'message': 'All health checks passing',
            'total_checks': len(self.health_checks)
        }
    
    def get_health_details(self) -> Dict[str, Any]:
        """Get detailed health status for all checks."""
        return {
            'overall': self.get_overall_health(),
            'checks': self.health_status.copy()
        }


class MonitoringSystem:
    """Main monitoring system coordinator."""
    
    def __init__(self, config: MetricConfig = None):
        self.config = config or MetricConfig()
        self.metrics = SystemMetrics()
        self.health_monitor = HealthMonitor()
        self.logger = logging.getLogger(__name__)
        
        # Metrics server
        self.metrics_server_started = False
        
        # Collection state
        self.is_collecting = False
        self.collection_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start monitoring system."""
        # Start metrics collection
        if self.config.enable_system_metrics:
            await self.start_metrics_collection()
        
        # Start health monitoring
        await self.health_monitor.start_monitoring()
        
        # Start Prometheus metrics server
        if self.config.enable_prometheus and PROMETHEUS_AVAILABLE:
            await self.start_metrics_server()
        
        # Register default health checks
        self._register_default_health_checks()
        
        self.logger.info("Monitoring system started")
    
    async def stop(self):
        """Stop monitoring system."""
        # Stop metrics collection
        await self.stop_metrics_collection()
        
        # Stop health monitoring
        await self.health_monitor.stop_monitoring()
        
        self.logger.info("Monitoring system stopped")
    
    async def start_metrics_collection(self):
        """Start periodic metrics collection."""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        self.collection_task = asyncio.create_task(self._collect_metrics_periodically())
        self.logger.info("Metrics collection started")
    
    async def stop_metrics_collection(self):
        """Stop metrics collection."""
        self.is_collecting = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Metrics collection stopped")
    
    async def start_metrics_server(self):
        """Start Prometheus metrics server."""
        if self.metrics_server_started or not PROMETHEUS_AVAILABLE:
            return
        
        try:
            start_http_server(self.config.metrics_port)
            self.metrics_server_started = True
            self.logger.info(f"Prometheus metrics server started on port {self.config.metrics_port}")
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")
    
    async def _collect_metrics_periodically(self):
        """Periodically collect system metrics."""
        while self.is_collecting:
            try:
                self.metrics.collect_system_metrics()
                await asyncio.sleep(self.config.collection_interval)
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(self.config.collection_interval)
    
    def _register_default_health_checks(self):
        """Register default health checks."""
        # Memory usage check
        def check_memory():
            memory = psutil.virtual_memory()
            return memory.percent < 90  # Alert if memory usage > 90%
        
        # Disk usage check
        def check_disk():
            disk = psutil.disk_usage('/')
            return disk.percent < 95  # Alert if disk usage > 95%
        
        # CPU usage check
        def check_cpu():
            cpu_percent = psutil.cpu_percent(interval=1)
            return cpu_percent < 95  # Alert if CPU usage > 95%
        
        self.health_monitor.register_health_check(
            HealthCheck("memory_usage", check_memory, critical=True, interval=60)
        )
        
        self.health_monitor.register_health_check(
            HealthCheck("disk_usage", check_disk, critical=True, interval=300)
        )
        
        self.health_monitor.register_health_check(
            HealthCheck("cpu_usage", check_cpu, critical=False, interval=60)
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'timestamp': datetime.now().isoformat(),
            'health': self.health_monitor.get_overall_health(),
            'metrics': self.metrics.get_metrics_summary(),
            'monitoring_config': asdict(self.config),
            'prometheus_available': PROMETHEUS_AVAILABLE,
            'metrics_server_running': self.metrics_server_started
        }
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed system status including all health checks."""
        return {
            'timestamp': datetime.now().isoformat(),
            'health_details': self.health_monitor.get_health_details(),
            'metrics_summary': self.metrics.get_metrics_summary(hours=24),
            'system_info': {
                'python_version': psutil.__version__,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3)
            }
        }


# Global monitoring system
global_monitoring: Optional[MonitoringSystem] = None


async def initialize_monitoring(config: MetricConfig = None) -> MonitoringSystem:
    """Initialize global monitoring system."""
    global global_monitoring
    global_monitoring = MonitoringSystem(config)
    await global_monitoring.start()
    return global_monitoring


def get_monitoring() -> Optional[MonitoringSystem]:
    """Get global monitoring system."""
    return global_monitoring


def get_metrics() -> Optional['SystemMetrics']:
    """Get metrics collector from global monitoring system."""
    if global_monitoring:
        return global_monitoring.metrics
    return None


def get_health_monitor() -> Optional['HealthMonitor']:
    """Get health monitor from global monitoring system."""
    if global_monitoring:
        return global_monitoring.health_monitor
    return None


# Convenience functions for metrics
def record_request_metric(agent_type: str, duration: float, success: bool):
    """Record a request metric."""
    if global_monitoring:
        global_monitoring.metrics.record_request(agent_type, duration, success)


def record_cache_metric(cache_type: str, hit: bool):
    """Record a cache metric."""
    if global_monitoring:
        global_monitoring.metrics.record_cache_operation(cache_type, hit)


def record_error_metric(error_type: str, component: str):
    """Record an error metric."""
    if global_monitoring:
        global_monitoring.metrics.record_error(error_type, component)
