#!/usr/bin/env python3
"""Organization setup functionality for AgenticScrum projects."""

import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .setup_core import SetupCore


class OrganizationSetup(SetupCore):
    """Extended setup class for creating AgenticScrum organizations."""
    
    def __init__(self, config: Dict[str, str]):
        """Initialize organization setup with configuration.
        
        Args:
            config: Dictionary containing organization configuration
        """
        # Set organization-specific defaults for parent class
        org_config = config.copy()
        org_config.setdefault('language', 'organization')  # Special marker
        org_config.setdefault('agents', 'organization_poa,organization_sma')
        
        # Ensure agents is always a string for parent class compatibility
        if not org_config.get('agents'):
            org_config['agents'] = 'organization_poa,organization_sma'
        
        super().__init__(org_config)
        
        self.organization_name = config['organization_name']
        self.organization_path = self.output_dir / self.organization_name
        
        # Override project_path for organization structure
        self.project_path = self.organization_path
    
    def create_organization(self):
        """Create the complete organization structure."""
        try:
            # Validate output directory first
            self.validate_output_directory()
            
            # Show where organization will be created
            print(f"\n📍 Creating organization at: {self.organization_path.absolute()}")
            
            # Create main organization directory
            try:
                self.organization_path.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                raise RuntimeError(
                    f"Failed to create organization directory '{self.organization_path}': {e}. "
                    "Please check permissions and ensure the path is valid."
                )
            
            # Create organization structure
            try:
                self._create_organization_structure()
            except (OSError, PermissionError) as e:
                raise RuntimeError(
                    f"Failed to create organization directory structure: {e}. "
                    "Please check disk space and permissions."
                )
            
            # Generate organization configuration files
            try:
                self._generate_organization_configs()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to generate organization configuration files: {e}. "
                    "Please check your organization configuration and try again."
                )
            
            # Generate organization agents
            try:
                self._generate_organization_agents()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to generate organization agents: {e}. "
                    "Please verify your agent configuration."
                )
            
            # Create shared resources
            try:
                self._create_shared_resources()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to create shared resources: {e}. "
                    "Please check template availability and disk space."
                )
            
            # Generate organization documentation
            try:
                self._generate_organization_documentation()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to generate organization documentation: {e}. "
                    "Please check template availability and disk space."
                )
            
            # Create MCP integration if enabled
            if self.enable_mcp:
                try:
                    self._create_organization_memory_structure()
                except OSError as e:
                    raise RuntimeError(
                        f"Failed to create organization MCP memory structure: {e}. "
                        "Please check disk space and permissions."
                    )
                    
        except Exception as e:
            # Clean up partially created organization on failure
            if self.organization_path.exists():
                try:
                    shutil.rmtree(self.organization_path)
                    print(f"\n🧹 Cleaned up partially created organization directory.")
                except OSError:
                    print(f"\n⚠️  Warning: Could not clean up {self.organization_path}. You may need to remove it manually.")
            raise
    
    def _create_organization_structure(self):
        """Create the standard AgenticScrum organization directory structure."""
        directories = [
            '.agentic',
            '.agentic/agents',
            '.agentic/shared_standards',
            '.agentic/shared_tooling',
            'projects',
            'shared',
            'shared/scripts',
            'docs',
            'docs/organization',
            'docs/standards'
        ]
        
        for directory in directories:
            (self.organization_path / directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_organization_configs(self):
        """Generate organization-level configuration files."""
        from datetime import datetime
        created_date = datetime.now().strftime('%Y-%m-%d')
        
        # Generate organization agentic_config.yaml
        org_config_template = self.jinja_env.get_template('organization/agentic_config.yaml.j2')
        org_config = org_config_template.render(
            organization_name=self.organization_name,
            llm_provider=self.llm_provider,
            default_model=self.default_model,
            created_date=created_date,
            enable_mcp=self.enable_mcp,
            enable_search=self.enable_search
        )
        (self.organization_path / '.agentic' / 'agentic_config.yaml').write_text(org_config)
        
        # Generate organization .gitignore
        gitignore_template = self.jinja_env.get_template('organization/.gitignore.j2')
        gitignore = gitignore_template.render()
        (self.organization_path / '.gitignore').write_text(gitignore)
        
        # Generate organization README
        readme_template = self.jinja_env.get_template('organization/README.md.j2')
        readme = readme_template.render(
            organization_name=self.organization_name,
            created_date=created_date
        )
        (self.organization_path / 'README.md').write_text(readme)
    
    def _generate_organization_agents(self):
        """Generate organization-level agent configurations."""
        # Organization POA (Portfolio Product Owner)
        org_poa_dir = self.organization_path / '.agentic' / 'agents' / 'organization_poa'
        org_poa_dir.mkdir(parents=True, exist_ok=True)
        
        org_poa_template = self.jinja_env.get_template('organization/agents/organization_poa/persona_rules.yaml.j2')
        org_poa_config = org_poa_template.render(
            organization_name=self.organization_name,
            llm_provider=self.llm_provider,
            default_model=self.default_model
        )
        (org_poa_dir / 'persona_rules.yaml').write_text(org_poa_config)
        
        # Organization SMA (Cross-project Scrum Master)
        org_sma_dir = self.organization_path / '.agentic' / 'agents' / 'organization_sma'
        org_sma_dir.mkdir(parents=True, exist_ok=True)
        
        org_sma_template = self.jinja_env.get_template('organization/agents/organization_sma/persona_rules.yaml.j2')
        org_sma_config = org_sma_template.render(
            organization_name=self.organization_name,
            llm_provider=self.llm_provider,
            default_model=self.default_model
        )
        (org_sma_dir / 'persona_rules.yaml').write_text(org_sma_config)
        
        # Generate organization MCP configuration for Claude integration
        if self.llm_provider == 'anthropic' or self.enable_mcp:
            org_mcp_template = self.jinja_env.get_template('organization/.mcp.json.j2')
            org_mcp_config = org_mcp_template.render(
                organization_name=self.organization_name,
                enable_search=self.enable_search
            )
            (self.organization_path / '.mcp.json').write_text(org_mcp_config)
    
    def _create_shared_resources(self):
        """Create shared resources for the organization."""
        # Generate shared docker-compose.yml
        docker_template = self.jinja_env.get_template('organization/shared/docker-compose.yml.j2')
        docker_compose = docker_template.render(
            organization_name=self.organization_name
        )
        (self.organization_path / 'shared' / 'docker-compose.yml').write_text(docker_compose)
        
        # Generate shared environment template
        env_template = self.jinja_env.get_template('organization/shared/.env.sample.j2')
        env_sample = env_template.render(
            organization_name=self.organization_name
        )
        (self.organization_path / 'shared' / '.env.sample').write_text(env_sample)
        
        # Generate shared scripts
        sync_script_template = self.jinja_env.get_template('organization/shared/scripts/sync_standards.sh.j2')
        sync_script = sync_script_template.render(
            organization_name=self.organization_name
        )
        sync_script_path = self.organization_path / 'shared' / 'scripts' / 'sync_standards.sh'
        sync_script_path.write_text(sync_script)
        
        # Make script executable
        import stat
        current_permissions = sync_script_path.stat().st_mode
        sync_script_path.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    def _generate_organization_documentation(self):
        """Generate organization documentation."""
        # Organization overview
        overview_template = self.jinja_env.get_template('organization/docs/ORGANIZATION_OVERVIEW.md.j2')
        overview = overview_template.render(
            organization_name=self.organization_name
        )
        (self.organization_path / 'docs' / 'ORGANIZATION_OVERVIEW.md').write_text(overview)
        
        # Cross-project standards
        standards_template = self.jinja_env.get_template('organization/docs/CROSS_PROJECT_STANDARDS.md.j2')
        standards = standards_template.render(
            organization_name=self.organization_name
        )
        (self.organization_path / 'docs' / 'CROSS_PROJECT_STANDARDS.md').write_text(standards)
        
        # Repository guidelines
        guidelines_template = self.jinja_env.get_template('organization/docs/REPOSITORY_GUIDELINES.md.j2')
        guidelines = guidelines_template.render(
            organization_name=self.organization_name
        )
        (self.organization_path / 'docs' / 'REPOSITORY_GUIDELINES.md').write_text(guidelines)
    
    def _create_organization_memory_structure(self):
        """Create organization-level memory structure for MCP integration."""
        if self.enable_mcp:
            memory_root = self.organization_path / '.agentic' / 'shared_memory'
            memory_root.mkdir(exist_ok=True)
            
            # Create organization-level memory files
            (memory_root / 'cross_project_decisions.jsonl').touch()
            (memory_root / 'shared_patterns.jsonl').touch()
            (memory_root / 'portfolio_feedback.jsonl').touch()
            (memory_root / 'organization_knowledge.jsonl').touch()
            
            # Create search cache if search is enabled
            if self.enable_search:
                (memory_root / 'search_cache.jsonl').touch()