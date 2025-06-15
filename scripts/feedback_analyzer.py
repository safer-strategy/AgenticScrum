#!/usr/bin/env python3
"""Analyze agent feedback and suggest improvements."""

import json
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class FeedbackAnalyzer:
    """Analyze feedback patterns and suggest agent improvements."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.feedback_path = project_path / "feedback"
        self.metrics_path = project_path / "metrics"
        
    def analyze_agent_performance(self, agent_name: str, days: int = 30) -> Dict:
        """Comprehensive analysis of agent performance."""
        
        # Collect all feedback data
        feedback_data = self._load_feedback_data(agent_name, days)
        metrics_data = self._load_metrics_data(agent_name, days)
        
        # Analyze patterns
        analysis = {
            "agent": agent_name,
            "period_days": days,
            "feedback_count": len(feedback_data),
            "metrics_count": len(metrics_data),
            "performance_summary": self._calculate_performance_summary(feedback_data, metrics_data),
            "issue_patterns": self._identify_issue_patterns(feedback_data),
            "improvement_trends": self._calculate_improvement_trends(feedback_data, metrics_data),
            "recommended_updates": self._generate_recommendations(feedback_data, metrics_data)
        }
        
        return analysis
    
    def _load_feedback_data(self, agent_name: str, days: int) -> List[Dict]:
        """Load feedback data for the specified period."""
        feedback_data = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if not self.feedback_path.exists():
            return feedback_data
        
        for file in self.feedback_path.glob(f"{agent_name}_*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    if datetime.fromisoformat(data.get("timestamp", "2000-01-01")) > cutoff_date:
                        feedback_data.append(data)
            except Exception as e:
                print(f"Error loading {file}: {e}")
        
        return feedback_data
    
    def _load_metrics_data(self, agent_name: str, days: int) -> List[Dict]:
        """Load metrics data for the specified period."""
        metrics_data = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        metrics_dir = self.metrics_path / "agent_performance"
        if not metrics_dir.exists():
            return metrics_data
        
        for file in metrics_dir.glob(f"{agent_name}_*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    if datetime.fromisoformat(data.get("timestamp", "2000-01-01")) > cutoff_date:
                        metrics_data.append(data)
            except Exception as e:
                print(f"Error loading {file}: {e}")
        
        return metrics_data
    
    def _calculate_performance_summary(self, feedback_data: List[Dict], metrics_data: List[Dict]) -> Dict:
        """Calculate overall performance summary."""
        summary = {
            "overall_score": 0.0,
            "avg_complexity": 0.0,
            "avg_coverage": 0.0,
            "doc_completeness": 0.0,
            "error_rate": 0.0
        }
        
        # Calculate from feedback
        if feedback_data:
            all_scores = []
            for feedback in feedback_data:
                scores = feedback.get("scores", {})
                if scores:
                    avg_score = sum(scores.values()) / len(scores)
                    all_scores.append(avg_score)
            
            if all_scores:
                summary["overall_score"] = sum(all_scores) / len(all_scores)
        
        # Calculate from metrics
        if metrics_data:
            complexities = []
            coverages = []
            
            for metric in metrics_data:
                m = metric.get("metrics", {})
                if "complexity" in m and "average" in m["complexity"]:
                    complexities.append(m["complexity"]["average"])
                if "coverage" in m:
                    coverages.append(m["coverage"])
            
            if complexities:
                summary["avg_complexity"] = sum(complexities) / len(complexities)
            if coverages:
                summary["avg_coverage"] = sum(coverages) / len(coverages)
        
        return summary
    
    def _identify_issue_patterns(self, feedback_data: List[Dict]) -> Dict:
        """Identify recurring issues from feedback."""
        
        issue_frequency = defaultdict(int)
        issue_severity = defaultdict(list)
        issue_examples = defaultdict(list)
        
        for feedback in feedback_data:
            for issue in feedback.get("issues", []):
                issue_type = issue.get("type", "unknown")
                issue_frequency[issue_type] += 1
                issue_severity[issue_type].append(
                    {"high": 3, "medium": 2, "low": 1}.get(issue.get("severity", "medium"), 2)
                )
                issue_examples[issue_type].append({
                    "file": issue.get("file"),
                    "description": issue.get("description")
                })
        
        # Calculate pattern strength
        patterns = {}
        for issue_type, frequency in issue_frequency.items():
            avg_severity_scores = issue_severity[issue_type]
            patterns[issue_type] = {
                "frequency": frequency,
                "percentage": (frequency / len(feedback_data)) * 100 if feedback_data else 0,
                "avg_severity": sum(avg_severity_scores) / len(avg_severity_scores) if avg_severity_scores else 0,
                "examples": issue_examples[issue_type][:3]  # Top 3 examples
            }
        
        return dict(sorted(patterns.items(), key=lambda x: x[1]["frequency"], reverse=True))
    
    def _calculate_improvement_trends(self, feedback_data: List[Dict], metrics_data: List[Dict]) -> Dict:
        """Calculate improvement trends over time."""
        # Group by week
        weekly_scores = defaultdict(list)
        weekly_metrics = defaultdict(list)
        
        for feedback in feedback_data:
            timestamp = datetime.fromisoformat(feedback.get("timestamp", "2000-01-01"))
            week = timestamp.isocalendar()[1]
            scores = feedback.get("scores", {})
            if scores:
                avg_score = sum(scores.values()) / len(scores)
                weekly_scores[week].append(avg_score)
        
        for metric in metrics_data:
            timestamp = datetime.fromisoformat(metric.get("timestamp", "2000-01-01"))
            week = timestamp.isocalendar()[1]
            weekly_metrics[week].append(metric.get("metrics", {}))
        
        # Calculate weekly averages
        trends = {
            "weekly_scores": {},
            "weekly_complexity": {},
            "weekly_coverage": {}
        }
        
        for week, scores in weekly_scores.items():
            if scores:
                trends["weekly_scores"][week] = sum(scores) / len(scores)
        
        for week, metrics in weekly_metrics.items():
            complexities = []
            coverages = []
            
            for m in metrics:
                if "complexity" in m and "average" in m["complexity"]:
                    complexities.append(m["complexity"]["average"])
                if "coverage" in m:
                    coverages.append(m["coverage"])
            
            if complexities:
                trends["weekly_complexity"][week] = sum(complexities) / len(complexities)
            if coverages:
                trends["weekly_coverage"][week] = sum(coverages) / len(coverages)
        
        return trends
    
    def _generate_recommendations(self, feedback_data: List[Dict], metrics_data: List[Dict]) -> Dict:
        """Generate specific recommendations for agent improvement."""
        
        recommendations = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }
        
        # Analyze issue patterns
        issue_patterns = self._identify_issue_patterns(feedback_data)
        
        for issue_type, pattern in issue_patterns.items():
            if pattern["frequency"] > 5 or pattern["avg_severity"] > 2.5:
                priority = "high_priority"
            elif pattern["frequency"] > 2:
                priority = "medium_priority"
            else:
                priority = "low_priority"
            
            recommendation = self._create_recommendation(issue_type, pattern)
            recommendations[priority].append(recommendation)
        
        return recommendations
    
    def _create_recommendation(self, issue_type: str, pattern: Dict) -> Dict:
        """Create specific recommendation based on issue type."""
        
        recommendations_map = {
            "missing_error_handling": {
                "rules": [
                    "ALWAYS wrap external API calls in try-except blocks",
                    "ALWAYS provide specific error messages for debugging",
                    "ALWAYS log errors with appropriate context"
                ],
                "priming": "Include comprehensive error handling examples for all external integrations"
            },
            "poor_test_coverage": {
                "rules": [
                    "ALWAYS write tests before implementation (TDD)",
                    "ENSURE minimum 90% code coverage for new code",
                    "ALWAYS test error paths and edge cases"
                ],
                "priming": "Emphasize test-driven development with examples"
            },
            "complex_functions": {
                "rules": [
                    "LIMIT function length to 30 lines maximum",
                    "EXTRACT complex logic into well-named helper functions",
                    "APPLY single responsibility principle strictly"
                ],
                "priming": "Show examples of well-decomposed functions"
            },
            "missing_documentation": {
                "rules": [
                    "ALWAYS include comprehensive docstrings for all public functions",
                    "ALWAYS document complex algorithms with inline comments",
                    "ALWAYS update README when adding new features"
                ],
                "priming": "Provide documentation templates and examples"
            }
        }
        
        base_recommendation = recommendations_map.get(issue_type, {
            "rules": [f"Address {issue_type} issues"],
            "priming": f"Add examples for handling {issue_type}"
        })
        
        return {
            "issue_type": issue_type,
            "frequency": pattern["frequency"],
            "impact": pattern["avg_severity"],
            "recommended_rules": base_recommendation["rules"],
            "priming_updates": base_recommendation["priming"],
            "examples": pattern["examples"]
        }
    
    def generate_performance_report(self, agent_name: str, output_path: Path):
        """Generate comprehensive performance report."""
        
        analysis = self.analyze_agent_performance(agent_name)
        
        # Create report
        report = f"""# Agent Performance Report: {agent_name}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Period: Last {analysis['period_days']} days

