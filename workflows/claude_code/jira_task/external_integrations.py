#!/usr/bin/env python3
"""
External Integrations Module - Phase 4

Provides integrations with external tools and services like Slack, Microsoft Teams,
email notifications, calendar integration, and other enterprise tools.
"""

import os
import json
import asyncio
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests
import sqlite3

from .config import JiraConfig
from .jira_client import JiraClient
from .team_management import TeamManager, User


@dataclass
class NotificationTemplate:
    """Template for notifications"""
    name: str
    subject: str
    body: str
    channels: List[str]  # ['email', 'slack', 'teams']
    trigger: str  # Event that triggers this notification


class SlackIntegration:
    """Slack integration for team notifications"""
    
    def __init__(self, webhook_url: Optional[str] = None, bot_token: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.base_url = "https://slack.com/api"
    
    def send_message(self, channel: str, message: str, blocks: List[Dict] = None) -> bool:
        """Send message to Slack channel"""
        if not self.webhook_url and not self.bot_token:
            print("⚠️  Slack not configured (missing webhook URL or bot token)")
            return False
        
        try:
            if self.webhook_url:
                return self._send_webhook_message(message, blocks)
            else:
                return self._send_api_message(channel, message, blocks)
        except Exception as e:
            print(f"❌ Failed to send Slack message: {e}")
            return False
    
    def _send_webhook_message(self, message: str, blocks: List[Dict] = None) -> bool:
        """Send message via webhook"""
        payload = {"text": message}
        if blocks:
            payload["blocks"] = blocks
        
        response = requests.post(self.webhook_url, json=payload)
        return response.status_code == 200
    
    def _send_api_message(self, channel: str, message: str, blocks: List[Dict] = None) -> bool:
        """Send message via Slack API"""
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": channel,
            "text": message
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        response = requests.post(f"{self.base_url}/chat.postMessage", 
                               headers=headers, json=payload)
        return response.status_code == 200
    
    def create_workflow_notification_blocks(self, event_type: str, issue_key: str, 
                                          user: str, details: Dict[str, Any]) -> List[Dict]:
        """Create rich Slack blocks for workflow notifications"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 JIRA Workflow: {event_type}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Issue:* {issue_key}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*User:* {user}"
                    }
                ]
            }
        ]
        
        if details.get('summary'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": f"*Summary:* {details['summary']}"
                }
            })
        
        if details.get('branch'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Branch:* `{details['branch']}`"
                }
            })
        
        # Add action buttons for approvals
        if event_type == "Approval Required":
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve"
                        },
                        "style": "primary",
                        "action_id": f"approve_{details.get('request_id')}"
                    },
                    {
                        "type": "button", 
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "action_id": f"reject_{details.get('request_id')}"
                    }
                ]
            })
        
        return blocks


class TeamsIntegration:
    """Microsoft Teams integration"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("TEAMS_WEBHOOK_URL")
    
    def send_message(self, title: str, message: str, details: Dict[str, Any] = None) -> bool:
        """Send message to Teams channel"""
        if not self.webhook_url:
            print("⚠️  Teams not configured (missing webhook URL)")
            return False
        
        try:
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": title,
                "sections": [
                    {
                        "activityTitle": title,
                        "activitySubtitle": message,
                        "facts": []
                    }
                ]
            }
            
            # Add details as facts
            if details:
                for key, value in details.items():
                    payload["sections"][0]["facts"].append({
                        "name": key.replace('_', ' ').title(),
                        "value": str(value)
                    })
            
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Failed to send Teams message: {e}")
            return False


class EmailIntegration:
    """Email notification integration"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587,
                 username: str = None, password: str = None):
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.username = username or os.getenv("SMTP_USERNAME")
        self.password = password or os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.username)
    
    def send_email(self, to_emails: List[str], subject: str, body: str, 
                   html_body: str = None) -> bool:
        """Send email notification"""
        if not all([self.smtp_server, self.username, self.password]):
            print("⚠️  Email not configured (missing SMTP settings)")
            return False
        
        try:
            msg = MimeMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add text body
            text_part = MimeText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MimeText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def create_workflow_email(self, event_type: str, issue_key: str, 
                            user: str, details: Dict[str, Any]) -> tuple[str, str]:
        """Create email content for workflow events"""
        subject = f"JIRA Workflow: {event_type} - {issue_key}"
        
        body = f"""
JIRA Workflow Notification

Event: {event_type}
Issue: {issue_key}
User: {user}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        for key, value in details.items():
            body += f"{key.replace('_', ' ').title()}: {value}\n"
        
        body += "\n---\nThis is an automated notification from the JIRA Workflow system."
        
        return subject, body


class CalendarIntegration:
    """Calendar integration for scheduling and reminders"""
    
    def __init__(self, calendar_type: str = "google"):
        self.calendar_type = calendar_type
        # In a real implementation, this would initialize calendar API clients
    
    def schedule_review_reminder(self, issue_key: str, reviewer_email: str, 
                               review_date: datetime) -> bool:
        """Schedule calendar reminder for code review"""
        # Placeholder for calendar integration
        print(f"📅 Calendar reminder scheduled: Code review for {issue_key} on {review_date}")
        return True
    
    def schedule_deployment_window(self, issue_key: str, deployment_time: datetime,
                                 duration_hours: int = 2) -> bool:
        """Schedule deployment window in team calendar"""
        print(f"📅 Deployment window scheduled: {issue_key} at {deployment_time} ({duration_hours}h)")
        return True


