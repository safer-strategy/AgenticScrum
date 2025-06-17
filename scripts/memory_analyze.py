#!/usr/bin/env python3
"""
Analyze agent memory patterns and effectiveness.

This script provides insights into agent learning patterns, memory usage,
and identifies opportunities for improvement.
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available - visualization features disabled")


class MemoryAnalyzer:
    """Analyze agent memory patterns and effectiveness."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_root = self.project_path / '.agent-memory'
        
    def analyze_patterns(self, agent: Optional[str] = None, days: Optional[int] = None) -> Dict:
        """Analyze memory patterns for insights.
        
        Args:
            agent: Specific agent to analyze (None for all)
            days: Analyze memories from last N days (None for all)
            
        Returns:
            Dictionary containing analysis results
        """
        memories = self._load_memories(agent, days)
        
        if not memories:
            return {"error": "No memories found"}
            
        analysis = {
            "total_memories": len(memories),
            "memory_types": self._analyze_memory_types(memories),
            "tag_frequency": self._analyze_tags(memories),
            "temporal_patterns": self._analyze_temporal_patterns(memories),
            "outcome_analysis": self._analyze_outcomes(memories),
            "agent_activity": self._analyze_agent_activity(memories),
            "learning_velocity": self._calculate_learning_velocity(memories),
            "memory_effectiveness": self._analyze_effectiveness(memories),
            "recommendations": self._generate_recommendations(memories)
        }
        
        return analysis
        
    def _load_memories(self, agent: Optional[str], days: Optional[int]) -> List[Dict]:
        """Load memories based on criteria."""
        memories = []
        cutoff_date = None
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
        # Determine which directories to scan
        if agent:
            agent_dirs = [self.memory_root / agent]
        else:
            agent_dirs = [d for d in self.memory_root.iterdir() if d.is_dir()]
            
        for agent_dir in agent_dirs:
            if not agent_dir.exists():
                continue
                
            for jsonl_file in agent_dir.glob('*.jsonl'):
                with open(jsonl_file, 'r') as f:
                    for line in f:
                        try:
                            memory = json.loads(line.strip())
                            
                            if 'agent' not in memory:
                                memory['agent'] = agent_dir.name
                                
                            if cutoff_date and 'timestamp' in memory:
                                memory_date = datetime.fromisoformat(memory['timestamp'].rstrip('Z'))
                                if memory_date < cutoff_date:
                                    continue
                                    
                            memories.append(memory)
                            
                        except json.JSONDecodeError:
                            continue
                            
        return memories
        
    def _analyze_memory_types(self, memories: List[Dict]) -> Dict:
        """Analyze distribution of memory types."""
        type_counts = Counter(m.get('type', 'unknown') for m in memories)
        
        return {
            "distribution": dict(type_counts),
            "most_common": type_counts.most_common(5)
        }
        
    def _analyze_tags(self, memories: List[Dict]) -> Dict:
        """Analyze tag frequency and relationships."""
        tag_counts = Counter()
        tag_pairs = Counter()
        
        for memory in memories:
            tags = memory.get('tags', [])
            tag_counts.update(tags)
            
            # Count tag co-occurrences
            for i in range(len(tags)):
                for j in range(i + 1, len(tags)):
                    pair = tuple(sorted([tags[i], tags[j]]))
                    tag_pairs[pair] += 1
                    
        return {
            "frequency": dict(tag_counts.most_common(20)),
            "common_pairs": [
                {"tags": list(pair), "count": count}
                for pair, count in tag_pairs.most_common(10)
            ]
        }
        
    def _analyze_temporal_patterns(self, memories: List[Dict]) -> Dict:
        """Analyze when memories are created."""
        hourly_dist = defaultdict(int)
        daily_dist = defaultdict(int)
        
        for memory in memories:
            timestamp = memory.get('timestamp')
            if timestamp:
                dt = datetime.fromisoformat(timestamp.rstrip('Z'))
                hourly_dist[dt.hour] += 1
                daily_dist[dt.weekday()] += 1
                
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        return {
            "hourly_distribution": dict(hourly_dist),
            "daily_distribution": {
                days[k]: v for k, v in daily_dist.items()
            },
            "peak_hours": sorted(hourly_dist.items(), key=lambda x: x[1], reverse=True)[:3]
        }
        
    def _analyze_outcomes(self, memories: List[Dict]) -> Dict:
        """Analyze memory outcomes and success rates."""
        outcomes = defaultdict(lambda: {"success": 0, "total": 0})
        
        for memory in memories:
            memory_type = memory.get('type', 'unknown')
            outcome = memory.get('outcome', '')
            
            outcomes[memory_type]["total"] += 1
            
            # Simple heuristic for success
            if any(word in str(outcome).lower() for word in 
                   ['success', 'improved', 'fixed', 'resolved', 'working']):
                outcomes[memory_type]["success"] += 1
                
        # Calculate success rates
        success_rates = {}
        for memory_type, stats in outcomes.items():
            if stats["total"] > 0:
                success_rates[memory_type] = {
                    "success_rate": stats["success"] / stats["total"],
                    "total_memories": stats["total"]
                }
                
        return success_rates
        
    def _analyze_agent_activity(self, memories: List[Dict]) -> Dict:
        """Analyze activity by agent."""
        agent_stats = defaultdict(lambda: {
            "total": 0,
            "types": Counter(),
            "recent_activity": None
        })
        
        for memory in memories:
            agent = memory.get('agent', 'unknown')
            agent_stats[agent]["total"] += 1
            agent_stats[agent]["types"][memory.get('type', 'unknown')] += 1
            
            # Track most recent activity
            timestamp = memory.get('timestamp')
            if timestamp:
                dt = datetime.fromisoformat(timestamp.rstrip('Z'))
                if (agent_stats[agent]["recent_activity"] is None or 
                    dt > agent_stats[agent]["recent_activity"]):
                    agent_stats[agent]["recent_activity"] = dt
                    
        # Convert to serializable format
        result = {}
        for agent, stats in agent_stats.items():
            result[agent] = {
                "total_memories": stats["total"],
                "memory_types": dict(stats["types"]),
                "most_common_type": stats["types"].most_common(1)[0] if stats["types"] else None,
                "last_activity": stats["recent_activity"].isoformat() if stats["recent_activity"] else None
            }
            
        return result
        
    def _calculate_learning_velocity(self, memories: List[Dict]) -> Dict:
        """Calculate how fast agents are learning (memories per time period)."""
        if not memories:
            return {}
            
        # Sort memories by timestamp
        dated_memories = []
        for memory in memories:
            timestamp = memory.get('timestamp')
            if timestamp:
                dt = datetime.fromisoformat(timestamp.rstrip('Z'))
                dated_memories.append((dt, memory))
                
        if not dated_memories:
            return {}
            
        dated_memories.sort(key=lambda x: x[0])
        
        # Calculate velocity over different time windows
        now = datetime.utcnow()
        velocities = {}
        
        for window_name, days in [("daily", 1), ("weekly", 7), ("monthly", 30)]:
            window_start = now - timedelta(days=days)
            window_memories = [m for dt, m in dated_memories if dt > window_start]
            velocities[window_name] = len(window_memories) / days
            
        return velocities
        
    def _analyze_effectiveness(self, memories: List[Dict]) -> Dict:
        """Analyze memory effectiveness based on reuse and outcomes."""
        pattern_reuse = defaultdict(int)
        solution_effectiveness = []
        
        for memory in memories:
            # Check if this memory references a pattern
            if 'pattern' in memory:
                pattern_reuse[memory['pattern']] += 1
                
            # Check solution effectiveness
            if 'solution' in memory and 'outcome' in memory:
                solution_effectiveness.append({
                    "solution": memory['solution'][:50],  # Truncate for display
                    "outcome": memory.get('outcome', 'unknown'),
                    "effectiveness": memory.get('effectiveness', 'unknown')
                })
                
        return {
            "most_reused_patterns": sorted(pattern_reuse.items(), 
                                         key=lambda x: x[1], reverse=True)[:10],
            "solution_count": len(solution_effectiveness),
            "top_solutions": solution_effectiveness[:5]
        }
        
    def _generate_recommendations(self, memories: List[Dict]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Check memory volume
        if len(memories) < 10:
            recommendations.append("Low memory volume - agents may need more time to build knowledge")
            
        # Check memory diversity
        memory_types = set(m.get('type') for m in memories)
        if len(memory_types) < 3:
            recommendations.append("Limited memory diversity - encourage agents to store different types of knowledge")
            
        # Check for recent activity
        recent_memories = [m for m in memories 
                          if 'timestamp' in m and 
                          datetime.fromisoformat(m['timestamp'].rstrip('Z')) > 
                          datetime.utcnow() - timedelta(days=7)]
        
        if not recent_memories:
            recommendations.append("No recent memory activity - check if agents are actively learning")
            
        # Check for failed patterns
        failed_patterns = [m for m in memories 
                          if 'outcome' in m and 
                          any(word in str(m['outcome']).lower() 
                              for word in ['failed', 'error', 'issue'])]
        
        if len(failed_patterns) > len(memories) * 0.3:
            recommendations.append("High failure rate - review and update agent strategies")
            
        return recommendations
        
    def generate_report(self, analysis: Dict, output_file: Optional[str] = None) -> None:
        """Generate a comprehensive analysis report."""
        report = []
        report.append("# Agent Memory Analysis Report")
        report.append(f"\nGenerated: {datetime.utcnow().isoformat()}")
        report.append(f"\nTotal Memories Analyzed: {analysis.get('total_memories', 0)}")
        
        # Memory Types
        report.append("\n## Memory Type Distribution")
        for memory_type, count in analysis['memory_types']['most_common']:
            report.append(f"- {memory_type}: {count}")
            
        # Agent Activity
        report.append("\n## Agent Activity Summary")
        for agent, stats in analysis['agent_activity'].items():
            report.append(f"\n### {agent}")
            report.append(f"- Total memories: {stats['total_memories']}")
            report.append(f"- Most common type: {stats['most_common_type']}")
            report.append(f"- Last activity: {stats['last_activity']}")
            
        # Learning Velocity
        report.append("\n## Learning Velocity")
        for period, velocity in analysis.get('learning_velocity', {}).items():
            report.append(f"- {period}: {velocity:.2f} memories/day")
            
        # Recommendations
        report.append("\n## Recommendations")
        for rec in analysis.get('recommendations', []):
            report.append(f"- {rec}")
            
        report_text = '\n'.join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
        else:
            print(report_text)
            
    def visualize_patterns(self, analysis: Dict, output_dir: Optional[str] = None) -> None:
        """Create visualizations of memory patterns."""
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlib is not installed. Install with: pip install matplotlib")
            return
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
        else:
            output_path = Path('.')
            
        # Memory type distribution pie chart
        if 'memory_types' in analysis and analysis['memory_types']['distribution']:
            plt.figure(figsize=(10, 8))
            types = list(analysis['memory_types']['distribution'].keys())
            counts = list(analysis['memory_types']['distribution'].values())
            plt.pie(counts, labels=types, autopct='%1.1f%%')
            plt.title('Memory Type Distribution')
            plt.savefig(output_path / 'memory_types.png')
            plt.close()
            
        # Temporal patterns
        if 'temporal_patterns' in analysis:
            # Hourly distribution
            hourly = analysis['temporal_patterns']['hourly_distribution']
            if hourly:
                plt.figure(figsize=(12, 6))
                hours = sorted(hourly.keys())
                values = [hourly.get(h, 0) for h in hours]
                plt.bar(hours, values)
                plt.xlabel('Hour of Day')
                plt.ylabel('Memory Count')
                plt.title('Memory Creation by Hour')
                plt.savefig(output_path / 'hourly_distribution.png')
                plt.close()


def main():
    parser = argparse.ArgumentParser(description='Analyze agent memory patterns')
    parser.add_argument('--project', default='.', help='Project root directory')
    parser.add_argument('--agent', help='Analyze specific agent')
    parser.add_argument('--days', type=int, help='Analyze memories from last N days')
    parser.add_argument('--report', help='Generate report to file')
    parser.add_argument('--visualize', help='Generate visualizations to directory')
    parser.add_argument('--json', action='store_true', help='Output analysis as JSON')
    
    args = parser.parse_args()
    
    analyzer = MemoryAnalyzer(args.project)
    analysis = analyzer.analyze_patterns(args.agent, args.days)
    
    if args.json:
        print(json.dumps(analysis, indent=2, default=str))
    else:
        analyzer.generate_report(analysis, args.report)
        
    if args.visualize:
        analyzer.visualize_patterns(analysis, args.visualize)
        logger.info(f"Visualizations saved to {args.visualize}")


if __name__ == '__main__':
    main()