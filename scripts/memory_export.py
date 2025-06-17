#!/usr/bin/env python3
"""
Export agent memories for backup or analysis.

This script allows you to export memories from the AgenticScrum agent memory system
for backup, analysis, or migration purposes.
"""

import argparse
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MemoryExporter:
    """Export agent memories in various formats."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_root = self.project_path / '.agent-memory'
        
    def export_memories(self, agent: Optional[str] = None, days: Optional[int] = None,
                       output_format: str = 'json', output_file: Optional[str] = None) -> None:
        """Export memories based on criteria.
        
        Args:
            agent: Specific agent to export (None for all agents)
            days: Export memories from last N days (None for all)
            output_format: Export format ('json' or 'csv')
            output_file: Output file path (None for stdout)
        """
        memories = self._collect_memories(agent, days)
        
        if output_format == 'json':
            self._export_json(memories, output_file)
        elif output_format == 'csv':
            self._export_csv(memories, output_file)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
            
        logger.info(f"Exported {len(memories)} memories")
        
    def _collect_memories(self, agent: Optional[str], days: Optional[int]) -> List[Dict]:
        """Collect memories based on criteria."""
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
                logger.warning(f"Agent directory not found: {agent_dir}")
                continue
                
            # Scan all JSONL files in the agent directory
            for jsonl_file in agent_dir.glob('*.jsonl'):
                with open(jsonl_file, 'r') as f:
                    for line in f:
                        try:
                            memory = json.loads(line.strip())
                            
                            # Add agent info if not present
                            if 'agent' not in memory:
                                memory['agent'] = agent_dir.name
                                
                            # Check date filter
                            if cutoff_date and 'timestamp' in memory:
                                memory_date = datetime.fromisoformat(memory['timestamp'].rstrip('Z'))
                                if memory_date < cutoff_date:
                                    continue
                                    
                            memories.append(memory)
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing memory in {jsonl_file}: {e}")
                            
        # Sort by timestamp (newest first)
        memories.sort(key=lambda m: m.get('timestamp', ''), reverse=True)
        
        return memories
        
    def _export_json(self, memories: List[Dict], output_file: Optional[str]) -> None:
        """Export memories as JSON."""
        export_data = {
            'export_date': datetime.utcnow().isoformat() + 'Z',
            'project_path': str(self.project_path),
            'memory_count': len(memories),
            'memories': memories
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
        else:
            print(json.dumps(export_data, indent=2))
            
    def _export_csv(self, memories: List[Dict], output_file: Optional[str]) -> None:
        """Export memories as CSV."""
        if not memories:
            logger.warning("No memories to export")
            return
            
        # Get all unique keys from memories
        all_keys = set()
        for memory in memories:
            all_keys.update(memory.keys())
            
        # Sort keys for consistent column order
        fieldnames = sorted(all_keys)
        
        if output_file:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(memories)
        else:
            # For stdout, use a simpler format
            for memory in memories:
                print(','.join(str(memory.get(k, '')) for k in fieldnames))


class MemoryImporter:
    """Import memories from backup files."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_root = self.project_path / '.agent-memory'
        
    def import_memories(self, import_file: str, merge: bool = True) -> None:
        """Import memories from a backup file.
        
        Args:
            import_file: Path to import file
            merge: If True, merge with existing memories; if False, replace
        """
        with open(import_file, 'r') as f:
            data = json.load(f)
            
        memories = data.get('memories', [])
        logger.info(f"Importing {len(memories)} memories")
        
        # Group memories by agent
        memories_by_agent = {}
        for memory in memories:
            agent = memory.get('agent', 'shared')
            if agent not in memories_by_agent:
                memories_by_agent[agent] = []
            memories_by_agent[agent].append(memory)
            
        # Import memories for each agent
        for agent, agent_memories in memories_by_agent.items():
            self._import_agent_memories(agent, agent_memories, merge)
            
        logger.info("Import completed")
        
    def _import_agent_memories(self, agent: str, memories: List[Dict], merge: bool) -> None:
        """Import memories for a specific agent."""
        agent_dir = self.memory_root / agent
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine the main memory file
        memory_file = agent_dir / 'main.jsonl'
        
        if not merge and memory_file.exists():
            # Backup existing file
            backup_file = memory_file.with_suffix('.jsonl.bak')
            memory_file.rename(backup_file)
            logger.info(f"Backed up existing memories to {backup_file}")
            
        # Write memories
        with open(memory_file, 'a' if merge else 'w') as f:
            for memory in memories:
                f.write(json.dumps(memory) + '\n')
                
        logger.info(f"Imported {len(memories)} memories for agent: {agent}")


def main():
    parser = argparse.ArgumentParser(description='Export and import agent memories')
    parser.add_argument('--project', default='.', help='Project root directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export memories')
    export_parser.add_argument('--agent', help='Export specific agent memories')
    export_parser.add_argument('--days', type=int, help='Export memories from last N days')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json',
                              help='Export format (default: json)')
    export_parser.add_argument('--output', help='Output file (default: stdout)')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import memories')
    import_parser.add_argument('file', help='Import file path')
    import_parser.add_argument('--replace', action='store_true',
                              help='Replace existing memories instead of merging')
    
    args = parser.parse_args()
    
    if args.command == 'export':
        exporter = MemoryExporter(args.project)
        exporter.export_memories(
            agent=args.agent,
            days=args.days,
            output_format=args.format,
            output_file=args.output
        )
        
    elif args.command == 'import':
        importer = MemoryImporter(args.project)
        importer.import_memories(args.file, merge=not args.replace)
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()