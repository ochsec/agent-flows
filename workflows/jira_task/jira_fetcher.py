#!/usr/bin/env python3
"""
Jira Issue Fetching Workflow - Standalone Implementation

This module provides a standalone workflow for fetching Jira issues and
piping them to the task execution workflow, separating issue fetching
from task execution.
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path

from .config import JiraConfig, load_jira_config
from .jira_client import JiraClient, JiraApiError
from .git_integration import GitIntegration, GitError
from .task_executor import TaskExecutor


class JiraIssueFetcher:
    """Standalone Jira issue fetching workflow"""
    
    def __init__(self, jira_config: JiraConfig, repo_path: Optional[str] = None):
        """
        Initialize Jira issue fetcher
        
        Args:
            jira_config: JIRA configuration object
            repo_path: Path to git repository (defaults to current directory)
        """
        self.jira_client = JiraClient(jira_config)
        self.git = GitIntegration(repo_path)
        self.task_executor = TaskExecutor(repo_path)
        
        # State tracking
        self.fetched_issues = {}
    
    def fetch_and_execute_issue(self, issue_key: str, execute_immediately: bool = True) -> Dict[str, Any]:
        """
        Fetch a Jira issue and optionally execute it as a task
        
        Args:
            issue_key: JIRA issue key (e.g., 'PROJ-123')
            execute_immediately: Whether to execute the task immediately
            
        Returns:
            Dict with fetch results and optional execution results
        """
        try:
            print(f"📋 Fetching JIRA issue: {issue_key}")
            
            # Step 1: Fetch issue details
            issue_data = self._fetch_issue_details(issue_key)
            if not issue_data:
                return {"status": "error", "message": f"Failed to fetch issue {issue_key}"}
            
            # Step 2: Create task prompt from issue
            task_prompt = self._create_task_prompt_from_issue(issue_data)
            
            # Step 3: Setup branch
            branch_name = self._create_branch_for_issue(issue_key, issue_data['summary'])
            
            # Step 4: Track the fetched issue
            self.fetched_issues[issue_key] = {
                'issue_data': issue_data,
                'task_prompt': task_prompt,
                'branch_name': branch_name,
                'fetched_at': datetime.now().isoformat(),
                'status': 'fetched'
            }
            
            result = {
                "status": "success",
                "issue_key": issue_key,
                "issue_data": issue_data,
                "task_prompt": task_prompt,
                "branch_name": branch_name,
                "message": f"Successfully fetched {issue_key}"
            }
            
            # Step 5: Execute task if requested
            if execute_immediately:
                print(f"🚀 Executing task for {issue_key}...")
                execution_result = self.task_executor.execute_task(
                    task_prompt=task_prompt,
                    task_id=issue_key,
                    branch_name=branch_name
                )
                
                # Update JIRA with development status
                self._update_jira_with_execution_status(issue_key, execution_result)
                
                result["execution_result"] = execution_result
                self.fetched_issues[issue_key]['status'] = 'executed'
                self.fetched_issues[issue_key]['execution_result'] = execution_result
            
            return result
            
        except Exception as e:
            error_result = {"status": "error", "message": f"Failed to fetch and execute {issue_key}: {e}"}
            print(f"❌ {error_result['message']}")
            return error_result
    
    def _fetch_issue_details(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information about a Jira issue
        
        Args:
            issue_key: JIRA issue key
            
        Returns:
            Dict with issue details or None if error
        """
        try:
            issue = self.jira_client.get_issue(issue_key)
            
            issue_data = {
                "key": issue['key'],
                "summary": issue['fields']['summary'],
                "description": self.jira_client.extract_description_text(issue),
                "status": issue['fields']['status']['name'],
                "assignee": issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
                "priority": issue['fields']['priority']['name'] if issue['fields']['priority'] else 'None',
                "issue_type": issue['fields']['issuetype']['name'],
                "project": issue['fields']['project']['key'],
                "created": issue['fields']['created'],
                "updated": issue['fields']['updated']
            }
            
            # Add labels if available
            if issue['fields'].get('labels'):
                issue_data['labels'] = issue['fields']['labels']
            
            # Add components if available
            if issue['fields'].get('components'):
                issue_data['components'] = [comp['name'] for comp in issue['fields']['components']]
            
            print(f"✅ Fetched issue details for {issue_key}")
            return issue_data
            
        except JiraApiError as e:
            print(f"❌ Error fetching issue {issue_key}: {e}")
            return None
    
    def _create_task_prompt_from_issue(self, issue_data: Dict[str, Any]) -> str:
        """
        Create a comprehensive task prompt from Jira issue data
        
        Args:
            issue_data: Issue information dictionary
            
        Returns:
            Formatted task prompt
        """
        prompt_parts = [
            f"JIRA Issue: {issue_data['key']} - {issue_data['summary']}",
            "",
            f"Issue Type: {issue_data['issue_type']}",
            f"Priority: {issue_data['priority']}",
            f"Status: {issue_data['status']}",
            f"Assignee: {issue_data['assignee']}",
            f"Project: {issue_data['project']}",
            ""
        ]
        
        if issue_data.get('components'):
            prompt_parts.extend([
                f"Components: {', '.join(issue_data['components'])}",
                ""
            ])
        
        if issue_data.get('labels'):
            prompt_parts.extend([
                f"Labels: {', '.join(issue_data['labels'])}",
                ""
            ])
        
        prompt_parts.extend([
            "Description:",
            issue_data['description'] if issue_data['description'] else "No description provided",
            "",
            "Implementation Requirements:",
            "- Analyze the codebase to understand the current implementation",
            "- Implement the requested functionality according to the description",
            "- Follow existing code patterns and conventions",
            "- Add appropriate tests for the new functionality",
            "- Ensure code quality and proper documentation",
            "- Prepare changes for review and potential pull request creation"
        ])
        
        return "\n".join(prompt_parts)
    
    def _create_branch_for_issue(self, issue_key: str, summary: str) -> str:
        """
        Create a feature branch for the issue
        
        Args:
            issue_key: JIRA issue key
            summary: Issue summary
            
        Returns:
            Created branch name
        """
        try:
            branch_name = self.git.create_branch(issue_key, summary)
            print(f"🌿 Created branch: {branch_name}")
            return branch_name
        except GitError as e:
            print(f"⚠️ Git error: {e}")
            # Return a fallback branch name
            return f"feature/{issue_key.lower()}"
    
    def _update_jira_with_execution_status(self, issue_key: str, execution_result: Dict[str, Any]) -> None:
        """
        Update Jira issue with task execution status
        
        Args:
            issue_key: JIRA issue key
            execution_result: Results from task execution
        """
        try:
            if execution_result['status'] == 'success':
                comment = f"""🚀 Development work started for {issue_key}

Branch: {execution_result.get('branch', 'N/A')}
Execution ID: {execution_result.get('execution_id', 'N/A')}

Development assistant has been engaged and will begin implementation.

_Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"""
            else:
                comment = f"""❌ Development setup failed for {issue_key}

Error: {execution_result.get('message', 'Unknown error')}

Please check the issue details and try again.

_Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"""
            
            self.jira_client.add_comment(issue_key, comment)
            print(f"💬 Updated JIRA issue {issue_key} with execution status")
            
        except JiraApiError as e:
            print(f"⚠️ Warning: Could not update JIRA issue {issue_key}: {e}")
    
    def fetch_my_issues(self, status: str = "To Do", max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch issues assigned to current user
        
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
    
    def pipe_issue_to_task_executor(self, issue_key: str, interactive: bool = False) -> Dict[str, Any]:
        """
        Fetch an issue and pipe it to the task executor
        
        Args:
            issue_key: JIRA issue key
            interactive: Whether to use interactive mode
            
        Returns:
            Dict with operation results
        """
        try:
            # Fetch issue if not already fetched
            if issue_key not in self.fetched_issues:
                fetch_result = self.fetch_and_execute_issue(issue_key, execute_immediately=False)
                if fetch_result['status'] != 'success':
                    return fetch_result
            
            issue_info = self.fetched_issues[issue_key]
            
            if interactive:
                print(f"🎭 Starting interactive development mode for {issue_key}")
                self.task_executor.interactive_development_mode(
                    task_prompt=issue_info['task_prompt'],
                    execution_id=issue_key
                )
                return {"status": "success", "message": f"Interactive mode completed for {issue_key}"}
            else:
                print(f"🚀 Executing task for {issue_key}")
                execution_result = self.task_executor.execute_task(
                    task_prompt=issue_info['task_prompt'],
                    task_id=issue_key,
                    branch_name=issue_info['branch_name']
                )
                
                # Update JIRA with execution status
                self._update_jira_with_execution_status(issue_key, execution_result)
                
                return {
                    "status": "success",
                    "message": f"Task executed for {issue_key}",
                    "execution_result": execution_result
                }
                
        except Exception as e:
            error_result = {"status": "error", "message": f"Failed to pipe {issue_key} to task executor: {e}"}
            print(f"❌ {error_result['message']}")
            return error_result
    
    def get_fetched_issues(self) -> Dict[str, Any]:
        """
        Get all fetched issues and their status
        
        Returns:
            Dict of fetched issues
        """
        return self.fetched_issues
    
    def get_issue_task_prompt(self, issue_key: str) -> Optional[str]:
        """
        Get the task prompt for a specific issue
        
        Args:
            issue_key: JIRA issue key
            
        Returns:
            Task prompt string or None if not found
        """
        if issue_key in self.fetched_issues:
            return self.fetched_issues[issue_key]['task_prompt']
        return None


def main():
    """Main entry point for Jira issue fetching workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Jira Issue Fetching Workflow")
    parser.add_argument("issue_key", nargs='?', help="JIRA issue key to fetch (e.g., PROJ-123)")
    parser.add_argument("--command", "-c", 
                       choices=["fetch", "execute", "pipe", "list", "status"], 
                       default="fetch",
                       help="Command to execute (default: fetch)")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Use interactive development mode")
    parser.add_argument("--status-filter", "-s", default="To Do", 
                       help="Issue status filter for list command")
    parser.add_argument("--config", help="Path to .env configuration file")
    parser.add_argument("--execute-immediately", action="store_true",
                       help="Execute task immediately after fetching")
    
    args = parser.parse_args()
    
    try:
        config = load_jira_config(args.config)
        fetcher = JiraIssueFetcher(config)
        
        if args.command == "fetch":
            if not args.issue_key:
                print("❌ Issue key required for fetch command")
                return
            
            result = fetcher.fetch_and_execute_issue(args.issue_key, args.execute_immediately)
            if result["status"] == "success":
                print(f"✅ {result['message']}")
                print(f"📋 Issue: {result['issue_data']['summary']}")
                print(f"🌿 Branch: {result['branch_name']}")
                if 'execution_result' in result:
                    print(f"🚀 Execution: {result['execution_result']['message']}")
            else:
                print(f"❌ {result['message']}")
        
        elif args.command == "execute":
            if not args.issue_key:
                print("❌ Issue key required for execute command")
                return
            
            result = fetcher.pipe_issue_to_task_executor(args.issue_key, args.interactive)
            print(f"{'✅' if result['status'] == 'success' else '❌'} {result['message']}")
        
        elif args.command == "pipe":
            if not args.issue_key:
                print("❌ Issue key required for pipe command")
                return
            
            result = fetcher.pipe_issue_to_task_executor(args.issue_key, args.interactive)
            print(f"{'✅' if result['status'] == 'success' else '❌'} {result['message']}")
        
        elif args.command == "list":
            issues = fetcher.fetch_my_issues(args.status_filter)
            if issues:
                print(f"📋 Your issues with status '{args.status_filter}':")
                for issue in issues:
                    print(f"   {issue['key']}: {issue['summary']}")
            else:
                print(f"No issues found with status '{args.status_filter}'")
        
        elif args.command == "status":
            fetched = fetcher.get_fetched_issues()
            if fetched:
                print("📋 Fetched Issues:")
                for issue_key, info in fetched.items():
                    print(f"   {issue_key}: {info['status']} - {info['issue_data']['summary']}")
            else:
                print("No issues have been fetched yet")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()