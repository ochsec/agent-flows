#!/usr/bin/env python3
"""
Webhook Integration Module - Phase 4

Provides real-time webhook processing for JIRA and GitHub events,
enabling automated workflow triggers and team notifications.
"""

import os
import json
import hmac
import hashlib
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from flask import Flask, request, jsonify
import sqlite3
import threading
from queue import Queue

from .config import JiraConfig
from .jira_client import JiraClient
from .advanced_automation import AdvancedJiraWorkflow, MultiProjectManager


@dataclass
class WebhookEvent:
    """Webhook event data structure"""
    source: str  # 'jira', 'github', 'gitlab'
    event_type: str  # 'issue_created', 'pr_opened', etc.
    timestamp: datetime
    data: Dict[str, Any]
    project: Optional[str] = None
    issue_key: Optional[str] = None
    user: Optional[str] = None


class WebhookProcessor:
    """Process webhook events and trigger workflows"""
    
    def __init__(self, jira_config: JiraConfig):
        self.jira_config = jira_config
        self.jira_client = JiraClient(jira_config)
        self.project_manager = MultiProjectManager()
        self.event_handlers = {}
        self.event_queue = Queue()
        self.db_path = "webhook_events.db"
        self.init_database()
        
        # Start event processing thread
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
    
    def init_database(self):
        """Initialize webhook events database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS webhook_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    project TEXT,
                    issue_key TEXT,
                    user_name TEXT,
                    data TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    result TEXT
                )
            ''')
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler for specific event types"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def process_webhook(self, source: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook and queue for handling"""
        try:
            # Verify webhook signature if available
            if not self._verify_webhook_signature(source, headers, payload):
                return {"status": "error", "message": "Invalid webhook signature"}
            
            # Parse event
            event = self._parse_webhook_event(source, payload)
            if not event:
                return {"status": "error", "message": "Unable to parse webhook event"}
            
            # Store in database
            self._store_event(event)
            
            # Queue for processing
            self.event_queue.put(event)
            
            return {"status": "success", "event_type": event.event_type}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _verify_webhook_signature(self, source: str, headers: Dict[str, str], payload: Dict[str, Any]) -> bool:
        """Verify webhook signature for security"""
        if source == "github":
            signature = headers.get("X-Hub-Signature-256", "")
            secret = os.getenv("GITHUB_WEBHOOK_SECRET")
            if secret:
                expected_signature = "sha256=" + hmac.new(
                    secret.encode(), 
                    json.dumps(payload).encode(), 
                    hashlib.sha256
                ).hexdigest()
                return hmac.compare_digest(signature, expected_signature)
        
        elif source == "jira":
            # JIRA webhook verification (if configured)
            secret = os.getenv("JIRA_WEBHOOK_SECRET")
            if secret:
                # Implement JIRA webhook verification logic
                pass
        
        return True  # Allow unverified webhooks in development
    
    def _parse_webhook_event(self, source: str, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        """Parse webhook payload into standardized event"""
        try:
            if source == "jira":
                return self._parse_jira_webhook(payload)
            elif source == "github":
                return self._parse_github_webhook(payload)
            elif source == "gitlab":
                return self._parse_gitlab_webhook(payload)
        except Exception as e:
            print(f"Error parsing {source} webhook: {e}")
        
        return None
    
    def _parse_jira_webhook(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        """Parse JIRA webhook events"""
        webhook_event = payload.get("webhookEvent", "")
        
        if webhook_event == "jira:issue_created":
            issue = payload["issue"]
            return WebhookEvent(
                source="jira",
                event_type="issue_created",
                timestamp=datetime.now(),
                data=payload,
                issue_key=issue["key"],
                project=issue["fields"]["project"]["key"],
                user=payload.get("user", {}).get("displayName")
            )
        
        elif webhook_event == "jira:issue_updated":
            issue = payload["issue"]
            changelog = payload.get("changelog", {})
            
            # Check if status changed
            status_changed = any(
                item["field"] == "status" 
                for item in changelog.get("items", [])
            )
            
            return WebhookEvent(
                source="jira",
                event_type="issue_updated" if not status_changed else "status_changed",
                timestamp=datetime.now(),
                data=payload,
                issue_key=issue["key"],
                project=issue["fields"]["project"]["key"],
                user=payload.get("user", {}).get("displayName")
            )
        
        return None
    
    def _parse_github_webhook(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        """Parse GitHub webhook events"""
        action = payload.get("action")
        
        if "pull_request" in payload:
            pr = payload["pull_request"]
            return WebhookEvent(
                source="github",
                event_type=f"pr_{action}",
                timestamp=datetime.now(),
                data=payload,
                project=payload["repository"]["name"],
                user=pr["user"]["login"]
            )
        
        elif "issue" in payload:
            issue = payload["issue"]
            return WebhookEvent(
                source="github",
                event_type=f"github_issue_{action}",
                timestamp=datetime.now(),
                data=payload,
                project=payload["repository"]["name"],
                user=issue["user"]["login"]
            )
        
        return None
    
    def _parse_gitlab_webhook(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        """Parse GitLab webhook events"""
        object_kind = payload.get("object_kind")
        
        if object_kind == "merge_request":
            mr = payload["object_attributes"]
            return WebhookEvent(
                source="gitlab",
                event_type=f"mr_{mr['action']}",
                timestamp=datetime.now(),
                data=payload,
                project=payload["project"]["name"],
                user=payload["user"]["name"]
            )
        
        return None
    
    def _store_event(self, event: WebhookEvent):
        """Store event in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO webhook_events 
                (source, event_type, project, issue_key, user_name, data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                event.source,
                event.event_type,
                event.project,
                event.issue_key,
                event.user,
                json.dumps(event.data)
            ))
    
    def _process_events(self):
        """Background thread to process webhook events"""
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                self._handle_event(event)
                self.event_queue.task_done()
            except:
                continue
    
    def _handle_event(self, event: WebhookEvent):
        """Handle specific webhook event"""
        handlers = self.event_handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                result = handler(event)
                print(f"Processed {event.event_type}: {result}")
            except Exception as e:
                print(f"Error handling {event.event_type}: {e}")
        
        # Update database with processing result
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE webhook_events 
                SET processed = TRUE, result = ? 
                WHERE source = ? AND event_type = ? AND timestamp = ?
            ''', (
                f"Processed by {len(handlers)} handlers",
                event.source,
                event.event_type,
                event.timestamp
            ))


class JiraWebhookHandlers:
    """Predefined handlers for JIRA webhook events"""
    
    def __init__(self, jira_config: JiraConfig):
        self.jira_config = jira_config
        self.workflow = AdvancedJiraWorkflow(jira_config)
    
    def handle_issue_created(self, event: WebhookEvent) -> str:
        """Auto-assign and start workflow for new issues"""
        try:
            issue_data = event.data["issue"]
            issue_key = issue_data["key"]
            
            # Check if issue is assigned to current user
            assignee = issue_data["fields"].get("assignee")
            current_user = self.jira_config.username
            
            if assignee and assignee.get("emailAddress") == current_user:
                # Auto-start workflow for assigned issues
                print(f"🚀 Auto-starting workflow for assigned issue: {issue_key}")
                result = self.workflow.start_work_on_issue(issue_key)
                return f"Auto-started workflow: {result['status']}"
            
            return "Issue not assigned to current user"
            
        except Exception as e:
            return f"Error: {e}"
    
    def handle_status_changed(self, event: WebhookEvent) -> str:
        """Handle issue status changes"""
        try:
            changelog = event.data.get("changelog", {})
            
            for item in changelog.get("items", []):
                if item["field"] == "status":
                    from_status = item["fromString"]
                    to_status = item["toString"]
                    
                    if to_status == "In Progress":
                        # Trigger workflow start
                        return f"Status changed to In Progress - consider starting workflow"
                    elif to_status in ["Done", "Closed"]:
                        # Trigger completion actions
                        return f"Issue completed - triggering cleanup actions"
            
            return "Status change processed"
            
        except Exception as e:
            return f"Error: {e}"


class GitHubWebhookHandlers:
    """Predefined handlers for GitHub webhook events"""
    
    def __init__(self, jira_config: JiraConfig):
        self.jira_config = jira_config
        self.jira_client = JiraClient(jira_config)
    
    def handle_pr_opened(self, event: WebhookEvent) -> str:
        """Handle PR opened events"""
        try:
            pr = event.data["pull_request"]
            branch_name = pr["head"]["ref"]
            
            # Extract JIRA issue key from branch name
            import re
            issue_match = re.search(r'([A-Z]+-\d+)', branch_name.upper())
            
            if issue_match:
                issue_key = issue_match.group(1)
                
                # Add comment to JIRA issue
                pr_url = pr["html_url"]
                comment = f"🔗 Pull Request created: {pr_url}\n\nTitle: {pr['title']}\nBranch: {branch_name}"
                
                self.jira_client.add_comment(issue_key, comment)
                return f"Updated JIRA issue {issue_key} with PR link"
            
            return "No JIRA issue key found in branch name"
            
        except Exception as e:
            return f"Error: {e}"
    
    def handle_pr_merged(self, event: WebhookEvent) -> str:
        """Handle PR merged events"""
        try:
            pr = event.data["pull_request"]
            branch_name = pr["head"]["ref"]
            
            # Extract JIRA issue key
            import re
            issue_match = re.search(r'([A-Z]+-\d+)', branch_name.upper())
            
            if issue_match:
                issue_key = issue_match.group(1)
                
                # Update JIRA issue status or add completion comment
                comment = f"✅ Pull Request merged successfully!\n\nPR: {pr['html_url']}\nBranch: {branch_name}\nMerged by: {pr['merged_by']['login']}"
                
                self.jira_client.add_comment(issue_key, comment)
                return f"Updated JIRA issue {issue_key} with merge confirmation"
            
            return "No JIRA issue key found in branch name"
            
        except Exception as e:
            return f"Error: {e}"


class WebhookServer:
    """Flask server for receiving webhooks"""
    
    def __init__(self, jira_config: JiraConfig, port: int = 8080):
        self.app = Flask(__name__)
        self.processor = WebhookProcessor(jira_config)
        self.port = port
        
        # Register default handlers
        jira_handlers = JiraWebhookHandlers(jira_config)
        github_handlers = GitHubWebhookHandlers(jira_config)
        
        self.processor.register_handler("issue_created", jira_handlers.handle_issue_created)
        self.processor.register_handler("status_changed", jira_handlers.handle_status_changed)
        self.processor.register_handler("pr_opened", github_handlers.handle_pr_opened)
        self.processor.register_handler("pr_closed", github_handlers.handle_pr_merged)
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes for webhook endpoints"""
        
        @self.app.route('/webhook/jira', methods=['POST'])
        def jira_webhook():
            headers = dict(request.headers)
            payload = request.get_json()
            
            result = self.processor.process_webhook("jira", headers, payload)
            return jsonify(result)
        
        @self.app.route('/webhook/github', methods=['POST'])
        def github_webhook():
            headers = dict(request.headers)
            payload = request.get_json()
            
            result = self.processor.process_webhook("github", headers, payload)
            return jsonify(result)
        
        @self.app.route('/webhook/gitlab', methods=['POST'])
        def gitlab_webhook():
            headers = dict(request.headers)
            payload = request.get_json()
            
            result = self.processor.process_webhook("gitlab", headers, payload)
            return jsonify(result)
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
        
        @self.app.route('/events', methods=['GET'])
        def list_events():
            """List recent webhook events"""
            with sqlite3.connect(self.processor.db_path) as conn:
                cursor = conn.execute('''
                    SELECT source, event_type, timestamp, project, issue_key, processed
                    FROM webhook_events 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                ''')
                
                events = []
                for row in cursor.fetchall():
                    events.append({
                        "source": row[0],
                        "event_type": row[1],
                        "timestamp": row[2],
                        "project": row[3],
                        "issue_key": row[4],
                        "processed": bool(row[5])
                    })
                
                return jsonify({"events": events})
    
    def run(self, debug: bool = False):
        """Start the webhook server"""
        print(f"🌐 Starting webhook server on port {self.port}")
        print(f"📡 Endpoints:")
        print(f"   JIRA: http://localhost:{self.port}/webhook/jira")
        print(f"   GitHub: http://localhost:{self.port}/webhook/github")
        print(f"   GitLab: http://localhost:{self.port}/webhook/gitlab")
        print(f"   Health: http://localhost:{self.port}/health")
        print(f"   Events: http://localhost:{self.port}/events")
        
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)


def main():
    """Main entry point for webhook server"""
    import argparse
    from .config import load_jira_config
    
    parser = argparse.ArgumentParser(description="JIRA Workflow Webhook Server")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--config", help="Path to .env configuration file")
    
    args = parser.parse_args()
    
    try:
        config = load_jira_config(args.config)
        server = WebhookServer(config, args.port)
        server.run(debug=args.debug)
    except Exception as e:
        print(f"❌ Error starting webhook server: {e}")


if __name__ == "__main__":
    main()