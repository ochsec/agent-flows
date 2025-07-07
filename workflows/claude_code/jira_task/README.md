# JIRA Task Workflow

Direct Python API integration for JIRA workflows with Claude Code development assistance.

## Overview

This workflow provides seamless integration between JIRA issues and development work, using Claude Code's capabilities to assist with implementation, testing, and code review.

**🏢 Phase 4 Enterprise Features Now Available!**
- AI-powered security and quality code review
- Role-based access control and approval workflows
- Real-time webhook integration (JIRA, GitHub, GitLab)
- Team collaboration and workload management
- External integrations (Slack, Teams, Email)
- Enterprise analytics and compliance reporting

**🚀 Phase 3 Advanced Features:**
- Multi-project support with auto-detection
- Project-specific workflow templates
- CI/CD pipeline integration and monitoring
- Analytics and reporting dashboard
- Automated deployment capabilities

**Phase 2 Enhanced Features:**
- Context preservation between commands
- Enhanced prompting strategies
- Automatic PR creation with GitHub CLI
- Professional workflow completion
- Comprehensive quality checks

## Features

- **Direct JIRA API Integration**: No external dependencies like MCP servers
- **Git Branch Management**: Automatic branch creation with standardized naming
- **Claude Code Integration**: Full development assistance with comprehensive tool permissions
- **Interactive Development**: Step-by-step workflow with analyze/implement/test/review commands
- **Progress Tracking**: Automatic JIRA updates throughout development lifecycle

## Quick Start

### 1. Setup Configuration

```bash
# Create sample configuration file
python example.py --create-config

# Edit .env file with your JIRA credentials
vim .env
```

Required environment variables:
```bash
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your_api_token_here
JIRA_USERNAME=your.email@company.com
JIRA_PROJECT_KEY=PROJ  # Optional
```

### 2. Test Setup

```bash
# Run all tests
python example.py --test-all

# Test with specific issue
python example.py --demo PROJ-123
```

### 3. Start Working on an Issue

```bash
# Standard workflow
python jira_task.py PROJ-123

# Enhanced workflow with Phase 2 features
python jira_task.py PROJ-123 --enhanced

# Advanced workflow with Phase 3 features
python jira_task.py PROJ-123 --advanced

# Enterprise workflow with Phase 4 features (recommended for teams)
python jira_task.py PROJ-123 --enterprise --user john.doe

# Specify project for multi-project support
python jira_task.py PROJ-123 --advanced --project my-project

# Or use specific commands
python jira_task.py PROJ-123 --command start
python jira_task.py PROJ-123 --command status
python jira_task.py PROJ-123 --command list
python jira_task.py PROJ-123 --command update --comment "Progress update"
```

## Workflow Phases

### Phase 1: Initial Setup (Automated)
1. **Issue Retrieval**: Fetch JIRA issue details and validate access
2. **Branch Creation**: Create feature branch with standardized naming
3. **JIRA Update**: Add comment indicating development started

### Phase 2: Interactive Development
Available commands in interactive mode:

- **`analyze`** - Analyze codebase to find relevant files
- **`implement`** - Get implementation help and make code changes
- **`test`** - Create/run tests for implemented functionality
- **`review`** - Review changes and prepare for commit
- **`done`** - Complete workflow with commits and PR creation
- **`quit`** - Exit development mode

### Phase 3: Completion
- Final code review and testing
- Git commit with descriptive message
- Branch push to remote
- Pull request creation
- JIRA update with completion status

## Enhanced Workflow Features (Phase 2)

### Context Preservation
- Maintains command history and file changes throughout session
- Builds upon previous analysis and work
- Avoids redundant operations
- Provides session summaries

### Enhanced Claude Code Integration
- Context-aware prompting with session history
- Task-specific instructions for better results
- Intelligent file modification tracking
- Professional workflow completion

### Automatic PR Creation
- GitHub CLI integration for seamless PR creation
- Comprehensive PR descriptions with change summaries
- Automatic JIRA issue linking
- Professional commit message generation

### Quality Assurance
- Code quality checks and linting integration
- Security and performance analysis
- Comprehensive testing coverage
- Professional review process

### Usage
```bash
# Use enhanced features
python jira_task.py PROJ-123 --enhanced

# Enhanced commands provide:
✨ Context preservation between commands
🔍 Deeper analysis with session awareness  
🛠️ Incremental implementation with quality focus
🧪 Comprehensive testing with coverage analysis
🔍 Professional code review with quality checks
🏁 Automated PR creation with GitHub integration
```

