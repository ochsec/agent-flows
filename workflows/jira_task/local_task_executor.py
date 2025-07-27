#!/usr/bin/env python3
"""
Local LLM Task Execution Workflow

This module provides task execution using local LLM models instead of Claude Code.
Supports various local model providers like Ollama, LMStudio, and OpenAI-compatible APIs.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional, Any, List
from pathlib import Path

from .git_integration import GitIntegration, GitError


class LocalLLMTaskExecutor:
    """Task execution workflow using local LLM models"""
    
    def __init__(self, repo_path: Optional[str] = None, model_config: Optional[Dict[str, Any]] = None):
        """
        Initialize local LLM task executor
        
        Args:
            repo_path: Path to git repository (defaults to current directory)
            model_config: Configuration for local LLM model
        """
        self.git = GitIntegration(repo_path)
        self.current_branch = None
        self.execution_state = {}
        
        # Default model configuration
        self.model_config = model_config or {
            "provider": "ollama",  # ollama, lmstudio, openai_compatible
            "model": "codellama:7b",
            "base_url": "http://localhost:11434",
            "api_key": None,
            "temperature": 0.1,
            "max_tokens": 4000
        }
    
    def execute_task_with_model(self, task_prompt: str, model_name: str, task_id: Optional[str] = None, 
                               branch_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using specified local model
        
        Args:
            task_prompt: The task description/prompt to execute
            model_name: Name of the local model to use
            task_id: Optional task identifier for tracking
            branch_name: Optional branch name (will create if doesn't exist)
            
        Returns:
            Dict with execution results
        """
        # Update model config
        original_model = self.model_config["model"]
        self.model_config["model"] = model_name
        
        try:
            result = self.execute_task(task_prompt, task_id, branch_name)
            result["model_used"] = model_name
            return result
        finally:
            # Restore original model
            self.model_config["model"] = original_model
    
    def execute_task(self, task_prompt: str, task_id: Optional[str] = None, branch_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task from a given prompt using local LLM
        
        Args:
            task_prompt: The task description/prompt to execute
            task_id: Optional task identifier for tracking
            branch_name: Optional branch name (will create if doesn't exist)
            
        Returns:
            Dict with execution results
        """
        try:
            print(f"🚀 Starting task execution with {self.model_config['model']}...")
            if task_id:
                print(f"📋 Task ID: {task_id}")
            
            # Setup branch if specified
            if branch_name:
                self._setup_branch(branch_name)
            
            # Track execution state
            execution_id = task_id or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.execution_state[execution_id] = {
                'status': 'in_progress',
                'branch': self.current_branch,
                'started_at': datetime.now().isoformat(),
                'prompt': task_prompt[:100] + "..." if len(task_prompt) > 100 else task_prompt,
                'model': self.model_config['model']
            }
            
            # Execute the task workflow
            result = self._execute_development_workflow(task_prompt, execution_id)
            
            # Update execution state
            self.execution_state[execution_id]['status'] = 'completed' if result['status'] == 'success' else 'failed'
            self.execution_state[execution_id]['completed_at'] = datetime.now().isoformat()
            
            return {
                "status": result['status'],
                "execution_id": execution_id,
                "branch": self.current_branch,
                "model": self.model_config['model'],
                "message": result.get('message', 'Task execution completed'),
                "details": result.get('details', '')
            }
            
        except Exception as e:
            error_result = {"status": "error", "message": f"Task execution failed: {e}"}
            print(f"❌ {error_result['message']}")
            return error_result
    
    def _setup_branch(self, branch_name: str) -> None:
        """Setup or switch to the specified branch"""
        try:
            if self.git.branch_exists(branch_name):
                print(f"🔄 Switching to existing branch: {branch_name}")
                self.git.checkout_branch(branch_name)
            else:
                print(f"🌿 Creating new branch: {branch_name}")
                self.git.create_branch_simple(branch_name)
            
            self.current_branch = branch_name
            
        except GitError as e:
            print(f"⚠️ Branch setup warning: {e}")
            self.current_branch = self.git.get_current_branch()
    
    def _execute_development_workflow(self, task_prompt: str, execution_id: str) -> Dict[str, Any]:
        """
        Execute the development workflow with local LLM
        
        Args:
            task_prompt: The task description/prompt
            execution_id: Unique execution identifier
            
        Returns:
            Dict with execution results
        """
        print(f"🤖 Launching {self.model_config['model']} development assistant...")
        
        # Create comprehensive development prompt
        development_prompt = f"""You are a development assistant executing task ID: {execution_id}

Task Description:
{task_prompt}

Current working directory: {os.getcwd()}

Please analyze this task and provide:
1. A step-by-step implementation plan
2. Specific file changes needed
3. Code snippets for implementation
4. Testing approach
5. Any dependencies that need to be installed

Provide a comprehensive response with actionable development steps."""
        
        # Execute with local LLM
        result = self._call_local_llm(development_prompt)
        
        if not result or "error" in result.lower():
            return {"status": "error", "message": "Local LLM execution failed", "details": result}
        
        print(f"✅ Task execution completed")
        return {"status": "success", "message": "Task executed successfully", "details": result}
    
    def _call_local_llm(self, prompt: str) -> str:
        """
        Call local LLM with the given prompt
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            LLM response text
        """
        provider = self.model_config["provider"]
        
        try:
            if provider == "ollama":
                return self._call_ollama(prompt)
            elif provider == "lmstudio":
                return self._call_lmstudio(prompt)
            elif provider == "openai_compatible":
                return self._call_openai_compatible(prompt)
            else:
                return f"Error: Unsupported provider '{provider}'"
        except Exception as e:
            return f"Error calling {provider}: {str(e)}"
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API"""
        url = f"{self.model_config['base_url']}/api/generate"
        
        payload = {
            "model": self.model_config["model"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.model_config.get("temperature", 0.1),
                "num_predict": self.model_config.get("max_tokens", 4000)
            }
        }
        
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        
        return response.json()["response"]
    
    def _call_lmstudio(self, prompt: str) -> str:
        """Call LMStudio API (OpenAI-compatible)"""
        url = f"{self.model_config['base_url']}/v1/chat/completions"
        
        payload = {
            "model": self.model_config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.model_config.get("temperature", 0.1),
            "max_tokens": self.model_config.get("max_tokens", 4000)
        }
        
        headers = {"Content-Type": "application/json"}
        if self.model_config.get("api_key"):
            headers["Authorization"] = f"Bearer {self.model_config['api_key']}"
        
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def _call_openai_compatible(self, prompt: str) -> str:
        """Call OpenAI-compatible API"""
        url = f"{self.model_config['base_url']}/v1/chat/completions"
        
        payload = {
            "model": self.model_config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.model_config.get("temperature", 0.1),
            "max_tokens": self.model_config.get("max_tokens", 4000)
        }
        
        headers = {"Content-Type": "application/json"}
        if self.model_config.get("api_key"):
            headers["Authorization"] = f"Bearer {self.model_config['api_key']}"
        
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def compare_models(self, task_prompt: str, models: List[str], task_id_prefix: str = "compare") -> Dict[str, Any]:
        """
        Execute the same task with multiple models for comparison
        
        Args:
            task_prompt: The task to execute
            models: List of model names to test
            task_id_prefix: Prefix for task IDs
            
        Returns:
            Dict with results from all models
        """
        results = {}
        
        for i, model in enumerate(models):
            print(f"\n🔄 Testing with model {i+1}/{len(models)}: {model}")
            task_id = f"{task_id_prefix}_{model.replace(':', '_')}_{i+1}"
            
            result = self.execute_task_with_model(
                task_prompt=task_prompt,
                model_name=model,
                task_id=task_id
            )
            
            results[model] = {
                "result": result,
                "execution_time": self._get_execution_time(task_id),
                "model": model
            }
            
            print(f"✅ Completed {model}: {result['status']}")
        
        return results
    
    def _get_execution_time(self, execution_id: str) -> Optional[float]:
        """Calculate execution time for a task"""
        if execution_id in self.execution_state:
            state = self.execution_state[execution_id]
            if 'completed_at' in state:
                start = datetime.fromisoformat(state['started_at'])
                end = datetime.fromisoformat(state['completed_at'])
                return (end - start).total_seconds()
        return None


def main():
    """Main entry point for local LLM task execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Local LLM Task Execution Workflow")
    parser.add_argument("prompt", nargs='?', help="Task prompt to execute")
    parser.add_argument("--model", "-m", help="Model name to use")
    parser.add_argument("--provider", choices=["ollama", "lmstudio", "openai_compatible"], 
                       default="ollama", help="LLM provider")
    parser.add_argument("--base-url", default="http://localhost:11434", 
                       help="Base URL for the LLM API")
    parser.add_argument("--api-key", help="API key if required")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperature setting")
    parser.add_argument("--max-tokens", type=int, default=4000, help="Maximum tokens")
    parser.add_argument("--task-id", help="Optional task identifier")
    parser.add_argument("--branch", help="Branch name to work on")
    parser.add_argument("--compare-models", nargs="+", help="Compare multiple models")
    parser.add_argument("--list", action="store_true", help="List all executions")
    
    args = parser.parse_args()
    
    # Build model configuration
    model_config = {
        "provider": args.provider,
        "model": args.model or "codellama:7b",
        "base_url": args.base_url,
        "api_key": args.api_key,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens
    }
    
    try:
        executor = LocalLLMTaskExecutor(model_config=model_config)
        
        if args.list:
            executions = executor.execution_state
            if executions:
                print("📋 Task Executions:")
                for execution_id, info in executions.items():
                    print(f"   {execution_id}: {info['status']} - {info['model']} - {info['prompt']}")
            else:
                print("No task executions found")
            return
        
        if not args.prompt:
            print("❌ Task prompt required")
            parser.print_help()
            return
        
        if args.compare_models:
            print(f"🔄 Comparing {len(args.compare_models)} models...")
            results = executor.compare_models(args.prompt, args.compare_models, args.task_id or "compare")
            
            print("\n📊 Comparison Results:")
            for model, data in results.items():
                status = data['result']['status']
                time_taken = data.get('execution_time', 'Unknown')
                print(f"   {model}: {status} ({time_taken}s)")
        else:
            result = executor.execute_task(args.prompt, args.task_id, args.branch)
            print(f"🎯 Result: {result['message']}")
            print(f"🤖 Model: {result.get('model', 'Unknown')}")
            if result['status'] == 'error':
                print(f"❌ Details: {result.get('details', '')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()