"""Init.sh Parser V2 - Simplified and more robust parsing of init.sh files."""

import re
from typing import List, Dict, Optional, Tuple


class InitShParser:
    """Parse and modify init.sh files safely."""
    
    def __init__(self, content: str):
        self.lines = content.split('\n')
        self.functions = {}
        self.cases = {}
        self.main_func_start = None
        self.main_func_end = None
        self.main_case_start = None
        self.main_case_end = None
        self._parse()
    
    def _parse(self):
        """Parse the init.sh structure."""
        # First, find all functions and their boundaries
        self._parse_functions()
        
        # Then parse case statements within main function
        self._parse_cases()
    
    def _parse_functions(self):
        """Parse all function definitions."""
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            
            # Look for function definition
            func_match = re.match(r'^(?:function\s+)?(\w+)\s*\(\)', line)
            if func_match:
                func_name = func_match.group(1)
                func_start = i
                
                # Find the end of this function
                func_end = self._find_function_end(i)
                
                self.functions[func_name] = {
                    'start': func_start,
                    'end': func_end,
                    'lines': self.lines[func_start:func_end+1] if func_end else []
                }
                
                if func_name == 'main':
                    self.main_func_start = func_start
                    self.main_func_end = func_end
                
                # Skip to after this function
                i = func_end + 1 if func_end else i + 1
            else:
                i += 1
    
    def _find_function_end(self, start_line: int) -> Optional[int]:
        """Find the end of a function starting at start_line."""
        brace_count = 0
        found_first_brace = False
        
        for i in range(start_line, len(self.lines)):
            line = self.lines[i]
            
            # Count braces, ignoring those in strings
            clean_line = self._remove_strings(line)
            
            # Look for opening brace
            if '{' in clean_line:
                found_first_brace = True
                brace_count += clean_line.count('{')
            
            # Count closing braces
            if found_first_brace:
                brace_count -= clean_line.count('}')
                
                if brace_count == 0:
                    return i
        
        return None
    
    def _remove_strings(self, line: str) -> str:
        """Remove quoted strings from a line to avoid counting braces in strings."""
        # Remove double-quoted strings
        line = re.sub(r'"[^"]*"', '', line)
        # Remove single-quoted strings  
        line = re.sub(r"'[^']*'", '', line)
        # Remove heredoc markers
        line = re.sub(r'<<\s*\w+', '', line)
        return line
    
    def _parse_cases(self):
        """Parse case statements within the main function."""
        if self.main_func_start is None or self.main_func_end is None:
            return
        
        in_case_statement = False
        current_case = None
        
        for i in range(self.main_func_start, self.main_func_end + 1):
            line = self.lines[i]
            stripped = line.strip()
            
            # Look for case statement start
            if not in_case_statement and re.search(r'case\s+["\']?\$\w*["\']?\s+in', stripped):
                self.main_case_start = i
                in_case_statement = True
                continue
            
            if in_case_statement:
                # Look for case end
                if stripped == 'esac':
                    self.main_case_end = i
                    in_case_statement = False
                    if current_case:
                        self.cases[current_case]['end'] = i - 1
                        current_case = None
                    continue
                
                # Look for case patterns
                case_match = re.match(r'^\s*([^)]+)\)', line)
                if case_match:
                    # Save previous case end if needed
                    if current_case:
                        # Find the ;; before this new case
                        for j in range(self.cases[current_case]['start'], i):
                            if ';;' in self.lines[j]:
                                self.cases[current_case]['end'] = j
                                break
                    
                    # Start new case
                    case_pattern = case_match.group(1).strip()
                    # Remove quotes if present
                    case_pattern = re.sub(r'^["\']|["\']$', '', case_pattern)
                    
                    current_case = case_pattern
                    self.cases[case_pattern] = {
                        'start': i,
                        'lines': []
                    }
                
                # Collect lines for current case
                if current_case:
                    self.cases[current_case]['lines'].append(line)
                    
                    # Check for inline ;; (case end)
                    if ';;' in line:
                        self.cases[current_case]['end'] = i
                        current_case = None
    
    def case_exists(self, case_name: str) -> bool:
        """Check if a case already exists."""
        if case_name in self.cases:
            return True
        
        # Check multi-pattern cases (e.g., "help|--help")
        for pattern in self.cases:
            if '|' in pattern:
                sub_patterns = [p.strip() for p in pattern.split('|')]
                if case_name in sub_patterns:
                    return True
        
        return False
    
    def function_exists(self, func_name: str) -> bool:
        """Check if a function already exists."""
        return func_name in self.functions
    
    def add_case(self, case_name: str, case_body: List[str],
                 after_case: str = None, before_case: str = None) -> bool:
        """Add a new case to the main switch."""
        if self.case_exists(case_name):
            return False
        
        if self.main_case_start is None or self.main_case_end is None:
            raise ValueError("No case statement found in main function")
        
        # Find insertion point
        insert_line = self._find_case_insertion_point(after_case, before_case)
        
        # Build the case with proper indentation
        indent = self._get_case_indent()
        case_lines = [f"{indent}{case_name})"]
        for line in case_body:
            if line:
                case_lines.append(f"{indent}  {line}")
            else:
                case_lines.append("")
        case_lines.append(f"{indent}  ;;")
        
        # Insert the case
        for i, line in enumerate(case_lines):
            self.lines.insert(insert_line + i, line)
        
        # Track the new case
        self.cases[case_name] = {
            'start': insert_line,
            'end': insert_line + len(case_lines) - 1,
            'lines': case_lines
        }
        
        # Update line numbers
        self._update_line_numbers(insert_line, len(case_lines))
        
        return True
    
    def add_function(self, func_name: str, func_body: List[str],
                    before_marker: str = "# --- Main Dispatcher ---",
                    after_function: str = None) -> bool:
        """Add a function."""
        if self.function_exists(func_name):
            return False
        
        # Find insertion point
        insert_line = None
        
        if after_function and after_function in self.functions:
            insert_line = self.functions[after_function]['end'] + 1
        else:
            # Look for marker
            for i, line in enumerate(self.lines):
                if before_marker in line:
                    insert_line = i
                    break
            
            if insert_line is None and self.main_func_start is not None:
                insert_line = self.main_func_start
        
        if insert_line is None:
            insert_line = len(self.lines)
        
        # Build function
        func_lines = ['', f'function {func_name}() {{']
        for line in func_body:
            if line:
                func_lines.append(f'  {line}')
            else:
                func_lines.append('')
        func_lines.append('}')
        func_lines.append('')
        
        # Insert function
        for i, line in enumerate(func_lines):
            self.lines.insert(insert_line + i, line)
        
        # Track the new function
        self.functions[func_name] = {
            'start': insert_line + 1,  # Skip empty line
            'end': insert_line + len(func_lines) - 3,  # Before closing empty line
            'lines': func_lines[1:-1]  # Exclude surrounding empty lines
        }
        
        # Update line numbers
        self._update_line_numbers(insert_line, len(func_lines))
        
        return True
    
    def update_case(self, case_name: str, new_body: List[str]) -> bool:
        """Update an existing case."""
        if case_name not in self.cases:
            return False
        
        case_info = self.cases[case_name]
        start_line = case_info['start'] + 1  # After case pattern
        
        # Find where the case body ends (before ;;)
        end_line = case_info['end']
        for i in range(end_line, start_line - 1, -1):
            if ';;' in self.lines[i]:
                end_line = i
                break
        
        # Get indentation
        indent = self._get_case_indent()
        
        # Build new lines
        new_lines = []
        for line in new_body:
            if line:
                new_lines.append(f"{indent}  {line}")
            else:
                new_lines.append("")
        
        # Replace content (keeping the case pattern and ;;)
        self.lines[start_line:end_line] = new_lines
        
        # Update tracking
        old_length = end_line - start_line
        new_length = len(new_lines)
        if old_length != new_length:
            self._update_line_numbers(end_line, new_length - old_length)
        
        return True
    
    def _find_case_insertion_point(self, after_case: str, before_case: str) -> int:
        """Find where to insert a new case."""
        if after_case:
            # Insert after specified case
            if after_case in self.cases:
                return self.cases[after_case]['end'] + 1
            # Check multi-pattern cases
            for pattern, info in self.cases.items():
                if '|' in pattern and after_case in pattern:
                    return info['end'] + 1
        
        if before_case:
            # Insert before specified case
            if before_case in self.cases:
                return self.cases[before_case]['start']
            # Check multi-pattern cases
            for pattern, info in self.cases.items():
                if '|' in pattern and before_case in pattern:
                    return info['start']
        
        # Default: insert before default case or esac
        for pattern in ['*', 'help|*', '*)', 'help|*)']:
            if pattern in self.cases:
                return self.cases[pattern]['start']
        
        # Last resort: before esac
        return self.main_case_end
    
    def _get_case_indent(self) -> str:
        """Get the indentation level for cases."""
        if self.cases:
            # Use existing case indentation
            first_case = next(iter(self.cases.values()))
            case_line = self.lines[first_case['start']]
            match = re.match(r'^(\s*)', case_line)
            if match:
                return match.group(1)
        
        # Fallback: use case statement indent + 2
        if self.main_case_start is not None:
            case_line = self.lines[self.main_case_start]
            match = re.match(r'^(\s*)', case_line)
            if match:
                return match.group(1) + '  '
        
        return '    '
    
    def _update_line_numbers(self, insert_point: int, num_lines: int):
        """Update all tracked line numbers after an insertion."""
        # Update cases
        for case_info in self.cases.values():
            if case_info['start'] >= insert_point:
                case_info['start'] += num_lines
            if 'end' in case_info and case_info['end'] >= insert_point:
                case_info['end'] += num_lines
        
        # Update functions
        for func_info in self.functions.values():
            if func_info['start'] >= insert_point:
                func_info['start'] += num_lines
            if 'end' in func_info and func_info['end'] >= insert_point:
                func_info['end'] += num_lines
        
        # Update main boundaries
        if self.main_func_start and self.main_func_start >= insert_point:
            self.main_func_start += num_lines
        if self.main_func_end and self.main_func_end >= insert_point:
            self.main_func_end += num_lines
        if self.main_case_start and self.main_case_start >= insert_point:
            self.main_case_start += num_lines
        if self.main_case_end and self.main_case_end >= insert_point:
            self.main_case_end += num_lines
    
    def get_content(self) -> str:
        """Get the modified content."""
        return '\n'.join(self.lines)