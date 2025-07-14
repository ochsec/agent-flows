#!/usr/bin/env python3
"""
Advanced Automation Features - Phase 3 Implementation

This module implements advanced automation features including CI/CD integration,
multi-project support, workflow templates, and team collaboration features.
"""

import os
import json
import yaml
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from .enhanced_workflow import EnhancedJiraWorkflow, WorkflowContext
from .config import JiraConfig
from .jira_client import JiraClient


class ProjectType(Enum):
    """Supported project types for workflow templates"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    REACT = "react"
    NEXTJS = "nextjs"
    DJANGO = "django"
    FLASK = "flask"
    FASTAPI = "fastapi"
    UNKNOWN = "unknown"


@dataclass
class ProjectConfig:
    """Configuration for multi-project support"""
    name: str
    type: ProjectType
    jira_project_key: str
    repository_url: str
    default_branch: str = "main"
    build_command: Optional[str] = None
    test_command: Optional[str] = None
    lint_command: Optional[str] = None
    deploy_command: Optional[str] = None
    ci_config_path: Optional[str] = None
    reviewers: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.reviewers is None:
            self.reviewers = []
        if self.labels is None:
            self.labels = []


class WorkflowTemplate:
    """Template for common development workflows"""
    
    def __init__(self, name: str, project_type: ProjectType):
        self.name = name
        self.project_type = project_type
        self.steps = []
        self.quality_checks = []
        self.automation_rules = {}
    
    def add_step(self, step_name: str, command: str, description: str):
        """Add a workflow step"""
        self.steps.append({
            "name": step_name,
            "command": command,
            "description": description
        })
    
    def add_quality_check(self, check_name: str, command: str, required: bool = True):
        """Add a quality check"""
        self.quality_checks.append({
            "name": check_name,
            "command": command,
            "required": required
        })
    
    def get_claude_prompt(self, issue_data: Dict[str, Any]) -> str:
        """Generate Claude Code prompt based on template"""
        prompt = f"""You are implementing a {self.project_type.value} solution for: {issue_data['summary']}

PROJECT TYPE: {self.project_type.value}
WORKFLOW TEMPLATE: {self.name}

STANDARD WORKFLOW STEPS:
"""
        for i, step in enumerate(self.steps, 1):
            prompt += f"{i}. {step['name']}: {step['description']}\n"
        
        prompt += f"""
QUALITY CHECKS TO PERFORM:
"""
        for check in self.quality_checks:
            required_text = "(REQUIRED)" if check['required'] else "(OPTIONAL)"
            prompt += f"- {check['name']}: {check['command']} {required_text}\n"
        
        prompt += f"""
