"""
Configuration settings for the Research Manager Workflow
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "claude": {
        "model": "sonnet",
        "output_format": "json",
        "timeout": 300,  # seconds
    },
    "perplexity": {
        "api_key": os.getenv("PERPLEXITY_API_KEY"),
        "model": "llama-3.1-sonar-small-128k-online",
    },
    "workflow": {
        "research_context_file": "research_context.md",
        "default_output_folder": "reports",
        "max_retries": 3,
        "step_delay": 1.0,  # seconds between steps
    },
    "agents": {
        "researcher": {
            "max_sources": 10,
            "search_depth": "comprehensive",
            "verification_level": "high",
        },
        "synthesizer": {
            "framework_type": "hierarchical",
            "connection_strength": "strong",
        },
        "expert_consultant": {
            "domain_focus": "auto-detect",
            "analysis_depth": "deep",
        },
        "fact_checker": {
            "verification_threshold": 0.8,
            "source_reliability_check": True,
        },
        "writer": {
            "technical_depth": "mandatory",
            "code_examples": True,
            "architectural_diagrams": True,
            "performance_metrics": True,
        },
    },
}


class WorkflowConfig:
    """Configuration manager for the research workflow"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self.config = config_dict or DEFAULT_CONFIG.copy()
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration settings"""
        # Claude Code validation - ensure claude command is available
        pass  # Claude Code doesn't require API key validation
    
    def get_claude_config(self) -> Dict[str, Any]:
        """Get Claude configuration"""
        return self.config["claude"]
    
    def get_perplexity_config(self) -> Dict[str, Any]:
        """Get Perplexity configuration"""
        return self.config["perplexity"]
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """Get workflow configuration"""
        return self.config["workflow"]
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        return self.config["agents"].get(agent_name, {})
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        self._deep_update(self.config, updates)
        self._validate_config()
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def save_config(self, filepath: Path):
        """Save configuration to file"""
        import json
        with open(filepath, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    @classmethod
    def load_config(cls, filepath: Path) -> 'WorkflowConfig':
        """Load configuration from file"""
        import json
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        return cls(config_dict)


# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    "claude": {
        "model": "haiku",
        "timeout": 120,
    },
    "workflow": {
        "step_delay": 0.5,
    },
}

PRODUCTION_CONFIG = {
    "claude": {
        "model": "sonnet",
        "timeout": 600,
    },
    "workflow": {
        "max_retries": 5,
        "step_delay": 2.0,
    },
}


def get_config(environment: str = "default") -> WorkflowConfig:
    """Get configuration for specified environment"""
    base_config = DEFAULT_CONFIG.copy()
    
    if environment == "development":
        config = WorkflowConfig(base_config)
        config.update_config(DEVELOPMENT_CONFIG)
    elif environment == "production":
        config = WorkflowConfig(base_config)
        config.update_config(PRODUCTION_CONFIG)
    else:
        config = WorkflowConfig(base_config)
    
    return config