class NotificationOrchestrator:
    """Orchestrates notifications across all channels"""
    
    def __init__(self, team_manager: TeamManager, jira_config: JiraConfig):
        self.team_manager = team_manager
        self.jira_client = JiraClient(jira_config)
        
        # Initialize integrations
        self.slack = SlackIntegration()
        self.teams = TeamsIntegration()
        self.email = EmailIntegration()
        self.calendar = CalendarIntegration()
        
        # Load notification templates
        self.templates = self._load_notification_templates()
        
        # Database for tracking notifications
        self.db_path = "notifications.db"
        self.init_database()
    
    def init_database(self):
        """Initialize notifications database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notifications_sent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    issue_key TEXT,
                    recipient TEXT,
                    channel TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    details TEXT
                )
            ''')
    
    def _load_notification_templates(self) -> Dict[str, NotificationTemplate]:
        """Load notification templates"""
        templates = {
            'workflow_started': NotificationTemplate(
                name='workflow_started',
                subject='🚀 Workflow Started: {issue_key}',
                body='Development workflow has been started for {issue_key}: {summary}',
                channels=['slack'],
                trigger='workflow_start'
            ),
            'approval_required': NotificationTemplate(
                name='approval_required',
                subject='🔐 Approval Required: {issue_key}',
                body='Action "{action}" requires approval for {issue_key}. Requested by {requester}.',
                channels=['slack', 'email'],
                trigger='approval_request'
            ),
            'pr_created': NotificationTemplate(
                name='pr_created',
                subject='🔗 Pull Request Created: {issue_key}',
                body='Pull request has been created for {issue_key}: {pr_url}',
                channels=['slack'],
                trigger='pr_created'
            ),
            'deployment_ready': NotificationTemplate(
                name='deployment_ready',
                subject='🚀 Ready for Deployment: {issue_key}',
                body='Code review completed. {issue_key} is ready for deployment to {environment}.',
                channels=['slack', 'teams', 'email'],
                trigger='deployment_ready'
            ),
            'workflow_completed': NotificationTemplate(
                name='workflow_completed',
                subject='✅ Workflow Completed: {issue_key}',
                body='Development workflow completed for {issue_key}. Changes have been merged.',
                channels=['slack'],
                trigger='workflow_complete'
            )
        }
        return templates
    
    def send_notification(self, event_type: str, issue_key: str, 
                         recipients: List[str], **kwargs) -> Dict[str, bool]:
        """Send notification to specified recipients"""
        template = self.templates.get(event_type)
        if not template:
            print(f"⚠️  No template found for event: {event_type}")
            return {}
        
        results = {}
        
        # Format message content
        try:
            subject = template.subject.format(issue_key=issue_key, **kwargs)
            body = template.body.format(issue_key=issue_key, **kwargs)
        except KeyError as e:
            print(f"❌ Missing template variable: {e}")
            return {}
        
        # Send to each channel
        for channel in template.channels:
            channel_results = self._send_to_channel(
                channel, subject, body, issue_key, recipients, event_type, kwargs
            )
            results.update(channel_results)
        
        return results
    
    def _send_to_channel(self, channel: str, subject: str, body: str, 
                        issue_key: str, recipients: List[str], 
                        event_type: str, details: Dict[str, Any]) -> Dict[str, bool]:
        """Send notification to specific channel"""
        results = {}
        
        if channel == 'slack':
            # Send to Slack
            blocks = self.slack.create_workflow_notification_blocks(
                event_type.replace('_', ' ').title(), issue_key, 
                details.get('user', 'System'), details
            )
            
            success = self.slack.send_message(
                channel=os.getenv("SLACK_CHANNEL", "#jira-workflow"),
                message=body,
                blocks=blocks
            )
            results[f'slack'] = success
            
            # Log notification
            self._log_notification(event_type, issue_key, 'slack_channel', 'slack', success, details)
        
        elif channel == 'teams':
            # Send to Teams
            success = self.teams.send_message(subject, body, details)
            results[f'teams'] = success
            
            self._log_notification(event_type, issue_key, 'teams_channel', 'teams', success, details)
        
        elif channel == 'email':
            # Send emails to recipients
            recipient_emails = self._get_recipient_emails(recipients)
            if recipient_emails:
                email_subject, email_body = self.email.create_workflow_email(
                    event_type.replace('_', ' ').title(), issue_key,
                    details.get('user', 'System'), details
                )
                
                success = self.email.send_email(recipient_emails, email_subject, email_body)
                results[f'email_batch'] = success
                
                for email in recipient_emails:
                    self._log_notification(event_type, issue_key, email, 'email', success, details)
        
        return results
    
    def _get_recipient_emails(self, recipients: List[str]) -> List[str]:
        """Get email addresses for recipients"""
        emails = []
        for recipient in recipients:
            user = self.team_manager.get_user(recipient)
            if user and user.email:
                emails.append(user.email)
        return emails
    
    def _log_notification(self, event_type: str, issue_key: str, recipient: str,
                         channel: str, success: bool, details: Dict[str, Any]):
        """Log notification in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO notifications_sent 
                (event_type, issue_key, recipient, channel, success, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                event_type, issue_key, recipient, channel, success,
                json.dumps(details)
            ))
    
    def notify_workflow_started(self, issue_key: str, user: str, summary: str, branch: str):
        """Send workflow started notification"""
        return self.send_notification(
            'workflow_started', issue_key, [user],
            user=user, summary=summary, branch=branch
        )
    
    def notify_approval_required(self, issue_key: str, action: str, 
                               requester: str, approvers: List[str], request_id: str):
        """Send approval required notification"""
        return self.send_notification(
            'approval_required', issue_key, approvers,
            action=action, requester=requester, request_id=request_id
        )
    
    def notify_pr_created(self, issue_key: str, user: str, pr_url: str, team: str):
        """Send PR created notification"""
        team_members = [m.username for m in self.team_manager.get_team_members(team)]
        return self.send_notification(
            'pr_created', issue_key, team_members,
            user=user, pr_url=pr_url
        )
    
    def notify_deployment_ready(self, issue_key: str, environment: str, approvers: List[str]):
        """Send deployment ready notification"""
        return self.send_notification(
            'deployment_ready', issue_key, approvers,
            environment=environment
        )
    
    def notify_workflow_completed(self, issue_key: str, user: str, team: str):
        """Send workflow completed notification"""
        team_members = [m.username for m in self.team_manager.get_team_members(team)]
        return self.send_notification(
            'workflow_completed', issue_key, team_members,
            user=user
        )
    
    def get_notification_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get notification statistics"""
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Total notifications
            cursor = conn.execute('''
                SELECT COUNT(*) FROM notifications_sent 
                WHERE timestamp > ?
            ''', (since_date.isoformat(),))
            total_notifications = cursor.fetchone()[0]
            
            # Success rate by channel
            cursor = conn.execute('''
                SELECT channel, 
                       COUNT(*) as total,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
                FROM notifications_sent 
                WHERE timestamp > ?
                GROUP BY channel
            ''', (since_date.isoformat(),))
            
            channel_stats = {}
            for row in cursor.fetchall():
                channel, total, successful = row
                channel_stats[channel] = {
                    'total': total,
                    'successful': successful,
                    'success_rate': (successful / total * 100) if total > 0 else 0
                }
            
            # Most common events
            cursor = conn.execute('''
                SELECT event_type, COUNT(*) as count
                FROM notifications_sent 
                WHERE timestamp > ?
                GROUP BY event_type
                ORDER BY count DESC
                LIMIT 5
            ''', (since_date.isoformat(),))
            
            common_events = dict(cursor.fetchall())
        
        return {
            'period_days': days,
            'total_notifications': total_notifications,
            'channel_stats': channel_stats,
            'common_events': common_events
        }


def main():
    """Main entry point for external integrations"""
    import argparse
    from .config import load_jira_config
    
    parser = argparse.ArgumentParser(description="External Integrations Management")
    parser.add_argument("command", choices=["test-slack", "test-teams", "test-email", "stats"])
    parser.add_argument("--message", default="Test message from JIRA Workflow")
    parser.add_argument("--config", help="Path to .env configuration file")
    parser.add_argument("--email", help="Email address for testing")
    
    args = parser.parse_args()
    
    try:
        if args.command == "test-slack":
            slack = SlackIntegration()
            success = slack.send_message("#general", args.message)
            print(f"{'✅' if success else '❌'} Slack test: {'Success' if success else 'Failed'}")
        
        elif args.command == "test-teams":
            teams = TeamsIntegration()
            success = teams.send_message("Test Notification", args.message)
            print(f"{'✅' if success else '❌'} Teams test: {'Success' if success else 'Failed'}")
        
        elif args.command == "test-email":
            if not args.email:
                print("❌ Email address required (--email)")
                return
            
            email_service = EmailIntegration()
            success = email_service.send_email([args.email], "Test Notification", args.message)
            print(f"{'✅' if success else '❌'} Email test: {'Success' if success else 'Failed'}")
        
        elif args.command == "stats":
            if args.config:
                jira_config = load_jira_config(args.config)
                team_manager = TeamManager()
                orchestrator = NotificationOrchestrator(team_manager, jira_config)
                
                stats = orchestrator.get_notification_stats()
                
                print("📊 Notification Statistics (Last 7 days):")
                print(f"   Total Notifications: {stats['total_notifications']}")
                print("   Channel Performance:")
                for channel, data in stats['channel_stats'].items():
                    print(f"      {channel}: {data['successful']}/{data['total']} ({data['success_rate']:.1f}%)")
                print("   Common Events:")
                for event, count in stats['common_events'].items():
                    print(f"      {event}: {count}")
            else:
                print("❌ Config required for stats")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()