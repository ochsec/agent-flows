"""
LM Studio API client for local LLM interactions.
Provides unified interface for LLM interactions using locally hosted models via LM Studio.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
import requests

from .llm_client import LLMClient, WorkflowType, ModelConfig

logger = logging.getLogger(__name__)


class LMStudioModels:
    """Common models available in LM Studio."""
    
    # Popular open-source models typically run in LM Studio
    LLAMA_3_8B = ModelConfig(
        name="llama-3-8b",
        max_tokens=4096,
        context_window=8192,
        cost_per_1k_tokens=0.0,  # Local models have no per-token cost
        best_for=[WorkflowType.GENERAL, WorkflowType.CODE_REVIEW],
        description="Meta's Llama 3 8B - good for general tasks and code"
    )
    
    MISTRAL_7B = ModelConfig(
        name="mistral-7b",
        max_tokens=4096,
        context_window=32000,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.RESEARCH, WorkflowType.GENERAL],
        description="Mistral 7B - excellent for research and analysis"
    )
    
    CODELLAMA_13B = ModelConfig(
        name="codellama-13b",
        max_tokens=4096,
        context_window=16384,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="Code Llama 13B - specialized for code generation and review"
    )
    
    DEEPSEEK_CODER_6B = ModelConfig(
        name="deepseek-coder-6.7b",
        max_tokens=4096,
        context_window=16384,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.CODE_REVIEW, WorkflowType.JIRA_TASK],
        description="DeepSeek Coder - optimized for coding tasks"
    )
    
    MIXTRAL_8X7B = ModelConfig(
        name="mixtral-8x7b",
        max_tokens=4096,
        context_window=32768,
        cost_per_1k_tokens=0.0,
        best_for=[WorkflowType.RESEARCH, WorkflowType.JIRA_TASK, WorkflowType.GENERAL],
        description="Mixtral 8x7B - powerful mixture of experts model"
    )
    
    @classmethod
    def get_recommended_models(cls, workflow_type: WorkflowType) -> List[ModelConfig]:
        """Get recommended models for a specific workflow type."""
        all_models = [
            cls.LLAMA_3_8B, cls.MISTRAL_7B, cls.CODELLAMA_13B, 
            cls.DEEPSEEK_CODER_6B, cls.MIXTRAL_8X7B
        ]
        return [model for model in all_models if workflow_type in model.best_for]
    
    @classmethod
    def get_default_model(cls, workflow_type: WorkflowType) -> ModelConfig:
        """Get the default recommended model for a workflow type."""
        recommendations = {
            WorkflowType.RESEARCH: cls.MIXTRAL_8X7B,
            WorkflowType.CODE_REVIEW: cls.CODELLAMA_13B,
            WorkflowType.JIRA_TASK: cls.DEEPSEEK_CODER_6B,
            WorkflowType.GENERAL: cls.LLAMA_3_8B
        }
        return recommendations.get(workflow_type, cls.LLAMA_3_8B)


class LMStudioClient(LLMClient):
    """
    LM Studio API client for local LLM interactions.
    Compatible with LM Studio's OpenAI-compatible API endpoint.
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        workflow_type: WorkflowType = WorkflowType.GENERAL,
        model_name: Optional[str] = None
    ):
        """
        Initialize LM Studio client.
        
        Args:
            base_url: LM Studio API URL (default: http://localhost:1234/v1)
            workflow_type: Type of workflow for model optimization
            model_name: Override default model selection
        """
        super().__init__(workflow_type)
        
        self.base_url = base_url or os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        
        # Test connection
        self._test_connection()
        
        # If model_name provided, override the default
        if model_name:
            self.default_model = ModelConfig(
                name=model_name,
                max_tokens=4096,
                context_window=8192,
                cost_per_1k_tokens=0.0,
                best_for=[workflow_type],
                description=f"Custom model: {model_name}"
            )
        
        logger.info(f"LM Studio client initialized for {workflow_type.value} with model {self.default_model.name}")
        logger.info(f"Base URL: {self.base_url}")
    
    def _test_connection(self):
        """Test connection to LM Studio server."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code != 200:
                raise ConnectionError(f"LM Studio server returned status {response.status_code}")
            logger.info("Successfully connected to LM Studio server")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Failed to connect to LM Studio at {self.base_url}. "
                f"Make sure LM Studio is running with the local server enabled. Error: {e}"
            )
    
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
        Execute a prompt using LM Studio's local API.
        
        Args:
            prompt: The prompt to execute
            model: Model name (defaults to workflow-optimized model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            timeout: Request timeout in seconds
            tools: List of tools (for compatibility - not used)
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
            
            # Prepare request payload
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"LM Studio API error: {response.status_code} - {response.text}")
            
            response_data = response.json()
            execution_time = time.time() - start_time
            
            # Format response to match expected format
            result = {
                "content": response_data["choices"][0]["message"]["content"],
                "model": response_data.get("model", model),
                "usage": {
                    "prompt_tokens": response_data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": response_data.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": response_data.get("usage", {}).get("total_tokens", 0)
                },
                "execution_time": execution_time,
                "success": True
            }
            
            logger.info(f"LM Studio request completed in {execution_time:.2f}s using {model}")
            return result
            
        except Exception as e:
            logger.error(f"LM Studio API error: {str(e)}")
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
            LMStudioModels.LLAMA_3_8B,
            LMStudioModels.MISTRAL_7B,
            LMStudioModels.CODELLAMA_13B,
            LMStudioModels.DEEPSEEK_CODER_6B,
            LMStudioModels.MIXTRAL_8X7B
        ]
        
        for model_config in all_models:
            if model_config.name == model_name:
                return model_config
        
        # Return a generic config for unknown models
        return ModelConfig(
            name=model_name,
            max_tokens=4096,
            context_window=8192,
            cost_per_1k_tokens=0.0,
            best_for=[self.workflow_type],
            description=f"Custom model: {model_name}"
        )
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from LM Studio."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                models = []
                
                for model in models_data.get("data", []):
                    model_id = model.get("id", "unknown")
                    # Try to find matching config
                    config = self._get_model_config(model_id)
                    
                    models.append({
                        "name": model_id,
                        "max_tokens": config.max_tokens,
                        "context_window": config.context_window,
                        "cost_per_1k_tokens": 0.0,
                        "description": config.description
                    })
                
                return models
            else:
                logger.error(f"Failed to fetch models: {response.status_code}")
                return self._get_default_models()
                
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            return self._get_default_models()
    
    def _get_default_models(self) -> List[Dict[str, Any]]:
        """Return default model list when can't fetch from server."""
        recommended = LMStudioModels.get_recommended_models(self.workflow_type)
        return [
            {
                "name": model.name,
                "max_tokens": model.max_tokens,
                "context_window": model.context_window,
                "cost_per_1k_tokens": 0.0,
                "description": model.description
            }
            for model in recommended
        ]
    
    def get_default_model(self, workflow_type: WorkflowType) -> ModelConfig:
        """Get the default recommended model for a workflow type."""
        return LMStudioModels.get_default_model(workflow_type)
    
    def estimate_cost(self, prompt: str, model: Optional[str] = None) -> Dict[str, float]:
        """Estimate cost for a prompt execution (always 0 for local models)."""
        if not model:
            model = self.default_model.name
        
        # Rough token estimation (4 chars = 1 token)
        estimated_tokens = len(prompt) // 4
        
        return {
            "estimated_cost": 0.0,  # Local models are free
            "prompt_tokens": estimated_tokens,
            "model": model,
            "cost_per_1k_tokens": 0.0
        }


