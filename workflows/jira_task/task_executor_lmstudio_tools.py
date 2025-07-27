#!/usr/bin/env python3
"""
Task Execution Workflow with LM Studio and Tools Integration

This module integrates LMStudioClient with actual file operation tools,
allowing the LLM to execute actions instead of just providing guidance.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Optional, Any, List, Tuple
from pathlib import Path

from .git_integration import GitIntegration, GitError
from .task_executor import TaskExecutor
from clients.lmstudio_client import LMStudioClient, create_jira_task_client, WorkflowType
from .modern_models_config import ModernLMStudioModels

# Import the actual tools
from tools.file_operations import FileOperations
from tools.command_execution import CommandExecution
from tools.search_navigation import SearchNavigation


class LMStudioTaskExecutorWithTools(TaskExecutor):
    """Task execution workflow using LM Studio client with integrated tools"""
    
    def __init__(self, repo_path: Optional[str] = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize LM Studio task executor with tools
        
        Args:
            repo_path: Path to git repository (defaults to current directory)
            base_url: LM Studio API URL (defaults from env)
            model_name: Override default model selection
        """
        super().__init__(repo_path)
        
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
    
    def _execute_claude_command(self, prompt: str) -> str:
        """
        Override to parse LLM response and execute tool commands
        
        Args:
            prompt: Prompt for the LLM
            
        Returns:
            Execution results
        """
        try:
            # Enhanced prompt to get structured tool commands
            enhanced_prompt = f"""You are an AI development assistant with access to file system tools.

{prompt}

IMPORTANT: You must respond with actual tool commands to implement the solution, not just guidance.

Use the following tool command format:
<tool_use>
<tool_name>ToolName</tool_name>
<parameters>
{{
  "param1": "value1",
  "param2": "value2"
}}
</parameters>
</tool_use>

Available tools:
1. Write - Create or overwrite a file
   Parameters: file_path (absolute path), content (file content)
   
2. Read - Read a file
   Parameters: file_path (absolute path), limit (optional), offset (optional)
   
3. Edit - Edit specific parts of a file
   Parameters: file_path, old_string, new_string, replace_all (optional)
   
4. Bash - Execute shell commands
   Parameters: command, timeout (optional)
   
5. Ls - List directory contents
   Parameters: path (absolute path)

6. Grep - Search for patterns in files
   Parameters: pattern, path (optional), glob (optional)

Remember to:
1. Create all files with proper content
2. Use absolute paths
3. Create directories before files if needed
4. Execute commands in sequence

Now implement the requested functionality using the tools."""

            print(f"🔄 Sending request to LM Studio ({self.model_name})...")
            
            # Get LLM response
            result = self.lm_client.execute_prompt(
                prompt=enhanced_prompt,
                model=self.model_name,
                temperature=0.1,
                max_tokens=8000  # Increase for full implementation
            )
            
            if not result['success']:
                return f"Error from LM Studio: {result.get('error', 'Unknown error')}"
            
            response = result['content']
            print(f"✅ LM Studio responded, executing tool commands...")
            
            # Parse and execute tool commands
            execution_results = self._parse_and_execute_tools(response)
            
            return self._format_execution_results(execution_results)
                
        except Exception as e:
            return f"Failed to execute LM Studio request: {e}"
    
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
        
        # Look for file creation patterns
        file_pattern = r'(?:Creating|File:)\s*`?([^`\n]+\.(?:py|txt|md|json|yml|yaml))`?\s*:?\s*\n```(?:python|json|yaml|markdown)?\n(.*?)\n```'
        matches = re.finditer(file_pattern, response, re.DOTALL)
        
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
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the file
        self.file_ops.write(file_path, content)
        self.execution_context["created_files"].append(file_path)
        
        return {
            "tool": "write",
            "status": "success",
            "file_path": file_path,
            "size": len(content)
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
        
        try:
            result = self.cmd_exec.bash(
                command,
                timeout=params.get("timeout", 30000)
            )
            self.execution_context["executed_commands"].append(command)
            return {
                "tool": "bash",
                "status": "success",
                "command": command,
                "output": result
            }
        except Exception as e:
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
        output.append(f"Executed {len(results)} tool commands:")
        
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
        
        return "\n".join(output)


def main():
    """Main entry point for LM Studio task execution with tools"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LM Studio Task Execution with Tools")
    parser.add_argument("prompt", nargs='?', help="Task prompt to execute")
    parser.add_argument("--model", "-m", help="Model name to use")
    parser.add_argument("--base-url", default=None, help="LM Studio API URL")
    parser.add_argument("--task-id", help="Optional task identifier")
    parser.add_argument("--branch", help="Branch name to work on")
    
    args = parser.parse_args()
    
    try:
        executor = LMStudioTaskExecutorWithTools(
            base_url=args.base_url,
            model_name=args.model
        )
        
        if not args.prompt:
            print("❌ Task prompt required")
            parser.print_help()
            return
        
        result = executor.execute_task(args.prompt, args.task_id, args.branch)
        print(f"\n🎯 Result: {result['message']}")
        print(f"🤖 Model: {executor.model_name}")
        if result['status'] == 'error':
            print(f"❌ Details: {result.get('details', '')}")
    
    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()