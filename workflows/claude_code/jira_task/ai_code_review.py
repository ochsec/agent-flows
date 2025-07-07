#!/usr/bin/env python3
"""
AI-Powered Code Review Module - Phase 4

Provides automated code quality analysis, security scanning, and 
intelligent code review suggestions using Claude and other AI tools.
"""

import os
import re
import ast
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3

from .config import JiraConfig
from .jira_client import JiraClient


@dataclass
class CodeIssue:
    """Represents a code quality or security issue"""
    file_path: str
    line_number: int
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    category: str  # 'security', 'performance', 'style', 'bug', 'maintainability'
    title: str
    description: str
    suggestion: Optional[str] = None
    rule_id: Optional[str] = None


@dataclass
class ReviewMetrics:
    """Code review metrics and scores"""
    total_lines: int
    files_analyzed: int
    issues_found: int
    security_score: float  # 0-100
    quality_score: float   # 0-100
    complexity_score: float # 0-100
    test_coverage: Optional[float] = None
    

class SecurityScanner:
    """Security vulnerability scanner"""
    
    def __init__(self):
        self.security_patterns = {
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r'SELECT.*\+.*FROM',
            ],
            'xss_vulnerable': [
                r'innerHTML\s*=.*\+',
                r'document\.write\s*\(',
                r'eval\s*\(',
            ],
            'weak_crypto': [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'DES\s*\(',
            ]
        }
    
    def scan_file(self, file_path: str) -> List[CodeIssue]:
        """Scan a file for security vulnerabilities"""
        issues = []
        
        if not Path(file_path).exists():
            return issues
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for category, patterns in self.security_patterns.items():
                for pattern in patterns:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append(CodeIssue(
                                file_path=file_path,
                                line_number=line_num,
                                severity='high' if category == 'hardcoded_secrets' else 'medium',
                                category='security',
                                title=f"Security: {category.replace('_', ' ').title()}",
                                description=f"Potential {category} detected in line {line_num}",
                                suggestion=self._get_security_suggestion(category),
                                rule_id=f"security_{category}"
                            ))
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return issues
    
    def _get_security_suggestion(self, category: str) -> str:
        """Get security remediation suggestions"""
        suggestions = {
            'hardcoded_secrets': "Use environment variables or secure configuration management for sensitive data",
            'sql_injection': "Use parameterized queries or ORM methods to prevent SQL injection",
            'xss_vulnerable': "Sanitize user input and use safe DOM manipulation methods",
            'weak_crypto': "Use stronger cryptographic algorithms like SHA-256 or bcrypt"
        }
        return suggestions.get(category, "Review this potential security issue")


class CodeQualityAnalyzer:
    """Analyze code quality metrics"""
    
    def analyze_python_file(self, file_path: str) -> Tuple[List[CodeIssue], Dict[str, Any]]:
        """Analyze Python file for quality issues"""
        issues = []
        metrics = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Analyze complexity
            complexity_analyzer = ComplexityAnalyzer()
            complexity_issues, complexity_metrics = complexity_analyzer.analyze(tree, file_path)
            issues.extend(complexity_issues)
            metrics.update(complexity_metrics)
            
            # Analyze style issues
            style_analyzer = StyleAnalyzer()
            style_issues = style_analyzer.analyze(content, file_path)
            issues.extend(style_issues)
            
            # Check for common anti-patterns
            antipattern_analyzer = AntiPatternAnalyzer()
            antipattern_issues = antipattern_analyzer.analyze(tree, file_path)
            issues.extend(antipattern_issues)
            
        except SyntaxError as e:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=e.lineno or 1,
                severity='critical',
                category='bug',
                title="Syntax Error",
                description=str(e),
                suggestion="Fix syntax error before proceeding"
            ))
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
        
        return issues, metrics


