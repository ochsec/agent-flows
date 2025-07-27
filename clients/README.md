# LLM Clients for Agent Workflows

This document describes the new multi-LLM support that has been added to the agent workflows, allowing you to use either OpenRouter (cloud-based) or LM Studio (local) for running LLMs.

## Overview

All workflows now support two LLM providers:
- **OpenRouter**: Cloud-based access to various commercial and open-source models
- **LM Studio**: Local execution of open-source models on your own hardware

## Installation

### Environment Configuration
1. Copy `.env.example` to `.env` in the project root
2. Fill in your configuration values

### For OpenRouter
1. Get an API key from [OpenRouter](https://openrouter.ai/)
2. Set the `OPENROUTER_API_KEY` in your `.env` file

### For LM Studio
1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a model in LM Studio
3. Enable the local server in LM Studio settings
4. Set `LMSTUDIO_BASE_URL` in your `.env` file if not using default (localhost:1234)

## Multi-LLM Workflows

The following workflows support both OpenRouter and LM Studio:
- `workflows/research/research_multi_llm.py` - Research workflow with multi-LLM support
- `workflows/code_review/review_multi_llm.py` - Code review workflow with multi-LLM support
- `workflows/jira_task/jira_task_multi_llm.py` - JIRA task workflow with multi-LLM support

## Common Command-Line Arguments

- `--provider`: Choose between "openrouter" or "lmstudio"
- `--model`: Specify the model to use
- `--lmstudio-url`: LM Studio API URL (default: http://localhost:1234/v1)
- `--api-key`: OpenRouter API key (if not using environment variable)
- `--output`: Output directory for generated files
- `--list-models`: List available models for the selected provider

## Usage Examples

### Research Workflow

#### Using OpenRouter (default):
```bash
python workflows/research/research_multi_llm.py "Best practices for microservices architecture"

# With specific model:
python workflows/research/research_multi_llm.py "Best practices for microservices architecture" \
  --provider openrouter \
  --model "anthropic/claude-3.5-sonnet"
```

#### Using LM Studio:
```bash
python workflows/research/research_multi_llm.py "Best practices for microservices architecture" \
  --provider lmstudio

# With custom model and URL:
python workflows/research/research_multi_llm.py "Best practices for microservices architecture" \
  --provider lmstudio \
  --model "llama-3-8b" \
  --lmstudio-url "http://localhost:1234/v1"

# Example with specific IP and model:
python workflows/research/research_multi_llm.py "Your topic" \
  --provider lmstudio \
  --lmstudio-url "http://192.168.0.155:6666/v1" \
  --model "qwen3-32b-mlx"
```

### Code Review Workflow

#### Using OpenRouter:
```bash
python workflows/code_review/review_multi_llm.py --base main

# With output file:
python workflows/code_review/review_multi_llm.py \
  --base main \
  --output review_report.md \
  --provider openrouter
```

#### Using LM Studio:
```bash
python workflows/code_review/review_multi_llm.py \
  --base main \
  --provider lmstudio \
  --model "codellama-13b"
```

### JIRA Task Workflow

#### Using OpenRouter:
```bash
python workflows/jira_task/jira_task_multi_llm.py \
  --task-id "PROJ-123" \
  --tech-stack "Python, FastAPI, PostgreSQL" \
  --output ./implementations
```

#### Using LM Studio:
```bash
python workflows/jira_task/jira_task_multi_llm.py \
  --description "Implement user authentication with JWT tokens" \
  --tech-stack "Node.js, Express" \
  --provider lmstudio \
  --model "deepseek-coder-6.7b"
```

## Listing Available Models

You can list recommended models for each provider:

```bash
# List OpenRouter models for research
python workflows/research/research_multi_llm.py --list-models --provider openrouter

# List LM Studio models for code review
python workflows/code_review/review_multi_llm.py --list-models --provider lmstudio
```

## Configuration

### Environment Variables

#### OpenRouter:
- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `OPENROUTER_SITE_URL`: Your site URL for leaderboards (optional)
- `OPENROUTER_SITE_NAME`: Your site name for leaderboards (optional)

#### LM Studio:
- `LMSTUDIO_BASE_URL`: Base URL for LM Studio API (default: http://localhost:1234/v1)

### Recommended Models

#### For Research Tasks:
- **OpenRouter**: anthropic/claude-3.5-sonnet, openai/gpt-4-turbo
- **LM Studio**: mixtral-8x7b, mistral-7b

#### For Code Review:
- **OpenRouter**: anthropic/claude-3.5-sonnet, deepseek/deepseek-coder
- **LM Studio**: codellama-13b, deepseek-coder-6.7b

#### For JIRA Tasks:
- **OpenRouter**: anthropic/claude-3.5-sonnet, openai/gpt-4-turbo
- **LM Studio**: deepseek-coder-6.7b, codellama-13b

## Architecture

The multi-LLM support is implemented through:

1. **Abstract Base Class** (`llm_client.py`): Defines the common interface
2. **Provider Implementations**:
   - `openrouter_client.py`: OpenRouter implementation
   - `lmstudio_client.py`: LM Studio implementation
3. **Updated Workflows**: All workflows in the `workflows/` directory now accept a client parameter

## File Structure

```
clients/
├── __init__.py          # Package initialization
├── llm_client.py        # Abstract base class
├── openrouter_client.py # OpenRouter implementation
├── lmstudio_client.py   # LM Studio implementation
└── README.md            # This documentation
```

## Migration Notes

The legacy OpenRouter-only workflow files have been removed in favor of the unified multi-LLM workflows. All functionality is preserved in the new files with the same command-line interface, plus the addition of:
- `--provider`: Choose between "openrouter" or "lmstudio" 
- `--lmstudio-url`: Specify LM Studio API URL if not using default

To use OpenRouter (same as before), simply add `--provider openrouter` to your existing commands.

## Cost Considerations

- **OpenRouter**: Pay per token based on the model used
- **LM Studio**: Free (runs on your local hardware)

## Performance Notes

- **OpenRouter**: Generally faster response times, larger context windows
- **LM Studio**: Performance depends on your hardware (GPU recommended)

## Troubleshooting

### LM Studio Connection Issues
1. Ensure LM Studio is running
2. Check that the local server is enabled in settings
3. Verify a model is loaded
4. Check the API URL (default: http://localhost:1234/v1)

### OpenRouter Issues
1. Verify your API key is correct
2. Check your account has credits
3. Ensure the model name is correct

## Future Enhancements

- Support for additional providers (Ollama, Together AI, etc.)
- Model-specific parameter tuning
- Automatic fallback between providers
- Cost tracking and optimization