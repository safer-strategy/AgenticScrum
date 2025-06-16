#!/usr/bin/env python3
"""
Animated ASCII Art Generator for AgenticScrum
Creates animated block-style ASCII art with neon effects
"""

import sys
import time
import random
from typing import List
from generate_ascii_art import BLOCK_FONT, FULL_BLOCK, generate_block_text, colorize

# ANSI codes for animation
CLEAR_LINE = '\033[2K'
CURSOR_UP = '\033[A'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'
RESET = '\033[0m'

# Neon color variations for animation
NEON_COLORS = [
    '\033[93m',      # Yellow
    '\033[33;1m',    # Bright yellow
    '\033[38;5;226m', # Neon yellow
    '\033[38;5;227m', # Light neon yellow
    '\033[38;5;228m', # Bright neon yellow
    '\033[38;5;229m', # Extra bright yellow
]


def matrix_rain_effect(text: str, duration: float = 2.0):
    """Create a matrix-style rain effect revealing the text"""
    lines = generate_block_text(text, 'blocks')
    height = len(lines)
    width = max(len(line) for line in lines) if lines else 0
    
    # Create a matrix to track revealed positions
    revealed = [[False] * width for _ in range(height)]
    
    # Hide cursor
    print(HIDE_CURSOR, end='', flush=True)
    
    # Print empty lines first
    for _ in range(height):
        print()
    
    # Move cursor back up
    print(f'\033[{height}A', end='', flush=True)
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Randomly reveal characters
        for _ in range(width // 4):  # Reveal multiple chars per frame
            y = random.randint(0, height - 1)
            x = random.randint(0, width - 1)
            revealed[y][x] = True
        
        # Redraw the text
        for y in range(height):
            line_output = ''
            for x in range(width):
                if x < len(lines[y]):
                    char = lines[y][x]
                    if revealed[y][x] and char != ' ':
                        # Use random neon color for revealed characters
                        color = random.choice(NEON_COLORS)
                        line_output += f"{color}{char}{RESET}"
                    else:
                        line_output += ' '
                else:
                    line_output += ' '
            
            print(f'\r{CLEAR_LINE}{line_output}')
        
        # Move cursor back up
        print(f'\033[{height}A', end='', flush=True)
        time.sleep(0.05)
    
    # Final reveal with stable color
    for i, line in enumerate(lines):
        color = NEON_COLORS[i % len(NEON_COLORS)]
        print(f'\r{CLEAR_LINE}{color}{line}{RESET}')
    
    # Show cursor again
    print(SHOW_CURSOR, end='', flush=True)


def typing_effect(text: str, speed: float = 0.05):
    """Create a typing effect for the ASCII art"""
    lines = generate_block_text(text, 'blocks')
    
    print(HIDE_CURSOR, end='', flush=True)
    
    for i, line in enumerate(lines):
        color = NEON_COLORS[i % len(NEON_COLORS)]
        output = ''
        for char in line:
            output += char
            print(f'\r{color}{output}{RESET}', end='', flush=True)
            if char != ' ':
                time.sleep(speed)
        print()  # New line after each row
    
    print(SHOW_CURSOR, end='', flush=True)


def pulse_effect(text: str, pulses: int = 3):
    """Create a pulsing neon effect"""
    lines = generate_block_text(text, 'blocks')
    height = len(lines)
    
    print(HIDE_CURSOR, end='', flush=True)
    
    # Print lines initially
    for line in lines:
        print(f"{NEON_COLORS[0]}{line}{RESET}")
    
    # Move cursor back up
    print(f'\033[{height}A', end='', flush=True)
    
    # Pulse effect
    for pulse in range(pulses):
        # Brighten
        for i in range(len(NEON_COLORS)):
            for j, line in enumerate(lines):
                print(f'\r{CLEAR_LINE}{NEON_COLORS[i]}{line}{RESET}')
            print(f'\033[{height}A', end='', flush=True)
            time.sleep(0.1)
        
        # Dim back
        for i in range(len(NEON_COLORS) - 1, -1, -1):
            for j, line in enumerate(lines):
                print(f'\r{CLEAR_LINE}{NEON_COLORS[i]}{line}{RESET}')
            print(f'\033[{height}A', end='', flush=True)
            time.sleep(0.1)
    
    # Final stable display
    for line in lines:
        print(f'\r{CLEAR_LINE}{NEON_COLORS[2]}{line}{RESET}')
    
    print(SHOW_CURSOR, end='', flush=True)


def glitch_effect(text: str, duration: float = 1.0):
    """Create a glitch effect"""
    lines = generate_block_text(text, 'blocks')
    height = len(lines)
    
    print(HIDE_CURSOR, end='', flush=True)
    
    # Print initial text
    for line in lines:
        print(f"{NEON_COLORS[2]}{line}{RESET}")
    
    print(f'\033[{height}A', end='', flush=True)
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Random glitch
        if random.random() < 0.3:  # 30% chance of glitch
            glitch_lines = []
            for line in lines:
                if random.random() < 0.2:  # 20% chance per line
                    # Create glitched line
                    glitched = ''
                    for char in line:
                        if char != ' ' and random.random() < 0.3:
                            glitched += random.choice(['▓', '▒', '░', '█', '▄', '▀'])
                        else:
                            glitched += char
                    glitch_lines.append(glitched)
                else:
                    glitch_lines.append(line)
            
            # Display glitched version
            for i, line in enumerate(glitch_lines):
                color = random.choice(NEON_COLORS)
                print(f'\r{CLEAR_LINE}{color}{line}{RESET}')
            
            print(f'\033[{height}A', end='', flush=True)
            time.sleep(0.05)
        
        # Restore normal
        for i, line in enumerate(lines):
            print(f'\r{CLEAR_LINE}{NEON_COLORS[2]}{line}{RESET}')
        
        print(f'\033[{height}A', end='', flush=True)
        time.sleep(0.1)
    
    # Final stable display
    for line in lines:
        print(f'\r{CLEAR_LINE}{NEON_COLORS[2]}{line}{RESET}')
    
    print(SHOW_CURSOR, end='', flush=True)


def scan_effect(text: str):
    """Create a scanning effect that reveals the text"""
    lines = generate_block_text(text, 'blocks')
    height = len(lines)
    width = max(len(line) for line in lines) if lines else 0
    
    print(HIDE_CURSOR, end='', flush=True)
    
    # Print empty lines
    for _ in range(height):
        print()
    
    print(f'\033[{height}A', end='', flush=True)
    
    # Scan from left to right
    for x in range(width + 1):
        for y, line in enumerate(lines):
            output = ''
            for i, char in enumerate(line):
                if i < x:
                    # Already scanned - show in stable color
                    if char != ' ':
                        output += f"{NEON_COLORS[2]}{char}{RESET}"
                    else:
                        output += char
                elif i == x:
                    # Scanning line - bright effect
                    if char != ' ':
                        output += f"{NEON_COLORS[-1]}{char}{RESET}"
                    else:
                        output += char
                else:
                    # Not yet scanned
                    output += ' '
            
            print(f'\r{CLEAR_LINE}{output}', end='')
            if y < height - 1:
                print()  # New line except for last line
        
        print(f'\033[{height-1}A', end='', flush=True)
        time.sleep(0.02)
    
    # Move to end
    for _ in range(height - 1):
        print()
    
    print(SHOW_CURSOR, end='', flush=True)


def main():
    """CLI interface for animated ASCII art"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate animated ASCII art')
    parser.add_argument('text', help='Text to animate')
    parser.add_argument('--effect', choices=['matrix', 'typing', 'pulse', 'glitch', 'scan'],
                       default='matrix', help='Animation effect')
    parser.add_argument('--duration', type=float, default=2.0,
                       help='Duration for certain effects')
    parser.add_argument('--speed', type=float, default=0.05,
                       help='Speed for typing effect')
    
    args = parser.parse_args()
    
    # Apply the selected effect
    if args.effect == 'matrix':
        matrix_rain_effect(args.text, args.duration)
    elif args.effect == 'typing':
        typing_effect(args.text, args.speed)
    elif args.effect == 'pulse':
        pulse_effect(args.text, int(args.duration))
    elif args.effect == 'glitch':
        glitch_effect(args.text, args.duration)
    elif args.effect == 'scan':
        scan_effect(args.text)
    
    # Add a subtitle after animation
    subtitle = "AI-Driven Development Framework"
    print()
    print(f"{NEON_COLORS[1]}{'═' * 10} {subtitle} {'═' * 10}{RESET}")


if __name__ == '__main__':
    main()