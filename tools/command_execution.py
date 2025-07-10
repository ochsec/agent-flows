import subprocess
import threading
import time
import os
import signal
from typing import Optional, Tuple, Dict, Any


class CommandExecution:
    """Command execution tool class for Claude Code tools implementation."""
    
    # Default and maximum timeout values in milliseconds
    DEFAULT_TIMEOUT_MS = 120000  # 2 minutes
    MAX_TIMEOUT_MS = 600000  # 10 minutes
    MAX_OUTPUT_LENGTH = 30000  # Maximum output length in characters
    
    def __init__(self):
        """Initialize the command execution tool."""
        self._shell_process: Optional[subprocess.Popen] = None
        self._shell_lock = threading.Lock()
        
    def bash(self, command: str, description: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a bash command in a persistent shell session.
        
        Args:
            command: The command to execute
            description: Optional description of what the command does (5-10 words)
            timeout: Optional timeout in milliseconds (max 600000ms/10 minutes)
            
        Returns:
            Dictionary containing:
                - stdout: Standard output from the command
                - stderr: Standard error from the command
                - return_code: Exit code of the command
                - truncated: Boolean indicating if output was truncated
                
        Raises:
            ValueError: If timeout exceeds maximum allowed
            TimeoutError: If command execution times out
        """
        # Validate timeout
        if timeout is not None:
            if timeout > self.MAX_TIMEOUT_MS:
                raise ValueError(f"Timeout cannot exceed {self.MAX_TIMEOUT_MS}ms (10 minutes)")
            if timeout <= 0:
                raise ValueError("Timeout must be positive")
        else:
            timeout = self.DEFAULT_TIMEOUT_MS
            
        # Convert timeout to seconds
        timeout_seconds = timeout / 1000.0
        
        # Execute command
        stdout, stderr, return_code = self._execute_command(command, timeout_seconds)
        
        # Truncate output if necessary
        truncated = False
        if len(stdout) > self.MAX_OUTPUT_LENGTH:
            stdout = stdout[:self.MAX_OUTPUT_LENGTH] + "\n... (output truncated)"
            truncated = True
            
        if len(stderr) > self.MAX_OUTPUT_LENGTH:
            stderr = stderr[:self.MAX_OUTPUT_LENGTH] + "\n... (output truncated)"
            truncated = True
            
        return {
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
            "truncated": truncated
        }
        
    def _execute_command(self, command: str, timeout_seconds: float) -> Tuple[str, str, int]:
        """
        Execute a command with timeout support.
        
        Args:
            command: The command to execute
            timeout_seconds: Timeout in seconds
            
        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        try:
            # Start the process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                # Use a new process group so we can kill all child processes
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                # Kill the entire process group
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                    
                # Give it a moment to terminate gracefully
                try:
                    stdout, stderr = process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    # Force kill if it didn't terminate
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    else:
                        process.kill()
                    stdout, stderr = process.communicate()
                    
                raise TimeoutError(f"Command timed out after {timeout_seconds} seconds")
                
            return stdout, stderr, return_code
            
        except TimeoutError:
            # Re-raise timeout errors so caller can handle them
            raise
        except Exception as e:
            # Return error information for other exceptions
            return "", str(e), -1
            
    def __del__(self):
        """Cleanup any running shell process."""
        if self._shell_process and self._shell_process.poll() is None:
            self._shell_process.terminate()
            try:
                self._shell_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._shell_process.kill()