## Executive Summary

- **Total Feedback Entries**: {analysis['feedback_count']}
- **Total Metrics Collected**: {analysis['metrics_count']}
- **Overall Performance Score**: {analysis['performance_summary']['overall_score']:.2f}/5.0

## Performance Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Code Complexity | {analysis['performance_summary']['avg_complexity']:.1f} | <10 | {'✅' if analysis['performance_summary']['avg_complexity'] < 10 else '⚠️'} |
| Test Coverage | {analysis['performance_summary']['avg_coverage']:.1f}% | >85% | {'✅' if analysis['performance_summary']['avg_coverage'] > 85 else '⚠️'} |
| Documentation | {analysis['performance_summary']['doc_completeness']:.1f}% | 100% | {'✅' if analysis['performance_summary']['doc_completeness'] == 100 else '⚠️'} |

## Top Issues

"""
        
        # Add issue patterns
        for issue_type, pattern in list(analysis['issue_patterns'].items())[:5]:
            report += f"""### {issue_type.replace('_', ' ').title()}
- **Frequency**: {pattern['frequency']} occurrences ({pattern['percentage']:.1f}% of reviews)
- **Average Severity**: {pattern['avg_severity']:.1f}/3.0

"""
        
        # Add recommendations
        report += "\n## Recommendations\n"
        
        for priority in ['high_priority', 'medium_priority', 'low_priority']:
            if analysis['recommended_updates'][priority]:
                report += f"\n### {priority.replace('_', ' ').title()}\n"
                for rec in analysis['recommended_updates'][priority]:
                    report += f"\n#### {rec['issue_type'].replace('_', ' ').title()}\n"
                    report += "\n**Suggested Rules:**\n"
                    for rule in rec['recommended_rules']:
                        report += f"- {rule}\n"
        
        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        
        print(f"Report saved to {output_path}")


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze agent feedback and performance")
    parser.add_argument("--agent", help="Agent name to analyze")
    parser.add_argument("--all-agents", action="store_true", help="Analyze all agents")
    parser.add_argument("--days", type=int, default=30, help="Days to look back")
    parser.add_argument("--output", help="Output directory for reports")
    
    args = parser.parse_args()
    
    analyzer = FeedbackAnalyzer(Path("."))
    
    agents = []
    if args.all_agents:
        agents = ["poa", "sma", "deva_python", "deva_javascript", "deva_typescript", "qaa", "saa"]
    elif args.agent:
        agents = [args.agent]
    else:
        parser.print_help()
        return
    
    output_dir = Path(args.output) if args.output else Path("reports")
    
    for agent in agents:
        print(f"\nAnalyzing {agent}...")
        output_path = output_dir / f"{agent}_performance_report.md"
        analyzer.generate_performance_report(agent, output_path)


if __name__ == "__main__":
    main()