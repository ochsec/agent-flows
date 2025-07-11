import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(Enum):
    """Task priority enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PlanningOrganization:
    """Planning and organization tools for Claude Code tools implementation."""
    
    def __init__(self):
        """Initialize the planning and organization tool."""
        # In-memory task storage (in real implementation, this would persist)
        self._todos: List[Dict[str, Any]] = []
        self._plan_mode_active = False
        
    def todo_write(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create and manage structured task lists.
        
        Args:
            todos: List of todo items, each containing:
                - id: Unique identifier for the task
                - content: Task description (required)
                - status: pending/in_progress/completed (required)
                - priority: high/medium/low (required)
                
        Returns:
            Dictionary containing:
                - success: Whether the operation succeeded
                - todos: The updated todo list
                - validation_errors: Any validation errors encountered
                
        Raises:
            ValueError: If validation fails
        """
        validation_errors = []
        
        # Validate todos structure
        if not isinstance(todos, list):
            raise ValueError("todos must be a list")
            
        # Validate each todo item
        for i, todo in enumerate(todos):
            errors = self._validate_todo_item(todo, i)
            validation_errors.extend(errors)
            
        # Check business rules
        in_progress_count = sum(1 for todo in todos if todo.get('status') == TaskStatus.IN_PROGRESS.value)
        if in_progress_count > 1:
            validation_errors.append("Only one task can be in_progress at a time")
            
        # If there are validation errors, return them
        if validation_errors:
            return {
                "success": False,
                "todos": self._todos,
                "validation_errors": validation_errors
            }
            
        # Update the todos list
        self._todos = todos.copy()
        
        # Add timestamps to new todos
        for todo in self._todos:
            if 'created_at' not in todo:
                todo['created_at'] = datetime.now().isoformat()
            if todo['status'] == TaskStatus.COMPLETED.value and 'completed_at' not in todo:
                todo['completed_at'] = datetime.now().isoformat()
                
        return {
            "success": True,
            "todos": self._todos,
            "validation_errors": []
        }
        
    def get_todos(self) -> List[Dict[str, Any]]:
        """
        Get the current todo list.
        
        Returns:
            Current list of todos
        """
        return self._todos.copy()
        
    def exit_plan_mode(self, plan: str) -> Dict[str, Any]:
        """
        Exit planning mode after presenting an implementation plan.
        
        Args:
            plan: The implementation plan to present to the user (supports markdown)
            
        Returns:
            Dictionary containing:
                - success: Whether the operation succeeded
                - plan: The submitted plan
                - message: Status message
                
        Raises:
            ValueError: If plan is empty or too short
        """
        # Validate plan
        if not plan or len(plan.strip()) < 10:
            raise ValueError("Plan must be at least 10 characters long")
            
        # In a real implementation, this would trigger a UI prompt
        # For the prototype, we simulate the behavior
        result = {
            "success": True,
            "plan": plan,
            "message": "Plan submitted. Waiting for user approval to exit plan mode.",
            "timestamp": datetime.now().isoformat()
        }
        
        # Mark that we're attempting to exit plan mode
        self._plan_mode_active = False
        
        return result
        
    def _validate_todo_item(self, todo: Dict[str, Any], index: int) -> List[str]:
        """
        Validate a single todo item.
        
        Args:
            todo: The todo item to validate
            index: The index of the item in the list
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check required fields
        required_fields = ['id', 'content', 'status', 'priority']
        for field in required_fields:
            if field not in todo:
                errors.append(f"Todo {index + 1}: Missing required field '{field}'")
                
        # Validate content
        if 'content' in todo:
            if not isinstance(todo['content'], str) or len(todo['content'].strip()) < 1:
                errors.append(f"Todo {index + 1}: Content must be a non-empty string")
                
        # Validate status
        if 'status' in todo:
            valid_statuses = [s.value for s in TaskStatus]
            if todo['status'] not in valid_statuses:
                errors.append(f"Todo {index + 1}: Invalid status '{todo['status']}'. Must be one of: {valid_statuses}")
                
        # Validate priority
        if 'priority' in todo:
            valid_priorities = [p.value for p in TaskPriority]
            if todo['priority'] not in valid_priorities:
                errors.append(f"Todo {index + 1}: Invalid priority '{todo['priority']}'. Must be one of: {valid_priorities}")
                
        # Validate ID uniqueness
        if 'id' in todo:
            ids = [t.get('id') for t in self._todos if t.get('id') == todo['id']]
            if len(ids) > 1:
                errors.append(f"Todo {index + 1}: Duplicate ID '{todo['id']}'")
                
        return errors
        
    def is_plan_mode_active(self) -> bool:
        """
        Check if plan mode is currently active.
        
        Returns:
            Whether plan mode is active
        """
        return self._plan_mode_active
        
    def enter_plan_mode(self) -> None:
        """Enter plan mode (for testing purposes)."""
        self._plan_mode_active = True
        
    def generate_task_id(self) -> str:
        """
        Generate a unique task ID.
        
        Returns:
            A unique identifier string
        """
        return str(uuid.uuid4())[:8]
        
    def task(self, description: str, prompt: str) -> Dict[str, Any]:
        """
        Launch an independent agent for complex searches and research tasks.
        
        The launched agent begins in Orchestrator Mode, which can coordinate and
        delegate to specialized modes as needed. This is a simulated implementation 
        for the prototype. In a real implementation, this would launch an actual 
        agent with access to all Claude Code tools.
        
        Args:
            description: A short description of the task (3-5 words)
            prompt: The detailed task for the agent to perform
            
        Returns:
            Dictionary containing the agent's response and metadata
            
        Raises:
            ValueError: If description or prompt is too short
        """
        # Validate inputs
        if len(description.strip()) < 3:
            raise ValueError("Description must be at least 3 characters")
            
        if len(prompt.strip()) < 10:
            raise ValueError("Prompt must be at least 10 characters")
            
        # Simulate agent execution
        # In real implementation, this would:
        # 1. Launch a new agent instance in Orchestrator Mode
        # 2. Provide it with the full toolset
        # 3. Orchestrator would delegate to specialized modes as needed
        # 4. Return the synthesized findings from all modes
        
        # For now, simulate some basic research based on the prompt
        simulated_response = self._simulate_agent_task(prompt)
        
        return {
            "description": description,
            "prompt": prompt,
            "response": simulated_response,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "agent_id": f"agent_{hash(prompt) % 10000}",
            "mode": "orchestrator"
        }
    
    def _simulate_agent_task(self, prompt: str) -> str:
        """
        Simulate agent task execution for prototype purposes.
        
        Args:
            prompt: The task prompt
            
        Returns:
            Simulated agent response
        """
        # Analyze the prompt to determine what kind of task it is
        prompt_lower = prompt.lower()
        
        if any(keyword in prompt_lower for keyword in ["find", "locate", "search for"]):
            return f"[Orchestrator Mode] Task Analysis\\n\\nI've analyzed the task '{prompt}' and delegated it to the Researcher mode for comprehensive search operations.\\n\\nResearcher Mode Results:\\n- Searched through the codebase using multiple strategies\\n- Located relevant files in the project structure\\n- Identified patterns and implementations\\n- Analyzed code relationships and dependencies\\n\\nThe search was completed successfully with all relevant information gathered.\\n\\nNote: This is a simulated response for prototype purposes."
            
        elif any(keyword in prompt_lower for keyword in ["implement", "create", "build"]):
            return f"[Orchestrator Mode] Task Delegation\\n\\nI've analyzed the task '{prompt}' and delegated it across multiple specialized modes:\\n\\n1. Architect Mode: Designed the solution architecture\\n2. Code Mode: Implemented the core functionality\\n3. Debug Mode: Validated the implementation\\n\\nAll subtasks completed successfully. The implementation follows best practices and integrates well with the existing codebase.\\n\\nNote: This is a simulated response for prototype purposes."
            
        elif any(keyword in prompt_lower for keyword in ["analyze", "understand", "explain"]):
            return f"[Orchestrator Mode] Analysis Coordination\\n\\nFor the task '{prompt}', I coordinated analysis across multiple modes:\\n\\n1. Researcher Mode: Gathered comprehensive information\\n2. Expert Consultant Mode: Provided domain expertise\\n3. Synthesizer Mode: Combined findings into coherent insights\\n\\nThe analysis is complete with detailed findings documented.\\n\\nNote: This is a simulated response for prototype purposes."
            
        else:
            return f"[Orchestrator Mode] Task Execution\\n\\nTask: '{prompt}'\\n\\nI've coordinated the execution of this task by:\\n1. Breaking it down into subtasks\\n2. Delegating to appropriate specialized modes\\n3. Synthesizing the results\\n\\nThe task was completed successfully using the full range of available tools and specialized modes.\\n\\nNote: This is a simulated response for prototype purposes."