## Advanced Workflow Features (Phase 3)

### Multi-Project Support
- Automatic project detection from repository
- Project-specific configurations and templates
- Support for Python, JavaScript, TypeScript, React, Next.js, FastAPI, Django, Flask
- Custom build, test, lint, and deployment commands per project

### Project Templates
- **FastAPI Template**: API development with pytest, black, flake8, mypy
- **React TypeScript**: Component development with Jest, ESLint, Prettier
- **Node.js TypeScript**: Backend services with comprehensive testing
- Automatically applies best practices for detected project type

### CI/CD Integration
- Auto-detection of CI/CD systems (GitHub Actions, GitLab CI, Jenkins, etc.)
- Real-time build status monitoring
- Automated deployment triggers
- Integration with existing pipeline configurations

### Analytics & Reporting
- Comprehensive workflow analytics and metrics
- Project productivity reports
- Team dashboard with success rates and timing
- Visual charts and trend analysis
- Quality metrics tracking

### Configuration
Create `jira_projects.yml` for multi-project support:
```yaml
projects:
  my-project:
    type: fastapi
    jira_project_key: API
    repository_url: https://github.com/example/my-project.git
    build_command: "pip install -r requirements.txt"
    test_command: "pytest --cov=app"
    reviewers: ["team-lead", "senior-dev"]
    labels: ["api", "backend"]
```

### Usage
```bash
# Advanced workflow with all Phase 3 features
python jira_task.py PROJ-123 --advanced

# Advanced commands include:
🎯 project    - Show project configuration and settings
🔧 ci         - Check CI/CD pipeline status
🚀 deploy     - Trigger deployment to environment
📊 analytics  - Generate productivity reports
🔍 analyze    - Project-specific codebase analysis
```

## Enterprise Workflow Features (Phase 4)

### AI-Powered Code Review
- **Security Scanning**: Automated detection of security vulnerabilities
- **Quality Analysis**: Code complexity, style, and maintainability analysis
- **Intelligent Suggestions**: AI-generated recommendations for improvements
- **Compliance Reporting**: Enterprise-grade security and quality reports

### Team Management & Collaboration
- **Role-Based Access Control**: Admin, Tech Lead, Developer, Reviewer roles
- **Approval Workflows**: Required approvals for sensitive actions
- **Team Workload Tracking**: Real-time visibility into team capacity
- **Activity Analytics**: Comprehensive team productivity metrics

### Real-Time Webhook Integration
- **JIRA Events**: Automatic workflow triggers from issue updates
- **GitHub/GitLab**: PR and merge event processing
- **Custom Actions**: Configurable responses to webhook events
- **Event History**: Complete audit trail of all webhook activities

### External Integrations
- **Slack Integration**: Rich notifications with interactive buttons
- **Microsoft Teams**: Adaptive cards and team notifications
- **Email Notifications**: Professional HTML email templates
- **Calendar Integration**: Automated scheduling for reviews and deployments

### Enterprise Security & Compliance
- **Secret Detection**: Automated scanning for hardcoded credentials
- **Security Scoring**: Quantitative security assessment (0-100)
- **Audit Logging**: Complete activity tracking for compliance
- **Access Control**: Granular permission management

### Configuration
Create `team_config.yml` for team management:
```yaml
teams:
  backend:
    description: "Backend Development Team"
    lead: "tech_lead"
    members: ["dev1", "dev2", "dev3"]
    approval_rules:
      deploy_production: ["tech_lead", "admin"]
      force_merge: ["tech_lead"]

users:
  - username: "tech_lead"
    email: "tech.lead@company.com"
    role: "tech_lead"
    team: "backend"
```

Environment variables for integrations:
```bash
# Webhook Security
GITHUB_WEBHOOK_SECRET=your_github_webhook_secret
JIRA_WEBHOOK_SECRET=your_jira_webhook_secret

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Microsoft Teams
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@company.com
SMTP_PASSWORD=your_app_password
```

