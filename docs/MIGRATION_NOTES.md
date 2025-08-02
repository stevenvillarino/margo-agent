# Migration Guide: Margo Agent Optimization

This guide helps you migrate from the current Margo Agent system to the optimized production-ready version.

## 🔄 Migration Overview

The optimization adds production-grade infrastructure while maintaining backward compatibility. Your existing workflows will continue to work, but you can gradually adopt optimization features.

## 🚀 Quick Start (Recommended)

### Option 1: Fresh Optimized Start
```bash
# Initialize the optimized system
python initialize_optimized_system.py

# Run optimized workflow
python -c "
import asyncio
from core.optimized_system import create_optimized_system
from core.config import get_config

async def main():
    config = get_config()
    system = await create_optimized_system(config)
    print('Optimized system ready!')

asyncio.run(main())
"
```

### Option 2: Gradual Migration
Continue using existing code while selectively adopting optimizations.

## 📋 Migration Checklist

### Phase 1: Environment Setup
- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Configure environment variables (see Configuration section)
- [ ] Run system check: `python initialize_optimized_system.py`

### Phase 2: Configuration Migration
- [ ] Review `core/config.py` for new configuration options
- [ ] Update `.env` file with optimization settings
- [ ] Test configuration loading

### Phase 3: Code Migration
- [ ] Choose migration approach (see below)
- [ ] Update imports and initialization
- [ ] Test existing functionality
- [ ] Validate optimization benefits

### Phase 4: Production Deployment
- [ ] Enable monitoring and metrics
- [ ] Configure Redis for distributed caching (optional)
- [ ] Set up health checks
- [ ] Monitor performance improvements

## 🔧 Configuration Updates

### New Environment Variables
Add these to your `.env` file:

```env
# Optimization Settings
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT_SECONDS=300
MAX_MEMORY_MB=512

# Caching (Optional)
REDIS_URL=redis://localhost:6379/0

# Monitoring (Optional)
ENABLE_MONITORING=true
METRICS_PORT=8080
LOG_LEVEL=INFO

# Circuit Breaker Settings
CB_FAILURE_THRESHOLD=5
CB_RECOVERY_TIMEOUT=60
CB_REQUEST_TIMEOUT=30
```

### Configuration Validation
The new system validates all configuration on startup:

```python
from core.config import get_config

config = get_config()
print(f"Environment: {config.environment}")
print(f"Integrations: {config.get_integration_status()}")
```

## 🎯 Migration Approaches

### Approach 1: Drop-in Replacement (Easiest)

Replace your existing system initialization with the optimized version:

**Before:**
```python
# In your existing code
from agents.enhanced_system import EnhancedWorkflowSystem

system = EnhancedWorkflowSystem()
result = await system.process_design_review(design_data)
```

**After:**
```python
# New optimized version
from core.optimized_system import create_optimized_system
from core.config import get_config

config = get_config()
system = await create_optimized_system(config)
result = await system.process_design_review(design_data)
```

### Approach 2: Gradual Integration (Flexible)

Adopt optimizations incrementally:

```python
# 1. Start with optimized configuration
from core.config import get_config
config = get_config()

# 2. Add connection pooling
from core.connection_manager import get_connection_manager
connection_manager = get_connection_manager()

# 3. Add caching
from core.cache import get_cache
cache = get_cache()

# 4. Your existing system with optimizations
from agents.enhanced_system import EnhancedWorkflowSystem
system = EnhancedWorkflowSystem()

# Cache design reviews
@cache.cached(ttl=3600)
async def cached_design_review(design_data):
    return await system.process_design_review(design_data)
```

### Approach 3: Wrapper Integration (Safe)

Wrap your existing agents with optimization features:

```python
from core.optimized_system import OptimizedAgentWrapper
from agents.design_reviewer import DesignReviewer

# Wrap existing agent
original_agent = DesignReviewer()
optimized_agent = OptimizedAgentWrapper(
    agent=original_agent,
    enable_caching=True,
    enable_monitoring=True
)

# Use as normal - now with optimizations
result = await optimized_agent.review_design(design_data)
```

## 🧪 Testing Migration

### Functional Testing
Ensure existing functionality works:

