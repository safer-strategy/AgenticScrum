"""Template rendering utilities for the patching system."""

import json
from pathlib import Path
from typing import Dict, Any
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape


class TemplateRenderer:
    """Handle Jinja2 template rendering for patch operations."""
    
    def __init__(self, context: Dict[str, Any]):
        """
        Initialize renderer with project context.
        
        Args:
            context: Dictionary of template variables
        """
        self.context = context
        self.env = Environment(
            loader=FileSystemLoader('/'),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['tojson'] = self._tojson_filter
    
    def _tojson_filter(self, value):
        """Custom tojson filter that matches Jinja2 behavior."""
        return json.dumps(value)
    
    def render_string(self, template_string: str) -> str:
        """
        Render a template string with context.
        
        Args:
            template_string: Jinja2 template content
            
        Returns:
            Rendered string
        """
        template = Template(template_string)
        return template.render(**self.context)
    
    def render_file(self, template_path: Path, target_path: Path) -> None:
        """
        Render a template file to a target location.
        
        Args:
            template_path: Path to Jinja2 template file
            target_path: Path where rendered content should be written
            
        Raises:
            ValueError: If rendered JSON is invalid
        """
        # Read template
        template_content = template_path.read_text()
        
        # Render with context
        rendered = self.render_string(template_content)
        
        # Validate if JSON file
        if target_path.suffix == '.json':
            try:
                json.loads(rendered)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Template rendering produced invalid JSON in {target_path}:\n"
                    f"Error: {e}\n"
                    f"Content preview: {rendered[:200]}..."
                )
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write rendered content
        target_path.write_text(rendered)
    
    def should_render_file(self, file_path: Path) -> bool:
        """
        Check if a file should be rendered as a template.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file should be rendered
        """
        # Render .j2 files
        if file_path.suffix == '.j2':
            return True
        
        # Also render certain files that might have inline templates
        template_files = {'.mcp.json', 'agentic_config.yaml'}
        if file_path.name in template_files:
            return True
        
        return False
    
    def copy_with_rendering(self, source_path: Path, target_path: Path) -> None:
        """
        Copy a file, rendering it if necessary.
        
        Args:
            source_path: Source file path
            target_path: Target file path
        """
        # Remove .j2 extension from target if present
        if target_path.suffix == '.j2':
            target_path = target_path.with_suffix('')
        
        if self.should_render_file(source_path):
            self.render_file(source_path, target_path)
        else:
            # Regular copy
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(source_path.read_text())