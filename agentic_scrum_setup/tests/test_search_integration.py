#!/usr/bin/env python3
"""
Tests for Story 304: Perplexity Search Integration
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agentic_scrum_setup.setup_core import SetupCore


class TestSearchIntegration(unittest.TestCase):
    """Test cases for Perplexity search integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_name = "TestProject"
        config = {
            'project_name': self.project_name,
            'output_dir': self.temp_dir,
            'language': 'python',
            'framework': 'fastapi',
            'agents': 'poa,sma,deva_python,qaa,saa',
            'llm_provider': 'anthropic',
            'default_model': 'claude-3-5-sonnet-20241022',
            'project_type': 'single',
            'enable_mcp': True,
            'enable_search': True
        }
        self.setup = SetupCore(config)
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_mcp_json_includes_perplexity(self):
        """Test that .mcp.json includes Perplexity search configuration."""
        # Generate the project
        self.setup.create_project()
        
        # Check if .mcp.json exists
        mcp_json_path = Path(self.temp_dir) / self.project_name / ".mcp.json"
        self.assertTrue(mcp_json_path.exists(), ".mcp.json file should exist")
        
        # Load and verify content
        with open(mcp_json_path, 'r') as f:
            mcp_config = json.load(f)
            
        # Check for Perplexity configuration
        self.assertIn('mcpServers', mcp_config)
        self.assertIn('perplexity-search', mcp_config['mcpServers'])
        
        perplexity_config = mcp_config['mcpServers']['perplexity-search']
        self.assertEqual(perplexity_config['command'], 'uvx')
        self.assertIn('perplexity-mcp', perplexity_config['args'])
        self.assertIn('env', perplexity_config)
        self.assertIn('PERPLEXITY_API_KEY', perplexity_config['env'])
        self.assertEqual(perplexity_config['env']['PERPLEXITY_API_KEY'], '${PERPLEXITY_API_KEY}')
        self.assertEqual(perplexity_config['env']['PERPLEXITY_MODEL'], 'sonar')
        
    def test_env_sample_includes_perplexity_key(self):
        """Test that .env.sample includes Perplexity API key."""
        # Generate the project
        self.setup.create_project()
        
        # Check if .env.sample exists
        env_sample_path = Path(self.temp_dir) / self.project_name / ".env.sample"
        self.assertTrue(env_sample_path.exists(), ".env.sample file should exist")
        
        # Check content
        with open(env_sample_path, 'r') as f:
            content = f.read()
            
        self.assertIn('PERPLEXITY_API_KEY', content)
        self.assertIn('your-perplexity-api-key-here', content)
        self.assertIn('https://www.perplexity.ai/settings/api', content)
        
    def test_poa_persona_has_search_patterns(self):
        """Test that POA persona includes search patterns."""
        # Generate the project
        self.setup.create_project()
        
        # Debug: Check what files were created
        agents_dir = Path(self.temp_dir) / self.project_name / "agents"
        if agents_dir.exists():
            print(f"Agents directory exists. Contents: {list(agents_dir.iterdir())}")
            poa_dir = agents_dir / "poa"
            if poa_dir.exists():
                print(f"POA directory exists. Contents: {list(poa_dir.iterdir())}")
        
        # Check POA persona file
        poa_persona_path = Path(self.temp_dir) / self.project_name / "agents" / "product_owner_agent" / "persona_rules.yaml"
        self.assertTrue(poa_persona_path.exists(), f"POA persona file should exist at {poa_persona_path}")
        
        with open(poa_persona_path, 'r') as f:
            content = f.read()
            
        # Check for search patterns
        self.assertIn('search_patterns:', content)
        self.assertIn('triggers:', content)
        self.assertIn('query_templates:', content)
        self.assertIn('result_caching:', content)
        
        # Check specific patterns
        self.assertIn('market analysis', content)
        self.assertIn('competitor features', content)
        self.assertIn('user feedback', content)
        
    def test_deva_persona_has_search_patterns(self):
        """Test that developer agents include search patterns."""
        # Generate the project
        self.setup.create_project()
        
        # Debug: Check developer agent directory
        agents_dir = Path(self.temp_dir) / self.project_name / "agents"
        dev_agent_dir = agents_dir / "developer_agent"
        if dev_agent_dir.exists():
            print(f"Developer agent directory exists. Contents: {list(dev_agent_dir.iterdir())}")
        else:
            print(f"Developer agent directory does not exist. Agents dir contents: {list(agents_dir.iterdir()) if agents_dir.exists() else 'No agents dir'}")
        
        # Check developer persona file - looking for the first python developer agent
        # The actual directory might be named differently based on the agent configuration
        possible_paths = [
            agents_dir / "developer_agent" / "persona_rules.yaml",
            agents_dir / "developer_agent" / "python_expert" / "persona_rules.yaml",
            agents_dir / "developer_agent_python" / "persona_rules.yaml",
            agents_dir / "deva_python" / "persona_rules.yaml"
        ]
        
        deva_persona_path = None
        for path in possible_paths:
            if path.exists():
                deva_persona_path = path
                break
        
        # If still not found, look for any developer agent
        if not deva_persona_path:
            for agent_dir in agents_dir.iterdir():
                if agent_dir.is_dir() and 'developer' in agent_dir.name:
                    persona_file = agent_dir / "persona_rules.yaml"
                    if persona_file.exists():
                        deva_persona_path = persona_file
                        break
        
        self.assertIsNotNone(deva_persona_path, f"Developer persona file should exist. Checked paths: {possible_paths}")
        
        with open(deva_persona_path, 'r') as f:
            content = f.read()
            
        # Check for search patterns
        self.assertIn('search_patterns:', content)
        
        # Check developer-specific patterns
        self.assertIn('latest version features', content)
        self.assertIn('best practices', content)
        self.assertIn('performance optimization', content)
        
    def test_saa_persona_has_security_search_patterns(self):
        """Test that SAA persona includes security-focused search patterns."""
        # Generate the project
        self.setup.create_project()
        
        # Check SAA persona file
        saa_persona_path = Path(self.temp_dir) / self.project_name / "agents" / "security_audit_agent" / "persona_rules.yaml"
        self.assertTrue(saa_persona_path.exists(), "SAA persona file should exist")
        
        with open(saa_persona_path, 'r') as f:
            content = f.read()
            
        # Check for security-specific search patterns
        self.assertIn('CVE', content)
        self.assertIn('OWASP', content)
        self.assertIn('zero-day', content)
        self.assertIn('security patch', content)
        self.assertIn('vulnerability', content)
        
    def test_init_sh_checks_perplexity_key(self):
        """Test that init.sh includes Perplexity API key checking."""
        # Generate the project
        self.setup.create_project()
        
        # Check init.sh
        init_sh_path = Path(self.temp_dir) / self.project_name / "init.sh"
        self.assertTrue(init_sh_path.exists(), "init.sh should exist")
        
        with open(init_sh_path, 'r') as f:
            content = f.read()
            
        # Check for API key checking function
        self.assertIn('check_api_keys', content)
        self.assertIn('PERPLEXITY_API_KEY', content)
        self.assertIn('perplexity-mcp', content)
        
    def test_search_cache_manager_script_exists(self):
        """Test that search cache manager script is available."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "search_cache_manager.py"
        self.assertTrue(script_path.exists(), "search_cache_manager.py should exist")
        
        # Check it's executable
        with open(script_path, 'r') as f:
            first_line = f.readline()
            self.assertTrue(first_line.startswith('#!/usr/bin/env python3'))
            
    def test_api_rate_limiter_script_exists(self):
        """Test that API rate limiter script is available."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "api_rate_limiter.py"
        self.assertTrue(script_path.exists(), "api_rate_limiter.py should exist")
        
        # Check it's executable
        with open(script_path, 'r') as f:
            first_line = f.readline()
            self.assertTrue(first_line.startswith('#!/usr/bin/env python3'))
            
    def test_memory_directory_structure_supports_search_cache(self):
        """Test that memory directory structure supports search caching."""
        # Generate the project
        self.setup.create_project()
        
        # Check shared memory directory exists
        shared_memory_path = Path(self.temp_dir) / self.project_name / ".agent-memory" / "shared"
        self.assertTrue(shared_memory_path.exists(), "Shared memory directory should exist")
        
        # Verify it's in .gitignore
        gitignore_path = Path(self.temp_dir) / self.project_name / ".gitignore"
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
            
        self.assertIn('.agent-memory/', gitignore_content)


if __name__ == '__main__':
    unittest.main()