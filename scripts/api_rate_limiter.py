#!/usr/bin/env python3
"""
API Rate Limiter for AgenticScrum

Manages rate limiting for external API calls (like Perplexity) to:
1. Prevent exceeding API rate limits
2. Track usage per agent
3. Implement backoff strategies
"""

import argparse
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class APIRateLimiter:
    """Manages API rate limiting for AgenticScrum agents."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_root = self.project_path / '.agent-memory'
        self.rate_limit_file = self.memory_root / 'shared' / 'api_usage.jsonl'
        
        # Default rate limits (can be overridden per API)
        self.default_limits = {
            'perplexity': {
                'requests_per_minute': 20,
                'requests_per_hour': 1000,
                'requests_per_day': 20000
            }
        }
        
    def _get_current_usage(self, api: str, agent: str) -> Dict[str, int]:
        """Get current API usage for an agent within time windows."""
        if not self.rate_limit_file.exists():
            return {'minute': 0, 'hour': 0, 'day': 0}
            
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        usage = {'minute': 0, 'hour': 0, 'day': 0}
        
        with open(self.rate_limit_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry['api'] == api and entry['agent'] == agent:
                        timestamp = datetime.fromisoformat(entry['timestamp'].rstrip('Z'))
                        
                        if timestamp > one_minute_ago:
                            usage['minute'] += 1
                        if timestamp > one_hour_ago:
                            usage['hour'] += 1
                        if timestamp > one_day_ago:
                            usage['day'] += 1
                            
                except json.JSONDecodeError:
                    continue
                    
        return usage
    
    def can_make_request(self, api: str, agent: str) -> tuple[bool, Optional[str]]:
        """Check if an agent can make an API request."""
        limits = self.default_limits.get(api, {})
        if not limits:
            return True, None
            
        usage = self._get_current_usage(api, agent)
        
        # Check each limit
        if usage['minute'] >= limits.get('requests_per_minute', float('inf')):
            return False, f"Rate limit exceeded: {usage['minute']}/{limits['requests_per_minute']} requests per minute"
            
        if usage['hour'] >= limits.get('requests_per_hour', float('inf')):
            return False, f"Rate limit exceeded: {usage['hour']}/{limits['requests_per_hour']} requests per hour"
            
        if usage['day'] >= limits.get('requests_per_day', float('inf')):
            return False, f"Rate limit exceeded: {usage['day']}/{limits['requests_per_day']} requests per day"
            
        return True, None
    
    def record_request(self, api: str, agent: str, success: bool = True,
                      response_time: float = None) -> None:
        """Record an API request."""
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'api': api,
            'agent': agent,
            'success': success,
            'response_time': response_time
        }
        
        # Ensure directory exists
        self.rate_limit_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to JSONL file
        with open(self.rate_limit_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
            
        logger.info(f"Recorded {api} request for {agent} (success: {success})")
    
    def get_usage_stats(self, api: str = None, agent: str = None) -> Dict:
        """Get usage statistics."""
        if not self.rate_limit_file.exists():
            return {}
            
        stats = defaultdict(lambda: defaultdict(lambda: {
            'total': 0,
            'success': 0,
            'failed': 0,
            'avg_response_time': 0,
            'response_times': []
        }))
        
        with open(self.rate_limit_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    api_name = entry['api']
                    agent_name = entry['agent']
                    
                    # Filter if specific api/agent requested
                    if api and api_name != api:
                        continue
                    if agent and agent_name != agent:
                        continue
                        
                    stats[api_name][agent_name]['total'] += 1
                    
                    if entry['success']:
                        stats[api_name][agent_name]['success'] += 1
                    else:
                        stats[api_name][agent_name]['failed'] += 1
                        
                    if entry.get('response_time'):
                        stats[api_name][agent_name]['response_times'].append(entry['response_time'])
                        
                except json.JSONDecodeError:
                    continue
        
        # Calculate average response times
        for api_stats in stats.values():
            for agent_stats in api_stats.values():
                if agent_stats['response_times']:
                    agent_stats['avg_response_time'] = sum(agent_stats['response_times']) / len(agent_stats['response_times'])
                del agent_stats['response_times']  # Remove raw data from output
                
        return dict(stats)
    
    def get_wait_time(self, api: str, agent: str) -> Optional[int]:
        """Get the time to wait before the next request is allowed."""
        limits = self.default_limits.get(api, {})
        if not limits:
            return None
            
        usage = self._get_current_usage(api, agent)
        
        # Check minute limit
        if usage['minute'] >= limits.get('requests_per_minute', float('inf')):
            return 60  # Wait up to 60 seconds
            
        # Check hour limit
        if usage['hour'] >= limits.get('requests_per_hour', float('inf')):
            return 3600  # Wait up to an hour
            
        # Check day limit  
        if usage['day'] >= limits.get('requests_per_day', float('inf')):
            return 86400  # Wait up to a day
            
        return None


def main():
    parser = argparse.ArgumentParser(description='Manage API rate limiting for AgenticScrum')
    parser.add_argument('--project', default='.', help='Project root directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check if request is allowed')
    check_parser.add_argument('--api', required=True, help='API name (e.g., perplexity)')
    check_parser.add_argument('--agent', required=True, help='Agent name')
    
    # Record command
    record_parser = subparsers.add_parser('record', help='Record an API request')
    record_parser.add_argument('--api', required=True, help='API name')
    record_parser.add_argument('--agent', required=True, help='Agent name')
    record_parser.add_argument('--success', action='store_true', help='Request was successful')
    record_parser.add_argument('--response-time', type=float, help='Response time in seconds')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show usage statistics')
    stats_parser.add_argument('--api', help='Filter by API')
    stats_parser.add_argument('--agent', help='Filter by agent')
    
    # Wait command
    wait_parser = subparsers.add_parser('wait', help='Get wait time until next request')
    wait_parser.add_argument('--api', required=True, help='API name')
    wait_parser.add_argument('--agent', required=True, help='Agent name')
    
    args = parser.parse_args()
    
    limiter = APIRateLimiter(args.project)
    
    if args.command == 'check':
        allowed, reason = limiter.can_make_request(args.api, args.agent)
        if allowed:
            print("Request allowed")
        else:
            print(f"Request denied: {reason}")
            
    elif args.command == 'record':
        limiter.record_request(args.api, args.agent, args.success, args.response_time)
        
    elif args.command == 'stats':
        stats = limiter.get_usage_stats(args.api, args.agent)
        print(json.dumps(stats, indent=2))
        
    elif args.command == 'wait':
        wait_time = limiter.get_wait_time(args.api, args.agent)
        if wait_time:
            print(f"Wait {wait_time} seconds before next request")
        else:
            print("No wait required")


if __name__ == '__main__':
    main()