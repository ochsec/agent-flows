import unittest
from datetime import datetime
from tools.planning_organization import PlanningOrganization, TaskStatus, TaskPriority


class TestPlanningOrganization(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.plan_org = PlanningOrganization()
        
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


if __name__ == '__main__':
    unittest.main()