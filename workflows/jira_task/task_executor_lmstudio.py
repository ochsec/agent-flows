#!/usr/bin/env python3
"""
Task Execution Workflow with LM Studio Integration

This module integrates the existing LMStudioClient for task execution,
providing seamless integration with locally hosted models via LM Studio.
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional, Any, List
from pathlib import Path

from .git_integration import GitIntegration, GitError
from .task_executor import TaskExecutor
from clients.lmstudio_client import LMStudioClient, create_jira_task_client, LMStudioModels, WorkflowType
from .modern_models_config import ModernLMStudioModels


class LMStudioTaskExecutor(TaskExecutor):
    """Task execution workflow using LM Studio client"""
    
    def __init__(self, repo_path: Optional[str] = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize LM Studio task executor
        
        Args:
            repo_path: Path to git repository (defaults to current directory)
            base_url: LM Studio API URL (defaults to http://localhost:1234/v1)
            model_name: Override default model selection
        """
        super().__init__(repo_path)
        
        # Initialize LM Studio client for JIRA tasks
        self.lm_client = create_jira_task_client(base_url=base_url, model_name=model_name)
        self.model_name = model_name or self.lm_client.default_model.name
        
        print(f"🤖 Using LM Studio with model: {self.model_name}")
    
    def _execute_claude_command(self, prompt: str) -> str:
        """
        Override parent method to use LM Studio instead of Claude Code CLI
        
        Args:
            prompt: Prompt for the LLM
            
        Returns:
            LLM response
        """
        try:
            # Add context about available tools and capabilities
            enhanced_prompt = f"""You are an AI development assistant helping with software engineering tasks.

{prompt}

Please provide detailed, actionable guidance for the development task. Include:
- Specific code examples where appropriate
- File paths and structure recommendations
- Testing strategies
- Best practices for the implementation

Remember to be specific and practical in your recommendations."""

            print(f"🔄 Sending request to LM Studio ({self.model_name})...")
            
            # Execute prompt with LM Studio
            result = self.lm_client.execute_prompt(
                prompt=enhanced_prompt,
                model=self.model_name,
                temperature=0.1,  # Lower temperature for more consistent code generation
                max_tokens=4000
            )
            
            if result['success']:
                print(f"✅ LM Studio responded successfully")
                return result['content']
            else:
                return f"Error from LM Studio: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"Failed to execute LM Studio request: {e}"
    
    def execute_task_with_model(self, task_prompt: str, model_name: str, task_id: Optional[str] = None, 
                               branch_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using a specific LM Studio model
        
        Args:
            task_prompt: The task description/prompt to execute
            model_name: Name of the LM Studio model to use
            task_id: Optional task identifier for tracking
            branch_name: Optional branch name (will create if doesn't exist)
            
        Returns:
            Dict with execution results
        """
        # Temporarily switch models
        original_model = self.model_name
        self.model_name = model_name
        
        try:
            print(f"🔄 Switching to model: {model_name}")
            result = self.execute_task(task_prompt, task_id, branch_name)
            result["model_used"] = model_name
            return result
        finally:
            # Restore original model
            self.model_name = original_model
    
    def compare_models_for_task(self, task_prompt: str, task_id_prefix: str = "compare", use_modern: bool = True) -> Dict[str, Any]:
        """
        Execute the same task with multiple recommended models for comparison
        
        Args:
            task_prompt: The task to execute
            task_id_prefix: Prefix for task IDs
            use_modern: Use modern high-parameter models instead of legacy ones
            
        Returns:
            Dict with results from all recommended models
        """
        # Get recommended models
        if use_modern:
            recommended_models = ModernLMStudioModels.get_recommended_for_coding()
            print("🚀 Using modern high-parameter models for comparison")
        else:
            recommended_models = LMStudioModels.get_recommended_models(WorkflowType.JIRA_TASK)
            print("📦 Using legacy models for comparison")
        
        print(f"🔬 Comparing {len(recommended_models)} models for JIRA task workflow")
        print(f"Models: {', '.join([m.name for m in recommended_models])}")
        
        results = {}
        
        for i, model_config in enumerate(recommended_models):
            model_name = model_config.name
            print(f"\n{'='*60}")
            print(f"🔄 Testing model {i+1}/{len(recommended_models)}: {model_name}")
            print(f"📝 Description: {model_config.description}")
            
            task_id = f"{task_id_prefix}_{model_name.replace(':', '_').replace('.', '_')}_{i+1}"
            
            # Check if model is available
            available_models = self.lm_client.get_available_models()
            model_available = any(m['name'] == model_name for m in available_models)
            
            if not model_available:
                print(f"⚠️  Model {model_name} not available in LM Studio, skipping...")
                results[model_name] = {
                    "status": "skipped",
                    "reason": "Model not available in LM Studio",
                    "model_config": model_config.__dict__
                }
                continue
            
            # Execute task with this model
            start_time = datetime.now()
            result = self.execute_task_with_model(
                task_prompt=task_prompt,
                model_name=model_name,
                task_id=task_id
            )
            execution_time = (datetime.now() - start_time).total_seconds()
            
            results[model_name] = {
                "result": result,
                "execution_time": execution_time,
                "model_config": model_config.__dict__,
                "status": result['status']
            }
            
            print(f"✅ Completed {model_name}: {result['status']} ({execution_time:.2f}s)")
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 Model Comparison Summary:")
        for model_name, data in results.items():
            status = data.get('status', 'unknown')
            time_taken = data.get('execution_time', 'N/A')
            if isinstance(time_taken, float):
                time_str = f"{time_taken:.2f}s"
            else:
                time_str = time_taken
            print(f"   {model_name}: {status} ({time_str})")
        
        return results
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from LM Studio"""
        return self.lm_client.get_available_models()
    
    def get_recommended_models(self, use_modern: bool = True) -> List[Dict[str, Any]]:
        """Get recommended models for JIRA task workflows"""
        if use_modern:
            models = ModernLMStudioModels.get_recommended_for_coding()
        else:
            models = LMStudioModels.get_recommended_models(WorkflowType.JIRA_TASK)
            
        return [
            {
                "name": model.name,
                "description": model.description,
                "max_tokens": model.max_tokens,
                "context_window": model.context_window
            }
            for model in models
        ]
    
    def get_models_by_vram(self, vram_gb: int) -> List[Dict[str, Any]]:
        """Get recommended models based on available VRAM"""
        models = ModernLMStudioModels.get_recommended_by_vram(vram_gb)
        results = []
        
        for model in models:
            requirements = ModernLMStudioModels.get_model_requirements(model)
            results.append({
                "name": model.name,
                "description": model.description,
                "max_tokens": model.max_tokens,
                "context_window": model.context_window,
                "requirements": requirements
            })
        
        return results


def main():
    """Main entry point for LM Studio task execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LM Studio Task Execution Workflow")
    parser.add_argument("prompt", nargs='?', help="Task prompt to execute")
    parser.add_argument("--model", "-m", help="Model name to use (e.g., 'codellama-13b', 'deepseek-coder-6.7b')")
    parser.add_argument("--base-url", default=None, help="LM Studio API URL (default: http://localhost:1234/v1)")
    parser.add_argument("--task-id", help="Optional task identifier")
    parser.add_argument("--branch", help="Branch name to work on")
    parser.add_argument("--compare-models", action="store_true", help="Compare all recommended models")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--list-recommended", action="store_true", help="List recommended models for JIRA tasks")
    parser.add_argument("--use-legacy", action="store_true", help="Use legacy small models instead of modern ones")
    parser.add_argument("--vram", type=int, help="Get models recommended for your VRAM (in GB)")
    
    args = parser.parse_args()
    
    try:
        executor = LMStudioTaskExecutor(
            base_url=args.base_url,
            model_name=args.model
        )
        
        if args.list_models:
            print("📋 Available models in LM Studio:")
            models = executor.get_available_models()
            for model in models:
                print(f"   • {model['name']}")
                if model.get('description'):
                    print(f"     {model['description']}")
            return
        
        if args.list_recommended:
            use_modern = not args.use_legacy
            print(f"🎯 Recommended {'modern high-parameter' if use_modern else 'legacy'} models for JIRA task workflows:")
            models = executor.get_recommended_models(use_modern=use_modern)
            for model in models:
                print(f"   • {model['name']}")
                print(f"     {model['description']}")
                print(f"     Max tokens: {model['max_tokens']}, Context: {model['context_window']}")
                print()
            return
        
        if args.vram:
            print(f"🎮 Recommended models for {args.vram}GB VRAM:")
            models = executor.get_models_by_vram(args.vram)
            for model in models:
                print(f"   • {model['name']}")
                print(f"     {model['description']}")
                print(f"     Requirements: {model['requirements']['min_vram_gb']}GB min, {model['requirements']['recommended_vram_gb']}GB recommended")
                print()
            return
        
        if not args.prompt:
            print("❌ Task prompt required")
            parser.print_help()
            return
        
        if args.compare_models:
            use_modern = not args.use_legacy
            print(f"🔬 Comparing recommended {'modern' if use_modern else 'legacy'} models for JIRA tasks...")
            results = executor.compare_models_for_task(
                task_prompt=args.prompt,
                task_id_prefix=args.task_id or "compare",
                use_modern=use_modern
            )
        else:
            result = executor.execute_task(args.prompt, args.task_id, args.branch)
            print(f"🎯 Result: {result['message']}")
            print(f"🤖 Model: {executor.model_name}")
            if result['status'] == 'error':
                print(f"❌ Details: {result.get('details', '')}")
    
    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("\nPlease make sure:")
        print("1. LM Studio is running")
        print("2. Local server is enabled in LM Studio settings")
        print("3. A model is loaded in LM Studio")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()