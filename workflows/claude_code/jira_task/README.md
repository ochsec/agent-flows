# JIRA Task Workflow

Direct Python API integration for JIRA workflows with Claude Code development assistance.

## Overview

This workflow provides seamless integration between JIRA issues and development work, using Claude Code's capabilities to assist with implementation, testing, and code review.

**🚀 Phase 2 Enhanced Features Now Available!**
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
├── __init__.py             # Package initialization with Phase 2 features
├── config.py               # Configuration management
├── jira_client.py          # JIRA API client
├── git_integration.py      # Git operations
├── jira_task.py            # Main workflow implementation
├── enhanced_workflow.py    # Phase 2 enhanced features
├── pr_creator.py           # GitHub PR creation utility
├── example.py              # Example usage and testing
└── README.md              # This documentation
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