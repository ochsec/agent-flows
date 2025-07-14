#!/usr/bin/env python3
"""
Analytics and Reporting Module - Phase 3

Provides comprehensive analytics, reporting, and metrics collection
for JIRA workflow usage and development productivity.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


@dataclass
class WorkflowMetrics:
    """Metrics for a single workflow execution"""
    session_id: str
    issue_key: str
    project_name: str
    project_type: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[float]
    commands_executed: int
    files_modified: int
    tests_created: int
    tests_passed: int
    pr_created: bool
    deployment_triggered: bool
    status: str  # completed, in_progress, failed
    user: str


@dataclass
class ProjectMetrics:
    """Aggregated metrics for a project"""
    project_name: str
    total_issues: int
    completed_issues: int
    avg_completion_time: float
    total_files_modified: int
    total_tests_created: int
    success_rate: float
    most_common_commands: List[Tuple[str, int]]


class AnalyticsDatabase:
    """SQLite database for storing workflow analytics"""
    
    def __init__(self, db_path: str = "jira_workflow_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS workflow_sessions (
                    session_id TEXT PRIMARY KEY,
                    issue_key TEXT NOT NULL,
                    project_name TEXT,
                    project_type TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_minutes REAL,
                    commands_executed INTEGER,
                    files_modified INTEGER,
                    tests_created INTEGER,
                    tests_passed INTEGER,
                    pr_created BOOLEAN,
                    deployment_triggered BOOLEAN,
                    status TEXT,
                    user TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    command_name TEXT,
                    timestamp TIMESTAMP,
                    duration_seconds REAL,
                    success BOOLEAN,
                    files_affected TEXT,
                    FOREIGN KEY (session_id) REFERENCES workflow_sessions (session_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES workflow_sessions (session_id)
                )
            ''')
    
    def record_session_start(self, metrics: WorkflowMetrics):
        """Record the start of a workflow session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO workflow_sessions 
                (session_id, issue_key, project_name, project_type, start_time, user, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.session_id, metrics.issue_key, metrics.project_name,
                metrics.project_type, metrics.start_time, metrics.user, 'in_progress'
            ))
    
    def record_session_end(self, session_id: str, metrics: WorkflowMetrics):
        """Record the completion of a workflow session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE workflow_sessions SET
                    end_time = ?, duration_minutes = ?, commands_executed = ?,
                    files_modified = ?, tests_created = ?, tests_passed = ?,
                    pr_created = ?, deployment_triggered = ?, status = ?
                WHERE session_id = ?
            ''', (
                metrics.end_time, metrics.duration_minutes, metrics.commands_executed,
                metrics.files_modified, metrics.tests_created, metrics.tests_passed,
                metrics.pr_created, metrics.deployment_triggered, metrics.status,
                session_id
            ))
    
    def record_command(self, session_id: str, command_name: str, 
                      duration: float, success: bool, files_affected: List[str]):
        """Record individual command execution"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO command_history 
                (session_id, command_name, timestamp, duration_seconds, success, files_affected)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id, command_name, datetime.now(), duration,
                success, json.dumps(files_affected)
            ))
    
    def record_quality_metric(self, session_id: str, metric_name: str, value: float):
        """Record quality metrics like test coverage, lint score, etc."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO quality_metrics (session_id, metric_name, metric_value, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (session_id, metric_name, value, datetime.now()))
    
    def get_project_metrics(self, project_name: str, days: int = 30) -> ProjectMetrics:
        """Get aggregated metrics for a project"""
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Get basic project stats
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total_issues,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_issues,
                    AVG(duration_minutes) as avg_duration,
                    SUM(files_modified) as total_files,
                    SUM(tests_created) as total_tests,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate
                FROM workflow_sessions 
                WHERE project_name = ? AND start_time > ?
            ''', (project_name, since_date))
            
            row = cursor.fetchone()
            
            # Get most common commands
            cursor = conn.execute('''
                SELECT command_name, COUNT(*) as count
                FROM command_history ch
                JOIN workflow_sessions ws ON ch.session_id = ws.session_id
                WHERE ws.project_name = ? AND ws.start_time > ?
                GROUP BY command_name
                ORDER BY count DESC
                LIMIT 5
            ''', (project_name, since_date))
            
            common_commands = cursor.fetchall()
            
            return ProjectMetrics(
                project_name=project_name,
                total_issues=row[0] or 0,
                completed_issues=row[1] or 0,
                avg_completion_time=row[2] or 0,
                total_files_modified=row[3] or 0,
                total_tests_created=row[4] or 0,
                success_rate=row[5] or 0,
                most_common_commands=common_commands
            )
    
    def get_user_productivity(self, user: str, days: int = 30) -> Dict[str, Any]:
        """Get productivity metrics for a user"""
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                    AVG(duration_minutes) as avg_session_duration,
                    SUM(files_modified) as total_files_modified,
                    AVG(commands_executed) as avg_commands_per_session
                FROM workflow_sessions 
                WHERE user = ? AND start_time > ?
            ''', (user, since_date))
            
            row = cursor.fetchone()
            
            return {
                'user': user,
                'total_sessions': row[0] or 0,
                'completed_sessions': row[1] or 0,
                'completion_rate': (row[1] / row[0] * 100) if row[0] else 0,
                'avg_session_duration': row[2] or 0,
                'total_files_modified': row[3] or 0,
                'avg_commands_per_session': row[4] or 0
            }


class ReportGenerator:
    """Generates various reports and visualizations"""
    
    def __init__(self, analytics_db: AnalyticsDatabase):
        self.db = analytics_db
    
    def generate_project_report(self, project_name: str, output_dir: str = "reports") -> str:
        """Generate comprehensive project report"""
        metrics = self.db.get_project_metrics(project_name)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        report_file = output_path / f"{project_name}_report.md"
        
        with open(report_file, 'w') as f:
            f.write(f"""# JIRA Workflow Analytics Report: {project_name}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Issues Processed**: {metrics.total_issues}
