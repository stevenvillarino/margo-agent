"""
Enhanced Configuration Management

Centralized, validated configuration system with environment-based settings
and runtime validation.
"""

import os
from typing import Dict, Any, Optional, List, Union, Literal
from dataclasses import dataclass, field
from pydantic import validator, Field
from pydantic_settings import BaseSettings
from enum import Enum
import json
import logging


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AgentType(Enum):
    """Agent types."""
    DESIGN_REVIEWER = "design_reviewer"
    ACCESSIBILITY_CHECKER = "accessibility_checker"
    VP_DESIGN_AGENT = "vp_design_agent"


@dataclass
class AgentConfig:
    """Configuration for individual agents."""
    max_concurrent: int = 3
    timeout_seconds: int = 30
    retry_attempts: int = 3
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    temperature: float = 0.3
    max_tokens: int = 1500


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    redis_url: Optional[str] = None
    local_cache_size: int = 128
    ttl_seconds: int = 3600
    prefix: str = "vp_design_cache"


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    enabled: bool = True
    metrics_port: int = 8080
    log_level: LogLevel = LogLevel.INFO
    enable_tracing: bool = False
    jaeger_endpoint: Optional[str] = None


class SystemConfig(BaseSettings):
    """Main system configuration with validation."""
    
    # Project Info
    project_name: str = Field(default="vp-design-agent", env="PROJECT_NAME")
    project_key: str = Field(default="VPDESIGN", env="PROJECT_KEY")
    environment: Literal["development", "staging", "production"] = "development"
    
    # Core API Keys (Required)
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # Optional API Keys
    exa_api_key: Optional[str] = Field(None, env="EXA_API_KEY")
    slack_bot_token: Optional[str] = Field(None, env="SLACK_BOT_TOKEN")
    slack_app_token: Optional[str] = Field(None, env="SLACK_APP_TOKEN")
    slack_signing_secret: Optional[str] = Field(None, env="SLACK_SIGNING_SECRET")
    
    # JIRA Configuration
    jira_url: Optional[str] = Field(None, env="JIRA_URL")
    jira_username: Optional[str] = Field(None, env="JIRA_USERNAME")
    jira_api_token: Optional[str] = Field(None, env="JIRA_API_TOKEN")
    jira_project_key: str = Field("VPDESIGN", env="JIRA_PROJECT_KEY")
    
    # Figma Configuration
    figma_access_token: Optional[str] = Field(None, env="FIGMA_ACCESS_TOKEN")
    
    # Confluence Configuration
    confluence_url: Optional[str] = Field(None, env="CONFLUENCE_URL")
    confluence_username: Optional[str] = Field(None, env="CONFLUENCE_USERNAME")
    confluence_api_key: Optional[str] = Field(None, env="CONFLUENCE_API_KEY")
    
    # System Performance
    max_concurrent_agents: int = Field(5, env="MAX_CONCURRENT_AGENTS")
    agent_timeout_seconds: int = Field(30, env="AGENT_TIMEOUT_SECONDS")
    max_memory_mb: int = Field(512, env="MAX_MEMORY_MB")
    enable_parallel_processing: bool = Field(True, env="ENABLE_PARALLEL_PROCESSING")
    
    # Cache Configuration
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    cache_enabled: bool = Field(True, env="CACHE_ENABLED")
    cache_ttl_seconds: int = Field(3600, env="CACHE_TTL_SECONDS")
    
    # Monitoring
    enable_monitoring: bool = Field(True, env="ENABLE_MONITORING")
    metrics_port: int = Field(8080, env="METRICS_PORT")
    log_level: LogLevel = Field(LogLevel.INFO, env="LOG_LEVEL")
    
    # Agent-specific configurations
    agent_configs: Dict[str, AgentConfig] = field(default_factory=dict)
    
    class Config:
        env_file = '.env'
        case_sensitive = False
        use_enum_values = True
    
    @validator('max_concurrent_agents')
    def validate_concurrency(cls, v):
        if v < 1 or v > 20:
            raise ValueError('max_concurrent_agents must be between 1 and 20')
        return v
    
    @validator('agent_timeout_seconds')
    def validate_timeout(cls, v):
        if v < 5 or v > 300:
            raise ValueError('agent_timeout_seconds must be between 5 and 300')
        return v
    
    @validator('max_memory_mb')
    def validate_memory(cls, v):
        if v < 128 or v > 8192:
            raise ValueError('max_memory_mb must be between 128 and 8192')
        return v
    
    @validator('openai_api_key')
    def validate_openai_key(cls, v):
        if not v or v == "your_openai_api_key_here":
            raise ValueError('Valid OpenAI API key is required')
        if not v.startswith('sk-'):
            raise ValueError('OpenAI API key must start with "sk-"')
        return v
    
    def __post_init__(self):
        """Initialize agent configurations after main config is loaded."""
        if not self.agent_configs:
            self.agent_configs = self._get_default_agent_configs()
    
    def _get_default_agent_configs(self) -> Dict[str, AgentConfig]:
        """Get default configurations for all agents."""
        return {
            AgentType.UI_SPECIALIST: AgentConfig(
                max_concurrent=3,
                timeout_seconds=45,
                temperature=0.3,
                max_tokens=2000
            ),
            AgentType.UX_RESEARCHER: AgentConfig(
                max_concurrent=2,
                timeout_seconds=60,
                temperature=0.4,
                max_tokens=2500
            ),
            AgentType.CREATIVE_DIRECTOR: AgentConfig(
                max_concurrent=2,
                timeout_seconds=50,
                temperature=0.5,
                max_tokens=2000
            ),
            AgentType.VP_PRODUCT: AgentConfig(
                max_concurrent=1,
                timeout_seconds=90,
                temperature=0.2,
                max_tokens=3000
            ),
            AgentType.ACCESSIBILITY_EXPERT: AgentConfig(
                max_concurrent=2,
                timeout_seconds=40,
                temperature=0.2,
                max_tokens=1800
            ),
            AgentType.QUALITY_EVALUATOR: AgentConfig(
                max_concurrent=2,
                timeout_seconds=35,
                temperature=0.1,
                max_tokens=1500
            ),
            AgentType.VP_DESIGN_AGENT: AgentConfig(
                max_concurrent=1,
                timeout_seconds=120,
                temperature=0.1,
                max_tokens=4000
            )
        }
    
    def get_agent_config(self, agent_type: Union[str, AgentType]) -> AgentConfig:
        """Get configuration for a specific agent."""
        agent_key = agent_type if isinstance(agent_type, str) else agent_type.value
        return self.agent_configs.get(agent_key, AgentConfig())
    
    def is_slack_configured(self) -> bool:
        """Check if Slack integration is properly configured."""
        return all([
            self.slack_bot_token,
            self.slack_app_token,
            self.slack_signing_secret,
            self.slack_bot_token != "xoxb-your-slack-bot-token",
            self.slack_app_token != "xapp-your-slack-app-token",
            self.slack_signing_secret != "your-slack-signing-secret"
        ])
    
    def is_jira_configured(self) -> bool:
        """Check if JIRA integration is properly configured."""
        return all([
            self.jira_url,
            self.jira_username,
            self.jira_api_token,
            self.jira_url != "https://your-company.atlassian.net",
            self.jira_username != "your_email@company.com",
            "atlassian.net" in (self.jira_url or "")
        ])
    
    def is_exa_configured(self) -> bool:
        """Check if EXA research is properly configured."""
        return bool(
            self.exa_api_key and 
            self.exa_api_key != "your_exa_api_key_here"
        )
    
    def is_figma_configured(self) -> bool:
        """Check if Figma integration is properly configured."""
        return bool(
            self.figma_access_token and 
            self.figma_access_token != "your_figma_access_token_here" and
            len(self.figma_access_token) > 20
        )
    
    def is_confluence_configured(self) -> bool:
        """Check if Confluence integration is properly configured."""
        return all([
            self.confluence_url,
            self.confluence_username,
            self.confluence_api_key,
            self.confluence_url != "https://your-domain.atlassian.net",
            self.confluence_username != "your_email@domain.com",
            "atlassian.net" in (self.confluence_url or "")
        ])
    
    def get_cache_config(self):
        """Get cache configuration compatible with core.cache.CacheConfig."""
        from core.cache import CacheConfig as DistributedCacheConfig
        return DistributedCacheConfig(
            redis_url=self.redis_url,
            local_cache_size=128,
            default_ttl=self.cache_ttl_seconds,
            prefix=f"{self.project_key.lower()}_cache",
            enable_local_cache=True,
            enable_redis_cache=bool(self.redis_url)
        )
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        return MonitoringConfig(
            enabled=self.enable_monitoring,
            metrics_port=self.metrics_port,
            log_level=self.log_level
        )
    
    def get_integration_status(self) -> Dict[str, bool]:
        """Get status of all integrations."""
        return {
            "openai": bool(self.openai_api_key),
            "slack": self.is_slack_configured(),
            "jira": self.is_jira_configured(),
            "exa": self.is_exa_configured(),
            "figma": self.is_figma_configured(),
            "confluence": self.is_confluence_configured(),
            "cache": bool(self.redis_url) if self.cache_enabled else False
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        config_dict = self.dict()
        
        # Mask sensitive information
        sensitive_fields = [
            'openai_api_key', 'exa_api_key', 'slack_bot_token', 
            'slack_app_token', 'slack_signing_secret', 'jira_api_token',
            'figma_access_token', 'confluence_api_key'
        ]
        
        for field in sensitive_fields:
            if field in config_dict and config_dict[field]:
                config_dict[field] = f"{config_dict[field][:8]}..." if len(config_dict[field]) > 8 else "***"
        
        return config_dict


class ConfigurationManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file or '.env'
        self.config: Optional[SystemConfig] = None
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> SystemConfig:
        """Load and validate configuration."""
        try:
            # Load configuration
            if self.env_file and os.path.exists(self.env_file):
                self.config = SystemConfig(_env_file=self.env_file)
            else:
                self.config = SystemConfig()
            
            # Post-initialization
            self.config.__post_init__()
            
            # Log configuration status
            integrations = self.config.get_integration_status()
            enabled_integrations = [k for k, v in integrations.items() if v]
            
            self.logger.info(f"Configuration loaded successfully")
            self.logger.info(f"Enabled integrations: {', '.join(enabled_integrations)}")
            
            return self.config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def reload_config(self) -> SystemConfig:
        """Reload configuration from environment."""
        self.config = None
        return self.load_config()
    
    def get_config(self) -> SystemConfig:
        """Get current configuration, loading if necessary."""
        if self.config is None:
            self.load_config()
        return self.config
    
    def validate_required_integrations(self, required: List[str]) -> List[str]:
        """Validate that required integrations are configured."""
        if not self.config:
            self.load_config()
        
        status = self.config.get_integration_status()
        missing = [integration for integration in required if not status.get(integration, False)]
        
        if missing:
            self.logger.warning(f"Missing required integrations: {', '.join(missing)}")
        
        return missing


# Global configuration manager
config_manager = ConfigurationManager()

# Convenience function to get configuration
def get_config() -> SystemConfig:
    """Get the current system configuration."""
    return config_manager.get_config()
