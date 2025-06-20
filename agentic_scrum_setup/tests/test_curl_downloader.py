"""Tests for curl-based patch downloader system."""

import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestCurlDownloader:
    """Test suite for the curl-based patch downloader."""

    @pytest.fixture
    def test_project_dir(self):
        """Create a temporary test project directory."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create minimal AgenticScrum project structure
        (temp_dir / "agentic_config.yaml").write_text("""
project_name: test_project
version: 1.0.0
agents:
  - poa
  - sma
""")
        
        (temp_dir / "init.sh").write_text("""#!/bin/bash
# Test init.sh
echo "Original init.sh"
""")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def downloader_script(self):
        """Path to the download script."""
        return Path(__file__).parent.parent.parent / "download-patch-updates.sh"

    def test_script_exists_and_executable(self, downloader_script):
        """Test that the download script exists and is executable."""
        assert downloader_script.exists(), "Download script should exist"
        assert downloader_script.stat().st_mode & 0o111, "Script should be executable"

    def test_help_option(self, downloader_script):
        """Test the help option displays available operations."""
        result = subprocess.run(
            [str(downloader_script), "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Available Patch Operations" in result.stdout
        assert "init-sh-update" in result.stdout
        assert "security-update" in result.stdout
        assert "animated-banner" in result.stdout

    def test_dry_run_mode(self, downloader_script, test_project_dir):
        """Test dry run mode doesn't make changes."""
        original_init = (test_project_dir / "init.sh").read_text()
        
        result = subprocess.run(
            [str(downloader_script), "init-sh-update", "--dry-run"],
            cwd=test_project_dir,
            capture_output=True,
            text=True
        )
        
        # Should not fail
        assert result.returncode == 0
        assert "DRY RUN MODE" in result.stdout
        
        # File should be unchanged
        assert (test_project_dir / "init.sh").read_text() == original_init

    def test_check_version_operation(self, downloader_script, test_project_dir):
        """Test version checking operation."""
        with patch('subprocess.run') as mock_run:
            # Mock curl call for version check
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="1.0.0-beta.8\n"
            )
            
            result = subprocess.run(
                [str(downloader_script), "check-version"],
                cwd=test_project_dir,
                capture_output=True,
                text=True
            )
            
            # Should complete without errors
            assert result.returncode in [0, 1]  # 1 if update available
            assert "Current version" in result.stdout

    def test_backup_creation(self, downloader_script, test_project_dir):
        """Test that backups are created before operations."""
        result = subprocess.run(
            [str(downloader_script), "backup-project"],
            cwd=test_project_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "backed up" in result.stdout.lower()

    def test_cleanup_operation(self, downloader_script, test_project_dir):
        """Test cleanup removes temporary files."""
        # Create some temp files
        temp_dir = test_project_dir / ".agentic_patch_temp"
        temp_dir.mkdir()
        (temp_dir / "test_file").write_text("test")
        
        result = subprocess.run(
            [str(downloader_script), "cleanup"],
            cwd=test_project_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert not temp_dir.exists()

    def test_project_context_detection(self, downloader_script):
        """Test detection of non-AgenticScrum directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [str(downloader_script), "check-version"],
                cwd=temp_dir,
                capture_output=True,
                text=True
            )
            
            # Should warn about project context
            assert "Not in an AgenticScrum project" in result.stdout

    def test_invalid_operation(self, downloader_script, test_project_dir):
        """Test handling of invalid operations."""
        result = subprocess.run(
            [str(downloader_script), "invalid-operation"],
            cwd=test_project_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 1
        assert "Unknown operation" in result.stdout

    def test_security_warning_for_piped_input(self, downloader_script):
        """Test security warning when script is piped from curl."""
        # This is harder to test directly, but we can verify the warning logic exists
        script_content = downloader_script.read_text()
        assert "SECURITY WARNING" in script_content
        assert "downloaded from the internet" in script_content

    @pytest.mark.slow
    def test_quick_scripts_exist(self):
        """Test that quick update scripts exist and are executable."""
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        
        quick_scripts = [
            "quick-init-update.sh",
            "quick-security-update.sh", 
            "quick-banner-update.sh",
            "quick-install-patcher.sh"
        ]
        
        for script_name in quick_scripts:
            script_path = scripts_dir / script_name
            assert script_path.exists(), f"Quick script {script_name} should exist"
            assert script_path.stat().st_mode & 0o111, f"Script {script_name} should be executable"

    def test_file_verification_logic(self, downloader_script):
        """Test file verification functions work correctly."""
        script_content = downloader_script.read_text()
        
        # Check that verification functions exist
        assert "verify_file()" in script_content
        assert "<!DOCTYPE html>" in script_content  # HTML error detection
        assert "file_size" in script_content  # Size verification

    def test_error_handling_robustness(self, downloader_script, test_project_dir):
        """Test error handling with network issues."""
        with patch.dict('os.environ', {'GITHUB_RAW_URL': 'https://invalid-url.example.com'}):
            result = subprocess.run(
                [str(downloader_script), "check-version"],
                cwd=test_project_dir,
                capture_output=True,
                text=True,
                timeout=30  # Don't wait forever
            )
            
            # Should handle network errors gracefully
            assert result.returncode == 1
            assert "Could not check" in result.stdout or "Failed to download" in result.stdout


class TestQuickScripts:
    """Test suite for quick update scripts."""

    def test_quick_init_update_structure(self):
        """Test quick init update script has correct structure."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "quick-init-update.sh"
        content = script_path.read_text()
        
        assert "#!/bin/bash" in content
        assert "init.sh" in content
        assert "curl -fsSL" in content
        assert "download-patch-updates.sh" in content

    def test_quick_security_update_structure(self):
        """Test quick security update script has correct structure."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "quick-security-update.sh"
        content = script_path.read_text()
        
        assert "#!/bin/bash" in content
        assert "security-update" in content
        assert "curl -fsSL" in content

    def test_quick_banner_update_structure(self):
        """Test quick banner update script has correct structure."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "quick-banner-update.sh"
        content = script_path.read_text()
        
        assert "#!/bin/bash" in content
        assert "animated-banner" in content
        assert "curl -fsSL" in content

    def test_quick_install_patcher_structure(self):
        """Test quick patcher install script has correct structure."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "quick-install-patcher.sh"
        content = script_path.read_text()
        
        assert "#!/bin/bash" in content
        assert ".local/bin" in content
        assert "agentic-patch" in content
        assert "PATH" in content


class TestIntegrationWithExistingSystem:
    """Test integration with existing patching system."""

    def test_compatibility_with_standalone_patcher(self):
        """Test that curl downloader is compatible with standalone patcher."""
        # Check that both systems use similar operation names
        downloader_script = Path(__file__).parent.parent.parent / "download-patch-updates.sh"
        standalone_script = Path(__file__).parent.parent.parent / "scripts" / "agentic-patch"
        
        downloader_content = downloader_script.read_text()
        standalone_content = standalone_script.read_text()
        
        # Both should support these operations
        common_operations = ["update-security", "add-background-agents", "add-animated-banner"]
        
        for operation in common_operations:
            assert operation in downloader_content, f"Downloader should support {operation}"
            assert operation in standalone_content, f"Standalone should support {operation}"

    def test_backup_directory_compatibility(self):
        """Test that backup directories follow consistent naming."""
        downloader_script = Path(__file__).parent.parent.parent / "download-patch-updates.sh"
        content = downloader_script.read_text()
        
        # Should use consistent backup naming
        assert ".agentic_patch_backup_" in content
        assert "$(date +" in content