- **Completed Issues**: {metrics.completed_issues}
- **Success Rate**: {metrics.success_rate:.1f}%
- **Average Completion Time**: {metrics.avg_completion_time:.1f} minutes
- **Total Files Modified**: {metrics.total_files_modified}
- **Total Tests Created**: {metrics.total_tests_created}

## Most Common Commands

""")
            
            for command, count in metrics.most_common_commands:
                f.write(f"- **{command}**: {count} executions\n")
            
            f.write(f"""
## Productivity Insights

- **Files per Issue**: {metrics.total_files_modified / max(metrics.completed_issues, 1):.1f}
- **Tests per Issue**: {metrics.total_tests_created / max(metrics.completed_issues, 1):.1f}
- **Workflow Efficiency**: {'High' if metrics.success_rate > 80 else 'Medium' if metrics.success_rate > 60 else 'Low'}

## Recommendations

""")
            
            if metrics.success_rate < 70:
                f.write("- Consider reviewing workflow templates and providing additional training\n")
            
            if metrics.avg_completion_time > 120:  # 2 hours
                f.write("- Look into breaking down larger issues into smaller tasks\n")
            
            if metrics.total_tests_created / max(metrics.completed_issues, 1) < 2:
                f.write("- Encourage more comprehensive testing practices\n")
        
        return str(report_file)
    
    def generate_productivity_chart(self, project_name: str, output_dir: str = "reports") -> str:
        """Generate productivity visualization"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            
            # Get daily completion data for the last 30 days
            with sqlite3.connect(self.db.db_path) as conn:
                df = pd.read_sql_query('''
                    SELECT 
                        DATE(start_time) as date,
                        COUNT(*) as total_issues,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_issues,
                        AVG(duration_minutes) as avg_duration
                    FROM workflow_sessions 
                    WHERE project_name = ? AND start_time > date('now', '-30 days')
                    GROUP BY DATE(start_time)
                    ORDER BY date
                ''', conn, params=[project_name])
            
            if df.empty:
                return None
            
            df['date'] = pd.to_datetime(df['date'])
            
            # Create visualization
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Issues per day
            ax1.plot(df['date'], df['total_issues'], label='Total Issues', marker='o')
            ax1.plot(df['date'], df['completed_issues'], label='Completed Issues', marker='s')
            ax1.set_title(f'Daily Issue Activity - {project_name}')
            ax1.set_ylabel('Number of Issues')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Average duration
            ax2.plot(df['date'], df['avg_duration'], label='Avg Duration', marker='d', color='orange')
            ax2.set_title('Average Completion Time')
            ax2.set_ylabel('Minutes')
            ax2.set_xlabel('Date')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Format x-axis
            for ax in [ax1, ax2]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            chart_file = output_path / f"{project_name}_productivity.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_file)
            
        except ImportError:
            print("Matplotlib/Pandas not available. Install with: pip install matplotlib pandas")
            return None
    
    def generate_team_dashboard(self, output_dir: str = "reports") -> str:
        """Generate team dashboard with overall metrics"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        dashboard_file = output_path / "team_dashboard.html"
        
        # Get team metrics
        with sqlite3.connect(self.db.db_path) as conn:
            # Project summary
            project_stats = pd.read_sql_query('''
                SELECT 
                    project_name,
                    COUNT(*) as total_issues,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    AVG(duration_minutes) as avg_duration,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate
                FROM workflow_sessions 
                WHERE start_time > date('now', '-30 days')
                GROUP BY project_name
                ORDER BY total_issues DESC
            ''', conn)
            
            # User productivity
            user_stats = pd.read_sql_query('''
                SELECT 
                    user,
                    COUNT(*) as sessions,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    AVG(duration_minutes) as avg_duration
                FROM workflow_sessions 
                WHERE start_time > date('now', '-30 days')
                GROUP BY user
                ORDER BY sessions DESC
            ''', conn)
        
        # Generate HTML dashboard
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>JIRA Workflow Team Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .metric-card {{ 
            background: #f5f5f5; padding: 20px; margin: 10px; 
            border-radius: 8px; display: inline-block; width: 200px;
        }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .header {{ text-align: center; color: #333; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1 class="header">JIRA Workflow Team Dashboard</h1>
        <p class="header">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Project Performance (Last 30 Days)</h2>
        <table>
            <tr>
                <th>Project</th>
                <th>Total Issues</th>
                <th>Completed</th>
                <th>Success Rate</th>
                <th>Avg Duration (min)</th>
            </tr>
"""
        
        for _, row in project_stats.iterrows():
            html_content += f"""
            <tr>
                <td>{row['project_name'] or 'Unknown'}</td>
                <td>{row['total_issues']}</td>
                <td>{row['completed']}</td>
                <td>{row['success_rate']:.1f}%</td>
                <td>{row['avg_duration']:.1f}</td>
            </tr>
"""
        
        html_content += """
        </table>
        
        <h2>User Productivity</h2>
        <table>
            <tr>
                <th>User</th>
                <th>Sessions</th>
                <th>Completed</th>
                <th>Completion Rate</th>
                <th>Avg Duration (min)</th>
            </tr>
"""
        
        for _, row in user_stats.iterrows():
            completion_rate = (row['completed'] / row['sessions'] * 100) if row['sessions'] else 0
            html_content += f"""
            <tr>
                <td>{row['user'] or 'Unknown'}</td>
                <td>{row['sessions']}</td>
                <td>{row['completed']}</td>
                <td>{completion_rate:.1f}%</td>
                <td>{row['avg_duration']:.1f}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
</body>
</html>
"""
        
        with open(dashboard_file, 'w') as f:
            f.write(html_content)
        
        return str(dashboard_file)


