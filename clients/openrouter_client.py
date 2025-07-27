"""
OpenRouter API client adapter for replacing Claude Code CLI integration.
Provides unified interface for LLM interactions across all workflow types.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Union
import logging
from openai import OpenAI

from .llm_client import LLMClient, WorkflowType, ModelConfig

logger = logging.getLogger(__name__)


class OpenRouterModels:
    """Recommended models for different workflow types."""
    
    # High-performance models for complex tasks
    CLAUDE_SONNET = ModelConfig(
        name="anthropic/claude-3.5-sonnet",
        max_tokens=8192,
        context_window=200000,
        cost_per_1k_tokens=0.003,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="Best for code analysis, complex reasoning, and development tasks"
    )
    
    GPT4_TURBO = ModelConfig(
        name="openai/gpt-4-turbo",
        max_tokens=4096,
        context_window=128000,
        cost_per_1k_tokens=0.01,
        best_for=[WorkflowType.RESEARCH, WorkflowType.JIRA_TASK],
        description="Excellent for research and comprehensive analysis"
    )
    
    # Cost-effective models for research
    CLAUDE_HAIKU = ModelConfig(
        name="anthropic/claude-3-haiku",
        max_tokens=4096,
        context_window=200000,
        cost_per_1k_tokens=0.00025,
        best_for=[WorkflowType.RESEARCH],
        description="Fast and cost-effective for research and data processing"
    )
    
    # Specialized models
    DEEPSEEK_CODER = ModelConfig(
        name="deepseek/deepseek-coder",
        max_tokens=4096,
        context_window=16000,
        cost_per_1k_tokens=0.00014,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="Specialized for code generation and review"
    )
    
    CLAUDE_SONNET_35 = ModelConfig(
        name="anthropic/claude-3.5-sonnet",
        max_tokens=8192,
        context_window=200000,
        cost_per_1k_tokens=0.003,
        best_for=[WorkflowType.RESEARCH, WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="Excellent for research, code review, and complex reasoning tasks"
    )

    @classmethod
    def get_recommended_models(cls, workflow_type: WorkflowType) -> List[ModelConfig]:
        """Get recommended models for a specific workflow type."""
        all_models = [cls.CLAUDE_SONNET, cls.GPT4_TURBO, cls.CLAUDE_HAIKU, 
                     cls.DEEPSEEK_CODER, cls.CLAUDE_SONNET_35]
        return [model for model in all_models if workflow_type in model.best_for]

    @classmethod
    def get_default_model(cls, workflow_type: WorkflowType) -> ModelConfig:
        """Get the default recommended model for a workflow type."""
        recommendations = {
            WorkflowType.RESEARCH: cls.CLAUDE_SONNET_35,
            WorkflowType.CODE_REVIEW: cls.CLAUDE_SONNET,
            WorkflowType.JIRA_TASK: cls.CLAUDE_SONNET,
            WorkflowType.GENERAL: cls.CLAUDE_HAIKU
        }
        return recommendations.get(workflow_type, cls.CLAUDE_HAIKU)


class OpenRouterClient(LLMClient):
    """
    OpenRouter API client that replaces Claude Code CLI functionality.
    Provides compatibility with existing workflow interfaces.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
        workflow_type: WorkflowType = WorkflowType.GENERAL
    ):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            site_url: Your site URL for OpenRouter leaderboards
            site_name: Your site name for OpenRouter leaderboards  
            workflow_type: Type of workflow for model optimization
        """
        super().__init__(workflow_type)
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY env var or pass api_key parameter.")
        
        self.site_url = site_url or os.getenv("OPENROUTER_SITE_URL", "https://github.com/agent-flows")
        self.site_name = site_name or os.getenv("OPENROUTER_SITE_NAME", "Agent Flows")
        
        # Initialize OpenAI client with OpenRouter endpoint
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        logger.info(f"OpenRouter client initialized for {workflow_type.value} with model {self.default_model.name}")

    def execute_prompt(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        timeout: int = 1800,
        tools: Optional[List[str]] = None,
        working_directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a prompt using OpenRouter API.
        Replaces Claude Code CLI subprocess calls.
        
        Args:
            prompt: The prompt to execute
            model: Model name (defaults to workflow-optimized model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            timeout: Request timeout in seconds
            tools: List of tools (for compatibility - not used in API)
            working_directory: Working directory (for compatibility)
            
        Returns:
            Dict with 'content', 'usage', 'model' keys
        """
        try:
            # Use default model if none specified
            if not model:
                model = self.default_model.name
            
            # Use model's max_tokens if not specified
            if not max_tokens:
                model_config = self._get_model_config(model)
                max_tokens = model_config.max_tokens if model_config else 4096
            
            start_time = time.time()
            
            # Prepare request headers
            extra_headers = {
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name
            }
            
            # Make API request
            response = self.client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }],
                max_tokens=max_tokens,
                temperature=temperature,
                extra_headers=extra_headers,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            # Format response to match Claude Code CLI output format
            result = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "execution_time": execution_time,
                "success": True
            }
            
            logger.info(f"OpenRouter request completed in {execution_time:.2f}s using {model}")
            return result
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "model": model or self.default_model.name,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "execution_time": 0,
                "success": False,
                "error": str(e)
            }

    def _get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model."""
        all_models = [
            OpenRouterModels.CLAUDE_SONNET,
            OpenRouterModels.GPT4_TURBO, 
            OpenRouterModels.CLAUDE_HAIKU,
            OpenRouterModels.DEEPSEEK_CODER,
            OpenRouterModels.CLAUDE_SONNET_35
        ]
        
        for model_config in all_models:
            if model_config.name == model_name:
                return model_config
        return None

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter."""
        try:
            # This would require a separate API call to /api/v1/models
            # For now, return our curated list
            recommended = OpenRouterModels.get_recommended_models(self.workflow_type)
            return [
                {
                    "name": model.name,
                    "max_tokens": model.max_tokens,
                    "context_window": model.context_window,
                    "cost_per_1k_tokens": model.cost_per_1k_tokens,
                    "description": model.description
                }
                for model in recommended
            ]
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            return []
    
    def get_default_model(self, workflow_type: WorkflowType) -> ModelConfig:
        """Get the default recommended model for a workflow type."""
        return OpenRouterModels.get_default_model(workflow_type)

    def estimate_cost(self, prompt: str, model: Optional[str] = None) -> Dict[str, float]:
        """Estimate cost for a prompt execution."""
        if not model:
            model = self.default_model.name
            
        model_config = self._get_model_config(model)
        if not model_config:
            return {"estimated_cost": 0.0, "prompt_tokens": 0}
        
        # Rough token estimation (4 chars = 1 token)
        estimated_tokens = len(prompt) // 4
        estimated_cost = estimated_tokens * model_config.cost_per_1k_tokens / 1000
        
        return {
            "estimated_cost": estimated_cost,
            "prompt_tokens": estimated_tokens,
            "model": model,
            "cost_per_1k_tokens": model_config.cost_per_1k_tokens
        }


