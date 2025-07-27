#!/usr/bin/env python3
"""
Git Integration for JIRA Task Workflow

Handles git operations including branch creation, naming conventions,
and repository management for JIRA issues.
"""

import subprocess
import re
from typing import Optional, Dict, List
from pathlib import Path


class GitError(Exception):
    """Custom exception for Git operations"""
    pass


class GitIntegration:
    """Git operations for JIRA workflow"""
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize Git integration
        
        Args:
            repo_path: Path to git repository (defaults to current directory)
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._validate_git_repo()
    
    def _validate_git_repo(self) -> None:
        """Validate that we're in a git repository"""
        try:
            self._run_git_command(['rev-parse', '--git-dir'])
        except GitError:
            raise GitError(f"Not a git repository: {self.repo_path}")
    
    def _run_git_command(self, args: List[str], check_output: bool = True) -> Optional[str]:
        """
        Run git command and return output
        
        Args:
            args: Git command arguments
            check_output: Whether to capture and return output
            
        Returns:
            Command output if check_output=True, None otherwise
            
        Raises:
            GitError: If git command fails
        """
        cmd = ['git'] + args
        
        try:
            if check_output:
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            else:
                subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    check=True
                )
                return None
        except subprocess.CalledProcessError as e:
            error_msg = f"Git command failed: {' '.join(cmd)}"
            if e.stderr:
                error_msg += f"\nError: {e.stderr.strip()}"
            raise GitError(error_msg)
    
    def sanitize_branch_name(self, text: str) -> str:
        """
        Convert text to valid git branch name
        
        Args:
            text: Text to sanitize
            
        Returns:
            Valid git branch name
        """
        # Remove special characters, keep only alphanumeric, spaces, hyphens
        sanitized = re.sub(r'[^\w\s-]', '', text.lower())
        
        # Replace spaces and multiple hyphens with single hyphen
        sanitized = re.sub(r'[-\s]+', '-', sanitized)
        
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        
        # Limit length to 50 characters
        if len(sanitized) > 50:
            sanitized = sanitized[:50].rstrip('-')
        
        return sanitized
    
    def get_current_branch(self) -> str:
        """
        Get current git branch name
        
        Returns:
            Current branch name
        """
        return self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
    
    def branch_exists(self, branch_name: str) -> bool:
        """
        Check if branch exists locally
        
        Args:
            branch_name: Name of branch to check
            
        Returns:
            True if branch exists
        """
        try:
            self._run_git_command(['show-ref', '--verify', f'refs/heads/{branch_name}'])
            return True
        except GitError:
            return False
    
    def create_branch(self, issue_key: str, summary: str, base_branch: str = "main") -> str:
        """
        Create feature branch from JIRA issue
        
        Args:
            issue_key: JIRA issue key (e.g., 'PROJ-123')
            summary: Issue summary/title
            base_branch: Base branch to create from (default: main)
            
        Returns:
            Created branch name
            
        Raises:
            GitError: If branch creation fails
        """
        # Create standardized branch name
        sanitized_summary = self.sanitize_branch_name(summary)
        branch_name = f"feature/{issue_key.lower()}-{sanitized_summary}"
        
        # Check if branch already exists
        if self.branch_exists(branch_name):
            print(f"Branch {branch_name} already exists, switching to it")
            self._run_git_command(['checkout', branch_name], check_output=False)
            return branch_name
        
        # Ensure we're on the base branch and it's up to date
        try:
            self._run_git_command(['checkout', base_branch], check_output=False)
            # Try to pull latest changes (might fail if no remote)
            try:
                self._run_git_command(['pull'], check_output=False)
            except GitError:
                print(f"Warning: Could not pull latest changes for {base_branch}")
        except GitError:
            # Base branch might not exist, try 'master' as fallback
            if base_branch == "main":
                try:
                    self._run_git_command(['checkout', 'master'], check_output=False)
                    base_branch = 'master'
                except GitError:
                    raise GitError("Could not find 'main' or 'master' branch")
            else:
                raise GitError(f"Base branch '{base_branch}' not found")
        
        # Create and checkout new branch
        self._run_git_command(['checkout', '-b', branch_name], check_output=False)
        
        print(f"Created and switched to branch: {branch_name}")
        return branch_name
    
    def checkout_branch(self, branch_name: str) -> None:
        """
        Checkout an existing branch
        
        Args:
            branch_name: Name of branch to checkout
            
        Raises:
            GitError: If checkout fails
        """
        self._run_git_command(['checkout', branch_name], check_output=False)
    
    def create_branch_simple(self, branch_name: str, base_branch: str = "main") -> str:
        """
        Create a simple branch with the given name
        
        Args:
            branch_name: Name of branch to create
            base_branch: Base branch to create from (default: main)
            
        Returns:
            Created branch name
            
        Raises:
            GitError: If branch creation fails
        """
        # Check if branch already exists
        if self.branch_exists(branch_name):
            print(f"Branch {branch_name} already exists, switching to it")
            self.checkout_branch(branch_name)
            return branch_name
        
        # Ensure we're on the base branch
        try:
            self.checkout_branch(base_branch)
        except GitError:
            # Try 'master' as fallback
            if base_branch == "main":
                try:
                    self.checkout_branch('master')
                except GitError:
                    raise GitError("Could not find 'main' or 'master' branch")
            else:
                raise GitError(f"Base branch '{base_branch}' not found")
        
        # Create and checkout new branch
        self._run_git_command(['checkout', '-b', branch_name], check_output=False)
        
        print(f"Created and switched to branch: {branch_name}")
        return branch_name
    
    def get_repo_status(self) -> Dict[str, List[str]]:
        """
        Get git repository status
        
        Returns:
            Dict with file status information
        """
        status_output = self._run_git_command(['status', '--porcelain'])
        
        status = {
            'modified': [],
            'added': [],
            'deleted': [],
            'untracked': []
        }
        
        if not status_output:
            return status
        
        for line in status_output.split('\n'):
            if len(line) < 3:
                continue
            
            status_code = line[:2]
            filename = line[3:]
            
            if status_code.startswith('M'):
                status['modified'].append(filename)
            elif status_code.startswith('A'):
                status['added'].append(filename)
            elif status_code.startswith('D'):
                status['deleted'].append(filename)
            elif status_code.startswith('??'):
                status['untracked'].append(filename)
        
        return status
    
    def has_uncommitted_changes(self) -> bool:
        """
        Check if repository has uncommitted changes
        
        Returns:
            True if there are uncommitted changes
        """
        status = self.get_repo_status()
        return any(files for files in status.values())
    
    def get_remote_url(self) -> Optional[str]:
        """
        Get remote repository URL
        
        Returns:
            Remote URL or None if no remote
        """
        try:
            return self._run_git_command(['remote', 'get-url', 'origin'])
        except GitError:
            return None
    
    def push_branch(self, branch_name: str, set_upstream: bool = True) -> bool:
        """
        Push branch to remote repository
        
        Args:
            branch_name: Name of branch to push
            set_upstream: Whether to set upstream tracking
            
        Returns:
            True if push successful
        """
        try:
            if set_upstream:
                self._run_git_command(['push', '-u', 'origin', branch_name], check_output=False)
            else:
                self._run_git_command(['push', 'origin', branch_name], check_output=False)
            return True
        except GitError:
            return False
    
    def commit_changes(self, message: str, add_all: bool = True) -> bool:
        """
        Commit changes with message
        
        Args:
            message: Commit message
            add_all: Whether to add all tracked files
            
        Returns:
            True if commit successful
        """
        try:
            if add_all:
                self._run_git_command(['add', '-A'], check_output=False)
            
            self._run_git_command(['commit', '-m', message], check_output=False)
            return True
        except GitError:
            return False
    
    def get_branch_info(self, branch_name: Optional[str] = None) -> Dict[str, str]:
        """
        Get information about a branch
        
        Args:
            branch_name: Branch to get info for (default: current branch)
            
        Returns:
            Dict with branch information
        """
        if not branch_name:
            branch_name = self.get_current_branch()
        
        info = {'name': branch_name}
        
        try:
            # Get last commit hash
            info['commit'] = self._run_git_command(['rev-parse', 'HEAD'])[:8]
            
            # Get last commit message
            info['message'] = self._run_git_command(['log', '-1', '--pretty=format:%s'])
            
            # Check if branch has remote tracking
            try:
                remote_branch = self._run_git_command(['rev-parse', '--abbrev-ref', f'{branch_name}@{{upstream}}'])
                info['remote'] = remote_branch
            except GitError:
                info['remote'] = None
                
        except GitError:
            pass
        
        return info


