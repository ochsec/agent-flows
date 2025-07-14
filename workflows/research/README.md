# Research Manager Workflow - Claude Code Integration

A comprehensive multi-agent research workflow system that orchestrates specialized AI agents using Claude Code commands to conduct rigorous research and generate technical reports.

## Overview

This workflow implements the research manager role defined in `modes/research_manager.md` using Claude Code commands as the execution layer with Python orchestration. It coordinates five specialized agents through a systematic research process:

1. **Researcher** - Information gathering and source evaluation
2. **Synthesizer** - Pattern identification and knowledge integration  
3. **Expert Consultant** - Domain-specific analysis and implications
4. **Fact-Checker** - Verification and accuracy validation
5. **Writer** - Technical report generation with mandatory depth

## Features

- **Claude Code Integration**: Uses `claude -p` commands as the primary execution layer
- **Multi-Agent Orchestration**: Systematic delegation between specialized agents
- **Cumulative Documentation**: All research stored in `research_context.md`
- **Technical Depth**: Mandatory code examples, architectural details, performance metrics
- **Quality Assurance**: Built-in fact-checking and verification processes
- **Perplexity Integration**: Enhanced research capabilities via MCP
- **Flexible Models**: Support for Claude sonnet, opus, and haiku models

## Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables** (Optional):
```bash
export PERPLEXITY_API_KEY="your-perplexity-api-key"  # Optional for enhanced research
```

**Note**: No API keys are required for basic functionality. Claude Code handles authentication automatically.

3. **Verify Installation**:
```bash
python workflows/research/research_manager.py --help
```

## Usage

### Command Line Interface

```bash
# Basic usage
python workflows/research/research_manager.py "Vector databases in AI applications"

# With custom output folder
python workflows/research/research_manager.py "Machine learning deployment patterns" --output reports/ml

# With specific Claude model
python workflows/research/research_manager.py "Microservices architecture" --model opus
```

### Python API

```python
from workflows.research.research_manager import ResearchManagerWorkflow

# Initialize workflow with Claude Code (default)
workflow = ResearchManagerWorkflow(model="sonnet")

# Or with Perplexity integration
workflow = ResearchManagerWorkflow(
    model="sonnet", 
    perplexity_api_key="your-perplexity-key"
)

# Execute research
report_path = workflow.execute_workflow(
    research_topic="Distributed systems patterns",
    output_folder="reports"
)

print(f"Report generated: {report_path}")
```

### Configuration

```python
from workflows.research.config import get_config

# Use development configuration
config = get_config("development")
workflow = ResearchManagerWorkflow(
    model=config.get_claude_config()["model"],
    perplexity_api_key=config.get_perplexity_config()["api_key"]
)
```

## Workflow Process

### 1. Initialize Research Context
- Creates/updates `research_context.md` with structured sections
- Preserves existing research content
- Timestamps new research tasks

### 2. Research Phase
- **Researcher Agent** uses Perplexity Ask commands for targeted information gathering
- Submits multiple focused queries rather than single broad research tasks
- Evaluates source credibility and accuracy
- Identifies conflicting information and gaps
- Appends findings to Research Findings section

### 3. Synthesis Phase
- **Synthesizer Agent** analyzes research findings
- Identifies patterns, themes, and relationships
- Resolves contradictions between sources
- Appends synthesis to Synthesis section

### 4. Expert Analysis Phase
- **Expert Consultant Agent** provides domain expertise
- Analyzes practical implications and applications
- Suggests future research directions
- Appends analysis to Expert Analysis section

### 5. Fact-Checking Phase
- **Fact-Checker Agent** verifies accuracy of all content
- Evaluates source reliability and citation accuracy
- Flags information requiring correction
- Appends verification results to Verification section

### 6. Report Generation Phase
- **Writer Agent** creates comprehensive technical report in **Markdown format**
- Includes mandatory technical depth requirements:
  - Code snippets and implementation details in markdown code blocks
  - Architectural diagrams and system design descriptions
  - Performance metrics and scalability analysis in tables
  - Comparative analysis with alternatives
- Generates publication-ready markdown saved to specified folder

## Technical Requirements

### Mandatory Technical Depth

All reports must include:
- **Granular Technical Explanations** - Detailed mechanism descriptions
- **Code Examples** - Actual implementation snippets
- **Architectural Details** - System design and component relationships
- **Performance Metrics** - Quantitative analysis and benchmarks
- **Scalability Considerations** - Growth and capacity planning
- **Implementation Specifics** - Precise technical requirements

### Output Structure

```
research_context.md          # Cumulative research documentation
reports/
├── topic_research_report.md # Final technical report
└── ...                     # Additional reports
```

## Configuration Options

### Environment Variables
```bash
PERPLEXITY_API_KEY=pplx-...        # Optional: Perplexity API key for enhanced research
RESEARCH_OUTPUT_FOLDER=reports     # Default output folder
```

**Note**: OpenRouter API key is no longer used. The workflow uses Claude Code CLI directly.

### Agent Configuration
```python
config = {
    "researcher": {
        "max_sources": 10,
        "verification_level": "high"
    },
    "writer": {
        "technical_depth": "mandatory",
        "code_examples": True,
        "performance_metrics": True
    }
}
```

## Examples

### Research AI Architecture Patterns
```bash
python workflows/research/research_manager.py \
  "AI architecture patterns for scalable machine learning systems" \
  --output reports/ai_architecture
```

### Research Database Technologies
```bash
python workflows/research/research_manager.py \
  "Vector databases vs traditional databases for AI applications" \
  --output reports/databases \
  --model opus
```

## Troubleshooting

### Common Issues

1. **Claude Code Not Available**
   - Ensure Claude Code CLI is installed and in PATH
   - Run `claude --version` to verify installation

2. **Permission Errors**
   - Ensure write permissions for output folder
   - Check file system permissions for `research_context.md`

3. **Rate Limiting**
   - Adjust `step_delay` in configuration
   - Use `haiku` model for faster development

4. **Perplexity Integration Issues**
   - Verify `PERPLEXITY_API_KEY` environment variable
   - Check MCP server configuration

### Debug Mode

```bash
python workflows/research/research_manager.py \
  "Your research topic" \
  --model haiku \
  --output debug_reports
```

## Contributing

1. Follow the agent specifications in `modes/` directory
2. Maintain technical depth requirements
3. Ensure all agents append to `research_context.md`
4. Include comprehensive error handling
5. Add tests for new functionality

## License

This workflow is part of the agent-flows project and follows the same licensing terms.