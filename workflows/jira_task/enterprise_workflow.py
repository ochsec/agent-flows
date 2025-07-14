#!/usr/bin/env python3
"""
Enterprise Workflow - Phase 4 Implementation

Integrates all Phase 4 enterprise features including webhooks, AI code review,
team management, approval workflows, and external integrations.
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path

from .config import JiraConfig
from .advanced_automation import AdvancedJiraWorkflow
from .webhook_integration import WebhookProcessor, WebhookServer
from .ai_code_review import AICodeReviewer
from .team_management import TeamManager, ApprovalWorkflow, CollaborationFeatures, Permission
from .external_integrations import NotificationOrchestrator
from .analytics import WorkflowAnalytics


class EnterpriseJiraWorkflow(AdvancedJiraWorkflow):
    """Enterprise JIRA workflow with Phase 4 features"""
    
    def __init__(self, jira_config: JiraConfig, repo_path: Optional[str] = None, 
                 current_user: str = None):
        super().__init__(jira_config, repo_path)
        
        # Phase 4 Enterprise Components
        self.team_manager = TeamManager()
        self.approval_workflow = ApprovalWorkflow(self.team_manager, jira_config)
        self.collaboration = CollaborationFeatures(self.team_manager, jira_config)
        self.notifications = NotificationOrchestrator(self.team_manager, jira_config)
        self.ai_reviewer = AICodeReviewer(jira_config)
        self.workflow_analytics = WorkflowAnalytics()
        
        # User context
        self.current_user = current_user or os.getenv("USER", "unknown")
        self.user = self.team_manager.get_user(self.current_user)
        
        print(f"🏢 Enterprise workflow initialized for user: {self.current_user}")
        if self.user:
            print(f"👤 Role: {self.user.role.value} | Team: {self.user.team}")
    
    def start_work_on_issue(self, issue_key: str) -> Dict[str, Any]:
        """Enhanced start workflow with enterprise features"""
        # Check permissions
        if not self._check_permission(Permission.START_WORKFLOW):
            return {
                "status": "error",
                "message": "Insufficient permissions to start workflow"
            }
        
        # Start analytics session
        analytics_session = self.workflow_analytics.start_session(
            issue_key, 
            self.current_project.name if self.current_project else "default",
            self.current_project.type.value if self.current_project else "unknown",
            self.current_user
        )
        
        # Call parent implementation
        result = super().start_work_on_issue(issue_key)
        
        if result["status"] == "success":
            # Log activity
            self.collaboration.log_user_activity(
                self.current_user, "start_workflow", issue_key,
                f"Started workflow for {result['issue']['summary']}"
            )
            
            # Send notifications
            self.notifications.notify_workflow_started(
                issue_key, self.current_user,
                result['issue']['summary'],
                result['branch']
            )
            
            result["analytics_session"] = analytics_session
            result["enterprise_features"] = True
        
        return result
    
    def enterprise_code_review(self, issue_key: str) -> Dict[str, Any]:
        """Perform enterprise-grade AI code review"""
        print("🔍 Starting enterprise AI code review...")
        
        # Check permissions
        if not self._check_permission(Permission.APPROVE_CHANGES):
            print("⚠️  Limited review capabilities due to permissions")
        
        # Perform AI code review
        review_result = self.ai_reviewer.review_changes(issue_key)
        
        # Log activity
        self.collaboration.log_user_activity(
            self.current_user, "code_review", issue_key,
            f"Performed AI code review: {review_result['total_issues']} issues found"
        )
        
        # Check if approval required for critical issues
        critical_issues = [
            issue for issue in review_result['issues'] 
            if issue['severity'] in ['critical', 'high']
        ]
        
        if critical_issues and self._has_permission(Permission.APPROVE_CHANGES):
            # Request approval for deployment if critical issues found
            approvers = self.team_manager.get_approvers_for_action(
                "deploy_with_issues", 
                self.user.team if self.user else "default"
            )
            
            if approvers:
                approval_id = self.approval_workflow.request_approval(
                    self.current_user,
                    "deploy_with_issues", 
                    issue_key,
                    f"Deployment with {len(critical_issues)} critical issues",
                    self.user.team if self.user else "default"
                )
                
                review_result["approval_required"] = approval_id
                
                # Notify approvers
                self.notifications.notify_approval_required(
                    issue_key, "deploy_with_issues", self.current_user, approvers, approval_id
                )
        
        return review_result
    
    def request_deployment_approval(self, issue_key: str, environment: str) -> str:
        """Request approval for deployment to environment"""
        if not self._check_permission(Permission.DEPLOY_PRODUCTION):
            raise PermissionError("Insufficient permissions for deployment")
        
        team_name = self.user.team if self.user else "default"
        
        approval_id = self.approval_workflow.request_approval(
            self.current_user,
            f"deploy_{environment}",
            issue_key,
            f"Deploy to {environment} environment",
            team_name,
            expires_hours=48 if environment == "production" else 24
        )
        
        # Get approvers and notify
        approvers = self.team_manager.get_approvers_for_action(
            f"deploy_{environment}", team_name
        )
        
        self.notifications.notify_deployment_ready(issue_key, environment, approvers)
        
        return approval_id
    
    def enterprise_complete(self, issue_key: str, deploy_env: str = None) -> None:
        """Complete workflow with enterprise features"""
        print("🏁 Completing enterprise workflow...")
        
        # Perform final code review
        review_result = self.enterprise_code_review(issue_key)
        
        # Check if deployment approval needed
        approval_id = None
        if deploy_env:
            try:
                approval_id = self.request_deployment_approval(issue_key, deploy_env)
                print(f"🔐 Deployment approval requested: {approval_id}")
            except PermissionError as e:
                print(f"⚠️  {e}")
                deploy_env = None
        
        # Complete with standard workflow
        if deploy_env and approval_id:
            # Wait for approval or proceed based on permissions
            pending_requests = self.approval_workflow.get_pending_requests(self.current_user)
            if any(req.id == approval_id for req in pending_requests):
                print("⏳ Waiting for deployment approval...")
                print("   Use 'approve' command to continue when approved")
                return
        
        # Complete workflow
        if deploy_env:
            self.advanced_complete_with_deployment(issue_key, deploy_env)
        else:
            self.enhanced_complete(issue_key)
        
        # Send completion notifications
        team_name = self.user.team if self.user else "default"
        self.notifications.notify_workflow_completed(issue_key, self.current_user, team_name)
        
        # End analytics session
        self.workflow_analytics.end_session(
            f"{issue_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            success=True,
            pr_created=True,
            deployment_triggered=bool(deploy_env)
        )
        
        print("✅ Enterprise workflow completed successfully!")
    
    def show_team_dashboard(self) -> None:
        """Show enterprise team dashboard"""
        print("\n🏢 ENTERPRISE TEAM DASHBOARD")
        print("=" * 60)
        
        # Team workload
        if self.user:
            workload = self.collaboration.get_team_workload(self.user.team)
            print(f"\n👥 Team {self.user.team.upper()} Workload:")
            for username, data in workload.items():
                if 'error' not in data:
                    print(f"   {data['display_name']} ({data['role']}): {data['active_issues']} active")
        
        # Pending approvals
        pending_approvals = self.approval_workflow.get_pending_requests(self.current_user)
        print(f"\n🔐 Pending Approvals ({len(pending_approvals)}):")
        for req in pending_approvals[:5]:
            print(f"   {req.id}: {req.action} for {req.issue_key}")
            print(f"      Requested by: {req.requester}")
            print(f"      Expires: {req.expires_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Analytics quick stats
        if self.current_project:
            stats = self.workflow_analytics.get_quick_stats(self.current_project.name)
            print(f"\n📊 Project Analytics (Last 7 days):")
            for key, value in stats.items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
        
        # Notification stats
        notification_stats = self.notifications.get_notification_stats()
        print(f"\n📢 Notifications (Last 7 days): {notification_stats['total_notifications']}")
        for channel, data in notification_stats['channel_stats'].items():
            print(f"   {channel}: {data['success_rate']:.1f}% success rate")
    
    def _check_permission(self, permission: Permission) -> bool:
        """Check if current user has permission"""
        return self.team_manager.check_permission(self.current_user, permission)
    
    def _has_permission(self, permission: Permission) -> bool:
        """Alias for _check_permission"""
        return self._check_permission(permission)
    
    def _enterprise_interactive_development_mode(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Enterprise interactive mode with Phase 4 features"""
        
        while True:
            print("\n" + "="*80)
            
            # Enhanced status line
            status_line = f"Session: {len(self.workflow_context.command_history)} commands | Phase: {self.workflow_context.current_phase}"
            if self.current_project:
                status_line += f" | Project: {self.current_project.name}"
            if self.user:
                status_line += f" | User: {self.user.display_name} ({self.user.role.value})"
            print(status_line)
            
            # Show pending approvals if any
            pending_approvals = self.approval_workflow.get_pending_requests(self.current_user)
            if pending_approvals:
                print(f"🔐 You have {len(pending_approvals)} pending approval(s)")
            
            user_input = input(f"\n👷 [{issue_key}] Enterprise Command (help/analyze/implement/test/review/approve/dashboard/ci/deploy/done/quit): ").strip().lower()
            
            if user_input == 'quit':
                self._show_session_summary(issue_key)
                break
                
            elif user_input == 'done':
                deploy_env = input("Deploy to environment? (dev/staging/production or leave empty): ").strip()
                self.enterprise_complete(issue_key, deploy_env if deploy_env else None)
                break
                
            elif user_input == 'help':
                self.show_enterprise_help()
                
            elif user_input == 'analyze':
                self.advanced_analyze_codebase(issue_key, issue_data)
                
            elif user_input == 'implement':
                self.enhanced_implement(issue_key, issue_data)
                
            elif user_input == 'test':
                self.enhanced_test(issue_key, issue_data)
                
            elif user_input == 'review':
                result = self.enterprise_code_review(issue_key)
                print(f"🔍 Code Review Complete: {result['total_issues']} issues found")
                print(f"🔒 Security Score: {result['metrics'].security_score:.1f}/100")
                print(f"⭐ Quality Score: {result['metrics'].quality_score:.1f}/100")
                
            elif user_input == 'approve':
                self._handle_approvals()
                
            elif user_input == 'dashboard':
                self.show_team_dashboard()
                
            elif user_input == 'ci':
                self.check_ci_status(issue_key)
                
            elif user_input == 'deploy':
                env = input("Enter deployment environment (dev/staging/production): ").strip()
                if env:
                    try:
                        approval_id = self.request_deployment_approval(issue_key, env)
                        print(f"🔐 Deployment approval requested: {approval_id}")
                    except PermissionError as e:
                        print(f"❌ {e}")
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
    
    def _handle_approvals(self):
        """Handle pending approval requests"""
        pending_requests = self.approval_workflow.get_pending_requests(self.current_user)
        
        if not pending_requests:
            print("✅ No pending approval requests")
            return
        
        print(f"\n🔐 Pending Approval Requests ({len(pending_requests)}):")
        for i, req in enumerate(pending_requests):
            print(f"{i+1}. {req.action} for {req.issue_key}")
            print(f"   Requested by: {req.requester}")
            print(f"   Description: {req.description}")
            print(f"   Expires: {req.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            choice = input("\nSelect request number to approve/reject (or 'cancel'): ").strip()
            if choice.lower() == 'cancel':
                return
            
            request_idx = int(choice) - 1
            if 0 <= request_idx < len(pending_requests):
                request = pending_requests[request_idx]
                
                action = input("Approve or Reject? (a/r): ").strip().lower()
                if action == 'a':
                    success = self.approval_workflow.approve_request(request.id, self.current_user)
                    print(f"{'✅ Approved' if success else '❌ Failed to approve'}")
                elif action == 'r':
                    reason = input("Rejection reason: ").strip()
                    success = self.approval_workflow.reject_request(request.id, self.current_user, reason)
                    print(f"{'❌ Rejected' if success else '❌ Failed to reject'}")
                
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    
    def show_enterprise_help(self) -> None:
        """Show enterprise help with Phase 4 commands"""
        help_text = f"""
📚 ENTERPRISE JIRA WORKFLOW COMMANDS (Phase 4):

🔍 analyze     - Advanced project-specific codebase analysis
🛠️  implement   - Template-guided implementation with best practices
🧪 test        - Comprehensive testing with CI/CD integration
🔍 review      - Enterprise AI-powered code review with security scanning
🔐 approve     - Handle pending approval requests
🏢 dashboard   - Show enterprise team dashboard and analytics
🔧 ci          - Check CI/CD pipeline status and build results
🚀 deploy      - Request deployment approval and trigger deployment
🏁 done        - Complete enterprise workflow with approvals
👋 quit        - Exit with detailed session analytics

🏢 PHASE 4 ENTERPRISE FEATURES:
- AI-powered security and quality code review
- Role-based access control and approval workflows
- Team collaboration and workload management
- Real-time notifications (Slack, Teams, Email)
- Comprehensive analytics and reporting
- Webhook integration for automated triggers

Current User: {self.current_user} ({self.user.role.value if self.user else 'Unknown'})
Team: {self.user.team if self.user else 'None'}
Permissions: {len(self.user.permissions) if self.user else 0}"""
        
        print(help_text)
    
    def execute_development_workflow(self, issue_key: str, issue_data: Dict[str, Any]) -> None:
        """Execute enterprise development workflow with Phase 4 features"""
        if not self.enhanced_claude:
            print("❌ Enhanced workflow not initialized properly.")
            return
            
        print("\n🏢 Enterprise development workflow ready!")
        print("✨ Phase 4 Features: AI code review, team management, approval workflows, notifications")
        
        # Show project and template info
        if self.current_project:
            template = self.template_manager.get_template(self.current_project.type)
            print(f"🎯 Project: {self.current_project.name} ({self.current_project.type.value})")
            if template:
                print(f"📋 Template: {template.name}")
        
        # Show user context
        if self.user:
            print(f"👤 User: {self.user.display_name} ({self.user.role.value}) | Team: {self.user.team}")
        
        # Enter enterprise interactive mode
        self._enterprise_interactive_development_mode(issue_key, issue_data)


def main():
    """Main entry point for enterprise workflow"""
    import argparse
    from .config import load_jira_config
    
    parser = argparse.ArgumentParser(description="Enterprise JIRA Workflow - Phase 4")
    parser.add_argument("issue_key", help="JIRA issue key to work on")
    parser.add_argument("--command", "-c", 
                       choices=["start", "review", "approve", "dashboard", "webhook-server"],
                       default="start",
                       help="Command to execute")
    parser.add_argument("--user", help="Current user (defaults to $USER)")
    parser.add_argument("--config", help="Path to .env configuration file")
    parser.add_argument("--webhook-port", type=int, default=8080, help="Webhook server port")
    
    args = parser.parse_args()
    
    try:
        config = load_jira_config(args.config)
        current_user = args.user or os.getenv("USER", "unknown")
        
        if args.command == "webhook-server":
            # Start webhook server
            from .webhook_integration import WebhookServer
            server = WebhookServer(config, args.webhook_port)
            server.run(debug=False)
            return
        
        workflow = EnterpriseJiraWorkflow(config, current_user=current_user)
        
        if args.command == "start":
            result = workflow.start_work_on_issue(args.issue_key)
            if result["status"] == "success":
                print("\n🤖 Launching Enterprise Claude Code development assistant...")
                workflow.execute_development_workflow(args.issue_key, result['issue'])
        
        elif args.command == "review":
            result = workflow.enterprise_code_review(args.issue_key)
            print(f"\n🎯 Enterprise Code Review Complete!")
            print(f"📊 Files: {result['files_analyzed']}, Issues: {result['total_issues']}")
            print(f"🔒 Security: {result['metrics'].security_score:.1f}/100")
            print(f"⭐ Quality: {result['metrics'].quality_score:.1f}/100")
            
            if result.get('approval_required'):
                print(f"🔐 Approval required: {result['approval_required']}")
        
        elif args.command == "approve":
            workflow._handle_approvals()
        
        elif args.command == "dashboard":
            workflow.show_team_dashboard()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()