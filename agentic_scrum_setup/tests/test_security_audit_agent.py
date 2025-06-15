"""Tests for SecurityAuditAgent functionality."""

import tempfile
from pathlib import Path
import pytest

from agentic_scrum_setup.setup_core import SetupCore


class TestSecurityAuditAgent:
    """Test cases for SecurityAuditAgent creation and configuration."""
    
    @pytest.fixture
    def test_config_with_saa(self):
        """Provide test configuration with SecurityAuditAgent."""
        return {
            'project_name': 'SecureWebApp',
            'language': 'python',
            'framework': 'fastapi',
            'agents': 'poa,sma,deva_python,qaa,saa',
            'llm_provider': 'openai',
            'default_model': 'gpt-4',
            'output_dir': tempfile.mkdtemp()
        }
    
    def test_saa_agent_created(self, test_config_with_saa):
        """Test that SecurityAuditAgent is properly created."""
        setup_core = SetupCore(test_config_with_saa)
        setup_core.create_project()
        
        project_path = Path(test_config_with_saa['output_dir']) / 'SecureWebApp'
        saa_path = project_path / 'agents' / 'security_audit_agent'
        
        # Check agent directory exists
        assert saa_path.exists()
        assert saa_path.is_dir()
        
        # Check persona_rules.yaml exists
        persona_rules_path = saa_path / 'persona_rules.yaml'
        assert persona_rules_path.exists()
        
        # Check priming_script.md exists
        priming_script_path = saa_path / 'priming_script.md'
        assert priming_script_path.exists()
    
    def test_saa_persona_rules_content(self, test_config_with_saa):
        """Test SecurityAuditAgent persona rules content."""
        setup_core = SetupCore(test_config_with_saa)
        setup_core.create_project()
        
        project_path = Path(test_config_with_saa['output_dir']) / 'SecureWebApp'
        persona_rules_path = project_path / 'agents' / 'security_audit_agent' / 'persona_rules.yaml'
        
        content = persona_rules_path.read_text()
        
        # Check key elements
        assert 'role: Security Audit Agent' in content
        assert 'OWASP Top 10' in content
        assert 'SQL injection' in content
        assert 'XSS' in content
        assert 'CSRF' in content
        assert 'authentication' in content
        assert 'authorization' in content
        assert 'input validation' in content
        assert 'hardcoded secrets' in content
        assert 'temperature: 0.2' in content  # Lower temperature for security
    
    def test_saa_priming_script_content(self, test_config_with_saa):
        """Test SecurityAuditAgent priming script content."""
        setup_core = SetupCore(test_config_with_saa)
        setup_core.create_project()
        
        project_path = Path(test_config_with_saa['output_dir']) / 'SecureWebApp'
        priming_script_path = project_path / 'agents' / 'security_audit_agent' / 'priming_script.md'
        
        content = priming_script_path.read_text()
        
        # Check mission elements
        assert 'SecurityAuditAgent' in content
        assert 'security audit' in content
        assert 'Frontend Security' in content
        assert 'Backend Security' in content
        assert 'Key Management' in content
        assert 'SecureWebApp' in content  # Project name
        assert 'fastapi' in content  # Framework
    
    def test_security_audit_checklist_created(self, test_config_with_saa):
        """Test that security audit checklist is created."""
        setup_core = SetupCore(test_config_with_saa)
        setup_core.create_project()
        
        project_path = Path(test_config_with_saa['output_dir']) / 'SecureWebApp'
        checklist_path = project_path / 'checklists' / 'security_audit_checklist.md'
        
        assert checklist_path.exists()
        
        content = checklist_path.read_text()
        
        # Check major sections
        assert 'Input Validation and Sanitization' in content
        assert 'Authentication and Authorization' in content
        assert 'Data Protection' in content
        assert 'Session Management' in content
        assert 'Cross-Site Scripting (XSS) Prevention' in content
        assert 'Cross-Site Request Forgery (CSRF) Protection' in content
        assert 'Security Headers' in content
        assert 'API Security' in content
        assert 'Error Handling and Logging' in content
        assert 'Secret Management' in content
        
        # Check specific items
        assert 'Passwords are hashed with bcrypt/scrypt/Argon2' in content
        assert 'HTTPS is enforced' in content
        assert 'No hardcoded passwords or API keys' in content
        assert 'SQL queries use parameterized statements' in content
    
    def test_saa_references_security_docs(self, test_config_with_saa):
        """Test that SAA references security documentation."""
        setup_core = SetupCore(test_config_with_saa)
        setup_core.create_project()
        
        project_path = Path(test_config_with_saa['output_dir']) / 'SecureWebApp'
        persona_rules_path = project_path / 'agents' / 'security_audit_agent' / 'persona_rules.yaml'
        
        content = persona_rules_path.read_text()
        
        # Check knowledge sources
        assert '/docs/SECURITY.md' in content
        assert '/checklists/security_audit_checklist.md' in content
        assert 'OWASP Top 10 guidelines' in content
    
    def test_saa_with_different_languages(self):
        """Test SAA works with different programming languages."""
        languages = ['python', 'javascript', 'java', 'go']
        
        for language in languages:
            config = {
                'project_name': f'Secure{language.title()}App',
                'language': language,
                'agents': 'saa',
                'llm_provider': 'openai',
                'default_model': 'gpt-4',
                'output_dir': tempfile.mkdtemp()
            }
            
            setup_core = SetupCore(config)
            setup_core.create_project()
            
            project_path = Path(config['output_dir']) / f'Secure{language.title()}App'
            saa_path = project_path / 'agents' / 'security_audit_agent'
            
            assert saa_path.exists()
            
            # Check language-specific references
            persona_content = (saa_path / 'persona_rules.yaml').read_text()
            assert f'{language}' in persona_content
    
    def test_saa_output_format(self, test_config_with_saa):
        """Test SAA output format specification."""
        setup_core = SetupCore(test_config_with_saa)
        setup_core.create_project()
        
        project_path = Path(test_config_with_saa['output_dir']) / 'SecureWebApp'
        persona_rules_path = project_path / 'agents' / 'security_audit_agent' / 'persona_rules.yaml'
        
        content = persona_rules_path.read_text()
        
        # Check output format
        assert 'Security Audit Report' in content
        assert 'Executive Summary' in content
        assert 'Severity' in content
        assert 'Location' in content
        assert 'Impact' in content
        assert 'Recommendation' in content