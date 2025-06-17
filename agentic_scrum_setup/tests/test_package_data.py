"""Test package data configuration to ensure all template files are included."""

import os
from pathlib import Path
from setuptools import find_packages
import unittest


class TestPackageData(unittest.TestCase):
    """Test that package_data configuration includes all necessary template files."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        self.templates_dir = Path(__file__).parent.parent / 'templates'
        
        # Package data patterns from setup.py
        self.package_data_patterns = [
            "templates/**/*.j2",
            "templates/**/.*.j2",
            "templates/**/*.sample", 
            "templates/**/*.sh",
            "templates/**/*.py",
            "templates/**/*.md",
            "templates/**/*.txt",
            "templates/**/*.json",
        ]
    
    def test_all_template_files_covered_by_package_data(self):
        """Test that all template files would be included by package_data patterns."""
        # Find all template files
        all_template_files = []
        for file in self.templates_dir.rglob('*'):
            if file.is_file() and '__pycache__' not in str(file):
                rel_path = file.relative_to(self.templates_dir.parent)
                all_template_files.append(str(rel_path))
        
        # Simulate what package_data would include
        included_files = set()
        for pattern in self.package_data_patterns:
            # Convert pattern to pathlib glob pattern
            if pattern.startswith('templates/'):
                pattern = pattern[10:]  # Remove 'templates/' prefix
            
            for file in self.templates_dir.glob(pattern):
                if file.is_file():
                    rel_path = file.relative_to(self.templates_dir.parent)
                    included_files.add(str(rel_path))
        
        # Find files that would not be included
        missing_files = [f for f in all_template_files if f not in included_files]
        
        # Assert all files are covered
        self.assertEqual(
            len(missing_files), 0,
            f"Template files not covered by package_data patterns: {missing_files}"
        )
        
        # Verify minimum expected files are present
        self.assertGreater(len(included_files), 50, 
                          "Expected at least 50 template files to be included")
        
        print(f"✅ All {len(all_template_files)} template files covered by package_data")
    
    def test_critical_runtime_files_included(self):
        """Test that specific files used at runtime are included."""
        critical_files = [
            'templates/.env.sample',
            'templates/claude/.mcp-secrets.json.sample', 
            'templates/scripts/check-secrets.sh',
            'templates/mcp_servers/datetime/server.py',
            'templates/mcp_servers/datetime/__init__.py',
            'templates/mcp_servers/datetime/datetime_tools.py',
            'templates/mcp_servers/datetime/requirements.txt',
            'templates/mcp_servers/datetime/README.md'
        ]
        
        # Check each critical file exists and would be included
        for critical_file in critical_files:
            file_path = self.templates_dir.parent / critical_file
            self.assertTrue(
                file_path.exists(),
                f"Critical template file does not exist: {critical_file}"
            )
            
            # Check if it matches any package_data pattern
            matched = False
            for pattern in self.package_data_patterns:
                test_pattern = pattern
                if pattern.startswith('templates/'):
                    test_pattern = pattern[10:]  # Remove 'templates/' prefix
                
                if file_path.match(test_pattern):
                    matched = True
                    break
            
            self.assertTrue(
                matched,
                f"Critical runtime file {critical_file} not covered by package_data patterns"
            )
        
        print(f"✅ All {len(critical_files)} critical runtime files are covered")
    
    def test_package_data_patterns_syntax(self):
        """Test that package_data patterns use correct glob syntax."""
        for pattern in self.package_data_patterns:
            # Should start with templates/
            self.assertTrue(
                pattern.startswith('templates/'),
                f"Package data pattern should start with 'templates/': {pattern}"
            )
            
            # Should use /** for recursive matching
            if '/' in pattern[10:]:  # After 'templates/'
                self.assertIn('**', pattern,
                             f"Recursive pattern should use **: {pattern}")


if __name__ == '__main__':
    unittest.main()