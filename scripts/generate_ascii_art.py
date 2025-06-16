#!/usr/bin/env python3
"""
ASCII Art Generator for AgenticScrum
Generates block-style ASCII art with neon yellow color scheme
"""

import sys
from typing import Dict, List

# ANSI color codes
NEON_YELLOW = '\033[93m'
BRIGHT_YELLOW = '\033[33;1m'
DIM_YELLOW = '\033[33m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Block characters for creating the art
FULL_BLOCK = '█'
LIGHT_SHADE = '░'
MEDIUM_SHADE = '▒'
DARK_SHADE = '▓'
UPPER_HALF = '▀'
LOWER_HALF = '▄'
LEFT_HALF = '▌'
RIGHT_HALF = '▐'

# Block-style font definition (simplified 5x7 grid per character)
BLOCK_FONT = {
    'A': [
        '  ███  ',
        ' █   █ ',
        '███████',
        '█     █',
        '█     █'
    ],
    'B': [
        '██████ ',
        '█     █',
        '██████ ',
        '█     █',
        '██████ '
    ],
    'C': [
        ' █████ ',
        '█     █',
        '█      ',
        '█     █',
        ' █████ '
    ],
    'D': [
        '██████ ',
        '█     █',
        '█     █',
        '█     █',
        '██████ '
    ],
    'E': [
        '███████',
        '█      ',
        '█████  ',
        '█      ',
        '███████'
    ],
    'F': [
        '███████',
        '█      ',
        '█████  ',
        '█      ',
        '█      '
    ],
    'G': [
        ' █████ ',
        '█     █',
        '█  ████',
        '█     █',
        ' █████ '
    ],
    'H': [
        '█     █',
        '█     █',
        '███████',
        '█     █',
        '█     █'
    ],
    'I': [
        '███████',
        '   █   ',
        '   █   ',
        '   █   ',
        '███████'
    ],
    'J': [
        '███████',
        '    █  ',
        '    █  ',
        '█   █  ',
        ' ███   '
    ],
    'K': [
        '█    █ ',
        '█   █  ',
        '████   ',
        '█   █  ',
        '█    █ '
    ],
    'L': [
        '█      ',
        '█      ',
        '█      ',
        '█      ',
        '███████'
    ],
    'M': [
        '█     █',
        '██   ██',
        '█ █ █ █',
        '█  █  █',
        '█     █'
    ],
    'N': [
        '█     █',
        '██    █',
        '█ █   █',
        '█  █  █',
        '█   ███'
    ],
    'O': [
        ' █████ ',
        '█     █',
        '█     █',
        '█     █',
        ' █████ '
    ],
    'P': [
        '██████ ',
        '█     █',
        '██████ ',
        '█      ',
        '█      '
    ],
    'Q': [
        ' █████ ',
        '█     █',
        '█     █',
        '█   █ █',
        ' ████ █'
    ],
    'R': [
        '██████ ',
        '█     █',
        '██████ ',
        '█   █  ',
        '█    █ '
    ],
    'S': [
        ' █████ ',
        '█     █',
        ' █████ ',
        '      █',
        '██████ '
    ],
    'T': [
        '███████',
        '   █   ',
        '   █   ',
        '   █   ',
        '   █   '
    ],
    'U': [
        '█     █',
        '█     █',
        '█     █',
        '█     █',
        ' █████ '
    ],
    'V': [
        '█     █',
        '█     █',
        ' █   █ ',
        '  █ █  ',
        '   █   '
    ],
    'W': [
        '█     █',
        '█  █  █',
        '█ █ █ █',
        '██   ██',
        '█     █'
    ],
    'X': [
        '█     █',
        ' █   █ ',
        '  ███  ',
        ' █   █ ',
        '█     █'
    ],
    'Y': [
        '█     █',
        ' █   █ ',
        '  ███  ',
        '   █   ',
        '   █   '
    ],
    'Z': [
        '███████',
        '     █ ',
        '   ██  ',
        ' ██    ',
        '███████'
    ],
    ' ': [
        '       ',
        '       ',
        '       ',
        '       ',
        '       '
    ],
    '-': [
        '       ',
        '       ',
        '███████',
        '       ',
        '       '
    ],
    '_': [
        '       ',
        '       ',
        '       ',
        '       ',
        '███████'
    ],
    '.': [
        '       ',
        '       ',
        '       ',
        '  ██   ',
        '  ██   '
    ],
    '!': [
        '  ██   ',
        '  ██   ',
        '  ██   ',
        '       ',
        '  ██   '
    ],
    '?': [
        ' █████ ',
        '█     █',
        '    ██ ',
        '       ',
        '   ██  '
    ],
    '1': [
        '  ██   ',
        ' ███   ',
        '  ██   ',
        '  ██   ',
        '███████'
    ],
    '2': [
        ' █████ ',
        '█     █',
        '    ██ ',
        '  ██   ',
        '███████'
    ],
    '3': [
        '██████ ',
        '      █',
        ' █████ ',
        '      █',
        '██████ '
    ],
    '4': [
        '█    █ ',
        '█    █ ',
        '███████',
        '     █ ',
        '     █ '
    ],
    '5': [
        '███████',
        '█      ',
        '██████ ',
        '      █',
        '██████ '
    ],
}


