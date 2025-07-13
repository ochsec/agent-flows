import unittest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.planning_organization import (
    PlanningOrganization, TaskStatus, TaskPriority, ThinkingLevel,
    PlanTemplate, EnhancedTask, Plan
)


class TestPlanningOrganization(unittest.TestCase):
    """Test cases for PlanningOrganization class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.plan_org = PlanningOrganization(project_path=self.temp_dir)
        
    def tearDown(self):
        """Clean up after each test."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """Test proper initialization of PlanningOrganization."""
        self.assertEqual(self.plan_org.project_path, self.temp_dir)
        self.assertEqual(self.plan_org.state_file, os.path.join(self.temp_dir, '.claude_state.json'))
        self.assertEqual(self.plan_org._todos, [])
        self.assertEqual(self.plan_org._plans, [])
        self.assertIsNone(self.plan_org._current_plan)
        self.assertFalse(self.plan_org._plan_mode_active)
        
    def test_todo_write_basic(self):
        """Test basic todo writing functionality."""
        todos = [
            {
                "id": "1",
                "content": "Implement feature X",
                "status": "pending",
                "priority": "high"
            },
            {
                "id": "2",
                "content": "Write tests for feature X",
                "status": "pending",
                "priority": "medium"
            }
        ]
        
        result = self.plan_org.todo_write(todos)
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['todos']), 2)
        self.assertEqual(result['validation_errors'], [])
        
        # Check that timestamps were added
        for todo in result['todos']:
            self.assertIn('created_at', todo)
            
    def test_todo_write_status_management(self):
        """Test task status management."""
        todos = [
            {
                "id": "1",
                "content": "Task 1",
                "status": "pending",
                "priority": "high"
            },
            {
                "id": "2",
                "content": "Task 2",
                "status": "in_progress",
                "priority": "medium"
            },
            {
                "id": "3",
                "content": "Task 3",
                "status": "completed",
                "priority": "low"
            }
        ]
        
        result = self.plan_org.todo_write(todos)
        
        self.assertTrue(result['success'])
        
        # Check that completed tasks have completion timestamp
        completed_todos = [t for t in result['todos'] if t['status'] == 'completed']
        for todo in completed_todos:
            self.assertIn('completed_at', todo)
            
    def test_todo_write_only_one_in_progress(self):
        """Test that only one task can be in progress at a time."""
        todos = [
            {
                "id": "1",
                "content": "Task 1",
                "status": "in_progress",
                "priority": "high"
            },
            {
                "id": "2",
                "content": "Task 2",
                "status": "in_progress",
                "priority": "medium"
            }
        ]
        
        result = self.plan_org.todo_write(todos)
        
        self.assertFalse(result['success'])
        self.assertIn("Only one task can be in_progress at a time", result['validation_errors'][0])
        
    def test_todo_write_validation_missing_fields(self):
        """Test validation for missing required fields."""
        todos = [
            {
                "id": "1",
                "content": "Task without status",
                # Missing status
                "priority": "high"
            }
        ]
        
        result = self.plan_org.todo_write(todos)
        
        self.assertFalse(result['success'])
        self.assertTrue(any("Missing required field 'status'" in err for err in result['validation_errors']))
        
    def test_todo_write_validation_empty_content(self):
        """Test validation for empty content."""
        todos = [
            {
                "id": "1",
                "content": "",
                "status": "pending",
                "priority": "high"
            }
        ]
        
        result = self.plan_org.todo_write(todos)
        
        self.assertFalse(result['success'])
        self.assertTrue(any("Content must be a non-empty string" in err for err in result['validation_errors']))
        
    def test_todo_write_validation_invalid_status(self):
        """Test validation for invalid status values."""
        todos = [
            {
                "id": "1",
                "content": "Task with invalid status",
                "status": "invalid_status",
                "priority": "high"
            }
        ]
        
        result = self.plan_org.todo_write(todos)
        
        self.assertFalse(result['success'])
        self.assertTrue(any("Invalid status" in err for err in result['validation_errors']))
        
    def test_todo_write_validation_invalid_priority(self):
        """Test validation for invalid priority values."""
        todos = [
            {
                "id": "1",
                "content": "Task with invalid priority",
                "status": "pending",
                "priority": "urgent"  # Invalid priority
            }
        ]
        
        result = self.plan_org.todo_write(todos)
        
        self.assertFalse(result['success'])
        self.assertTrue(any("Invalid priority" in err for err in result['validation_errors']))
        
    def test_todo_write_not_list(self):
        """Test that todos must be a list."""
        with self.assertRaises(ValueError) as cm:
            self.plan_org.todo_write("not a list")
        self.assertIn("must be a list", str(cm.exception))
        
    def test_get_todos(self):
        """Test getting the current todo list."""
        # Initially empty
        todos = self.plan_org.get_todos()
        self.assertEqual(todos, [])
        
        # Add some todos
        new_todos = [
            {
                "id": "1",
                "content": "Test task",
                "status": "pending",
                "priority": "high"
            }
        ]
        self.plan_org.todo_write(new_todos)
        
        # Get todos again
        todos = self.plan_org.get_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]['content'], "Test task")
        
    def test_exit_plan_mode_basic(self):
        """Test basic exit plan mode functionality."""
        plan = "## Implementation Plan\n\n1. First implement X\n2. Then implement Y\n3. Finally test everything"
        
        result = self.plan_org.exit_plan_mode(plan)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['plan'], plan)
        self.assertIn('timestamp', result)
        self.assertIn("Waiting for user approval", result['message'])
        
    def test_exit_plan_mode_validation_empty(self):
        """Test exit plan mode with empty plan."""
        with self.assertRaises(ValueError) as cm:
            self.plan_org.exit_plan_mode("")
        self.assertIn("at least 10 characters", str(cm.exception))
        
    def test_exit_plan_mode_validation_too_short(self):
        """Test exit plan mode with too short plan."""
        with self.assertRaises(ValueError) as cm:
            self.plan_org.exit_plan_mode("short")
        self.assertIn("at least 10 characters", str(cm.exception))
        
    def test_plan_mode_state(self):
        """Test plan mode state management."""
        # Initially not in plan mode
        self.assertFalse(self.plan_org.is_plan_mode_active())
        
        # Enter plan mode
        self.plan_org.enter_plan_mode()
        self.assertTrue(self.plan_org.is_plan_mode_active())
        
        # Exit plan mode
        self.plan_org.exit_plan_mode("This is a valid plan for testing")
        self.assertFalse(self.plan_org.is_plan_mode_active())
        
    def test_generate_task_id(self):
        """Test task ID generation."""
        id1 = self.plan_org.generate_task_id()
        id2 = self.plan_org.generate_task_id()
        
        # IDs should be strings
        self.assertIsInstance(id1, str)
        self.assertIsInstance(id2, str)
        
        # IDs should be unique
        self.assertNotEqual(id1, id2)
        
        # IDs should have reasonable length
        self.assertEqual(len(id1), 8)
        self.assertEqual(len(id2), 8)
        
    def test_task_persistence(self):
        """Test that todos persist between calls."""
        # Add initial todos
        todos1 = [
            {
                "id": "1",
                "content": "First task",
                "status": "pending",
                "priority": "high"
            }
        ]
        self.plan_org.todo_write(todos1)
        
        # Add more todos (replacing the list)
        todos2 = [
            {
                "id": "1",
                "content": "First task",
                "status": "completed",
                "priority": "high"
            },
            {
                "id": "2",
                "content": "Second task",
                "status": "pending",
                "priority": "medium"
            }
        ]
        result = self.plan_org.todo_write(todos2)
        
        # Should have both todos
        self.assertEqual(len(result['todos']), 2)
        
        # First task should be marked as completed
        first_task = next(t for t in result['todos'] if t['id'] == '1')
        self.assertEqual(first_task['status'], 'completed')
        
    def test_todo_write_preserves_existing_timestamps(self):
        """Test that existing timestamps are preserved."""
        # Create a todo with a specific timestamp
        original_timestamp = "2024-01-01T12:00:00"
        todos = [
            {
                "id": "1",
                "content": "Task with timestamp",
                "status": "pending",
                "priority": "high",
                "created_at": original_timestamp
            }
        ]
        
        result = self.plan_org.todo_write(todos)
        
        # Timestamp should be preserved
        self.assertEqual(result['todos'][0]['created_at'], original_timestamp)
        
    def test_enum_values(self):
        """Test that enum values are correctly defined."""
        # Test TaskStatus enum
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        
        # Test TaskPriority enum
        self.assertEqual(TaskPriority.HIGH.value, "high")
        self.assertEqual(TaskPriority.MEDIUM.value, "medium")
        self.assertEqual(TaskPriority.LOW.value, "low")
        
        # Test ThinkingLevel enum
        self.assertEqual(ThinkingLevel.THINK.value, "think")
        self.assertEqual(ThinkingLevel.THINK_HARD.value, "think_hard")
        self.assertEqual(ThinkingLevel.THINK_HARDER.value, "think_harder")
        self.assertEqual(ThinkingLevel.ULTRATHINK.value, "ultrathink")
        
        # Test PlanTemplate enum
        self.assertEqual(PlanTemplate.FEATURE_DEVELOPMENT.value, "feature_development")
        self.assertEqual(PlanTemplate.REFACTORING.value, "refactoring")
        self.assertEqual(PlanTemplate.DEBUGGING.value, "debugging")
        self.assertEqual(PlanTemplate.RESEARCH.value, "research")
        
    def test_task_basic_execution(self):
        """Test basic task execution."""
        result = self.plan_org.task("search files", "Find all Python files in the project")
        
        self.assertIn('description', result)
        self.assertIn('prompt', result)
        self.assertIn('response', result)
        self.assertIn('timestamp', result)
        self.assertIn('status', result)
        self.assertIn('agent_id', result)
        self.assertIn('mode', result)
        
        self.assertEqual(result['description'], "search files")
        self.assertEqual(result['status'], "completed")
        self.assertEqual(result['mode'], "orchestrator")
        self.assertIn("Orchestrator Mode", result['response'])
        
    def test_task_validation_short_description(self):
        """Test task validation with short description."""
        with self.assertRaises(ValueError) as cm:
            self.plan_org.task("hi", "Long prompt here with enough characters")
        self.assertIn("at least 3 characters", str(cm.exception))
        
    def test_task_validation_short_prompt(self):
        """Test task validation with short prompt."""
        with self.assertRaises(ValueError) as cm:
            self.plan_org.task("valid desc", "short")
        self.assertIn("at least 10 characters", str(cm.exception))
        
    def test_task_search_simulation(self):
        """Test task simulation for search tasks."""
        result = self.plan_org.task("find config", "Find configuration files in the project")
        
        response = result['response']
        self.assertIn("Orchestrator Mode", response)
        self.assertIn("Researcher mode", response)
        self.assertIn("simulated response", response)
        
    def test_task_implementation_simulation(self):
        """Test task simulation for implementation tasks."""
        result = self.plan_org.task("implement feature", "Create a new authentication system")
        
        response = result['response']
        self.assertIn("Orchestrator Mode", response)
        self.assertIn("Architect Mode", response)
        self.assertIn("simulated response", response)
        
    def test_task_analysis_simulation(self):
        """Test task simulation for analysis tasks."""
        result = self.plan_org.task("analyze code", "Analyze the current database schema")
        
        response = result['response']
        self.assertIn("Orchestrator Mode", response)
        self.assertIn("Expert Consultant Mode", response)
        self.assertIn("simulated response", response)
        
    def test_task_general_simulation(self):
        """Test task simulation for general tasks."""
        result = self.plan_org.task("help debug", "Debug the failing test cases")
        
        response = result['response']
        self.assertIn("Orchestrator Mode", response)
        self.assertIn("simulated response", response)
        
    def test_task_agent_id_generation(self):
        """Test that agent IDs are generated consistently."""
        result1 = self.plan_org.task("test", "Same prompt here")
        result2 = self.plan_org.task("test", "Same prompt here")
        
        # Same prompt should generate same agent ID
        self.assertEqual(result1['agent_id'], result2['agent_id'])
        
        result3 = self.plan_org.task("test", "Different prompt here")
        
        # Different prompt should generate different agent ID
        self.assertNotEqual(result1['agent_id'], result3['agent_id'])
        
    def test_create_plan_from_template(self):
        """Test plan creation from templates."""
        context = {
            "title": "Test Feature",
            "description": "Implement a new test feature for the application"
        }
        
        plan = self.plan_org.create_plan_from_template(
            PlanTemplate.FEATURE_DEVELOPMENT.value,
            context
        )
        
        self.assertIsInstance(plan, Plan)
        self.assertEqual(plan.title, "Test Feature")
        self.assertEqual(plan.template_type, PlanTemplate.FEATURE_DEVELOPMENT.value)
        self.assertGreater(len(plan.goals), 0)
        self.assertGreater(len(plan.implementation_steps), 0)
        self.assertIn(plan, self.plan_org._plans)
        
    def test_validate_plan(self):
        """Test plan validation."""
        # Valid plan
        valid_plan = Plan(
            id="plan1",
            title="Valid Plan",
            description="This is a valid plan description that is long enough",
            goals=["Goal 1", "Goal 2"],
            challenges=["Challenge 1"],
            implementation_steps=[
                {"step": 1, "description": "Step 1"},
                {"step": 2, "description": "Step 2"}
            ],
            success_criteria=["Success criterion 1"]
        )
        
        is_valid, errors = self.plan_org.validate_plan(valid_plan)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid plan - short title
        invalid_plan = Plan(
            id="plan2",
            title="Bad",  # Too short
            description="Short description too",  # Too short
            goals=[],  # Empty
            challenges=[],
            implementation_steps=[],  # Empty
            success_criteria=[]  # Empty
        )
        
        is_valid, errors = self.plan_org.validate_plan(invalid_plan)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("title must be at least 5 characters" in err for err in errors))
        
    def test_interactive_planning_session(self):
        """Test interactive planning session."""
        result = self.plan_org.interactive_planning_session(
            "Implement a new feature for user authentication with OAuth support"
        )
        
        self.assertTrue(result["success"])
        self.assertIn("plan_id", result)
        self.assertIn("plan", result)
        self.assertIn("is_valid", result)
        self.assertIn("validation_errors", result)
        self.assertTrue(self.plan_org._plan_mode_active)
        self.assertIsNotNone(self.plan_org._current_plan)
        
    def test_refine_plan(self):
        """Test plan refinement."""
        # Create initial plan
        session_result = self.plan_org.interactive_planning_session(
            "Refactor the authentication module for better performance"
        )
        plan_id = session_result["plan_id"]
        
        # Refine the plan
        refinements = {
            "goals": ["Additional goal: Improve security"],
            "implementation_steps": [
                {"step": 7, "description": "Add security audit"}
            ],
            "thinking_level": ThinkingLevel.THINK_HARD.value
        }
        
        result = self.plan_org.refine_plan(plan_id, refinements)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["version"], 2)
        self.assertTrue(any("Improve security" in goal for goal in result["plan"]["goals"]))
        self.assertEqual(result["plan"]["thinking_level"], ThinkingLevel.THINK_HARD.value)
        
    def test_set_thinking_budget(self):
        """Test setting thinking budget levels."""
        # Valid level
        self.plan_org.set_thinking_budget(ThinkingLevel.ULTRATHINK.value)
        self.assertEqual(self.plan_org._current_thinking_level, ThinkingLevel.ULTRATHINK.value)
        
        # Invalid level
        with self.assertRaises(ValueError):
            self.plan_org.set_thinking_budget("invalid_level")
            
    def test_execute_development_workflow(self):
        """Test development workflow execution."""
        result = self.plan_org.execute_development_workflow(
            "Build a REST API for user management with CRUD operations"
        )
        
        self.assertIn("workflow_id", result)
        self.assertIn("phases", result)
        self.assertIn("exploration", result["phases"])
        self.assertIn("planning", result["phases"])
        self.assertIn("implementation", result["phases"])
        self.assertIn("review", result["phases"])
        self.assertEqual(result["status"], "initiated")
        
        # Check exploration phase
        exploration = result["phases"]["exploration"]
        self.assertEqual(exploration["status"], TaskStatus.IN_PROGRESS.value)
        self.assertIn("research", exploration["required_skills"])
        
    def test_custom_command_registration(self):
        """Test custom command registration and execution."""
        # Register command
        reg_result = self.plan_org.register_custom_command(
            "format_code",
            "black {file_path} --line-length {line_length}",
            "Format Python code with Black"
        )
        
        self.assertTrue(reg_result["success"])
        self.assertEqual(reg_result["command"], "format_code")
        
        # Execute command
        exec_result = self.plan_org.execute_custom_command(
            "format_code",
            {"file_path": "test.py", "line_length": "88"}
        )
        
        self.assertTrue(exec_result["success"])
        self.assertEqual(
            exec_result["executed_template"],
            "black test.py --line-length 88"
        )
        
        # Try to register duplicate
        dup_result = self.plan_org.register_custom_command(
            "format_code",
            "duplicate",
            "duplicate"
        )
        
        self.assertFalse(dup_result["success"])
        self.assertIn("already exists", dup_result["error"])
        
    def test_state_persistence(self):
        """Test saving and loading state."""
        # Create some state
        todos = [
            {
                "id": "task1",
                "content": "Persistent task",
                "status": TaskStatus.COMPLETED.value,
                "priority": TaskPriority.MEDIUM.value
            }
        ]
        self.plan_org.todo_write(todos)
        
        # Create a plan
        self.plan_org.interactive_planning_session("Test persistence")
        
        # Register a custom command
        self.plan_org.register_custom_command(
            "test_cmd",
            "echo {message}",
            "Test command"
        )
        
        # Save state
        self.plan_org.save_state()
        
        # Create new instance and verify state loaded
        new_planner = PlanningOrganization(project_path=self.temp_dir)
        
        self.assertEqual(len(new_planner._todos), 1)
        self.assertEqual(new_planner._todos[0]["content"], "Persistent task")
        self.assertEqual(len(new_planner._plans), 1)
        self.assertIn("test_cmd", new_planner._custom_commands)
        
    def test_track_planning_metrics(self):
        """Test planning metrics tracking."""
        # Create some tasks and plans
        todos = [
            {
                "id": "1",
                "content": "Task 1",
                "status": TaskStatus.COMPLETED.value,
                "priority": TaskPriority.HIGH.value
            },
            {
                "id": "2",
                "content": "Task 2",
                "status": TaskStatus.PENDING.value,
                "priority": TaskPriority.MEDIUM.value
            },
            {
                "id": "3",
                "content": "Task 3",
                "status": TaskStatus.IN_PROGRESS.value,
                "priority": TaskPriority.LOW.value
            }
        ]
        self.plan_org.todo_write(todos)
        
        # Create a plan
        self.plan_org.interactive_planning_session("Test metrics")
        
        # Get metrics
        metrics = self.plan_org.track_planning_metrics()
        
        self.assertIn("task_metrics", metrics)
        self.assertEqual(metrics["task_metrics"]["total"], 3)
        self.assertEqual(metrics["task_metrics"]["completed"], 1)
        self.assertEqual(metrics["task_metrics"]["pending"], 1)
        self.assertEqual(metrics["task_metrics"]["in_progress"], 1)
        self.assertEqual(metrics["task_metrics"]["completion_rate"], 1/3)
        
        self.assertIn("plan_metrics", metrics)
        self.assertEqual(metrics["plan_metrics"]["total_plans"], 1)
        self.assertEqual(metrics["plan_metrics"]["approved_plans"], 0)
        
    def test_enhanced_task_dataclass(self):
        """Test EnhancedTask dataclass functionality."""
        task = EnhancedTask(
            id="test1",
            content="Test enhanced task",
            status=TaskStatus.PENDING.value,
            priority=TaskPriority.HIGH.value,
            estimated_duration=120,
            required_skills=["python", "testing"],
            dependencies=["task0"]
        )
        
        self.assertEqual(task.id, "test1")
        self.assertEqual(task.content, "Test enhanced task")
        self.assertEqual(task.complexity_score, 1)
        self.assertIsNone(task.completed_at)
        self.assertIn("python", task.required_skills)
        self.assertIn("task0", task.dependencies)
        
    def test_plan_dataclass(self):
        """Test Plan dataclass functionality."""
        plan = Plan(
            id="plan1",
            title="Test Plan",
            description="This is a test plan description",
            goals=["Goal 1", "Goal 2"],
            challenges=["Challenge 1"],
            implementation_steps=[{"step": 1, "description": "Step 1"}],
            success_criteria=["Criterion 1"],
            thinking_level=ThinkingLevel.THINK_HARD.value
        )
        
        self.assertEqual(plan.id, "plan1")
        self.assertEqual(plan.title, "Test Plan")
        self.assertFalse(plan.approved)
        self.assertEqual(plan.version, 1)
        self.assertEqual(plan.thinking_level, ThinkingLevel.THINK_HARD.value)


if __name__ == '__main__':
    unittest.main()