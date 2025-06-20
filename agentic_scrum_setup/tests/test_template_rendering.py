"""Tests for template rendering in the patching system."""

import json
import pytest
import tempfile
from pathlib import Path
import yaml

from agentic_scrum_setup.patching.utils.project_context import load_project_context, detect_project_language
from agentic_scrum_setup.patching.utils.template_renderer import TemplateRenderer


class TestProjectContext:
    """Test project context loading."""
    
    def test_load_context_with_config(self):
        """Test loading context from agentic_config.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / "agentic_config.yaml"
            
            # Create test config
            config = {
                'project_name': 'TestProject',
                'language': 'python',
                'agents': ['poa', 'sma', 'deva_python'],
                'enable_search': True,
                'enable_mcp': True,
                'llm_provider': 'openai',
                'default_model': 'gpt-4'
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
            
            # Load context
            context = load_project_context(project_path)
            
            assert context['project_name'] == 'TestProject'
            assert context['language'] == 'python'
            assert context['agents'] == ['poa', 'sma', 'deva_python']
            assert context['enable_search'] is True
            assert context['llm_provider'] == 'openai'
    
    def test_load_context_without_config(self):
        """Test loading context when config is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            context = load_project_context(project_path)
            
            # Should use defaults
            assert context['project_name'] == Path(tmpdir).name
            assert context['language'] == 'python'
            assert context['agents'] == ['poa', 'sma', 'deva_python', 'qaa']
            assert context['enable_search'] is False
    
    def test_detect_python_project(self):
        """Test language detection for Python project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create Python indicators
            (project_path / "setup.py").touch()
            (project_path / "requirements.txt").touch()
            
            language = detect_project_language(project_path)
            assert language == 'python'
    
    def test_detect_typescript_project(self):
        """Test language detection for TypeScript project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create TypeScript indicators
            (project_path / "tsconfig.json").touch()
            (project_path / "index.ts").touch()
            
            language = detect_project_language(project_path)
            assert language == 'typescript'


class TestTemplateRenderer:
    """Test template rendering functionality."""
    
    def test_render_simple_template(self):
        """Test rendering a simple template string."""
        context = {
            'project_name': 'MyProject',
            'language': 'python'
        }
        
        renderer = TemplateRenderer(context)
        template = "Project: {{ project_name }}, Language: {{ language }}"
        rendered = renderer.render_string(template)
        
        assert rendered == "Project: MyProject, Language: python"
    
    def test_render_json_template(self):
        """Test rendering a JSON template with tojson filter."""
        context = {
            'project_name': 'TestProject',
            'agents': ['poa', 'sma', 'deva_python']
        }
        
        renderer = TemplateRenderer(context)
        template = '{"name": "{{ project_name }}", "agents": {{ agents | tojson }}}'
        rendered = renderer.render_string(template)
        
        # Should produce valid JSON
        data = json.loads(rendered)
        assert data['name'] == 'TestProject'
        assert data['agents'] == ['poa', 'sma', 'deva_python']
    
    def test_render_conditional_template(self):
        """Test rendering template with conditionals."""
        context = {
            'enable_search': True,
            'api_key': 'test-key'
        }
        
        renderer = TemplateRenderer(context)
        template = '''
        {
            "search": {% if enable_search %}
            {
                "enabled": true,
                "key": "{{ api_key }}"
            }
            {% else %}
            null
            {% endif %}
        }
        '''
        
        rendered = renderer.render_string(template)
        data = json.loads(rendered)
        assert data['search']['enabled'] is True
        assert data['search']['key'] == 'test-key'
    
    def test_render_file_with_validation(self):
        """Test rendering a file with JSON validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "template.json.j2"
            target_path = Path(tmpdir) / "output.json"
            
            context = {
                'project_name': 'Test',
                'agents': ['poa', 'sma']
            }
            
            # Create template
            template_path.write_text('''
            {
                "name": "{{ project_name }}",
                "agents": {{ agents | tojson }}
            }
            ''')
            
            renderer = TemplateRenderer(context)
            renderer.render_file(template_path, target_path)
            
            # Verify output
            assert target_path.exists()
            data = json.loads(target_path.read_text())
            assert data['name'] == 'Test'
            assert data['agents'] == ['poa', 'sma']
    
    def test_invalid_json_rendering_raises_error(self):
        """Test that invalid JSON rendering raises an error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "bad.json.j2"
            target_path = Path(tmpdir) / "output.json"
            
            context = {'value': 'missing quote'}
            
            # Create bad template
            template_path.write_text('{"key": {{ value }}}')  # Missing quotes
            
            renderer = TemplateRenderer(context)
            
            with pytest.raises(ValueError) as exc_info:
                renderer.render_file(template_path, target_path)
            
            assert "invalid JSON" in str(exc_info.value)
    
    def test_should_render_file(self):
        """Test file rendering detection."""
        renderer = TemplateRenderer({})
        
        # Should render .j2 files
        assert renderer.should_render_file(Path("template.yaml.j2"))
        assert renderer.should_render_file(Path("config.json.j2"))
        
        # Should render special files
        assert renderer.should_render_file(Path(".mcp.json"))
        assert renderer.should_render_file(Path("agentic_config.yaml"))
        
        # Should not render regular files
        assert not renderer.should_render_file(Path("script.py"))
        assert not renderer.should_render_file(Path("README.md"))