#!/usr/bin/env python3
"""
Standalone LM Studio Task Executor with Tools Integration

This module uses LM Studio to execute tasks with actual file operations,
completely independent of Claude Code.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Optional, Any, List, Tuple
from pathlib import Path

from clients.lmstudio_client import LMStudioClient, create_jira_task_client, WorkflowType
from .modern_models_config import ModernLMStudioModels

# Import the actual tools
from tools.file_operations import FileOperations
from tools.command_execution import CommandExecution
from tools.search_navigation import SearchNavigation


class StandaloneLMStudioTaskExecutor:
    """Standalone task execution using LM Studio with integrated tools"""
    
    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize standalone LM Studio task executor
        
        Args:
            base_url: LM Studio API URL (defaults from env)
            model_name: Model to use
        """
        # Initialize LM Studio client
        self.lm_client = create_jira_task_client(base_url=base_url, model_name=model_name)
        self.model_name = model_name or self.lm_client.default_model.name
        
        # Initialize tools
        self.file_ops = FileOperations()
        self.cmd_exec = CommandExecution()
        self.search_nav = SearchNavigation()
        
        # Track execution context
        self.execution_context = {
            "created_files": [],
            "modified_files": [],
            "executed_commands": []
        }
        
        print(f"🤖 Using LM Studio with model: {self.model_name}")
        print("🛠️  Tools enabled: file operations, command execution, search")
    
    def execute_task(self, task_prompt: str) -> Dict[str, Any]:
        """
        Execute a task using LM Studio and tools
        
        Args:
            task_prompt: The task description
            
        Returns:
            Dict with execution results
        """
        try:
            print(f"🚀 Starting task execution with {self.model_name}...")
            
            # Enhanced prompt to get structured tool commands
            current_dir = os.getcwd()
            enhanced_prompt = f"""You are an AI assistant with access to file system tools.

CURRENT WORKING DIRECTORY: {current_dir}

{task_prompt}

IMPORTANT: You must provide the actual file contents, not just guidance.

You can respond in TWO ways:

METHOD 1 - Tool Commands (Preferred):
<tool_use>
<tool_name>Write</tool_name>
<parameters>
{{
  "file_path": "{current_dir}/docs/tests/local_llms/flappy_bird/MODEL_DIR/filename.py",
  "content": "import pygame\\n# Your code here"
}}
</parameters>
</tool_use>

METHOD 2 - Code Blocks (Alternative):
If you can't use tool commands, provide files like this:

**main.py**:
```python
import pygame
import sys
from bird import Bird
from pipe import Pipe

# Complete main.py implementation here
```

**bird.py**:
```python
import pygame

class Bird:
    def __init__(self, x, y):
        # Complete bird implementation
```

**pipe.py**: 
```python
import pygame

class Pipe:
    def __init__(self, x):
        # Complete pipe implementation
```

**game.py**:
```python
import pygame
from bird import Bird
from pipe import Pipe

class Game:
    def __init__(self):
        # Complete game state management
```

**requirements.txt**:
```text
pygame>=2.0.0
```

**README.md**:
```markdown
# Flappy Bird Game
Installation and usage instructions
```

CRITICAL: Provide COMPLETE, FUNCTIONAL code for each file. Make the game immediately playable.

Now implement the Flappy Bird game with all required files and complete implementations."""

            print(f"🔄 Sending request to LM Studio...")
            
            # Get LLM response
            result = self.lm_client.execute_prompt(
                prompt=enhanced_prompt,
                model=self.model_name,
                temperature=0.1,
                max_tokens=8000
            )
            
            if not result['success']:
                return {
                    "status": "error",
                    "message": f"LM Studio error: {result.get('error', 'Unknown error')}"
                }
            
            response = result['content']
            print(f"✅ LM Studio responded, parsing and executing tool commands...")
            
            # Parse and execute tool commands
            execution_results = self._parse_and_execute_tools(response)
            
            # Format results
            summary = self._format_execution_results(execution_results)
            
            success = any(r.get('status') == 'success' for r in execution_results)
            
            return {
                "status": "success" if success else "error",
                "message": "Task execution completed" if success else "No successful tool executions",
                "details": summary,
                "model": self.model_name,
                "execution_results": execution_results
            }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Task execution failed: {e}",
                "model": self.model_name
            }
    
    def _parse_and_execute_tools(self, response: str) -> List[Dict[str, Any]]:
        """Parse tool commands from LLM response and execute them"""
        results = []
        
        # Find all tool uses in the response
        tool_pattern = r'<tool_use>\s*<tool_name>(\w+)</tool_name>\s*<parameters>\s*(.*?)\s*</parameters>\s*</tool_use>'
        matches = re.finditer(tool_pattern, response, re.DOTALL)
        
        for match in matches:
            tool_name = match.group(1).lower()
            params_str = match.group(2).strip()
            
            # Handle multiline strings in JSON
            if '"""' in params_str:
                # Extract the content between triple quotes
                content_pattern = r'"content":\s*"""(.*?)"""'
                content_match = re.search(content_pattern, params_str, re.DOTALL)
                if content_match:
                    content = content_match.group(1)
                    # Escape the content for JSON
                    content_escaped = json.dumps(content)[1:-1]  # Remove outer quotes
                    params_str = re.sub(content_pattern, f'"content": "{content_escaped}"', params_str, flags=re.DOTALL)
            
            # Also handle file paths with /path/to prefix
            params_str = params_str.replace('/path/to/', os.path.abspath('.') + '/')
            
            try:
                params = json.loads(params_str)
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                params_str = re.sub(r',\s*}', '}', params_str)  # Remove trailing commas
                params_str = re.sub(r'}\s*}', '}}', params_str)  # Fix double closing braces
                try:
                    params = json.loads(params_str)
                except:
                    results.append({
                        "tool": tool_name,
                        "status": "error",
                        "error": f"Invalid JSON parameters: {params_str[:200]}..."
                    })
                    continue
            
            # Execute the tool
            result = self._execute_tool(tool_name, params)
            results.append(result)
        
        # If no tool commands found, try alternative parsing
        if not results:
            results = self._parse_alternative_format(response)
        
        return results
    
    def _parse_alternative_format(self, response: str) -> List[Dict[str, Any]]:
        """Parse alternative formats like code blocks with file paths"""
        results = []
        
        # Pattern 1: File creation with explicit file names
        file_pattern1 = r'(?:Creating|File:|Create)\s*`?([^`\n]+\.(?:py|txt|md|json|yml|yaml))`?\s*:?\s*\n```(?:python|json|yaml|markdown|text)?\n(.*?)\n```'
        matches = re.finditer(file_pattern1, response, re.DOTALL)
        
        for match in matches:
            file_path = match.group(1).strip()
            content = match.group(2)
            
            # Convert relative paths to absolute
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
            
            result = self._execute_tool("write", {
                "file_path": file_path,
                "content": content
            })
            results.append(result)
        
        # Pattern 2: Sequential file creation patterns (main.py, bird.py, etc.)
        if not results:
            current_dir = os.getcwd()
            target_dir = f"{current_dir}/docs/tests/local_llms/flappy_bird"
            
            # Look for specific file mentions with code blocks
            files_to_create = {
                'main.py': r'(?:main\.py|Main game|Game loop).*?```(?:python)?\n(.*?)\n```',
                'bird.py': r'(?:bird\.py|Bird class).*?```(?:python)?\n(.*?)\n```',
                'pipe.py': r'(?:pipe\.py|Pipe class).*?```(?:python)?\n(.*?)\n```',
                'game.py': r'(?:game\.py|Game.*?class|Game state).*?```(?:python)?\n(.*?)\n```',
                'requirements.txt': r'(?:requirements\.txt|dependencies).*?```(?:text|txt)?\n(.*?)\n```',
                'README.md': r'(?:README\.md|Installation|Instructions).*?```(?:markdown|md)?\n(.*?)\n```'
            }
            
            for filename, pattern in files_to_create.items():
                matches = re.finditer(pattern, response, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    content = match.group(1).strip()
                    if content and len(content) > 10:  # Ensure meaningful content
                        # Determine the correct subdirectory based on the model
                        if 'qwen_3_32B_8b' in response or 'qwen3-32b' in self.model_name.lower():
                            subdir = 'qwen_3_32B_8b'
                        elif 'qwen_25_coder_32B' in response or 'qwen2.5-coder' in self.model_name.lower():
                            subdir = 'qwen_25_coder_32B'
                        else:
                            # Extract model name for subdirectory
                            model_clean = self.model_name.replace('/', '_').replace(':', '_').replace('-', '_')
                            subdir = model_clean
                        
                        file_path = f"{target_dir}/{subdir}/{filename}"
                        
                        result = self._execute_tool("write", {
                            "file_path": file_path,
                            "content": content
                        })
                        results.append(result)
                        break  # Only take the first match for each file
        
        # Pattern 3: Look for any code blocks with common programming patterns
        if not results:
            print("   🔍 Trying to extract any Python code blocks...")
            python_blocks = re.finditer(r'```(?:python)?\n(import.*?)\n```', response, re.DOTALL)
            
            for i, match in enumerate(python_blocks):
                content = match.group(1).strip()
                if 'pygame' in content:  # Likely game-related code
                    filename = f"generated_code_{i+1}.py"
                    current_dir = os.getcwd()
                    
                    # Use model name for subdirectory
                    model_clean = self.model_name.replace('/', '_').replace(':', '_').replace('-', '_')
                    file_path = f"{current_dir}/docs/tests/local_llms/flappy_bird/{model_clean}/{filename}"
                    
                    result = self._execute_tool("write", {
                        "file_path": file_path,
                        "content": content
                    })
                    results.append(result)
        
        return results
    
    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool command"""
        try:
            if tool_name == "write":
                return self._execute_write(params)
            elif tool_name == "read":
                return self._execute_read(params)
            elif tool_name == "edit":
                return self._execute_edit(params)
            elif tool_name == "bash":
                return self._execute_bash(params)
            elif tool_name == "ls":
                return self._execute_ls(params)
            elif tool_name == "grep":
                return self._execute_grep(params)
            else:
                return {
                    "tool": tool_name,
                    "status": "error",
                    "error": f"Unknown tool: {tool_name}"
                }
        except Exception as e:
            return {
                "tool": tool_name,
                "status": "error",
                "error": str(e),
                "params": params
            }
    
    def _execute_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute write tool"""
        file_path = params.get("file_path")
        content = params.get("content")
        
        if not file_path or not content:
            return {
                "tool": "write",
                "status": "error",
                "error": "Missing required parameters: file_path and content"
            }
        
        # Fix path resolution - convert relative paths to absolute
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        # Handle common LLM path mistakes
        if file_path.startswith('/docs/'):
            # Model thinks docs is at root, fix to current directory
            file_path = os.path.join(os.getcwd(), file_path[1:])  # Remove leading /
        elif file_path.startswith('/Users/') and '/docs/' not in file_path:
            # Model might be missing the docs path component
            if 'github/agent-flows' in file_path and 'docs/tests' not in file_path:
                # Insert docs/tests after agent-flows
                file_path = file_path.replace('github/agent-flows/', 'github/agent-flows/docs/tests/')
        
        print(f"   📝 Writing to: {file_path}")
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write the file
            self.file_ops.write(file_path, content)
            self.execution_context["created_files"].append(file_path)
            
            print(f"   ✅ Created: {file_path}")
            
            return {
                "tool": "write",
                "status": "success",
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            print(f"   ❌ Failed to write {file_path}: {e}")
            return {
                "tool": "write",
                "status": "error",
                "error": str(e),
                "attempted_path": file_path
            }
    
    def _execute_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute read tool"""
        file_path = params.get("file_path")
        
        if not file_path:
            return {
                "tool": "read",
                "status": "error",
                "error": "Missing required parameter: file_path"
            }
        
        try:
            content = self.file_ops.read(
                file_path,
                offset=params.get("offset"),
                limit=params.get("limit")
            )
            return {
                "tool": "read",
                "status": "success",
                "file_path": file_path,
                "content": content
            }
        except FileNotFoundError:
            return {
                "tool": "read",
                "status": "error",
                "error": f"File not found: {file_path}"
            }
    
    def _execute_edit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute edit tool"""
        file_path = params.get("file_path")
        old_string = params.get("old_string")
        new_string = params.get("new_string")
        
        if not all([file_path, old_string, new_string]):
            return {
                "tool": "edit",
                "status": "error",
                "error": "Missing required parameters: file_path, old_string, new_string"
            }
        
        try:
            self.file_ops.edit(
                file_path,
                old_string,
                new_string,
                replace_all=params.get("replace_all", False)
            )
            self.execution_context["modified_files"].append(file_path)
            print(f"   ✅ Modified: {file_path}")
            return {
                "tool": "edit",
                "status": "success",
                "file_path": file_path
            }
        except Exception as e:
            return {
                "tool": "edit",
                "status": "error",
                "error": str(e)
            }
    
    def _execute_bash(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bash command"""
        command = params.get("command")
        
        if not command:
            return {
                "tool": "bash",
                "status": "error",
                "error": "Missing required parameter: command"
            }
        
        # Fix path issues in bash commands
        if '/docs/' in command and not '/Users/' in command:
            # Replace /docs/ with the correct absolute path
            current_dir = os.getcwd()
            command = command.replace('/docs/', f'{current_dir}/docs/')
        
        print(f"   🔧 Executing: {command}")
        
        try:
            result = self.cmd_exec.bash(
                command,
                timeout=params.get("timeout", 30000)
            )
            self.execution_context["executed_commands"].append(command)
            print(f"   ✅ Command succeeded")
            return {
                "tool": "bash",
                "status": "success",
                "command": command,
                "output": result
            }
        except Exception as e:
            print(f"   ❌ Command failed: {e}")
            return {
                "tool": "bash",
                "status": "error",
                "command": command,
                "error": str(e)
            }
    
    def _execute_ls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ls tool"""
        path = params.get("path", ".")
        
        try:
            result = self.search_nav.ls(path, ignore=params.get("ignore", []))
            return {
                "tool": "ls",
                "status": "success",
                "path": path,
                "content": result
            }
        except Exception as e:
            return {
                "tool": "ls",
                "status": "error",
                "path": path,
                "error": str(e)
            }
    
    def _execute_grep(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute grep tool"""
        pattern = params.get("pattern")
        
        if not pattern:
            return {
                "tool": "grep",
                "status": "error",
                "error": "Missing required parameter: pattern"
            }
        
        try:
            result = self.search_nav.grep(
                pattern,
                path=params.get("path", "."),
                glob_pattern=params.get("glob"),
                case_sensitive=not params.get("-i", False),
                output_mode=params.get("output_mode", "files_with_matches")
            )
            return {
                "tool": "grep",
                "status": "success",
                "pattern": pattern,
                "results": result
            }
        except Exception as e:
            return {
                "tool": "grep",
                "status": "error",
                "pattern": pattern,
                "error": str(e)
            }
    
    def _format_execution_results(self, results: List[Dict[str, Any]]) -> str:
        """Format execution results for display"""
        if not results:
            return "No tool commands were executed. The LLM provided guidance only."
        
        output = []
        success_count = sum(1 for r in results if r.get('status') == 'success')
        output.append(f"Executed {len(results)} tool commands ({success_count} successful):")
        
        for i, result in enumerate(results, 1):
            tool = result.get("tool", "unknown")
            status = result.get("status", "unknown")
            
            if status == "success":
                output.append(f"{i}. ✅ {tool}: Success")
                if tool == "write":
                    output.append(f"   Created: {result.get('file_path')}")
                elif tool == "bash":
                    output.append(f"   Command: {result.get('command')}")
            else:
                output.append(f"{i}. ❌ {tool}: Failed")
                output.append(f"   Error: {result.get('error')}")
        
        # Summary
        output.append("\nSummary:")
        output.append(f"Created files: {len(self.execution_context['created_files'])}")
        for f in self.execution_context['created_files']:
            output.append(f"  - {f}")
        
        if self.execution_context['modified_files']:
            output.append(f"Modified files: {len(self.execution_context['modified_files'])}")
            for f in self.execution_context['modified_files']:
                output.append(f"  - {f}")
        
        if self.execution_context['executed_commands']:
            output.append(f"Executed commands: {len(self.execution_context['executed_commands'])}")
        
        return "\n".join(output)


def main():
    """Main entry point for standalone LM Studio task execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Standalone LM Studio Task Execution with Tools")
    parser.add_argument("prompt", nargs='?', help="Task prompt to execute")
    parser.add_argument("--model", "-m", help="Model name to use")
    parser.add_argument("--base-url", default=None, help="LM Studio API URL")
    
    args = parser.parse_args()
    
    try:
        executor = StandaloneLMStudioTaskExecutor(
            base_url=args.base_url,
            model_name=args.model
        )
        
        if not args.prompt:
            print("❌ Task prompt required")
            parser.print_help()
            return
        
        result = executor.execute_task(args.prompt)
        
        print(f"\n{'='*60}")
        print(f"📊 Task Execution Result: {result['status'].upper()}")
        print(f"🤖 Model: {result['model']}")
        if result.get('details'):
            print(f"\n{result['details']}")
        if result['status'] == 'error':
            print(f"\n❌ Error: {result.get('message', 'Unknown error')}")
    
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