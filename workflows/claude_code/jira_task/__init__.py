"""
JIRA Task Workflow Package

Direct Python API integration for JIRA workflows with Claude Code development assistance.
"""

from .config import JiraConfig, load_jira_config, create_sample_env_file
from .jira_client import JiraClient, JiraApiError
from .git_integration import GitIntegration, GitError
from .jira_task import JiraWorkflow

__version__ = "1.0.0"
__author__ = "Claude Code Workflows"

__all__ = [
    "JiraConfig",
    "load_jira_config", 
    "create_sample_env_file",
    "JiraClient",
    "JiraApiError",
    "GitIntegration", 
    "GitError",
    "JiraWorkflow"
]