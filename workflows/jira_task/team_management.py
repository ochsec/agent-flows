#!/usr/bin/env python3
"""
Team Management and Collaboration Module - Phase 4

Provides team management, role-based access control, approval workflows,
and collaboration features for enterprise JIRA workflows.
"""

import os
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
import sqlite3

from .config import JiraConfig
from .jira_client import JiraClient


class Role(Enum):
    """User roles with different permissions"""
    ADMIN = "admin"
    TECH_LEAD = "tech_lead"
    SENIOR_DEV = "senior_dev"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class Permission(Enum):
    """Granular permissions"""
    START_WORKFLOW = "start_workflow"
    APPROVE_CHANGES = "approve_changes"
    DEPLOY_PRODUCTION = "deploy_production"
    MANAGE_TEAM = "manage_team"
    VIEW_ANALYTICS = "view_analytics"
    MODIFY_CONFIG = "modify_config"
    FORCE_MERGE = "force_merge"
    ACCESS_SENSITIVE = "access_sensitive"


@dataclass
class User:
    """User profile with role and permissions"""
    username: str
    email: str
    display_name: str
    role: Role
    team: str
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_active: Optional[datetime] = None
    permissions: Set[Permission] = field(default_factory=set)
    
    def __post_init__(self):
        # Set default permissions based on role
        self.permissions = self._get_default_permissions()
    
    def _get_default_permissions(self) -> Set[Permission]:
        """Get default permissions for role"""
        permission_map = {
            Role.ADMIN: {Permission.START_WORKFLOW, Permission.APPROVE_CHANGES, 
                        Permission.DEPLOY_PRODUCTION, Permission.MANAGE_TEAM,
                        Permission.VIEW_ANALYTICS, Permission.MODIFY_CONFIG, 
                        Permission.FORCE_MERGE, Permission.ACCESS_SENSITIVE},
            Role.TECH_LEAD: {Permission.START_WORKFLOW, Permission.APPROVE_CHANGES,
                           Permission.DEPLOY_PRODUCTION, Permission.VIEW_ANALYTICS,
                           Permission.FORCE_MERGE, Permission.ACCESS_SENSITIVE},
            Role.SENIOR_DEV: {Permission.START_WORKFLOW, Permission.APPROVE_CHANGES,
                            Permission.VIEW_ANALYTICS},
            Role.DEVELOPER: {Permission.START_WORKFLOW},
            Role.REVIEWER: {Permission.APPROVE_CHANGES, Permission.VIEW_ANALYTICS},
            Role.VIEWER: {Permission.VIEW_ANALYTICS}
        }
        return permission_map.get(self.role, set())
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions


@dataclass
class ApprovalRequest:
    """Approval request for workflow actions"""
    id: str
    requester: str
    action: str
    issue_key: str
    description: str
    created_at: datetime
    approvers_required: List[str]
    approvals_received: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, approved, rejected, expired
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_approved(self) -> bool:
        """Check if request has sufficient approvals"""
        return len(self.approvals_received) >= len(self.approvers_required)
    
    def is_expired(self) -> bool:
        """Check if request has expired"""
        return self.expires_at and datetime.now() > self.expires_at


