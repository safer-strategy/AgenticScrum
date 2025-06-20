"""Test the standalone agentic-patch script functionality."""

import subprocess
import sys
import os
from pathlib import Path
import tempfile
import shutil

import pytest


class TestStandalonePatchScript:
    """Test the standalone patch script operations."""
    
    @pytest.fixture
    def script_path(self):
        """Get the path to the standalone script."""
        # Find the script relative to this test file
        test_dir = Path(__file__).parent
        framework_dir = test_dir.parent.parent
        script = framework_dir / "scripts" / "agentic-patch"
        assert script.exists(), f"Script not found at {script}"
        return script
    
    @pytest.fixture
    def framework_path(self):
        """Get the framework path."""
        test_dir = Path(__file__).parent
        return test_dir.parent.parent
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "test-project"
            project_dir.mkdir()
            
            # Create minimal project structure
            (project_dir / "agentic_config.yaml").write_text("""
project_name: TestProject
agents:
  - poa
  - sma
""")
            yield project_dir
    
    def run_patch_command(self, script_path, framework_path, args, cwd=None):
        """Run the patch script with given arguments."""
        cmd = [sys.executable, str(script_path), "--framework-path", str(framework_path)] + args
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None
        )
        
        return result
    
    def test_help_shows_all_operations(self, script_path, framework_path):
        """Test that help output shows all new operations."""
        result = self.run_patch_command(script_path, framework_path, ["--help"])
        
        # Check for new operations in help text
        assert "update-all" in result.stdout
        assert "add-background-agents" in result.stdout
        assert "update-security" in result.stdout
        
        # Check operations are present in examples
        assert "agentic-patch update-all" in result.stdout
        assert "agentic-patch add-background-agents" in result.stdout
        assert "agentic-patch update-security" in result.stdout
    
    def test_status_command_works(self, script_path, framework_path):
        """Test that status command executes successfully."""
        result = self.run_patch_command(script_path, framework_path, ["status"])
        
        assert result.returncode == 0
        assert "AgenticScrum Remote Patching System" in result.stdout
        assert "Status Report" in result.stdout
    
    def test_update_all_dry_run(self, script_path, framework_path, temp_project):
        """Test update-all operation in dry run mode."""
        result = self.run_patch_command(
            script_path, 
            framework_path, 
            ["update-all", "--dry-run"],
            cwd=temp_project
        )
        
        assert result.returncode == 0
        assert "DRY RUN: Comprehensive project update" in result.stdout
        assert "Update init.sh with latest framework integration" in result.stdout
        assert "Update MCP configurations if outdated" in result.stdout
        assert "No changes applied in dry run mode" in result.stdout
    
    def test_add_background_agents_dry_run(self, script_path, framework_path, temp_project):
        """Test add-background-agents operation in dry run mode."""
        result = self.run_patch_command(
            script_path,
            framework_path,
            ["add-background-agents", "--dry-run"],
            cwd=temp_project
        )
        
        assert result.returncode == 0
        assert "DRY RUN: Add background agent system" in result.stdout
        assert "Create background agent directories" in result.stdout
        assert "Add background agent runner script" in result.stdout
        assert "No changes applied in dry run mode" in result.stdout
    
    def test_update_security_dry_run(self, script_path, framework_path, temp_project):
        """Test update-security operation in dry run mode."""
        result = self.run_patch_command(
            script_path,
            framework_path,
            ["update-security", "--dry-run"],
            cwd=temp_project
        )
        
        assert result.returncode == 0
        assert "DRY RUN: Security training update" in result.stdout
        assert "Add security training documentation" in result.stdout
        assert "No changes applied in dry run mode" in result.stdout
    
    def test_operation_from_different_directory(self, script_path, framework_path):
        """Test that operations work from arbitrary directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory structure simulating a different location
            work_dir = Path(tmpdir) / "some" / "random" / "location"
            work_dir.mkdir(parents=True)
            
            # Test status from this random location
            result = self.run_patch_command(
                script_path,
                framework_path,
                ["status"],
                cwd=work_dir
            )
            
            assert result.returncode == 0
            assert str(work_dir) in result.stdout  # Should show working directory
    
    def test_invalid_operation_shows_help(self, script_path, framework_path):
        """Test that invalid operation shows helpful error."""
        result = self.run_patch_command(
            script_path,
            framework_path,
            ["invalid-operation"]
        )
        
        assert result.returncode != 0
        assert "invalid choice" in result.stderr
    
    def test_operation_without_framework_path(self, script_path):
        """Test operations discover framework automatically when run from framework dir."""
        # This test only works if we're in the framework directory
        framework_dir = script_path.parent.parent
        
        cmd = [sys.executable, str(script_path), "status"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(framework_dir)
        )
        
        # Should either work (if not installed) or show version mismatch warning
        assert result.returncode == 0 or "not available in this installation" in result.stdout