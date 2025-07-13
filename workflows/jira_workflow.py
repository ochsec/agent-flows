#!/usr/bin/env python3
"""
JIRA Workflow Integration for Planning Organization Tool

This script implements the complete JIRA workflow:
1. Pull JIRA issues
2. Create prompts based on issue content
3. Invoke the planning organization task tool
4. Update JIRA with progress
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.jira_integration import (
    JiraClient, JiraConfig, JiraIssue, JiraPromptGenerator, load_jira_config
)
from tools.planning_organization import PlanningOrganization


class JiraWorkflow:
    """Main JIRA workflow orchestrator that connects JIRA issues with the planning organization tool."""
    
    def __init__(self, project_path: str, jira_config: Optional[JiraConfig] = None):
        """
        Initialize the JIRA workflow.
        
        Args:
            project_path: Path to the project directory
            jira_config: Optional JIRA configuration. If None, loads from environment
        """
        self.project_path = project_path
        self.jira_config = jira_config or load_jira_config()
        self.jira_client = JiraClient(self.jira_config)
        self.prompt_generator = JiraPromptGenerator()
        self.planning_org = PlanningOrganization(project_path=project_path)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def execute_issue_workflow(self, issue_key: str) -> Dict[str, Any]:
        """
        Execute the complete JIRA workflow for a single issue.
        
        Args:
            issue_key: JIRA issue key (e.g., "PROJ-123")
            
        Returns:
            Dict containing workflow results and status
        """
        workflow_result = {
            "issue_key": issue_key,
            "success": False,
            "stages": {
                "jira_retrieval": {"status": "pending"},
                "prompt_generation": {"status": "pending"}, 
                "task_execution": {"status": "pending"},
                "jira_update": {"status": "pending"}
            },
            "error": None
        }
        
        try:
            # Stage 1: Retrieve JIRA issue
            self.logger.info(f"Retrieving JIRA issue {issue_key}")
            workflow_result["stages"]["jira_retrieval"]["status"] = "in_progress"
            
            issue = self.jira_client.get_issue(issue_key)
            workflow_result["stages"]["jira_retrieval"]["status"] = "completed"
            workflow_result["stages"]["jira_retrieval"]["issue"] = {
                "summary": issue.summary,
                "type": issue.issue_type,
                "status": issue.status,
                "priority": issue.priority
            }
            
            self.logger.info(f"Retrieved issue: {issue.summary} ({issue.issue_type})")
            
            # Stage 2: Generate task prompt
            workflow_result["stages"]["prompt_generation"]["status"] = "in_progress"
            
            description, detailed_prompt = self.prompt_generator.generate_task_prompt(issue)
            workflow_result["stages"]["prompt_generation"]["status"] = "completed"
            workflow_result["stages"]["prompt_generation"]["description"] = description
            workflow_result["stages"]["prompt_generation"]["prompt_length"] = len(detailed_prompt)
            
            self.logger.info(f"Generated prompt: '{description}' ({len(detailed_prompt)} chars)")
            
            # Stage 3: Execute planning organization task
            workflow_result["stages"]["task_execution"]["status"] = "in_progress"
            
            task_result = self.planning_org.task(description, detailed_prompt)
            workflow_result["stages"]["task_execution"]["status"] = "completed"
            workflow_result["stages"]["task_execution"]["result"] = task_result
            
            self.logger.info(f"Task completed successfully with agent {task_result.get('agent_id', 'unknown')}")
            
            # Stage 4: Update JIRA with progress
            workflow_result["stages"]["jira_update"]["status"] = "in_progress"
            
            # Create progress comment for JIRA
            progress_comment = self._format_progress_comment(task_result, issue)
            comment_success = self.jira_client.add_comment(issue_key, progress_comment)
            
            if comment_success:
                workflow_result["stages"]["jira_update"]["status"] = "completed"
                self.logger.info(f"Added progress comment to {issue_key}")
            else:
                workflow_result["stages"]["jira_update"]["status"] = "failed"
                workflow_result["stages"]["jira_update"]["error"] = "Failed to add comment"
                self.logger.warning(f"Failed to add comment to {issue_key}")
            
            workflow_result["success"] = True
            self.logger.info(f"Workflow completed successfully for {issue_key}")
            
        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            workflow_result["error"] = error_msg
            self.logger.error(error_msg, exc_info=True)
            
            # Mark current stage as failed
            for stage_name, stage_data in workflow_result["stages"].items():
                if stage_data["status"] == "in_progress":
                    stage_data["status"] = "failed"
                    stage_data["error"] = str(e)
                    break
        
        return workflow_result
    
    def execute_multiple_issues(self, issue_keys: list[str]) -> Dict[str, Any]:
        """
        Execute workflow for multiple JIRA issues.
        
        Args:
            issue_keys: List of JIRA issue keys
            
        Returns:
            Dict containing results for all issues
        """
        results = {
            "total_issues": len(issue_keys),
            "successful": 0,
            "failed": 0,
            "issues": {}
        }
        
        for issue_key in issue_keys:
            self.logger.info(f"Processing issue {issue_key}")
            issue_result = self.execute_issue_workflow(issue_key)
            results["issues"][issue_key] = issue_result
            
            if issue_result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
        
        self.logger.info(f"Batch processing complete: {results['successful']}/{results['total_issues']} successful")
        return results
    
    def search_and_execute(self, jql_query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for issues using JQL and execute workflow for found issues.
        
        Args:
            jql_query: JQL query string
            max_results: Maximum number of issues to process
            
        Returns:
            Dict containing search and execution results
        """
        try:
            self.logger.info(f"Searching issues with JQL: {jql_query}")
            issues = self.jira_client.search_issues(jql_query, max_results)
            
            if not issues:
                return {
                    "success": True,
                    "message": "No issues found matching the JQL query",
                    "issues_found": 0,
                    "issues_processed": 0
                }
            
            issue_keys = [issue.key for issue in issues]
            self.logger.info(f"Found {len(issues)} issues to process")
            
            results = self.execute_multiple_issues(issue_keys)
            results["jql_query"] = jql_query
            results["issues_found"] = len(issues)
            results["issues_processed"] = len(issue_keys)
            
            return results
            
        except Exception as e:
            error_msg = f"Search and execute failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "jql_query": jql_query
            }
    
    def _format_progress_comment(self, task_result: Dict[str, Any], issue: JiraIssue) -> str:
        """Format a progress comment for JIRA based on task execution results."""
        comment_parts = [
            f"🤖 Automated Analysis Complete for {issue.issue_type}: {issue.summary}",
            "",
            f"**Agent Used:** {task_result.get('mode', 'Unknown')} (ID: {task_result.get('agent_id', 'N/A')})",
            f"**Status:** {task_result.get('status', 'Unknown')}",
            f"**Execution Time:** {task_result.get('execution_time', 'N/A')} seconds",
            "",
            "**Analysis Summary:**"
        ]
        
        # Add truncated response for the comment
        response = task_result.get('response', '')
        if len(response) > 500:
            response = response[:497] + "..."
        
        comment_parts.extend([
            response,
            "",
            "---",
            "*This comment was automatically generated by the JIRA workflow integration*"
        ])
        
        return "\n".join(comment_parts)
    
    def test_connection(self) -> bool:
        """Test JIRA connection and authentication."""
        try:
            success = self.jira_client.test_connection()
            if success:
                self.logger.info("JIRA connection test successful")
            else:
                self.logger.error("JIRA connection test failed")
            return success
        except Exception as e:
            self.logger.error(f"JIRA connection test error: {str(e)}")
            return False