class ComplexityAnalyzer:
    """Analyze code complexity"""
    
    def analyze(self, tree: ast.AST, file_path: str) -> Tuple[List[CodeIssue], Dict[str, Any]]:
        """Analyze cyclomatic complexity"""
        issues = []
        metrics = {
            'total_functions': 0,
            'complex_functions': 0,
            'max_complexity': 0,
            'avg_complexity': 0
        }
        
        complexities = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_complexity(node)
                complexities.append(complexity)
                metrics['total_functions'] += 1
                
                if complexity > 10:  # High complexity threshold
                    metrics['complex_functions'] += 1
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        severity='medium' if complexity <= 15 else 'high',
                        category='maintainability',
                        title=f"High Complexity Function: {node.name}",
                        description=f"Function '{node.name}' has cyclomatic complexity of {complexity}",
                        suggestion="Consider breaking down this function into smaller functions",
                        rule_id="high_complexity"
                    ))
        
        if complexities:
            metrics['max_complexity'] = max(complexities)
            metrics['avg_complexity'] = sum(complexities) / len(complexities)
        
        return issues, metrics
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


class StyleAnalyzer:
    """Analyze code style issues"""
    
    def analyze(self, content: str, file_path: str) -> List[CodeIssue]:
        """Analyze style issues"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 100:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    severity='low',
                    category='style',
                    title="Line Too Long",
                    description=f"Line {line_num} has {len(line)} characters (recommended: ≤100)",
                    suggestion="Break long lines for better readability",
                    rule_id="line_length"
                ))
            
            # Trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    severity='info',
                    category='style',
                    title="Trailing Whitespace",
                    description=f"Line {line_num} has trailing whitespace",
                    suggestion="Remove trailing whitespace",
                    rule_id="trailing_whitespace"
                ))
        
        return issues


class AntiPatternAnalyzer:
    """Detect common anti-patterns"""
    
    def analyze(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Analyze for anti-patterns"""
        issues = []
        
        for node in ast.walk(tree):
            # Bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=node.lineno,
                    severity='medium',
                    category='bug',
                    title="Bare Except Clause",
                    description="Using bare 'except:' can hide important errors",
                    suggestion="Catch specific exceptions instead",
                    rule_id="bare_except"
                ))
            
            # Global variables
            elif isinstance(node, ast.Global):
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=node.lineno,
                    severity='low',
                    category='maintainability',
                    title="Global Variable Usage",
                    description="Global variables can make code harder to test and maintain",
                    suggestion="Consider using function parameters or class attributes",
                    rule_id="global_usage"
                ))
        
        return issues


