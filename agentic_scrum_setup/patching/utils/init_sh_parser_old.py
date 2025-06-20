"""Init.sh Parser - Safe parsing and modification of init.sh files."""

import re
from typing import List, Dict, Tuple, Optional


class InitShParser:
    """Parse and modify init.sh files safely."""
    
    def __init__(self, content: str):
        self.lines = content.split('\n')
        self.main_case_start = None
        self.main_case_end = None
        self.main_func_start = None
        self.main_func_end = None
        self.cases = {}
        self.functions = {}
        self._parse()
    
    def _parse(self):
        """Parse the init.sh structure."""
        in_function = False
        current_function = None
        function_brace_depth = 0
        function_start_line = None
        
        # First pass: identify functions
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            
            # Track function definitions
            func_match = re.match(r'^(?:function\s+)?(\w+)\s*\(\).*$', line)
            if func_match and not in_function:
                func_name = func_match.group(1)
                self.functions[func_name] = {'start': i, 'lines': []}
                current_function = func_name
                in_function = True
                function_start_line = i
                
                if func_name == 'main':
                    self.main_func_start = i
                
                # Check if opening brace is on same line
                if '{' in line:
                    function_brace_depth = 1
                elif i + 1 < len(self.lines):
                    # Look for opening brace on next line
                    next_line = self.lines[i + 1].strip()
                    if next_line == '{':
                        function_brace_depth = 0  # Will be incremented when we process the brace line
            
            # Track braces for function end
            if in_function:
                # Count braces but ignore those in strings
                line_without_strings = re.sub(r'"[^"]*"', '', line)
                line_without_strings = re.sub(r"'[^']*'", '', line_without_strings)
                
                # Only start counting after we've seen the first brace
                if function_brace_depth > 0 or '{' in line_without_strings:
                    function_brace_depth += line_without_strings.count('{') - line_without_strings.count('}')
                    
                    if function_brace_depth == 0 and i > function_start_line:
                        self.functions[current_function]['end'] = i
                        if current_function == 'main':
                            self.main_func_end = i
                        current_function = None
                        in_function = False
                        function_brace_depth = 0
        
        # Second pass: parse case statements within main function
        if self.main_func_start is not None and self.main_func_end is not None:
            in_case = False
            current_case = None
            
            for i in range(self.main_func_start, self.main_func_end + 1):
                line = self.lines[i]
                stripped = line.strip()
                
                # Find case statement
                if not in_case and re.match(r'case\s+["\']?\$\w*["\']?\s+in', stripped):
                    self.main_case_start = i
                    in_case = True
                
                # Parse individual cases
                if in_case:
                    # Look for case patterns
                    if ')' in line and not line.strip().startswith('*)'):
                        # Extract everything before the first )
                        before_paren = line.split(')')[0]
                        # Remove leading whitespace
                        case_part = before_paren.strip()
                        
                        # Handle different quote styles
                        case_part = re.sub(r'^["\'](.+)["\']$', r'\1', case_part)
                        
                        if case_part and not case_part.startswith('('):
                            # This is a new case
                            if ';;' in line:
                                # Inline case - complete on one line
                                self.cases[case_part] = {
                                    'start': i,
                                    'end': i,
                                    'lines': [line]
                                }
                            else:
                                # Multi-line case
                                current_case = case_part
                                self.cases[case_part] = {
                                    'start': i,
                                    'lines': [line]
                                }
                    elif line.strip().startswith('*)'):
                        # Default case
                        case_part = '*'
                        if ';;' in line:
                            # Inline default case
                            self.cases[case_part] = {
                                'start': i,
                                'end': i,
                                'lines': [line]
                            }
                        else:
                            current_case = case_part
                            self.cases[case_part] = {
                                'start': i,
                                'lines': [line]
                            }
                    elif current_case and current_case in self.cases:
                        # Continue collecting lines for current case
                        self.cases[current_case]['lines'].append(line)
                        
                        # Check for end of case
                        if ';;' in line:
                            self.cases[current_case]['end'] = i
                            current_case = None
                    
                    # End of case statement
                    if 'esac' in stripped:
                        self.main_case_end = i
                        in_case = False
    
    def case_exists(self, case_name: str) -> bool:
        """Check if a case already exists."""
        # Check exact match
        if case_name in self.cases:
            return True
        
        # Check if case exists in any multi-case pattern (e.g., "help|*)")
        for case_pattern in self.cases:
            if '|' in case_pattern:
                cases = [c.strip() for c in case_pattern.split('|')]
                if case_name in cases:
                    return True
        
        return False
    
    def function_exists(self, func_name: str) -> bool:
        """Check if a function already exists."""
        return func_name in self.functions
    
    def add_case(self, case_name: str, case_body: List[str], 
                 after_case: str = None, before_case: str = None) -> bool:
        """Add a new case to the main switch."""
        if self.case_exists(case_name):
            return False  # Already exists
        
        if self.main_case_start is None or self.main_case_end is None:
            raise ValueError("No case statement found in main function")
        
        # Find insertion point
        insert_line = None
        
        if after_case:
            # Insert after specified case
            if after_case in self.cases:
                insert_line = self.cases[after_case]['end'] + 1
            else:
                # Look for case in multi-case patterns
                for case_pattern, info in self.cases.items():
                    if '|' in case_pattern and after_case in case_pattern:
                        insert_line = info['end'] + 1
                        break
        
        elif before_case:
            # Insert before specified case
            if before_case in self.cases:
                insert_line = self.cases[before_case]['start']
            else:
                # Look for case in multi-case patterns
                for case_pattern, info in self.cases.items():
                    if '|' in case_pattern and before_case in case_pattern:
                        insert_line = info['start']
                        break
        
        if insert_line is None:
            # Default: insert before help|*) or *) case
            for case_pattern, info in self.cases.items():
                if 'help' in case_pattern or '*' in case_pattern:
                    insert_line = info['start']
                    break
            else:
                # If no default case, insert before esac
                insert_line = self.main_case_end
        
        # Build case block with proper indentation
        indent = self._get_case_indent()
        case_lines = [f"{indent}{case_name})"]
        for line in case_body:
            if line:  # Skip empty lines from getting extra indentation
                case_lines.append(f"{indent}  {line}")
            else:
                case_lines.append("")
        case_lines.append(f"{indent}  ;;")
        
        # Insert the case
        for i, line in enumerate(case_lines):
            self.lines.insert(insert_line + i, line)
        
        # Update line numbers for cases after insertion
        self._update_line_numbers(insert_line, len(case_lines))
        
        # Add the new case to our tracking
        self.cases[case_name] = {
            'start': insert_line,
            'end': insert_line + len(case_lines) - 1,
            'lines': case_lines
        }
        
        return True
    
    def add_function(self, func_name: str, func_body: List[str],
                    before_marker: str = "# --- Main Dispatcher ---",
                    after_function: str = None) -> bool:
        """Add a function before the main dispatcher or after another function."""
        if self.function_exists(func_name):
            return False  # Already exists
        
        # Find insertion point
        insert_line = None
        
        if after_function and after_function in self.functions:
            # Insert after specified function
            insert_line = self.functions[after_function]['end'] + 1
        else:
            # Look for marker
            for i, line in enumerate(self.lines):
                if before_marker in line:
                    insert_line = i
                    break
            
            if insert_line is None and self.main_func_start is not None:
                # Fallback: insert before main function
                insert_line = self.main_func_start
            
            if insert_line is None:
                # Last resort: end of file
                insert_line = len(self.lines)
        
        # Build function with proper formatting
        func_lines = ['', f'function {func_name}() {{']
        for line in func_body:
            if line:  # Preserve empty lines
                func_lines.append(f'  {line}')
            else:
                func_lines.append('')
        func_lines.append('}')
        func_lines.append('')  # Extra newline after function
        
        # Insert the function
        for i, line in enumerate(func_lines):
            self.lines.insert(insert_line + i, line)
        
        # Update line numbers
        self._update_line_numbers(insert_line, len(func_lines))
        
        return True
    
    def update_case(self, case_name: str, new_body: List[str]) -> bool:
        """Update an existing case with new body."""
        if case_name not in self.cases:
            return False
        
        case_info = self.cases[case_name]
        start_line = case_info['start'] + 1  # Skip the case pattern line
        end_line = case_info['end']  # ;;
        
        # Get indentation
        indent = self._get_case_indent()
        
        # Build new content
        new_lines = []
        for line in new_body:
            if line:
                new_lines.append(f"{indent}  {line}")
            else:
                new_lines.append("")
        
        # Replace the content
        self.lines[start_line:end_line] = new_lines
        
        # Update line numbers
        old_length = end_line - start_line
        new_length = len(new_lines)
        if old_length != new_length:
            self._update_line_numbers(end_line, new_length - old_length)
        
        return True
    
    def _get_case_indent(self) -> str:
        """Get the indentation used for cases."""
        if self.cases:
            # Get indent from first case
            for case_info in self.cases.values():
                line = self.lines[case_info['start']]
                match = re.match(r'^(\s*)', line)
                if match:
                    return match.group(1)
        
        # Fallback: check case statement indent and add 2 spaces
        if self.main_case_start is not None:
            case_line = self.lines[self.main_case_start]
            match = re.match(r'^(\s*)', case_line)
            if match:
                return match.group(1) + '  '
        
        return '    '  # Default to 4 spaces
    
    def _update_line_numbers(self, insert_point: int, num_lines: int):
        """Update line numbers after insertion."""
        # Update case line numbers
        for case_info in self.cases.values():
            if case_info['start'] >= insert_point:
                case_info['start'] += num_lines
            if case_info['end'] >= insert_point:
                case_info['end'] += num_lines
        
        # Update function line numbers
        for func_info in self.functions.values():
            if func_info['start'] >= insert_point:
                func_info['start'] += num_lines
            if 'end' in func_info and func_info['end'] >= insert_point:
                func_info['end'] += num_lines
        
        # Update main case boundaries
        if self.main_case_start and self.main_case_start >= insert_point:
            self.main_case_start += num_lines
        if self.main_case_end and self.main_case_end >= insert_point:
            self.main_case_end += num_lines
        
        # Update main function boundaries
        if self.main_func_start and self.main_func_start >= insert_point:
            self.main_func_start += num_lines
        if self.main_func_end and self.main_func_end >= insert_point:
            self.main_func_end += num_lines
    
    def get_content(self) -> str:
        """Get the modified content."""
        return '\n'.join(self.lines)
    
    def get_case_names(self) -> List[str]:
        """Get list of all case names."""
        names = []
        for case_pattern in self.cases.keys():
            if '|' in case_pattern:
                names.extend([c.strip() for c in case_pattern.split('|')])
            else:
                names.append(case_pattern)
        return names
    
    def get_function_names(self) -> List[str]:
        """Get list of all function names."""
        return list(self.functions.keys())