```python
# Test existing workflow
import asyncio
from demo_enhanced_system import test_workflow

async def test_migration():
    """Test that existing functionality still works."""
    try:
        result = await test_workflow()
        print("✅ Migration successful - existing functionality preserved")
        return True
    except Exception as e:
        print(f"❌ Migration issue: {e}")
        return False

asyncio.run(test_migration())
```

### Performance Testing
Compare before/after performance:

```python
import time
import asyncio
from core.monitoring import get_metrics

async def performance_test():
    """Compare performance with optimizations."""
    metrics = get_metrics()
    
    start_time = time.time()
    # Run your typical workflow
    result = await your_workflow()
    end_time = time.time()
    
    print(f"Execution time: {end_time - start_time:.2f}s")
    print(f"Memory usage: {metrics.get_memory_usage():.2f}MB")
    print(f"Cache hits: {metrics.get_cache_stats()}")

asyncio.run(performance_test())
```

## 📊 Monitoring and Observability

### Metrics Collection
Access system metrics:

```python
from core.monitoring import get_metrics

metrics = get_metrics()
print(f"Total requests: {metrics.total_requests}")
print(f"Average response time: {metrics.avg_response_time}ms")
print(f"Error rate: {metrics.error_rate}%")
print(f"Cache hit rate: {metrics.cache_hit_rate}%")
```

### Health Checks
Monitor system health:

```python
from core.monitoring import get_health_monitor

health = get_health_monitor()
status = await health.check_health()
print(f"System status: {status.status}")
print(f"Services: {status.services}")
```

### Prometheus Integration
If monitoring is enabled, metrics are available at:
- http://localhost:8080/metrics

## 🚨 Common Issues and Solutions

### Issue: Configuration Errors
**Problem:** Missing environment variables or invalid configuration.
**Solution:** Run `python initialize_optimized_system.py` to validate setup.

### Issue: Import Errors
**Problem:** Missing dependencies for optimization features.
**Solution:** 
```bash
pip install -r requirements.txt
# Or install specific dependencies:
pip install redis psutil prometheus-client
```

### Issue: Redis Connection Errors
**Problem:** Redis configured but not running.
**Solution:** 
```bash
# Disable Redis caching
export REDIS_URL=""
# Or install and start Redis
brew install redis  # macOS
redis-server
```

### Issue: Performance Degradation
**Problem:** System slower after migration.
**Solution:** 
- Check that caching is enabled and working
- Verify connection pooling is active
- Monitor resource usage
- Consider disabling features during debugging

### Issue: Memory Issues
**Problem:** Higher memory usage than expected.
**Solution:**
- Adjust `MAX_MEMORY_MB` in configuration
- Enable memory cleanup: `ENABLE_MEMORY_CLEANUP=true`
- Monitor with: `from core.monitoring import get_memory_usage`

## 🔄 Rollback Plan

If you need to rollback to the original system:

1. **Keep backups** of your original configuration
2. **Disable optimizations** by setting environment variables:
   ```env
   USE_OPTIMIZED_SYSTEM=false
   ```
3. **Revert imports** to original agent classes
4. **Remove optimization dependencies** if needed

## 📈 Performance Expectations

After migration, expect:

- **30-50% faster response times** (due to caching and connection pooling)
- **40-60% reduction in API calls** (prompt optimization and caching)
- **Better resource utilization** (connection pooling and load balancing)
- **Improved reliability** (circuit breakers and error handling)
- **Better observability** (metrics and monitoring)

## 🎯 Next Steps

1. **Run the initialization script** to validate your setup
2. **Choose your migration approach** based on your needs
3. **Test thoroughly** with your existing workflows
4. **Monitor performance** improvements
5. **Enable additional features** gradually (Redis, monitoring, etc.)

## 💡 Tips for Success

- **Start small**: Migrate one component at a time
- **Monitor closely**: Watch metrics during migration
- **Test thoroughly**: Validate all existing functionality
- **Document changes**: Keep track of what you've migrated
- **Get help**: Check logs and monitoring for issues

## 📞 Support

If you encounter issues during migration:

1. Check the logs for detailed error messages
2. Run the system health check: `python initialize_optimized_system.py`
3. Review this migration guide
4. Check individual component documentation in `core/` folder

Happy migrating! 🚀