if __name__ == "__main__":
    # Example usage and testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Integration Testing")
    parser.add_argument("--status", action="store_true",
                       help="Show repository status")
    parser.add_argument("--current-branch", action="store_true",
                       help="Show current branch")
    parser.add_argument("--create-branch", nargs=2, metavar=('ISSUE_KEY', 'SUMMARY'),
                       help="Create branch for issue")
    parser.add_argument("--repo-path", help="Path to git repository")
    
    args = parser.parse_args()
    
    try:
        git = GitIntegration(args.repo_path)
        
        if args.status:
            status = git.get_repo_status()
            print("Repository Status:")
            for status_type, files in status.items():
                if files:
                    print(f"  {status_type}: {len(files)} files")
                    for file in files[:5]:  # Show first 5 files
                        print(f"    - {file}")
                    if len(files) > 5:
                        print(f"    ... and {len(files) - 5} more")
        
        elif args.current_branch:
            branch = git.get_current_branch()
            info = git.get_branch_info(branch)
            print(f"Current branch: {branch}")
            print(f"Last commit: {info.get('commit', 'unknown')} - {info.get('message', 'no message')}")
            if info.get('remote'):
                print(f"Remote tracking: {info['remote']}")
        
        elif args.create_branch:
            issue_key, summary = args.create_branch
            branch_name = git.create_branch(issue_key, summary)
            print(f"✅ Created branch: {branch_name}")
        
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"❌ Error: {e}")