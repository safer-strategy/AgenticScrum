"""Fix CLI operation for AgenticScrum patching system.

This module handles applying CLI bug fixes and enhancements to the framework.
"""

import re
import ast
import difflib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from ..validation import PatchValidator


class FixCLIOperation:
    """Handles applying CLI fixes and enhancements."""
    
    def __init__(self, framework_path: Path, validator: PatchValidator):
        """Initialize the operation.
        
        Args:
            framework_path: Path to AgenticScrum framework
            validator: Patch validator instance
        """
        self.framework_path = framework_path
        self.validator = validator
        self.cli_file = framework_path / 'agentic_scrum_setup' / 'cli.py'
        self.init_script = framework_path / 'init.sh'
    
    def apply_cli_patch(self, patch_file: Path) -> List[Path]:
        """Apply a CLI patch from a patch file.
        
        Args:
            patch_file: Path to patch file (unified diff format)
            
        Returns:
            List of files that were modified
        """
        if not patch_file.exists():
            raise ValueError(f"Patch file not found: {patch_file}")
        
        patch_content = patch_file.read_text()
        
        # Parse the patch to identify target files and changes
        patches = self._parse_unified_diff(patch_content)
        modified_files = []
        
        for file_path, hunks in patches.items():
            target_file = self.framework_path / file_path
            
            if not target_file.exists():
                raise ValueError(f"Target file not found: {target_file}")
            
            # Apply the patch to this file
            if self._apply_file_patch(target_file, hunks):
                modified_files.append(target_file)
        
        return modified_files
    
    def fix_argument_parsing(self, fix_description: str) -> List[Path]:
        """Fix common argument parsing issues in the CLI.
        
        Args:
            fix_description: Description of the fix being applied
            
        Returns:
            List of files that were modified
        """
        modified_files = []
        
        if not self.cli_file.exists():
            raise ValueError(f"CLI file not found: {self.cli_file}")
        
        content = self.cli_file.read_text()
        original_content = content
        
        # Fix common argument parsing issues
        fixes_applied = []
        
        # Fix 1: Add space handling for comma-separated lists
        if 'agents.split(\',\')' in content:
            content = content.replace(
                'agents.split(\',\')',
                '[agent.strip() for agent in agents.split(\',\')]'
            )
            fixes_applied.append("Added space handling for agent lists")
        
        # Fix 2: Fix missing argument validation
        if 'validate_cli_arguments' not in content:
            # Add validation call
            validation_code = '''
        # Validate CLI arguments early
        validation_errors = validate_cli_arguments(args)
        if validation_errors:
            print("❌ Configuration errors found:")
            for error in validation_errors:
                print(f"  - {error}")
            print("\\nPlease fix these issues and try again, or run without arguments for interactive mode.")
            sys.exit(1)
'''
            # Insert after args parsing
            content = content.replace(
                'args = parser.parse_args()',
                'args = parser.parse_args()' + validation_code
            )
            fixes_applied.append("Added argument validation")
        
        # Fix 3: Improve error handling
        if 'try:' not in content or 'except Exception' not in content:
            # Wrap main CLI execution in try-catch
            main_execution_pattern = r'(setup = SetupCore\(config\).*?setup\.create_project\(\))'
            
            try_catch_wrapper = '''try:
            \\1
        except ValueError as e:
            print(f"\\n❌ Configuration error: {e}")
            print("\\nTroubleshooting tips:")
            print("  - Check that your project name contains only valid characters")
            print("  - Verify that all agent types are spelled correctly")
            print("  - Ensure the output directory path is valid and accessible")
            sys.exit(1)
        except Exception as e:
            print(f"\\n❌ Unexpected error: {e}")
            print("\\nIf this problem persists, please report it at:")
            print("  https://github.com/anthropics/AgenticScrum/issues")
            sys.exit(1)'''
            
            content = re.sub(main_execution_pattern, try_catch_wrapper, content, flags=re.DOTALL)
            if content != original_content:
                fixes_applied.append("Improved error handling")
        
        # Fix 4: Add missing imports
        missing_imports = []
        if 'from pathlib import Path' not in content:
            missing_imports.append('from pathlib import Path')
        if 're' in content and 'import re' not in content:
            missing_imports.append('import re')
        
        if missing_imports:
            # Add imports after existing imports
            import_section = content.split('\n\n')[0]  # First section is usually imports
            for import_stmt in missing_imports:
                if import_stmt not in import_section:
                    import_section += f'\n{import_stmt}'
                    fixes_applied.append(f"Added missing import: {import_stmt}")
            
            content = import_section + content[len(content.split('\n\n')[0]):]
        
        # Write changes if any were made
        if content != original_content:
            # Validate the modified content
            validation_result = self.validator.validate_file_content(self.cli_file, content)
            if not validation_result.is_valid:
                raise ValueError(f"CLI fix validation failed: {validation_result.error_message}")
            
            self.cli_file.write_text(content)
            modified_files.append(self.cli_file)
            
            print(f"✅ Applied CLI fixes: {', '.join(fixes_applied)}")
        
        return modified_files
    
    def fix_init_script(self, fix_description: str) -> List[Path]:
        """Fix common issues in the init.sh script.
        
        Args:
            fix_description: Description of the fix being applied
            
        Returns:
            List of files that were modified
        """
        modified_files = []
        
        if not self.init_script.exists():
            raise ValueError(f"Init script not found: {self.init_script}")
        
        content = self.init_script.read_text()
        original_content = content
        
        fixes_applied = []
        
        # Fix 1: Add proper quoting for command arguments
        if '--agents "$agents"' not in content and '--agents $agents' in content:
            content = content.replace('--agents $agents', '--agents "$agents"')
            fixes_applied.append("Added proper quoting for agents parameter")
        
        # Fix 2: Add space removal for agent lists
        if 'tr -d \' \'' not in content and 'agents=' in content:
            # Find agent input handling and add space removal
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'read -p' in line and 'agents' in line:
                    # Add space removal after the read
                    if i + 1 < len(lines) and 'tr -d' not in lines[i + 1]:
                        lines.insert(i + 1, '    agents=$(echo "$agents" | tr -d \' \')')
                        fixes_applied.append("Added space removal for agent lists")
                        break
            content = '\n'.join(lines)
        
        # Fix 3: Add error checking for required commands
        required_commands = ['python3', 'pip', 'git']
        for cmd in required_commands:
            check_cmd = f'command -v {cmd}'
            if check_cmd not in content:
                # Add command check at the beginning of the script
                check_block = f'''
# Check if {cmd} is available
if ! command -v {cmd} &> /dev/null; then
    echo "❌ Error: {cmd} is required but not installed"
    exit 1
fi
'''
                # Insert after shebang and before main script
                lines = content.split('\n')
                insert_index = 1  # After shebang
                for line in check_block.strip().split('\n'):
                    lines.insert(insert_index, line)
                    insert_index += 1
                
                content = '\n'.join(lines)
                fixes_applied.append(f"Added {cmd} availability check")
        
        # Fix 4: Improve error messages
        if 'echo "Error:"' in content and 'echo "❌ Error:"' not in content:
            content = content.replace('echo "Error:', 'echo "❌ Error:')
            fixes_applied.append("Improved error message formatting")
        
        # Write changes if any were made
        if content != original_content:
            self.init_script.write_text(content)
            # Ensure script remains executable
            import os
            os.chmod(self.init_script, 0o755)
            modified_files.append(self.init_script)
            
            print(f"✅ Applied init script fixes: {', '.join(fixes_applied)}")
        
        return modified_files
    
    def add_new_cli_option(self, option_name: str, option_config: Dict[str, Any]) -> List[Path]:
        """Add a new CLI option to the argument parser.
        
        Args:
            option_name: Name of the new option (e.g., '--enable-feature')
            option_config: Configuration for the option (type, help, default, etc.)
            
        Returns:
            List of files that were modified
        """
        if not self.cli_file.exists():
            raise ValueError(f"CLI file not found: {self.cli_file}")
        
        content = self.cli_file.read_text()
        
        # Parse the Python AST to find the argument parser setup
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"CLI file has syntax errors: {e}")
        
        # Find where to insert the new argument
        lines = content.split('\n')
        insert_index = None
        
        # Look for existing add_argument calls in the init parser
        for i, line in enumerate(lines):
            if 'add_argument(' in line and 'init_parser' in lines[max(0, i-5):i+1]:
                insert_index = i + 1
        
        if insert_index is None:
            # Find the init_parser definition and add after it
            for i, line in enumerate(lines):
                if 'init_parser =' in line and 'add_parser' in line:
                    insert_index = i + 1
                    break
        
        if insert_index is None:
            raise ValueError("Could not find where to insert new CLI option")
        
        # Generate the add_argument call
        option_code = self._generate_argument_code(option_name, option_config)
        
        # Insert the new option
        lines.insert(insert_index, option_code)
        
        # Update the content
        updated_content = '\n'.join(lines)
        
        # Validate the updated content
        validation_result = self.validator.validate_file_content(self.cli_file, updated_content)
        if not validation_result.is_valid:
            raise ValueError(f"CLI option validation failed: {validation_result.error_message}")
        
        self.cli_file.write_text(updated_content)
        
        print(f"✅ Added new CLI option: {option_name}")
        return [self.cli_file]
    
    def _parse_unified_diff(self, patch_content: str) -> Dict[str, List[Tuple[int, List[str], List[str]]]]:
        """Parse a unified diff patch.
        
        Args:
            patch_content: Content of the patch file
            
        Returns:
            Dictionary mapping file paths to list of hunks
        """
        patches = {}
        current_file = None
        current_hunk = None
        
        for line in patch_content.split('\n'):
            if line.startswith('--- '):
                # Start of a new file patch
                continue
            elif line.startswith('+++ '):
                # Target file
                current_file = line[4:].split('\t')[0]  # Remove timestamp
                if current_file.startswith('b/'):
                    current_file = current_file[2:]  # Remove 'b/' prefix
                patches[current_file] = []
            elif line.startswith('@@'):
                # Start of a new hunk
                hunk_info = line.split(' ')
                old_start = int(hunk_info[1].split(',')[0][1:])  # Remove '-' prefix
                current_hunk = {
                    'start': old_start,
                    'old_lines': [],
                    'new_lines': []
                }
                patches[current_file].append(current_hunk)
            elif current_hunk is not None:
                if line.startswith('-'):
                    current_hunk['old_lines'].append(line[1:])
                elif line.startswith('+'):
                    current_hunk['new_lines'].append(line[1:])
                elif line.startswith(' '):
                    # Context line
                    current_hunk['old_lines'].append(line[1:])
                    current_hunk['new_lines'].append(line[1:])
        
        return patches
    
    def _apply_file_patch(self, target_file: Path, hunks: List[Dict]) -> bool:
        """Apply hunks to a specific file.
        
        Args:
            target_file: File to patch
            hunks: List of hunks to apply
            
        Returns:
            True if file was modified
        """
        if not hunks:
            return False
        
        content = target_file.read_text()
        lines = content.split('\n')
        
        # Apply hunks in reverse order to preserve line numbers
        for hunk in reversed(hunks):
            start_line = hunk['start'] - 1  # Convert to 0-based indexing
            old_lines = hunk['old_lines']
            new_lines = hunk['new_lines']
            
            # Find the exact location to apply the hunk
            for offset in range(-5, 6):  # Try with small offsets
                actual_start = start_line + offset
                if actual_start < 0 or actual_start + len(old_lines) > len(lines):
                    continue
                
                # Check if the old lines match
                match = True
                for i, old_line in enumerate(old_lines):
                    if actual_start + i >= len(lines) or lines[actual_start + i] != old_line:
                        match = False
                        break
                
                if match:
                    # Apply the hunk
                    lines[actual_start:actual_start + len(old_lines)] = new_lines
                    break
            else:
                # Could not apply hunk
                raise ValueError(f"Could not apply hunk at line {hunk['start']} in {target_file}")
        
        # Write the patched content
        updated_content = '\n'.join(lines)
        
        # Validate the patched content
        validation_result = self.validator.validate_file_content(target_file, updated_content)
        if not validation_result.is_valid:
            raise ValueError(f"Patched file validation failed: {validation_result.error_message}")
        
        target_file.write_text(updated_content)
        return True
    
    def _generate_argument_code(self, option_name: str, config: Dict[str, Any]) -> str:
        """Generate Python code for adding a CLI argument.
        
        Args:
            option_name: Name of the option
            config: Configuration dictionary
            
        Returns:
            Python code string
        """
        # Base indentation to match existing code
        indent = '    '
        
        code_parts = [f'{indent}init_parser.add_argument(']
        code_parts.append(f'{indent}    \'{option_name}\',')
        
        if 'type' in config:
            code_parts.append(f'{indent}    type={config["type"].__name__},')
        
        if 'action' in config:
            code_parts.append(f'{indent}    action=\'{config["action"]}\',')
        
        if 'choices' in config:
            choices_str = str(config['choices'])
            code_parts.append(f'{indent}    choices={choices_str},')
        
        if 'default' in config:
            default_str = repr(config['default'])
            code_parts.append(f'{indent}    default={default_str},')
        
        if 'help' in config:
            help_str = repr(config['help'])
            code_parts.append(f'{indent}    help={help_str}')
        
        code_parts.append(f'{indent})')
        
        return '\n'.join(code_parts)