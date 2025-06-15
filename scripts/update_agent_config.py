#!/usr/bin/env python3
"""Automatically update agent configurations based on feedback."""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta

class AgentConfigUpdater:
    """Automatically update agent configurations based on feedback."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.agents_path = project_path / "agents"
        self.feedback_path = project_path / "feedback"
        self.feedback_path.mkdir(exist_ok=True)
    
    def analyze_feedback(self, agent_name: str, days: int = 30) -> Dict[str, Any]:
        """Analyze recent feedback for an agent."""
        feedback_files = list(self.feedback_path.glob(f"{agent_name}_*.json"))
        
        recent_feedback = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file in feedback_files:
            with open(file) as f:
                data = json.load(f)
                if datetime.fromisoformat(data["timestamp"]) > cutoff_date:
                    recent_feedback.append(data)
        
        return self._aggregate_feedback(recent_feedback)
    
    def _aggregate_feedback(self, feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate feedback to identify patterns."""
        if not feedback:
            return {}
        
        aggregated = {
            "total_feedback": len(feedback),
            "average_scores": {},
            "common_issues": {},
            "suggested_rules": [],
            "performance_trends": {}
        }
        
        # Calculate average scores
        score_categories = [
            "functional_correctness", "code_structure", "readability",
            "performance", "testing", "documentation"
        ]
        
        for category in score_categories:
            scores = [f["scores"][category] for f in feedback if category in f.get("scores", {})]
            if scores:
                aggregated["average_scores"][category] = sum(scores) / len(scores)
        
        # Identify common issues
        all_issues = []
        for f in feedback:
            all_issues.extend(f.get("issues", []))
        
        # Count issue frequencies
        issue_counts = {}
        for issue in all_issues:
            issue_type = issue.get("type", "unknown")
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        aggregated["common_issues"] = issue_counts
        
        # Collect suggested rules
        for f in feedback:
            aggregated["suggested_rules"].extend(f.get("suggested_rules", []))
        
        return aggregated
    
    def generate_config_updates(self, agent_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate configuration updates based on analysis."""
        updates = {
            "persona_rules_updates": {},
            "priming_script_updates": [],
            "llm_config_updates": {}
        }
        
        # Update temperature based on consistency issues
        avg_scores = analysis.get("average_scores", {})
        if avg_scores.get("functional_correctness", 5) < 4:
            updates["llm_config_updates"]["temperature"] = 0.2  # Lower for more consistency
        
        # Add rules based on common issues
        common_issues = analysis.get("common_issues", {})
        new_rules = []
        
        if "missing_error_handling" in common_issues:
            new_rules.extend([
                "ALWAYS wrap external calls in try-except blocks",
                "ALWAYS provide meaningful error messages",
                "ALWAYS log errors with appropriate context"
            ])
        
        if "poor_test_coverage" in common_issues:
            new_rules.extend([
                "ALWAYS write tests before implementing functionality",
                "ENSURE test coverage exceeds 90% for new code",
                "ALWAYS test edge cases and error paths"
            ])
        
        if "complex_functions" in common_issues:
            new_rules.extend([
                "LIMIT function length to 30 lines maximum",
                "EXTRACT complex logic into helper functions",
                "ENSURE cyclomatic complexity stays below 10"
            ])
        
        # Add performance rules if needed
        if avg_scores.get("performance", 5) < 3.5:
            new_rules.extend([
                "PROFILE code for functions processing large datasets",
                "USE generators instead of lists for large iterations",
                "IMPLEMENT caching for expensive computations"
            ])
        
        if new_rules:
            updates["persona_rules_updates"]["rules"] = new_rules
        
        return updates
    
    def apply_updates(self, agent_name: str, updates: Dict[str, Any], dry_run: bool = True):
        """Apply updates to agent configuration files."""
        agent_dir = self.agents_path / self._get_agent_directory(agent_name)
        
        if not agent_dir.exists():
            print(f"Agent directory not found: {agent_dir}")
            return None
        
        # Update persona_rules.yaml
        if updates.get("persona_rules_updates"):
            persona_file = agent_dir / "persona_rules.yaml"
            
            if not persona_file.exists():
                print(f"Persona rules file not found: {persona_file}")
                return None
            
            with open(persona_file) as f:
                current_config = yaml.safe_load(f)
            
            # Merge updates
            for key, value in updates["persona_rules_updates"].items():
                if key == "rules" and isinstance(value, list):
                    current_rules = current_config.get("rules", [])
                    # Add new rules if not already present
                    for rule in value:
                        if rule not in current_rules:
                            current_rules.append(rule)
                    current_config["rules"] = current_rules
                elif key in ["llm_config"]:
                    # Merge llm_config updates
                    if key not in current_config:
                        current_config[key] = {}
                    current_config[key].update(value)
                else:
                    current_config[key] = value
            
            if not dry_run:
                # Backup current config
                backup_file = persona_file.with_suffix(".yaml.bak")
                with open(backup_file, "w") as f:
                    yaml.dump(current_config, f, default_flow_style=False)
                
                # Write updated config
                with open(persona_file, "w") as f:
                    yaml.dump(current_config, f, default_flow_style=False, sort_keys=False)
                
                print(f"Updated {persona_file}")
            else:
                print("Dry run - changes to be applied:")
                print(yaml.dump(updates, default_flow_style=False))
            
            return current_config
    
    def _get_agent_directory(self, agent_name: str) -> str:
        """Get the directory name for an agent."""
        agent_mapping = {
            "poa": "product_owner_agent",
            "sma": "scrum_master_agent",
            "deva_python": "developer_agent/python_expert",
            "deva_javascript": "developer_agent/javascript_expert",
            "deva_typescript": "developer_agent/typescript_expert",
            "qaa": "qa_agent",
            "saa": "security_audit_agent"
        }
        return agent_mapping.get(agent_name, agent_name)
    
    def recommend_updates(self, agent_name: str) -> Dict[str, Any]:
        """Generate recommendations based on feedback analysis."""
        analysis = self.analyze_feedback(agent_name)
        
        if not analysis:
            return {"message": "No feedback data found"}
        
        updates = self.generate_config_updates(agent_name, analysis)
        
        recommendations = {
            "agent": agent_name,
            "analysis_summary": {
                "total_feedback": analysis["total_feedback"],
                "average_scores": analysis["average_scores"],
                "top_issues": dict(sorted(
                    analysis["common_issues"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5])
            },
            "recommended_updates": updates,
            "priority": self._calculate_priority(analysis)
        }
        
        return recommendations
    
    def _calculate_priority(self, analysis: Dict[str, Any]) -> str:
        """Calculate update priority based on analysis."""
        avg_scores = analysis.get("average_scores", {})
        
        # Calculate overall score
        if avg_scores:
            overall_score = sum(avg_scores.values()) / len(avg_scores)
            
            if overall_score < 3.0:
                return "high"
            elif overall_score < 4.0:
                return "medium"
            else:
                return "low"
        
        return "medium"


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update agent configurations based on feedback")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze feedback for an agent")
    analyze_parser.add_argument("--agent", required=True, help="Agent name")
    analyze_parser.add_argument("--days", type=int, default=30, help="Days to look back")
    
    # Recommend command
    recommend_parser = subparsers.add_parser("recommend", help="Generate recommendations")
    recommend_parser.add_argument("--agent", required=True, help="Agent name")
    recommend_parser.add_argument("--all-agents", action="store_true", help="Analyze all agents")
    
    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply configuration updates")
    apply_parser.add_argument("--agent", required=True, help="Agent name")
    apply_parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    apply_parser.add_argument("--confirm", action="store_true", help="Apply changes without dry run")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    updater = AgentConfigUpdater(Path("."))
    
    if args.command == "analyze":
        analysis = updater.analyze_feedback(args.agent, args.days)
        print(json.dumps(analysis, indent=2))
    
    elif args.command == "recommend":
        if args.all_agents:
            agents = ["poa", "sma", "deva_python", "deva_javascript", "qaa", "saa"]
            for agent in agents:
                recommendations = updater.recommend_updates(agent)
                print(f"\n=== {agent} ===")
                print(json.dumps(recommendations, indent=2))
        else:
            recommendations = updater.recommend_updates(args.agent)
            print(json.dumps(recommendations, indent=2))
    
    elif args.command == "apply":
        analysis = updater.analyze_feedback(args.agent)
        updates = updater.generate_config_updates(args.agent, analysis)
        
        if args.confirm:
            updater.apply_updates(args.agent, updates, dry_run=False)
        else:
            updater.apply_updates(args.agent, updates, dry_run=not args.dry_run)


if __name__ == "__main__":
    main()