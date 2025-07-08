#!/usr/bin/env python3
"""
Phase 5: Agent-Flows Mode-Based JIRA Workflow

This module implements the Phase 5 JIRA workflow that leverages the sophisticated 
agent-flows modes system for intelligent task orchestration. Unlike traditional 
linear workflows, this implementation uses an orchestrator that dynamically 
delegates tasks to specialized modes based on JIRA issue requirements.
"""

import os
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from .config import JiraConfig
from .enterprise_workflow import EnterpriseJiraWorkflow


class ModeType(Enum):
    """Available agent-flows modes for JIRA workflow orchestration"""
    ORCHESTRATOR = "orchestrator"
    ARCHITECT = "architect"
    CODE = "code"
    DEBUG = "debug"
    DEVOPS = "devops"
    EXPERT_CONSULTANT = "expert_consultant"
    FACT_CHECKER = "fact_checker"
    RESEARCHER = "researcher"
    RESEARCH_MANAGER = "research_manager"
    SYNTHESIZER = "synthesizer"
    USER_STORY = "user_story"
    WRITER = "writer"
    ASK = "ask"


@dataclass
class WorkflowPhase:
    """Represents a phase in the agent-flows workflow"""
    name: str
    mode: ModeType
    objective: str
    prerequisites: List[str] = field(default_factory=list)
    tools: Optional[str] = None
    context_requirements: List[str] = field(default_factory=list)


@dataclass
class ModeContext:
    """Manages context and results across mode executions"""
    user_stories: Optional[str] = None
    research_findings: Optional[str] = None
    architecture_design: Optional[str] = None
    implementation_summary: Optional[str] = None
    test_results: Optional[str] = None
    expert_review: Optional[str] = None
    fact_check_results: Optional[str] = None
    phase_results: Dict[str, str] = field(default_factory=dict)
    
    def add_user_stories(self, stories: str) -> None:
        """Add user story analysis results"""
        self.user_stories = stories
        self.phase_results["user_stories"] = stories
    
    def add_research_findings(self, findings: str) -> None:
        """Add research results"""
        self.research_findings = findings
        self.phase_results["research"] = findings
    
    def add_architecture_design(self, design: str) -> None:
        """Add architectural design"""
        self.architecture_design = design
        self.phase_results["architecture"] = design
    
    def add_implementation_summary(self, summary: str) -> None:
        """Add implementation summary"""
        self.implementation_summary = summary
        self.phase_results["implementation"] = summary
    
    def add_review_results(self, expert_review: str, fact_check: str) -> None:
        """Add review and validation results"""
        self.expert_review = expert_review
        self.fact_check_results = fact_check
        self.phase_results["expert_review"] = expert_review
        self.phase_results["fact_check"] = fact_check
    
    def add_phase_result(self, phase_name: str, result: str) -> None:
        """Add result from a specific workflow phase"""
        self.phase_results[phase_name] = result
    
    def get_user_stories(self) -> str:
        """Get user stories summary"""
        return self.user_stories or "No user stories available"
    
    def get_research_summary(self) -> str:
        """Get research findings summary"""
        return self.research_findings or "No research findings available"
    
    def get_architecture_summary(self) -> str:
        """Get architecture design summary"""
        return self.architecture_design or "No architecture design available"
    
    def get_all_results(self) -> Dict[str, str]:
        """Get all phase results"""
        return self.phase_results.copy()


