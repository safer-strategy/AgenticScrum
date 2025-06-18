"""Sync changes operation for AgenticScrum patching system.

This module handles syncing changes from local projects back to the framework,
enabling reverse patching for improvements discovered during development.
"""

import shutil
import filecmp
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import difflib

from ..validation import PatchValidator


class SyncChangesOperation:
    """Handles syncing changes from projects back to the framework."""
    
    def __init__(self, framework_path: Path, validator: PatchValidator):
        """Initialize the operation.
        
        Args:
            framework_path: Path to AgenticScrum framework
            validator: Patch validator instance
        """
        self.framework_path = framework_path
        self.validator = validator
        self.templates_dir = framework_path / 'agentic_scrum_setup' / 'templates'
    
    def sync_from_project(self, project_path: Path, sync_options: Dict[str, bool] = None) -> List[Path]:
        """Sync changes from a project back to the framework.
        
        Args:
            project_path: Path to project to sync from
            sync_options: Options for what to sync (templates, configs, etc.)
            
        Returns:
            List of files that were modified in the framework
        """
        if not project_path.exists():
            raise ValueError(f"Project path not found: {project_path}")
        
        if sync_options is None:
            sync_options = {
                'templates': True,
                'mcp_configs': True,
                'agent_configs': True,
                'scripts': False,  # Scripts are usually project-specific
                'docs': False     # Docs are usually project-specific
            }
        
        modified_files = []
        
        # Sync agent templates
        if sync_options.get('templates', False):
            template_files = self._sync_agent_templates(project_path)
            modified_files.extend(template_files)
        
        # Sync MCP configurations
        if sync_options.get('mcp_configs', False):
            mcp_files = self._sync_mcp_configs(project_path)
            modified_files.extend(mcp_files)
        
        # Sync agent configurations
        if sync_options.get('agent_configs', False):
            config_files = self._sync_agent_configs(project_path)
            modified_files.extend(config_files)
        
        # Sync scripts if requested
        if sync_options.get('scripts', False):
            script_files = self._sync_scripts(project_path)
            modified_files.extend(script_files)
        
        print(f"✅ Synced {len(modified_files)} files from {project_path.name}")
        return modified_files
    
    def compare_projects(self, project1_path: Path, project2_path: Path) -> Dict[str, Any]:
        """Compare two projects to identify differences.
        
        Args:
            project1_path: Path to first project
            project2_path: Path to second project
            
        Returns:
            Dictionary with comparison results
        """
        if not project1_path.exists():
            raise ValueError(f"Project 1 not found: {project1_path}")
        if not project2_path.exists():
            raise ValueError(f"Project 2 not found: {project2_path}")
        
        comparison = {
            'different_files': [],
            'unique_to_project1': [],
            'unique_to_project2': [],
            'identical_files': []
        }
        
        # Get relevant files from both projects
        project1_files = self._get_syncable_files(project1_path)
        project2_files = self._get_syncable_files(project2_path)
        
        # Compare files
        for rel_path in project1_files:
            file1 = project1_path / rel_path
            file2 = project2_path / rel_path
            
            if rel_path in project2_files:
                if filecmp.cmp(file1, file2, shallow=False):
                    comparison['identical_files'].append(str(rel_path))
                else:
                    comparison['different_files'].append({
                        'path': str(rel_path),
                        'project1_size': file1.stat().st_size,
                        'project2_size': file2.stat().st_size,
                        'project1_mtime': file1.stat().st_mtime,
                        'project2_mtime': file2.stat().st_mtime
                    })
            else:
                comparison['unique_to_project1'].append(str(rel_path))
        
        # Files unique to project2
        for rel_path in project2_files:
            if rel_path not in project1_files:
                comparison['unique_to_project2'].append(str(rel_path))
        
        return comparison
    
    def sync_specific_files(self, source_project: Path, target_files: List[str]) -> List[Path]:
        """Sync specific files from a project to the framework.
        
        Args:
            source_project: Project to sync from
            target_files: List of relative file paths to sync
            
        Returns:
            List of files modified in framework
        """
        if not source_project.exists():
            raise ValueError(f"Source project not found: {source_project}")
        
        modified_files = []
        
        for target_file in target_files:
            source_file = source_project / target_file
            
            if not source_file.exists():
                print(f"⚠️  File not found in source project: {target_file}")
                continue
            
            # Determine target location in framework
            framework_target = self._determine_framework_target(target_file)
            
            if framework_target:
                # Validate source file
                validation_result = self.validator.validate_file_content(
                    source_file, source_file.read_text()
                )
                
                if not validation_result.is_valid:
                    print(f"⚠️  Validation failed for {target_file}: {validation_result.error_message}")
                    continue
                
                # Copy file to framework
                framework_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, framework_target)
                modified_files.append(framework_target)
                
                print(f"✅ Synced {target_file} -> {framework_target.relative_to(self.framework_path)}")
        
        return modified_files
    
    def create_sync_patch(self, source_project: Path, target_file: str) -> str:
        """Create a patch showing differences between project and framework files.
        
        Args:
            source_project: Project to compare
            target_file: Relative path to file
            
        Returns:
            Unified diff patch string
        """
        source_file = source_project / target_file
        framework_target = self._determine_framework_target(target_file)
        
        if not source_file.exists():
            raise ValueError(f"Source file not found: {source_file}")
        
        if not framework_target or not framework_target.exists():
            # New file
            source_content = source_file.read_text().splitlines(keepends=True)
            framework_content = []
        else:
            source_content = source_file.read_text().splitlines(keepends=True)
            framework_content = framework_target.read_text().splitlines(keepends=True)
        
        # Generate unified diff
        diff = difflib.unified_diff(
            framework_content,
            source_content,
            fromfile=f'a/{framework_target.relative_to(self.framework_path) if framework_target else target_file}',
            tofile=f'b/{framework_target.relative_to(self.framework_path) if framework_target else target_file}',
            lineterm=''
        )
        
        return ''.join(diff)
    
    def _sync_agent_templates(self, project_path: Path) -> List[Path]:
        """Sync agent templates from project to framework.
        
        Args:
            project_path: Path to project
            
        Returns:
            List of modified framework files
        """
        modified_files = []
        
        # Look for agent directories in the project
        agents_dir = project_path / 'agents'
        if not agents_dir.exists():
            return modified_files
        
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            
            agent_name = agent_dir.name
            
            # Look for persona rules and other templates
            template_files = [
                'persona_rules.yaml',
                'memory_patterns.yaml',
                'search_patterns.yaml'
            ]
            
            for template_file in template_files:
                source_template = agent_dir / template_file
                
                if source_template.exists():
                    # Target location in framework
                    target_template = self.templates_dir / agent_name / f'{template_file}.j2'
                    
                    # Check if framework template exists and compare
                    if target_template.exists():
                        if not filecmp.cmp(source_template, target_template, shallow=False):
                            # Files are different - ask user or auto-merge
                            print(f"📝 Template difference found: {agent_name}/{template_file}")
                            
                            # For now, copy the project version
                            target_template.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source_template, target_template)
                            modified_files.append(target_template)
                    else:
                        # New template
                        target_template.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_template, target_template)
                        modified_files.append(target_template)
        
        return modified_files
    
    def _sync_mcp_configs(self, project_path: Path) -> List[Path]:
        """Sync MCP configurations from project to framework.
        
        Args:
            project_path: Path to project
            
        Returns:
            List of modified framework files
        """
        modified_files = []
        
        # Sync .mcp.json configuration
        project_mcp_config = project_path / '.mcp.json'
        framework_mcp_template = self.templates_dir / 'claude' / '.mcp.json.j2'
        
        if project_mcp_config.exists():
            # Convert project config to template format
            config_content = project_mcp_config.read_text()
            
            # Replace project-specific values with template variables
            project_name = project_path.name
            template_content = config_content.replace(project_name, '{{ project_name }}')
            
            # Check if different from framework template
            if framework_mcp_template.exists():
                framework_content = framework_mcp_template.read_text()
                if template_content != framework_content:
                    framework_mcp_template.write_text(template_content)
                    modified_files.append(framework_mcp_template)
            else:
                framework_mcp_template.parent.mkdir(parents=True, exist_ok=True)
                framework_mcp_template.write_text(template_content)
                modified_files.append(framework_mcp_template)
        
        # Sync MCP service files
        project_mcp_dir = project_path / '.mcp'
        if project_mcp_dir.exists():
            for service_file in project_mcp_dir.rglob('*.py'):
                if service_file.is_file():
                    # Convert to template
                    service_content = service_file.read_text()
                    
                    # Replace project-specific values
                    project_name = project_path.name
                    template_content = service_content.replace(project_name, '{{ project_name }}')
                    
                    # Target location in framework templates
                    relative_path = service_file.relative_to(project_mcp_dir)
                    target_template = self.templates_dir / 'claude' / f'{relative_path}.j2'
                    
                    target_template.parent.mkdir(parents=True, exist_ok=True)
                    target_template.write_text(template_content)
                    modified_files.append(target_template)
        
        return modified_files
    
    def _sync_agent_configs(self, project_path: Path) -> List[Path]:
        """Sync agent configurations from project to framework.
        
        Args:
            project_path: Path to project
            
        Returns:
            List of modified framework files
        """
        modified_files = []
        
        # Sync agentic_config.yaml improvements
        project_config = project_path / 'agentic_config.yaml'
        
        if project_config.exists():
            # Look for new configuration options that could be added to templates
            config_content = project_config.read_text()
            
            # Extract configuration patterns that could be templated
            new_options = self._extract_new_config_options(config_content)
            
            if new_options:
                # Update base configuration template
                base_config_template = self.templates_dir / 'agentic_config.yaml.j2'
                
                if base_config_template.exists():
                    template_content = base_config_template.read_text()
                    
                    # Add new options to template
                    for option_name, option_value in new_options.items():
                        if option_name not in template_content:
                            # Add new option to template
                            template_content += f'\n# {option_name}\n{option_name}: {option_value}\n'
                    
                    base_config_template.write_text(template_content)
                    modified_files.append(base_config_template)
        
        return modified_files
    
    def _sync_scripts(self, project_path: Path) -> List[Path]:
        """Sync useful scripts from project to framework.
        
        Args:
            project_path: Path to project
            
        Returns:
            List of modified framework files
        """
        modified_files = []
        
        # Look for scripts that could be useful framework-wide
        scripts_dir = project_path / 'scripts'
        if not scripts_dir.exists():
            return modified_files
        
        framework_scripts_dir = self.framework_path / 'scripts'
        
        for script_file in scripts_dir.iterdir():
            if script_file.is_file() and script_file.suffix == '.py':
                # Check if this is a general-purpose script
                script_content = script_file.read_text()
                
                # Heuristics to determine if script is framework-worthy
                if any(keyword in script_content for keyword in [
                    'agentic_scrum_setup',
                    'AgenticScrum',
                    'framework',
                    'template'
                ]):
                    target_script = framework_scripts_dir / script_file.name
                    
                    # Copy if new or different
                    if not target_script.exists() or not filecmp.cmp(script_file, target_script):
                        shutil.copy2(script_file, target_script)
                        modified_files.append(target_script)
        
        return modified_files
    
    def _get_syncable_files(self, project_path: Path) -> Set[Path]:
        """Get set of files that can be synced from a project.
        
        Args:
            project_path: Path to project
            
        Returns:
            Set of relative paths that can be synced
        """
        syncable_files = set()
        
        # Syncable patterns
        patterns = [
            'agents/**/*.yaml',
            'agents/**/*.yml',
            '.mcp.json',
            '.mcp/**/*.py',
            'agentic_config.yaml',
            'scripts/*.py'
        ]
        
        for pattern in patterns:
            for file_path in project_path.glob(pattern):
                if file_path.is_file():
                    syncable_files.add(file_path.relative_to(project_path))
        
        return syncable_files
    
    def _determine_framework_target(self, project_relative_path: str) -> Optional[Path]:
        """Determine target location in framework for a project file.
        
        Args:
            project_relative_path: Relative path in project
            
        Returns:
            Target path in framework, or None if not syncable
        """
        rel_path = Path(project_relative_path)
        
        # Agent templates
        if rel_path.parts[0] == 'agents' and len(rel_path.parts) >= 3:
            agent_name = rel_path.parts[1]
            template_name = rel_path.parts[2]
            
            # Add .j2 extension if not present
            if not template_name.endswith('.j2'):
                template_name += '.j2'
            
            return self.templates_dir / agent_name / template_name
        
        # MCP configuration
        if rel_path.name == '.mcp.json':
            return self.templates_dir / 'claude' / '.mcp.json.j2'
        
        # MCP services
        if rel_path.parts[0] == '.mcp' and rel_path.suffix == '.py':
            service_name = rel_path.name + '.j2'
            return self.templates_dir / 'claude' / service_name
        
        # Configuration template
        if rel_path.name == 'agentic_config.yaml':
            return self.templates_dir / 'agentic_config.yaml.j2'
        
        # Scripts
        if rel_path.parts[0] == 'scripts' and rel_path.suffix == '.py':
            return self.framework_path / 'scripts' / rel_path.name
        
        return None
    
    def _extract_new_config_options(self, config_content: str) -> Dict[str, str]:
        """Extract new configuration options from project config.
        
        Args:
            config_content: Content of project configuration
            
        Returns:
            Dictionary of new options
        """
        # This is a simplified implementation
        # A full version would parse YAML and compare with base template
        new_options = {}
        
        lines = config_content.split('\n')
        for line in lines:
            line = line.strip()
            if line and ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Check if this is a potentially new option
                if key not in ['project_name', 'language', 'framework', 'agents']:
                    new_options[key] = value
        
        return new_options