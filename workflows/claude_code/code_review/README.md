# Code Review Workflow - Claude Code Integration

A comprehensive multi-agent code review workflow system that orchestrates specialized AI agents using Claude Code to conduct thorough PR reviews with parallel processing and real-time intelligence.

## Overview

This workflow implements an AI-powered GitHub pull request review system using Claude Code as the execution layer with Python orchestration. It coordinates five specialized agents through a systematic review process:

1. **Code Analyzer** - Code quality, complexity, and best practices analysis
2. **Security Reviewer** - Vulnerability detection and security assessment
3. **Documentation Agent** - Documentation quality and completeness evaluation
4. **Performance Optimizer** - Performance bottlenecks and optimization opportunities
5. **Integration Tester** - Test coverage and integration testing analysis

## Features

- **Claude Code Integration**: Uses Claude Code CLI as the primary AI execution layer
- **Multi-Agent Orchestration**: Parallel execution of specialized review agents
- **Local Analysis Focus**: Designed for local code analysis and review
- **Perplexity AI Enhancement**: Real-time knowledge access for current best practices
- **Weighted Scoring System**: Configurable criteria-based scoring and recommendations
- **Comprehensive Reporting**: Detailed review reports with actionable insights
- **Flexible Configuration**: Environment-specific configurations and customization

## Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Install Claude Code CLI**:
```bash
curl -fsSL https://claude.ai/install.sh | sh
echo "$HOME/.claude/bin" >> $PATH
```

3. **Set Environment Variables** (Optional):
```bash
export PERPLEXITY_API_KEY="your-perplexity-api-key"  # Optional for enhanced analysis
```

**Note**: No API keys required for basic functionality. Claude Code handles authentication automatically when signed in.

## Usage

### Command Line Interface

```bash
# Basic PR review (uses current repository context)
python workflows/claude_code/code_review/pr_reviewer.py 123

# Review PR in specific repository
python workflows/claude_code/code_review/pr_reviewer.py 123 \
  --repository anthropics/claude-code

# With specific Claude model
python workflows/claude_code/code_review/pr_reviewer.py 123 \
  --model sonnet

# With custom instructions
python workflows/claude_code/code_review/pr_reviewer.py 456 \
  --repository myorg/myrepo \
  --instructions "Focus on security and performance"

# With enhanced Perplexity analysis
python workflows/claude_code/code_review/pr_reviewer.py 456 \
  --repository myorg/myrepo \
  --model sonnet \
  --parallel-agents 5 \
  --perplexity-api-key $PERPLEXITY_API_KEY

# Alternative: Run as module
python -m workflows.claude_code.code_review.pr_reviewer 123
```


### Python API

```python
from workflows.claude_code.code_review import PRReviewWorkflow

# Initialize workflow with Claude Code (default)
workflow = PRReviewWorkflow(model="sonnet")

# Or with Perplexity integration
workflow = PRReviewWorkflow(
    model="sonnet", 
    perplexity_api_key="your-perplexity-key"
)

# Execute review for specific PR
results = workflow.review_pr("anthropics/claude-code", 123)

print(f"Overall Score: {results['overall_score']:.1f}/10")
print(f"Recommendation: {results['recommendation']}")
```

## Configuration

Review criteria and workflow settings are configured directly in the Python code. The default configuration includes:

- **Code Quality** (30% weight): Complexity, best practices, maintainability
- **Security** (30% weight): Vulnerability detection, secure coding practices  
- **Documentation** (20% weight): Comment coverage, API documentation
- **Performance** (10% weight): Algorithmic efficiency, resource usage
- **Testing** (10% weight): Test coverage and quality

Configuration can be customized by modifying the workflow parameters.

## Workflow Process

### 1. Local Code Analysis Setup
- Creates analysis context for the specified code review task
- Prepares data structure for multi-agent analysis
- Configures parallel execution environment

### 2. Parallel Agent Execution
- **Code Analyzer**: Evaluates complexity, quality, and best practices
- **Security Reviewer**: Scans for vulnerabilities and security issues
- **Documentation Agent**: Checks documentation coverage and quality
- **Performance Optimizer**: Identifies performance bottlenecks
- **Integration Tester**: Analyzes test coverage and quality

### 3. Enhanced Context (Perplexity AI)
- Fetches current best practices for detected technologies
- Provides real-time security guidelines and standards
- Offers performance insights and optimization strategies
- Suggests testing methodologies and frameworks

### 4. Result Aggregation
- Calculates weighted overall score based on criteria
- Aggregates issues, suggestions, and comments
- Generates recommendation (APPROVE, REQUEST_CHANGES, REJECT)
- Creates comprehensive review summary