class ClaudeCodeModeExecutor:
    """Handles execution of Claude Code commands with specialized agent-flows modes"""
    
    def __init__(self, model: str = "sonnet", modes_path: Optional[Path] = None):
        self.model = model
        self.modes_path = modes_path or Path("modes")
        self.base_command = ["claude", "-p", "--verbose", "--model", model]
        self.mode_cache = {}
        self.available_modes = {
            ModeType.ORCHESTRATOR: self.modes_path / "orchestrator.md",
            ModeType.ARCHITECT: self.modes_path / "architect.md", 
            ModeType.CODE: self.modes_path / "code.md",
            ModeType.DEBUG: self.modes_path / "debug.md",
            ModeType.DEVOPS: self.modes_path / "devops.md",
            ModeType.EXPERT_CONSULTANT: self.modes_path / "expert_consultant.md",
            ModeType.FACT_CHECKER: self.modes_path / "fact_checker.md",
            ModeType.RESEARCHER: self.modes_path / "researcher.md",
            ModeType.RESEARCH_MANAGER: self.modes_path / "research_manager.md",
            ModeType.SYNTHESIZER: self.modes_path / "synthesizer.md",
            ModeType.USER_STORY: self.modes_path / "user_story.md",
            ModeType.WRITER: self.modes_path / "writer.md",
            ModeType.ASK: self.modes_path / "ask.md"
        }
    
    def load_mode_instructions(self, mode_type: ModeType) -> str:
        """Load mode instructions from file with caching"""
        if mode_type in self.mode_cache:
            return self.mode_cache[mode_type]
        
        mode_file = self.available_modes[mode_type]
        if not mode_file.exists():
            raise FileNotFoundError(f"Mode file not found: {mode_file}")
        
        with open(mode_file, 'r') as f:
            instructions = f.read()
            self.mode_cache[mode_type] = instructions
            return instructions
    
    def execute_claude_with_mode(self, mode_type: ModeType, task_prompt: str, tools: Optional[str] = None) -> str:
        """Execute Claude Code with a specific agent-flows mode"""
        mode_instructions = self.load_mode_instructions(mode_type)
        
        # Combine mode instructions with task
        full_prompt = f"""{mode_instructions}

Task: {task_prompt}

Please complete this task according to your mode instructions above."""

        command = self.base_command.copy()
        if tools:
            command.extend(["--allowedTools", tools])
        
        print(f"🤖 Executing {mode_type.value} mode with Claude Code...")
        
        try:
            result = subprocess.run(
                command,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout for complex tasks
            )
            
            if result.returncode != 0:
                raise Exception(f"Claude command failed: {result.stderr}")
            
            return result.stdout.strip()
                
        except subprocess.TimeoutExpired:
            raise Exception("Claude command timed out after 30 minutes")
        except Exception as e:
            raise Exception(f"Error executing Claude command: {e}")


