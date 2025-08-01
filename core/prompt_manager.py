"""
Optimized Prompt Management System

Implements intelligent prompt caching, compression, and optimization
to reduce token usage and improve response times.
"""

import asyncio
import hashlib
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from functools import lru_cache
import re
from datetime import datetime, timedelta
import threading


@dataclass
class PromptTemplate:
    """Structured prompt template."""
    name: str
    template: str
    variables: List[str]
    category: str
    estimated_tokens: int
    usage_count: int = 0
    last_used: Optional[datetime] = None
    avg_response_time: float = 0.0
    success_rate: float = 1.0


@dataclass
class PromptOptimization:
    """Prompt optimization configuration."""
    max_length: int = 4000
    compression_enabled: bool = True
    cache_enabled: bool = True
    variable_substitution: bool = True
    auto_formatting: bool = True
    token_estimation_enabled: bool = True


class TokenEstimator:
    """Estimates token count for prompts."""
    
    # Common token patterns and their approximate ratios
    TOKEN_RATIOS = {
        'english': 0.75,  # ~0.75 tokens per character
        'code': 0.85,     # Code is more token-dense
        'json': 0.9,      # JSON is very token-dense
        'xml': 0.8,       # XML has overhead
    }
    
    @staticmethod
    def estimate_tokens(text: str, content_type: str = 'english') -> int:
        """Estimate token count for text."""
        if not text:
            return 0
        
        ratio = TokenEstimator.TOKEN_RATIOS.get(content_type, 0.75)
        base_estimate = int(len(text) * ratio)
        
        # Adjust for special patterns
        if '{' in text and '}' in text:
            # Template variables reduce effective token count
            variable_count = len(re.findall(r'\{[^}]+\}', text))
            base_estimate -= variable_count * 2
        
        return max(1, base_estimate)
    
    @staticmethod
    def estimate_completion_tokens(prompt_tokens: int, response_type: str = 'detailed') -> int:
        """Estimate expected completion tokens."""
        ratios = {
            'brief': 0.3,
            'standard': 0.7,
            'detailed': 1.2,
            'comprehensive': 2.0
        }
        
        base_ratio = ratios.get(response_type, 0.7)
        return int(prompt_tokens * base_ratio)


class PromptCompressor:
    """Compresses prompts while maintaining meaning."""
    
    # Common replacements for compression
    COMPRESSIONS = {
        'Please analyze': 'Analyze',
        'Please provide': 'Provide',
        'Please review': 'Review',
        'Please evaluate': 'Evaluate',
        'I would like you to': '',
        'Could you please': '',
        'Can you': '',
        'It is important that': '',
        'Make sure to': '',
        'Be sure to': '',
        'Please note that': 'Note:',
        'Please keep in mind': 'Remember:',
        'Additionally,': 'Also,',
        'Furthermore,': 'Also,',
        'In addition,': 'Also,',
        'However,': 'But',
        'Nevertheless,': 'But',
        'Therefore,': 'So',
        'Consequently,': 'So',
        'As a result,': 'So',
    }
    
    @staticmethod
    def compress_prompt(prompt: str, max_compression: float = 0.2) -> str:
        """Compress prompt by removing redundant words."""
        original_length = len(prompt)
        compressed = prompt
        
        # Apply common compressions
        for original, replacement in PromptCompressor.COMPRESSIONS.items():
            compressed = compressed.replace(original, replacement)
        
        # Remove redundant whitespace
        compressed = re.sub(r'\s+', ' ', compressed)
        compressed = re.sub(r'\n\s*\n', '\n', compressed)
        compressed = compressed.strip()
        
        # Check compression ratio
        compression_ratio = 1 - (len(compressed) / original_length)
        if compression_ratio > max_compression:
            # Too much compression, use original
            return prompt
        
        return compressed
    
    @staticmethod
    def smart_truncate(prompt: str, max_tokens: int) -> str:
        """Intelligently truncate prompt to fit token limit."""
        estimated_tokens = TokenEstimator.estimate_tokens(prompt)
        
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Calculate target length
        target_ratio = max_tokens / estimated_tokens
        target_length = int(len(prompt) * target_ratio * 0.95)  # 5% buffer
        
        # Find good truncation points (sentence boundaries)
        sentences = re.split(r'[.!?]\s+', prompt)
        
        truncated = ""
        for sentence in sentences:
            if len(truncated + sentence) <= target_length:
                truncated += sentence + ". "
            else:
                break
        
        return truncated.strip()


