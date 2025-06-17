#!/usr/bin/env python3
"""
Prune outdated or redundant memories to optimize storage and performance.

This script implements intelligent memory pruning strategies to keep
agent memories relevant and manageable.
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import hashlib
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pruning configuration
RELEVANCE_DECAY = 0.95  # Daily decay factor for relevance
MIN_RELEVANCE_SCORE = 0.1  # Minimum score to keep memory
DUPLICATE_SIMILARITY_THRESHOLD = 0.9  # Threshold for considering memories as duplicates


class MemoryPruner:
    """Prune agent memories based on various strategies."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_root = self.project_path / '.agent-memory'
        self.stats = {
            'total_memories': 0,
            'pruned_memories': 0,
            'retained_memories': 0,
            'space_saved': 0
        }
        
    def prune_memories(self, strategy: str = 'balanced', dry_run: bool = True,
                      max_age_days: Optional[int] = None,
                      max_memories_per_agent: Optional[int] = None) -> Dict:
        """Prune memories based on selected strategy.
        
        Args:
            strategy: Pruning strategy ('aggressive', 'balanced', 'conservative')
            dry_run: If True, only simulate pruning without actual deletion
            max_age_days: Remove memories older than this many days
            max_memories_per_agent: Keep only N most relevant memories per agent
            
        Returns:
            Dictionary with pruning statistics
        """
        logger.info(f"Starting memory pruning (strategy: {strategy}, dry_run: {dry_run})")
        
        # Process each agent's memories
        for agent_dir in self.memory_root.iterdir():
            if agent_dir.is_dir():
                self._prune_agent_memories(
                    agent_dir, strategy, dry_run, 
                    max_age_days, max_memories_per_agent
                )
                
        logger.info(f"Pruning complete. Stats: {self.stats}")
        return self.stats
        
    def _prune_agent_memories(self, agent_dir: Path, strategy: str, dry_run: bool,
                            max_age_days: Optional[int],
                            max_memories_per_agent: Optional[int]) -> None:
        """Prune memories for a specific agent."""
        agent_name = agent_dir.name
        logger.info(f"Processing agent: {agent_name}")
        
        # Load all memories for the agent
        memories = []
        memory_files = list(agent_dir.glob('*.jsonl'))
        
        for memory_file in memory_files:
            file_memories = []
            with open(memory_file, 'r') as f:
                for line_num, line in enumerate(f):
                    try:
                        memory = json.loads(line.strip())
                        memory['_file'] = str(memory_file)
                        memory['_line'] = line_num
                        file_memories.append(memory)
                    except json.JSONDecodeError:
                        logger.error(f"Error parsing line {line_num} in {memory_file}")
                        
            memories.extend(file_memories)
            
        if not memories:
            return
            
        self.stats['total_memories'] += len(memories)
        
        # Apply pruning strategies
        memories_to_keep = self._apply_pruning_strategies(
            memories, strategy, max_age_days, max_memories_per_agent
        )
        
        # Calculate what to prune
        memories_to_prune = len(memories) - len(memories_to_keep)
        self.stats['pruned_memories'] += memories_to_prune
        self.stats['retained_memories'] += len(memories_to_keep)
        
        if memories_to_prune > 0:
            logger.info(f"Pruning {memories_to_prune} memories from {agent_name}")
            
            if not dry_run:
                self._write_pruned_memories(agent_dir, memories_to_keep)
            else:
                logger.info(f"[DRY RUN] Would prune {memories_to_prune} memories")
                
    def _apply_pruning_strategies(self, memories: List[Dict], strategy: str,
                                 max_age_days: Optional[int],
                                 max_memories_per_agent: Optional[int]) -> List[Dict]:
        """Apply pruning strategies and return memories to keep."""
        # Calculate relevance scores
        scored_memories = []
        for memory in memories:
            score = self._calculate_relevance_score(memory, strategy)
            scored_memories.append((score, memory))
            
        # Sort by relevance score (highest first)
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        # Apply filters
        memories_to_keep = []
        
        for score, memory in scored_memories:
            # Skip if below minimum relevance
            if score < MIN_RELEVANCE_SCORE:
                continue
                
            # Skip if too old
            if max_age_days and self._get_memory_age_days(memory) > max_age_days:
                continue
                
            # Skip if we've reached the limit
            if max_memories_per_agent and len(memories_to_keep) >= max_memories_per_agent:
                break
                
            memories_to_keep.append(memory)
            
        # Remove duplicates
        memories_to_keep = self._remove_duplicate_memories(memories_to_keep)
        
        return memories_to_keep
        
    def _calculate_relevance_score(self, memory: Dict, strategy: str) -> float:
        """Calculate relevance score for a memory."""
        base_score = 1.0
        
        # Age factor
        age_days = self._get_memory_age_days(memory)
        age_factor = RELEVANCE_DECAY ** age_days
        
        # Type factor (some memory types are more valuable)
        type_weights = {
            'code_pattern': 1.2,
            'solution': 1.1,
            'bug_fix': 1.1,
            'security_fix': 1.3,
            'requirement_pattern': 1.0,
            'test_strategy': 1.0,
            'search_result': 0.7  # Search results decay faster
        }
        type_factor = type_weights.get(memory.get('type', ''), 0.9)
        
        # Outcome factor
        outcome_factor = 1.0
        outcome = str(memory.get('outcome', '')).lower()
        if any(word in outcome for word in ['success', 'improved', 'fixed']):
            outcome_factor = 1.2
        elif any(word in outcome for word in ['failed', 'error']):
            outcome_factor = 0.8
            
        # Reuse factor (memories with patterns that are reused are more valuable)
        reuse_factor = 1.0
        if 'pattern' in memory:
            # In a real implementation, we'd check how often this pattern is referenced
            reuse_factor = 1.1
            
        # Tag factor (memories with more tags are usually more comprehensive)
        tag_factor = 1.0 + (len(memory.get('tags', [])) * 0.05)
        
        # Strategy adjustments
        if strategy == 'aggressive':
            # Aggressive pruning: stronger decay, lower base score
            age_factor = age_factor ** 1.5
            base_score = 0.8
        elif strategy == 'conservative':
            # Conservative pruning: weaker decay, higher base score
            age_factor = age_factor ** 0.7
            base_score = 1.1
            
        # Calculate final score
        score = base_score * age_factor * type_factor * outcome_factor * reuse_factor * tag_factor
        
        return min(score, 2.0)  # Cap maximum score
        
    def _get_memory_age_days(self, memory: Dict) -> float:
        """Get age of memory in days."""
        timestamp = memory.get('timestamp')
        if not timestamp:
            return 365  # Assume very old if no timestamp
            
        try:
            memory_date = datetime.fromisoformat(timestamp.rstrip('Z'))
            age = datetime.utcnow() - memory_date
            return age.days + (age.seconds / 86400)  # Include fractional days
        except:
            return 365
            
    def _remove_duplicate_memories(self, memories: List[Dict]) -> List[Dict]:
        """Remove duplicate or very similar memories."""
        unique_memories = []
        memory_hashes = set()
        
        for memory in memories:
            # Create a hash of the memory content (excluding metadata)
            content_dict = {
                k: v for k, v in memory.items()
                if k not in ['timestamp', '_file', '_line', 'id']
            }
            content_str = json.dumps(content_dict, sort_keys=True)
            content_hash = hashlib.md5(content_str.encode()).hexdigest()
            
            if content_hash not in memory_hashes:
                memory_hashes.add(content_hash)
                unique_memories.append(memory)
            else:
                logger.debug(f"Removing duplicate memory: {memory.get('type', 'unknown')}")
                
        return unique_memories
        
    def _write_pruned_memories(self, agent_dir: Path, memories_to_keep: List[Dict]) -> None:
        """Write the pruned memories back to files."""
        # Group memories by original file
        memories_by_file = defaultdict(list)
        for memory in memories_to_keep:
            # Remove internal metadata
            clean_memory = {k: v for k, v in memory.items() 
                           if not k.startswith('_')}
            memories_by_file[memory['_file']].append(clean_memory)
            
        # Write each file
        for file_path, file_memories in memories_by_file.items():
            file_path = Path(file_path)
            
            # Backup original file
            backup_path = file_path.with_suffix('.jsonl.bak')
            file_path.rename(backup_path)
            
            # Write pruned memories
            with open(file_path, 'w') as f:
                for memory in file_memories:
                    f.write(json.dumps(memory) + '\n')
                    
            # Calculate space saved
            original_size = backup_path.stat().st_size
            new_size = file_path.stat().st_size
            self.stats['space_saved'] += (original_size - new_size)
            
            logger.info(f"Pruned {file_path.name}: {original_size} -> {new_size} bytes")
            
    def analyze_pruning_impact(self, strategy: str = 'balanced',
                              max_age_days: Optional[int] = None) -> Dict:
        """Analyze what would be pruned without actually pruning."""
        analysis = {
            'by_agent': {},
            'by_type': defaultdict(lambda: {'keep': 0, 'prune': 0}),
            'by_age': {
                'last_week': {'keep': 0, 'prune': 0},
                'last_month': {'keep': 0, 'prune': 0},
                'last_quarter': {'keep': 0, 'prune': 0},
                'older': {'keep': 0, 'prune': 0}
            },
            'total_size_bytes': 0,
            'estimated_size_after_pruning': 0
        }
        
        for agent_dir in self.memory_root.iterdir():
            if not agent_dir.is_dir():
                continue
                
            agent_name = agent_dir.name
            agent_stats = {'total': 0, 'keep': 0, 'prune': 0}
            
            # Load memories
            memories = []
            for memory_file in agent_dir.glob('*.jsonl'):
                analysis['total_size_bytes'] += memory_file.stat().st_size
                
                with open(memory_file, 'r') as f:
                    for line in f:
                        try:
                            memory = json.loads(line.strip())
                            memories.append(memory)
                        except:
                            continue
                            
            agent_stats['total'] = len(memories)
            
            # Apply pruning logic
            for memory in memories:
                score = self._calculate_relevance_score(memory, strategy)
                age_days = self._get_memory_age_days(memory)
                
                will_prune = (score < MIN_RELEVANCE_SCORE or 
                            (max_age_days and age_days > max_age_days))
                
                if will_prune:
                    agent_stats['prune'] += 1
                    action = 'prune'
                else:
                    agent_stats['keep'] += 1
                    action = 'keep'
                    analysis['estimated_size_after_pruning'] += len(json.dumps(memory))
                    
                # Update type stats
                memory_type = memory.get('type', 'unknown')
                analysis['by_type'][memory_type][action] += 1
                
                # Update age stats
                if age_days <= 7:
                    analysis['by_age']['last_week'][action] += 1
                elif age_days <= 30:
                    analysis['by_age']['last_month'][action] += 1
                elif age_days <= 90:
                    analysis['by_age']['last_quarter'][action] += 1
                else:
                    analysis['by_age']['older'][action] += 1
                    
            analysis['by_agent'][agent_name] = agent_stats
            
        return analysis


