# Separated Jira Workflows

This document describes the separated Jira workflow components that split task execution from issue fetching.

## Components

### 1. TaskExecutor (`task_executor.py`)
Standalone task execution workflow that can be invoked with a prompt from any source.

**Key Features:**
- Executes tasks from text prompts
- Optional branch management
- Interactive development mode
- Integration with Claude Code
- Task state tracking

**Usage:**
```python
from workflows.jira_task import TaskExecutor

# Basic task execution
executor = TaskExecutor()
result = executor.execute_task("Add logging to the authentication module")

# With specific branch
result = executor.execute_task(
    task_prompt="Fix bug in payment processing",
    task_id="custom-task-1",
    branch_name="feature/payment-fix"
)

# Interactive mode
executor.interactive_development_mode("Refactor database connection", "task-123")
```

**Command Line:**
```bash
# Basic execution
python -m workflows.jira_task.task_executor "Add unit tests for user service"

# With options
python -m workflows.jira_task.task_executor "Fix memory leak" --task-id "leak-fix" --branch "hotfix/memory"

# Interactive mode
python -m workflows.jira_task.task_executor "Implement caching" --interactive

# Check status
python -m workflows.jira_task.task_executor --status task-123
python -m workflows.jira_task.task_executor --list
```

### 2. JiraIssueFetcher (`jira_fetcher.py`)
Fetches Jira issues and pipes them to the task execution workflow.

**Key Features:**
- Fetches issue details from Jira
- Converts issues to task prompts
- Creates feature branches
- Pipes to TaskExecutor
- Updates Jira with progress

**Usage:**
```python
from workflows.jira_task import JiraIssueFetcher, load_jira_config

# Setup
config = load_jira_config()
fetcher = JiraIssueFetcher(config)

# Fetch and execute immediately
result = fetcher.fetch_and_execute_issue("PROJ-123", execute_immediately=True)

# Fetch only (no execution)
result = fetcher.fetch_and_execute_issue("PROJ-124", execute_immediately=False)

# Pipe to task executor later
result = fetcher.pipe_issue_to_task_executor("PROJ-124", interactive=True)

# List my issues
issues = fetcher.fetch_my_issues("In Progress")
```

**Command Line:**
```bash
# Fetch and execute
python -m workflows.jira_task.jira_fetcher PROJ-123 --execute-immediately

# Fetch only
python -m workflows.jira_task.jira_fetcher PROJ-124 --command fetch

# Pipe to executor
python -m workflows.jira_task.jira_fetcher PROJ-124 --command pipe --interactive

# List issues
python -m workflows.jira_task.jira_fetcher --command list --status-filter "To Do"
```

## Workflow Separation Benefits

### 1. Modularity
- Task execution is completely independent of Jira
- Can execute tasks from any source (CLI, API, other systems)
- Easy to test individual components

### 2. Flexibility
- Use TaskExecutor with any prompt source
- Mix Jira and non-Jira tasks in same workflow
- Support for multiple task sources simultaneously

### 3. Reusability
- TaskExecutor can be used in other workflows
- JiraIssueFetcher can pipe to different executors
- Components can be composed differently for different use cases

## Integration Examples

### 1. Non-Jira Task Execution
```python
# Execute tasks from any source
executor = TaskExecutor()

# From a text file
with open("tasks.txt") as f:
    for line in f:
        if line.strip():
            executor.execute_task(line.strip())

# From user input
task = input("What would you like me to work on? ")
executor.execute_task(task)

# From another system
api_task = get_task_from_external_api()
executor.execute_task(api_task['description'])
```

### 2. Batch Processing
```python
# Process multiple Jira issues
fetcher = JiraIssueFetcher(config)
executor = TaskExecutor()

issues = ["PROJ-123", "PROJ-124", "PROJ-125"]
for issue_key in issues:
    # Fetch issue details
    result = fetcher.fetch_and_execute_issue(issue_key, execute_immediately=False)
    if result['status'] == 'success':
        # Execute with custom settings
        executor.execute_task(
            task_prompt=result['task_prompt'],
            task_id=issue_key,
            branch_name=result['branch_name']
        )
```

### 3. Custom Workflow
```python
# Create a custom workflow combining both
class CustomWorkflow:
    def __init__(self, jira_config):
        self.fetcher = JiraIssueFetcher(jira_config)
        self.executor = TaskExecutor()
    
    def process_priority_issues(self):
        # Get high priority issues
        issues = self.fetcher.fetch_my_issues("To Do")
        priority_issues = [i for i in issues if i.get('priority') == 'High']
        
        for issue in priority_issues:
            # Fetch and execute
            self.fetcher.pipe_issue_to_task_executor(issue['key'])
```

## Configuration

The separated workflows use the same configuration as the original workflow:

```bash
# Copy sample configuration
cp workflows/jira_task/.env.sample .env

# Edit with your settings
nano .env
```

Required environment variables:
- `JIRA_SERVER_URL`
- `JIRA_USERNAME`
- `JIRA_API_TOKEN`

## Migration from Original Workflow

The original `jira_task.py` workflow is still available and functional. To migrate to the separated workflows:

### 1. Replace Direct Usage
```python
# Old way
from workflows.jira_task import JiraWorkflow
workflow = JiraWorkflow(config)
workflow.start_work_on_issue("PROJ-123")

# New way
from workflows.jira_task import JiraIssueFetcher
fetcher = JiraIssueFetcher(config)
fetcher.fetch_and_execute_issue("PROJ-123")
```

### 2. Use Individual Components
```python
# For task-only execution
from workflows.jira_task import TaskExecutor
executor = TaskExecutor()
executor.execute_task("Your task description here")

# For Jira-only fetching
from workflows.jira_task import JiraIssueFetcher
fetcher = JiraIssueFetcher(config)
task_prompt = fetcher.get_issue_task_prompt("PROJ-123")
```

## Benefits of the Separated Architecture

1. **Modularity**: Each component has a single responsibility
2. **Testability**: Easier to unit test individual components
3. **Flexibility**: Can mix and match components as needed
4. **Reusability**: TaskExecutor can be used with any task source
5. **Maintainability**: Cleaner separation of concerns
6. **Extensibility**: Easy to add new task sources or executors