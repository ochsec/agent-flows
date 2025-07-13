import uuid
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


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


class ThinkingLevel(Enum):
    """Thinking budget levels for different task complexities."""
    THINK = "think"
    THINK_HARD = "think_hard"
    THINK_HARDER = "think_harder"
    ULTRATHINK = "ultrathink"


class PlanTemplate(Enum):
    """Plan templates for different project types."""
    FEATURE_DEVELOPMENT = "feature_development"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"
    RESEARCH = "research"
    ARCHITECTURE = "architecture"


class AgentMode(Enum):
    """Specialized agent modes for different tasks."""
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    ARCHITECT = "architect"
    CODE = "code"
    DEBUG = "debug"
    EXPERT_CONSULTANT = "expert_consultant"
    SYNTHESIZER = "synthesizer"
    WRITER = "writer"


@dataclass
class AgentTask:
    """Task for specialized agents."""
    id: str
    mode: str
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


@dataclass
class AgentResult:
    """Result from a specialized agent."""
    agent_id: str
    mode: str
    task_id: str
    success: bool
    data: Dict[str, Any]
    execution_time: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SpecializedAgent:
    """Base class for specialized agents."""
    
    def __init__(self, agent_id: str, mode: AgentMode):
        self.agent_id = agent_id
        self.mode = mode
        self.is_busy = False
        self.current_task = None
        
    def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a task and return results."""
        self.is_busy = True
        self.current_task = task
        start_time = time.time()
        
        try:
            # Delegate to specialized execution method
            result_data = self._execute_specialized_task(task)
            success = True
        except Exception as e:
            result_data = {"error": str(e), "traceback": None}
            success = False
        
        execution_time = time.time() - start_time
        
        result = AgentResult(
            agent_id=self.agent_id,
            mode=self.mode.value,
            task_id=task.id,
            success=success,
            data=result_data,
            execution_time=execution_time
        )
        
        task.result = asdict(result)
        task.completed_at = datetime.now().isoformat()
        
        self.is_busy = False
        self.current_task = None
        
        return result
    
    def _execute_specialized_task(self, task: AgentTask) -> Dict[str, Any]:
        """Override in subclasses for specialized behavior."""
        raise NotImplementedError("Subclasses must implement _execute_specialized_task")


class ResearcherAgent(SpecializedAgent):
    """Agent specialized in research and information gathering."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentMode.RESEARCHER)
    
    def _execute_specialized_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute research tasks."""
        prompt = task.prompt.lower()
        
        # Simulate research capabilities
        if "find" in prompt or "search" in prompt or "locate" in prompt:
            return {
                "type": "search_results",
                "findings": [
                    "Located relevant files in project structure",
                    "Identified patterns and relationships",
                    "Analyzed dependencies and imports",
                    "Documented key components"
                ],
                "files_analyzed": 15,
                "patterns_found": 8,
                "confidence": 0.9
            }
        elif "analyze" in prompt or "understand" in prompt:
            return {
                "type": "analysis_results",
                "insights": [
                    "System architecture follows MVC pattern",
                    "Dependencies are well-organized",
                    "Code quality metrics are above average",
                    "Documentation coverage is 85%"
                ],
                "complexity_score": 6,
                "maintainability": 0.8,
                "recommendations": [
                    "Consider adding more unit tests",
                    "Refactor large functions",
                    "Update outdated documentation"
                ]
            }
        else:
            return {
                "type": "general_research",
                "summary": f"Conducted comprehensive research on: {task.prompt}",
                "key_findings": [
                    "Gathered relevant information from multiple sources",
                    "Analyzed current state and context",
                    "Identified potential approaches"
                ],
                "confidence": 0.8
            }


class ArchitectAgent(SpecializedAgent):
    """Agent specialized in solution architecture and design."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentMode.ARCHITECT)
    
    def _execute_specialized_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute architecture design tasks."""
        return {
            "type": "architecture_design",
            "solution_architecture": {
                "components": [
                    "Data Layer - Handle persistence and retrieval",
                    "Business Logic Layer - Core functionality",
                    "API Layer - External interfaces",
                    "Presentation Layer - User interfaces"
                ],
                "patterns": ["Repository Pattern", "Factory Pattern", "Observer Pattern"],
                "technologies": ["Python", "SQLAlchemy", "FastAPI", "React"]
            },
            "design_principles": [
                "Separation of Concerns",
                "Single Responsibility",
                "Dependency Inversion",
                "Open/Closed Principle"
            ],
            "scalability_considerations": [
                "Horizontal scaling capabilities",
                "Caching strategies",
                "Load balancing",
                "Database optimization"
            ],
            "estimated_complexity": 7,
            "implementation_time_days": 14
        }


class CodeAgent(SpecializedAgent):
    """Agent specialized in code implementation."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentMode.CODE)
    
    def _execute_specialized_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute code implementation tasks."""
        return {
            "type": "implementation_results",
            "implementation_plan": [
                "Set up project structure and dependencies",
                "Implement core data models",
                "Create business logic components",
                "Build API endpoints",
                "Add error handling and validation",
                "Write unit and integration tests"
            ],
            "code_structure": {
                "modules": ["models", "services", "controllers", "utils"],
                "test_coverage_target": 90,
                "coding_standards": "PEP 8",
                "documentation_format": "Google Style"
            },
            "technical_decisions": [
                "Use SQLAlchemy for ORM",
                "Implement async/await for I/O operations",
                "Add comprehensive logging",
                "Use dependency injection"
            ],
            "estimated_loc": 2500,
            "confidence": 0.85
        }


class DebugAgent(SpecializedAgent):
    """Agent specialized in debugging and problem resolution."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentMode.DEBUG)
    
    def _execute_specialized_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute debugging tasks."""
        return {
            "type": "debug_analysis",
            "issue_analysis": {
                "potential_causes": [
                    "Race condition in concurrent operations",
                    "Memory leak in caching layer",
                    "Database connection pool exhaustion",
                    "Unhandled edge cases in validation"
                ],
                "severity": "medium",
                "impact_scope": "moderate"
            },
            "debugging_steps": [
                "Reproduce issue in controlled environment",
                "Add detailed logging to suspected areas",
                "Profile memory and CPU usage",
                "Analyze database query patterns",
                "Test with various input combinations"
            ],
            "recommended_fixes": [
                "Add proper synchronization mechanisms",
                "Implement cache eviction policies",
                "Optimize database connection management",
                "Add comprehensive input validation"
            ],
            "testing_strategy": [
                "Unit tests for edge cases",
                "Integration tests for workflows",
                "Load testing for performance",
                "Regression tests for stability"
            ],
            "confidence": 0.8
        }


class ExpertConsultantAgent(SpecializedAgent):
    """Agent specialized in domain expertise and best practices."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentMode.EXPERT_CONSULTANT)
    
    def _execute_specialized_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute expert consultation tasks."""
        return {
            "type": "expert_consultation",
            "domain_expertise": {
                "best_practices": [
                    "Follow SOLID principles in design",
                    "Implement comprehensive error handling",
                    "Use design patterns appropriately",
                    "Maintain high test coverage"
                ],
                "industry_standards": [
                    "RESTful API design",
                    "Security best practices",
                    "Performance optimization",
                    "Code maintainability"
                ],
                "risk_assessment": {
                    "technical_risks": ["Scalability limitations", "Security vulnerabilities"],
                    "business_risks": ["Timeline delays", "Resource constraints"],
                    "mitigation_strategies": ["Phased rollout", "Security audit", "Load testing"]
                }
            },
            "recommendations": [
                "Implement monitoring and alerting",
                "Plan for disaster recovery",
                "Document architectural decisions",
                "Establish code review process"
            ],
            "quality_gates": [
                "Automated testing pipeline",
                "Security scanning",
                "Performance benchmarks",
                "Code quality metrics"
            ],
            "confidence": 0.9
        }


class SynthesizerAgent(SpecializedAgent):
    """Agent specialized in synthesizing results from multiple agents."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentMode.SYNTHESIZER)
    
    def _execute_specialized_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute synthesis tasks."""
        agent_results = task.context.get("agent_results", [])
        
        return {
            "type": "synthesis_results",
            "consolidated_findings": {
                "research_insights": self._extract_research_insights(agent_results),
                "architectural_decisions": self._extract_architectural_decisions(agent_results),
                "implementation_guidance": self._extract_implementation_guidance(agent_results),
                "quality_recommendations": self._extract_quality_recommendations(agent_results)
            },
            "integrated_plan": [
                "Research phase completed with high confidence",
                "Architecture design approved and documented",
                "Implementation roadmap established",
                "Quality gates and testing strategy defined"
            ],
            "success_probability": 0.87,
            "key_risks": [
                "Timeline constraints may impact quality",
                "Resource availability needs monitoring",
                "External dependencies require coordination"
            ],
            "next_steps": [
                "Begin implementation phase",
                "Set up monitoring and alerts",
                "Schedule regular progress reviews",
                "Prepare rollback procedures"
            ]
        }
    
    def _extract_research_insights(self, results: List[Dict]) -> List[str]:
        """Extract research insights from agent results."""
        insights = []
        for result in results:
            if result.get("mode") == AgentMode.RESEARCHER.value:
                data = result.get("data", {})
                insights.extend(data.get("findings", []))
                insights.extend(data.get("insights", []))
        return insights[:5]  # Top 5 insights
    
    def _extract_architectural_decisions(self, results: List[Dict]) -> List[str]:
        """Extract architectural decisions from agent results."""
        decisions = []
        for result in results:
            if result.get("mode") == AgentMode.ARCHITECT.value:
                data = result.get("data", {})
                arch = data.get("solution_architecture", {})
                decisions.extend(arch.get("patterns", []))
                decisions.extend(arch.get("technologies", []))
        return decisions
    
    def _extract_implementation_guidance(self, results: List[Dict]) -> List[str]:
        """Extract implementation guidance from agent results."""
        guidance = []
        for result in results:
            if result.get("mode") == AgentMode.CODE.value:
                data = result.get("data", {})
                guidance.extend(data.get("implementation_plan", []))
                guidance.extend(data.get("technical_decisions", []))
        return guidance
    
    def _extract_quality_recommendations(self, results: List[Dict]) -> List[str]:
        """Extract quality recommendations from agent results."""
        recommendations = []
        for result in results:
            if result.get("mode") == AgentMode.EXPERT_CONSULTANT.value:
                data = result.get("data", {})
                recommendations.extend(data.get("recommendations", []))
            elif result.get("mode") == AgentMode.DEBUG.value:
                data = result.get("data", {})
                recommendations.extend(data.get("recommended_fixes", []))
        return recommendations


@dataclass
class EnhancedTask:
    """Enhanced task with metadata and relationships."""
    id: str
    content: str
    status: str
    priority: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    complexity_score: int = 1
    required_skills: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    sub_tasks: List[Dict[str, Any]] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Plan:
    """Structured plan with validation and metadata."""
    id: str
    title: str
    description: str
    goals: List[str]
    challenges: List[str]
    implementation_steps: List[Dict[str, Any]]
    success_criteria: List[str]
    template_type: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved: bool = False
    version: int = 1
    thinking_level: str = ThinkingLevel.THINK.value
    estimated_duration: Optional[int] = None


class PlanningOrganization:
    """Planning and organization tools for Claude Code tools implementation."""
    
    def __init__(self, project_path: Optional[str] = None):
        """Initialize the planning and organization tool."""
        self.project_path = project_path or os.getcwd()
        self.state_file = os.path.join(self.project_path, '.claude_state.json')
        
        # Task and plan storage
        self._todos: List[Dict[str, Any]] = []
        self._plans: List[Plan] = []
        self._current_plan: Optional[Plan] = None
        self._plan_mode_active = False
        
        # Agent coordination
        self._active_agents: Dict[str, Dict[str, Any]] = {}
        self._custom_commands: Dict[str, Dict[str, Any]] = {}
        self._agent_pool: Dict[str, SpecializedAgent] = {}
        self._task_queue: List[AgentTask] = []
        self._completed_tasks: List[AgentTask] = []
        
        # Initialize agent pool
        self._initialize_agent_pool()
        
        # Thinking budget configuration
        self._thinking_budgets = {
            ThinkingLevel.THINK.value: 1000,
            ThinkingLevel.THINK_HARD.value: 2500,
            ThinkingLevel.THINK_HARDER.value: 5000,
            ThinkingLevel.ULTRATHINK.value: 10000
        }
        self._current_thinking_level = ThinkingLevel.THINK.value
        
        # Load persisted state
        self.load_state()
        
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
        Launch an independent agent orchestration for complex tasks.
        
        The orchestrator analyzes the task and delegates to specialized agents
        as needed, then synthesizes their results into a comprehensive response.
        
        Args:
            description: A short description of the task (3-5 words)
            prompt: The detailed task for the agent to perform
            
        Returns:
            Dictionary containing the orchestrated response and metadata
            
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
        
        # Execute multi-agent orchestration
        orchestration_result = self._orchestrate_task(description, prompt)
        
        return {
            "description": description,
            "prompt": prompt,
            "response": orchestration_result["synthesized_response"],
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "agent_id": orchestration_result["orchestrator_id"],
            "mode": "orchestrator",
            "agent_results": orchestration_result["agent_results"],
            "execution_time": orchestration_result["total_execution_time"],
            "agents_used": orchestration_result["agents_used"]
        }
    
    
    def create_plan_from_template(self, template_type: str, context: Dict[str, Any]) -> Plan:
        """
        Create a plan from a predefined template.
        
        Args:
            template_type: Type of template to use
            context: Context information for the plan
            
        Returns:
            Created Plan object
        """
        templates = {
            PlanTemplate.FEATURE_DEVELOPMENT.value: {
                "goals": [
                    "Implement the new feature as specified",
                    "Ensure code quality and maintainability",
                    "Add comprehensive tests",
                    "Update documentation"
                ],
                "challenges": [
                    "Integration with existing codebase",
                    "Maintaining backward compatibility",
                    "Performance considerations"
                ],
                "implementation_steps": [
                    {"step": 1, "description": "Analyze requirements and existing code"},
                    {"step": 2, "description": "Design solution architecture"},
                    {"step": 3, "description": "Implement core functionality"},
                    {"step": 4, "description": "Add unit and integration tests"},
                    {"step": 5, "description": "Update documentation"},
                    {"step": 6, "description": "Code review and refinement"}
                ],
                "success_criteria": [
                    "All tests pass",
                    "Code coverage meets standards",
                    "Performance benchmarks satisfied",
                    "Documentation complete"
                ]
            },
            PlanTemplate.REFACTORING.value: {
                "goals": [
                    "Improve code structure and readability",
                    "Maintain existing functionality",
                    "Enhance performance where possible"
                ],
                "challenges": [
                    "Preserving behavior during changes",
                    "Managing dependencies",
                    "Minimizing risk"
                ],
                "implementation_steps": [
                    {"step": 1, "description": "Analyze current implementation"},
                    {"step": 2, "description": "Identify refactoring opportunities"},
                    {"step": 3, "description": "Create comprehensive test suite"},
                    {"step": 4, "description": "Perform incremental refactoring"},
                    {"step": 5, "description": "Validate behavior preservation"}
                ],
                "success_criteria": [
                    "All existing tests still pass",
                    "Code complexity reduced",
                    "No functionality regression"
                ]
            },
            PlanTemplate.DEBUGGING.value: {
                "goals": [
                    "Identify root cause of issue",
                    "Implement permanent fix",
                    "Prevent future occurrences"
                ],
                "challenges": [
                    "Reproducing the issue",
                    "Understanding system interactions",
                    "Avoiding side effects"
                ],
                "implementation_steps": [
                    {"step": 1, "description": "Reproduce the issue"},
                    {"step": 2, "description": "Analyze logs and error traces"},
                    {"step": 3, "description": "Identify root cause"},
                    {"step": 4, "description": "Implement and test fix"},
                    {"step": 5, "description": "Add regression tests"}
                ],
                "success_criteria": [
                    "Issue no longer reproducible",
                    "All tests pass",
                    "No new issues introduced"
                ]
            },
            PlanTemplate.RESEARCH.value: {
                "goals": [
                    "Gather comprehensive information",
                    "Understand current state and options",
                    "Provide actionable insights"
                ],
                "challenges": [
                    "Information completeness",
                    "Source reliability",
                    "Analysis depth"
                ],
                "implementation_steps": [
                    {"step": 1, "description": "Define research scope and questions"},
                    {"step": 2, "description": "Gather information from multiple sources"},
                    {"step": 3, "description": "Analyze and synthesize findings"},
                    {"step": 4, "description": "Document key insights"},
                    {"step": 5, "description": "Provide recommendations"}
                ],
                "success_criteria": [
                    "All research questions answered",
                    "Sources documented",
                    "Clear recommendations provided"
                ]
            }
        }
        
        template = templates.get(template_type, templates[PlanTemplate.FEATURE_DEVELOPMENT.value])
        
        plan = Plan(
            id=self.generate_task_id(),
            title=context.get("title", "Development Plan"),
            description=context.get("description", ""),
            goals=template["goals"],
            challenges=template["challenges"],
            implementation_steps=template["implementation_steps"],
            success_criteria=template["success_criteria"],
            template_type=template_type,
            thinking_level=self._current_thinking_level
        )
        
        self._plans.append(plan)
        return plan
    
    def validate_plan(self, plan: Plan) -> Tuple[bool, List[str]]:
        """
        Validate a plan meets quality standards.
        
        Args:
            plan: Plan to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check minimum content requirements
        if len(plan.title.strip()) < 5:
            errors.append("Plan title must be at least 5 characters")
            
        if len(plan.description.strip()) < 20:
            errors.append("Plan description must be at least 20 characters")
            
        if len(plan.goals) < 1:
            errors.append("Plan must have at least one goal")
            
        if len(plan.implementation_steps) < 2:
            errors.append("Plan must have at least 2 implementation steps")
            
        if len(plan.success_criteria) < 1:
            errors.append("Plan must have at least one success criterion")
            
        # Validate implementation steps structure
        for i, step in enumerate(plan.implementation_steps):
            if "step" not in step or "description" not in step:
                errors.append(f"Implementation step {i+1} missing required fields")
                
        return (len(errors) == 0, errors)
    
    def interactive_planning_session(self, initial_prompt: str) -> Dict[str, Any]:
        """
        Conduct an interactive planning session with iterative refinement.
        
        Args:
            initial_prompt: Initial planning prompt
            
        Returns:
            Dictionary containing session results
        """
        # Create initial plan
        context = {
            "title": f"Plan for: {initial_prompt[:50]}",
            "description": initial_prompt
        }
        
        # Determine template type based on prompt
        prompt_lower = initial_prompt.lower()
        if "refactor" in prompt_lower:
            template_type = PlanTemplate.REFACTORING.value
        elif "debug" in prompt_lower or "fix" in prompt_lower:
            template_type = PlanTemplate.DEBUGGING.value
        elif "research" in prompt_lower or "analyze" in prompt_lower:
            template_type = PlanTemplate.RESEARCH.value
        else:
            template_type = PlanTemplate.FEATURE_DEVELOPMENT.value
            
        plan = self.create_plan_from_template(template_type, context)
        self._current_plan = plan
        self._plan_mode_active = True
        
        # Validate initial plan
        is_valid, errors = self.validate_plan(plan)
        
        return {
            "success": True,
            "plan_id": plan.id,
            "plan": asdict(plan),
            "is_valid": is_valid,
            "validation_errors": errors,
            "message": "Planning session initiated. Use refine_plan() to improve the plan."
        }
    
    def refine_plan(self, plan_id: str, refinements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine an existing plan based on feedback.
        
        Args:
            plan_id: ID of plan to refine
            refinements: Dictionary of refinements to apply
            
        Returns:
            Updated plan information
        """
        plan = next((p for p in self._plans if p.id == plan_id), None)
        if not plan:
            return {"success": False, "error": "Plan not found"}
            
        # Apply refinements
        if "goals" in refinements:
            plan.goals.extend(refinements["goals"])
            
        if "implementation_steps" in refinements:
            plan.implementation_steps.extend(refinements["implementation_steps"])
            
        if "success_criteria" in refinements:
            plan.success_criteria.extend(refinements["success_criteria"])
            
        if "thinking_level" in refinements:
            plan.thinking_level = refinements["thinking_level"]
            
        # Increment version
        plan.version += 1
        
        # Revalidate
        is_valid, errors = self.validate_plan(plan)
        
        return {
            "success": True,
            "plan": asdict(plan),
            "is_valid": is_valid,
            "validation_errors": errors,
            "version": plan.version
        }
    
    def set_thinking_budget(self, level: str) -> None:
        """
        Set the thinking budget level for tasks.
        
        Args:
            level: Thinking level to set
        """
        if level in [level_enum.value for level_enum in ThinkingLevel]:
            self._current_thinking_level = level
        else:
            raise ValueError(f"Invalid thinking level: {level}")
    
    def execute_development_workflow(self, project_description: str) -> Dict[str, Any]:
        """
        Execute the explore-plan-code-commit workflow pattern.
        
        Args:
            project_description: Description of the project/task
            
        Returns:
            Workflow execution results
        """
        workflow_id = self.generate_task_id()
        
        # Phase 1: Exploration
        exploration_task = EnhancedTask(
            id=self.generate_task_id(),
            content=f"Explore: {project_description}",
            status=TaskStatus.IN_PROGRESS.value,
            priority=TaskPriority.HIGH.value,
            required_skills=["research", "analysis"],
            context={"phase": "exploration", "workflow_id": workflow_id}
        )
        
        # Phase 2: Planning
        planning_result = self.interactive_planning_session(project_description)
        
        # Phase 3: Implementation
        implementation_tasks = []
        if planning_result["is_valid"] and self._current_plan:
            plan = self._current_plan
            for step in plan.implementation_steps:
                task = EnhancedTask(
                    id=self.generate_task_id(),
                    content=step["description"],
                    status=TaskStatus.PENDING.value,
                    priority=TaskPriority.HIGH.value,
                    dependencies=[exploration_task.id],
                    context={"phase": "implementation", "workflow_id": workflow_id}
                )
                implementation_tasks.append(task)
        
        # Phase 4: Review and Commit
        review_task = EnhancedTask(
            id=self.generate_task_id(),
            content="Review changes and prepare commit",
            status=TaskStatus.PENDING.value,
            priority=TaskPriority.HIGH.value,
            dependencies=[t.id for t in implementation_tasks],
            context={"phase": "review", "workflow_id": workflow_id}
        )
        
        return {
            "workflow_id": workflow_id,
            "phases": {
                "exploration": asdict(exploration_task),
                "planning": planning_result,
                "implementation": [asdict(t) for t in implementation_tasks],
                "review": asdict(review_task)
            },
            "status": "initiated"
        }
    
    def register_custom_command(self, name: str, command_template: str, description: str) -> Dict[str, Any]:
        """
        Register a custom command for repetitive tasks.
        
        Args:
            name: Command name
            command_template: Command template with placeholders
            description: Command description
            
        Returns:
            Registration result
        """
        if name in self._custom_commands:
            return {"success": False, "error": "Command already exists"}
            
        self._custom_commands[name] = {
            "template": command_template,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        self.save_state()
        
        return {
            "success": True,
            "command": name,
            "message": f"Custom command '{name}' registered successfully"
        }
    
    def execute_custom_command(self, command_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered custom command.
        
        Args:
            command_name: Name of command to execute
            context: Context for template substitution
            
        Returns:
            Execution result
        """
        if command_name not in self._custom_commands:
            return {"success": False, "error": "Command not found"}
            
        command = self._custom_commands[command_name]
        template = command["template"]
        
        # Simple template substitution
        for key, value in context.items():
            template = template.replace(f"{{{key}}}", str(value))
            
        return {
            "success": True,
            "command": command_name,
            "executed_template": template,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_state(self) -> None:
        """Persist todos, plans, and agent states to disk."""
        state = {
            "todos": self._todos,
            "plans": [asdict(p) for p in self._plans],
            "current_plan_id": self._current_plan.id if self._current_plan else None,
            "plan_mode_active": self._plan_mode_active,
            "active_agents": self._active_agents,
            "custom_commands": self._custom_commands,
            "thinking_level": self._current_thinking_level
        }
        
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            # In production, this would log the error
            pass
    
    def load_state(self) -> None:
        """Restore previous session state from disk."""
        if not os.path.exists(self.state_file):
            return
            
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                
            self._todos = state.get("todos", [])
            
            # Restore plans
            plan_dicts = state.get("plans", [])
            self._plans = []
            for plan_dict in plan_dicts:
                # Remove 'id' from dict to pass as argument
                plan_id = plan_dict.pop('id')
                plan = Plan(id=plan_id, **plan_dict)
                self._plans.append(plan)
                
            # Restore current plan
            current_plan_id = state.get("current_plan_id")
            if current_plan_id:
                self._current_plan = next((p for p in self._plans if p.id == current_plan_id), None)
                
            self._plan_mode_active = state.get("plan_mode_active", False)
            self._active_agents = state.get("active_agents", {})
            self._custom_commands = state.get("custom_commands", {})
            self._current_thinking_level = state.get("thinking_level", ThinkingLevel.THINK.value)
            
        except Exception as e:
            # In production, this would log the error
            pass
    
    def track_planning_metrics(self) -> Dict[str, Any]:
        """
        Track planning success rates, time estimates vs actuals,
        common failure points, and optimization opportunities.
        
        Returns:
            Dictionary of planning metrics
        """
        completed_tasks = [t for t in self._todos if t.get('status') == TaskStatus.COMPLETED.value]
        pending_tasks = [t for t in self._todos if t.get('status') == TaskStatus.PENDING.value]
        in_progress_tasks = [t for t in self._todos if t.get('status') == TaskStatus.IN_PROGRESS.value]
        
        # Calculate metrics
        total_tasks = len(self._todos)
        completion_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0
        
        # Plan metrics
        approved_plans = [p for p in self._plans if p.approved]
        plan_approval_rate = len(approved_plans) / len(self._plans) if self._plans else 0
        
        # Average plan iterations
        avg_plan_versions = sum(p.version for p in self._plans) / len(self._plans) if self._plans else 0
        
        return {
            "task_metrics": {
                "total": total_tasks,
                "completed": len(completed_tasks),
                "pending": len(pending_tasks),
                "in_progress": len(in_progress_tasks),
                "completion_rate": completion_rate
            },
            "plan_metrics": {
                "total_plans": len(self._plans),
                "approved_plans": len(approved_plans),
                "approval_rate": plan_approval_rate,
                "average_versions": avg_plan_versions
            },
            "custom_commands": len(self._custom_commands),
            "timestamp": datetime.now().isoformat()
        }
    
    def _initialize_agent_pool(self) -> None:
        """Initialize the pool of specialized agents."""
        self._agent_pool = {
            "researcher_01": ResearcherAgent("researcher_01"),
            "architect_01": ArchitectAgent("architect_01"),
            "code_01": CodeAgent("code_01"),
            "debug_01": DebugAgent("debug_01"),
            "expert_01": ExpertConsultantAgent("expert_01"),
            "synthesizer_01": SynthesizerAgent("synthesizer_01")
        }
    
    def _orchestrate_task(self, description: str, prompt: str) -> Dict[str, Any]:
        """
        Orchestrate task execution across multiple specialized agents.
        
        Args:
            description: Task description
            prompt: Detailed task prompt
            
        Returns:
            Dictionary with orchestration results
        """
        orchestrator_id = f"orchestrator_{hash(prompt) % 10000}"
        start_time = time.time()
        
        # Analyze task and determine required agents
        required_agents = self._analyze_task_requirements(prompt)
        
        # Create tasks for each required agent
        agent_tasks = []
        for agent_mode in required_agents:
            task = AgentTask(
                id=self.generate_task_id(),
                mode=agent_mode,
                prompt=prompt,
                context={"description": description, "orchestrator_id": orchestrator_id}
            )
            agent_tasks.append(task)
        
        # Execute tasks in parallel using ThreadPoolExecutor
        agent_results = self._execute_agent_tasks_parallel(agent_tasks)
        
        # Synthesize results
        synthesis_task = AgentTask(
            id=self.generate_task_id(),
            mode=AgentMode.SYNTHESIZER.value,
            prompt=f"Synthesize results for: {description}",
            context={
                "agent_results": [asdict(result) for result in agent_results],
                "original_prompt": prompt,
                "description": description
            }
        )
        
        synthesizer = self._agent_pool["synthesizer_01"]
        synthesis_result = synthesizer.execute_task(synthesis_task)
        
        total_execution_time = time.time() - start_time
        
        # Create comprehensive response
        synthesized_response = self._format_orchestrated_response(
            description, prompt, agent_results, synthesis_result
        )
        
        return {
            "orchestrator_id": orchestrator_id,
            "agent_results": [asdict(result) for result in agent_results],
            "synthesis_result": asdict(synthesis_result),
            "synthesized_response": synthesized_response,
            "total_execution_time": total_execution_time,
            "agents_used": required_agents
        }
    
    def _analyze_task_requirements(self, prompt: str) -> List[str]:
        """
        Analyze task prompt to determine which specialized agents are needed.
        
        Args:
            prompt: Task prompt to analyze
            
        Returns:
            List of agent modes required for the task
        """
        prompt_lower = prompt.lower()
        required_agents = []
        
        # Always start with research for understanding
        required_agents.append(AgentMode.RESEARCHER.value)
        
        # Determine specific agents based on task type
        if any(keyword in prompt_lower for keyword in ["implement", "create", "build", "develop"]):
            required_agents.extend([
                AgentMode.ARCHITECT.value,
                AgentMode.CODE.value,
                AgentMode.EXPERT_CONSULTANT.value
            ])
        elif any(keyword in prompt_lower for keyword in ["debug", "fix", "error", "issue", "problem"]):
            required_agents.extend([
                AgentMode.DEBUG.value,
                AgentMode.EXPERT_CONSULTANT.value
            ])
        elif any(keyword in prompt_lower for keyword in ["design", "architecture", "structure"]):
            required_agents.extend([
                AgentMode.ARCHITECT.value,
                AgentMode.EXPERT_CONSULTANT.value
            ])
        elif any(keyword in prompt_lower for keyword in ["analyze", "understand", "explain", "review"]):
            required_agents.append(AgentMode.EXPERT_CONSULTANT.value)
        else:
            # General tasks get expert consultation
            required_agents.append(AgentMode.EXPERT_CONSULTANT.value)
        
        return list(set(required_agents))  # Remove duplicates
    
    def _execute_agent_tasks_parallel(self, tasks: List[AgentTask]) -> List[AgentResult]:
        """
        Execute agent tasks in parallel using thread pool.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            List of agent results
        """
        results = []
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as executor:
            # Submit all tasks
            future_to_task = {}
            for task in tasks:
                agent_key = f"{task.mode}_01"
                if agent_key in self._agent_pool:
                    agent = self._agent_pool[agent_key]
                    future = executor.submit(agent.execute_task, task)
                    future_to_task[future] = task
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Create error result
                    task = future_to_task[future]
                    error_result = AgentResult(
                        agent_id=f"{task.mode}_01",
                        mode=task.mode,
                        task_id=task.id,
                        success=False,
                        data={"error": str(e)},
                        execution_time=0.0
                    )
                    results.append(error_result)
        
        return results
    
    def _format_orchestrated_response(self, description: str, prompt: str, 
                                    agent_results: List[AgentResult], 
                                    synthesis_result: AgentResult) -> str:
        """
        Format the final orchestrated response.
        
        Args:
            description: Task description
            prompt: Original prompt
            agent_results: Results from specialized agents
            synthesis_result: Result from synthesizer
            
        Returns:
            Formatted response string
        """
        response_parts = [
            f"[Orchestrator Mode] Multi-Agent Task Execution\\n",
            f"Task: {description}\\n",
            f"Prompt: {prompt}\\n\\n"
        ]
        
        # Add agent execution summary
        response_parts.append("Agent Execution Summary:\\n")
        for result in agent_results:
            status = "✓" if result.success else "✗"
            response_parts.append(
                f"{status} {result.mode.title()} Agent: {result.execution_time:.2f}s\\n"
            )
        
        # Add synthesis results
        if synthesis_result.success and synthesis_result.data:
            synthesis_data = synthesis_result.data
            
            response_parts.append("\\nConsolidated Findings:\\n")
            
            # Add integrated plan if available
            if "integrated_plan" in synthesis_data:
                response_parts.append("Integrated Plan:\\n")
                for item in synthesis_data["integrated_plan"]:
                    response_parts.append(f"• {item}\\n")
                response_parts.append("\\n")
            
            # Add key insights
            consolidated = synthesis_data.get("consolidated_findings", {})
            if consolidated:
                response_parts.append("Key Insights:\\n")
                for category, items in consolidated.items():
                    if items:
                        response_parts.append(f"{category.title().replace('_', ' ')}:\\n")
                        for item in items[:3]:  # Top 3 items per category
                            response_parts.append(f"  - {item}\\n")
                        response_parts.append("\\n")
            
            # Add success probability
            if "success_probability" in synthesis_data:
                prob = synthesis_data["success_probability"]
                response_parts.append(f"Success Probability: {prob:.1%}\\n\\n")
            
            # Add next steps
            if "next_steps" in synthesis_data:
                response_parts.append("Recommended Next Steps:\\n")
                for step in synthesis_data["next_steps"]:
                    response_parts.append(f"• {step}\\n")
        
        response_parts.append("\\nOrchestration completed successfully.")
        
        return "".join(response_parts)
    
