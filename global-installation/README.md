# Global Agent Flows Installation

This directory contains the files needed to install Agent Flows globally on your system, allowing you to run research workflows and code review workflows from any directory.

## Quick Setup

1. **Run the setup script:**
   ```bash
   cd global-installation
   ./setup.sh
   ```

2. **Restart your terminal** or reload your shell profile:
   ```bash
   source ~/.bashrc  # or ~/.zshrc depending on your shell
   ```

3. **Configure your services:**
   ```bash
   configure
   ```

4. **Test the installation:**
   ```bash
   research --help
   review --help
   jira_task --help
   ```

## What the Setup Script Does

The setup script (`setup.sh`) automatically:

1. **Creates installation directory** at `~/.agent-flows`
2. **Copies all project files** to the installation directory
3. **Creates a Python virtual environment** with required dependencies
4. **Installs wrapper scripts** (`research`, `review`, `jira_task`, `configure`) in `~/.agent-flows/bin/`
5. **Adds the bin directory to your PATH** in shell profiles

## Manual Installation

If you prefer to install manually:

1. **Create installation directory:**
   ```bash
   mkdir -p ~/.agent-flows
   ```

2. **Copy project files:**
   ```bash
   cp -r /path/to/agent-flows/* ~/.agent-flows/
   ```

3. **Create virtual environment:**
   ```bash
   cd ~/.agent-flows
   python3 -m venv .venv
   source .venv/bin/activate
   pip install pydantic python-dotenv tomli tomli-w
   ```

4. **Install wrapper scripts:**
   ```bash
   mkdir -p ~/.agent-flows/bin
   cp global-installation/research ~/.agent-flows/bin/
   cp global-installation/review ~/.agent-flows/bin/
   cp global-installation/jira_task ~/.agent-flows/bin/
   cp global-installation/configure ~/.agent-flows/bin/
   chmod +x ~/.agent-flows/bin/research
   chmod +x ~/.agent-flows/bin/review
   chmod +x ~/.agent-flows/bin/jira_task
   chmod +x ~/.agent-flows/bin/configure
   ```

5. **Add to PATH:**
   ```bash
   echo 'export PATH="$HOME/.agent-flows/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Usage

Once installed, you can configure services and run research, code review, and JIRA task workflows from any directory:

### Research Workflow

```bash
# Basic research
research "How to implement microservices in Python"

# Research with custom output folder
research "Machine learning best practices" --output ./reports

# Research with specific Claude model
research "Blockchain technology overview" --model opus

# Research with Perplexity API integration
research "Latest AI developments" --perplexity-api-key your_key_here
```

### Code Review Workflow

```bash
# Review a PR in the current repository
review 123

# Review a PR in a specific repository
review 456 --repository owner/repo-name

# Review with custom instructions
review 789 --instructions "Focus on security vulnerabilities"

# Review with specific Claude model
review 101 --model opus --repository myorg/myrepo

# Save review to specific directory
review 202 --output ./reviews
```

### Configuration

```bash
# Interactive setup for all services (JIRA, Perplexity)
configure

# Show current configuration status
configure show

# Configure only JIRA
configure configure --jira

# Configure only Perplexity
configure configure --perplexity

# Show sample configuration format
configure sample

# Reset all configuration
configure reset
```

### JIRA Task Workflow

```bash
# Start work on a JIRA issue (Phase 1: Basic workflow)
jira_task PROJ-123

# Start work with enhanced features (Phase 2)
jira_task PROJ-123 --enhanced

# Start work with advanced automation (Phase 3)
jira_task PROJ-123 --advanced

# Start work with enterprise features (Phase 4)
jira_task PROJ-123 --enterprise --user your-username

# Start work with agent-flows mode-based workflow (Phase 5)
jira_task PROJ-123 --agent-modes --modes-path ./modes

# List your assigned issues
jira_task --command list --status-filter "To Do"

# Update issue progress
jira_task PROJ-123 --command update --comment "Implemented authentication feature"

# Check issue status
jira_task PROJ-123 --command status
```

## Configuration System

Agent Flows uses a unified TOML-based configuration system that stores all service credentials in `~/.agent-flows/config.toml`.

### Setup Configuration

1. **Interactive setup (recommended):**
   ```bash
   configure
   ```

2. **Manual TOML file editing:**
   ```bash
   # View sample format
   configure sample
   
   # Edit the config file directly
   vim ~/.agent-flows/config.toml
   ```

### Configuration File Format

The configuration file uses TOML format with sections for each service:

```toml
[jira]
base_url = "https://your-company.atlassian.net"
username = "your.email@company.com"
api_token = "your_jira_api_token_here"
project_key = "PROJ"  # Optional default project

