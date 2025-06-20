"""MCP Configuration Merger - Safely merge MCP configs preserving customizations."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class MCPConfigMerger:
    """Safely merge MCP configurations preserving project customizations."""
    
    # Fields that should always be preserved from existing config
    PRESERVE_FIELDS = {
        'mcpServers': {
            '*': ['env', 'args'],  # Preserve custom env vars and args for all servers
        },
        'globalEnv': '*',  # Always preserve global environment variables
    }
    
    # Fields that can be safely updated from template
    SAFE_UPDATE_FIELDS = {
        'mcpServers': {
            '*': ['command'],  # Update command paths if framework structure changes
        }
    }
    
    @staticmethod
    def backup_config(config_path: Path) -> Path:
        """Create timestamped backup of existing config.
        
        Args:
            config_path: Path to config file to backup
            
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = config_path.parent / '.mcp_backups'
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / f"{config_path.stem}.backup.{timestamp}{config_path.suffix}"
        shutil.copy2(config_path, backup_path)
        return backup_path
    
    @classmethod
    def merge_mcp_configs(cls, template_config: Dict[str, Any], 
                         existing_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge template with existing config, preserving customizations.
        
        Args:
            template_config: New template configuration
            existing_config: Current project configuration
            
        Returns:
            Merged configuration preserving customizations
        """
        merged = existing_config.copy()
        
        # Handle mcpServers
        existing_servers = existing_config.get('mcpServers', {})
        template_servers = template_config.get('mcpServers', {})
        
        # Initialize if not present
        if 'mcpServers' not in merged:
            merged['mcpServers'] = {}
        
        # Process each server from template
        for server_name, server_config in template_servers.items():
            if server_name not in existing_servers:
                # New server - add it entirely
                merged['mcpServers'][server_name] = server_config
                print(f"  + Adding new MCP server: {server_name}")
            else:
                # Existing server - merge carefully
                existing_server = existing_servers[server_name]
                merged_server = server_config.copy()
                
                # Preserve custom environment variables
                if 'env' in existing_server:
                    merged_server['env'] = existing_server['env']
                    if server_config.get('env'):
                        # Merge env vars, preferring existing values
                        for key, value in server_config['env'].items():
                            if key not in existing_server['env']:
                                merged_server['env'][key] = value
                
                # Preserve custom arguments
                if 'args' in existing_server:
                    # Special handling for args to preserve customizations
                    existing_args = existing_server['args']
                    template_args = server_config.get('args', [])
                    
                    # If args structure is similar, preserve custom values
                    if len(existing_args) == len(template_args):
                        merged_server['args'] = existing_args
                    else:
                        # Structure changed, use template but warn
                        merged_server['args'] = template_args
                        print(f"  ⚠️  {server_name} args structure changed, using template")
                
                # Update command path if needed (framework might have moved)
                if 'command' in server_config:
                    if existing_server.get('command') != server_config['command']:
                        merged_server['command'] = server_config['command']
                        print(f"  ↻ Updated {server_name} command path")
                
                # Preserve any custom fields not in template
                for key, value in existing_server.items():
                    if key not in merged_server:
                        merged_server[key] = value
                
                merged['mcpServers'][server_name] = merged_server
        
        # Preserve servers that exist in project but not in template
        for server_name, server_config in existing_servers.items():
            if server_name not in template_servers:
                merged['mcpServers'][server_name] = server_config
                print(f"  ✓ Preserving custom server: {server_name}")
        
        # Preserve globalEnv entirely
        if 'globalEnv' in existing_config:
            merged['globalEnv'] = existing_config['globalEnv']
        elif 'globalEnv' in template_config:
            merged['globalEnv'] = template_config['globalEnv']
        
        # Preserve other top-level custom fields
        for key, value in existing_config.items():
            if key not in merged:
                merged[key] = value
        
        return merged
    
    @staticmethod
    def add_datetime_server(config: Dict[str, Any]) -> bool:
        """Add datetime MCP server to configuration if not present.
        
        Args:
            config: MCP configuration dictionary
            
        Returns:
            True if datetime server was added, False if already present
        """
        if 'mcpServers' not in config:
            config['mcpServers'] = {}
        
        if 'datetime' not in config['mcpServers']:
            config['mcpServers']['datetime'] = {
                "command": "python",
                "args": ["mcp_servers/datetime/simple_server.py"],
                "env": {}
            }
            return True
        
        return False
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """Validate MCP configuration structure.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic structure validation
        if not isinstance(config, dict):
            return False
        
        # If mcpServers exists, validate structure
        if 'mcpServers' in config:
            if not isinstance(config['mcpServers'], dict):
                return False
            
            for server_name, server_config in config['mcpServers'].items():
                if not isinstance(server_config, dict):
                    return False
                
                # Each server should have at least a command
                if 'command' not in server_config:
                    return False
        
        return True
    
    @classmethod
    def merge_configs_safely(cls, template_path: Path, target_path: Path, 
                           project_name: str, context: Dict[str, Any] = None) -> Optional[Path]:
        """Safely merge template config with existing config.
        
        Args:
            template_path: Path to template config
            target_path: Path to existing config
            project_name: Project name for template rendering
            context: Full template context (optional, uses project_name if not provided)
            
        Returns:
            Path to backup if merge was performed, None if no changes
        """
        try:
            # Read existing config
            existing_config = json.loads(target_path.read_text())
            
            # Read and render template
            template_content = template_path.read_text()
            
            if context:
                # Use full context with Jinja2
                from jinja2 import Template
                template = Template(template_content)
                rendered_template = template.render(**context)
            else:
                # Fallback to simple replacement
                rendered_template = template_content.replace("{{ project_name }}", project_name)
                
            template_config = json.loads(rendered_template)
            
            # Validate both configs
            if not cls.validate_config(existing_config):
                print(f"  ⚠️  Invalid existing config structure, skipping merge")
                return None
            
            if not cls.validate_config(template_config):
                print(f"  ⚠️  Invalid template config structure, skipping merge")
                return None
            
            # Merge configurations
            merged_config = cls.merge_mcp_configs(template_config, existing_config)
            
            # Check if anything changed
            if merged_config == existing_config:
                return None
            
            # Backup and update
            backup_path = cls.backup_config(target_path)
            target_path.write_text(json.dumps(merged_config, indent=2))
            
            return backup_path
            
        except json.JSONDecodeError as e:
            print(f"  ⚠️  Error parsing JSON configs: {e}")
            return None
        except Exception as e:
            print(f"  ⚠️  Error merging configs: {e}")
            return None