@dataclass
class Team:
    """Team configuration and members"""
    name: str
    description: str
    lead: str
    members: List[str]
    projects: List[str] = field(default_factory=list)
    approval_rules: Dict[str, List[str]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class TeamManager:
    """Manages teams, users, and permissions"""
    
    def __init__(self, config_file: str = "team_config.yml"):
        self.config_file = config_file
        self.users: Dict[str, User] = {}
        self.teams: Dict[str, Team] = {}
        self.db_path = "team_management.db"
        self.init_database()
        self.load_configuration()
    
    def init_database(self):
        """Initialize team management database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    display_name TEXT,
                    role TEXT,
                    team TEXT,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP,
                    permissions TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    lead TEXT,
                    members TEXT,
                    projects TEXT,
                    approval_rules TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS approval_requests (
                    id TEXT PRIMARY KEY,
                    requester TEXT,
                    action TEXT,
                    issue_key TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approvers_required TEXT,
                    approvals_received TEXT,
                    status TEXT DEFAULT 'pending',
                    expires_at TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    action TEXT,
                    issue_key TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            ''')
    
    def load_configuration(self):
        """Load team configuration from YAML file"""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Load teams
                for team_name, team_data in config.get('teams', {}).items():
                    team = Team(
                        name=team_name,
                        description=team_data.get('description', ''),
                        lead=team_data.get('lead', ''),
                        members=team_data.get('members', []),
                        projects=team_data.get('projects', []),
                        approval_rules=team_data.get('approval_rules', {})
                    )
                    self.teams[team_name] = team
                
                # Load users
                for user_data in config.get('users', []):
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        display_name=user_data.get('display_name', user_data['username']),
                        role=Role(user_data['role']),
                        team=user_data.get('team', 'default')
                    )
                    self.users[user.username] = user
                    
            except Exception as e:
                print(f"Error loading team configuration: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default team configuration"""
        default_config = {
            'teams': {
                'backend': {
                    'description': 'Backend Development Team',
                    'lead': 'tech_lead',
                    'members': ['developer1', 'developer2'],
                    'projects': ['api', 'services'],
                    'approval_rules': {
                        'deploy_production': ['tech_lead'],
                        'force_merge': ['tech_lead', 'admin']
                    }
                },
                'frontend': {
                    'description': 'Frontend Development Team', 
                    'lead': 'frontend_lead',
                    'members': ['frontend_dev1', 'frontend_dev2'],
                    'projects': ['web', 'mobile'],
                    'approval_rules': {
                        'deploy_production': ['frontend_lead']
                    }
                }
            },
            'users': [
                {
                    'username': 'admin',
                    'email': 'admin@company.com',
                    'display_name': 'System Admin',
                    'role': 'admin',
                    'team': 'backend'
                },
                {
                    'username': 'tech_lead',
                    'email': 'tech.lead@company.com',
                    'display_name': 'Tech Lead',
                    'role': 'tech_lead',
                    'team': 'backend'
                }
            ]
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"Created default team configuration: {self.config_file}")
    
    def save_configuration(self):
        """Save current configuration to YAML file"""
        config = {
            'teams': {
                name: {
                    'description': team.description,
                    'lead': team.lead,
                    'members': team.members,
                    'projects': team.projects,
                    'approval_rules': team.approval_rules
                }
                for name, team in self.teams.items()
            },
            'users': [
                {
                    'username': user.username,
                    'email': user.email,
                    'display_name': user.display_name,
                    'role': user.role.value,
                    'team': user.team
                }
                for user in self.users.values() if user.active
            ]
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def add_user(self, username: str, email: str, display_name: str, role: Role, team: str) -> User:
        """Add new user to team"""
        user = User(
            username=username,
            email=email,
            display_name=display_name,
            role=role,
            team=team
        )
        
        self.users[username] = user
        
        # Add to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO users 
                (username, email, display_name, role, team, permissions)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user.username, user.email, user.display_name,
                user.role.value, user.team,
                json.dumps([p.value for p in user.permissions])
            ))
        
        self.save_configuration()
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)
    
    def check_permission(self, username: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        user = self.get_user(username)
        return user and user.has_permission(permission)
    
    def get_team_members(self, team_name: str) -> List[User]:
        """Get all active members of a team"""
        team = self.teams.get(team_name)
        if not team:
            return []
        
        return [
            user for user in self.users.values()
            if user.team == team_name and user.active
        ]
    
    def get_approvers_for_action(self, action: str, team_name: str) -> List[str]:
        """Get required approvers for specific action"""
        team = self.teams.get(team_name)
        if not team:
            return []
        
        # Check team-specific approval rules
        if action in team.approval_rules:
            return team.approval_rules[action]
        
        # Default approval rules
        if action == "deploy_production":
            return [team.lead]
        elif action == "force_merge":
            return [team.lead, "admin"]
        
        return []


class ApprovalWorkflow:
    """Manages approval workflows for sensitive actions"""
    
    def __init__(self, team_manager: TeamManager, jira_config: JiraConfig):
        self.team_manager = team_manager
        self.jira_client = JiraClient(jira_config)
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.load_pending_requests()
    
    def load_pending_requests(self):
        """Load pending approval requests from database"""
        with sqlite3.connect(self.team_manager.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM approval_requests WHERE status = 'pending'
            ''')
            
            for row in cursor.fetchall():
                request = ApprovalRequest(
                    id=row[0],
                    requester=row[1],
                    action=row[2],
                    issue_key=row[3],
                    description=row[4],
                    created_at=datetime.fromisoformat(row[5]),
                    approvers_required=json.loads(row[6]),
                    approvals_received=json.loads(row[7] or '[]'),
                    status=row[8],
                    expires_at=datetime.fromisoformat(row[9]) if row[9] else None,
                    metadata=json.loads(row[10] or '{}')
                )
                self.pending_requests[request.id] = request
    
    def request_approval(self, requester: str, action: str, issue_key: str, 
                        description: str, team_name: str, 
                        expires_hours: int = 24) -> str:
        """Request approval for sensitive action"""
        # Get required approvers
        approvers = self.team_manager.get_approvers_for_action(action, team_name)
        
        if not approvers:
            raise ValueError(f"No approvers configured for action: {action}")
        
        # Create approval request
        request_id = f"{action}_{issue_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        request = ApprovalRequest(
            id=request_id,
            requester=requester,
            action=action,
            issue_key=issue_key,
            description=description,
            created_at=datetime.now(),
            approvers_required=approvers,
            expires_at=expires_at
        )
        
        self.pending_requests[request_id] = request
        
        # Store in database
        with sqlite3.connect(self.team_manager.db_path) as conn:
            conn.execute('''
                INSERT INTO approval_requests 
                (id, requester, action, issue_key, description, approvers_required, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.id, request.requester, request.action, request.issue_key,
                request.description, json.dumps(request.approvers_required),
                request.expires_at.isoformat()
            ))
        
        # Notify approvers
        self._notify_approvers(request)
        
        return request_id
    
    def approve_request(self, request_id: str, approver: str) -> bool:
        """Approve a pending request"""
        request = self.pending_requests.get(request_id)
        if not request:
            return False
        
        if request.is_expired():
            request.status = "expired"
            return False
        
        if approver not in request.approvers_required:
            return False
        
        if approver not in request.approvals_received:
            request.approvals_received.append(approver)
        
        # Check if fully approved
        if request.is_approved():
            request.status = "approved"
            self._execute_approved_action(request)
        
        # Update database
        with sqlite3.connect(self.team_manager.db_path) as conn:
            conn.execute('''
                UPDATE approval_requests 
                SET approvals_received = ?, status = ?
                WHERE id = ?
            ''', (
                json.dumps(request.approvals_received),
                request.status,
                request_id
            ))
        
        return True
    
    def reject_request(self, request_id: str, approver: str, reason: str = "") -> bool:
        """Reject a pending request"""
        request = self.pending_requests.get(request_id)
        if not request:
            return False
        
        if approver not in request.approvers_required:
            return False
        
        request.status = "rejected"
        request.metadata["rejection_reason"] = reason
        request.metadata["rejected_by"] = approver
        
        # Update database
        with sqlite3.connect(self.team_manager.db_path) as conn:
            conn.execute('''
                UPDATE approval_requests 
                SET status = ?, metadata = ?
                WHERE id = ?
            ''', (
                request.status,
                json.dumps(request.metadata),
                request_id
            ))
        
        # Notify requester
        self._notify_rejection(request, approver, reason)
        
        return True
    
    def get_pending_requests(self, user: str = None) -> List[ApprovalRequest]:
        """Get pending requests for user or all"""
        requests = []
        
        for request in self.pending_requests.values():
            if request.status != "pending" or request.is_expired():
                continue
                
            if user and user not in request.approvers_required:
                continue
                
            requests.append(request)
        
        return sorted(requests, key=lambda r: r.created_at, reverse=True)
    
    def _notify_approvers(self, request: ApprovalRequest):
        """Notify approvers about new request"""
        # Add comment to JIRA issue
        comment = f"""🔐 Approval Required: {request.action}

Requested by: {request.requester}
Description: {request.description}
Approvers needed: {', '.join(request.approvers_required)}
Expires: {request.expires_at.strftime('%Y-%m-%d %H:%M:%S')}

Request ID: {request.id}"""
        
        try:
            self.jira_client.add_comment(request.issue_key, comment)
        except Exception as e:
            print(f"Failed to notify via JIRA: {e}")
    
    def _notify_rejection(self, request: ApprovalRequest, approver: str, reason: str):
        """Notify about request rejection"""
        comment = f"""❌ Approval Request Rejected

Action: {request.action}
Rejected by: {approver}
Reason: {reason}

Request ID: {request.id}"""
        
        try:
            self.jira_client.add_comment(request.issue_key, comment)
        except Exception as e:
            print(f"Failed to notify rejection via JIRA: {e}")
    
    def _execute_approved_action(self, request: ApprovalRequest):
        """Execute the approved action"""
        comment = f"""✅ Approval Request Approved

Action: {request.action}
Approved by: {', '.join(request.approvals_received)}
Ready to proceed with: {request.description}

Request ID: {request.id}"""
        
        try:
            self.jira_client.add_comment(request.issue_key, comment)
        except Exception as e:
            print(f"Failed to notify approval via JIRA: {e}")


class CollaborationFeatures:
    """Team collaboration and communication features"""
    
    def __init__(self, team_manager: TeamManager, jira_config: JiraConfig):
        self.team_manager = team_manager
        self.jira_client = JiraClient(jira_config)
    
    def get_team_workload(self, team_name: str) -> Dict[str, Any]:
        """Get current workload for team members"""
        team_members = self.team_manager.get_team_members(team_name)
        workload = {}
        
        for member in team_members:
            try:
                # Get assigned issues from JIRA
                issues = self.jira_client.get_user_issues(member.email)
                
                workload[member.username] = {
                    'display_name': member.display_name,
                    'role': member.role.value,
                    'active_issues': len([i for i in issues if i['status'] in ['In Progress', 'To Do']]),
                    'total_issues': len(issues),
                    'issues': issues[:5]  # Show top 5
                }
            except Exception as e:
                workload[member.username] = {
                    'display_name': member.display_name,
                    'role': member.role.value,
                    'error': str(e)
                }
        
        return workload
    
    def get_team_activity_summary(self, team_name: str, days: int = 7) -> Dict[str, Any]:
        """Get team activity summary"""
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.team_manager.db_path) as conn:
            cursor = conn.execute('''
                SELECT username, COUNT(*) as activity_count, 
                       MAX(timestamp) as last_activity
                FROM user_activity 
                WHERE timestamp > ? 
                GROUP BY username
                ORDER BY activity_count DESC
            ''', (since_date.isoformat(),))
            
            activity_data = {}
            for row in cursor.fetchall():
                username, count, last_activity = row
                user = self.team_manager.get_user(username)
                if user and user.team == team_name:
                    activity_data[username] = {
                        'display_name': user.display_name,
                        'activity_count': count,
                        'last_activity': last_activity
                    }
        
        return {
            'team': team_name,
            'period_days': days,
            'member_activity': activity_data,
            'total_team_activity': sum(data['activity_count'] for data in activity_data.values())
        }
    
    def log_user_activity(self, username: str, action: str, issue_key: str = None, details: str = None):
        """Log user activity for analytics"""
        with sqlite3.connect(self.team_manager.db_path) as conn:
            conn.execute('''
                INSERT INTO user_activity (username, action, issue_key, details)
                VALUES (?, ?, ?, ?)
            ''', (username, action, issue_key, details))
        
        # Update user last_active timestamp
        user = self.team_manager.get_user(username)
        if user:
            user.last_active = datetime.now()


