#!/usr/bin/env python3
"""
JIRA API Client

Direct JIRA REST API integration using Python requests library.
Provides core JIRA operations for the workflow.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from .config import JiraConfig


class JiraApiError(Exception):
    """Custom exception for JIRA API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class JiraClient:
    """Direct JIRA API client using requests library"""
    
    def __init__(self, config: JiraConfig):
        """
        Initialize JIRA client with configuration
        
        Args:
            config: JiraConfig object with connection details
        """
        self.config = config
        self.session = requests.Session()
        self.session.auth = (config.username, config.api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Set timeout for all requests
        self.timeout = 30
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make authenticated request to JIRA API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (will be prefixed with base_url)
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response object
            
        Raises:
            JiraApiError: If request fails
        """
        url = f"{self.config.base_url}{endpoint}"
        
        # Set default timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            error_msg = f"JIRA API error: {e}"
            try:
                error_detail = response.json()
                if 'errorMessages' in error_detail:
                    error_msg += f" - {', '.join(error_detail['errorMessages'])}"
            except:
                pass
            raise JiraApiError(error_msg, response.status_code, response.text)
        except requests.exceptions.RequestException as e:
            raise JiraApiError(f"Request failed: {e}")
    
    def test_connection(self) -> bool:
        """
        Test connection to JIRA API
        
        Returns:
            bool: True if connection successful
            
        Raises:
            JiraApiError: If connection fails
        """
        try:
            response = self._make_request('GET', '/rest/api/3/myself')
            user_info = response.json()
            print(f"✅ Connected to JIRA as: {user_info.get('displayName', 'Unknown')}")
            return True
        except JiraApiError:
            raise
    
    def get_issue(self, issue_key: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Retrieve a JIRA issue by key
        
        Args:
            issue_key: JIRA issue key (e.g., 'PROJ-123')
            fields: Optional list of fields to retrieve
            
        Returns:
            Dict containing issue data
            
        Raises:
            JiraApiError: If issue not found or access denied
        """
        endpoint = f"/rest/api/3/issue/{issue_key}"
        
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
        
        response = self._make_request('GET', endpoint, params=params)
        return response.json()
    
    def search_issues(self, jql: str, max_results: int = 50, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search issues using JQL (JIRA Query Language)
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            fields: Optional list of fields to retrieve
            
        Returns:
            Dict containing search results
            
        Raises:
            JiraApiError: If search fails
        """
        endpoint = "/rest/api/3/search"
        
        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": fields or ["key", "summary", "status", "assignee", "description"]
        }
        
        response = self._make_request('POST', endpoint, json=payload)
        return response.json()
    
    def get_my_issues(self, status: str = "To Do", max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Get issues assigned to current user
        
        Args:
            status: Issue status to filter by
            max_results: Maximum number of issues to return
            
        Returns:
            List of issue dictionaries
        """
        jql = f'assignee = currentUser() AND status = "{status}" ORDER BY created DESC'
        
        try:
            result = self.search_issues(jql, max_results)
            
            issues = []
            for issue in result.get('issues', []):
                issues.append({
                    "key": issue['key'],
                    "summary": issue['fields']['summary'],
                    "status": issue['fields']['status']['name'],
                    "assignee": issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned'
                })
            
            return issues
        except JiraApiError:
            # Return empty list if search fails (might be permissions issue)
            return []
    
    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """
        Add comment to JIRA issue
        
        Args:
            issue_key: JIRA issue key
            comment: Comment text
            
        Returns:
            Dict containing comment data
            
        Raises:
            JiraApiError: If comment creation fails
        """
        endpoint = f"/rest/api/3/issue/{issue_key}/comment"
        
        # Use Atlassian Document Format (ADF) for comment body
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }
        
        response = self._make_request('POST', endpoint, json=payload)
        return response.json()
    
    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get available transitions for an issue
        
        Args:
            issue_key: JIRA issue key
            
        Returns:
            List of available transitions
        """
        endpoint = f"/rest/api/3/issue/{issue_key}/transitions"
        response = self._make_request('GET', endpoint)
        return response.json().get('transitions', [])
    
    def transition_issue(self, issue_key: str, transition_id: str) -> bool:
        """
        Transition issue to new status
        
        Args:
            issue_key: JIRA issue key
            transition_id: ID of transition to execute
            
        Returns:
            bool: True if transition successful
        """
        endpoint = f"/rest/api/3/issue/{issue_key}/transitions"
        payload = {"transition": {"id": transition_id}}
        
        try:
            self._make_request('POST', endpoint, json=payload)
            return True
        except JiraApiError:
            return False
    
    def extract_description_text(self, issue: Dict[str, Any]) -> str:
        """
        Extract plain text description from JIRA issue ADF format
        
        Args:
            issue: Issue dictionary from JIRA API
            
        Returns:
            str: Plain text description
        """
        description = issue['fields'].get('description')
        if not description:
            return ''
        
        # Handle Atlassian Document Format (ADF)
        content = description.get('content', [])
        text_parts = []
        
        for block in content:
            if block.get('type') == 'paragraph':
                for inline in block.get('content', []):
                    if inline.get('type') == 'text':
                        text_parts.append(inline.get('text', ''))
        
        return ' '.join(text_parts)


if __name__ == "__main__":
    # Example usage and testing
    import argparse
    from .config import load_jira_config
    
    parser = argparse.ArgumentParser(description="JIRA Client Testing")
    parser.add_argument("--test-connection", action="store_true",
                       help="Test JIRA connection")
    parser.add_argument("--issue", help="Get specific issue by key")
    parser.add_argument("--my-issues", action="store_true",
                       help="List my assigned issues")
    parser.add_argument("--config", help="Path to .env file")
    
    args = parser.parse_args()
    
    try:
        config = load_jira_config(args.config)
        client = JiraClient(config)
        
        if args.test_connection:
            client.test_connection()
            print("✅ JIRA connection test successful!")
            
        elif args.issue:
            issue = client.get_issue(args.issue)
            print(f"Issue: {issue['key']}")
            print(f"Summary: {issue['fields']['summary']}")
            print(f"Status: {issue['fields']['status']['name']}")
            print(f"Description: {client.extract_description_text(issue)}")
            
        elif args.my_issues:
            issues = client.get_my_issues()
            if issues:
                print("Your assigned issues:")
                for issue in issues:
                    print(f"  {issue['key']}: {issue['summary']} ({issue['status']})")
            else:
                print("No issues found or no access")
                
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"❌ Error: {e}")