### 5. Local Results Saving
- Saves comprehensive review results to JSON file
- Generates markdown summary report
- Provides console output with key metrics
- Stores results for future analysis

## Agent Specifications

### Code Analyzer Agent
- **Language Detection**: Automatic programming language identification
- **Complexity Analysis**: Cyclomatic complexity and maintainability scoring
- **Best Practices**: Language-specific convention checking
- **Refactoring Suggestions**: Improvement recommendations

### Security Reviewer Agent
- **Vulnerability Scanning**: OWASP Top 10 and language-specific patterns
- **Authentication Analysis**: Credential and authorization checking
- **Data Exposure Detection**: Sensitive data logging and exposure
- **Security Standards**: Framework-specific security guidelines

### Documentation Agent
- **Coverage Analysis**: Function and API documentation completeness
- **Quality Assessment**: Clarity and accuracy evaluation
- **README Validation**: Documentation update requirements
- **API Documentation**: Interface and usage documentation

### Performance Optimizer Agent
- **Algorithmic Analysis**: Complexity and efficiency evaluation
- **Memory Patterns**: Memory usage and leak detection
- **Network Optimization**: API and database query efficiency
- **Scalability Assessment**: Performance under load considerations

### Integration Tester Agent
- **Coverage Analysis**: Test coverage threshold validation
- **Test Quality**: Assertion and test case completeness
- **Integration Scenarios**: End-to-end testing recommendations
- **Testing Strategies**: Framework and methodology suggestions

## Output Structure

```
review_results_local_pr_0.json           # Complete JSON results
review_summary_local_pr_0.md             # Markdown summary
```

### Review Result Format

```json
{
  "overall_score": 8.2,
  "recommendation": "APPROVE_WITH_SUGGESTIONS",
  "agent_results": {
    "code_analyzer": {
      "score": 8.5,
      "issues": [...],
      "suggestions": [...],
      "summary": "Code analysis completed..."
    }
  },
  "enhanced_context": {
    "security_guidelines": {...},
    "code_quality_standards": {...},
    "performance_insights": {...}
  },
  "summary": {
    "total_issues": 3,
    "total_suggestions": 7,
    "execution_time": 45.2
  }
}
```

## Performance Characteristics

| PR Size | Lines of Code | Review Time | Agents | Memory Usage |
|---------|---------------|-------------|--------|--------------|
| Small   | <100         | 15-30s      | 5      | <500MB       |
| Medium  | 100-500      | 30-60s      | 5      | 500MB-1GB    |
| Large   | 500-1000     | 1-2min      | 5-7    | 1-2GB        |
| XL      | >1000        | 2-5min      | 7-10   | 2-4GB        |

## Error Handling

The workflow includes comprehensive error handling:

- **Agent Failures**: Individual agent failures don't stop the review
- **Rate Limiting**: Automatic retry with exponential backoff
- **Timeout Handling**: Configurable timeouts for long-running operations
- **API Errors**: Graceful degradation when external APIs are unavailable

## Troubleshooting

### Common Issues

1. **Claude Code Not Available**
   ```bash
   # Verify Claude Code installation
   claude --version
   # Reinstall if necessary
   curl -fsSL https://claude.ai/install.sh | sh
   ```

2. **GitHub API Rate Limiting**
   ```bash
   # Check rate limit status
   curl -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/rate_limit
   ```

3. **Permission Errors**
   - Ensure GitHub token has proper permissions: `repo`, `pull_requests`
   - Verify Anthropic API key is valid and has sufficient credits

4. **Memory Issues with Large PRs**
   ```python
   # Reduce parallel agents for large PRs
   config.update_config({"workflow": {"parallel_agents": 3}})
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Use lighter model for testing
python workflows/claude_code/code_review/pr_reviewer.py \
  --model haiku \
  --parallel-agents 3
```

## Customization

### Custom Agent Integration

```python
from workflows.claude_code.code_review.agents import CodeReviewAgent

class CustomSecurityAgent(CodeReviewAgent):
    def __init__(self, config):
        super().__init__("Custom Security", config)
    
    def analyze(self, pr_data, executor):
        # Custom security analysis logic
        return ReviewResult(...)
```

## Contributing

1. Follow the agent specifications in the codebase
2. Maintain comprehensive error handling
3. Include tests for new functionality
4. Update documentation for changes
5. Follow the established coding standards

## Performance Optimization

### For Large Repositories
- Use intelligent code chunking for context window management
- Implement differential analysis to focus on changed areas
- Cache frequently accessed data and analysis results
- Use parallel processing for independent operations

### For High-Volume Usage
- Implement request queuing and rate limiting
- Use connection pooling for API requests
- Cache results for similar code patterns
- Optimize agent execution order based on dependencies

## License

This workflow is part of the agent-flows project and follows the same licensing terms.