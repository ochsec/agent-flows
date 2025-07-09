#!/usr/bin/env python3
"""
JIRA Task Workflow - Main Implementation

This module implements the JIRA task workflow described in the research report,
providing direct Python API integration for Claude Code development assistance.
"""

import os
import subprocess
import json
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path

from .config import JiraConfig, load_jira_config
from .jira_client import JiraClient, JiraApiError
from .git_integration import GitIntegration, GitError


class JiraWorkflow:
    """Main JIRA workflow orchestrator"""
    
    def __init__(self, jira_config: JiraConfig, repo_path: Optional[str] = None):
        """
        Initialize JIRA workflow
        
        Args:
            jira_config: JIRA configuration object
            repo_path: Path to git repository (defaults to current directory)
        """
        self.jira_client = JiraClient(jira_config)
        self.git = GitIntegration(repo_path)
        self.current_issue = None
        self.current_branch = None
        
        # Workflow state tracking
        self.workflow_state = {}
    
    def start_work_on_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Start working on a JIRA issue
        
        Phase 1: Initial Setup
        1. Retrieve issue details and validate access
        2. Create feature branch with standardized naming
        3. Add comment to JIRA indicating development started
        
        Args:
            issue_key: JIRA issue key (e.g., 'PROJ-123')
            
        Returns:
            Dict with status and issue information
        """
        try:
            print(f"🚀 Starting work on JIRA issue: {issue_key}")
            
            # Step 1: Get issue details
            print("📋 Retrieving issue details...")
            issue = self.jira_client.get_issue(issue_key)
            self.current_issue = issue
            
            issue_info = {
                "key": issue['key'],
                "summary": issue['fields']['summary'],
                "description": self.jira_client.extract_description_text(issue),
                "status": issue['fields']['status']['name'],
                "assignee": issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned'
            }
            
            # Step 2: Create feature branch
            print("🌿 Creating feature branch...")
            summary = issue['fields']['summary']
            branch_name = self.git.create_branch(issue_key, summary)
            self.current_branch = branch_name
            
            # Step 3: Add comment to JIRA
            print("💬 Updating JIRA with development status...")
            comment = f"🚀 Started development work on branch: {branch_name}\\n\\nBranch created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.jira_client.add_comment(issue_key, comment)
            
            # Track workflow state
            self.workflow_state[issue_key] = {
                'status': 'in_progress',
                'branch': branch_name,
                'started_at': datetime.now().isoformat(),
                'issue_summary': summary
            }
            
            result = {
                "status": "success",
                "issue": issue_info,
                "branch": branch_name,
                "message": f"Ready to work on {issue_key}: {summary}"
            }
            
            print(f"✅ {result['message']}")
            print(f"📋 Issue: {issue_info['summary']}")
            print(f"🌿 Branch: {branch_name}")
            if issue_info['description']:
                print(f"📝 Description: {issue_info['description'][:100]}...")
            
            return result
            
        except (JiraApiError, GitError) as e:
            error_result = {"status": "error", "message": str(e)}
            print(f"❌ {error_result['message']}")
            return error_result
        except Exception as e:
            error_result = {"status": "error", "message": f"Unexpected error: {e}"}
            print(f"❌ {error_result['message']}")
            return error_result
    
    def find_my_issues(self, status: str = "To Do", max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Find issues assigned to current user
        
        Args:
            status: Issue status to filter by
            max_results: Maximum number of issues to return
            
        Returns:
            List of issue dictionaries
        """
        try:
            return self.jira_client.get_my_issues(status, max_results)
        except JiraApiError as e:
            print(f"❌ Error finding issues: {e}")
            return []
    
    def update_progress(self, issue_key: str, progress_comment: str) -> bool:
        """
        Update issue progress with comment
        
        Args:
            issue_key: JIRA issue key
            progress_comment: Progress update comment
            
        Returns:
            True if update successful
        """
        try:
            # Add timestamp to comment
            timestamped_comment = f"{progress_comment}\\n\\n_Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
            self.jira_client.add_comment(issue_key, timestamped_comment)
            return True
        except JiraApiError as e:
            print(f"❌ Error updating progress: {e}")
            return False
    
    def get_issue_status(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of an issue
        
        Args:
            issue_key: JIRA issue key
            
        Returns:
            Dict with issue status information or None if error
        """
        try:
            issue = self.jira_client.get_issue(issue_key)
            return {
                "key": issue['key'],
                "summary": issue['fields']['summary'],
                "status": issue['fields']['status']['name'],
                "assignee": issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
                "description": self.jira_client.extract_description_text(issue)
            }
        except JiraApiError as e:
            print(f"❌ Error getting issue status: {e}")
            return None
    
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
            "--allowedTools", 
            "read,write,edit,multiEdit,glob,grep,ls,bash,git,npm,cargo,python,pytest,webSearch,task"
        ]
        
        try:
            result = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout for complex development tasks
            )
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 minutes"
        except Exception as e:
            return f"Failed to execute Claude command: {e}"
    
    def execute_development_workflow(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """
        Execute complete development workflow with Claude Code integration
        
        Phase 2: Development Assistance (Claude Code Integration)
        1. Analysis: Claude Code analyzes the issue requirements
        2. Planning: Creates a step-by-step development plan
        3. Interactive Mode: Enters interactive development assistance
        
        Args:
            issue_key: JIRA issue key
            issue_data: Issue information dictionary
        """
        # Step 1: Analyze the issue and create development plan
        print("📅 Creating development plan...")
        plan_prompt = f"""You are a development assistant helping with JIRA issue {issue_key}: {issue_data['summary']}

Description: {issue_data['description']}

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
2. Identify the files that likely need changes
3. Create a step-by-step development plan
4. Suggest the first concrete action to take

Start by exploring the codebase to understand the current architecture and then provide an actionable development plan."""
        
        # Use Claude Code to create development plan
        plan_result = self._execute_claude_command(plan_prompt)
        print(f"📝 Development Plan:\\n{plan_result}")
        
        # Step 2: Interactive development assistance
        print("\\n🚀 Ready for development! Claude Code will assist you.")
        print("Available commands:")
        print("  - 'analyze': Analyze codebase for relevant files")
        print("  - 'implement': Get implementation suggestions")
        print("  - 'test': Create or run tests")
        print("  - 'review': Review changes before commit")
        print("  - 'done': Mark issue complete and create PR")
        
        # Step 3: Enter interactive mode
        self._interactive_development_mode(issue_key, issue_data)
    
    def _interactive_development_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Interactive development assistance mode"""
        
        while True:
            print("\\n" + "="*50)
            user_input = input(f"\\n👷 [{issue_key}] What would you like to do? (help/analyze/implement/test/review/done/quit): ").strip().lower()
            
            if user_input == 'quit':
                print(f"👋 Exiting development mode. Use 'python jira_task.py {issue_key} -c update' to add progress comments.")
                break
                
            elif user_input == 'done':
                self._complete_issue_workflow(issue_key)
                break
                
            elif user_input == 'help':
                self._show_help()
                
            elif user_input == 'analyze':
                self._analyze_codebase(issue_key, issue_data)
                
            elif user_input == 'implement':
                self._get_implementation_help(issue_key, issue_data)
                
            elif user_input == 'test':
                self._handle_testing(issue_key, issue_data)
                
            elif user_input == 'review':
                self._review_changes(issue_key)
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")

    def _analyze_codebase(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Analyze codebase for issue-related files"""
        analyze_prompt = f"""Analyze the codebase for JIRA issue {issue_key}: {issue_data['summary']}

Description: {issue_data['description']}

Please:
1. Use ls to explore the project structure
2. Use grep to search for relevant code patterns
3. Identify files that need modification
4. Suggest where new files should be created
5. Provide specific file paths and reasoning

Focus on finding the exact files that relate to this issue."""
        
        result = self._execute_claude_command(analyze_prompt)
        print(f"🔍 Codebase Analysis:\\n{result}")

    def _get_implementation_help(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Get specific implementation assistance"""
        implement_prompt = f"""Provide implementation help for JIRA issue {issue_key}: {issue_data['summary']}

Description: {issue_data['description']}

Please:
1. Read the relevant files to understand current implementation
2. Provide specific code changes needed
3. Use edit or multiEdit to make suggested changes
4. Explain the changes and their impact
5. Suggest any additional files that need creation

Make concrete code changes where appropriate."""
        
        result = self._execute_claude_command(implement_prompt)
        print(f"🛠️ Implementation Assistance:\\n{result}")

    def _handle_testing(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Handle testing for the issue"""
        test_prompt = f"""Handle testing for JIRA issue {issue_key}: {issue_data['summary']}

Description: {issue_data['description']}

Please:
1. Identify existing test files and patterns
2. Create or update tests for the changes
3. Run tests using pytest or appropriate test runner
4. Report test results and fix any failures
5. Ensure good test coverage for the new functionality

Use the testing tools available to create comprehensive tests."""
        
        result = self._execute_claude_command(test_prompt)
        print(f"🧪 Testing Results:\\n{result}")

    def _review_changes(self, issue_key: str) -> None:
        """Review all changes made for the issue"""
        review_prompt = f"""Review all changes made for JIRA issue {issue_key}.

Please:
1. Use git commands to see what files have been modified
2. Review the changes for code quality and style
3. Check that all requirements are met
4. Run any linting or formatting tools
5. Prepare a summary of changes
6. Suggest a commit message

Provide a comprehensive review of the current state."""
        
        result = self._execute_claude_command(review_prompt)
        print(f"🔍 Change Review:\\n{result}")

    def _show_help(self) -> None:
        """Show available commands and their descriptions"""
        help_text = """
📚 Available Development Commands:

🔍 analyze    - Analyze codebase to find relevant files for this issue
🛠️  implement  - Get specific implementation help and code suggestions  
🧪 test       - Create/run tests for the implemented functionality
🔍 review     - Review all changes and prepare for commit
🏁 done       - Complete the issue workflow and prepare PR
👋 quit       - Exit development mode (save progress first)
📚 help       - Show this help message

Each command will launch Claude Code with full development permissions to:
- Read/write/edit files
- Search codebase (grep, glob)
- Run shell commands (bash, git)
- Use development tools (npm, cargo, python, pytest)
- Create commits and prepare PRs"""
        print(help_text)

    def _complete_issue_workflow(self, issue_key: str) -> None:
        """Complete the development workflow with commits and PR creation"""
        print(f"🏁 Completing work on {issue_key}...")
        
        # Run final checks and create commit
        completion_prompt = f"""Complete the development workflow for JIRA issue {issue_key}:

1. Run final tests to ensure everything works
2. Check code quality and formatting
3. Review all changes with git status and git diff
4. Create a proper git commit with descriptive message
5. Push the branch to remote
6. Create a pull request using GitHub CLI (gh pr create)
7. Provide PR title and description referencing the JIRA issue

Perform all necessary steps to complete the development cycle.
Use the available tools to make commits and create the PR."""
        
        completion_result = self._execute_claude_command(completion_prompt)
        print(f"🔍 Completion Process:\\n{completion_result}")
        
        # Update JIRA with completion and PR link
        completion_comment = f"""🏆 Development completed for {issue_key}

Final summary:
{completion_result[:800]}...

Next steps: Review and merge the pull request."""
        
        self.jira_client.add_comment(issue_key, completion_comment)
        
        print(f"✅ Issue {issue_key} completed and PR created!")
        print("🔗 Check your repository for the new pull request")


def main():
    """Main entry point for JIRA workflow - follows research.py pattern"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JIRA Task Workflow Integration - Claude Code")
    parser.add_argument("issue_key", nargs='?', help="JIRA issue key to work on (e.g., PROJ-123)")
    parser.add_argument("--command", "-c", 
                       choices=["start", "list", "update", "status", "configure"], 
                       default="start",
                       help="Command to execute (default: start)")
    parser.add_argument("--comment", help="Progress comment for update command")
    parser.add_argument("--status-filter", "-s", default="To Do", 
                       help="Issue status filter for list command")
    parser.add_argument("--config", help="Path to .env configuration file")
    parser.add_argument("--enhanced", action="store_true",
                       help="Use enhanced workflow with Phase 2 features")
    parser.add_argument("--advanced", action="store_true",
                       help="Use advanced workflow with Phase 3 features (includes enhanced)")
    parser.add_argument("--enterprise", action="store_true",
                       help="Use enterprise workflow with Phase 4 features (includes all previous phases)")
    parser.add_argument("--agent-modes", action="store_true",
                       help="Use agent-flows mode-based workflow with Phase 5 features (includes all previous phases)")
    parser.add_argument("--modes-path", help="Path to agent-flows modes directory (default: ./modes)")
    parser.add_argument("--project", help="Specify project name for multi-project support")
    parser.add_argument("--user", help="Current user for enterprise features")
    
    args = parser.parse_args()
    
    try:
        config = load_jira_config(args.config)
        
        # Use agent-flows mode-based workflow if requested (Phase 5)
        if args.agent_modes:
            try:
                from .mode_based_workflow import ModeBasedJiraWorkflow
                from pathlib import Path
                
                current_user = args.user or os.getenv("USER", "unknown")
                modes_path = Path(args.modes_path) if args.modes_path else None
                workflow = ModeBasedJiraWorkflow(config, current_user=current_user, modes_path=modes_path)
                print("🎭 Using agent-flows mode-based workflow with Phase 5 features")
            except ImportError as e:
                print(f"⚠️  Agent-flows mode-based workflow not available: {e}")
                print("   Falling back to enterprise workflow")
                try:
                    from .enterprise_workflow import EnterpriseJiraWorkflow
                    current_user = args.user or os.getenv("USER", "unknown")
                    workflow = EnterpriseJiraWorkflow(config, current_user=current_user)
                    print("🏢 Using enterprise workflow with Phase 4 features")
                except ImportError:
                    print("⚠️  Enterprise workflow not available, falling back to advanced workflow")
                    try:
                        from .advanced_automation import AdvancedJiraWorkflow
                        workflow = AdvancedJiraWorkflow(config)
                        print("🚀 Using advanced workflow with Phase 3 features")
                    except ImportError:
                        print("⚠️  Advanced workflow not available, falling back to enhanced workflow")
                        try:
                            from .enhanced_workflow import EnhancedJiraWorkflow
                            workflow = EnhancedJiraWorkflow(config)
                            print("✨ Using enhanced workflow with Phase 2 features")
                        except ImportError:
                            print("⚠️  Enhanced workflow not available, using standard workflow")
                            workflow = JiraWorkflow(config)
        # Use enterprise workflow if requested (Phase 4)
        elif args.enterprise:
            try:
                from .enterprise_workflow import EnterpriseJiraWorkflow
                current_user = args.user or os.getenv("USER", "unknown")
                workflow = EnterpriseJiraWorkflow(config, current_user=current_user)
                print("🏢 Using enterprise workflow with Phase 4 features")
            except ImportError:
                print("⚠️  Enterprise workflow not available, falling back to advanced workflow")
                try:
                    from .advanced_automation import AdvancedJiraWorkflow
                    workflow = AdvancedJiraWorkflow(config)
                    print("🚀 Using advanced workflow with Phase 3 features")
                except ImportError:
                    print("⚠️  Advanced workflow not available, falling back to enhanced workflow")
                    try:
                        from .enhanced_workflow import EnhancedJiraWorkflow
                        workflow = EnhancedJiraWorkflow(config)
                        print("✨ Using enhanced workflow with Phase 2 features")
                    except ImportError:
                        print("⚠️  Enhanced workflow not available, using standard workflow")
                        workflow = JiraWorkflow(config)
        # Use advanced workflow if requested (Phase 3)
        elif args.advanced:
            try:
                from .advanced_automation import AdvancedJiraWorkflow
                workflow = AdvancedJiraWorkflow(config)
                print("🚀 Using advanced workflow with Phase 3 features")
            except ImportError:
                print("⚠️  Advanced workflow not available, falling back to enhanced workflow")
                try:
                    from .enhanced_workflow import EnhancedJiraWorkflow
                    workflow = EnhancedJiraWorkflow(config)
                    print("✨ Using enhanced workflow with Phase 2 features")
                except ImportError:
                    print("⚠️  Enhanced workflow not available, using standard workflow")
                    workflow = JiraWorkflow(config)
        # Use enhanced workflow if requested (Phase 2)
        elif args.enhanced:
            try:
                from .enhanced_workflow import EnhancedJiraWorkflow
                workflow = EnhancedJiraWorkflow(config)
                print("✨ Using enhanced workflow with Phase 2 features")
            except ImportError:
                print("⚠️  Enhanced workflow not available, using standard workflow")
                workflow = JiraWorkflow(config)
        else:
            workflow = JiraWorkflow(config)
        
        if args.command == "start":
            # Check if this is a Phase 5 mode-based workflow
            if hasattr(workflow, 'start_mode_based_workflow'):
                # Phase 5: Agent-flows mode-based workflow
                workflow.start_mode_based_workflow(args.issue_key)
            else:
                # Phases 1-4: Traditional workflows
                result = workflow.start_work_on_issue(args.issue_key)
                if result["status"] == "success":
                    # Continue with development workflow
                    print("\\n🤖 Launching Claude Code development assistant...")
                    workflow.execute_development_workflow(args.issue_key, result['issue'])
            
        elif args.command == "list":
            issues = workflow.find_my_issues(args.status_filter)
            if issues:
                print(f"📋 Your issues with status '{args.status_filter}':")
                for issue in issues:
                    print(f"   {issue['key']}: {issue['summary']}")
            else:
                print(f"No issues found with status '{args.status_filter}'")
        
        elif args.command == "update":
            if not args.comment:
                print("❌ Comment required for update command (use --comment)")
                return
            
            success = workflow.update_progress(args.issue_key, args.comment)
            if success:
                print(f"✅ Updated {args.issue_key} with progress comment")
            else:
                print(f"❌ Failed to update {args.issue_key}")
        
        elif args.command == "status":
            issue_status = workflow.get_issue_status(args.issue_key)
            if issue_status:
                print(f"📋 Issue: {args.issue_key}")
                print(f"📝 Summary: {issue_status['summary']}")
                print(f"📊 Status: {issue_status['status']}")
                print(f"👤 Assignee: {issue_status['assignee']}")
                if issue_status['description']:
                    print(f"📄 Description: {issue_status['description'][:200]}...")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()