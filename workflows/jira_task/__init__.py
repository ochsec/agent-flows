"""
JIRA Task Workflow Package

Direct Python API integration for JIRA workflows with Claude Code development assistance.
Includes Phase 2 enhanced features for professional development workflows.
"""

from .config import JiraConfig, load_jira_config, create_sample_env_file
from .jira_client import JiraClient, JiraApiError
from .git_integration import GitIntegration, GitError
from .jira_task import JiraWorkflow
from .task_executor import TaskExecutor
from .jira_fetcher import JiraIssueFetcher
from .task_executor_lmstudio import LMStudioTaskExecutor
from .task_executor_lmstudio_tools import LMStudioTaskExecutorWithTools

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

# Phase 4 Enterprise Features
try:
    from .webhook_integration import WebhookProcessor, WebhookServer, JiraWebhookHandlers, GitHubWebhookHandlers
    from .ai_code_review import AICodeReviewer, SecurityScanner, CodeQualityAnalyzer, CodeIssue, ReviewMetrics
    from .team_management import TeamManager, ApprovalWorkflow, CollaborationFeatures, User, Role, Permission
    from .external_integrations import (
        NotificationOrchestrator, SlackIntegration, TeamsIntegration, 
        EmailIntegration, CalendarIntegration
    )
    _ENTERPRISE_FEATURES_AVAILABLE = True
except ImportError:
    _ENTERPRISE_FEATURES_AVAILABLE = False

# Phase 5 Agent-Flows Mode Integration
try:
    from .mode_based_workflow import (
        ModeBasedJiraWorkflow, ClaudeCodeModeExecutor, TaskAnalyzer,
        ModeType, WorkflowPhase, ModeContext
    )
    _AGENT_FLOWS_FEATURES_AVAILABLE = True
except ImportError:
    _AGENT_FLOWS_FEATURES_AVAILABLE = False

__version__ = "5.0.0"
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
    "JiraWorkflow",
    "TaskExecutor",
    "JiraIssueFetcher",
    "LMStudioTaskExecutor"
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

# Add enterprise features to exports if available
if _ENTERPRISE_FEATURES_AVAILABLE:
    __all__.extend([
        "WebhookProcessor",
        "WebhookServer", 
        "JiraWebhookHandlers",
        "GitHubWebhookHandlers",
        "AICodeReviewer",
        "SecurityScanner",
        "CodeQualityAnalyzer",
        "CodeIssue",
        "ReviewMetrics",
        "TeamManager",
        "ApprovalWorkflow",
        "CollaborationFeatures",
        "User",
        "Role", 
        "Permission",
        "NotificationOrchestrator",
        "SlackIntegration",
        "TeamsIntegration",
        "EmailIntegration",
        "CalendarIntegration"
    ])

# Add agent-flows mode-based features to exports if available
if _AGENT_FLOWS_FEATURES_AVAILABLE:
    __all__.extend([
        "ModeBasedJiraWorkflow",
        "ClaudeCodeModeExecutor",
        "TaskAnalyzer",
        "ModeType",
        "WorkflowPhase", 
        "ModeContext"
    ])