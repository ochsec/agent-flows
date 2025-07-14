# Agent Flows

A collection of my frequently-used agent workflows and agent modes.

## Global Installation

Install Agent Flows globally to run workflows from any directory:

```bash
# Clone the repository
git clone https://github.com/your-username/agent-flows.git
cd agent-flows

# Run the setup script
cd global-installation
./setup.sh

# Restart your terminal and test
research "How to implement microservices in Python"
review 123 --repository owner/repo
```

This installs global `research` and `review` commands for comprehensive technical research and AI-powered code reviews.

For detailed installation instructions, see [Global Installation Guide](global-installation/README.md).

## Agent Workflows

### Research
- [Research Manager Workflow](workflows/research/README.md) - Comprehensive multi-agent research workflow using Claude Code integration for conducting rigorous research and generating technical reports

### Code Review
- [Simple PR Review Workflow](workflows/code_review/README.md) - Straightforward code review workflow leveraging Claude Code's GitHub integration for comprehensive pull request analysis

## Agent Modes

- **architect.md** - Gathers context and creates detailed plans for technical tasks before implementation
- **ask.md** - Provides technical assistance and answers questions about software development and technology
- **code.md** - Serves as a skilled software engineer for programming tasks across multiple languages and frameworks
- **debug.md** - Specializes in systematic problem diagnosis and resolution with methodical debugging approaches
- **devops.md** - Handles deployment, infrastructure automation, CI/CD pipelines, and cloud operations
- **expert_consultant.md** - Provides domain-specific expert analysis and context for research findings
- **fact_checker.md** - Verifies accuracy and reliability of research findings through systematic validation
- **orchestrator.md** - Coordinates complex workflows by delegating tasks to appropriate specialized modes
- **research_manager.md** - Orchestrates comprehensive research workflows through systematic delegation to specialized modes
- **researcher.md** - Gathers and analyzes high-quality information on specific research topics using strategic search methods
- **synthesizer.md** - Integrates diverse research findings into cohesive knowledge structures and identifies patterns
- **user_story.md** - Creates clear, valuable user stories following agile methodology with acceptance criteria
- **writer.md** - Transforms research findings into polished, professional reports with mandatory technical depth