### Usage
```bash
# Enterprise workflow with all Phase 4 features
python jira_task.py PROJ-123 --enterprise --user john.doe

# Start webhook server for real-time integration
python enterprise_workflow.py PROJ-123 --command webhook-server --webhook-port 8080

# Enterprise commands include:
🔍 analyze     - AI-powered codebase analysis
🛠️  implement   - Template-guided implementation
🧪 test        - Comprehensive testing with CI/CD
🔍 review      - Enterprise AI code review with security scanning
🔐 approve     - Handle team approval requests
🏢 dashboard   - Enterprise team dashboard and analytics
🔧 ci          - CI/CD pipeline status monitoring
🚀 deploy      - Deployment with approval workflows
🏁 done        - Complete enterprise workflow with notifications
```

## Claude Code Permissions

The workflow launches Claude Code with comprehensive development permissions:

```bash
claude -p --verbose --model sonnet --allowedTools \
  "read,write,edit,multiEdit,glob,grep,ls,bash,git,npm,cargo,python,pytest,webSearch,task"
```

**Tool Categories:**
- **File Operations**: read, write, edit, multiEdit
- **Code Search**: glob, grep, ls
- **Shell Commands**: bash (for cp, mv, grep, etc.)
- **Version Control**: git
- **Package Managers**: npm, cargo
- **Python Tools**: python, pytest
- **Research**: webSearch, task

## Example Usage

```bash
# Start work on issue
$ python jira_task.py PROJ-123

🚀 Starting work on JIRA issue: PROJ-123
📋 Retrieving issue details...
🌿 Creating feature branch...
💬 Updating JIRA with development status...
✅ Ready to work on PROJ-123: Implement user authentication
📋 Issue: Implement user authentication
🌿 Branch: feature/proj-123-implement-user-authentication

🤖 Launching Claude Code development assistant...
📅 Creating development plan...
[Claude Code analyzes codebase and creates plan]

🚀 Ready for development! Claude Code will assist you.
Available commands:
  - 'analyze': Analyze codebase for relevant files
  - 'implement': Get implementation suggestions
  - 'test': Create or run tests
  - 'review': Review changes before commit
  - 'done': Mark issue complete and create PR

==================================================

👷 [PROJ-123] What would you like to do? (help/analyze/implement/test/review/done/quit): 
```

## Dependencies

### Core Dependencies
- Python 3.7+
- requests
- python-dotenv
- pydantic
- git (command line tool)

### Phase 2 Enhanced Features
- GitHub CLI (gh) for automated PR creation
- Additional Python packages for enhanced functionality

### Installation
```bash
# Core dependencies
pip install requests python-dotenv pydantic

# Install GitHub CLI for PR creation
# macOS: brew install gh
# Ubuntu: apt install gh  
# Windows: winget install GitHub.cli

# Authenticate GitHub CLI
gh auth login
```

## File Structure

```
jira_task/
├── __init__.py               # Package initialization with all phases
├── config.py                 # Configuration management
├── jira_client.py            # JIRA API client
├── git_integration.py        # Git operations
├── jira_task.py              # Main workflow implementation
├── enhanced_workflow.py      # Phase 2 enhanced features
├── advanced_automation.py    # Phase 3 advanced features
├── enterprise_workflow.py    # Phase 4 enterprise features
├── webhook_integration.py    # Phase 4 webhook processing
├── ai_code_review.py         # Phase 4 AI code review
├── team_management.py        # Phase 4 team collaboration
├── external_integrations.py  # Phase 4 external tools
├── pr_creator.py             # GitHub PR creation utility
├── analytics.py              # Analytics and reporting
├── jira_projects.yml         # Multi-project configuration
├── team_config.yml           # Team management configuration
├── example.py                # Example usage and testing
└── README.md                # This documentation
```

## JIRA API Token Setup

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label (e.g., "Claude Code Workflow")
4. Copy the token to your `.env` file

## Troubleshooting

### Configuration Issues
```bash
# Test configuration
python example.py --test-all
```

### JIRA Connection Issues
- Verify JIRA_BASE_URL is correct
- Check API token is valid
- Ensure username/email is correct

### Git Issues
- Ensure you're in a git repository
- Check git is installed and configured
- Verify GitHub CLI (gh) is installed for PR creation

### Permission Issues
- Verify JIRA permissions for the project
- Check if issue is assigned to you
- Ensure git repository has push permissions

## Development

To modify or extend the workflow:

1. **Add new commands**: Extend `_interactive_development_mode()` in `jira_task.py`
2. **Modify JIRA operations**: Update methods in `jira_client.py`
3. **Change git behavior**: Modify `git_integration.py`
4. **Add configuration options**: Update `config.py`

## License

This workflow is part of the Claude Code agent-flows repository.