class WorkflowAnalytics:
    """Main analytics interface for the JIRA workflow"""
    
    def __init__(self, db_path: str = "jira_workflow_analytics.db"):
        self.db = AnalyticsDatabase(db_path)
        self.report_generator = ReportGenerator(self.db)
        self.current_session = None
    
    def start_session(self, issue_key: str, project_name: str, 
                     project_type: str, user: str) -> str:
        """Start tracking a new workflow session"""
        session_id = f"{issue_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        metrics = WorkflowMetrics(
            session_id=session_id,
            issue_key=issue_key,
            project_name=project_name,
            project_type=project_type,
            start_time=datetime.now(),
            end_time=None,
            duration_minutes=None,
            commands_executed=0,
            files_modified=0,
            tests_created=0,
            tests_passed=0,
            pr_created=False,
            deployment_triggered=False,
            status='in_progress',
            user=user
        )
        
        self.db.record_session_start(metrics)
        self.current_session = metrics
        return session_id
    
    def end_session(self, session_id: str, success: bool = True, 
                   pr_created: bool = False, deployment_triggered: bool = False):
        """End tracking for a workflow session"""
        if self.current_session and self.current_session.session_id == session_id:
            self.current_session.end_time = datetime.now()
            self.current_session.duration_minutes = (
                self.current_session.end_time - self.current_session.start_time
            ).total_seconds() / 60
            self.current_session.status = 'completed' if success else 'failed'
            self.current_session.pr_created = pr_created
            self.current_session.deployment_triggered = deployment_triggered
            
            self.db.record_session_end(session_id, self.current_session)
    
    def record_command_execution(self, command_name: str, duration: float, 
                               success: bool, files_affected: List[str]):
        """Record execution of a workflow command"""
        if self.current_session:
            self.current_session.commands_executed += 1
            self.current_session.files_modified += len(files_affected)
            
            self.db.record_command(
                self.current_session.session_id, command_name, 
                duration, success, files_affected
            )
    
    def generate_reports(self, project_name: str = None) -> Dict[str, str]:
        """Generate all available reports"""
        reports = {}
        
        if project_name:
            # Project-specific reports
            reports['project_report'] = self.report_generator.generate_project_report(project_name)
            chart_file = self.report_generator.generate_productivity_chart(project_name)
            if chart_file:
                reports['productivity_chart'] = chart_file
        
        # Team dashboard
        reports['team_dashboard'] = self.report_generator.generate_team_dashboard()
        
        return reports
    
    def get_quick_stats(self, project_name: str = None, days: int = 7) -> Dict[str, Any]:
        """Get quick statistics for display"""
        if project_name:
            metrics = self.db.get_project_metrics(project_name, days)
            return {
                'project': project_name,
                'period_days': days,
                'total_issues': metrics.total_issues,
                'completed_issues': metrics.completed_issues,
                'success_rate': f"{metrics.success_rate:.1f}%",
                'avg_completion_time': f"{metrics.avg_completion_time:.1f} min"
            }
        else:
            # Overall stats
            since_date = datetime.now() - timedelta(days=days)
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                        AVG(duration_minutes) as avg_duration
                    FROM workflow_sessions 
                    WHERE start_time > ?
                ''', (since_date,))
                
                row = cursor.fetchone()
                total, completed, avg_duration = row
                
                return {
                    'period_days': days,
                    'total_sessions': total,
                    'completed_sessions': completed,
                    'success_rate': f"{(completed/total*100) if total else 0:.1f}%",
                    'avg_duration': f"{avg_duration or 0:.1f} min"
                }


if __name__ == "__main__":
    # Example usage
    analytics = WorkflowAnalytics()
    
    # Generate sample reports
    reports = analytics.generate_reports()
    print("Generated reports:")
    for report_type, file_path in reports.items():
        print(f"  {report_type}: {file_path}")
    
    # Show quick stats
    stats = analytics.get_quick_stats()
    print(f"\nQuick Stats (Last 7 days):")
    for key, value in stats.items():
        print(f"  {key}: {value}")