Please follow this template while adapting to the specific requirements of the issue.
Focus on best practices for {self.project_type.value} development.
"""
        return prompt


class TemplateManager:
    """Manages workflow templates for different project types"""
    
    def __init__(self):
        self.templates = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default templates for common project types"""
        
        # Python/FastAPI Template
        python_template = WorkflowTemplate("FastAPI Development", ProjectType.FASTAPI)
        python_template.add_step("analysis", "analyze", "Analyze existing FastAPI structure and endpoints")
        python_template.add_step("implementation", "implement", "Implement new endpoints with proper error handling")
        python_template.add_step("testing", "test", "Create comprehensive tests using pytest")
        python_template.add_step("documentation", "document", "Update API documentation and docstrings")
        python_template.add_quality_check("pytest", "pytest --cov=. --cov-report=term-missing", True)
        python_template.add_quality_check("black", "black --check .", True)
        python_template.add_quality_check("flake8", "flake8 .", True)
        python_template.add_quality_check("mypy", "mypy .", False)
        self.templates[ProjectType.FASTAPI] = python_template
        
        # React/TypeScript Template
        react_template = WorkflowTemplate("React TypeScript Development", ProjectType.REACT)
        react_template.add_step("analysis", "analyze", "Analyze component structure and state management")
        react_template.add_step("implementation", "implement", "Implement components with TypeScript interfaces")
        react_template.add_step("testing", "test", "Create unit and integration tests with Jest/RTL")
        react_template.add_step("styling", "style", "Implement responsive styling with CSS modules")
        react_template.add_quality_check("typescript", "tsc --noEmit", True)
        react_template.add_quality_check("eslint", "eslint src/ --ext .ts,.tsx", True)
        react_template.add_quality_check("prettier", "prettier --check src/", True)
        react_template.add_quality_check("jest", "npm test -- --coverage --watchAll=false", True)
        self.templates[ProjectType.REACT] = react_template
        
        # Node.js/TypeScript Template
        node_template = WorkflowTemplate("Node.js TypeScript Development", ProjectType.TYPESCRIPT)
        node_template.add_step("analysis", "analyze", "Analyze existing Node.js architecture and modules")
        node_template.add_step("implementation", "implement", "Implement functionality with proper TypeScript types")
        node_template.add_step("testing", "test", "Create comprehensive tests with Jest or Mocha")
        node_template.add_step("integration", "integrate", "Test integration points and APIs")
        node_template.add_quality_check("typescript", "tsc --noEmit", True)
        node_template.add_quality_check("eslint", "eslint src/ --ext .ts", True)
        node_template.add_quality_check("prettier", "prettier --check src/", True)
        node_template.add_quality_check("jest", "npm test", True)
        self.templates[ProjectType.TYPESCRIPT] = node_template
    
    def get_template(self, project_type: ProjectType) -> Optional[WorkflowTemplate]:
        """Get template for project type"""
        return self.templates.get(project_type)
    
    def detect_project_type(self, repo_path: str = ".") -> ProjectType:
        """Auto-detect project type from repository structure"""
        repo_path_obj = Path(repo_path)
        
        # Check for package.json and framework indicators
        if (repo_path_obj / "package.json").exists():
            try:
                with open(repo_path_obj / "package.json") as f:
                    package_json = json.load(f)
                    deps = {**package_json.get("dependencies", {}), 
                           **package_json.get("devDependencies", {})}
                    
                    if "next" in deps:
                        return ProjectType.NEXTJS
                    elif "react" in deps:
                        return ProjectType.REACT
                    elif "typescript" in deps:
                        return ProjectType.TYPESCRIPT
                    else:
                        return ProjectType.JAVASCRIPT
            except:
                pass
        
        # Check for Python project indicators
        python_files = ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]
        if any((repo_path_obj / f).exists() for f in python_files):
            # Check for specific Python frameworks
            if (repo_path_obj / "manage.py").exists() or any(p.name == "django" for p in repo_path_obj.rglob("*")):
                return ProjectType.DJANGO
            elif any(p.name == "app.py" for p in repo_path_obj.rglob("*")) or "flask" in str(repo_path_obj):
                return ProjectType.FLASK
            elif any("fastapi" in str(p) for p in repo_path_obj.rglob("*.py")):
                return ProjectType.FASTAPI
            else:
                return ProjectType.PYTHON
        
        # Check for Java project indicators
        java_files = ["pom.xml", "build.gradle", "build.gradle.kts"]
        if any((repo_path_obj / f).exists() for f in java_files):
            return ProjectType.JAVA
        
        return ProjectType.UNKNOWN