def main():
    """Command-line interface for the JIRA workflow."""
    parser = argparse.ArgumentParser(description="JIRA Workflow Integration for Planning Organization")
    parser.add_argument("--project-path", default=".", help="Path to project directory")
    parser.add_argument("--test-connection", action="store_true", help="Test JIRA connection only")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Single issue command
    issue_parser = subparsers.add_parser("issue", help="Process a single JIRA issue")
    issue_parser.add_argument("issue_key", help="JIRA issue key (e.g., PROJ-123)")
    
    # Multiple issues command
    issues_parser = subparsers.add_parser("issues", help="Process multiple JIRA issues")
    issues_parser.add_argument("issue_keys", nargs="+", help="JIRA issue keys")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search and process issues using JQL")
    search_parser.add_argument("jql_query", help="JQL query string")
    search_parser.add_argument("--max-results", type=int, default=10, help="Maximum results to process")
    
    args = parser.parse_args()
    
    try:
        # Initialize workflow
        workflow = JiraWorkflow(project_path=args.project_path)
        
        # Test connection if requested
        if args.test_connection:
            success = workflow.test_connection()
            sys.exit(0 if success else 1)
        
        # Execute commands
        if args.command == "issue":
            result = workflow.execute_issue_workflow(args.issue_key)
            print(f"Issue {args.issue_key}: {'SUCCESS' if result['success'] else 'FAILED'}")
            if not result['success']:
                print(f"Error: {result['error']}")
        
        elif args.command == "issues":
            result = workflow.execute_multiple_issues(args.issue_keys)
            print(f"Processed {result['total_issues']} issues: {result['successful']} successful, {result['failed']} failed")
        
        elif args.command == "search":
            result = workflow.search_and_execute(args.jql_query, args.max_results)
            if result.get('success', True):
                print(f"Found {result.get('issues_found', 0)} issues, processed {result.get('issues_processed', 0)}")
                if 'successful' in result:
                    print(f"Results: {result['successful']} successful, {result['failed']} failed")
            else:
                print(f"Search failed: {result['error']}")
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nWorkflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Workflow error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()