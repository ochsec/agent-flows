import os
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class JiraConfig:
    """Configuration for JIRA API connection."""
    base_url: str
    api_token: str
    username: str
    project_key: Optional[str] = None


@dataclass  
class JiraIssue:
    """Structured representation of a JIRA issue."""
    key: str
    summary: str
    description: str
    issue_type: str
    status: str
    priority: str
    assignee: Optional[str] = None
    project_key: str = ""
    labels: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = field(default_factory=dict)


class JiraClient:
    """Direct JIRA API client for issue retrieval and updates."""
    
    def __init__(self, config: JiraConfig):
        self.config = config
        self.session = requests.Session()
        self.session.auth = (config.username, config.api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def test_connection(self) -> bool:
        """Test JIRA connection and authentication."""
        try:
            url = f"{self.config.base_url}/rest/api/3/myself"
            response = self.session.get(url)
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    def get_issue(self, issue_key: str) -> JiraIssue:
        """
        Retrieve a JIRA issue by key.
        
        Args:
            issue_key: JIRA issue key (e.g., "PROJ-123")
            
        Returns:
            JiraIssue object with structured data
            
        Raises:
            Exception: If issue not found or API error occurs
        """
        url = f"{self.config.base_url}/rest/api/3/issue/{issue_key}"
        
        # Request specific fields to optimize response
        params = {
            'fields': 'key,summary,description,issuetype,status,priority,assignee,project,labels,components'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            issue_data = response.json()
            
            return self._parse_issue(issue_data)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(f"Issue {issue_key} not found")
            elif e.response.status_code == 401:
                raise Exception("Authentication failed - check your API token")
            elif e.response.status_code == 403:
                raise Exception(f"Access denied to issue {issue_key}")
            else:
                raise Exception(f"JIRA API error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to retrieve issue {issue_key}: {str(e)}")
    
    def add_comment(self, issue_key: str, comment: str) -> bool:
        """
        Add a comment to a JIRA issue.
        
        Args:
            issue_key: JIRA issue key
            comment: Comment text to add
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.config.base_url}/rest/api/3/issue/{issue_key}/comment"
        
        # Handle both simple strings and Atlassian Document Format
        comment_data = {
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
        
        try:
            response = self.session.post(url, json=comment_data)
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    def update_issue_status(self, issue_key: str, transition_id: str) -> bool:
        """
        Update issue status via transition.
        
        Args:
            issue_key: JIRA issue key
            transition_id: ID of the transition to execute
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.config.base_url}/rest/api/3/issue/{issue_key}/transitions"
        
        transition_data = {
            "transition": {
                "id": transition_id
            }
        }
        
        try:
            response = self.session.post(url, json=transition_data)
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[JiraIssue]:
        """
        Search for issues using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            
        Returns:
            List of JiraIssue objects
        """
        url = f"{self.config.base_url}/rest/api/3/search"
        
        search_data = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ["key", "summary", "description", "issuetype", "status", "priority", "assignee", "project", "labels", "components"]
        }
        
        try:
            response = self.session.post(url, json=search_data)
            response.raise_for_status()
            search_results = response.json()
            
            issues = []
            for issue_data in search_results.get('issues', []):
                issues.append(self._parse_issue(issue_data))
            
            return issues
            
        except Exception as e:
            raise Exception(f"Failed to search issues: {str(e)}")
    
    def _parse_issue(self, issue_data: Dict[str, Any]) -> JiraIssue:
        """Parse raw JIRA API response into JiraIssue object."""
        fields = issue_data.get('fields', {})
        
        # Extract description with ADF handling
        description = self._extract_description(fields.get('description'))
        
        # Extract assignee
        assignee = None
        if fields.get('assignee'):
            assignee = fields['assignee'].get('displayName', fields['assignee'].get('emailAddress', 'Unknown'))
        
        # Extract labels and components
        labels = [label for label in fields.get('labels', [])]
        components = [comp.get('name', '') for comp in fields.get('components', [])]
        
        return JiraIssue(
            key=issue_data.get('key', ''),
            summary=fields.get('summary', ''),
            description=description,
            issue_type=fields.get('issuetype', {}).get('name', 'Unknown'),
            status=fields.get('status', {}).get('name', 'Unknown'),
            priority=fields.get('priority', {}).get('name', 'Medium'),
            assignee=assignee,
            project_key=fields.get('project', {}).get('key', ''),
            labels=labels,
            components=components,
            raw_data=issue_data
        )
    
    def _extract_description(self, description_data: Any) -> str:
        """Extract plain text description from JIRA's Atlassian Document Format."""
        if not description_data:
            return ""
        
        # Handle plain text descriptions
        if isinstance(description_data, str):
            return description_data
        
        # Handle Atlassian Document Format (ADF)
        if isinstance(description_data, dict):
            content = description_data.get('content', [])
            text_parts = []
            
            for block in content:
                if block.get('type') == 'paragraph':
                    for inline in block.get('content', []):
                        if inline.get('type') == 'text':
                            text_parts.append(inline.get('text', ''))
                        elif inline.get('type') == 'hardBreak':
                            text_parts.append('\n')
                elif block.get('type') == 'codeBlock':
                    # Handle code blocks
                    for inline in block.get('content', []):
                        if inline.get('type') == 'text':
                            text_parts.append(f"```\n{inline.get('text', '')}\n```")
                elif block.get('type') == 'bulletList' or block.get('type') == 'orderedList':
                    # Handle lists
                    for list_item in block.get('content', []):
                        if list_item.get('type') == 'listItem':
                            for paragraph in list_item.get('content', []):
                                if paragraph.get('type') == 'paragraph':
                                    for inline in paragraph.get('content', []):
                                        if inline.get('type') == 'text':
                                            text_parts.append(f"• {inline.get('text', '')}")
            
            return ' '.join(text_parts).strip()
        
        return str(description_data)


