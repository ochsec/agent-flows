# OpenRouter Migration Guide

This guide helps you migrate your workflows from Claude Code CLI to OpenRouter, giving you access to 400+ AI models from multiple providers.

## Overview

**Benefits of Migration:**
- 🌐 Access to **400+ models** from providers like OpenAI, Anthropic, Google, Meta, Mistral
- 💰 **Cost optimization** with automatic model routing and fallbacks  
- 🔑 **Single API key** instead of managing multiple provider keys
- 🚀 **Better performance** with direct API calls vs CLI subprocess overhead
- 🎯 **Model flexibility** - switch models without changing your code

## Quick Start

### 1. Install Dependencies
```bash
pip install openai>=1.0.0  # OpenRouter uses OpenAI SDK
```

### 2. Get OpenRouter API Key
1. Sign up at [openrouter.ai](https://openrouter.ai)
2. Get your API key from the dashboard
3. Set environment variable:
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

### 3. Choose Your Migration Path

#### Option A: Use New OpenRouter Workflows (Recommended)
```bash
# Research workflow
python workflows/research/research_openrouter.py "your research topic"

# Code review workflow  
python workflows/code_review/review_openrouter.py 123 --repository owner/repo

# JIRA task workflow
python workflows/jira_task/enhanced_workflow_openrouter.py PROJ-123 "implement feature"
```

#### Option B: Replace Claude Code Client in Existing Workflows
Use the `OpenRouterClient` class to replace `subprocess.run(["claude", ...])` calls:

```python
from openrouter_client import OpenRouterClient, WorkflowType

# Replace Claude Code CLI calls
client = OpenRouterClient(workflow_type=WorkflowType.RESEARCH)
result = client.execute_prompt("Your prompt here")
```

## Recommended Models by Workflow

### Research Workflow
- **Primary**: `perplexity/llama-3.1-sonar-large-128k-online` ($0.001/1K tokens)
  - Excellent for research with web access
- **Alternative**: `anthropic/claude-3-haiku` ($0.00025/1K tokens)
  - Fast and cost-effective

### Code Review Workflow  
- **Primary**: `anthropic/claude-3.5-sonnet` ($0.003/1K tokens)
  - Best for code analysis and complex reasoning
- **Alternative**: `deepseek/deepseek-coder` ($0.00014/1K tokens)
  - Specialized for code review tasks

### JIRA Task Development
- **Primary**: `anthropic/claude-3.5-sonnet` ($0.003/1K tokens)
  - Excellent for development tasks
- **Alternative**: `openai/gpt-4-turbo` ($0.01/1K tokens)
  - Great for comprehensive analysis

## Migration Examples

### Before: Claude Code CLI
```python
import subprocess

command = ["claude", "-p", "--verbose", "--model", "sonnet", "--allowedTools", "bash,webSearch"]
result = subprocess.run(command, input=prompt, capture_output=True, text=True, timeout=1800)
response = result.stdout.strip()
```

### After: OpenRouter API
```python
from openrouter_client import OpenRouterClient, WorkflowType

client = OpenRouterClient(workflow_type=WorkflowType.RESEARCH)
result = client.execute_prompt(prompt, timeout=1800)
response = result["content"]
```

## Workflow-Specific Migration

### Research Workflow Migration

**Old Command:**
```bash
python workflows/research/research.py "AI trends 2024"
```

**New Command:**
```bash
python workflows/research/research_openrouter.py "AI trends 2024"
```

**Key Differences:**
- ✅ Direct API calls (faster)
- ✅ Better error handling  
- ✅ Cost estimation
- ✅ Multiple model options
- ✅ Usage tracking

### Code Review Migration

**Old Command:**
```bash
python workflows/code_review/review.py 123 --repository owner/repo
```

**New Command:**
```bash
python workflows/code_review/review_openrouter.py 123 --repository owner/repo
```

**Enhanced Features:**
- `--list-models`: See recommended models
- `--estimate-cost`: Estimate review cost before running
- `--model`: Specify exact model to use

### JIRA Task Migration

**Old Command:**
```bash
python workflows/jira_task/enhanced_workflow.py
```

**New Command:**
```bash
python workflows/jira_task/enhanced_workflow_openrouter.py PROJ-123 "implement user authentication"
```

**Enhanced Features:**
- Context preservation across interactions
- Dynamic model switching
- Better error recovery
- Cost tracking

## Configuration

### Environment Variables
```bash
# Required
export OPENROUTER_API_KEY="your-api-key"

# Optional (for OpenRouter leaderboards)
export OPENROUTER_SITE_URL="https://github.com/yourusername/yourproject"
export OPENROUTER_SITE_NAME="Your Project Name"
```

### Model Selection
```python
# List available models for a workflow type
python -c "
from openrouter_client import OpenRouterModels, WorkflowType
models = OpenRouterModels.get_recommended_models(WorkflowType.RESEARCH)
for model in models:
    print(f'{model.name}: {model.description}')
"
```

## Cost Comparison

| Provider | Model | Cost per 1K tokens | Best for |
|----------|-------|-------------------|----------|
| Claude Code | claude-3.5-sonnet | $0.003 | All workflows |
| OpenRouter | anthropic/claude-3.5-sonnet | $0.003 | Same model, more flexibility |
| OpenRouter | anthropic/claude-3-haiku | $0.00025 | Cost-effective tasks |
| OpenRouter | deepseek/deepseek-coder | $0.00014 | Code-focused tasks |
| OpenRouter | perplexity/sonar-large | $0.001 | Research with web access |

## Troubleshooting

### Common Issues

#### "OpenRouter API key required"
```bash
export OPENROUTER_API_KEY="your-key-here"
# Or pass directly:
python script.py --api-key "your-key-here"
```

#### "Model not found"
```bash
# List available models
python script.py --list-models
```

#### Import errors
```bash
pip install openai>=1.0.0
```

### Getting Help

1. **Check model availability**: Use `--list-models` flag
2. **Estimate costs**: Use `--estimate-cost` flag  
3. **Enable verbose logging**: Use `--verbose` flag
4. **Test with simple prompts**: Start with basic requests

## Advanced Usage

### Custom Model Configuration
```python
from openrouter_client import OpenRouterClient

client = OpenRouterClient()
# Use specific model
result = client.execute_prompt(
    prompt="your prompt", 
    model="anthropic/claude-3.5-sonnet",
    max_tokens=4096,
    temperature=0.7
)
```

### Cost Estimation
```python
cost_info = client.estimate_cost("your prompt", model="anthropic/claude-3.5-sonnet")
print(f"Estimated cost: ${cost_info['estimated_cost']:.4f}")
```

### Multiple Models in One Workflow
```python
# Use different models for different tasks
research_client = OpenRouterClient(workflow_type=WorkflowType.RESEARCH)
code_client = OpenRouterClient(workflow_type=WorkflowType.CODE_REVIEW)

# Each optimized for their respective tasks
research_result = research_client.execute_prompt("research prompt")
code_result = code_client.execute_prompt("code review prompt")
```

## Next Steps

1. **Start with one workflow**: Migrate your most-used workflow first
2. **Test with small tasks**: Verify functionality before large projects
3. **Monitor costs**: Use the cost estimation features
4. **Experiment with models**: Try different models for different use cases
5. **Optimize for your needs**: Adjust models based on quality vs cost preferences

## Support

- **OpenRouter Documentation**: [openrouter.ai/docs](https://openrouter.ai/docs)
- **Model Information**: [openrouter.ai/models](https://openrouter.ai/models)
- **GitHub Issues**: Report problems in your project repository

---

**Ready to migrate?** Start with the research workflow using:
```bash
python workflows/research/research_openrouter.py "test migration" --list-models
```