class AICodeReviewer:
    """AI-powered code review using Claude"""
    
    def __init__(self, jira_config: JiraConfig):
        self.jira_config = jira_config
        self.security_scanner = SecurityScanner()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.db_path = "code_review_results.db"
        self.init_database()
    
    def init_database(self):
        """Initialize review results database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS review_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_key TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    files_analyzed INTEGER,
                    total_issues INTEGER,
                    security_score REAL,
                    quality_score REAL,
                    review_summary TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS review_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    file_path TEXT,
                    line_number INTEGER,
                    severity TEXT,
                    category TEXT,
                    title TEXT,
                    description TEXT,
                    suggestion TEXT,
                    rule_id TEXT,
                    FOREIGN KEY (session_id) REFERENCES review_sessions (id)
                )
            ''')
    
    def review_changes(self, issue_key: str, file_paths: List[str] = None) -> Dict[str, Any]:
        """Perform comprehensive code review"""
        print("🔍 Starting AI-powered code review...")
        
        # Get changed files if not specified
        if not file_paths:
            file_paths = self._get_changed_files()
        
        all_issues = []
        total_lines = 0
        
        # Analyze each file
        for file_path in file_paths:
            if not Path(file_path).exists():
                continue
                
            print(f"📄 Analyzing {file_path}...")
            
            # Security scan
            security_issues = self.security_scanner.scan_file(file_path)
            all_issues.extend(security_issues)
            
            # Quality analysis (for Python files)
            if file_path.endswith('.py'):
                quality_issues, metrics = self.quality_analyzer.analyze_python_file(file_path)
                all_issues.extend(quality_issues)
            
            # Count lines
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        
        # Calculate scores
        metrics = self._calculate_review_metrics(all_issues, total_lines, len(file_paths))
        
        # Generate AI review summary
        ai_summary = self._generate_ai_summary(file_paths, all_issues, metrics)
        
        # Store results
        session_id = self._store_review_results(issue_key, all_issues, metrics, ai_summary)
        
        # Generate review report
        report = self._generate_review_report(issue_key, all_issues, metrics, ai_summary)
        
        return {
            'session_id': session_id,
            'files_analyzed': len(file_paths),
            'total_issues': len(all_issues),
            'metrics': metrics,
            'issues': [asdict(issue) for issue in all_issues],
            'ai_summary': ai_summary,
            'report': report
        }
    
    def _get_changed_files(self) -> List[str]:
        """Get list of changed files from git"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1..HEAD'],
                capture_output=True, text=True, check=True
            )
            return [f.strip() for f in result.stdout.split('\n') if f.strip()]
        except:
            # Fallback to staged files
            try:
                result = subprocess.run(
                    ['git', 'diff', '--cached', '--name-only'],
                    capture_output=True, text=True, check=True
                )
                return [f.strip() for f in result.stdout.split('\n') if f.strip()]
            except:
                return []
    
    def _calculate_review_metrics(self, issues: List[CodeIssue], total_lines: int, files_count: int) -> ReviewMetrics:
        """Calculate review metrics and scores"""
        security_issues = [i for i in issues if i.category == 'security']
        critical_issues = [i for i in issues if i.severity in ['critical', 'high']]
        
        # Security score (0-100, higher is better)
        security_score = max(0, 100 - (len(security_issues) * 10))
        
        # Quality score (0-100, higher is better)
        issue_density = len(issues) / max(total_lines, 1) * 1000  # issues per 1000 lines
        quality_score = max(0, 100 - (issue_density * 2))
        
        # Complexity score (simplified, 0-100, higher is better)
        complexity_issues = [i for i in issues if 'complexity' in i.rule_id or '']
        complexity_score = max(0, 100 - (len(complexity_issues) * 5))
        
        return ReviewMetrics(
            total_lines=total_lines,
            files_analyzed=files_count,
            issues_found=len(issues),
            security_score=security_score,
            quality_score=quality_score,
            complexity_score=complexity_score
        )
    
    def _generate_ai_summary(self, file_paths: List[str], issues: List[CodeIssue], metrics: ReviewMetrics) -> str:
        """Generate AI-powered review summary using Claude"""
        try:
            # Prepare review context
            context = f"""Code Review Analysis:

Files Analyzed: {len(file_paths)}
Total Lines: {metrics.total_lines}
Issues Found: {len(issues)}

Security Score: {metrics.security_score:.1f}/100
Quality Score: {metrics.quality_score:.1f}/100
Complexity Score: {metrics.complexity_score:.1f}/100

Issue Breakdown:
"""
            
            # Categorize issues
            by_severity = {}
            by_category = {}
            
            for issue in issues:
                by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
                by_category[issue.category] = by_category.get(issue.category, 0) + 1
            
            context += "Severity: " + ", ".join([f"{k}: {v}" for k, v in by_severity.items()]) + "\n"
            context += "Categories: " + ", ".join([f"{k}: {v}" for k, v in by_category.items()]) + "\n"
            
            # Use Claude to generate summary
            prompt = f"""As a senior software engineer, provide a concise code review summary based on this analysis:

{context}

Focus on:
1. Overall code quality assessment
2. Most critical issues to address
3. Specific actionable recommendations
4. Positive aspects if any

Provide a professional, constructive review in 2-3 paragraphs."""
            
            # This would integrate with Claude API in a real implementation
            # For now, return a structured summary
            return self._generate_structured_summary(by_severity, by_category, metrics)
            
        except Exception as e:
            return f"Error generating AI summary: {e}"
    
    def _generate_structured_summary(self, by_severity: Dict[str, int], by_category: Dict[str, int], metrics: ReviewMetrics) -> str:
        """Generate structured summary when AI is not available"""
        summary = f"""Code Review Summary:

Quality Assessment: {'Excellent' if metrics.quality_score >= 90 else 'Good' if metrics.quality_score >= 70 else 'Needs Improvement'}
Security Status: {'Secure' if metrics.security_score >= 90 else 'Minor Issues' if metrics.security_score >= 70 else 'Attention Required'}

"""
        
        if by_severity.get('critical', 0) > 0:
            summary += f"🚨 CRITICAL: {by_severity['critical']} critical issues require immediate attention.\n"
        
        if by_severity.get('high', 0) > 0:
            summary += f"⚠️  HIGH: {by_severity['high']} high-priority issues should be addressed.\n"
        
        if by_category.get('security', 0) > 0:
            summary += f"🔒 SECURITY: {by_category['security']} security-related findings detected.\n"
        
        summary += "\nRecommendations:\n"
        if metrics.security_score < 80:
            summary += "- Address security vulnerabilities before deployment\n"
        if metrics.quality_score < 70:
            summary += "- Improve code quality and maintainability\n"
        if metrics.complexity_score < 80:
            summary += "- Refactor complex functions for better maintainability\n"
        
        return summary
    
    def _store_review_results(self, issue_key: str, issues: List[CodeIssue], metrics: ReviewMetrics, summary: str) -> int:
        """Store review results in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO review_sessions 
                (issue_key, files_analyzed, total_issues, security_score, quality_score, review_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                issue_key, metrics.files_analyzed, len(issues),
                metrics.security_score, metrics.quality_score, summary
            ))
            
            session_id = cursor.lastrowid
            
            # Store individual issues
            for issue in issues:
                conn.execute('''
                    INSERT INTO review_issues 
                    (session_id, file_path, line_number, severity, category, title, description, suggestion, rule_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, issue.file_path, issue.line_number, issue.severity,
                    issue.category, issue.title, issue.description, issue.suggestion, issue.rule_id
                ))
            
            return session_id
    
    def _generate_review_report(self, issue_key: str, issues: List[CodeIssue], metrics: ReviewMetrics, summary: str) -> str:
        """Generate formatted review report"""
        report = f"""# Code Review Report - {issue_key}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
{summary}

