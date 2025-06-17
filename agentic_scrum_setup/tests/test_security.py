"""Tests for security features."""

import tempfile
from pathlib import Path
import pytest

from agentic_scrum_setup.setup_core import SetupCore


class TestSecurityFeatures:
    """Test cases for security-related functionality."""
    
    @pytest.fixture
    def test_config(self):
        """Provide test configuration."""
        return {
            'project_name': 'SecurityTestProject',
            'language': 'python',
            'agents': 'poa,sma,deva_python,qaa',
            'llm_provider': 'openai',
            'default_model': 'gpt-4',
            'output_dir': tempfile.mkdtemp()
        }
    
    def test_agentic_config_gitignored(self, test_config):
        """Test that agentic_config.yaml is in .gitignore."""
        setup_core = SetupCore(test_config)
        setup_core.create_project()
        
        project_path = Path(test_config['output_dir']) / 'SecurityTestProject'
        gitignore_path = project_path / '.gitignore'
        
        assert gitignore_path.exists()
        gitignore_content = gitignore_path.read_text()
        
        # Check that agentic_config.yaml is gitignored
        assert 'agentic_config.yaml' in gitignore_content
        assert 'agentic_config.yml' in gitignore_content
        
        # Check other security-related entries
        assert '*.secret' in gitignore_content
        assert '*.key' in gitignore_content
        assert 'credentials.json' in gitignore_content
    
    def test_sample_config_created(self, test_config):
        """Test that agentic_config.yaml.sample is created."""
        setup_core = SetupCore(test_config)
        setup_core.create_project()
        
        project_path = Path(test_config['output_dir']) / 'SecurityTestProject'
        
        # Both files should exist
        assert (project_path / 'agentic_config.yaml').exists()
        assert (project_path / 'agentic_config.yaml.sample').exists()
        
        # Sample should contain security warnings
        sample_content = (project_path / 'agentic_config.yaml.sample').read_text()
        assert 'IMPORTANT:' in sample_content
        assert 'gitignored for security' in sample_content
        assert 'NEVER commit' in sample_content
    
    def test_api_key_uses_env_var(self, test_config):
        """Test that API keys reference environment variables."""
        setup_core = SetupCore(test_config)
        setup_core.create_project()
        
        project_path = Path(test_config['output_dir']) / 'SecurityTestProject'
        config_content = (project_path / 'agentic_config.yaml').read_text()
        
        # Should use environment variable format
        assert '${OPENAI_API_KEY}' in config_content
        
        # Should not contain actual API keys
        assert 'sk-' not in config_content  # OpenAI keys start with sk-
        assert 'your-actual-api-key' not in config_content
    
    def test_security_documentation_created(self, test_config):
        """Test that SECURITY.md is created."""
        setup_core = SetupCore(test_config)
        setup_core.create_project()
        
        project_path = Path(test_config['output_dir']) / 'SecurityTestProject'
        security_doc_path = project_path / 'docs' / 'SECURITY.md'
        
        assert security_doc_path.exists()
        security_content = security_doc_path.read_text()
        
        # Check for important security content
        assert 'Never Commit API Keys' in security_content
        assert 'Environment Variables' in security_content
        assert 'Security Checklist' in security_content
        assert 'If You Accidentally Commit Secrets' in security_content
    
    def test_readme_mentions_security(self, test_config):
        """Test that README mentions security configuration."""
        setup_core = SetupCore(test_config)
        setup_core.create_project()
        
        project_path = Path(test_config['output_dir']) / 'SecurityTestProject'
        readme_content = (project_path / 'README.md').read_text()
        
        # README should mention security setup
        assert 'Configure API Keys' in readme_content
        assert 'agentic_config.yaml.sample' in readme_content
        assert 'Never commit' in readme_content
        assert 'docs/SECURITY.md' in readme_content
    
    def test_no_hardcoded_secrets(self, test_config):
        """Test that no files contain hardcoded secrets."""
        setup_core = SetupCore(test_config)
        setup_core.create_project()
        
        project_path = Path(test_config['output_dir']) / 'SecurityTestProject'
        
        # Common patterns that indicate hardcoded secrets
        import re
        secret_patterns = [
            (r'password\s*=\s*["\']?[A-Za-z0-9+/=]{8,}', 'password'),
            (r'api[_-]?key\s*=\s*["\']?[A-Za-z0-9+/=]{20,}', 'api_key'),
            (r'secret\s*=\s*["\']?[A-Za-z0-9+/=]{16,}', 'secret'),
            (r'token\s*=\s*["\']?[A-Za-z0-9+/=]{20,}', 'token'),
            (r'sk-[A-Za-z0-9]{48}', 'OpenAI API key'),  # OpenAI
            (r'claude-[0-9a-zA-Z]{40,}', 'Anthropic API key'),  # Anthropic API keys
            (r'AIza[0-9A-Za-z\-_]{35}', 'Google API key'),  # Google
        ]
        
        # Check all generated files (except .sample)
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and '.sample' not in file_path.name:
                content = file_path.read_text(errors='ignore')
                for pattern, desc in secret_patterns:
                    # Allow environment variable references
                    if re.search(pattern, content) and '${' not in content:
                        # Additional check: skip if it's in a comment or documentation
                        lines = content.split('\n')
                        for line in lines:
                            if re.search(pattern, line):
                                # Skip if it's a comment line or in quotes as an example
                                if line.strip().startswith('#') or line.strip().startswith('//') or 'example:' in line.lower() or 'e.g.' in line:
                                    continue
                                # Skip if it's a model name reference
                                if 'model' in line.lower() or 'claude-3' in line or 'claude-opus' in line or 'claude-sonnet' in line:
                                    continue
                                pytest.fail(f"Found potential {desc} in {file_path}")