def main():
    """Main entry point for team management"""
    import argparse
    from .config import load_jira_config
    
    parser = argparse.ArgumentParser(description="Team Management and Collaboration")
    parser.add_argument("command", choices=["add-user", "list-users", "list-teams", "pending-approvals", "workload"])
    parser.add_argument("--username", help="Username for user operations")
    parser.add_argument("--email", help="Email for new user")
    parser.add_argument("--role", choices=[r.value for r in Role], help="User role")
    parser.add_argument("--team", help="Team name")
    parser.add_argument("--config", help="Path to .env configuration file")
    
    args = parser.parse_args()
    
    try:
        team_manager = TeamManager()
        
        if args.command == "add-user":
            if not all([args.username, args.email, args.role, args.team]):
                print("❌ All fields required: --username, --email, --role, --team")
                return
            
            user = team_manager.add_user(
                args.username, args.email, args.username.title(),
                Role(args.role), args.team
            )
            print(f"✅ Added user: {user.display_name} ({user.role.value}) to team {user.team}")
        
        elif args.command == "list-users":
            print("👥 Team Users:")
            for user in team_manager.users.values():
                if user.active:
                    perms = len(user.permissions)
                    print(f"   {user.display_name} ({user.username}) - {user.role.value} - {user.team} - {perms} permissions")
        
        elif args.command == "list-teams":
            print("🏢 Teams:")
            for team in team_manager.teams.values():
                print(f"   {team.name}: {team.description}")
                print(f"      Lead: {team.lead}")
                print(f"      Members: {', '.join(team.members)}")
                print(f"      Projects: {', '.join(team.projects)}")
        
        elif args.command == "pending-approvals":
            if args.config:
                jira_config = load_jira_config(args.config)
                approval_workflow = ApprovalWorkflow(team_manager, jira_config)
                
                requests = approval_workflow.get_pending_requests(args.username)
                
                if requests:
                    print(f"📋 Pending Approval Requests ({len(requests)}):")
                    for req in requests:
                        print(f"   {req.id}: {req.action} for {req.issue_key}")
                        print(f"      Requested by: {req.requester}")
                        print(f"      Description: {req.description}")
                        print(f"      Expires: {req.expires_at}")
                else:
                    print("✅ No pending approval requests")
            else:
                print("❌ Config required for approval workflow")
        
        elif args.command == "workload":
            if not args.team:
                print("❌ Team name required (--team)")
                return
            
            if args.config:
                jira_config = load_jira_config(args.config)
                collab = CollaborationFeatures(team_manager, jira_config)
                
                workload = collab.get_team_workload(args.team)
                
                print(f"📊 Team {args.team} Workload:")
                for username, data in workload.items():
                    if 'error' in data:
                        print(f"   {data['display_name']}: Error - {data['error']}")
                    else:
                        print(f"   {data['display_name']} ({data['role']}): {data['active_issues']} active / {data['total_issues']} total")
            else:
                print("❌ Config required for workload analysis")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()