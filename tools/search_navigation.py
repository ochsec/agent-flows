import os
import glob
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime


class SearchNavigation:
    """Search and navigation tools for Claude Code tools implementation."""
    
    def glob(self, pattern: str, path: Optional[str] = None) -> List[str]:
        """
        Find files by pattern matching, sorted by modification time.
        
        Args:
            pattern: The glob pattern to match files against
            path: The directory to search in (defaults to current working directory)
            
        Returns:
            List of matching file paths sorted by modification time (newest first)
            
        Raises:
            ValueError: If the path doesn't exist
        """
        # Use current working directory if path not specified
        if path is None:
            search_path = os.getcwd()
        else:
            search_path = path
            
        # Validate path exists
        if not os.path.exists(search_path):
            raise ValueError(f"Path does not exist: {search_path}")
            
        # Build the full pattern
        if os.path.isabs(pattern):
            full_pattern = pattern
        else:
            full_pattern = os.path.join(search_path, pattern)
            
        # Find matching files
        matches = glob.glob(full_pattern, recursive=True)
        
        # Filter out directories (only return files)
        files = [f for f in matches if os.path.isfile(f)]
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        return files
    
    def grep(self, pattern: str, include: Optional[str] = None, path: Optional[str] = None) -> List[str]:
        """
        Search file contents using regular expressions.
        
        Args:
            pattern: The regular expression pattern to search for
            include: Optional file pattern to include (e.g., "*.py", "*.{js,ts}")
            path: The directory to search in (defaults to current working directory)
            
        Returns:
            List of file paths that contain at least one match, sorted by modification time (newest first)
            
        Raises:
            ValueError: If the path doesn't exist or pattern is invalid
            re.error: If the regex pattern is invalid
        """
        # Validate regex pattern
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise re.error(f"Invalid regex pattern: {e}")
            
        # Use current working directory if path not specified
        if path is None:
            search_path = os.getcwd()
        else:
            search_path = path
            
        # Validate path exists
        if not os.path.exists(search_path):
            raise ValueError(f"Path does not exist: {search_path}")
            
        matching_files = []
        
        # Determine which files to search
        if include:
            # Use glob to find files matching the include pattern
            files_to_search = self.glob(include, search_path)
        else:
            # Search all files recursively
            files_to_search = []
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        files_to_search.append(file_path)
        
        # Search each file for the pattern
        for file_path in files_to_search:
            try:
                # Skip binary files by attempting to read as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Check if pattern matches
                if compiled_pattern.search(content):
                    matching_files.append(file_path)
                    
            except (UnicodeDecodeError, PermissionError, OSError):
                # Skip files that can't be read
                continue
        
        # Sort by modification time (newest first)
        matching_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        return matching_files
    
    def task(self, description: str, prompt: str) -> Dict[str, Any]:
        """
        Launch an independent agent for complex searches and research tasks.
        
        This is a simulated implementation for the prototype. In a real implementation,
        this would launch an actual agent with access to all Claude Code tools.
        
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
        # 1. Launch a new agent instance
        # 2. Provide it with the full toolset
        # 3. Execute the task autonomously
        # 4. Return the agent's findings
        
        # For now, simulate some basic research based on the prompt
        simulated_response = self._simulate_agent_task(prompt)
        
        return {
            "description": description,
            "prompt": prompt,
            "response": simulated_response,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "agent_id": f"agent_{hash(prompt) % 10000}"
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
            return f"Agent Search Results:\\n\\nBased on the task '{prompt}', I searched through the codebase and found several relevant files and patterns. The analysis included file system traversal, content analysis, and pattern matching.\\n\\nKey findings:\\n- Located relevant files in the project structure\\n- Identified patterns and implementations\\n- Analyzed code relationships and dependencies\\n\\nNote: This is a simulated response for prototype purposes."
            
        elif any(keyword in prompt_lower for keyword in ["implement", "create", "build"]):
            return f"Agent Implementation Analysis:\\n\\nFor the task '{prompt}', I analyzed the requirements and current codebase structure.\\n\\nRecommendations:\\n- Identified optimal implementation approach\\n- Located relevant existing patterns to follow\\n- Analyzed dependencies and requirements\\n- Prepared implementation strategy\\n\\nNote: This is a simulated response for prototype purposes."
            
        elif any(keyword in prompt_lower for keyword in ["analyze", "understand", "explain"]):
            return f"Agent Analysis Report:\\n\\nRegarding '{prompt}', I performed a comprehensive analysis of the codebase.\\n\\nFindings:\\n- Examined code structure and patterns\\n- Analyzed functionality and relationships\\n- Identified key components and their interactions\\n- Documented current implementation details\\n\\nNote: This is a simulated response for prototype purposes."
            
        else:
            return f"Agent Task Results:\\n\\nCompleted task: '{prompt}'\\n\\nThe agent executed the requested task using available tools including file operations, search capabilities, and analysis functions. The task was completed successfully with comprehensive results.\\n\\nNote: This is a simulated response for prototype purposes."