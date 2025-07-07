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

3. **Test the installation:**
   ```bash
   research --help
   review --help
   ```

## What the Setup Script Does

The setup script (`setup.sh`) automatically:

1. **Creates installation directory** at `~/.agent-flows`
2. **Copies all project files** to the installation directory
3. **Creates a Python virtual environment** with required dependencies
4. **Installs wrapper scripts** (`research`, `review`) in `~/.agent-flows/bin/`
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
   pip install pydantic python-dotenv
   ```

4. **Install wrapper scripts:**
   ```bash
   mkdir -p ~/.agent-flows/bin
   cp global-installation/research ~/.agent-flows/bin/
   cp global-installation/review ~/.agent-flows/bin/
   chmod +x ~/.agent-flows/bin/research
   chmod +x ~/.agent-flows/bin/review
   ```

5. **Add to PATH:**
   ```bash
   echo 'export PATH="$HOME/.agent-flows/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Usage

Once installed, you can run research and code review workflows from any directory:

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

## Environment Variables

### Optional: Perplexity API Key

For enhanced research capabilities, set your Perplexity API key:

```bash
export PERPLEXITY_API_KEY="your_api_key_here"
```

Add this to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) to make it permanent:

```bash
echo 'export PERPLEXITY_API_KEY="your_api_key_here"' >> ~/.bashrc
```

## How It Works

### Wrapper Script Architecture

The `research` command is a bash wrapper script that:

1. **Preserves working directory** - Captures where you ran the command
2. **Activates virtual environment** - Ensures Python dependencies are available
3. **Changes to installation directory** - Required for the Python script to find its files
4. **Passes original directory** - Via `ORIGINAL_PWD` environment variable
5. **Runs Python workflow** - Executes the research workflow with all arguments

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

## Troubleshooting

### Command not found
- Ensure `~/.agent-flows/bin` is in your PATH
- Restart your terminal after installation
- Check that the wrapper scripts are executable: `chmod +x ~/.agent-flows/bin/research ~/.agent-flows/bin/review`

### Python environment issues
- Ensure the virtual environment exists: `ls ~/.agent-flows/.venv`
- Recreate if needed: `cd ~/.agent-flows && python3 -m venv .venv`
- Install dependencies: `source ~/.agent-flows/.venv/bin/activate && pip install pydantic python-dotenv`

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
   cp workflows/claude_code/research/research.py ~/.agent-flows/workflows/claude_code/research/
   cp workflows/claude_code/code_review/review.py ~/.agent-flows/workflows/claude_code/code_review/
   ```
3. **Test the changes** by running the `research` or `review` commands

The wrapper script architecture makes it easy to develop locally and deploy globally.