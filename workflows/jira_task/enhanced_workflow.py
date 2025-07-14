#!/usr/bin/env python3
"""
Enhanced JIRA Task Workflow - Phase 2 Implementation

This module extends the base JIRA workflow with enhanced Claude Code integration,
context preservation, and advanced development assistance features.
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path

from .jira_task import JiraWorkflow
from .config import JiraConfig


class WorkflowContext:
    """Manages workflow context and state between commands"""
    
    def __init__(self, issue_key: str, issue_data: Dict[str, Any]):
        self.issue_key = issue_key
        self.issue_data = issue_data
        self.session_start = datetime.now()
        self.command_history = []
        self.file_changes = []
        self.analysis_results = {}
        self.implementation_notes = []
        self.test_results = []
        self.current_phase = "planning"
        
    def add_command(self, command: str, result: str, files_modified: List[str] = None):
        """Add command and result to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result[:500] + "..." if len(result) > 500 else result,
            "files_modified": files_modified or []
        }
        self.command_history.append(entry)
        
        if files_modified:
            self.file_changes.extend(files_modified)
    
    def get_context_summary(self) -> str:
        """Generate context summary for prompts"""
        summary = f"""
WORKFLOW CONTEXT for {self.issue_key}:
Issue: {self.issue_data.get('summary', 'Unknown')}
Current Phase: {self.current_phase}
Session Duration: {datetime.now() - self.session_start}
Commands Executed: {len(self.command_history)}
Files Modified: {len(set(self.file_changes))}

RECENT ACTIVITY:
"""
        # Add last 3 commands
        for cmd in self.command_history[-3:]:
            summary += f"- {cmd['command']}: {cmd['result'][:100]}...\n"
        
        if self.file_changes:
            summary += f"\nMODIFIED FILES: {', '.join(set(self.file_changes[-10:]))}"
        
        return summary


