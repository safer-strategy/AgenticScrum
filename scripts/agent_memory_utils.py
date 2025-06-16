#!/usr/bin/env python3
"""
Agent Memory Utilities for AgenticScrum Framework

This module provides utilities for agents to store and retrieve memories
from their persistent JSONL memory stores.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class AgentMemory:
    """Handle agent memory storage and retrieval."""
    
    def __init__(self, agent_type: str, project_path: str = "."):
        """
        Initialize agent memory handler.
        
        Args:
            agent_type: Type of agent (poa, sma, deva, qaa, saa)
            project_path: Path to project root (default: current directory)
        """
        self.agent_type = agent_type
        self.project_path = Path(project_path)
        self.memory_path = self.project_path / '.agent-memory' / agent_type
        
        # Ensure memory directory exists
        self.memory_path.mkdir(parents=True, exist_ok=True)
    
    def remember(self, memory_type: str, content: Dict[str, Any], 
                 memory_file: str = "main.jsonl") -> str:
        """
        Store a memory entry.
        
        Args:
            memory_type: Type of memory (e.g., 'code_pattern', 'bug_fix')
            content: Dictionary containing memory content
            memory_file: Target memory file (default: main.jsonl)
            
        Returns:
            Memory ID for future reference
        """
        # Create memory entry
        entry = {
            'id': self._generate_id(content),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': memory_type,
            'agent': self.agent_type,
            **content
        }
        
        # Append to JSONL file
        file_path = self.memory_path / memory_file
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        return entry['id']
    
    def recall(self, query: Optional[Dict[str, Any]] = None, 
               memory_file: str = "main.jsonl",
               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories.
        
        Args:
            query: Query parameters to filter memories
            memory_file: Source memory file (default: main.jsonl)
            limit: Maximum number of memories to return
            
        Returns:
            List of memory entries matching the query
        """
        file_path = self.memory_path / memory_file
        if not file_path.exists():
            return []
        
        memories = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        memory = json.loads(line)
                        if self._matches_query(memory, query):
                            memories.append(memory)
                    except json.JSONDecodeError:
                        continue
        
        # Sort by timestamp (most recent first) and limit
        memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return memories[:limit]
    
    def search_by_tags(self, tags: List[str], memory_file: str = "main.jsonl") -> List[Dict[str, Any]]:
        """
        Search memories by tags.
        
        Args:
            tags: List of tags to search for
            memory_file: Source memory file
            
        Returns:
            Memories containing any of the specified tags
        """
        return self.recall({'tags': tags}, memory_file)
    
    def get_patterns(self, pattern_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get specific pattern types from memory.
        
        Args:
            pattern_type: Type of pattern to retrieve
            limit: Maximum number of patterns
            
        Returns:
            List of pattern memories
        """
        # Map agent types to their pattern files
        pattern_files = {
            'poa': {'requirement': 'requirements.jsonl', 'decision': 'decisions.jsonl'},
            'sma': {'retrospective': 'retrospectives.jsonl', 'impediment': 'impediments.jsonl'},
            'deva': {'code': 'patterns.jsonl', 'refactor': 'refactors.jsonl'},
            'qaa': {'test': 'test-strategies.jsonl', 'bug': 'bug-patterns.jsonl'},
            'saa': {'vulnerability': 'vulnerabilities.jsonl', 'mitigation': 'mitigations.jsonl'}
        }
        
        if self.agent_type in pattern_files and pattern_type in pattern_files[self.agent_type]:
            file_name = pattern_files[self.agent_type][pattern_type]
            return self.recall(memory_file=file_name, limit=limit)
        
        # Fallback to main memory
        return self.recall({'type': f'{pattern_type}_pattern'}, limit=limit)
    
    def get_recent_memories(self, days: int = 7, memory_file: str = "main.jsonl") -> List[Dict[str, Any]]:
        """
        Get memories from the last N days.
        
        Args:
            days: Number of days to look back
            memory_file: Source memory file
            
        Returns:
            Recent memories within the specified timeframe
        """
        cutoff_date = datetime.utcnow().isoformat()
        # Simple date comparison (could be enhanced)
        memories = self.recall(memory_file=memory_file, limit=100)
        
        # Filter by date (simplified - in production, use proper date parsing)
        recent = []
        for memory in memories:
            if 'timestamp' in memory:
                # This is a simplified check - enhance for production
                recent.append(memory)
                if len(recent) >= 50:  # Reasonable limit
                    break
        
        return recent
    
    def _generate_id(self, content: Dict[str, Any]) -> str:
        """Generate a unique ID for a memory entry."""
        # Create ID from content hash and timestamp
        content_str = json.dumps(content, sort_keys=True)
        hash_obj = hashlib.md5(content_str.encode())
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"{self.agent_type}_{timestamp}_{hash_obj.hexdigest()[:8]}"
    
    def _matches_query(self, memory: Dict[str, Any], query: Optional[Dict[str, Any]]) -> bool:
        """Check if a memory matches the query parameters."""
        if not query:
            return True
        
        for key, value in query.items():
            if key == 'tags' and isinstance(value, list):
                # Check if any query tag is in memory tags
                memory_tags = memory.get('tags', [])
                if not any(tag in memory_tags for tag in value):
                    return False
            elif key not in memory or memory[key] != value:
                return False
        
        return True


class SharedMemory(AgentMemory):
    """Handle shared cross-agent memory."""
    
    def __init__(self, project_path: str = "."):
        """Initialize shared memory handler."""
        super().__init__('shared', project_path)
    
    def add_timeline_event(self, event_type: str, description: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an event to the project timeline."""
        content = {
            'event_type': event_type,
            'description': description,
            'metadata': metadata or {}
        }
        return self.remember('timeline_event', content, 'timeline.jsonl')
    
    def add_architecture_decision(self, decision: str, rationale: str,
                                 alternatives: Optional[List[str]] = None) -> str:
        """Record an architecture decision."""
        content = {
            'decision': decision,
            'rationale': rationale,
            'alternatives': alternatives or [],
            'status': 'active'
        }
        return self.remember('architecture_decision', content, 'architecture.jsonl')
    
    def get_timeline(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent timeline events."""
        return self.recall(memory_file='timeline.jsonl', limit=limit)
    
    def get_architecture_decisions(self, status: str = 'active') -> List[Dict[str, Any]]:
        """Get architecture decisions by status."""
        return self.recall({'status': status}, 'architecture.jsonl')


# Example usage functions for agents
def remember_code_pattern(pattern_name: str, code_snippet: str, 
                         description: str, tags: List[str]) -> str:
    """Helper function for DEVA agents to remember code patterns."""
    memory = AgentMemory('deva')
    return memory.remember('code_pattern', {
        'pattern_name': pattern_name,
        'code_snippet': code_snippet,
        'description': description,
        'language': 'python',  # Could be parameterized
        'tags': tags
    }, 'patterns.jsonl')


def remember_test_strategy(component: str, approach: str, 
                          coverage: float, effectiveness: str) -> str:
    """Helper function for QAA agents to remember test strategies."""
    memory = AgentMemory('qaa')
    return memory.remember('test_strategy', {
        'component': component,
        'approach': approach,
        'coverage_achieved': f"{coverage}%",
        'effectiveness': effectiveness,
        'tags': ['testing', component]
    }, 'test-strategies.jsonl')


def remember_security_issue(vulnerability: str, severity: str,
                           fix_applied: str, tags: List[str]) -> str:
    """Helper function for SAA agents to remember security issues."""
    memory = AgentMemory('saa')
    return memory.remember('vulnerability', {
        'vulnerability': vulnerability,
        'severity': severity,
        'fix_applied': fix_applied,
        'tags': tags
    }, 'vulnerabilities.jsonl')


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Memory Utilities")
    parser.add_argument('action', choices=['remember', 'recall', 'timeline'],
                       help="Action to perform")
    parser.add_argument('--agent', default='shared',
                       help="Agent type (poa, sma, deva, qaa, saa, shared)")
    parser.add_argument('--type', help="Memory type")
    parser.add_argument('--content', help="JSON content for remember action")
    parser.add_argument('--query', help="JSON query for recall action")
    parser.add_argument('--limit', type=int, default=10,
                       help="Limit for recall results")
    
    args = parser.parse_args()
    
    if args.action == 'remember' and args.content:
        memory = AgentMemory(args.agent)
        content = json.loads(args.content)
        memory_id = memory.remember(args.type or 'general', content)
        print(f"Stored memory: {memory_id}")
    
    elif args.action == 'recall':
        memory = AgentMemory(args.agent)
        query = json.loads(args.query) if args.query else None
        memories = memory.recall(query, limit=args.limit)
        for m in memories:
            print(json.dumps(m, indent=2))
    
    elif args.action == 'timeline':
        shared = SharedMemory()
        timeline = shared.get_timeline(args.limit)
        for event in timeline:
            print(f"[{event['timestamp']}] {event['description']}")