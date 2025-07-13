# JIRA Workflow Integration

This directory contains the complete JIRA workflow integration for the planning organization tool. The workflow pulls JIRA issues, creates intelligent prompts based on issue content, and invokes the task tool for automated analysis.

## Files

- `jira_integration.py` - Core JIRA API client and prompt generation
- `jira_workflow.py` - Main workflow orchestrator with CLI
- `README.md` - This documentation file

## Setup

### 1. Install Dependencies

```bash
pip install requests python-dotenv
```

### 2. Configure JIRA Credentials

Copy the example environment file and configure your JIRA credentials:

```bash
cp .env.example .env
```

Edit `.env` with your JIRA details:

```env
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_API_TOKEN=your_api_token_here
JIRA_USERNAME=your.email@company.com
JIRA_PROJECT_KEY=PROJ
```

### 3. Generate JIRA API Token

1. Go to [Atlassian Account Security](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label and copy the generated token
4. Use this token as `JIRA_API_TOKEN` in your `.env` file

## Usage

### Command Line Interface

The workflow provides a comprehensive CLI for different use cases:

#### Test Connection

```bash
python workflows/jira_workflow.py --test-connection
```

#### Process Single Issue

```bash
python workflows/jira_workflow.py issue PROJ-123
```

#### Process Multiple Issues

```bash
python workflows/jira_workflow.py issues PROJ-123 PROJ-124 PROJ-125
```

#### Search and Process Issues

```bash
# Process all open bugs
python workflows/jira_workflow.py search "project = PROJ AND status = 'Open' AND type = Bug"

# Process high priority stories assigned to you
python workflows/jira_workflow.py search "assignee = currentUser() AND priority = High AND type = Story" --max-results 5
```

### Programmatic Usage

```python
from workflows.jira_workflow import JiraWorkflow

# Initialize workflow
workflow = JiraWorkflow(project_path=".")

# Test connection
if workflow.test_connection():
    print("JIRA connection successful")

# Process single issue
result = workflow.execute_issue_workflow("PROJ-123")
print(f"Success: {result['success']}")

# Search and process issues
results = workflow.search_and_execute(
    "project = PROJ AND status = 'To Do'",
    max_results=10
)
print(f"Processed {results['issues_processed']} issues")
```

## Workflow Stages

Each issue goes through four stages:

1. **JIRA Retrieval** - Fetch issue details from JIRA API
2. **Prompt Generation** - Create intelligent prompts based on issue type and content
3. **Task Execution** - Run planning organization task tool with generated prompt
4. **JIRA Update** - Add progress comments back to JIRA issue

## Issue Type Support

The workflow supports intelligent prompt generation for:

- **Bug** - Root cause analysis, reproduction steps, testing strategy
- **Story** - Requirements analysis, acceptance criteria, implementation approach
- **Task** - Execution planning, resource assessment, quality assurance
- **Epic** - Strategic planning, breakdown, coordination activities
- **Improvement** - Current state analysis, benefit assessment, optimization
- **New Feature** - Feature analysis, technical design, integration planning

## Features

### Intelligent Prompt Generation

- Issue type-specific prompts with tailored requirements
- Extracts and processes Atlassian Document Format (ADF) content
- Includes project context, components, labels, and assignee information

### Multi-Agent Orchestration

- Integrates with planning organization tool's multi-agent system
- Specialized agents: Researcher, Architect, Code, Debug, Expert Consultant, Synthesizer
- Parallel execution for complex analysis tasks

### Progress Tracking

- Adds automated progress comments to JIRA issues
- Includes agent information, execution time, and analysis summary
- Tracks workflow success/failure across all stages

### Error Handling

- Comprehensive error handling for each workflow stage
- Detailed logging with configurable levels
- Graceful degradation when JIRA updates fail

## JQL Query Examples

```bash
# All open issues in current sprint
python workflows/jira_workflow.py search "project = PROJ AND sprint in openSprints() AND status != Done"

# High priority bugs
python workflows/jira_workflow.py search "project = PROJ AND type = Bug AND priority in (High, Highest)"

# Recently created stories
python workflows/jira_workflow.py search "project = PROJ AND type = Story AND created >= -7d"

# Unassigned critical issues
python workflows/jira_workflow.py search "project = PROJ AND assignee is EMPTY AND priority = Critical"
```

## Integration with Planning Organization Tool

The workflow seamlessly integrates with the planning organization tool:

- Uses the `task()` method for agent orchestration
- Supports all thinking budget levels (think, think_hard, think_harder, ultrathink)
- Maintains task history and state persistence
- Leverages specialized agent modes based on prompt analysis

## Security Notes

- API tokens are stored in environment variables, not in code
- Supports modern JIRA authentication (API tokens, OAuth 2.0)
- Follows secure credential management practices
- No sensitive information logged or exposed

## Troubleshooting

### Connection Issues

```bash
# Test your connection
python workflows/jira_workflow.py --test-connection
```

Common issues:
- Invalid API token - regenerate from Atlassian
- Wrong base URL - ensure no trailing slash
- Network connectivity - check firewall/proxy settings

### Permission Issues

Ensure your JIRA user has:
- Read access to target projects
- Comment permissions on issues
- Search permissions for JQL queries

### API Rate Limiting

JIRA Cloud has rate limits:
- Add delays between requests if processing many issues
- Use `--max-results` to limit batch sizes
- Consider processing during off-peak hours

## Advanced Configuration

### Custom Prompt Templates

Extend `JiraPromptGenerator` to add custom issue types:

```python
class CustomJiraPromptGenerator(JiraPromptGenerator):
    def __init__(self):
        super().__init__()
        self.prompt_templates["CustomType"] = self._generate_custom_prompt
    
    def _generate_custom_prompt(self, issue):
        # Custom prompt logic
        pass
```

### Webhook Integration

For real-time processing, consider setting up JIRA webhooks:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/jira-webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    if data['webhookEvent'] == 'jira:issue_created':
        issue_key = data['issue']['key']
        workflow.execute_issue_workflow(issue_key)
    return 'OK'
```

This integration provides a complete bridge between JIRA issue management and AI-powered analysis through the planning organization tool.