class CIPipelineIntegration:
    """Integration with CI/CD pipelines"""
    
    def __init__(self, project_config: ProjectConfig):
        self.project_config = project_config
    
    def detect_ci_system(self) -> Optional[str]:
        """Detect CI/CD system in use"""
        ci_indicators = {
            ".github/workflows": "github_actions",
            ".gitlab-ci.yml": "gitlab_ci",
            ".travis.yml": "travis_ci",
            "Jenkinsfile": "jenkins",
            ".circleci/config.yml": "circle_ci",
            "azure-pipelines.yml": "azure_devops"
        }
        
        for indicator, system in ci_indicators.items():
            if Path(indicator).exists():
                return system
        
        return None
    
    def get_build_status(self, branch_name: str) -> Dict[str, Any]:
        """Get CI/CD build status for branch"""
        ci_system = self.detect_ci_system()
        
        if ci_system == "github_actions":
            return self._get_github_actions_status(branch_name)
        elif ci_system == "gitlab_ci":
            return self._get_gitlab_ci_status(branch_name)
        else:
            return {"status": "unknown", "system": ci_system}
    
    def _get_github_actions_status(self, branch_name: str) -> Dict[str, Any]:
        """Get GitHub Actions status"""
        try:
            cmd = ["gh", "run", "list", "--branch", branch_name, "--limit", "1", "--json", "status,conclusion"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            runs = json.loads(result.stdout)
            if runs:
                run = runs[0]
                return {
                    "status": run.get("status", "unknown"),
                    "conclusion": run.get("conclusion"),
                    "system": "github_actions"
                }
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass
        
        return {"status": "unknown", "system": "github_actions"}
    
    def _get_gitlab_ci_status(self, branch_name: str) -> Dict[str, Any]:
        """Get GitLab CI status (placeholder - would need GitLab API integration)"""
        return {"status": "not_implemented", "system": "gitlab_ci"}
    
    def trigger_deployment(self, environment: str) -> bool:
        """Trigger deployment to specified environment"""
        if self.project_config.deploy_command:
            try:
                cmd = self.project_config.deploy_command.replace("{environment}", environment)
                subprocess.run(cmd.split(), check=True)
                return True
            except subprocess.CalledProcessError:
                return False
        return False


class MultiProjectManager:
    """Manages multiple projects with different configurations"""
    
    def __init__(self, config_file: str = "jira_projects.yml"):
        self.config_file = config_file
        self.projects = {}
        self.load_projects()
    
    def load_projects(self):
        """Load project configurations from YAML file"""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = yaml.safe_load(f)
                    
                for project_name, config_data in data.get('projects', {}).items():
                    project_config = ProjectConfig(
                        name=project_name,
                        type=ProjectType(config_data.get('type', 'unknown')),
                        **{k: v for k, v in config_data.items() if k != 'type'}
                    )
                    self.projects[project_name] = project_config
            except Exception as e:
                print(f"Error loading project configurations: {e}")
    
    def save_projects(self):
        """Save project configurations to YAML file"""
        data = {
            'projects': {
                name: asdict(config) for name, config in self.projects.items()
            }
        }
        
        # Convert enum to string
        for project_data in data['projects'].values():
            if isinstance(project_data['type'], ProjectType):
                project_data['type'] = project_data['type'].value
        
        with open(self.config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def add_project(self, project_config: ProjectConfig):
        """Add a new project configuration"""
        self.projects[project_config.name] = project_config
        self.save_projects()
    
    def get_project(self, name: str) -> Optional[ProjectConfig]:
        """Get project configuration by name"""
        return self.projects.get(name)
    
    def detect_current_project(self) -> Optional[ProjectConfig]:
        """Detect current project based on repository URL or directory"""
        try:
            # Get git remote URL
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True, check=True)
            repo_url = result.stdout.strip()
            
            # Find matching project
            for project in self.projects.values():
                if project.repository_url in repo_url or repo_url in project.repository_url:
                    return project
        except subprocess.CalledProcessError:
            pass
        
        # Fallback: check directory name
        current_dir = Path.cwd().name
        return self.projects.get(current_dir)
    
    def list_projects(self) -> List[ProjectConfig]:
        """List all configured projects"""
        return list(self.projects.values())


class AdvancedJiraWorkflow(EnhancedJiraWorkflow):
    """Advanced JIRA workflow with Phase 3 features"""
    
    def __init__(self, jira_config: JiraConfig, repo_path: Optional[str] = None):
        super().__init__(jira_config, repo_path)
        
        # Phase 3 components
        self.project_manager = MultiProjectManager()
        self.template_manager = TemplateManager()
        self.current_project = self.project_manager.detect_current_project()
        self.ci_integration = None
        
        if self.current_project:
            self.ci_integration = CIPipelineIntegration(self.current_project)
            print(f"🎯 Detected project: {self.current_project.name} ({self.current_project.type.value})")
    
    def start_work_on_issue(self, issue_key: str) -> Dict[str, Any]:
        """Enhanced start workflow with project-specific templates"""
        result = super().start_work_on_issue(issue_key)
        
        if result["status"] == "success" and self.current_project:
            # Apply project-specific template
            template = self.template_manager.get_template(self.current_project.type)
            if template:
                result["template"] = template.name
                result["project_type"] = self.current_project.type.value
                print(f"📋 Using {template.name} workflow template")
        
        return result
    
    def advanced_analyze_codebase(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Advanced analysis with project-specific insights"""
        if not self.enhanced_claude:
            print("❌ Enhanced workflow not initialized. Use start command first.")
            return
        
        # Get project-specific template prompt
        template_prompt = ""
        if self.current_project:
            template = self.template_manager.get_template(self.current_project.type)
            if template:
                template_prompt = template.get_claude_prompt(issue_data)
        
        analyze_prompt = f"""Perform advanced project-specific analysis for {issue_key}: {issue_data['summary']}

PROJECT CONTEXT:
{f"Project: {self.current_project.name}" if self.current_project else "No project configuration detected"}
{f"Type: {self.current_project.type.value}" if self.current_project else ""}
{f"Repository: {self.current_project.repository_url}" if self.current_project else ""}

{template_prompt}

ADVANCED ANALYSIS REQUIREMENTS:
1. PROJECT STRUCTURE ANALYSIS:
   - Identify project architecture patterns
   - Analyze dependency management and build tools
   - Assess current development workflows

2. TECHNOLOGY-SPECIFIC CONSIDERATIONS:
   - Framework-specific best practices
   - Performance optimization opportunities
   - Security considerations for the technology stack

3. CI/CD INTEGRATION:
   - Check existing CI/CD pipeline configuration
   - Identify testing and deployment requirements
   - Assess impact on build and release processes

4. TEAM COLLABORATION:
   - Consider code review requirements
   - Identify stakeholders and reviewers
   - Assess documentation needs

Provide comprehensive analysis with specific recommendations for this project type."""
        
        result = self.enhanced_claude.execute_command(analyze_prompt, "analyze")
        print(f"🔍 Advanced Project Analysis:\n{result}")
    
    def check_ci_status(self, issue_key: str) -> None:
        """Check CI/CD pipeline status for current branch"""
        if not self.ci_integration:
            print("ℹ️  No CI/CD integration configured for this project")
            return
        
        current_branch = self.git.get_current_branch()
        status = self.ci_integration.get_build_status(current_branch)
        
        print(f"🔧 CI/CD Status for branch '{current_branch}':")
        print(f"   System: {status.get('system', 'unknown')}")
        print(f"   Status: {status.get('status', 'unknown')}")
        
        if status.get('conclusion'):
            print(f"   Result: {status['conclusion']}")
    
    def advanced_complete_with_deployment(self, issue_key: str, deploy_env: Optional[str] = None) -> None:
        """Advanced completion with optional deployment"""
        # Run standard completion
        self.enhanced_complete(issue_key)
        
        # Check CI status
        self.check_ci_status(issue_key)
        
        # Optional deployment
        if deploy_env and self.ci_integration:
            print(f"🚀 Triggering deployment to {deploy_env}...")
            success = self.ci_integration.trigger_deployment(deploy_env)
            if success:
                print(f"✅ Deployment to {deploy_env} initiated successfully")
                
                # Update JIRA with deployment info
                deploy_comment = f"🚀 Deployment initiated to {deploy_env} environment\n\nDeployment triggered automatically as part of workflow completion."
                self.jira_client.add_comment(issue_key, deploy_comment)
            else:
                print(f"❌ Failed to trigger deployment to {deploy_env}")
    
    def show_project_info(self) -> None:
        """Show current project information and configuration"""
        if not self.current_project:
            print("ℹ️  No project configuration detected")
            print("💡 To configure projects, create a jira_projects.yml file")
            return
        
        print(f"""
🎯 PROJECT INFORMATION:
   Name: {self.current_project.name}
   Type: {self.current_project.type.value}
   JIRA Project: {self.current_project.jira_project_key}
   Repository: {self.current_project.repository_url}
   Default Branch: {self.current_project.default_branch}

🔧 BUILD CONFIGURATION:
   Build: {self.current_project.build_command or 'Not configured'}
   Test: {self.current_project.test_command or 'Not configured'}
   Lint: {self.current_project.lint_command or 'Not configured'}
   Deploy: {self.current_project.deploy_command or 'Not configured'}

👥 TEAM SETTINGS:
   Reviewers: {', '.join(self.current_project.reviewers) if self.current_project.reviewers else 'None configured'}
   Labels: {', '.join(self.current_project.labels) if self.current_project.labels else 'None configured'}
""")
    
    def _advanced_interactive_development_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Advanced interactive mode with Phase 3 features"""
        
        while True:
            print("\n" + "="*70)
            
            # Show enhanced status
            status_line = f"Session: {len(self.workflow_context.command_history)} commands | Phase: {self.workflow_context.current_phase}"
            if self.current_project:
                status_line += f" | Project: {self.current_project.name}"
            print(status_line)
            
            user_input = input(f"\n👷 [{issue_key}] Command (help/analyze/implement/test/review/ci/deploy/project/done/quit): ").strip().lower()
            
            if user_input == 'quit':
                self._show_session_summary(issue_key)
                break
                
            elif user_input == 'done':
                deploy_env = input("Deploy to environment? (leave empty to skip): ").strip()
                self.advanced_complete_with_deployment(issue_key, deploy_env if deploy_env else None)
                break
                
            elif user_input == 'help':
                self.show_advanced_help()
                
            elif user_input == 'analyze':
                self.advanced_analyze_codebase(issue_key, issue_data)
                
            elif user_input == 'implement':
                self.enhanced_implement(issue_key, issue_data)
                
            elif user_input == 'test':
                self.enhanced_test(issue_key, issue_data)
                
            elif user_input == 'review':
                self.enhanced_review(issue_key)
                
            elif user_input == 'ci':
                self.check_ci_status(issue_key)
                
            elif user_input == 'deploy':
                env = input("Enter deployment environment: ").strip()
                if env and self.ci_integration:
                    success = self.ci_integration.trigger_deployment(env)
                    print(f"{'✅' if success else '❌'} Deployment {'initiated' if success else 'failed'}")
                
            elif user_input == 'project':
                self.show_project_info()
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
    
    def show_advanced_help(self) -> None:
        """Show advanced help with Phase 3 commands"""
        help_text = f"""
📚 ADVANCED JIRA WORKFLOW COMMANDS (Phase 3):

🔍 analyze    - Advanced project-specific codebase analysis
🛠️  implement  - Template-guided implementation with best practices
🧪 test       - Comprehensive testing with CI/CD integration
🔍 review     - Professional code review with quality gates
🔧 ci         - Check CI/CD pipeline status and build results
🚀 deploy     - Trigger deployment to specified environment
🎯 project    - Show current project configuration and settings
🏁 done       - Complete workflow with optional deployment
👋 quit       - Exit with detailed session analytics

🎯 PHASE 3 ENHANCED FEATURES:
- Multi-project support with auto-detection
- Project-specific workflow templates
- CI/CD pipeline integration and monitoring
- Automated deployment capabilities
- Advanced analytics and reporting
- Team collaboration tools

Current Project: {self.current_project.name if self.current_project else 'None detected'}
Template: {self.template_manager.get_template(self.current_project.type).name if self.current_project and self.template_manager.get_template(self.current_project.type) else 'Generic'}
CI/CD: {self.ci_integration.detect_ci_system() if self.ci_integration else 'Not detected'}"""
        
        print(help_text)
    
    def execute_development_workflow(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Execute advanced development workflow with Phase 3 features"""
        if not self.enhanced_claude:
            print("❌ Enhanced workflow not initialized properly.")
            return
            
        print("\n🚀 Advanced development workflow ready!")
        print("✨ Phase 3 Features: Multi-project support, CI/CD integration, automated deployment")
        
        # Show project and template info
        if self.current_project:
            template = self.template_manager.get_template(self.current_project.type)
            print(f"🎯 Project: {self.current_project.name} ({self.current_project.type.value})")
            if template:
                print(f"📋 Template: {template.name}")
        
        # Enter advanced interactive mode
        self._advanced_interactive_development_mode(issue_key, issue_data)


if __name__ == "__main__":
    # Example usage for testing
    print("Advanced JIRA Workflow - Phase 3")
    print("Features: Multi-project support, CI/CD integration, workflow templates")