# Compatibility functions for easy migration
def create_research_client(base_url: Optional[str] = None, model_name: Optional[str] = None) -> LMStudioClient:
    """Create LM Studio client optimized for research workflows."""
    return LMStudioClient(base_url=base_url, workflow_type=WorkflowType.RESEARCH, model_name=model_name)

def create_code_review_client(base_url: Optional[str] = None, model_name: Optional[str] = None) -> LMStudioClient:
    """Create LM Studio client optimized for code review workflows."""
    return LMStudioClient(base_url=base_url, workflow_type=WorkflowType.CODE_REVIEW, model_name=model_name)

def create_jira_task_client(base_url: Optional[str] = None, model_name: Optional[str] = None) -> LMStudioClient:
    """Create LM Studio client optimized for JIRA task workflows."""
    return LMStudioClient(base_url=base_url, workflow_type=WorkflowType.JIRA_TASK, model_name=model_name)


if __name__ == "__main__":
    # Example usage and testing
    print("LM Studio Client - Testing Connection and Models")
    print("=" * 60)
    
    try:
        # Test connection
        client = LMStudioClient()
        
        print("\nAvailable models:")
        models = client.get_available_models()
        for model in models:
            print(f"  • {model['name']}")
            print(f"    {model['description']}")
            print()
        
        # Test a simple prompt
        print("\nTesting prompt execution...")
        result = client.execute_prompt("Hello, how are you?", max_tokens=50)
        if result['success']:
            print(f"Response: {result['content'][:100]}...")
            print(f"Tokens used: {result['usage']['total_tokens']}")
        else:
            print(f"Error: {result['error']}")
            
    except ConnectionError as e:
        print(f"Connection Error: {e}")
        print("\nPlease make sure:")
        print("1. LM Studio is running")
        print("2. Local server is enabled in LM Studio settings")
        print("3. A model is loaded in LM Studio")