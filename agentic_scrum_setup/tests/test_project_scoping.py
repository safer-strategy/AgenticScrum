"""Tests for project scoping questionnaire and kickoff guide generation."""

import pytest
from pathlib import Path
from agentic_scrum_setup.setup_core import SetupCore


class TestProjectScopingGeneration:
    """Test the generation of PROJECT_SCOPE.md and PROJECT_KICKOFF.md files."""
    
    def test_project_scope_generates_with_correct_name(self, tmp_path):
        """Test that PROJECT_SCOPE.md generates with correct project name."""
        config = {
            'project_name': "TestProject",
            'output_dir': str(tmp_path),
            'language': "python",
            'agents': "poa,sma,deva_python,qaa",
            'llm_provider': "openai",
            'default_model': "gpt-4"
        }
        setup = SetupCore(config)
        
        setup.create_project()
        
        scope_file = tmp_path / "TestProject" / "docs" / "PROJECT_SCOPE.md"
        assert scope_file.exists()
        
        content = scope_file.read_text()
        assert "Project Scope Questionnaire for TestProject" in content
        assert "## 1. Project Vision & Goals" in content
        assert "## 2. Core Features & Functionality" in content
        assert "## 7. Quality & Compliance" in content
        
    def test_project_kickoff_includes_conditional_content(self, tmp_path):
        """Test that PROJECT_KICKOFF.md includes conditional content based on features."""
        # Test with MCP enabled
        config = {
            'project_name': "MCPProject",
            'output_dir': str(tmp_path),
            'language': "python",
            'agents': "poa,sma,deva_python,qaa",
            'llm_provider': "anthropic",
            'default_model': "claude-3-opus",
            'enable_mcp': True,
            'enable_search': True
        }
        setup = SetupCore(config)
        
        setup.create_project()
        
        kickoff_file = tmp_path / "MCPProject" / "docs" / "PROJECT_KICKOFF.md"
        assert kickoff_file.exists()
        
        content = kickoff_file.read_text()
        assert "Project Kickoff Guide for MCPProject" in content
        assert "With MCP Features:" in content
        assert "Claude will automatically access agent memories" in content
        assert "Search capabilities enabled for research" in content
        
    def test_files_created_in_correct_location(self, tmp_path):
        """Test that files are created in the docs/ directory."""
        config = {
            'project_name': "DocsTest",
            'output_dir': str(tmp_path),
            'language': "javascript",
            'agents': "poa,deva_javascript",
            'llm_provider': "openai",
            'default_model': "gpt-4"
        }
        setup = SetupCore(config)
        
        setup.create_project()
        
        docs_dir = tmp_path / "DocsTest" / "docs"
        assert docs_dir.exists()
        assert (docs_dir / "PROJECT_SCOPE.md").exists()
        assert (docs_dir / "PROJECT_KICKOFF.md").exists()
        assert (docs_dir / "SECURITY.md").exists()
        
    def test_template_variables_properly_substituted(self, tmp_path):
        """Test that template variables are properly substituted."""
        config = {
            'project_name': "VariableTest",
            'output_dir': str(tmp_path),
            'language': "typescript",
            'agents': "poa,sma,deva_typescript,qaa,saa",
            'llm_provider': "anthropic",
            'default_model': "claude-3-sonnet"
        }
        setup = SetupCore(config)
        
        setup.create_project()
        
        kickoff_file = tmp_path / "VariableTest" / "docs" / "PROJECT_KICKOFF.md"
        content = kickoff_file.read_text()
        
        # Check agent descriptions are included
        assert "ProductOwnerAgent (POA)" in content
        assert "ScrumMasterAgent (SMA)" in content
        assert "TypeScriptDeveloperAgent" in content
        assert "QAAgent (QAA)" in content
        assert "SecurityAuditAgent (SAA)" in content
        
        # Check no unrendered variables
        assert "{{" not in content
        assert "}}" not in content
        
    def test_works_with_fullstack_project(self, tmp_path):
        """Test that scoping documents work with fullstack projects."""
        config = {
            'project_name': "FullstackTest",
            'output_dir': str(tmp_path),
            'project_type': "fullstack",
            'language': "python",
            'backend_framework': "fastapi",
            'frontend_language': "typescript",
            'frontend_framework': "react",
            'agents': "poa,deva_python,deva_typescript,qaa",
            'llm_provider': "openai",
            'default_model': "gpt-4"
        }
        setup = SetupCore(config)
        
        setup.create_project()
        
        scope_file = tmp_path / "FullstackTest" / "docs" / "PROJECT_SCOPE.md"
        assert scope_file.exists()
        
        content = scope_file.read_text()
        # Should still have the basic structure
        assert "Project Scope Questionnaire for FullstackTest" in content
        
    def test_readme_includes_starting_development_section(self, tmp_path):
        """Test that README.md includes the new Starting Development section."""
        config = {
            'project_name': "ReadmeTest",
            'output_dir': str(tmp_path),
            'language': "python",
            'agents': "poa,deva_python",
            'llm_provider': "openai",
            'default_model': "gpt-4"
        }
        setup = SetupCore(config)
        
        setup.create_project()
        
        readme_file = tmp_path / "ReadmeTest" / "README.md"
        content = readme_file.read_text()
        
        assert "## 🚀 Starting Development" in content
        assert "Complete the questionnaire in `docs/PROJECT_SCOPE.md`" in content
        assert "Use `docs/PROJECT_KICKOFF.md` for step-by-step instructions" in content
        assert "The more detail you provide in PROJECT_SCOPE.md" in content
        
    def test_claude_md_includes_scope_instructions(self, tmp_path):
        """Test that CLAUDE.md includes instructions to check PROJECT_SCOPE.md."""
        config = {
            'project_name': "ClaudeTest",
            'output_dir': str(tmp_path),
            'language': "python",
            'agents': "poa,deva_claude_python",
            'llm_provider': "anthropic",
            'default_model': "claude-3-opus"
        }
        setup = SetupCore(config)
        
        setup.create_project()
        
        claude_file = tmp_path / "ClaudeTest" / "CLAUDE.md"
        content = claude_file.read_text()
        
        assert "**ALWAYS check `docs/PROJECT_SCOPE.md` first**" in content
        assert "If PROJECT_SCOPE.md is incomplete, help the user fill it out" in content
        assert "Use the scoping document to create initial user stories" in content
        
    def test_poa_agent_includes_scope_in_knowledge(self, tmp_path):
        """Test that POA agent includes PROJECT_SCOPE.md in knowledge sources."""
        config = {
            'project_name': "POATest",
            'output_dir': str(tmp_path),
            'language': "python",
            'agents': "poa",
            'llm_provider': "openai",
            'default_model': "gpt-4"
        }
        setup = SetupCore(config)
        
        setup.create_project()
        
        poa_file = tmp_path / "POATest" / "agents" / "product_owner_agent" / "persona_rules.yaml"
        content = poa_file.read_text()
        
        assert "/docs/PROJECT_SCOPE.md" in content
        assert content.index("/docs/PROJECT_SCOPE.md") < content.index("/docs/requirements/product_backlog.md")