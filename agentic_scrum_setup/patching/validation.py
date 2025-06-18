"""Patch validation and safety checks for AgenticScrum framework updates.

This module provides comprehensive validation to ensure patches are safe to apply
and won't break the framework or cause data loss.
"""

import os
import re
import ast
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during patch analysis."""
    severity: ValidationSeverity
    message: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of patch validation."""
    is_valid: bool
    issues: List[ValidationIssue]
    error_message: Optional[str] = None
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any error-level issues."""
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)


class PatchValidator:
    """Validates patches before application to ensure safety."""
    
    def __init__(self, framework_path: Path):
        """Initialize validator.
        
        Args:
            framework_path: Path to AgenticScrum framework
        """
        self.framework_path = framework_path
        self.critical_files = self._get_critical_files()
        self.protected_patterns = self._get_protected_patterns()
    
    def _get_critical_files(self) -> Set[Path]:
        """Get list of critical files that need extra validation."""
        critical_files = {
            self.framework_path / 'agentic_scrum_setup' / '__init__.py',
            self.framework_path / 'agentic_scrum_setup' / 'cli.py',
            self.framework_path / 'agentic_scrum_setup' / 'setup_core.py',
            self.framework_path / 'pyproject.toml',
            self.framework_path / 'setup.py',
            self.framework_path / 'init.sh'
        }
        return {f for f in critical_files if f.exists()}
    
    def _get_protected_patterns(self) -> List[str]:
        """Get regex patterns for protected content that shouldn't be modified."""
        return [
            r'__version__\s*=',  # Version definitions
            r'setup\s*\(',  # Setup function calls
            r'if\s+__name__\s*==\s*["\']__main__["\']',  # Main blocks
            r'import\s+sys',  # Critical imports
            r'sys\.path',  # Path modifications
        ]
    
    def validate_patch_safety(self, files_to_modify: List[Path]) -> ValidationResult:
        """Validate that a patch is safe to apply.
        
        Args:
            files_to_modify: List of files that will be modified
            
        Returns:
            ValidationResult with safety assessment
        """
        issues = []
        
        # Check file permissions
        issues.extend(self._check_file_permissions(files_to_modify))
        
        # Check for critical file modifications
        issues.extend(self._check_critical_files(files_to_modify))
        
        # Check disk space
        issues.extend(self._check_disk_space())
        
        # Check git status if available
        issues.extend(self._check_git_status())
        
        # Determine if patch is valid
        has_critical = any(issue.severity == ValidationSeverity.CRITICAL for issue in issues)
        has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        
        is_valid = not (has_critical or has_errors)
        error_message = None
        
        if has_critical:
            error_message = "Critical issues prevent patch application"
        elif has_errors:
            error_message = "Errors found that must be resolved before patching"
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            error_message=error_message
        )
    
    def validate_file_content(self, file_path: Path, new_content: str) -> ValidationResult:
        """Validate new file content before writing.
        
        Args:
            file_path: Path to file being modified
            new_content: New content to validate
            
        Returns:
            ValidationResult for the content
        """
        issues = []
        
        # Check for syntax errors in Python files
        if file_path.suffix == '.py':
            issues.extend(self._validate_python_syntax(file_path, new_content))
        
        # Check for protected pattern modifications
        issues.extend(self._check_protected_patterns(file_path, new_content))
        
        # Check for security issues
        issues.extend(self._check_security_issues(file_path, new_content))
        
        # Check for encoding issues
        issues.extend(self._check_encoding_issues(new_content))
        
        has_critical = any(issue.severity == ValidationSeverity.CRITICAL for issue in issues)
        has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        
        is_valid = not (has_critical or has_errors)
        error_message = None
        
        if has_critical:
            error_message = "Critical content issues found"
        elif has_errors:
            error_message = "Content errors must be resolved"
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            error_message=error_message
        )
    
    def _check_file_permissions(self, files: List[Path]) -> List[ValidationIssue]:
        """Check if files can be written to."""
        issues = []
        
        for file_path in files:
            if file_path.exists():
                if not os.access(file_path, os.W_OK):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        message=f"No write permission for file: {file_path}",
                        file_path=file_path,
                        suggestion="Check file permissions and ownership"
                    ))
            else:
                # Check parent directory permissions for new files
                parent_dir = file_path.parent
                if not parent_dir.exists():
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Parent directory does not exist: {parent_dir}",
                        file_path=file_path,
                        suggestion="Create parent directory first"
                    ))
                elif not os.access(parent_dir, os.W_OK):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        message=f"No write permission for directory: {parent_dir}",
                        file_path=file_path,
                        suggestion="Check directory permissions"
                    ))
        
        return issues
    
    def _check_critical_files(self, files: List[Path]) -> List[ValidationIssue]:
        """Check if critical files are being modified."""
        issues = []
        
        for file_path in files:
            if file_path in self.critical_files:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Modifying critical file: {file_path.name}",
                    file_path=file_path,
                    suggestion="Ensure backup is created and test thoroughly"
                ))
        
        return issues
    
    def _check_disk_space(self) -> List[ValidationIssue]:
        """Check available disk space."""
        issues = []
        
        try:
            statvfs = os.statvfs(self.framework_path)
            available_bytes = statvfs.f_frsize * statvfs.f_bavail
            available_mb = available_bytes / (1024 * 1024)
            
            if available_mb < 100:  # Less than 100MB
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Low disk space: {available_mb:.1f}MB available",
                    suggestion="Free up disk space before patching"
                ))
            elif available_mb < 500:  # Less than 500MB
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Disk space warning: {available_mb:.1f}MB available",
                    suggestion="Consider freeing up more disk space"
                ))
        except Exception:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message="Could not check disk space",
                suggestion="Manually verify sufficient disk space available"
            ))
        
        return issues
    
    def _check_git_status(self) -> List[ValidationIssue]:
        """Check git repository status."""
        issues = []
        
        git_dir = self.framework_path / '.git'
        if not git_dir.exists():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Not a git repository - rollback options limited",
                suggestion="Initialize git repository for better patch management"
            ))
            return issues
        
        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.framework_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Uncommitted changes in git repository",
                    suggestion="Commit or stash changes before patching"
                ))
            
            # Check current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.framework_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                if current_branch in ['main', 'master']:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        message=f"Patching on {current_branch} branch",
                        suggestion="Consider creating a feature branch for patches"
                    ))
        
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"Could not check git status: {e}",
                suggestion="Manually verify git repository state"
            ))
        
        return issues
    
    def _validate_python_syntax(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate Python syntax."""
        issues = []
        
        try:
            ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                message=f"Python syntax error: {e.msg}",
                file_path=file_path,
                line_number=e.lineno,
                suggestion="Fix syntax error before applying patch"
            ))
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Python parsing error: {e}",
                file_path=file_path,
                suggestion="Check file content for issues"
            ))
        
        return issues
    
    def _check_protected_patterns(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Check for modifications to protected patterns."""
        issues = []
        
        if file_path in self.critical_files:
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                for pattern in self.protected_patterns:
                    if re.search(pattern, line):
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message=f"Modifying protected pattern: {pattern}",
                            file_path=file_path,
                            line_number=line_num,
                            suggestion="Ensure this modification is intentional and safe"
                        ))
        
        return issues
    
    def _check_security_issues(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Check for potential security issues."""
        issues = []
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r'eval\s*\(', "Use of eval() function"),
            (r'exec\s*\(', "Use of exec() function"),
            (r'os\.system\s*\(', "Use of os.system()"),
            (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "Subprocess with shell=True"),
            (r'__import__\s*\(', "Dynamic import"),
            (r'open\s*\([^)]*[\'"]w[\'"]', "File write operation")
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, description in dangerous_patterns:
                if re.search(pattern, line):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Potential security issue: {description}",
                        file_path=file_path,
                        line_number=line_num,
                        suggestion="Review this code for security implications"
                    ))
        
        return issues
    
    def _check_encoding_issues(self, content: str) -> List[ValidationIssue]:
        """Check for encoding issues."""
        issues = []
        
        try:
            content.encode('utf-8')
        except UnicodeEncodeError as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Encoding error: {e}",
                suggestion="Ensure content is valid UTF-8"
            ))
        
        # Check for common encoding issues
        if '\r\n' in content:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message="Windows line endings detected",
                suggestion="Consider using Unix line endings (LF) for consistency"
            ))
        
        return issues
    
    def validate_template_file(self, template_path: Path) -> ValidationResult:
        """Validate a template file for patch operations.
        
        Args:
            template_path: Path to template file
            
        Returns:
            ValidationResult for template
        """
        issues = []
        
        if not template_path.exists():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                message=f"Template file not found: {template_path}",
                suggestion="Ensure template file exists and path is correct"
            ))
            return ValidationResult(False, issues, "Template file not found")
        
        try:
            content = template_path.read_text()
            
            # Check for Jinja2 template syntax if it's a .j2 file
            if template_path.suffix == '.j2':
                issues.extend(self._validate_jinja2_template(template_path, content))
            
            # Check for YAML syntax if it's a YAML file
            if template_path.suffix in ['.yaml', '.yml']:
                issues.extend(self._validate_yaml_syntax(template_path, content))
            
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Could not read template file: {e}",
                file_path=template_path,
                suggestion="Check file permissions and content"
            ))
        
        has_critical = any(issue.severity == ValidationSeverity.CRITICAL for issue in issues)
        has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        
        return ValidationResult(
            is_valid=not (has_critical or has_errors),
            issues=issues,
            error_message="Template validation failed" if (has_critical or has_errors) else None
        )
    
    def _validate_jinja2_template(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate Jinja2 template syntax."""
        issues = []
        
        try:
            from jinja2 import Environment, meta
            env = Environment()
            ast = env.parse(content)
            # Template parsed successfully
        except ImportError:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Jinja2 not available for template validation",
                file_path=file_path,
                suggestion="Install Jinja2 for proper template validation"
            ))
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Jinja2 template syntax error: {e}",
                file_path=file_path,
                suggestion="Fix template syntax errors"
            ))
        
        return issues
    
    def _validate_yaml_syntax(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate YAML syntax."""
        issues = []
        
        try:
            import yaml
            yaml.safe_load(content)
        except ImportError:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="PyYAML not available for YAML validation",
                file_path=file_path,
                suggestion="Install PyYAML for proper YAML validation"
            ))
        except yaml.YAMLError as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"YAML syntax error: {e}",
                file_path=file_path,
                suggestion="Fix YAML syntax errors"
            ))
        
        return issues