[perplexity]
api_key = "your_perplexity_api_key_here"
```

### Getting API Tokens

- **JIRA API Token:** Visit https://id.atlassian.com/manage-profile/security/api-tokens
- **Perplexity API Key:** Get from your Perplexity account dashboard

### Legacy Environment Variables

For backward compatibility, the system still supports environment variables:
- `JIRA_BASE_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`
- `PERPLEXITY_API_KEY`

The unified config system takes precedence over environment variables.

## How It Works

### Wrapper Script Architecture

The `research`, `review`, and `jira_task` commands are bash wrapper scripts that:

1. **Preserves working directory** - Captures where you ran the command
2. **Activates virtual environment** - Ensures Python dependencies are available
3. **Changes to installation directory** - Required for the Python script to find its files
4. **Passes original directory** - Via `ORIGINAL_PWD` environment variable
5. **Runs Python workflow** - Executes the appropriate workflow (research, review, or JIRA task) with all arguments

### Directory Handling

The Python script automatically:

1. **Detects original directory** - From the `ORIGINAL_PWD` environment variable
2. **Changes back to original directory** - Where you invoked the command
3. **Creates files in correct location** - Research context and reports in your working directory
4. **Cleans up temporary files** - Removes research context after generating final report

### File Output

- **Research reports** are saved in the directory where you ran the command
- **Temporary files** (`research_context.md`) are created and cleaned up automatically
- **Report filenames** are sanitized to avoid filesystem issues

## Command Line Options

### Research Command

```bash
research "Your research topic" [OPTIONS]

Options:
  --output, -o FOLDER          Output folder for reports (default: current directory)
  --model MODEL               Claude model to use (sonnet, opus, haiku)
  --perplexity-api-key KEY    Perplexity API key for enhanced research
  --help                      Show help message
```

### Review Command

```bash
review PR_NUMBER [OPTIONS]

Options:
  --repository REPO           Repository in format owner/repo (defaults to current repo)
  --model MODEL              Claude model to use (sonnet, opus, haiku)
  --instructions TEXT        Additional review instructions
  --output, -o FOLDER        Output directory for review file (default: current directory)
  --verbose, -v              Enable verbose logging
  --help                     Show help message
```

### JIRA Task Command

```bash
jira_task ISSUE_KEY [OPTIONS]

Required Arguments:
  ISSUE_KEY                   JIRA issue key to work on (e.g., PROJ-123)

Options:
  --command, -c COMMAND       Command to execute (start, list, update, status) [default: start]
  --comment COMMENT           Progress comment for update command
  --status-filter, -s STATUS  Issue status filter for list command [default: "To Do"]
  --config CONFIG             Path to .env configuration file
  --enhanced                  Use enhanced workflow with Phase 2 features
  --advanced                  Use advanced workflow with Phase 3 features
  --enterprise                Use enterprise workflow with Phase 4 features
  --agent-modes               Use agent-flows mode-based workflow with Phase 5 features
  --modes-path PATH           Path to agent-flows modes directory [default: ./modes]
  --project PROJECT           Specify project name for multi-project support
  --user USER                 Current user for enterprise features
  --help                      Show help message
```

## Troubleshooting

### Command not found
- Ensure `~/.agent-flows/bin` is in your PATH
- Restart your terminal after installation
- Check that the wrapper scripts are executable: `chmod +x ~/.agent-flows/bin/*`

### Python environment issues
- Ensure the virtual environment exists: `ls ~/.agent-flows/.venv`
- Recreate if needed: `cd ~/.agent-flows && python3 -m venv .venv`
- Install dependencies: `source ~/.agent-flows/.venv/bin/activate && pip install pydantic python-dotenv tomli tomli-w`

### Files created in wrong directory
- This was a known issue that has been fixed
- The wrapper scripts now preserve your original working directory
- Research reports and code reviews should appear where you ran the command

### Research context file not cleaned up
- The script now properly cleans up temporary files after generating reports
- If you see old `research_context.md` files, you can safely delete them

## Uninstallation

To remove the global installation:

```bash
# Remove installation directory
rm -rf ~/.agent-flows

# Remove from PATH (edit your shell profile)
# Remove this line from ~/.bashrc, ~/.zshrc, or ~/.bash_profile:
# export PATH="$HOME/.agent-flows/bin:$PATH"
```

## Development

To update the global installation after making changes:

1. **Update the code** in your development directory
2. **Copy updated files** to the global installation:
   ```bash
   cp workflows/research/research.py ~/.agent-flows/workflows/research/
   cp workflows/code_review/review.py ~/.agent-flows/workflows/code_review/
   cp workflows/jira_task/*.py ~/.agent-flows/workflows/jira_task/
   ```
3. **Test the changes** by running the `research`, `review`, or `jira_task` commands


The wrapper script architecture makes it easy to develop locally and deploy globally.