import unittest
import time
import sys
from tools.command_execution import CommandExecution


class TestCommandExecution(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.cmd_exec = CommandExecution()
        
    def test_bash_simple_command(self):
        """Test basic command execution."""
        result = self.cmd_exec.bash("echo 'Hello World'")
        
        self.assertEqual(result['stdout'].strip(), "Hello World")
        self.assertEqual(result['stderr'], "")
        self.assertEqual(result['return_code'], 0)
        self.assertFalse(result['truncated'])
        
    def test_bash_with_stderr(self):
        """Test command that produces stderr."""
        result = self.cmd_exec.bash("echo 'Error message' >&2")
        
        self.assertEqual(result['stdout'], "")
        self.assertEqual(result['stderr'].strip(), "Error message")
        self.assertEqual(result['return_code'], 0)
        
    def test_bash_with_error_code(self):
        """Test command that returns non-zero exit code."""
        result = self.cmd_exec.bash("exit 42")
        
        self.assertEqual(result['return_code'], 42)
        
    def test_bash_timeout(self):
        """Test command timeout."""
        # Use a short timeout for testing
        with self.assertRaises(TimeoutError):
            # Sleep for longer than timeout
            self.cmd_exec.bash("sleep 5", timeout=1000)  # 1 second timeout
            
    def test_bash_timeout_validation(self):
        """Test timeout validation."""
        # Test max timeout
        with self.assertRaises(ValueError) as cm:
            self.cmd_exec.bash("echo test", timeout=700000)
        self.assertIn("cannot exceed", str(cm.exception))
        
        # Test negative timeout
        with self.assertRaises(ValueError) as cm:
            self.cmd_exec.bash("echo test", timeout=-1)
        self.assertIn("must be positive", str(cm.exception))
        
    def test_bash_output_truncation(self):
        """Test that large outputs are truncated."""
        # Generate output larger than MAX_OUTPUT_LENGTH
        large_output_cmd = f"python3 -c \"print('x' * 40000)\""
        result = self.cmd_exec.bash(large_output_cmd)
        
        self.assertTrue(result['truncated'])
        self.assertLessEqual(len(result['stdout']), 30100)  # Allow for truncation message
        self.assertIn("truncated", result['stdout'])
        
    def test_bash_multiline_output(self):
        """Test command with multiline output."""
        result = self.cmd_exec.bash("printf 'Line 1\\nLine 2\\nLine 3'")
        
        lines = result['stdout'].strip().split('\n')
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], "Line 1")
        self.assertEqual(lines[1], "Line 2")
        self.assertEqual(lines[2], "Line 3")
        
    def test_bash_environment_variables(self):
        """Test that environment variables work."""
        result = self.cmd_exec.bash("TEST_VAR='test123' && echo $TEST_VAR")
        
        self.assertEqual(result['stdout'].strip(), "test123")
        
    def test_bash_working_directory(self):
        """Test working directory commands."""
        result = self.cmd_exec.bash("pwd")
        
        self.assertNotEqual(result['stdout'].strip(), "")
        self.assertEqual(result['return_code'], 0)
        
    def test_bash_pipe_commands(self):
        """Test piped commands."""
        result = self.cmd_exec.bash("echo 'hello world' | wc -w")
        
        self.assertEqual(result['stdout'].strip(), "2")
        self.assertEqual(result['return_code'], 0)
        
    def test_bash_command_chaining(self):
        """Test command chaining with && and ||."""
        # Test successful chaining
        result = self.cmd_exec.bash("echo 'first' && echo 'second'")
        self.assertIn("first", result['stdout'])
        self.assertIn("second", result['stdout'])
        
        # Test failed chaining
        result = self.cmd_exec.bash("false || echo 'fallback'")
        self.assertEqual(result['stdout'].strip(), "fallback")
        
    def test_bash_quoted_arguments(self):
        """Test handling of quoted arguments."""
        result = self.cmd_exec.bash('echo "Hello World" "Test 123"')
        
        self.assertEqual(result['stdout'].strip(), "Hello World Test 123")
        
    def test_bash_special_characters(self):
        """Test handling of special characters."""
        result = self.cmd_exec.bash("echo '$HOME' '$(pwd)' '`date`'")
        
        # Should not expand variables/commands in single quotes
        self.assertIn("$HOME", result['stdout'])
        self.assertIn("$(pwd)", result['stdout'])
        
    def test_bash_with_description(self):
        """Test command with description parameter."""
        # Description is optional and doesn't affect execution
        result = self.cmd_exec.bash("echo test", description="Simple echo command")
        
        self.assertEqual(result['stdout'].strip(), "test")
        
    def test_bash_unicode_handling(self):
        """Test handling of unicode characters."""
        result = self.cmd_exec.bash("echo '你好世界 🌍'")
        
        self.assertIn("你好世界", result['stdout'])
        self.assertIn("🌍", result['stdout'])


if __name__ == '__main__':
    unittest.main()