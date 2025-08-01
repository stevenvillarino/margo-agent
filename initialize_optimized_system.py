#!/usr/bin/env python3
"""
Optimized VP of Design Agent System Initialization

This script initializes and configures all optimized components
for production deployment.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import optimization components
from core.config import SystemConfig, ConfigurationManager
from core.memory_manager import MemoryManager, MemoryConfig
from core.connection_manager import ConnectionManager
from core.cache import initialize_cache, CacheConfig
from core.prompt_manager import initialize_prompt_manager, PromptOptimization
from core.event_bus import initialize_event_bus, EventBusConfig
from core.monitoring import initialize_monitoring, MetricConfig
from core.optimized_system import create_optimized_system


async def initialize_system() -> bool:
    """Initialize the complete optimized system."""
    
    print("🚀 Initializing Optimized VP of Design Agent System...")
    
    try:
        # 1. Load and validate configuration
        print("📋 Loading configuration...")
        config_manager = ConfigurationManager()
        config = config_manager.load_config()
        
        # Validate required integrations
        missing = config_manager.validate_required_integrations(['openai'])
        if missing:
            print(f"❌ Missing required integrations: {', '.join(missing)}")
            return False
        
        print(f"✅ Configuration loaded - Environment: {config.environment}")
        
        # 2. Initialize memory management
        print("🧠 Initializing memory management...")
        memory_config = MemoryConfig(
            max_conversation_tokens=config.max_memory_mb * 100,  # Rough estimate
            max_conversation_messages=50,
            max_memory_mb=config.max_memory_mb
        )
        # Memory manager is global, already initialized
        print("✅ Memory management initialized")
        
        # 3. Initialize caching
        print("💾 Initializing caching system...")
        cache_config = CacheConfig(
            redis_url=config.redis_url,
            local_cache_size=128,
            default_ttl=3600,
            enable_redis_cache=bool(config.redis_url),
            enable_local_cache=True
        )
        cache = initialize_cache(cache_config)
        print("✅ Caching system initialized")
        
        # 4. Initialize prompt optimization
        print("📝 Initializing prompt optimization...")
        prompt_config = PromptOptimization(
            max_length=4000,
            compression_enabled=True,
            cache_enabled=True,
            variable_substitution=True,
            auto_formatting=True
        )
        prompt_manager = initialize_prompt_manager(prompt_config)
        print("✅ Prompt optimization initialized")
        
        # 5. Initialize event bus
        print("📡 Initializing event bus...")
        event_config = EventBusConfig(
            max_event_history=10000,
            retry_delay_seconds=1.0,
            max_concurrent_handlers=config.max_concurrent_agents * 2
        )
        event_bus = await initialize_event_bus(event_config)
        print("✅ Event bus initialized")
        
        # 6. Initialize monitoring
        print("📊 Initializing monitoring system...")
        monitoring_config = MetricConfig(
            enable_prometheus=config.enable_monitoring,
            metrics_port=config.metrics_port,
            collection_interval=60,
            enable_system_metrics=True
        )
        monitoring = await initialize_monitoring(monitoring_config)
        print("✅ Monitoring system initialized")
        
        # 7. Create optimized workflow system
        print("🤖 Creating optimized workflow system...")
        optimized_system = await create_optimized_system(config)
        print("✅ Optimized workflow system created")
        
        # 8. Display system status
        print("\n📈 System Status:")
        integrations = config.get_integration_status()
        for integration, status in integrations.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {integration.title()}: {'Enabled' if status else 'Disabled'}")
        
        print(f"\n🎯 Optimization Features:")
        print(f"   ✅ Memory Management: Bounded conversations, automatic cleanup")
        print(f"   ✅ Connection Pooling: HTTP connection reuse")
        print(f"   ✅ Circuit Breakers: Fault tolerance for external APIs")
        print(f"   ✅ Distributed Caching: {'Redis + Local' if config.redis_url else 'Local only'}")
        print(f"   ✅ Prompt Optimization: Compression and caching")
        print(f"   ✅ Event-Driven Architecture: Decoupled agent communication")
        print(f"   ✅ Load Balancing: Agent resource management")
        print(f"   ✅ Monitoring: {'Prometheus + Health checks' if config.enable_monitoring else 'Basic'}")
        
        print(f"\n🔧 Performance Settings:")
        print(f"   • Max Concurrent Agents: {config.max_concurrent_agents}")
        print(f"   • Agent Timeout: {config.agent_timeout_seconds}s")
        print(f"   • Memory Limit: {config.max_memory_mb}MB")
        print(f"   • Cache TTL: {cache_config.default_ttl}s")
        
        print(f"\n🌐 API Endpoints:")
        if config.enable_monitoring:
            print(f"   • Metrics: http://localhost:{config.metrics_port}/metrics")
        print(f"   • Health Check: Available via monitoring system")
        
        print("\n🎉 Optimized VP of Design Agent System ready!")
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        logging.exception("System initialization error")
        return False


def run_system_check():
    """Run comprehensive system check."""
    
    print("🔍 Running System Health Check...")
    
    try:
        # Check Python version
        import sys
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check required environment variables
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("   Please update your .env file with valid API keys")
            return False
        print(f"✅ Required environment variables configured")
        
        # Check optional dependencies
        optional_deps = {
            'redis': 'Redis caching',
            'psutil': 'System monitoring',
            'prometheus_client': 'Metrics collection'
        }
        
        for dep, description in optional_deps.items():
            try:
                __import__(dep)
                print(f"✅ {description}: Available")
            except ImportError:
                print(f"⚠️  {description}: Not available (install {dep} for enhanced features)")
        
        # Test configuration loading
        try:
            from core.config import get_config
            config = get_config()
            print(f"✅ Configuration: Loaded successfully")
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return False
        
        print("\n✅ System check passed!")
        return True
        
    except Exception as e:
        print(f"❌ System check failed: {e}")
        return False


async def main():
    """Main initialization function."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("🎨 VP OF DESIGN AGENT - OPTIMIZED SYSTEM INITIALIZATION")
    print("=" * 60)
    
    # Run system check
    if not run_system_check():
        print("\n❌ System check failed. Please fix the issues above.")
        return False
    
    print("\n" + "=" * 60)
    
    # Initialize system
    success = await initialize_system()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 SYSTEM READY FOR PRODUCTION")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start the Streamlit app: streamlit run app.py")
        print("2. Or run advanced workflow: python demo_enhanced_system.py")
        print("3. Monitor metrics at: http://localhost:8080/metrics")
        print("4. Check logs for any warnings or errors")
        return True
    else:
        print("\n❌ System initialization failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
