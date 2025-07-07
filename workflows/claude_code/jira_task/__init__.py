"""
JIRA Task Workflow Package

Direct Python API integration for JIRA workflows with Claude Code development assistance.
Includes Phase 2 enhanced features for professional development workflows.
"""

from .config import JiraConfig, load_jira_config, create_sample_env_file
from .jira_client import JiraClient, JiraApiError
from .git_integration import GitIntegration, GitError
from .jira_task import JiraWorkflow

# Phase 2 Enhanced Features
try:
    from .enhanced_workflow import EnhancedJiraWorkflow, WorkflowContext, EnhancedClaudeCodeClient
    from .pr_creator import GitHubPRCreator, PRCreationError
    _ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    _ENHANCED_FEATURES_AVAILABLE = False

# Phase 3 Advanced Features
try:
    from .advanced_automation import (
        AdvancedJiraWorkflow, ProjectConfig, ProjectType, 
        WorkflowTemplate, TemplateManager, MultiProjectManager, CIPipelineIntegration
    )
    from .analytics import WorkflowAnalytics, AnalyticsDatabase, ReportGenerator
    _ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    _ADVANCED_FEATURES_AVAILABLE = False

__version__ = "3.0.0"
__author__ = "Claude Code Workflows"

__all__ = [
    # Core Components
    "JiraConfig",
    "load_jira_config", 
    "create_sample_env_file",
    "JiraClient",
    "JiraApiError",
    "GitIntegration", 
    "GitError",
    "JiraWorkflow"
]

# Add enhanced features to exports if available
if _ENHANCED_FEATURES_AVAILABLE:
    __all__.extend([
        "EnhancedJiraWorkflow",
        "WorkflowContext", 
        "EnhancedClaudeCodeClient",
        "GitHubPRCreator",
        "PRCreationError"
    ])

# Add advanced features to exports if available  
if _ADVANCED_FEATURES_AVAILABLE:
    __all__.extend([
        "AdvancedJiraWorkflow",
        "ProjectConfig",
        "ProjectType",
        "WorkflowTemplate", 
        "TemplateManager",
        "MultiProjectManager",
        "CIPipelineIntegration",
        "WorkflowAnalytics",
        "AnalyticsDatabase",
        "ReportGenerator"
    ])