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