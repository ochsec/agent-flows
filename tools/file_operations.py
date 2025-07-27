import os
import glob
import fnmatch
from typing import Optional, List, Dict, Any


class FileOperations:
    """File operations tool class for Claude Code tools implementation."""
    
    def write(self, file_path: str, content: str) -> None:
        """
        Write content to a file.
        
        Args:
            file_path: The absolute path to the file to write
            content: The content to write to the file
            
        Raises:
            ValueError: If path is not absolute
        """
        if not os.path.isabs(file_path):
            raise ValueError("file_path must be absolute")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def read(self, file_path: str, offset: Optional[int] = None, limit: Optional[int] = None) -> str:
        """
        Read file contents.
        
        Args:
            file_path: The absolute path to the file to read
            offset: The line number to start reading from (1-indexed)
            limit: The number of lines to read
            
        Returns:
            File contents with line numbers in cat -n format
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If path is not absolute
        """
        if not os.path.isabs(file_path):
            raise ValueError("file_path must be absolute")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Apply offset and limit
        start_line = (offset - 1) if offset else 0
        end_line = start_line + limit if limit else len(lines)
        
        # Default limit of 2000 lines if not specified
        if not limit and not offset:
            end_line = min(2000, len(lines))
            
        result_lines = []
        for i in range(start_line, min(end_line, len(lines))):
            line_num = i + 1
            line_content = lines[i].rstrip('\n')
            
            # Truncate lines longer than 2000 characters
            if len(line_content) > 2000:
                line_content = line_content[:2000] + "..."
                
            # Format with line numbers in cat -n style
            result_lines.append(f"{line_num:>6}\t{line_content}")
            
        return '\n'.join(result_lines)
    
    def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> None:
        """
        Perform exact string replacements in files.
        
        Args:
            file_path: The absolute path to the file to modify
            old_string: The text to replace (must match exactly)
            new_string: The text to replace it with
            replace_all: Replace all occurrences (default: False)
            
        Raises:
            ValueError: If path is not absolute, strings are identical, or old_string not found
            FileNotFoundError: If the file doesn't exist
        """
        if not os.path.isabs(file_path):
            raise ValueError("file_path must be absolute")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if old_string == new_string:
            raise ValueError("old_string and new_string must be different")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if old_string not in content:
            raise ValueError(f"old_string not found in file: {file_path}")
            
        if not replace_all:
            # Check if old_string is unique
            occurrences = content.count(old_string)
            if occurrences > 1:
                raise ValueError(f"old_string appears {occurrences} times. Use replace_all=True or provide more context to make it unique")
                
        # Perform replacement
        if replace_all:
            new_content = content.replace(old_string, new_string)
        else:
            new_content = content.replace(old_string, new_string, 1)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    def multi_edit(self, file_path: str, edits: List[Dict[str, Any]]) -> None:
        """
        Make multiple edits to a single file in one operation.
        
        Args:
            file_path: The absolute path to the file to modify
            edits: List of edit operations, each containing:
                - old_string: The text to replace
                - new_string: The text to replace it with
                - replace_all: Optional, replace all occurrences (default: False)
                
        Raises:
            ValueError: If path is not absolute, no edits provided, or edit validation fails
            FileNotFoundError: If the file doesn't exist
        """
        if not os.path.isabs(file_path):
            raise ValueError("file_path must be absolute")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not edits:
            raise ValueError("At least one edit must be provided")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Apply edits sequentially
        for i, edit in enumerate(edits):
            if 'old_string' not in edit or 'new_string' not in edit:
                raise ValueError(f"Edit {i+1}: Must contain 'old_string' and 'new_string'")
                
            old_string = edit['old_string']
            new_string = edit['new_string']
            replace_all = edit.get('replace_all', False)
            
            if old_string == new_string:
                raise ValueError(f"Edit {i+1}: old_string and new_string must be different")
                
            if old_string not in content:
                raise ValueError(f"Edit {i+1}: old_string not found in current content")
                
            if not replace_all:
                occurrences = content.count(old_string)
                if occurrences > 1:
                    raise ValueError(f"Edit {i+1}: old_string appears {occurrences} times. Use replace_all=True or provide more context")
                    
            # Apply the edit
            if replace_all:
                content = content.replace(old_string, new_string)
            else:
                content = content.replace(old_string, new_string, 1)
                
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def write(self, file_path: str, content: str) -> None:
        """
        Write a file to the filesystem.
        
        Args:
            file_path: The absolute path to the file to write
            content: The content to write to the file
            
        Raises:
            ValueError: If path is not absolute
        """
        if not os.path.isabs(file_path):
            raise ValueError("file_path must be absolute")
            
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def ls(self, path: str, ignore: Optional[List[str]] = None) -> List[str]:
        """
        List files and directories in a given path.
        
        Args:
            path: The absolute path to the directory to list
            ignore: Optional list of glob patterns to ignore
            
        Returns:
            List of file and directory names
            
        Raises:
            ValueError: If path is not absolute
            FileNotFoundError: If the directory doesn't exist
            NotADirectoryError: If path is not a directory
        """
        if not os.path.isabs(path):
            raise ValueError("path must be absolute")
            
        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory not found: {path}")
            
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a directory: {path}")
            
        entries = []
        
        # Get all entries in the directory
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            
            # Check if entry should be ignored
            if ignore:
                should_ignore = False
                for pattern in ignore:
                    if fnmatch.fnmatch(entry, pattern):
                        should_ignore = True
                        break
                if should_ignore:
                    continue
                    
            # Add entry with indicator for directories
            if os.path.isdir(full_path):
                entries.append(entry + '/')
            else:
                entries.append(entry)
                
        # Sort entries (directories first, then files)
        dirs = sorted([e for e in entries if e.endswith('/')])
        files = sorted([e for e in entries if not e.endswith('/')])
        
        return dirs + files