# Compatibility functions for easy migration from Claude Code CLI

def create_research_client(api_key: Optional[str] = None) -> OpenRouterClient:
    """Create OpenRouter client optimized for research workflows."""
    return OpenRouterClient(api_key=api_key, workflow_type=WorkflowType.RESEARCH)

def create_code_review_client(api_key: Optional[str] = None) -> OpenRouterClient:
    """Create OpenRouter client optimized for code review workflows.""" 
    return OpenRouterClient(api_key=api_key, workflow_type=WorkflowType.CODE_REVIEW)

def create_jira_task_client(api_key: Optional[str] = None) -> OpenRouterClient:
    """Create OpenRouter client optimized for JIRA task workflows."""
    return OpenRouterClient(api_key=api_key, workflow_type=WorkflowType.JIRA_TASK)


if __name__ == "__main__":
    # Example usage and testing
    print("OpenRouter Client - Available Models by Workflow Type")
    print("=" * 60)
    
    for workflow_type in WorkflowType:
        print(f"\n{workflow_type.value.upper()} Workflow:")
        models = OpenRouterModels.get_recommended_models(workflow_type)
        for model in models:
            print(f"  • {model.name}")
            print(f"    {model.description}")
            print(f"    Cost: ${model.cost_per_1k_tokens:.4f}/1K tokens")
            print()