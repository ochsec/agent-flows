"""
Abstract base class for LLM clients.
Provides a unified interface for different LLM providers (OpenRouter, LM Studio, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """Workflow types with optimized model recommendations."""
    RESEARCH = "research"
    CODE_REVIEW = "code_review" 
    JIRA_TASK = "jira_task"
    GENERAL = "general"


@dataclass
class ModelConfig:
    """Configuration for specific models with workflow optimization."""
    name: str
    max_tokens: int
    context_window: int
    cost_per_1k_tokens: float
    best_for: List[WorkflowType]
    description: str


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    All LLM provider implementations should inherit from this class.
    """
    
    def __init__(self, workflow_type: WorkflowType = WorkflowType.GENERAL):
        """
        Initialize the LLM client.
        
        Args:
            workflow_type: Type of workflow for model optimization
        """
        self.workflow_type = workflow_type
        self.default_model = self.get_default_model(workflow_type)
        
    @abstractmethod
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
        Execute a prompt using the LLM provider's API.
        
        Args:
            prompt: The prompt to execute
            model: Model name (defaults to workflow-optimized model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            timeout: Request timeout in seconds
            tools: List of tools (for compatibility)
            working_directory: Working directory (for compatibility)
            
        Returns:
            Dict with 'content', 'usage', 'model' keys
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from the provider."""
        pass
    
    @abstractmethod
    def get_default_model(self, workflow_type: WorkflowType) -> ModelConfig:
        """Get the default recommended model for a workflow type."""
        pass
    
    @abstractmethod
    def estimate_cost(self, prompt: str, model: Optional[str] = None) -> Dict[str, float]:
        """Estimate cost for a prompt execution."""
        pass
    
    def get_provider_name(self) -> str:
        """Get the name of the LLM provider."""
        return self.__class__.__name__.replace("Client", "")