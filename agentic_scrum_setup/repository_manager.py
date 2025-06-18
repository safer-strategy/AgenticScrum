#!/usr/bin/env python3
"""Repository management for AgenticScrum organizations."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional

from .setup_core import SetupCore


class RepositoryManager:
    """Manages repositories within an AgenticScrum organization."""
    
    def __init__(self, organization_path: Path):
        """Initialize repository manager.
        
        Args:
            organization_path: Path to the organization directory
        """
        self.organization_path = organization_path
        self.org_config_path = organization_path / '.agentic' / 'agentic_config.yaml'
        self.projects_dir = organization_path / 'projects'
        
        if not self.org_config_path.exists():
            raise ValueError(f"Organization config not found at {self.org_config_path}")
        
        # Load organization configuration
        with open(self.org_config_path, 'r') as f:
            self.org_config = yaml.safe_load(f)
    
    def add_repository(self, repo_config: Dict[str, str]) -> Path:
        """Add new repository to the organization.
        
        Args:
            repo_config: Repository configuration dictionary
            
        Returns:
            Path to the created repository
        """
        # Validate repository name uniqueness
        self._validate_repository_name(repo_config['repo_name'])
        
        # Create inherited configuration
        inherited_config = self._create_inherited_config(repo_config)
        
        # Create repository using SetupCore
        repo_setup = SetupCore(inherited_config)
        repo_setup.create_project()
        
        repo_path = self.projects_dir / repo_config['repo_name']
        
        # Link repository to organization agents
        self._link_repository_to_organization(repo_path, repo_config)
        
        # Update organization tracking
        self._update_organization_tracking(repo_config)
        
        return repo_path
    
    def list_repositories(self) -> List[Dict[str, str]]:
        """List all repositories in the organization.
        
        Returns:
            List of repository information dictionaries
        """
        if not self.projects_dir.exists():
            return []
        
        repositories = []
        for repo_dir in self.projects_dir.iterdir():
            if repo_dir.is_dir():
                repo_config_path = repo_dir / 'agentic_config.yaml'
                if repo_config_path.exists():
                    with open(repo_config_path, 'r') as f:
                        repo_config = yaml.safe_load(f)
                    
                    repositories.append({
                        'name': repo_dir.name,
                        'language': repo_config.get('project', {}).get('language', 'unknown'),
                        'framework': repo_config.get('project', {}).get('framework', 'none'),
                        'agents': repo_config.get('agents', {}).keys() if isinstance(repo_config.get('agents'), dict) else [],
                        'status': 'configured'
                    })
                else:
                    repositories.append({
                        'name': repo_dir.name,
                        'language': 'unknown',
                        'framework': 'none',
                        'agents': [],
                        'status': 'missing_config'
                    })
        
        return sorted(repositories, key=lambda x: x['name'])
    
    def remove_repository(self, repo_name: str, confirm: bool = False) -> bool:
        """Remove repository from organization.
        
        Args:
            repo_name: Name of repository to remove
            confirm: Whether removal is confirmed
            
        Returns:
            True if removal successful, False otherwise
        """
        repo_path = self.projects_dir / repo_name
        
        if not repo_path.exists():
            raise ValueError(f"Repository '{repo_name}' not found")
        
        if not confirm:
            raise ValueError("Repository removal requires explicit confirmation")
        
        import shutil
        try:
            shutil.rmtree(repo_path)
            self._remove_from_organization_tracking(repo_name)
            return True
        except OSError as e:
            raise RuntimeError(f"Failed to remove repository: {e}")
    
    def _validate_repository_name(self, repo_name: str):
        """Validate that repository name is unique and valid."""
        if not repo_name or not repo_name.strip():
            raise ValueError("Repository name cannot be empty")
        
        # Check for conflicts with existing repositories
        if (self.projects_dir / repo_name).exists():
            raise ValueError(f"Repository '{repo_name}' already exists in organization")
        
        # Check for invalid characters (same as project name validation)
        import re
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        if re.search(invalid_chars, repo_name):
            raise ValueError(
                f"Repository name '{repo_name}' contains invalid characters. "
                "Repository names cannot contain: < > : \" / \\ | ? * or control characters. "
                "Use only letters, numbers, hyphens, and underscores."
            )
    
    def _create_inherited_config(self, repo_config: Dict[str, str]) -> Dict[str, str]:
        """Create repository config inheriting from organization defaults.
        
        Args:
            repo_config: Repository-specific configuration
            
        Returns:
            Complete configuration for repository creation
        """
        # Start with organization defaults
        inherited_config = {
            'project_name': repo_config['repo_name'],
            'project_type': 'single',  # Individual repos are single projects
            'language': repo_config['language'],
            'framework': repo_config.get('framework'),
            'agents': repo_config['agents'],
            'llm_provider': self.org_config.get('llm_provider', 'anthropic'),
            'default_model': self.org_config.get('default_model', 'claude-sonnet-4-0'),
            'output_dir': str(self.projects_dir),
            'enable_mcp': self.org_config.get('enable_mcp', False),
            'enable_search': self.org_config.get('enable_search', False),
            'organization_name': self.org_config.get('organization_name'),
            'organization_path': str(self.organization_path)
        }
        
        return inherited_config
    
    def _link_repository_to_organization(self, repo_path: Path, repo_config: Dict[str, str]):
        """Link repository to organization-level agents and memory.
        
        Args:
            repo_path: Path to the repository
            repo_config: Repository configuration
        """
        # Create organization link file  
        org_link = {
            'organization_name': self.org_config.get('organization', {}).get('name') or self.organization_path.name,
            'organization_path': str(self.organization_path),
            'organization_agents': {
                'organization_poa': str(self.organization_path / '.agentic' / 'agents' / 'organization_poa'),
                'organization_sma': str(self.organization_path / '.agentic' / 'agents' / 'organization_sma')
            },
            'shared_memory': str(self.organization_path / '.agentic' / 'shared_memory'),
            'shared_standards': str(self.organization_path / '.agentic' / 'shared_standards')
        }
        
        # Write organization link to repository
        org_link_path = repo_path / '.agentic_organization_link.yaml'
        with open(org_link_path, 'w') as f:
            yaml.dump(org_link, f, default_flow_style=False, sort_keys=False)
        
        # Update repository agents with organization awareness
        self._update_repository_agent_configs(repo_path, org_link)
    
    def _update_repository_agent_configs(self, repo_path: Path, org_link: Dict):
        """Update repository agent configurations with organization awareness.
        
        Args:
            repo_path: Path to the repository
            org_link: Organization link information
        """
        agents_dir = repo_path / 'agents'
        if not agents_dir.exists():
            return
        
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                persona_file = agent_dir / 'persona_rules.yaml'
                if persona_file.exists():
                    # Read existing persona configuration
                    with open(persona_file, 'r') as f:
                        persona_config = yaml.safe_load(f)
                    
                    # Add organization awareness
                    if 'organization' not in persona_config:
                        persona_config['organization'] = {}
                    
                    persona_config['organization'].update({
                        'name': org_link['organization_name'],
                        'path': org_link['organization_path'],
                        'coordination_agents': org_link['organization_agents'],
                        'shared_memory': org_link['shared_memory'],
                        'shared_standards': org_link['shared_standards']
                    })
                    
                    # Write updated configuration
                    with open(persona_file, 'w') as f:
                        yaml.dump(persona_config, f, default_flow_style=False, sort_keys=False)
    
    def _update_organization_tracking(self, repo_config: Dict[str, str]):
        """Update organization-level tracking of repositories.
        
        Args:
            repo_config: Repository configuration
        """
        tracking_file = self.organization_path / '.agentic' / 'repositories.yaml'
        
        # Load existing tracking or create new
        if tracking_file.exists():
            with open(tracking_file, 'r') as f:
                tracking = yaml.safe_load(f) or {}
        else:
            tracking = {}
        
        if 'repositories' not in tracking:
            tracking['repositories'] = {}
        
        # Add repository information
        tracking['repositories'][repo_config['repo_name']] = {
            'language': repo_config['language'],
            'framework': repo_config.get('framework'),
            'agents': repo_config['agents'].split(',') if isinstance(repo_config['agents'], str) else repo_config['agents'],
            'created_date': str(Path().cwd()),  # Add proper date tracking
            'status': 'active'
        }
        
        # Write updated tracking
        with open(tracking_file, 'w') as f:
            yaml.dump(tracking, f, default_flow_style=False, sort_keys=False)
    
    def _remove_from_organization_tracking(self, repo_name: str):
        """Remove repository from organization tracking.
        
        Args:
            repo_name: Name of repository to remove from tracking
        """
        tracking_file = self.organization_path / '.agentic' / 'repositories.yaml'
        
        if tracking_file.exists():
            with open(tracking_file, 'r') as f:
                tracking = yaml.safe_load(f) or {}
            
            if 'repositories' in tracking and repo_name in tracking['repositories']:
                del tracking['repositories'][repo_name]
                
                with open(tracking_file, 'w') as f:
                    yaml.dump(tracking, f, default_flow_style=False, sort_keys=False)