class EnhancedClaudeCodeClient:
    """Enhanced Claude Code client with better prompting and context management"""
    
    def __init__(self, context: WorkflowContext):
        self.context = context
        self.base_tools = [
            "read", "write", "edit", "multiEdit", "glob", "grep", "ls", 
            "bash", "git", "npm", "cargo", "python", "pytest", "webSearch", "task"
        ]
    
    def _create_enhanced_prompt(self, task_prompt: str, command_type: str) -> str:
        """Create enhanced prompt with context and specific instructions"""
        
        context_aware_prompt = f"""You are an expert development assistant working on JIRA issue {self.context.issue_key}.

{self.context.get_context_summary()}

CURRENT TASK TYPE: {command_type}

TASK-SPECIFIC INSTRUCTIONS:
{self._get_task_instructions(command_type)}

CURRENT REQUEST:
{task_prompt}

IMPORTANT GUIDELINES:
- Consider the context from previous commands
- Build upon work already done in this session
- Avoid repeating analysis already completed
- Focus on incremental progress
- Be specific about file paths and changes
- Provide clear explanations for your actions
"""
        return context_aware_prompt
    
    def _get_task_instructions(self, command_type: str) -> str:
        """Get specific instructions for different command types"""
        instructions = {
            "analyze": """
For ANALYSIS tasks:
1. Use ls to explore directory structure systematically
2. Use grep to search for relevant patterns and existing implementations
3. Use read to examine key files identified
4. Focus on understanding current architecture and identifying integration points
5. Provide specific file paths and line numbers where relevant
6. Summarize findings with clear recommendations for next steps
""",
            "implement": """
For IMPLEMENTATION tasks:
1. Read existing files to understand current patterns and conventions
2. Use edit or multiEdit to make specific, targeted changes
3. Follow existing code style and patterns
4. Add appropriate comments and documentation
5. Ensure changes are atomic and focused
6. Test changes locally where possible
7. Explain the reasoning behind each change
""",
            "test": """
For TESTING tasks:
1. Identify existing test patterns and frameworks
2. Create tests that follow existing conventions
3. Use pytest or appropriate test runner
4. Ensure good test coverage for new functionality
5. Run tests and report results clearly
6. Fix any test failures before proceeding
7. Consider edge cases and error conditions
""",
            "review": """
For REVIEW tasks:
1. Use git status and git diff to see all changes
2. Review code quality, style, and consistency
3. Check that all requirements are met
4. Run linting and formatting tools if available
5. Verify tests are passing
6. Prepare clear, descriptive commit message
7. Identify any remaining work or issues
""",
            "completion": """
For COMPLETION tasks:
1. Perform final quality checks and testing
2. Create comprehensive commit with proper message
3. Push branch to remote repository
4. Create pull request with detailed description
5. Link PR to JIRA issue
6. Provide summary of work completed
7. Identify any follow-up tasks needed
"""
        }
        return instructions.get(command_type, "Follow best practices for software development.")
    
    def execute_command(self, prompt: str, command_type: str) -> str:
        """Execute Claude Code command with enhanced prompting"""
        enhanced_prompt = self._create_enhanced_prompt(prompt, command_type)
        
        command = [
            "claude", "-p", "--verbose", "--model", "sonnet",
            "--allowedTools", ",".join(self.base_tools)
        ]
        
        try:
            result = subprocess.run(
                command,
                input=enhanced_prompt,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes
            )
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            response = result.stdout.strip()
            
            # Extract file modifications from response (basic pattern matching)
            modified_files = self._extract_modified_files(response)
            
            # Add to context
            self.context.add_command(command_type, response, modified_files)
            
            return response
            
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 minutes"
        except Exception as e:
            return f"Failed to execute Claude command: {e}"
    
    def _extract_modified_files(self, response: str) -> List[str]:
        """Extract list of modified files from Claude Code response"""
        # This is a basic implementation - could be enhanced with better parsing
        modified_files = []
        lines = response.split('\n')
        
        for line in lines:
            # Look for common patterns indicating file modifications
            if any(pattern in line.lower() for pattern in ['modified:', 'created:', 'updated:', 'edited:']):
                # Extract file path (this is a simple approach)
                parts = line.split()
                for part in parts:
                    if '/' in part and '.' in part:
                        modified_files.append(part.strip(',.()'))
        
        return modified_files


