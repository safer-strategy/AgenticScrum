"""Core patching logic for AgenticScrum framework updates.

This module provides the main AgenticPatcher class that handles patch application,
rollback, and coordination of all patching operations.
"""

import os
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import git
import json

from .discovery import find_agentic_scrum_location, get_framework_info, verify_patch_compatibility
from .validation import PatchValidator, ValidationResult


class PatchError(Exception):
    """Base exception for patching operations."""
    pass


class PatchValidationError(PatchError):
    """Raised when patch validation fails."""
    pass


class GitOperationError(PatchError):
    """Raised when git operations fail."""
    pass


class PatchApplication:
    """Represents a single patch application with metadata."""
    
    def __init__(self, patch_id: str, operation: str, description: str, 
                 timestamp: datetime, files_modified: List[str]):
        self.patch_id = patch_id
        self.operation = operation
        self.description = description
        self.timestamp = timestamp
        self.files_modified = files_modified
        self.git_commit = None
        self.backup_path = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'patch_id': self.patch_id,
            'operation': self.operation,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'files_modified': self.files_modified,
            'git_commit': self.git_commit,
            'backup_path': str(self.backup_path) if self.backup_path else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatchApplication':
        """Create from dictionary."""
        patch = cls(
            patch_id=data['patch_id'],
            operation=data['operation'],
            description=data['description'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            files_modified=data['files_modified']
        )
        patch.git_commit = data.get('git_commit')
        patch.backup_path = Path(data['backup_path']) if data.get('backup_path') else None
        return patch


class AgenticPatcher:
    """Main patching system for AgenticScrum framework updates."""
    
    def __init__(self, framework_path: Optional[Path] = None, create_backups: bool = True):
        """Initialize the patcher.
        
        Args:
            framework_path: Path to framework (auto-discovered if None)
            create_backups: Whether to create backups before patching
        """
        if framework_path is None:
            framework_path = find_agentic_scrum_location()
        
        self.framework_path = framework_path
        self.create_backups = create_backups
        self.validator = PatchValidator(framework_path)
        
        # Initialize patch tracking
        self.patch_history_file = framework_path / '.agentic_patches.json'
        self.backup_dir = framework_path / '.patch_backups'
        self.backup_dir.mkdir(exist_ok=True)
        
        # Initialize git repository if available
        self.git_repo = None
        if (framework_path / '.git').exists():
            try:
                self.git_repo = git.Repo(framework_path)
            except git.InvalidGitRepositoryError:
                pass
        
        # Verify compatibility
        is_compatible, issues = verify_patch_compatibility(framework_path)
        if not is_compatible:
            raise PatchError(f"Framework not compatible with patching: {'; '.join(issues)}")
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Get information about the current framework installation."""
        return get_framework_info(self.framework_path)
    
    def create_backup(self, files_to_backup: List[Path]) -> Path:
        """Create backup of files before patching.
        
        Args:
            files_to_backup: List of file paths to backup
            
        Returns:
            Path to backup directory
        """
        if not self.create_backups:
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        patch_id = str(uuid.uuid4())[:8]
        backup_path = self.backup_dir / f'backup_{timestamp}_{patch_id}'
        backup_path.mkdir(exist_ok=True)
        
        for file_path in files_to_backup:
            if file_path.exists():
                # Preserve directory structure in backup
                relative_path = file_path.relative_to(self.framework_path)
                backup_file_path = backup_path / relative_path
                backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_file_path)
        
        return backup_path
    
    def restore_backup(self, backup_path: Path) -> None:
        """Restore files from backup.
        
        Args:
            backup_path: Path to backup directory
        """
        if not backup_path or not backup_path.exists():
            raise PatchError(f"Backup path not found: {backup_path}")
        
        for backup_file in backup_path.rglob('*'):
            if backup_file.is_file():
                relative_path = backup_file.relative_to(backup_path)
                target_path = self.framework_path / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target_path)
    
    def create_git_branch(self, branch_name: str) -> str:
        """Create a new git branch for patching.
        
        Args:
            branch_name: Name for the new branch
            
        Returns:
            Name of created branch
        """
        if not self.git_repo:
            return None
        
        try:
            # Ensure we're on a clean state
            if self.git_repo.is_dirty():
                raise GitOperationError("Git repository has uncommitted changes")
            
            # Create and checkout new branch
            new_branch = self.git_repo.create_head(branch_name)
            new_branch.checkout()
            
            return branch_name
        except Exception as e:
            raise GitOperationError(f"Failed to create git branch: {e}")
    
    def commit_changes(self, message: str, files: List[Path]) -> str:
        """Commit changes to git repository.
        
        Args:
            message: Commit message
            files: List of files to commit
            
        Returns:
            Commit hash
        """
        if not self.git_repo:
            return None
        
        try:
            # Add files to staging
            for file_path in files:
                if file_path.exists():
                    relative_path = file_path.relative_to(self.framework_path)
                    self.git_repo.index.add([str(relative_path)])
            
            # Commit changes
            commit = self.git_repo.index.commit(message)
            return commit.hexsha
        except Exception as e:
            raise GitOperationError(f"Failed to commit changes: {e}")
    
    def load_patch_history(self) -> List[PatchApplication]:
        """Load patch history from file."""
        if not self.patch_history_file.exists():
            return []
        
        try:
            with open(self.patch_history_file, 'r') as f:
                data = json.load(f)
                return [PatchApplication.from_dict(item) for item in data]
        except Exception:
            return []
    
    def save_patch_history(self, patches: List[PatchApplication]) -> None:
        """Save patch history to file."""
        try:
            data = [patch.to_dict() for patch in patches]
            with open(self.patch_history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise PatchError(f"Failed to save patch history: {e}")
    
    def apply_patch(self, operation: str, description: str, 
                   patch_function: callable, files_to_modify: List[Path],
                   dry_run: bool = False) -> PatchApplication:
        """Apply a patch with full safety and tracking.
        
        Args:
            operation: Name of the patch operation
            description: Description of what the patch does
            patch_function: Function that applies the actual patch
            files_to_modify: List of files that will be modified
            dry_run: If True, validate but don't apply the patch
            
        Returns:
            PatchApplication object
        """
        # Generate patch ID
        patch_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()
        
        # Validate patch
        validation_result = self.validator.validate_patch_safety(files_to_modify)
        if not validation_result.is_valid:
            raise PatchValidationError(f"Patch validation failed: {validation_result.error_message}")
        
        if dry_run:
            print(f"DRY RUN: Would apply patch '{operation}' affecting {len(files_to_modify)} files")
            for file_path in files_to_modify:
                print(f"  - {file_path.relative_to(self.framework_path)}")
            return None
        
        # Create backup
        backup_path = self.create_backup(files_to_modify)
        
        # Create git branch if possible
        branch_name = None
        if self.git_repo:
            branch_name = f"patch-{operation.lower().replace('_', '-')}-{patch_id}"
            try:
                self.create_git_branch(branch_name)
            except GitOperationError as e:
                print(f"Warning: Could not create git branch: {e}")
        
        patch_app = PatchApplication(
            patch_id=patch_id,
            operation=operation,
            description=description,
            timestamp=timestamp,
            files_modified=[str(f.relative_to(self.framework_path)) for f in files_to_modify]
        )
        patch_app.backup_path = backup_path
        
        try:
            # Apply the actual patch
            result = patch_function()
            
            # Commit to git if available
            if self.git_repo:
                commit_message = f"feat: {description}\n\nPatch ID: {patch_id}\nOperation: {operation}\n\n🤖 Applied via AgenticScrum Remote Patching System"
                commit_hash = self.commit_changes(commit_message, files_to_modify)
                patch_app.git_commit = commit_hash
            
            # Update patch history
            patches = self.load_patch_history()
            patches.append(patch_app)
            self.save_patch_history(patches)
            
            print(f"✅ Patch '{operation}' applied successfully (ID: {patch_id})")
            if commit_hash:
                print(f"📝 Git commit: {commit_hash[:8]}")
            
            return patch_app
            
        except Exception as e:
            # Rollback on failure
            print(f"❌ Patch application failed: {e}")
            if backup_path:
                print("🔄 Restoring from backup...")
                self.restore_backup(backup_path)
            
            # Reset git branch if created
            if self.git_repo and branch_name:
                try:
                    self.git_repo.heads.main.checkout()  # or master
                    self.git_repo.delete_head(branch_name, force=True)
                except Exception:
                    pass
            
            raise PatchError(f"Patch application failed: {e}")
    
    def rollback_patch(self, patch_id: str) -> bool:
        """Rollback a specific patch.
        
        Args:
            patch_id: ID of patch to rollback
            
        Returns:
            True if rollback successful
        """
        patches = self.load_patch_history()
        patch_to_rollback = None
        
        for patch in patches:
            if patch.patch_id == patch_id:
                patch_to_rollback = patch
                break
        
        if not patch_to_rollback:
            raise PatchError(f"Patch {patch_id} not found in history")
        
        try:
            # Restore from backup if available
            if patch_to_rollback.backup_path and patch_to_rollback.backup_path.exists():
                print(f"🔄 Restoring files from backup...")
                self.restore_backup(patch_to_rollback.backup_path)
            
            # Revert git commit if available
            elif self.git_repo and patch_to_rollback.git_commit:
                print(f"🔄 Reverting git commit {patch_to_rollback.git_commit[:8]}...")
                commit = self.git_repo.commit(patch_to_rollback.git_commit)
                self.git_repo.git.revert(commit.hexsha, no_edit=True)
            
            else:
                raise PatchError("No backup or git commit available for rollback")
            
            # Remove from patch history
            patches = [p for p in patches if p.patch_id != patch_id]
            self.save_patch_history(patches)
            
            print(f"✅ Patch {patch_id} rolled back successfully")
            return True
            
        except Exception as e:
            raise PatchError(f"Rollback failed: {e}")
    
    def get_patch_history(self) -> List[PatchApplication]:
        """Get list of applied patches."""
        return self.load_patch_history()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current patching system status."""
        patches = self.load_patch_history()
        framework_info = self.get_framework_info()
        
        return {
            'framework_path': str(self.framework_path),
            'framework_info': framework_info,
            'total_patches': len(patches),
            'recent_patches': [p.to_dict() for p in patches[-5:]],  # Last 5 patches
            'git_available': self.git_repo is not None,
            'backup_enabled': self.create_backups,
            'backup_directory': str(self.backup_dir)
        }