class PromptCache:
    """Cache for prompt templates and results."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.templates: Dict[str, PromptTemplate] = {}
        self.rendered_cache: Dict[str, Tuple[str, float]] = {}  # prompt_hash -> (rendered, timestamp)
        self.usage_stats: Dict[str, int] = defaultdict(int)
        self.lock = threading.RLock()
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get prompt template by name."""
        with self.lock:
            template = self.templates.get(name)
            if template:
                template.usage_count += 1
                template.last_used = datetime.now()
                self.usage_stats[name] += 1
            return template
    
    def add_template(self, template: PromptTemplate) -> None:
        """Add prompt template to cache."""
        with self.lock:
            self.templates[template.name] = template
    
    def get_rendered_prompt(self, prompt_hash: str, ttl: int = 3600) -> Optional[str]:
        """Get cached rendered prompt."""
        with self.lock:
            if prompt_hash in self.rendered_cache:
                prompt, timestamp = self.rendered_cache[prompt_hash]
                if time.time() - timestamp < ttl:
                    return prompt
                else:
                    del self.rendered_cache[prompt_hash]
            return None
    
    def cache_rendered_prompt(self, prompt_hash: str, rendered_prompt: str) -> None:
        """Cache rendered prompt."""
        with self.lock:
            # Limit cache size
            if len(self.rendered_cache) >= self.max_size:
                # Remove oldest entries
                oldest_keys = sorted(
                    self.rendered_cache.keys(),
                    key=lambda k: self.rendered_cache[k][1]
                )[:self.max_size // 4]
                
                for key in oldest_keys:
                    del self.rendered_cache[key]
            
            self.rendered_cache[prompt_hash] = (rendered_prompt, time.time())
    
    def get_popular_templates(self, limit: int = 10) -> List[PromptTemplate]:
        """Get most popular templates."""
        with self.lock:
            return sorted(
                self.templates.values(),
                key=lambda t: t.usage_count,
                reverse=True
            )[:limit]
    
    def cleanup_old_entries(self, max_age_hours: int = 24) -> int:
        """Clean up old cache entries."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        removed = 0
        
        with self.lock:
            # Clean rendered cache
            keys_to_remove = [
                key for key, (_, timestamp) in self.rendered_cache.items()
                if timestamp < cutoff_time
            ]
            
            for key in keys_to_remove:
                del self.rendered_cache[key]
                removed += 1
        
        return removed


class PromptManager:
    """Advanced prompt management with optimization and caching."""
    
    def __init__(self, optimization: PromptOptimization = None):
        self.optimization = optimization or PromptOptimization()
        self.cache = PromptCache()
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.render_times: List[float] = []
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Template registry
        self.template_categories: Dict[str, List[str]] = defaultdict(list)
        
        # Start background cleanup
        self._start_cleanup_worker()
    
    def register_template(self, 
                         name: str, 
                         template: str, 
                         variables: List[str], 
                         category: str = "general") -> PromptTemplate:
        """Register a new prompt template."""
        estimated_tokens = TokenEstimator.estimate_tokens(template)
        
        prompt_template = PromptTemplate(
            name=name,
            template=template,
            variables=variables,
            category=category,
            estimated_tokens=estimated_tokens
        )
        
        self.cache.add_template(prompt_template)
        self.template_categories[category].append(name)
        
        self.logger.info(f"Registered template '{name}' ({estimated_tokens} tokens)")
        return prompt_template
    
    def render_prompt(self, 
                     template_name: str, 
                     variables: Dict[str, Any], 
                     optimize: bool = True) -> str:
        """Render prompt template with variables."""
        start_time = time.time()
        
        # Get template
        template = self.cache.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Generate cache key
        cache_key = self._generate_cache_key(template_name, variables)
        
        # Check cache
        if self.optimization.cache_enabled:
            cached_prompt = self.cache.get_rendered_prompt(cache_key)
            if cached_prompt:
                self.cache_hits += 1
                return cached_prompt
        
        self.cache_misses += 1
        
        # Render template
        rendered = template.template
        
        # Variable substitution
        if self.optimization.variable_substitution:
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in rendered:
                    rendered = rendered.replace(placeholder, str(var_value))
        
        # Apply optimizations
        if optimize and self.optimization.compression_enabled:
            rendered = PromptCompressor.compress_prompt(rendered)
        
        # Auto-formatting
        if self.optimization.auto_formatting:
            rendered = self._auto_format(rendered)
        
        # Ensure within length limits
        if self.optimization.max_length > 0:
            estimated_tokens = TokenEstimator.estimate_tokens(rendered)
            if estimated_tokens > self.optimization.max_length:
                rendered = PromptCompressor.smart_truncate(rendered, self.optimization.max_length)
        
        # Cache result
        if self.optimization.cache_enabled:
            self.cache.cache_rendered_prompt(cache_key, rendered)
        
        # Track performance
        render_time = time.time() - start_time
        self.render_times.append(render_time)
        
        # Keep only recent render times
        if len(self.render_times) > 1000:
            self.render_times = self.render_times[-500:]
        
        return rendered
    
    def create_dynamic_prompt(self, 
                            base_template: str, 
                            context: Dict[str, Any], 
                            focus_areas: List[str] = None) -> str:
        """Create optimized prompt dynamically."""
        
        # Build prompt sections
        sections = [base_template]
        
        # Add context if provided
        if context:
            context_section = self._build_context_section(context)
            if context_section:
                sections.append(context_section)
        
        # Add focus areas
        if focus_areas:
            focus_section = self._build_focus_section(focus_areas)
            sections.append(focus_section)
        
        # Combine sections
        full_prompt = "\n\n".join(sections)
        
        # Optimize
        if self.optimization.compression_enabled:
            full_prompt = PromptCompressor.compress_prompt(full_prompt)
        
        # Ensure token limits
        if self.optimization.max_length > 0:
            full_prompt = PromptCompressor.smart_truncate(full_prompt, self.optimization.max_length)
        
        return full_prompt
    
    def estimate_cost(self, template_name: str, variables: Dict[str, Any], 
                     model: str = "gpt-4", response_type: str = "standard") -> Dict[str, Any]:
        """Estimate token usage and cost for prompt."""
        
        # Model pricing (tokens per dollar)
        pricing = {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},  # per 1K tokens
            "gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002},
        }
        
        if model not in pricing:
            model = "gpt-4"  # Default to most expensive
        
        # Render prompt
        rendered_prompt = self.render_prompt(template_name, variables, optimize=True)
        
        # Estimate tokens
        prompt_tokens = TokenEstimator.estimate_tokens(rendered_prompt)
        completion_tokens = TokenEstimator.estimate_completion_tokens(prompt_tokens, response_type)
        total_tokens = prompt_tokens + completion_tokens
        
        # Calculate cost
        prompt_cost = (prompt_tokens / 1000) * pricing[model]["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing[model]["completion"]
        total_cost = prompt_cost + completion_cost
        
        return {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "prompt_cost": prompt_cost,
            "completion_cost": completion_cost,
            "total_cost": total_cost,
            "response_type": response_type
        }
    
    def get_optimization_suggestions(self, template_name: str) -> List[str]:
        """Get suggestions for optimizing a template."""
        template = self.cache.get_template(template_name)
        if not template:
            return ["Template not found"]
        
        suggestions = []
        
        # Token count suggestions
        if template.estimated_tokens > 2000:
            suggestions.append("Consider breaking into smaller templates")
        
        # Usage-based suggestions
        if template.usage_count > 100 and template.avg_response_time > 5.0:
            suggestions.append("High usage template with slow response - consider optimization")
        
        # Content analysis
        if "please" in template.template.lower():
            suggestions.append("Remove politeness words to reduce token count")
        
        if len(re.findall(r'\{[^}]+\}', template.template)) > 10:
            suggestions.append("Too many variables - consider simplifying")
        
        return suggestions
    
    def _generate_cache_key(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Generate cache key for rendered prompt."""
        var_str = json.dumps(variables, sort_keys=True, default=str)
        content = f"{template_name}:{var_str}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _auto_format(self, prompt: str) -> str:
        """Apply automatic formatting improvements."""
        # Remove excessive whitespace
        prompt = re.sub(r'\n\s*\n\s*\n', '\n\n', prompt)
        prompt = re.sub(r' +', ' ', prompt)
        
        # Ensure proper sentence spacing
        prompt = re.sub(r'\.([A-Z])', r'. \1', prompt)
        
        # Clean up list formatting
        prompt = re.sub(r'\n\s*-\s*', '\n- ', prompt)
        
        return prompt.strip()
    
    def _build_context_section(self, context: Dict[str, Any]) -> str:
        """Build context section for dynamic prompts."""
        if not context:
            return ""
        
        lines = ["**Context:**"]
        for key, value in context.items():
            if value:
                key_formatted = key.replace('_', ' ').title()
                lines.append(f"- {key_formatted}: {value}")
        
        return "\n".join(lines) if len(lines) > 1 else ""
    
    def _build_focus_section(self, focus_areas: List[str]) -> str:
        """Build focus areas section."""
        if not focus_areas:
            return ""
        
        lines = ["**Focus Areas:**"]
        for area in focus_areas:
            lines.append(f"- {area}")
        
        return "\n".join(lines)
    
    def _start_cleanup_worker(self):
        """Start background cleanup worker."""
        def cleanup_worker():
            while True:
                try:
                    # Clean up old cache entries every hour
                    removed = self.cache.cleanup_old_entries()
                    if removed > 0:
                        self.logger.info(f"Cleaned up {removed} old cache entries")
                    
                    time.sleep(3600)  # 1 hour
                except Exception as e:
                    self.logger.error(f"Cleanup worker error: {e}")
                    time.sleep(3600)
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        avg_render_time = sum(self.render_times) / len(self.render_times) if self.render_times else 0
        cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        
        return {
            "average_render_time": avg_render_time,
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "total_templates": len(self.cache.templates),
            "popular_templates": [t.name for t in self.cache.get_popular_templates(5)]
        }


# Global prompt manager instance
global_prompt_manager: Optional[PromptManager] = None


def initialize_prompt_manager(optimization: PromptOptimization = None) -> PromptManager:
    """Initialize global prompt manager."""
    global global_prompt_manager
    global_prompt_manager = PromptManager(optimization)
    return global_prompt_manager


def get_prompt_manager() -> Optional[PromptManager]:
    """Get global prompt manager."""
    return global_prompt_manager