class EnhancedJiraWorkflow(JiraWorkflow):
    """Enhanced JIRA workflow with Phase 2 features"""
    
    def __init__(self, jira_config: JiraConfig, repo_path: Optional[str] = None):
        super().__init__(jira_config, repo_path)
        self.workflow_context = None
        self.enhanced_claude = None
    
    def start_work_on_issue(self, issue_key: str) -> Dict[str, Any]:
        """Enhanced start workflow with context initialization"""
        result = super().start_work_on_issue(issue_key)
        
        if result["status"] == "success":
            # Initialize enhanced context
            self.workflow_context = WorkflowContext(issue_key, result["issue"])
            self.enhanced_claude = EnhancedClaudeCodeClient(self.workflow_context)
            
            # Enhanced initial analysis
            initial_analysis = self._perform_initial_analysis(issue_key, result["issue"])
            result["initial_analysis"] = initial_analysis
        
        return result
    
    def _perform_initial_analysis(self, issue_key: str, issue_data: Dict[str, Any]) -> str:
        """Perform enhanced initial analysis of the issue"""
        analysis_prompt = f"""Perform comprehensive initial analysis for JIRA issue {issue_key}: {issue_data['summary']}

Description: {issue_data.get('description', 'No description provided')}

Please perform the following analysis:

1. PROJECT STRUCTURE ANALYSIS:
   - Explore the repository structure with ls
   - Identify the technology stack and frameworks in use
   - Locate configuration files, dependencies, and build tools

2. REQUIREMENTS ANALYSIS:
   - Break down the issue description into specific requirements
   - Identify functional and non-functional requirements
   - Consider edge cases and constraints

3. ARCHITECTURE ASSESSMENT:
   - Identify existing patterns and conventions
   - Locate relevant modules and components
   - Assess impact of proposed changes

4. IMPLEMENTATION STRATEGY:
   - Propose a high-level implementation approach
   - Identify files that will need modification
   - Suggest testing strategy
   - Estimate complexity and potential risks

5. DEVELOPMENT PLAN:
   - Create step-by-step implementation plan
   - Prioritize tasks and identify dependencies
   - Suggest checkpoints for validation

Provide a comprehensive analysis that will guide the entire development process."""
        
        return self.enhanced_claude.execute_command(analysis_prompt, "analyze")
    
    def enhanced_analyze_codebase(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Enhanced codebase analysis with context awareness"""
        if not self.enhanced_claude:
            print("❌ Enhanced workflow not initialized. Use start command first.")
            return
        
        self.workflow_context.current_phase = "analysis"
        
        analyze_prompt = f"""Perform detailed codebase analysis for implementing the solution.

Based on previous analysis, now dive deeper into:

1. DETAILED FILE EXAMINATION:
   - Read key files identified in initial analysis
   - Understand current implementation patterns
   - Identify integration points and dependencies

2. SIMILAR IMPLEMENTATIONS:
   - Search for similar features or patterns in the codebase
   - Analyze how similar problems were solved
   - Identify reusable components or utilities

3. IMPACT ANALYSIS:
   - Identify all files that will need changes
   - Assess backward compatibility requirements
   - Consider performance implications

4. TECHNICAL CONSTRAINTS:
   - Identify any technical limitations or constraints
   - Check for conflicting implementations
   - Assess testing requirements

Provide specific file paths, code examples, and detailed recommendations."""
        
        result = self.enhanced_claude.execute_command(analyze_prompt, "analyze")
        print(f"🔍 Enhanced Codebase Analysis:\n{result}")
    
    def enhanced_implement(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Enhanced implementation with incremental development"""
        if not self.enhanced_claude:
            print("❌ Enhanced workflow not initialized. Use start command first.")
            return
        
        self.workflow_context.current_phase = "implementation"
        
        implement_prompt = f"""Implement the next phase of the solution based on our analysis and previous work.

IMPLEMENTATION GUIDELINES:
1. Make incremental, focused changes
2. Follow existing code patterns and conventions
3. Implement one logical component at a time
4. Add appropriate error handling and validation
5. Include necessary documentation and comments
6. Ensure changes are testable

CURRENT IMPLEMENTATION PHASE:
Based on our analysis and previous commands, implement the next logical step in our development plan.

If this is the first implementation step, start with the core functionality.
If previous implementation has been done, build upon it incrementally.

Focus on creating working, tested code that advances toward the complete solution."""
        
        result = self.enhanced_claude.execute_command(implement_prompt, "implement")
        print(f"🛠️ Enhanced Implementation:\n{result}")
    
    def enhanced_test(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Enhanced testing with comprehensive coverage"""
        if not self.enhanced_claude:
            print("❌ Enhanced workflow not initialized. Use start command first.")
            return
        
        self.workflow_context.current_phase = "testing"
        
        test_prompt = f"""Create comprehensive tests for the implemented functionality.

TESTING REQUIREMENTS:
1. Unit tests for individual components
2. Integration tests for component interactions
3. Edge case and error condition testing
4. Performance testing if relevant
5. Backward compatibility verification

TESTING APPROACH:
1. Follow existing test patterns and frameworks
2. Ensure good test coverage (aim for >80%)
3. Create meaningful test data and scenarios
4. Test both success and failure paths
5. Run all tests and ensure they pass
6. Generate test report with coverage information

Focus on creating robust, maintainable tests that will catch regressions."""
        
        result = self.enhanced_claude.execute_command(test_prompt, "test")
        print(f"🧪 Enhanced Testing:\n{result}")
    
    def enhanced_review(self, issue_key: str) -> None:
        """Enhanced code review with quality checks"""
        if not self.enhanced_claude:
            print("❌ Enhanced workflow not initialized. Use start command first.")
            return
        
        self.workflow_context.current_phase = "review"
        
        review_prompt = f"""Perform comprehensive code review and quality assessment.

REVIEW CHECKLIST:
1. CODE QUALITY:
   - Check for code style consistency
   - Verify adherence to project conventions
   - Assess code clarity and maintainability
   - Look for potential code smells or anti-patterns

2. FUNCTIONALITY:
   - Verify all requirements are implemented
   - Check error handling and edge cases
   - Ensure proper input validation
   - Test integration points

3. TESTING:
   - Verify test coverage is adequate
   - Ensure all tests pass
   - Check test quality and meaningfulness
   - Validate test data and scenarios

4. DOCUMENTATION:
   - Check code comments and documentation
   - Verify API documentation if applicable
   - Ensure README updates if needed

5. SECURITY:
   - Check for security vulnerabilities
   - Verify input sanitization
   - Assess authorization and authentication
   - Review dependency security

6. PERFORMANCE:
   - Check for performance bottlenecks
   - Verify efficient algorithms and data structures
   - Assess memory usage and resource management

7. COMMIT PREPARATION:
   - Generate descriptive commit message
   - Ensure atomic, focused commits
   - Prepare for pull request creation

Provide detailed review findings and prepare for completion."""
        
        result = self.enhanced_claude.execute_command(review_prompt, "review")
        print(f"🔍 Enhanced Code Review:\n{result}")
    
    def enhanced_complete(self, issue_key: str) -> None:
        """Enhanced completion with automated PR creation"""
        if not self.enhanced_claude:
            print("❌ Enhanced workflow not initialized. Use start command first.")
            return
        
        self.workflow_context.current_phase = "completion"
        
        completion_prompt = f"""Complete the development workflow with professional finishing touches.

COMPLETION CHECKLIST:
1. FINAL QUALITY ASSURANCE:
   - Run final test suite
   - Perform final code review
   - Check for any remaining TODOs or FIXMEs
   - Verify all requirements are met

2. DOCUMENTATION:
   - Update relevant documentation
   - Add inline code comments where needed
   - Update API documentation if applicable

3. VERSION CONTROL:
   - Create clean, descriptive commit message
   - Include JIRA issue reference in commit
   - Ensure commit is atomic and focused

4. PULL REQUEST CREATION:
   - Push branch to remote repository
   - Create pull request with GitHub CLI (gh pr create)
   - Include comprehensive PR description
   - Link PR to JIRA issue
   - Add appropriate labels and reviewers

5. JIRA INTEGRATION:
   - Prepare final status update for JIRA
   - Include summary of work completed
   - Link to pull request
   - Note any follow-up tasks

PULL REQUEST TEMPLATE:
Title: {issue_key}: [Brief description]
Description should include:
- Summary of changes
- Implementation approach
- Testing performed
- Breaking changes (if any)
- Additional notes

Complete all steps to finish the development workflow professionally."""
        
        result = self.enhanced_claude.execute_command(completion_prompt, "completion")
        print(f"🏁 Enhanced Completion:\n{result}")
        
        # Update JIRA with final completion status
        self._update_jira_completion(issue_key, result)
    
    def _update_jira_completion(self, issue_key: str, completion_result: str) -> None:
        """Update JIRA with comprehensive completion information"""
        session_duration = datetime.now() - self.workflow_context.session_start
        
        completion_comment = f"""🏆 Development workflow completed for {issue_key}

📊 SESSION SUMMARY:
- Duration: {session_duration}
- Commands executed: {len(self.workflow_context.command_history)}
- Files modified: {len(set(self.workflow_context.file_changes))}

🔧 COMPLETION DETAILS:
{completion_result[:800]}...

📁 MODIFIED FILES:
{', '.join(set(self.workflow_context.file_changes))}

✅ Ready for code review and merge."""
        
        self.jira_client.add_comment(issue_key, completion_comment)
    
    def show_enhanced_help(self) -> None:
        """Show enhanced help with detailed command descriptions"""
        help_text = f"""
📚 ENHANCED JIRA WORKFLOW COMMANDS:

🔍 analyze    - Perform deep codebase analysis with context awareness
              - Builds upon previous analysis results
              - Provides specific file paths and recommendations
              - Identifies integration points and patterns

🛠️  implement  - Incremental implementation with quality focus
              - Follows existing code patterns and conventions  
              - Makes focused, atomic changes
              - Includes error handling and documentation

🧪 test       - Comprehensive testing with coverage analysis
              - Creates unit and integration tests
              - Follows existing test patterns
              - Ensures high test coverage and quality

🔍 review     - Professional code review with quality checks
              - Performs security and performance analysis
              - Checks code style and conventions
              - Prepares optimized commit messages

🏁 done       - Automated completion with PR creation
              - Creates professional pull requests
              - Links to JIRA with comprehensive updates
              - Handles all finishing touches

👋 quit       - Exit with session summary and recommendations
📚 help       - Show this enhanced help

🎯 ENHANCED FEATURES:
- Context preservation between commands
- Intelligent prompt enhancement
- Automated quality checks
- Professional workflow completion
- Comprehensive JIRA integration

Current Session: {len(self.workflow_context.command_history) if self.workflow_context else 0} commands executed"""
        
        print(help_text)
    
    def _enhanced_interactive_development_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Enhanced interactive mode with context awareness"""
        
        while True:
            print("\n" + "="*60)
            print(f"Session: {len(self.workflow_context.command_history)} commands | Phase: {self.workflow_context.current_phase}")
            user_input = input(f"\n👷 [{issue_key}] What would you like to do? (help/analyze/implement/test/review/done/quit): ").strip().lower()
            
            if user_input == 'quit':
                self._show_session_summary(issue_key)
                break
                
            elif user_input == 'done':
                self.enhanced_complete(issue_key)
                break
                
            elif user_input == 'help':
                self.show_enhanced_help()
                
            elif user_input == 'analyze':
                self.enhanced_analyze_codebase(issue_key, issue_data)
                
            elif user_input == 'implement':
                self.enhanced_implement(issue_key, issue_data)
                
            elif user_input == 'test':
                self.enhanced_test(issue_key, issue_data)
                
            elif user_input == 'review':
                self.enhanced_review(issue_key)
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
    
    def _show_session_summary(self, issue_key: str) -> None:
        """Show comprehensive session summary"""
        if not self.workflow_context:
            return
            
        duration = datetime.now() - self.workflow_context.session_start
        
        summary = f"""
📊 SESSION SUMMARY for {issue_key}:

⏱️  Duration: {duration}
🔧 Commands executed: {len(self.workflow_context.command_history)}
📁 Files modified: {len(set(self.workflow_context.file_changes))}
📋 Current phase: {self.workflow_context.current_phase}

💡 TO RESUME WORK:
   python jira_task.py {issue_key} --command start

💬 TO UPDATE JIRA:
   python jira_task.py {issue_key} --command update --comment "Session summary: {len(self.workflow_context.command_history)} commands executed"

🔗 MODIFIED FILES:
   {', '.join(set(self.workflow_context.file_changes)) if self.workflow_context.file_changes else 'None'}
"""
        print(summary)
    
    def execute_development_workflow(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Execute enhanced development workflow"""
        if not self.enhanced_claude:
            print("❌ Enhanced workflow not initialized properly.")
            return
            
        print("\n🚀 Enhanced development workflow ready!")
        print("✨ Features: Context preservation, quality checks, automated PR creation")
        
        # Show initial analysis results
        if hasattr(self, '_last_analysis'):
            print("\n📋 Initial Analysis Complete - Ready for interactive development")
        
        # Enter enhanced interactive mode
        self._enhanced_interactive_development_mode(issue_key, issue_data)