def generate_block_text(text: str, style: str = 'blocks') -> List[str]:
    """Generate block-style ASCII art for the given text"""
    text = text.upper()
    lines = [''] * 5  # 5 lines for each character row
    
    for char in text:
        if char in BLOCK_FONT:
            char_pattern = BLOCK_FONT[char]
            for i in range(5):
                lines[i] += char_pattern[i] + ' '
        else:
            # Default to space for unknown characters
            for i in range(5):
                lines[i] += '       ' + ' '
    
    # Apply styling
    styled_lines = []
    for line in lines:
        if style == 'blocks':
            # Replace filled areas with block characters
            styled_line = line.replace('█', FULL_BLOCK)
        elif style == 'shade':
            # Use different shading levels
            styled_line = line.replace('█', DARK_SHADE)
        elif style == 'outline':
            # Create outline effect
            styled_line = ''
            for i, char in enumerate(line):
                if char == '█':
                    # Check neighbors to determine if this is an edge
                    left = i > 0 and line[i-1] == '█'
                    right = i < len(line)-1 and line[i+1] == '█'
                    if not left or not right:
                        styled_line += FULL_BLOCK
                    else:
                        styled_line += ' '
                else:
                    styled_line += char
        else:
            styled_line = line
            
        styled_lines.append(styled_line)
    
    return styled_lines


def add_border(lines: List[str], border_style: str = 'simple') -> List[str]:
    """Add a decorative border around the text"""
    if not lines:
        return lines
    
    width = max(len(line) for line in lines)
    bordered_lines = []
    
    if border_style == 'simple':
        border_char = FULL_BLOCK
        bordered_lines.append(border_char * (width + 4))
        for line in lines:
            bordered_lines.append(f"{border_char} {line.ljust(width)} {border_char}")
        bordered_lines.append(border_char * (width + 4))
    elif border_style == 'double':
        top_border = '╔' + '═' * (width + 2) + '╗'
        bottom_border = '╚' + '═' * (width + 2) + '╝'
        bordered_lines.append(top_border)
        for line in lines:
            bordered_lines.append(f"║ {line.ljust(width)} ║")
        bordered_lines.append(bottom_border)
    
    return bordered_lines


def colorize(lines: List[str], color_scheme: str = 'neon') -> List[str]:
    """Apply color to the ASCII art"""
    colored_lines = []
    
    if color_scheme == 'neon':
        # Neon yellow with variations
        for i, line in enumerate(lines):
            if i % 2 == 0:
                colored_lines.append(f"{NEON_YELLOW}{BOLD}{line}{RESET}")
            else:
                colored_lines.append(f"{BRIGHT_YELLOW}{line}{RESET}")
    elif color_scheme == 'gradient':
        # Create a gradient effect
        colors = [DIM_YELLOW, BRIGHT_YELLOW, NEON_YELLOW, BRIGHT_YELLOW, DIM_YELLOW]
        for i, line in enumerate(lines):
            color = colors[i % len(colors)]
            colored_lines.append(f"{color}{line}{RESET}")
    else:
        # Plain neon yellow
        for line in lines:
            colored_lines.append(f"{NEON_YELLOW}{line}{RESET}")
    
    return colored_lines


def generate_title(text: str, style: str = 'blocks', border: str = 'simple', 
                  color_scheme: str = 'neon', subtitle: str = '') -> str:
    """Generate a complete title screen"""
    # Generate main title
    title_lines = generate_block_text(text, style)
    
    # Add border if requested
    if border != 'none':
        title_lines = add_border(title_lines, border)
    
    # Colorize
    title_lines = colorize(title_lines, color_scheme)
    
    # Add subtitle if provided
    if subtitle:
        title_lines.append('')
        subtitle_line = f"{BRIGHT_YELLOW}{'═' * 10} {subtitle} {'═' * 10}{RESET}"
        centered_subtitle = subtitle_line.center(len(title_lines[0]) + 20)
        title_lines.append(centered_subtitle)
    
    return '\n'.join(title_lines)


def main():
    """CLI interface for the ASCII art generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ASCII art titles')
    parser.add_argument('text', help='Text to convert to ASCII art')
    parser.add_argument('--style', choices=['blocks', 'shade', 'outline'], 
                       default='blocks', help='Art style')
    parser.add_argument('--border', choices=['none', 'simple', 'double'], 
                       default='simple', help='Border style')
    parser.add_argument('--color', choices=['neon', 'gradient', 'plain'], 
                       default='neon', help='Color scheme')
    parser.add_argument('--subtitle', default='', help='Optional subtitle')
    
    args = parser.parse_args()
    
    # Generate and print the title
    title = generate_title(args.text, args.style, args.border, 
                          args.color, args.subtitle)
    print(title)


if __name__ == '__main__':
    main()