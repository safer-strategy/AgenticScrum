"""Update MCP operation for AgenticScrum patching system.

This module handles updating MCP (Model Context Protocol) services and 
configurations in the framework and existing projects.
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..validation import PatchValidator


class UpdateMCPOperation:
    """Handles updating MCP services and configurations."""
    
    def __init__(self, framework_path: Path, validator: PatchValidator):
        """Initialize the operation.
        
        Args:
            framework_path: Path to AgenticScrum framework
            validator: Patch validator instance
        """
        self.framework_path = framework_path
        self.validator = validator
        self.mcp_templates_dir = framework_path / 'agentic_scrum_setup' / 'templates' / 'claude'
    
    def update_mcp_service(self, service_file: Path) -> List[Path]:
        """Update an MCP service configuration.
        
        Args:
            service_file: Path to new MCP service file
            
        Returns:
            List of files that were modified/created
        """
        if not service_file.exists():
            raise ValueError(f"MCP service file not found: {service_file}")
        
        # Validate service file
        validation_result = self.validator.validate_file_content(service_file, service_file.read_text())
        if not validation_result.is_valid:
            raise ValueError(f"MCP service validation failed: {validation_result.error_message}")
        
        modified_files = []
        
        # Copy service file to templates
        target_path = self.mcp_templates_dir / service_file.name
        shutil.copy2(service_file, target_path)
        modified_files.append(target_path)
        
        return modified_files
    
    def add_mcp_to_project(self, project_path: Path) -> List[Path]:
        """Add MCP configuration to an existing project.
        
        Args:
            project_path: Path to existing project
            
        Returns:
            List of files that were created/modified
        """
        if not project_path.exists():
            raise ValueError(f"Project path not found: {project_path}")
        
        modified_files = []
        
        # Check if project already has MCP configuration
        mcp_config_file = project_path / '.mcp.json'
        if mcp_config_file.exists():
            print(f"⚠️  MCP configuration already exists at {mcp_config_file}")
            print("Would you like to update it? (This will backup the existing config)")
            # In a real implementation, this would be handled by the CLI
        
        # Copy MCP configuration template
        template_mcp_config = self.mcp_templates_dir / '.mcp.json.j2'
        if template_mcp_config.exists():
            # Read template and render with project-specific values
            template_content = template_mcp_config.read_text()
            
            # Simple template variable replacement
            # In a full implementation, this would use Jinja2
            project_name = project_path.name
            rendered_content = template_content.replace('{{ project_name }}', project_name)
            
            mcp_config_file.write_text(rendered_content)
            modified_files.append(mcp_config_file)
        
        # Create MCP services directory
        mcp_services_dir = project_path / '.mcp' / 'services'
        mcp_services_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy memory service
        memory_service_template = self.mcp_templates_dir / 'memory_service.py.j2'
        if memory_service_template.exists():
            target_memory_service = mcp_services_dir / 'memory_service.py'
            template_content = memory_service_template.read_text()
            
            # Render template
            project_name = project_path.name
            rendered_content = template_content.replace('{{ project_name }}', project_name)
            
            target_memory_service.write_text(rendered_content)
            modified_files.append(target_memory_service)
        
        # Copy search service if enabled
        search_service_template = self.mcp_templates_dir / 'search_service.py.j2'
        if search_service_template.exists():
            target_search_service = mcp_services_dir / 'search_service.py'
            template_content = search_service_template.read_text()
            
            # Render template
            project_name = project_path.name
            rendered_content = template_content.replace('{{ project_name }}', project_name)
            
            target_search_service.write_text(rendered_content)
            modified_files.append(target_search_service)
        
        # Update project configuration to enable MCP
        agentic_config = project_path / 'agentic_config.yaml'
        if agentic_config.exists():
            content = agentic_config.read_text()
            
            # Check if MCP is already configured
            if 'enable_mcp: true' not in content:
                # Add MCP configuration
                lines = content.split('\n')
                
                # Find a good place to insert MCP config
                insert_index = len(lines)
                for i, line in enumerate(lines):
                    if line.startswith('llm_provider:'):
                        insert_index = i + 2  # Insert after LLM config
                        break
                
                mcp_config_lines = [
                    '',
                    '# MCP (Model Context Protocol) Configuration',
                    'enable_mcp: true',
                    'enable_search: true',
                    'mcp_services:',
                    '  - memory',
                    '  - search'
                ]
                
                # Insert MCP configuration
                for j, mcp_line in enumerate(mcp_config_lines):
                    lines.insert(insert_index + j, mcp_line)
                
                agentic_config.write_text('\n'.join(lines))
                modified_files.append(agentic_config)
        
        return modified_files
    
    def update_mcp_template(self, template_name: str, template_content: str) -> List[Path]:
        """Update an MCP template in the framework.
        
        Args:
            template_name: Name of the template file
            template_content: New template content
            
        Returns:
            List of files that were modified
        """
        # Validate template content
        validation_result = self.validator.validate_file_content(
            Path(template_name), template_content
        )
        if not validation_result.is_valid:
            raise ValueError(f"Template validation failed: {validation_result.error_message}")
        
        # Write template file
        template_path = self.mcp_templates_dir / template_name
        template_path.write_text(template_content)
        
        return [template_path]
    
    def add_custom_mcp_service(self, service_name: str, service_code: str) -> List[Path]:
        """Add a custom MCP service to the framework.
        
        Args:
            service_name: Name of the service
            service_code: Python code for the service
            
        Returns:
            List of files that were created/modified
        """
        # Validate service code
        validation_result = self.validator.validate_file_content(
            Path(f'{service_name}_service.py'), service_code
        )
        if not validation_result.is_valid:
            raise ValueError(f"Service code validation failed: {validation_result.error_message}")
        
        modified_files = []
        
        # Create service template
        service_template_path = self.mcp_templates_dir / f'{service_name}_service.py.j2'
        service_template_path.write_text(service_code)
        modified_files.append(service_template_path)
        
        # Update MCP configuration template to include new service
        mcp_config_template = self.mcp_templates_dir / '.mcp.json.j2'
        if mcp_config_template.exists():
            content = mcp_config_template.read_text()
            
            # Parse JSON-like content to add new service
            # This is a simplified approach; a full implementation would use proper JSON parsing
            if f'"{service_name}"' not in content:
                # Add service to services list
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '"services":' in line:
                        # Find the end of services array
                        for j in range(i, len(lines)):
                            if ']' in lines[j]:
                                # Insert new service before closing bracket
                                indent = '      '  # Match existing indentation
                                lines.insert(j, f'{indent}"{service_name}",')
                                break
                        break
                
                mcp_config_template.write_text('\n'.join(lines))
                modified_files.append(mcp_config_template)
        
        return modified_files
    
    def upgrade_mcp_version(self, version: str) -> List[Path]:
        """Upgrade MCP to a new version.
        
        Args:
            version: Target MCP version
            
        Returns:
            List of files that were modified
        """
        modified_files = []
        
        # Update MCP configuration template with new version
        mcp_config_template = self.mcp_templates_dir / '.mcp.json.j2'
        if mcp_config_template.exists():
            content = mcp_config_template.read_text()
            
            # Update version in JSON
            import json
            try:
                # Remove Jinja2 template syntax for parsing
                temp_content = content.replace('{{ project_name }}', 'temp_project')
                config_data = json.loads(temp_content)
                config_data['version'] = version
                
                # Convert back to template format
                updated_content = json.dumps(config_data, indent=2)
                updated_content = updated_content.replace('temp_project', '{{ project_name }}')
                
                mcp_config_template.write_text(updated_content)
                modified_files.append(mcp_config_template)
            except json.JSONDecodeError:
                # Fallback to string replacement
                import re
                version_pattern = r'"version":\s*"[^"]*"'
                replacement = f'"version": "{version}"'
                updated_content = re.sub(version_pattern, replacement, content)
                
                mcp_config_template.write_text(updated_content)
                modified_files.append(mcp_config_template)
        
        # Update service templates if needed for version compatibility
        service_files = list(self.mcp_templates_dir.glob('*_service.py.j2'))
        for service_file in service_files:
            content = service_file.read_text()
            
            # Check if content needs updating for new version
            if 'mcp_version' in content or 'MCP_VERSION' in content:
                # Update version references in service code
                updated_content = content.replace(
                    'MCP_VERSION = "', f'MCP_VERSION = "{version}"'
                )
                
                if updated_content != content:
                    service_file.write_text(updated_content)
                    modified_files.append(service_file)
        
        return modified_files
    
    def sync_mcp_config(self, source_project: Path, target_project: Path) -> List[Path]:
        """Sync MCP configuration from one project to another.
        
        Args:
            source_project: Project to copy MCP config from
            target_project: Project to copy MCP config to
            
        Returns:
            List of files that were modified in target project
        """
        if not source_project.exists():
            raise ValueError(f"Source project not found: {source_project}")
        if not target_project.exists():
            raise ValueError(f"Target project not found: {target_project}")
        
        modified_files = []
        
        # Copy MCP configuration
        source_mcp_config = source_project / '.mcp.json'
        target_mcp_config = target_project / '.mcp.json'
        
        if source_mcp_config.exists():
            shutil.copy2(source_mcp_config, target_mcp_config)
            modified_files.append(target_mcp_config)
        
        # Copy MCP services
        source_mcp_dir = source_project / '.mcp'
        target_mcp_dir = target_project / '.mcp'
        
        if source_mcp_dir.exists():
            if target_mcp_dir.exists():
                shutil.rmtree(target_mcp_dir)
            shutil.copytree(source_mcp_dir, target_mcp_dir)
            
            # Add all copied files to modified list
            for mcp_file in target_mcp_dir.rglob('*'):
                if mcp_file.is_file():
                    modified_files.append(mcp_file)
        
        return modified_files