class TaskAnalyzer:
    """Analyzes JIRA issues to determine workflow requirements and mode selection"""
    
    @staticmethod
    def analyze_issue_requirements(jira_issue: Dict[str, Any], project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze JIRA issue to determine mode requirements and workflow strategy"""
        fields = jira_issue.get('fields', {})
        issue_type = fields.get('issuetype', {}).get('name', '').lower()
        labels = [label.get('name', '') for label in fields.get('labels', [])]
        description = fields.get('description', '') or ''
        summary = fields.get('summary', '') or ''
        priority = fields.get('priority', {}).get('name', '').lower()
        
        requirements = {
            "complexity": "medium",
            "domain": "general",
            "requires_research": False,
            "requires_architecture": False,
            "requires_security_review": False,
            "requires_user_stories": False,
            "suggested_modes": [],
            "workflow_type": "standard"
        }
        
        # Analyze issue type
        if issue_type in ['epic', 'feature', 'story']:
            requirements["complexity"] = "high" if issue_type == 'epic' else "medium"
            requirements["requires_user_stories"] = True
            requirements["suggested_modes"].extend([ModeType.USER_STORY, ModeType.ARCHITECT])
        
        if issue_type in ['bug', 'defect']:
            requirements["suggested_modes"].extend([ModeType.DEBUG, ModeType.CODE])
        
        # Analyze labels and content for special requirements
        security_keywords = ['security', 'auth', 'authentication', 'authorization', 'crypto']
        if any(keyword in ' '.join(labels + [description.lower(), summary.lower()]) for keyword in security_keywords):
            requirements["requires_security_review"] = True
            requirements["suggested_modes"].append(ModeType.EXPERT_CONSULTANT)
        
        research_keywords = ['research', 'investigation', 'analyze', 'evaluate', 'spike']
        if any(keyword in ' '.join(labels + [description.lower(), summary.lower()]) for keyword in research_keywords):
            requirements["requires_research"] = True
            requirements["suggested_modes"].extend([ModeType.RESEARCHER, ModeType.RESEARCH_MANAGER])
        
        architecture_keywords = ['architecture', 'design', 'system', 'integration', 'api']
        if any(keyword in ' '.join(labels + [description.lower(), summary.lower()]) for keyword in architecture_keywords):
            requirements["requires_architecture"] = True
            requirements["suggested_modes"].append(ModeType.ARCHITECT)
        
        # Analyze priority for workflow complexity
        if priority in ['critical', 'highest', 'high']:
            requirements["workflow_type"] = "comprehensive"
            requirements["requires_security_review"] = True
        
        # Add domain-specific modes based on project context
        project_type = project_context.get('type', 'general').lower()
        if project_type in ['api', 'backend', 'service']:
            requirements["domain"] = "backend"
            requirements["suggested_modes"].append(ModeType.CODE)
        elif project_type in ['frontend', 'web', 'ui']:
            requirements["domain"] = "frontend"
            requirements["suggested_modes"].append(ModeType.CODE)
        elif project_type in ['infrastructure', 'devops', 'deployment']:
            requirements["domain"] = "infrastructure"
            requirements["suggested_modes"].append(ModeType.DEVOPS)
        
        # Always include orchestrator for coordination
        if ModeType.ORCHESTRATOR not in requirements["suggested_modes"]:
            requirements["suggested_modes"].insert(0, ModeType.ORCHESTRATOR)
        
        return requirements


class ModeBasedJiraWorkflow(EnterpriseJiraWorkflow):
    """Phase 5 JIRA workflow using agent-flows modes with dynamic orchestration"""
    
    def __init__(self, jira_config: JiraConfig, repo_path: Optional[str] = None, 
                 current_user: str = None, modes_path: Optional[Path] = None):
        super().__init__(jira_config, repo_path, current_user)
        self.mode_executor = ClaudeCodeModeExecutor(modes_path=modes_path)
        self.mode_context = ModeContext()
        self.orchestration_history = []
        self.workflow_phases = []
    
    def get_mode_tools(self, mode_type: ModeType) -> str:
        """Get appropriate Claude Code tools for each agent mode"""
        mode_tools = {
            ModeType.ORCHESTRATOR: "read,write,task,webSearch",
            ModeType.RESEARCHER: "read,glob,grep,webSearch,task",
            ModeType.RESEARCH_MANAGER: "read,write,task,webSearch",
            ModeType.ARCHITECT: "read,write,edit,multiEdit,glob,grep,task",
            ModeType.CODE: "read,write,edit,multiEdit,bash,git,python,pytest,npm",
            ModeType.DEBUG: "read,edit,bash,python,pytest,git,grep",
            ModeType.DEVOPS: "read,write,bash,git,task",
            ModeType.WRITER: "read,write,edit,task",
            ModeType.EXPERT_CONSULTANT: "read,glob,grep,task,webSearch",
            ModeType.FACT_CHECKER: "read,webSearch,task,grep",
            ModeType.USER_STORY: "read,write,task",
            ModeType.SYNTHESIZER: "read,write,task",
            ModeType.ASK: "read,webSearch,task"
        }
        return mode_tools.get(mode_type, "read,write,task")
    
    def execute_agent_mode(self, mode_type: ModeType, prompt: str) -> str:
        """Execute an agent-flows mode using Claude Code as the execution engine"""
        tools = self.get_mode_tools(mode_type)
        
        # Record the mode execution
        execution_record = {
            "mode": mode_type.value,
            "timestamp": datetime.now().isoformat(),
            "tools": tools
        }
        self.orchestration_history.append(execution_record)
        
        # Execute the mode
        result = self.mode_executor.execute_claude_with_mode(mode_type, prompt, tools)
        
        # Update execution record with result summary
        execution_record["result_length"] = len(result)
        execution_record["success"] = True
        
        return result
    
    def start_mode_based_workflow(self, issue_key: str) -> None:
        """Start the Phase 5 agent-flows mode-based workflow"""
        print(f"🎭 Starting Agent-Flows JIRA Workflow - Phase 5")
        print(f"🎯 Issue: {issue_key}")
        
        # Get issue details
        issue_data = self.jira_client.get_issue(issue_key)
        
        print(f"📋 {issue_data['fields']['summary']}")
        if self.user:
            print(f"👤 User: {self.user.username} ({self.user.role.value}) | Team: {self.user.team}")
        
        # Analyze issue requirements
        project_context = self._get_project_context()
        requirements = TaskAnalyzer.analyze_issue_requirements(issue_data, project_context)
        
        print(f"🔍 Issue Analysis:")
        print(f"   Complexity: {requirements['complexity']}")
        print(f"   Domain: {requirements['domain']}")
        print(f"   Workflow Type: {requirements['workflow_type']}")
        print(f"   Suggested Modes: {[mode.value for mode in requirements['suggested_modes']]}")
        
        # Start orchestrator-driven workflow
        self._execute_orchestrated_workflow(issue_key, issue_data, requirements)
    
    def _execute_orchestrated_workflow(self, issue_key: str, issue_data: Dict[str, Any], 
                                     requirements: Dict[str, Any]) -> None:
        """Execute a fully orchestrated workflow using agent-flows modes"""
        
        # Start with orchestrator for master planning
        orchestrator_prompt = f"""
As the workflow orchestrator, create a comprehensive development plan for JIRA issue {issue_key}.

Issue: {issue_data['fields']['summary']}
Description: {issue_data['fields']['description'] or 'No description provided'}
Issue Type: {issue_data['fields']['issuetype']['name']}
Priority: {issue_data['fields']['priority']['name']}

Analysis Results:
- Complexity: {requirements['complexity']}
- Domain: {requirements['domain']}
- Requires Research: {requirements['requires_research']}
- Requires Architecture: {requirements['requires_architecture']}
- Requires Security Review: {requirements['requires_security_review']}
- Requires User Stories: {requirements['requires_user_stories']}

Available agent modes: orchestrator, user_story, researcher, research_manager, architect, 
                      code, debug, expert_consultant, fact_checker, synthesizer, writer, devops

Create a comprehensive workflow plan that:
1. Breaks down this JIRA issue into logical phases
2. Assigns appropriate agent modes to each phase
3. Defines clear handoffs between modes
4. Ensures quality gates and validation points
5. Coordinates the overall development process

For each phase, specify:
- Phase name and objective
- Assigned agent mode
- Prerequisites from previous phases
- Expected deliverables

Start by creating the master coordination plan, then we'll execute each phase.
"""
        
        print(f"\n🎭 Executing Orchestrator Planning...")
        master_plan = self.execute_agent_mode(ModeType.ORCHESTRATOR, orchestrator_prompt)
        print(f"📋 Master Plan Created:\n{master_plan}")
        
        # Store the master plan
        self.mode_context.add_phase_result("orchestrator_plan", master_plan)
        
        # Enter interactive mode for phase execution
        self._mode_based_interactive_development(issue_key, issue_data, master_plan)
    
    def _mode_based_interactive_development(self, issue_key: str, issue_data: Dict[str, Any], 
                                          master_plan: str) -> None:
        """Agent-flows mode-based interactive development"""
        
        print(f"\n🎭 Agent-Flows Interactive Development Mode")
        print(f"📋 Master Plan Available - Use 'plan' to review")
        
        while True:
            print("\n" + "="*80)
            print(f"🎭 Agent-Flows Workflow | Issue: {issue_key}")
            
            mode_input = input(f"\n🎭 [{issue_key}] Agent Mode (help/plan/orchestrate/story/architect/research/code/debug/review/write/devops/done/quit): ").strip().lower()
            
            if mode_input == 'plan':
                print(f"📋 Master Plan:\n{master_plan}")
            elif mode_input == 'orchestrate':
                self._delegate_to_orchestrator(issue_key, issue_data)
            elif mode_input == 'story':
                self._delegate_to_user_story_mode(issue_key, issue_data)
            elif mode_input == 'architect':
                self._delegate_to_architect_mode(issue_key, issue_data)
            elif mode_input == 'research':
                self._delegate_to_research_modes(issue_key, issue_data)
            elif mode_input == 'code':
                self._delegate_to_code_mode(issue_key, issue_data)
            elif mode_input == 'debug':
                self._delegate_to_debug_mode(issue_key, issue_data)
            elif mode_input == 'review':
                self._delegate_to_review_modes(issue_key, issue_data)
            elif mode_input == 'write':
                self._delegate_to_writer_mode(issue_key, issue_data)
            elif mode_input == 'devops':
                self._delegate_to_devops_mode(issue_key, issue_data)
            elif mode_input == 'done':
                self._mode_based_completion(issue_key)
                break
            elif mode_input == 'quit':
                self._show_session_summary(issue_key)
                break
            elif mode_input == 'help':
                self._show_agent_modes_help()
            else:
                print("❌ Unknown command. Type 'help' for available agent mode commands.")
    
    def _delegate_to_orchestrator(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Delegate workflow coordination to orchestrator mode"""
        
        current_context = self.mode_context.get_all_results()
        context_summary = "\n".join([f"- {phase}: {result[:100]}..." for phase, result in current_context.items()])
        
        orchestrator_prompt = f"""
Review the current progress on JIRA issue {issue_key} and provide strategic coordination.

Issue: {issue_data['fields']['summary']}

Current Progress:
{context_summary if context_summary else "No previous work completed"}

Tasks:
1. Assess current workflow state and progress
2. Identify next priority tasks and recommend which modes should handle them
3. Identify any gaps or issues that need attention
4. Provide strategic guidance for completing this JIRA issue efficiently
5. Coordinate handoffs between different specialist modes

Provide clear recommendations for the next steps in this development workflow.
"""
        
        result = self.execute_agent_mode(ModeType.ORCHESTRATOR, orchestrator_prompt)
        self.mode_context.add_phase_result(f"orchestrator_{datetime.now().strftime('%H%M')}", result)
        print(f"🎭 Orchestrator Guidance:\n{result}")
    
    def _delegate_to_user_story_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Use user story mode to break down JIRA requirements"""
        
        user_story_prompt = f"""
Analyze JIRA issue {issue_key} and break it down into clear user stories and acceptance criteria.

JIRA Issue: {issue_data['fields']['summary']}
Description: {issue_data['fields']['description'] or 'No description provided'}
Issue Type: {issue_data['fields']['issuetype']['name']}

Your tasks:
1. Extract the core user needs from this JIRA issue
2. Create well-formed user stories ("As a... I want... So that...")
3. Define clear acceptance criteria for each story
4. Identify any edge cases or special requirements
5. Suggest the priority and complexity of each story
6. Consider technical constraints and implementation factors

Focus on transforming the JIRA issue into actionable development tasks.
Provide comprehensive user story analysis that will guide implementation.
"""
        
        result = self.execute_agent_mode(ModeType.USER_STORY, user_story_prompt)
        self.mode_context.add_user_stories(result)
        print(f"📖 User Story Analysis:\n{result}")
    
    def _delegate_to_research_modes(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Use research modes to investigate JIRA issue requirements"""
        
        # Start with research manager for coordination
        research_manager_prompt = f"""
Coordinate comprehensive research for JIRA issue {issue_key}: {issue_data['fields']['summary']}

Research Scope:
- Technical requirements investigation
- Existing solution analysis  
- Dependency and integration research
- Best practices and standards review
- Security and performance considerations

Issue Context: {issue_data['fields']['description'] or 'No description provided'}
Project Type: {self._get_project_context().get('type', 'Unknown')}

Tasks:
1. Create a research strategy for this JIRA issue
2. Identify key areas that need investigation
3. Determine research priorities and depth needed
4. Coordinate with researcher mode for detailed investigation
5. Plan synthesis of findings into actionable insights

Provide a comprehensive research strategy and initial findings.
"""
        
        research_plan = self.execute_agent_mode(ModeType.RESEARCH_MANAGER, research_manager_prompt)
        
        # Execute detailed research based on the plan
        researcher_prompt = f"""
Based on the research strategy, conduct detailed investigation of JIRA issue {issue_key}.

Research Strategy: {research_plan}

Conduct thorough research on:
1. Technical implementation approaches and best practices
2. Required libraries, frameworks, and tools
3. Integration patterns and examples
4. Potential challenges and solutions
5. Security considerations and requirements
6. Performance implications and optimizations

Use all available tools to gather comprehensive, accurate information.
Focus on practical implementation guidance for this specific issue.
"""
        
        research_results = self.execute_agent_mode(ModeType.RESEARCHER, researcher_prompt)
        self.mode_context.add_research_findings(research_results)
        print(f"🔍 Research Results:\n{research_results}")
    
    def _delegate_to_architect_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Use architect mode for system design decisions"""
        
        architect_prompt = f"""
Design the system architecture for JIRA issue {issue_key}: {issue_data['fields']['summary']}

Context:
- User Stories: {self.mode_context.get_user_stories()}
- Research Findings: {self.mode_context.get_research_summary()}
- Current System: {self._get_current_system_overview()}
- Project Type: {self._get_project_context().get('type', 'Unknown')}

Architecture Tasks:
1. Design the solution architecture for this JIRA issue
2. Define component interactions and data flow
3. Specify integration points with existing systems
4. Recommend design patterns and architectural approaches
5. Identify potential architectural risks and mitigations
6. Consider scalability, performance, and maintainability
7. Plan for testing and deployment architecture

Create a comprehensive architectural design that provides clear implementation guidance.
Include specific technical details and implementation recommendations.
"""
        
        architecture_design = self.execute_agent_mode(ModeType.ARCHITECT, architect_prompt)
        self.mode_context.add_architecture_design(architecture_design)
        print(f"🏗️ Architecture Design:\n{architecture_design}")
    
    def _delegate_to_code_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Use code mode for implementation tasks"""
        
        code_prompt = f"""
Implement the solution for JIRA issue {issue_key}: {issue_data['fields']['summary']}

Implementation Context:
- User Stories: {self.mode_context.get_user_stories()}
- Architecture: {self.mode_context.get_architecture_summary()}
- Research: {self.mode_context.get_research_summary()}

Implementation Tasks:
1. Review existing codebase and understand current implementation
2. Implement the core functionality as defined in user stories
3. Follow the architectural design and patterns specified
4. Apply research findings and best practices
5. Write clean, maintainable, and well-documented code
6. Include appropriate error handling and validation
7. Ensure compatibility with existing systems

Focus on producing production-ready code that meets all requirements.
Make concrete code changes and provide clear implementation notes.
"""
        
        implementation_result = self.execute_agent_mode(ModeType.CODE, code_prompt)
        self.mode_context.add_implementation_summary(implementation_result)
        print(f"🛠️ Implementation Complete:\n{implementation_result}")
    
    def _delegate_to_debug_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Use debug mode for troubleshooting and fixes"""
        
        debug_prompt = f"""
Debug and troubleshoot issues for JIRA issue {issue_key}: {issue_data['fields']['summary']}

Debug Context:
- Current Implementation: {self.mode_context.get_architecture_summary()}
- Recent Changes: {self.mode_context.implementation_summary or 'No recent implementation'}

Debug Tasks:
1. Identify and analyze any bugs or issues in the current implementation
2. Review test failures and error logs
3. Use debugging tools and techniques to isolate problems
4. Provide specific fixes for identified issues
5. Verify fixes work correctly
6. Update tests to prevent regression
7. Document debugging process and solutions

Focus on systematic problem-solving and providing clear fixes.
Use all available debugging and testing tools.
"""
        
        debug_result = self.execute_agent_mode(ModeType.DEBUG, debug_prompt)
        print(f"🐛 Debug Analysis:\n{debug_result}")
    
    def _delegate_to_review_modes(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Use expert consultant and fact checker for comprehensive review"""
        
        # Expert technical review
        expert_prompt = f"""
Provide expert technical consultation for JIRA issue {issue_key} implementation.

Implementation Context:
- Architecture: {self.mode_context.get_architecture_summary()}
- Implementation: {self.mode_context.implementation_summary or 'No implementation summary available'}
- User Stories: {self.mode_context.get_user_stories()}

Expert Review Tasks:
1. Assess overall solution quality and approach
2. Identify security, performance, and scalability concerns
3. Review code quality, maintainability, and best practices
4. Validate alignment with architectural design
5. Recommend improvements and optimizations
6. Ensure compliance with project standards and guidelines
7. Provide expert recommendations for production readiness

Provide comprehensive expert feedback and specific recommendations.
"""
        
        expert_review = self.execute_agent_mode(ModeType.EXPERT_CONSULTANT, expert_prompt)
        
        # Fact checking for validation
        fact_check_prompt = f"""
Validate the technical claims and implementation accuracy for JIRA issue {issue_key}.

Items to Verify:
- Technical approach feasibility and correctness
- Implementation accuracy and completeness
- Security measures adequacy
- Performance expectations and optimizations
- Integration compatibility and reliability
- Best practices compliance

Expert Claims to Verify: {expert_review}

Systematically verify technical accuracy and flag any concerns or inaccuracies.
Provide fact-based validation of the implementation and recommendations.
"""
        
        fact_check_results = self.execute_agent_mode(ModeType.FACT_CHECKER, fact_check_prompt)
        
        self.mode_context.add_review_results(expert_review, fact_check_results)
        print(f"👨‍💼 Expert Review:\n{expert_review}")
        print(f"✅ Fact Check:\n{fact_check_results}")
    
    def _delegate_to_writer_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Use writer mode for documentation tasks"""
        
        writer_prompt = f"""
Create comprehensive documentation for JIRA issue {issue_key}: {issue_data['fields']['summary']}

Documentation Context:
- Implementation: {self.mode_context.implementation_summary or 'No implementation available'}
- Architecture: {self.mode_context.get_architecture_summary()}
- Expert Review: {self.mode_context.expert_review or 'No expert review available'}

Documentation Tasks:
1. Create API documentation for any new endpoints or interfaces
2. Write user guides and how-to documentation
3. Document deployment and configuration procedures
4. Create troubleshooting and maintenance guides
5. Update architectural documentation
6. Write clear code comments and inline documentation
7. Create changelog and release notes

Focus on creating clear, comprehensive documentation that will help users and developers.
Ensure documentation is accurate, up-to-date, and well-organized.
"""
        
        documentation_result = self.execute_agent_mode(ModeType.WRITER, writer_prompt)
        print(f"📝 Documentation Complete:\n{documentation_result}")
    
    def _delegate_to_devops_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Use devops mode for deployment and infrastructure tasks"""
        
        devops_prompt = f"""
Handle DevOps and deployment tasks for JIRA issue {issue_key}: {issue_data['fields']['summary']}

DevOps Context:
- Implementation: {self.mode_context.implementation_summary or 'No implementation available'}
- Architecture: {self.mode_context.get_architecture_summary()}

DevOps Tasks:
1. Configure deployment pipeline and automation
2. Set up monitoring, logging, and alerting for the new functionality
3. Plan and execute staging and production deployments
4. Configure infrastructure and environment requirements
5. Set up backup and disaster recovery procedures
6. Implement security and compliance measures
7. Create operational runbooks and procedures

Focus on production-ready deployment and operational excellence.
Ensure robust, scalable, and secure deployment processes.
"""
        
        devops_result = self.execute_agent_mode(ModeType.DEVOPS, devops_prompt)
        print(f"🚀 DevOps Configuration:\n{devops_result}")
    
    def _mode_based_completion(self, issue_key: str) -> None:
        """Complete the agent-flows workflow with comprehensive synthesis"""
        
        # Final synthesis of all results
        synthesis_prompt = f"""
Synthesize the complete workflow results for JIRA issue {issue_key}.

Workflow Results: {self.mode_context.get_all_results()}

Create a comprehensive summary of:
1. What was accomplished in each phase
2. Key decisions and their rationale
3. Implementation highlights and technical details
4. Quality assurance and validation results
5. Deployment readiness and next steps
6. Overall project impact and success metrics

Provide a clear, actionable summary of the completed work that can be used for:
- Project reporting and stakeholder communication
- Future reference and maintenance
- Team knowledge sharing
- JIRA issue closure documentation

Focus on professional, comprehensive synthesis of all workflow phases.
"""
        
        final_synthesis = self.execute_agent_mode(ModeType.SYNTHESIZER, synthesis_prompt)
        
        print(f"\n🎉 Agent-Flows Workflow Complete!")
        print(f"📊 Final Synthesis:\n{final_synthesis}")
        
        # Update JIRA with comprehensive results
        self._update_jira_with_mode_results(issue_key, final_synthesis)
        
        # Show execution summary
        self._show_execution_summary(issue_key)
    
    def _show_session_summary(self, issue_key: str) -> None:
        """Show summary of the current session"""
        
        print(f"\n📊 Session Summary for {issue_key}")
        print(f"🎭 Modes Executed: {len(self.orchestration_history)}")
        
        for i, execution in enumerate(self.orchestration_history, 1):
            print(f"   {i}. {execution['mode']} - {execution['timestamp']}")
        
        phase_results = self.mode_context.get_all_results()
        print(f"📋 Phases Completed: {len(phase_results)}")
        for phase, result in phase_results.items():
            print(f"   ✅ {phase}: {len(result)} characters")
    
    def _show_execution_summary(self, issue_key: str) -> None:
        """Show detailed execution summary"""
        
        print(f"\n📈 Execution Summary for {issue_key}")
        print(f"🎭 Total Mode Executions: {len(self.orchestration_history)}")
        print(f"⏱️  Total Execution Time: {self._calculate_total_time()}")
        print(f"📊 Success Rate: 100%")  # All executions succeeded if we got here
        
        print(f"\n🎯 Workflow Phases Completed:")
        for phase, result in self.mode_context.get_all_results().items():
            print(f"   ✅ {phase.replace('_', ' ').title()}: {len(result)} characters")
    
    def _show_agent_modes_help(self) -> None:
        """Show available agent mode commands and their descriptions"""
        
        help_text = """
🎭 Available Agent-Flows Modes:

📋 plan         - Review the orchestrator's master plan for this issue
🎭 orchestrate  - Strategic workflow coordination and next steps guidance
📖 story        - Break down requirements into user stories and acceptance criteria
🏗️  architect    - Design system architecture and technical approach
🔍 research     - Investigate technical solutions and best practices
🛠️  code         - Implement functionality with production-ready code
🐛 debug        - Debug issues and troubleshoot problems
👨‍💼 review       - Expert technical review and fact-checking validation
📝 write        - Create comprehensive documentation and guides
🚀 devops       - Configure deployment, monitoring, and operations
🏁 done         - Complete workflow with comprehensive synthesis
👋 quit         - Exit development mode and show session summary
📚 help         - Show this help message

Each mode leverages specialized agent-flows instructions and appropriate Claude Code tools.
The orchestrator coordinates the overall workflow and recommends next steps.
"""
        print(help_text)
    
    def _get_project_context(self) -> Dict[str, Any]:
        """Get current project context for mode execution"""
        
        context = {
            "type": "general",
            "repository": os.getcwd(),
            "framework": "unknown"
        }
        
        # Try to detect project type from files
        cwd = Path.cwd()
        if (cwd / "package.json").exists():
            context["type"] = "javascript"
            context["framework"] = "node"
        elif (cwd / "requirements.txt").exists() or (cwd / "pyproject.toml").exists():
            context["type"] = "python"
            
            # Check for specific frameworks
            if (cwd / "app.py").exists() or any(cwd.glob("**/app.py")):
                context["framework"] = "flask"
            elif (cwd / "main.py").exists() or any(cwd.glob("**/main.py")):
                context["framework"] = "fastapi"
            elif (cwd / "manage.py").exists():
                context["framework"] = "django"
                
        elif (cwd / "Cargo.toml").exists():
            context["type"] = "rust"
        elif (cwd / "go.mod").exists():
            context["type"] = "go"
        
        return context
    
    def _get_current_system_overview(self) -> str:
        """Get overview of current system architecture"""
        
        # This would ideally read from architecture docs or analyze the codebase
        return "Current system overview not available - analyze codebase to understand existing architecture"
    
    def _calculate_total_time(self) -> str:
        """Calculate total execution time from orchestration history"""
        
        if not self.orchestration_history:
            return "0 minutes"
        
        # Calculate approximate time based on number of mode executions
        # Each mode execution typically takes 2-5 minutes
        total_executions = len(self.orchestration_history)
        estimated_minutes = total_executions * 3  # Average of 3 minutes per execution
        
        return f"~{estimated_minutes} minutes"
    
    def _update_jira_with_mode_results(self, issue_key: str, synthesis: str) -> None:
        """Update JIRA issue with comprehensive mode-based workflow results"""
        
        # Create comprehensive comment with all results
        results_summary = "🎭 **Agent-Flows Workflow Complete**\n\n"
        results_summary += f"**Final Synthesis:**\n{synthesis[:1000]}...\n\n"
        
        results_summary += f"**Workflow Phases Completed:**\n"
        for phase, result in self.mode_context.get_all_results().items():
            results_summary += f"✅ {phase.replace('_', ' ').title()}\n"
        
        results_summary += f"\n**Mode Executions:** {len(self.orchestration_history)}\n"
        results_summary += f"**Success Rate:** 100%\n"
        results_summary += f"**Status:** Ready for review and deployment"
        
        # Add comment to JIRA
        self.jira_client.add_comment(issue_key, results_summary)
        
        print(f"💬 JIRA issue {issue_key} updated with comprehensive workflow results")