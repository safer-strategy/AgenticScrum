#!/usr/bin/env python3
"""Collect quality metrics for agent-generated code."""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class AgentMetricsCollector:
    """Collect quality metrics for agent-generated code."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.metrics_path = project_path / "metrics" / "agent_performance"
        self.metrics_path.mkdir(parents=True, exist_ok=True)
    
    def collect_code_metrics(self, agent_name: str, file_path: Path) -> Dict[str, Any]:
        """Collect metrics for a specific file."""
        metrics = {
            "agent": agent_name,
            "file": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        # Code complexity (using radon)
        complexity = self._get_complexity(file_path)
        metrics["metrics"]["complexity"] = complexity
        
        # Test coverage
        coverage = self._get_coverage(file_path)
        metrics["metrics"]["coverage"] = coverage
        
        # Linting scores
        lint_score = self._get_lint_score(file_path)
        metrics["metrics"]["lint_score"] = lint_score
        
        # Type checking
        type_check = self._check_types(file_path)
        metrics["metrics"]["type_check_passed"] = type_check
        
        # Performance benchmarks
        if file_path.suffix == ".py":
            performance = self._benchmark_performance(file_path)
            metrics["metrics"]["performance"] = performance
        
        return metrics
    
    def _get_complexity(self, file_path: Path) -> Dict[str, float]:
        """Calculate cyclomatic complexity."""
        try:
            result = subprocess.run(
                ["radon", "cc", str(file_path), "-j"],
                capture_output=True,
                text=True
            )
            data = json.loads(result.stdout)
            
            total_complexity = 0
            function_count = 0
            
            for file_data in data.values():
                for func in file_data:
                    total_complexity += func["complexity"]
                    function_count += 1
            
            avg_complexity = total_complexity / function_count if function_count > 0 else 0
            
            return {
                "average": avg_complexity,
                "total": total_complexity,
                "functions": function_count
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_coverage(self, file_path: Path) -> float:
        """Get test coverage percentage."""
        try:
            # Run coverage for specific file
            subprocess.run(
                ["coverage", "run", "-m", "pytest", f"tests/test_{file_path.stem}.py"],
                capture_output=True
            )
            
            result = subprocess.run(
                ["coverage", "report", "--include", str(file_path)],
                capture_output=True,
                text=True
            )
            
            # Parse coverage percentage from output
            lines = result.stdout.strip().split("\n")
            for line in lines:
                if str(file_path) in line:
                    parts = line.split()
                    return float(parts[-1].rstrip("%"))
            
            return 0.0
        except Exception:
            return 0.0
    
    def _get_lint_score(self, file_path: Path) -> float:
        """Get linting score using pylint or similar."""
        try:
            if file_path.suffix == ".py":
                result = subprocess.run(
                    ["pylint", str(file_path), "--output-format=json"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    data = json.loads(result.stdout)
                    # Calculate score based on messages
                    total_issues = len(data)
                    # Simple scoring: start at 10 and subtract 0.5 for each issue
                    score = max(0, 10 - (total_issues * 0.5))
                    return score
            
            return 10.0  # Default perfect score if no linter
        except Exception:
            return 0.0
    
    def _check_types(self, file_path: Path) -> bool:
        """Check type annotations using mypy or similar."""
        try:
            if file_path.suffix == ".py":
                result = subprocess.run(
                    ["mypy", str(file_path)],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            
            return True  # Assume types are fine for non-Python
        except Exception:
            return False
    
    def _benchmark_performance(self, file_path: Path) -> Dict[str, float]:
        """Run performance benchmarks if applicable."""
        # This is a placeholder - implement based on your specific needs
        return {
            "execution_time": 0.0,
            "memory_usage": 0.0
        }
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{metrics['agent']}_{timestamp}.json"
        
        with open(self.metrics_path / filename, "w") as f:
            json.dump(metrics, f, indent=2)
    
    def generate_report(self, agent_name: str, days: int = 30) -> Dict[str, Any]:
        """Generate performance report for an agent."""
        # Load all metrics for the agent
        metrics_files = list(self.metrics_path.glob(f"{agent_name}_*.json"))
        
        all_metrics = []
        cutoff_date = datetime.now().timestamp() - (days * 86400)
        
        for file in metrics_files:
            with open(file) as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data["timestamp"]).timestamp()
                if timestamp > cutoff_date:
                    all_metrics.append(data)
        
        # Calculate trends and averages
        report = {
            "agent": agent_name,
            "period_days": days,
            "total_files_generated": len(all_metrics),
            "metrics_summary": self._calculate_summary(all_metrics)
        }
        
        return report
    
    def _calculate_summary(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        if not metrics:
            return {}
        
        summary = {
            "average_complexity": 0,
            "average_coverage": 0,
            "lint_pass_rate": 0,
            "type_check_pass_rate": 0
        }
        
        complexities = []
        coverages = []
        lint_passes = 0
        type_passes = 0
        
        for m in metrics:
            metric_data = m.get("metrics", {})
            
            if "complexity" in metric_data and "average" in metric_data["complexity"]:
                complexities.append(metric_data["complexity"]["average"])
            
            if "coverage" in metric_data:
                coverages.append(metric_data["coverage"])
            
            if metric_data.get("lint_score", 0) > 8:
                lint_passes += 1
            
            if metric_data.get("type_check_passed", False):
                type_passes += 1
        
        if complexities:
            summary["average_complexity"] = sum(complexities) / len(complexities)
        
        if coverages:
            summary["average_coverage"] = sum(coverages) / len(coverages)
        
        if metrics:
            summary["lint_pass_rate"] = (lint_passes / len(metrics)) * 100
            summary["type_check_pass_rate"] = (type_passes / len(metrics)) * 100
        
        return summary


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect metrics for agent-generated code")
    parser.add_argument("--agent", required=True, help="Agent name (e.g., deva_python)")
    parser.add_argument("--file", required=True, help="File path to analyze")
    parser.add_argument("--project-path", default=".", help="Project root path")
    parser.add_argument("--save", action="store_true", help="Save metrics to file")
    
    args = parser.parse_args()
    
    collector = AgentMetricsCollector(Path(args.project_path))
    metrics = collector.collect_code_metrics(args.agent, Path(args.file))
    
    print(json.dumps(metrics, indent=2))
    
    if args.save:
        collector.save_metrics(metrics)
        print(f"Metrics saved to {collector.metrics_path}")


if __name__ == "__main__":
    main()