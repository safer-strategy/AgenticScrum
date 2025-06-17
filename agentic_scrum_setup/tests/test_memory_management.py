#!/usr/bin/env python3
"""
Tests for Story 305: Memory Management Utilities
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from memory_export import MemoryExporter, MemoryImporter
from memory_analyze import MemoryAnalyzer
from memory_prune import MemoryPruner


class TestMemoryManagement(unittest.TestCase):
    """Test cases for memory management utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.memory_root = self.project_path / '.agent-memory'
        
        # Create test memory structure
        self._create_test_memories()
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_test_memories(self):
        """Create test memory files."""
        # Create agent directories
        agents = ['poa', 'deva', 'qaa']
        
        for agent in agents:
            agent_dir = self.memory_root / agent
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # Create memory file
            memory_file = agent_dir / 'main.jsonl'
            
            # Add some test memories
            memories = []
            
            # Recent memory
            memories.append({
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'type': 'code_pattern',
                'pattern': 'async/await usage',
                'solution': 'Use asyncio for concurrent operations',
                'outcome': 'Improved performance by 3x',
                'tags': ['async', 'performance', 'python']
            })
            
            # Older memory
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
            memories.append({
                'timestamp': week_ago,
                'type': 'bug_fix',
                'issue': 'Memory leak in connection pool',
                'fix': 'Properly close connections',
                'outcome': 'Fixed memory leak',
                'tags': ['bug', 'memory', 'database']
            })
            
            # Very old memory
            month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'
            memories.append({
                'timestamp': month_ago,
                'type': 'requirement_pattern',
                'pattern': 'User authentication',
                'decision': 'Use JWT tokens',
                'outcome': 'Successfully implemented',
                'tags': ['auth', 'security']
            })
            
            # Write memories to file
            with open(memory_file, 'w') as f:
                for memory in memories:
                    f.write(json.dumps(memory) + '\n')
                    
    def test_memory_export_json(self):
        """Test exporting memories as JSON."""
        exporter = MemoryExporter(self.project_path)
        
        # Export to temp file
        export_file = self.project_path / 'export.json'
        exporter.export_memories(output_format='json', output_file=str(export_file))
        
        # Verify export file exists
        self.assertTrue(export_file.exists())
        
        # Load and verify content
        with open(export_file, 'r') as f:
            data = json.load(f)
            
        self.assertIn('export_date', data)
        self.assertIn('memories', data)
        self.assertIn('memory_count', data)
        self.assertEqual(data['memory_count'], 9)  # 3 agents * 3 memories each
        
    def test_memory_export_csv(self):
        """Test exporting memories as CSV."""
        exporter = MemoryExporter(self.project_path)
        
        # Export to temp file
        export_file = self.project_path / 'export.csv'
        exporter.export_memories(output_format='csv', output_file=str(export_file))
        
        # Verify export file exists
        self.assertTrue(export_file.exists())
        
        # Verify CSV content
        with open(export_file, 'r') as f:
            lines = f.readlines()
            
        # Should have header + 9 data rows
        self.assertEqual(len(lines), 10)
        
    def test_memory_export_filter_agent(self):
        """Test exporting memories for specific agent."""
        exporter = MemoryExporter(self.project_path)
        
        # Export only POA memories
        export_file = self.project_path / 'poa_export.json'
        exporter.export_memories(agent='poa', output_format='json', 
                               output_file=str(export_file))
        
        with open(export_file, 'r') as f:
            data = json.load(f)
            
        self.assertEqual(data['memory_count'], 3)
        
    def test_memory_export_filter_days(self):
        """Test exporting recent memories only."""
        exporter = MemoryExporter(self.project_path)
        
        # Export memories from last 3 days
        export_file = self.project_path / 'recent_export.json'
        exporter.export_memories(days=3, output_format='json', 
                               output_file=str(export_file))
        
        with open(export_file, 'r') as f:
            data = json.load(f)
            
        # Should only include recent memories (1 per agent)
        self.assertEqual(data['memory_count'], 3)
        
    def test_memory_import(self):
        """Test importing memories from backup."""
        # First export
        exporter = MemoryExporter(self.project_path)
        export_file = self.project_path / 'backup.json'
        exporter.export_memories(output_format='json', output_file=str(export_file))
        
        # Create new agent directory for import test
        new_agent_dir = self.memory_root / 'saa'
        new_agent_dir.mkdir(exist_ok=True)
        
        # Import memories
        importer = MemoryImporter(self.project_path)
        importer.import_memories(str(export_file), merge=True)
        
        # Verify memories were imported
        poa_memories = list((self.memory_root / 'poa' / 'main.jsonl').open('r'))
        # Should have original 3 + imported 3 = 6 memories (due to merge)
        self.assertEqual(len(poa_memories), 6)
        
    def test_memory_analyze_patterns(self):
        """Test memory pattern analysis."""
        analyzer = MemoryAnalyzer(self.project_path)
        analysis = analyzer.analyze_patterns()
        
        # Verify analysis structure
        self.assertIn('total_memories', analysis)
        self.assertIn('memory_types', analysis)
        self.assertIn('tag_frequency', analysis)
        self.assertIn('temporal_patterns', analysis)
        self.assertIn('agent_activity', analysis)
        self.assertIn('recommendations', analysis)
        
        # Verify memory count
        self.assertEqual(analysis['total_memories'], 9)
        
        # Verify memory types
        self.assertIn('code_pattern', analysis['memory_types']['distribution'])
        self.assertIn('bug_fix', analysis['memory_types']['distribution'])
        
    def test_memory_analyze_agent_specific(self):
        """Test analyzing specific agent memories."""
        analyzer = MemoryAnalyzer(self.project_path)
        analysis = analyzer.analyze_patterns(agent='poa')
        
        self.assertEqual(analysis['total_memories'], 3)
        
    def test_memory_analyze_temporal(self):
        """Test temporal pattern analysis."""
        analyzer = MemoryAnalyzer(self.project_path)
        analysis = analyzer.analyze_patterns()
        
        temporal = analysis['temporal_patterns']
        self.assertIn('hourly_distribution', temporal)
        self.assertIn('daily_distribution', temporal)
        
    def test_memory_prune_dry_run(self):
        """Test memory pruning in dry run mode."""
        pruner = MemoryPruner(self.project_path)
        stats = pruner.prune_memories(strategy='balanced', dry_run=True)
        
        # Verify stats
        self.assertIn('total_memories', stats)
        self.assertIn('pruned_memories', stats)
        self.assertIn('retained_memories', stats)
        
        # In dry run, files should not be modified
        poa_memories = list((self.memory_root / 'poa' / 'main.jsonl').open('r'))
        self.assertEqual(len(poa_memories), 3)  # Original count
        
    def test_memory_prune_age_based(self):
        """Test pruning memories by age."""
        pruner = MemoryPruner(self.project_path)
        stats = pruner.prune_memories(
            strategy='balanced', 
            dry_run=True,
            max_age_days=14  # Keep only last 2 weeks
        )
        
        # Should prune the month-old memories (1 per agent = 3 total)
        self.assertGreaterEqual(stats['pruned_memories'], 3)
        
    def test_memory_prune_relevance_calculation(self):
        """Test relevance score calculation."""
        pruner = MemoryPruner(self.project_path)
        
        # Recent successful memory should have high score
        recent_memory = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'code_pattern',
            'outcome': 'Successfully improved performance',
            'tags': ['performance', 'optimization']
        }
        score = pruner._calculate_relevance_score(recent_memory, 'balanced')
        self.assertGreater(score, 1.0)
        
        # Old failed memory should have low score
        old_memory = {
            'timestamp': (datetime.utcnow() - timedelta(days=365)).isoformat() + 'Z',
            'type': 'attempt',
            'outcome': 'Failed to compile',
            'tags': []
        }
        score = pruner._calculate_relevance_score(old_memory, 'balanced')
        self.assertLess(score, 0.5)
        
    def test_memory_prune_strategy_differences(self):
        """Test different pruning strategies."""
        pruner = MemoryPruner(self.project_path)
        
        # Test memory
        memory = {
            'timestamp': (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z',
            'type': 'code_pattern',
            'outcome': 'Working solution',
            'tags': ['test']
        }
        
        # Aggressive should give lower score
        aggressive_score = pruner._calculate_relevance_score(memory, 'aggressive')
        
        # Conservative should give higher score
        conservative_score = pruner._calculate_relevance_score(memory, 'conservative')
        
        self.assertLess(aggressive_score, conservative_score)
        
    def test_memory_prune_analyze_impact(self):
        """Test analyzing pruning impact."""
        pruner = MemoryPruner(self.project_path)
        analysis = pruner.analyze_pruning_impact(strategy='balanced')
        
        # Verify analysis structure
        self.assertIn('by_agent', analysis)
        self.assertIn('by_type', analysis)
        self.assertIn('by_age', analysis)
        self.assertIn('total_size_bytes', analysis)
        
        # Verify agent stats
        for agent in ['poa', 'deva', 'qaa']:
            self.assertIn(agent, analysis['by_agent'])
            agent_stats = analysis['by_agent'][agent]
            self.assertEqual(agent_stats['total'], 3)
            
    def test_scripts_are_executable(self):
        """Test that all scripts have proper shebang."""
        scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
        scripts = [
            'memory_export.py',
            'memory_analyze.py', 
            'memory_prune.py'
        ]
        
        for script_name in scripts:
            script_path = scripts_dir / script_name
            self.assertTrue(script_path.exists(), f"{script_name} should exist")
            
            with open(script_path, 'r') as f:
                first_line = f.readline()
                self.assertTrue(first_line.startswith('#!/usr/bin/env python3'),
                              f"{script_name} should have proper shebang")


if __name__ == '__main__':
    unittest.main()