## Metrics
- **Files Analyzed**: {metrics.files_analyzed}
- **Total Lines**: {metrics.total_lines}
- **Issues Found**: {len(issues)}
- **Security Score**: {metrics.security_score:.1f}/100
- **Quality Score**: {metrics.quality_score:.1f}/100
- **Complexity Score**: {metrics.complexity_score:.1f}/100

## Issues by Severity
"""
        
        by_severity = {}
        for issue in issues:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)
        
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            if severity in by_severity:
                report += f"\n### {severity.upper()} ({len(by_severity[severity])} issues)\n"
                for issue in by_severity[severity][:5]:  # Show top 5 per severity
                    report += f"- **{issue.title}** ({issue.file_path}:{issue.line_number})\n"
                    report += f"  {issue.description}\n"
                    if issue.suggestion:
                        report += f"  💡 *{issue.suggestion}*\n"
                    report += "\n"
        
        return report


def main():
    """Main entry point for code review"""
    import argparse
    from .config import load_jira_config
    
    parser = argparse.ArgumentParser(description="AI-Powered Code Review")
    parser.add_argument("issue_key", help="JIRA issue key")
    parser.add_argument("--files", nargs="+", help="Specific files to review")
    parser.add_argument("--config", help="Path to .env configuration file")
    parser.add_argument("--output", help="Output file for review report")
    
    args = parser.parse_args()
    
    try:
        config = load_jira_config(args.config)
        reviewer = AICodeReviewer(config)
        
        result = reviewer.review_changes(args.issue_key, args.files)
        
        print(f"\n🎯 Review Complete!")
        print(f"📊 Files: {result['files_analyzed']}, Issues: {result['total_issues']}")
        print(f"🔒 Security: {result['metrics'].security_score:.1f}/100")
        print(f"⭐ Quality: {result['metrics'].quality_score:.1f}/100")
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result['report'])
            print(f"📄 Report saved to: {args.output}")
        else:
            print(f"\n{result['ai_summary']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()