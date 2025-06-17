#!/usr/bin/env python3
"""
Search Cache Manager for AgenticScrum

Manages caching of Perplexity search results in agent memory to:
1. Reduce API usage and costs
2. Improve response times for repeated queries
3. Track search patterns across agents
"""

import argparse
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SearchCacheManager:
    """Manages search result caching for AgenticScrum agents."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_root = self.project_path / '.agent-memory'
        self.cache_file = self.memory_root / 'shared' / 'search_cache.jsonl'
        self.cache_ttl_days = 30  # Default cache TTL
        
    def _get_query_hash(self, query: str) -> str:
        """Generate a hash for a search query to use as cache key."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def cache_search_result(self, agent: str, query: str, results: Dict, 
                          tags: List[str] = None) -> None:
        """Cache a search result in agent memory."""
        query_hash = self._get_query_hash(query)
        
        cache_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'search_result',
            'agent': agent,
            'query': query,
            'query_hash': query_hash,
            'results': results,
            'tags': tags or [],
            'source': 'perplexity',
            'expires': (datetime.utcnow() + timedelta(days=self.cache_ttl_days)).isoformat() + 'Z'
        }
        
        # Ensure directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to JSONL file
        with open(self.cache_file, 'a') as f:
            f.write(json.dumps(cache_entry) + '\n')
            
        logger.info(f"Cached search result for query: {query[:50]}...")
        
    def get_cached_result(self, query: str) -> Optional[Dict]:
        """Retrieve a cached search result if available and not expired."""
        if not self.cache_file.exists():
            return None
            
        query_hash = self._get_query_hash(query)
        now = datetime.utcnow()
        
        # Read all cache entries (in production, consider using a database)
        with open(self.cache_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if (entry.get('query_hash') == query_hash and 
                        datetime.fromisoformat(entry['expires'].rstrip('Z')) > now):
                        logger.info(f"Found cached result for query: {query[:50]}...")
                        return entry
                except json.JSONDecodeError:
                    continue
                    
        return None
    
    def clean_expired_cache(self) -> int:
        """Remove expired cache entries."""
        if not self.cache_file.exists():
            return 0
            
        now = datetime.utcnow()
        valid_entries = []
        expired_count = 0
        
        with open(self.cache_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if datetime.fromisoformat(entry['expires'].rstrip('Z')) > now:
                        valid_entries.append(line.strip())
                    else:
                        expired_count += 1
                except json.JSONDecodeError:
                    continue
        
        # Rewrite file with only valid entries
        if expired_count > 0:
            with open(self.cache_file, 'w') as f:
                for entry in valid_entries:
                    f.write(entry + '\n')
                    
        logger.info(f"Cleaned {expired_count} expired cache entries")
        return expired_count
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the search cache."""
        if not self.cache_file.exists():
            return {
                'total_entries': 0,
                'expired_entries': 0,
                'agents': {},
                'popular_queries': []
            }
            
        stats = {
            'total_entries': 0,
            'expired_entries': 0,
            'agents': {},
            'popular_queries': {}
        }
        
        now = datetime.utcnow()
        
        with open(self.cache_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    stats['total_entries'] += 1
                    
                    if datetime.fromisoformat(entry['expires'].rstrip('Z')) < now:
                        stats['expired_entries'] += 1
                    
                    # Count by agent
                    agent = entry.get('agent', 'unknown')
                    stats['agents'][agent] = stats['agents'].get(agent, 0) + 1
                    
                    # Track query frequency
                    query = entry.get('query', '')
                    if query:
                        stats['popular_queries'][query] = stats['popular_queries'].get(query, 0) + 1
                        
                except json.JSONDecodeError:
                    continue
        
        # Get top 10 popular queries
        popular = sorted(stats['popular_queries'].items(), key=lambda x: x[1], reverse=True)[:10]
        stats['popular_queries'] = [{'query': q, 'count': c} for q, c in popular]
        
        return stats


def main():
    parser = argparse.ArgumentParser(description='Manage search result caching for AgenticScrum')
    parser.add_argument('--project', default='.', help='Project root directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Cache command
    cache_parser = subparsers.add_parser('cache', help='Cache a search result')
    cache_parser.add_argument('--agent', required=True, help='Agent name')
    cache_parser.add_argument('--query', required=True, help='Search query')
    cache_parser.add_argument('--results', required=True, help='JSON results')
    cache_parser.add_argument('--tags', nargs='+', help='Tags for the result')
    
    # Retrieve command
    get_parser = subparsers.add_parser('get', help='Get cached result')
    get_parser.add_argument('--query', required=True, help='Search query')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean expired cache entries')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show cache statistics')
    
    args = parser.parse_args()
    
    manager = SearchCacheManager(args.project)
    
    if args.command == 'cache':
        results = json.loads(args.results)
        manager.cache_search_result(args.agent, args.query, results, args.tags)
        
    elif args.command == 'get':
        result = manager.get_cached_result(args.query)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("No cached result found")
            
    elif args.command == 'clean':
        count = manager.clean_expired_cache()
        print(f"Cleaned {count} expired entries")
        
    elif args.command == 'stats':
        stats = manager.get_cache_stats()
        print(f"Cache Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Expired entries: {stats['expired_entries']}")
        print(f"\nEntries by agent:")
        for agent, count in stats['agents'].items():
            print(f"    {agent}: {count}")
        print(f"\nTop 10 popular queries:")
        for item in stats['popular_queries']:
            print(f"    {item['query'][:50]}... ({item['count']} times)")


if __name__ == '__main__':
    main()