def load_jira_config() -> JiraConfig:
    """Load JIRA configuration from environment variables."""
    base_url = os.getenv("JIRA_BASE_URL", "")
    api_token = os.getenv("JIRA_API_TOKEN", "")
    username = os.getenv("JIRA_USERNAME", "")
    project_key = os.getenv("JIRA_PROJECT_KEY")
    
    if not all([base_url, api_token, username]):
        raise Exception(
            "Missing required JIRA configuration. Please set environment variables: "
            "JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME"
        )
    
    return JiraConfig(
        base_url=base_url.rstrip('/'),  # Remove trailing slash
        api_token=api_token,
        username=username,
        project_key=project_key
    )


class JiraPromptGenerator:
    """Generates intelligent prompts for the planning organization task tool based on JIRA issues."""
    
    def __init__(self):
        self.prompt_templates = {
            "Bug": self._generate_bug_prompt,
            "Story": self._generate_story_prompt,
            "Task": self._generate_task_prompt,
            "Epic": self._generate_epic_prompt,
            "Improvement": self._generate_improvement_prompt,
            "New Feature": self._generate_feature_prompt,
        }
    
    def generate_task_prompt(self, issue: JiraIssue) -> tuple[str, str]:
        """
        Generate description and prompt for the planning organization task tool.
        
        Args:
            issue: JiraIssue object with issue details
            
        Returns:
            Tuple of (description, detailed_prompt)
        """
        # Generate description (3-5 words)
        description = self._generate_description(issue)
        
        # Generate detailed prompt based on issue type
        prompt_generator = self.prompt_templates.get(issue.issue_type, self._generate_generic_prompt)
        detailed_prompt = prompt_generator(issue)
        
        return description, detailed_prompt
    
    def _generate_description(self, issue: JiraIssue) -> str:
        """Generate a short description for the task."""
        # Extract key words from summary
        summary_words = issue.summary.lower().split()
        
        # Common action words to prioritize
        action_words = ["implement", "create", "build", "fix", "debug", "add", "remove", "update", "refactor", "design"]
        
        # Find action word in summary
        action = None
        for word in summary_words:
            if word in action_words:
                action = word
                break
        
        if not action:
            action = "work on"
        
        # Get main subject (try to extract noun from summary)
        key_terms = [word for word in summary_words if len(word) > 4 and word not in ["with", "from", "that", "this", "when", "where"]]
        subject = key_terms[0] if key_terms else issue.issue_type.lower()
        
        return f"{action} {subject}"
    
    def _generate_bug_prompt(self, issue: JiraIssue) -> str:
        """Generate prompt for bug issues."""
        return f"""Analyze and fix the bug described in JIRA issue {issue.key}.

## Issue Details
**Summary:** {issue.summary}
**Status:** {issue.status}
**Priority:** {issue.priority}
**Project:** {issue.project_key}

## Problem Description
{issue.description}

## Task Requirements
1. **Root Cause Analysis**: Investigate the bug to understand the underlying cause
2. **Reproduction**: Ensure the bug can be consistently reproduced  
3. **Impact Assessment**: Evaluate the scope and severity of the issue
4. **Solution Design**: Develop a comprehensive fix that addresses the root cause
5. **Testing Strategy**: Create tests to verify the fix and prevent regression
6. **Documentation**: Update relevant documentation if needed

## Additional Context
- **Components:** {', '.join(issue.components) if issue.components else 'None specified'}
- **Labels:** {', '.join(issue.labels) if issue.labels else 'None'}
- **Assignee:** {issue.assignee or 'Unassigned'}

Please provide a detailed analysis, implementation plan, and ensure the solution is robust and well-tested."""

    def _generate_story_prompt(self, issue: JiraIssue) -> str:
        """Generate prompt for user story issues."""
        return f"""Implement the user story described in JIRA issue {issue.key}.

## User Story Details
**Summary:** {issue.summary}
**Status:** {issue.status}
**Priority:** {issue.priority}
**Project:** {issue.project_key}

## Story Description
{issue.description}

## Implementation Requirements
1. **Requirements Analysis**: Break down the user story into specific technical requirements
2. **Acceptance Criteria**: Define clear, testable acceptance criteria
3. **Technical Design**: Design the solution architecture and implementation approach
4. **Development**: Implement the functionality following best practices
5. **Testing**: Create comprehensive tests including unit, integration, and user acceptance tests
6. **User Experience**: Ensure the implementation provides excellent user experience

## Additional Context
- **Components:** {', '.join(issue.components) if issue.components else 'None specified'}
- **Labels:** {', '.join(issue.labels) if issue.labels else 'None'}
- **Assignee:** {issue.assignee or 'Unassigned'}

Focus on delivering value to the end user while maintaining code quality and system reliability."""

    def _generate_task_prompt(self, issue: JiraIssue) -> str:
        """Generate prompt for task issues."""
        return f"""Complete the task described in JIRA issue {issue.key}.

## Task Details
**Summary:** {issue.summary}
**Status:** {issue.status}
**Priority:** {issue.priority}
**Project:** {issue.project_key}

## Task Description
{issue.description}

## Execution Plan
1. **Task Analysis**: Understand the specific requirements and scope
2. **Planning**: Create a detailed implementation plan with clear steps
3. **Resource Assessment**: Identify required tools, libraries, and dependencies
4. **Implementation**: Execute the task following established standards and practices
5. **Quality Assurance**: Verify the work meets requirements and quality standards
6. **Documentation**: Update relevant documentation and provide clear handoff notes

## Additional Context
- **Components:** {', '.join(issue.components) if issue.components else 'None specified'}
- **Labels:** {', '.join(issue.labels) if issue.labels else 'None'}
- **Assignee:** {issue.assignee or 'Unassigned'}

Ensure the task is completed efficiently while maintaining high quality standards."""

    def _generate_epic_prompt(self, issue: JiraIssue) -> str:
        """Generate prompt for epic issues.""" 
        return f"""Plan and coordinate the epic described in JIRA issue {issue.key}.

## Epic Overview
**Summary:** {issue.summary}
**Status:** {issue.status}
**Priority:** {issue.priority}
**Project:** {issue.project_key}

## Epic Description
{issue.description}

## Strategic Planning Requirements
1. **Epic Breakdown**: Decompose the epic into manageable user stories and tasks
2. **Architecture Planning**: Design high-level system architecture and integration points
3. **Resource Planning**: Estimate effort, timeline, and resource requirements
4. **Risk Assessment**: Identify potential risks and mitigation strategies
5. **Milestone Definition**: Define key milestones and success criteria
6. **Stakeholder Alignment**: Ensure alignment with business objectives and user needs

## Coordination Activities
- Create detailed project plan with phases and dependencies
- Establish technical standards and guidelines for the epic
- Design integration and testing strategies
- Plan deployment and rollout approach

## Additional Context
- **Components:** {', '.join(issue.components) if issue.components else 'None specified'}
- **Labels:** {', '.join(issue.labels) if issue.labels else 'None'}
- **Assignee:** {issue.assignee or 'Unassigned'}

Focus on creating a comprehensive plan that enables successful delivery of this major initiative."""

    def _generate_improvement_prompt(self, issue: JiraIssue) -> str:
        """Generate prompt for improvement issues."""
        return f"""Implement the improvement described in JIRA issue {issue.key}.

## Improvement Details
**Summary:** {issue.summary}
**Status:** {issue.status}
**Priority:** {issue.priority}
**Project:** {issue.project_key}

## Improvement Description
{issue.description}

## Enhancement Strategy
1. **Current State Analysis**: Analyze existing functionality and identify improvement opportunities
2. **Benefit Assessment**: Quantify expected benefits and impact of the improvement
3. **Solution Design**: Design enhanced solution that addresses identified issues
4. **Implementation Planning**: Plan implementation to minimize disruption
5. **Performance Optimization**: Focus on improving performance, usability, or maintainability
6. **Validation**: Measure improvement results against baseline metrics

## Quality Focus Areas
- **Performance**: Optimize speed, efficiency, and resource usage
- **User Experience**: Enhance usability and user satisfaction
- **Maintainability**: Improve code quality and system maintainability
- **Reliability**: Increase system stability and error handling

## Additional Context
- **Components:** {', '.join(issue.components) if issue.components else 'None specified'}
- **Labels:** {', '.join(issue.labels) if issue.labels else 'None'}
- **Assignee:** {issue.assignee or 'Unassigned'}

Deliver measurable improvements while maintaining system stability and code quality."""

    def _generate_feature_prompt(self, issue: JiraIssue) -> str:
        """Generate prompt for new feature issues."""
        return f"""Develop the new feature described in JIRA issue {issue.key}.

## Feature Specification
**Summary:** {issue.summary}
**Status:** {issue.status}
**Priority:** {issue.priority}
**Project:** {issue.project_key}

## Feature Description
{issue.description}

## Development Requirements
1. **Feature Analysis**: Analyze requirements and define feature scope clearly
2. **Technical Design**: Design scalable, maintainable architecture for the feature
3. **API Design**: Define clean, intuitive APIs and interfaces
4. **Implementation**: Develop the feature following coding standards and best practices
5. **Integration**: Ensure seamless integration with existing system components
6. **Testing**: Implement comprehensive testing including edge cases and error scenarios

## Quality Standards
- **Scalability**: Design for future growth and increased usage
- **Security**: Implement appropriate security measures and data protection
- **Performance**: Ensure feature performs efficiently under expected load
- **Usability**: Create intuitive, user-friendly interfaces and experiences
- **Documentation**: Provide thorough documentation for users and developers

## Additional Context
- **Components:** {', '.join(issue.components) if issue.components else 'None specified'}
- **Labels:** {', '.join(issue.labels) if issue.labels else 'None'}
- **Assignee:** {issue.assignee or 'Unassigned'}

Build a high-quality feature that adds significant value to the product while maintaining system integrity."""

    def _generate_generic_prompt(self, issue: JiraIssue) -> str:
        """Generate generic prompt for unknown issue types."""
        return f"""Work on the issue described in JIRA issue {issue.key}.

## Issue Details
**Summary:** {issue.summary}
**Type:** {issue.issue_type}
**Status:** {issue.status}
**Priority:** {issue.priority}
**Project:** {issue.project_key}

## Description
{issue.description}

## General Approach
1. **Analysis**: Thoroughly analyze the issue requirements and context
2. **Planning**: Create a detailed plan for addressing the issue
3. **Research**: Investigate any unknowns or technical challenges
4. **Implementation**: Execute the planned solution with attention to quality
5. **Testing**: Verify the solution works correctly and meets requirements
6. **Documentation**: Document the solution and any important decisions

## Quality Considerations
- Follow established coding standards and best practices
- Ensure solution is maintainable and well-documented
- Include appropriate testing and error handling
- Consider impact on existing system components

## Additional Context
- **Components:** {', '.join(issue.components) if issue.components else 'None specified'}
- **Labels:** {', '.join(issue.labels) if issue.labels else 'None'}
- **Assignee:** {issue.assignee or 'Unassigned'}

Provide a thorough, professional solution that addresses all requirements."""