def main():
    parser = argparse.ArgumentParser(description='Prune agent memories')
    parser.add_argument('--project', default='.', help='Project root directory')
    parser.add_argument('--strategy', choices=['aggressive', 'balanced', 'conservative'],
                       default='balanced', help='Pruning strategy')
    parser.add_argument('--max-age-days', type=int, help='Remove memories older than N days')
    parser.add_argument('--max-per-agent', type=int, help='Keep only N memories per agent')
    parser.add_argument('--analyze', action='store_true', help='Analyze impact without pruning')
    parser.add_argument('--execute', action='store_true', help='Actually execute pruning (not dry run)')
    
    args = parser.parse_args()
    
    pruner = MemoryPruner(args.project)
    
    if args.analyze:
        analysis = pruner.analyze_pruning_impact(args.strategy, args.max_age_days)
        print(json.dumps(analysis, indent=2))
    else:
        stats = pruner.prune_memories(
            strategy=args.strategy,
            dry_run=not args.execute,
            max_age_days=args.max_age_days,
            max_memories_per_agent=args.max_per_agent
        )
        
        print(f"\nPruning Statistics:")
        print(f"  Total memories: {stats['total_memories']}")
        print(f"  Memories pruned: {stats['pruned_memories']}")
        print(f"  Memories retained: {stats['retained_memories']}")
        if args.execute:
            print(f"  Space saved: {stats['space_saved'] / 1024:.2f} KB")
        
        if not args.execute:
            print("\nThis was a dry run. Use --execute to actually prune memories.")


if __name__ == '__main__':
    main()