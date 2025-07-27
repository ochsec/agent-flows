#!/usr/bin/env python3
"""
Task Execution Workflow - Standalone Implementation

This module provides a standalone task execution workflow that can be invoked
with a prompt from any source, separating task execution from task fetching.
"""

import os
import subprocess
import json
from datetime import datetime
from typing import Dict, Optional, Any, List
from pathlib import Path

from .git_integration import GitIntegration, GitError


class TaskExecutor:
    """Standalone task execution workflow"""
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize task executor
        
        Args:
            repo_path: Path to git repository (defaults to current directory)
        """
        self.git = GitIntegration(repo_path)
        self.current_branch = None
        
        # Execution state tracking
        self.execution_state = {}
    
    def execute_task(self, task_prompt: str, task_id: Optional[str] = None, branch_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task from a given prompt
        
        Args:
            task_prompt: The task description/prompt to execute
            task_id: Optional task identifier for tracking
            branch_name: Optional branch name (will create if doesn't exist)
            
        Returns:
            Dict with execution results
        """
        try:
            print(f"🚀 Starting task execution...")
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
                'prompt': task_prompt[:100] + "..." if len(task_prompt) > 100 else task_prompt
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
            # Check if branch exists
            if self.git.branch_exists(branch_name):
                print(f"🔄 Switching to existing branch: {branch_name}")
                self.git.checkout_branch(branch_name)
            else:
                print(f"🌿 Creating new branch: {branch_name}")
                self.git.create_branch_simple(branch_name)
            
            self.current_branch = branch_name
            
        except GitError as e:
            print(f"⚠️ Branch setup warning: {e}")
            # Continue with current branch
            self.current_branch = self.git.get_current_branch()
    
    def _execute_development_workflow(self, task_prompt: str, execution_id: str) -> Dict[str, Any]:
        """
        Execute the development workflow with Claude Code integration
        
        Args:
            task_prompt: The task description/prompt
            execution_id: Unique execution identifier
            
        Returns:
            Dict with execution results
        """
        print("🤖 Launching Claude Code development assistant...")
        
        # Create comprehensive development prompt
        development_prompt = f"""You are a development assistant executing task ID: {execution_id}

Task Description:
{task_prompt}

You have access to all development tools including:
- File operations (read, write, edit, multiEdit)
- Code search (glob, grep)
- Directory listing (ls)
- Shell commands (bash for cp, mv, ls, grep)
- Git operations (commits, branching)
- Package managers (npm, cargo)
- Python tools (python, pytest)
- Web search for documentation

Please:
1. Analyze the current codebase structure using ls and grep
2. Understand the requirements from the task description
3. Implement the necessary changes
4. Test the implementation
5. Review and prepare for commit if appropriate

Provide a comprehensive implementation of the requested task."""
        
        # Execute with Claude Code
        result = self._execute_claude_command(development_prompt)
        
        if "Error:" in result:
            return {"status": "error", "message": "Claude Code execution failed", "details": result}
        
        print(f"✅ Task execution completed")
        return {"status": "success", "message": "Task executed successfully", "details": result}
    
    def _execute_claude_command(self, prompt: str) -> str:
        """
        Execute Claude Code command with full development permissions
        
        Args:
            prompt: Prompt for Claude Code
            
        Returns:
            Claude Code response
        """
        # Claude Code command with comprehensive development permissions
        command = [
            "claude", "-p",  # Print mode for programmatic use
            "--verbose",
            "--model", "sonnet",
            "--allowedTools", "read,write,edit,multiEdit,glob,grep,ls,bash,git,npm,cargo,python,pytest,webSearch,task"
        ]
        
        try:
            working_dir = os.getenv('ORIGINAL_PWD', os.getcwd())
            result = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=1800
            )
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 minutes"
        except Exception as e:
            return f"Failed to execute Claude command: {e}"
    
    def interactive_development_mode(self, task_prompt: str, execution_id: str) -> None:
        """
        Enter interactive development mode for complex tasks
        
        Args:
            task_prompt: The task description
            execution_id: Unique execution identifier
        """
        print(f"🚀 Entering interactive development mode for task: {execution_id}")
        print("Available commands:")
        print("  - 'analyze': Analyze codebase for relevant files")
        print("  - 'implement': Get implementation suggestions")
        print("  - 'test': Create or run tests")
        print("  - 'review': Review changes before commit")
        print("  - 'done': Complete task and prepare for commit")
        print("  - 'quit': Exit without completing")
        
        while True:
            print("\n" + "="*50)
            user_input = input(f"\n👷 [{execution_id}] What would you like to do? (help/analyze/implement/test/review/done/quit): ").strip().lower()
            
            if user_input == 'quit':
                print(f"👋 Exiting development mode for task {execution_id}")
                break
                
            elif user_input == 'done':
                self._complete_task(execution_id, task_prompt)
                break
                
            elif user_input == 'help':
                self._show_help()
                
            elif user_input == 'analyze':
                self._analyze_codebase(task_prompt)
                
            elif user_input == 'implement':
                self._get_implementation_help(task_prompt)
                
            elif user_input == 'test':
                self._handle_testing(task_prompt)
                
            elif user_input == 'review':
                self._review_changes(execution_id)
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
    
    def _analyze_codebase(self, task_prompt: str) -> None:
        """Analyze codebase for task-related files"""
        analyze_prompt = f"""Analyze the codebase for the following task:

Task: {task_prompt}

Please:
1. Use ls to explore the project structure
2. Use grep to search for relevant code patterns
3. Identify files that need modification
4. Suggest where new files should be created
5. Provide specific file paths and reasoning

Focus on finding the exact files that relate to this task."""
        
        result = self._execute_claude_command(analyze_prompt)
        print(f"🔍 Codebase Analysis:\n{result}")

    def _get_implementation_help(self, task_prompt: str) -> None:
        """Get specific implementation assistance"""
        implement_prompt = f"""Provide implementation help for the following task:

Task: {task_prompt}

Please:
1. Read the relevant files to understand current implementation
2. Provide specific code changes needed
3. Use edit or multiEdit to make suggested changes
4. Explain the changes and their impact
5. Suggest any additional files that need creation

Make concrete code changes where appropriate."""
        
        result = self._execute_claude_command(implement_prompt)
        print(f"🛠️ Implementation Assistance:\n{result}")

    def _handle_testing(self, task_prompt: str) -> None:
        """Handle testing for the task"""
        test_prompt = f"""Handle testing for the following task:

Task: {task_prompt}

Please:
1. Identify existing test files and patterns
2. Create or update tests for the changes
3. Run tests using pytest or appropriate test runner
4. Report test results and fix any failures
5. Ensure good test coverage for the new functionality

Use the testing tools available to create comprehensive tests."""
        
        result = self._execute_claude_command(test_prompt)
        print(f"🧪 Testing Results:\n{result}")

    def _review_changes(self, execution_id: str) -> None:
        """Review all changes made for the task"""
        review_prompt = f"""Review all changes made for task {execution_id}.

Please:
1. Use git commands to see what files have been modified
2. Review the changes for code quality and style
3. Check that all requirements are met
4. Run any linting or formatting tools
5. Prepare a summary of changes
6. Suggest a commit message

Provide a comprehensive review of the current state."""
        
        result = self._execute_claude_command(review_prompt)
        print(f"🔍 Change Review:\n{result}")

    def _complete_task(self, execution_id: str, task_prompt: str) -> None:
        """Complete the task with commits and cleanup"""
        print(f"🏁 Completing task {execution_id}...")
        
        completion_prompt = f"""Complete the development task {execution_id}:

Original task: {task_prompt}

1. Run final tests to ensure everything works
2. Check code quality and formatting
3. Review all changes with git status and git diff
4. Create a proper git commit with descriptive message
5. Provide a summary of what was accomplished

Perform all necessary steps to complete the development cycle."""
        
        completion_result = self._execute_claude_command(completion_prompt)
        print(f"🔍 Completion Process:\n{completion_result}")
        
        print(f"✅ Task {execution_id} completed!")

    def _show_help(self) -> None:
        """Show available commands and their descriptions"""
        help_text = """
📚 Available Development Commands:

🔍 analyze    - Analyze codebase to find relevant files for this task
🛠️  implement  - Get specific implementation help and code suggestions  
🧪 test       - Create/run tests for the implemented functionality
🔍 review     - Review all changes and prepare for commit
🏁 done       - Complete the task workflow and prepare commit
👋 quit       - Exit development mode
📚 help       - Show this help message

Each command will launch Claude Code with full development permissions to:
- Read/write/edit files
- Search codebase (grep, glob)
- Run shell commands (bash, git)
- Use development tools (npm, cargo, python, pytest)"""
        print(help_text)

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific execution
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Dict with execution status or None if not found
        """
        return self.execution_state.get(execution_id)

    def list_executions(self) -> List[Dict[str, Any]]:
        """
        List all executions with their status
        
        Returns:
            List of execution status dictionaries
        """
        return [
            {"execution_id": eid, **status}
            for eid, status in self.execution_state.items()
        ]


def main():
    """Main entry point for standalone task execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Standalone Task Execution Workflow")
    parser.add_argument("prompt", nargs='?', help="Task prompt to execute")
    parser.add_argument("--task-id", help="Optional task identifier")
    parser.add_argument("--branch", help="Branch name to work on")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Enter interactive development mode")
    parser.add_argument("--status", help="Get status of specific execution ID")
    parser.add_argument("--list", action="store_true", help="List all executions")
    
    args = parser.parse_args()
    
    try:
        executor = TaskExecutor()
        
        if args.list:
            executions = executor.list_executions()
            if executions:
                print("📋 Task Executions:")
                for execution in executions:
                    print(f"   {execution['execution_id']}: {execution['status']} - {execution['prompt']}")
            else:
                print("No task executions found")
            return
        
        if args.status:
            status = executor.get_execution_status(args.status)
            if status:
                print(f"📋 Execution: {args.status}")
                print(f"📊 Status: {status['status']}")
                print(f"🌿 Branch: {status.get('branch', 'N/A')}")
                print(f"⏰ Started: {status['started_at']}")
                if 'completed_at' in status:
                    print(f"🏁 Completed: {status['completed_at']}")
                print(f"📝 Prompt: {status['prompt']}")
            else:
                print(f"❌ Execution {args.status} not found")
            return
        
        if not args.prompt:
            print("❌ Task prompt required")
            parser.print_help()
            return
        
        if args.interactive:
            execution_id = args.task_id or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            executor.interactive_development_mode(args.prompt, execution_id)
        else:
            result = executor.execute_task(args.prompt, args.task_id, args.branch)
            print(f"🎯 Result: {result['message']}")
            if result['status'] == 'error':
                print(f"❌ Details: {result.get('details', '')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()