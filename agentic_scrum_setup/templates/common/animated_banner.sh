#!/bin/bash
# Animated ASCII Banner for AgenticScrum
# This is a self-contained version that can be embedded in init.sh

function show_animated_banner() {
    local text="$1"
    local subtitle="${2:-AI-Driven Development Framework}"
    
    # ANSI codes
    local CLEAR_LINE='\033[2K'
    local CURSOR_UP='\033[A'
    local HIDE_CURSOR='\033[?25l'
    local SHOW_CURSOR='\033[?25h'
    local RESET='\033[0m'
    
    # Neon colors
    local YELLOW='\033[93m'
    local BRIGHT_YELLOW='\033[33;1m'
    local NEON_YELLOW='\033[38;5;226m'
    local LIGHT_NEON='\033[38;5;227m'
    local BRIGHT_NEON='\033[38;5;228m'
    local EXTRA_BRIGHT='\033[38;5;229m'
    
    # Block characters for ASCII art
    local FULL_BLOCK='█'
    local LIGHT_SHADE='░'
    local MEDIUM_SHADE='▒'
    local DARK_SHADE='▓'
    
    # Simple block font mapping
    declare -A BLOCK_LETTERS
    BLOCK_LETTERS[A]="███  ▄█▄  █ █"
    BLOCK_LETTERS[B]="███  ███  ███"
    BLOCK_LETTERS[C]="███  █    ███"
    BLOCK_LETTERS[D]="██▄  █ █  ███"
    BLOCK_LETTERS[E]="███  ██   ███"
    BLOCK_LETTERS[F]="███  ██   █"
    BLOCK_LETTERS[G]="███  █ █  ███"
    BLOCK_LETTERS[H]="█ █  ███  █ █"
    BLOCK_LETTERS[I]="███   █   ███"
    BLOCK_LETTERS[J]="  █   █   ██"
    BLOCK_LETTERS[K]="█ █  ██   █ █"
    BLOCK_LETTERS[L]="█    █    ███"
    BLOCK_LETTERS[M]="█ █  ███  █ █"
    BLOCK_LETTERS[N]="██▄  █ █  █▄█"
    BLOCK_LETTERS[O]="███  █ █  ███"
    BLOCK_LETTERS[P]="███  ███  █"
    BLOCK_LETTERS[Q]="███  █ █  ██▄"
    BLOCK_LETTERS[R]="███  ███  █ █"
    BLOCK_LETTERS[S]="███  ▄█▄  ███"
    BLOCK_LETTERS[T]="███   █    █"
    BLOCK_LETTERS[U]="█ █  █ █  ███"
    BLOCK_LETTERS[V]="█ █  █ █  ▄█▄"
    BLOCK_LETTERS[W]="█ █  ███  █ █"
    BLOCK_LETTERS[X]="█ █  ▄█▄  █ █"
    BLOCK_LETTERS[Y]="█ █  ▄█▄   █"
    BLOCK_LETTERS[Z]="███  ▄█▄  ███"
    BLOCK_LETTERS[' ']="     "
    BLOCK_LETTERS['-']="     ███  "
    BLOCK_LETTERS['_']="        ███"
    
    # Convert text to uppercase
    text="${text^^}"
    
    # Hide cursor
    echo -ne "$HIDE_CURSOR"
    
    # Generate block text (simplified 3-line version)
    local lines=("" "" "")
    for (( i=0; i<${#text}; i++ )); do
        local char="${text:i:1}"
        local pattern="${BLOCK_LETTERS[$char]:-█ █  ▄█▄  █ █}"
        
        # Split pattern into 3 lines (groups of 5 chars)
        lines[0]+="${pattern:0:5} "
        lines[1]+="${pattern:5:5} "
        lines[2]+="${pattern:10:5} "
    done
    
    # Matrix rain effect (simplified)
    local width=${#lines[0]}
    local height=3
    
    # Print empty lines
    for (( i=0; i<$height; i++ )); do
        echo
    done
    
    # Move cursor back up
    echo -ne "\033[${height}A"
    
    # Animate reveal
    for (( x=0; x<=$width; x++ )); do
        for (( y=0; y<$height; y++ )); do
            local line="${lines[$y]}"
            local output=""
            
            for (( i=0; i<${#line}; i++ )); do
                local char="${line:i:1}"
                if (( i < x )); then
                    # Revealed characters with color
                    if [[ "$char" != " " ]]; then
                        output+="${NEON_YELLOW}${char}${RESET}"
                    else
                        output+=" "
                    fi
                elif (( i == x )); then
                    # Scanning position - extra bright
                    if [[ "$char" != " " ]]; then
                        output+="${EXTRA_BRIGHT}${char}${RESET}"
                    else
                        output+=" "
                    fi
                else
                    # Not yet revealed
                    output+=" "
                fi
            done
            
            echo -ne "\r${CLEAR_LINE}${output}"
            if (( y < height - 1 )); then
                echo
            fi
        done
        
        # Move cursor back up
        if (( x < width )); then
            echo -ne "\033[$((height-1))A"
        fi
        
        # Animation speed
        sleep 0.02
    done
    
    # Final pulse effect
    echo
    for (( pulse=0; pulse<2; pulse++ )); do
        # Brighten
        for color in "$BRIGHT_YELLOW" "$LIGHT_NEON" "$BRIGHT_NEON" "$EXTRA_BRIGHT"; do
            echo -ne "\033[${height}A"
            for (( y=0; y<$height; y++ )); do
                echo -ne "\r${CLEAR_LINE}${color}${lines[$y]}${RESET}"
                if (( y < height - 1 )); then
                    echo
                fi
            done
            sleep 0.05
        done
        
        # Dim back
        for color in "$BRIGHT_NEON" "$LIGHT_NEON" "$BRIGHT_YELLOW" "$NEON_YELLOW"; do
            echo -ne "\033[${height}A"
            for (( y=0; y<$height; y++ )); do
                echo -ne "\r${CLEAR_LINE}${color}${lines[$y]}${RESET}"
                if (( y < height - 1 )); then
                    echo
                fi
            done
            sleep 0.05
        done
    done
    
    # Final stable display
    echo
    
    # Add subtitle
    local subtitle_width=${#subtitle}
    local total_width=$((subtitle_width + 20))
    echo
    echo -e "${BRIGHT_YELLOW}$( printf '═%.0s' $(seq 1 10) ) ${subtitle} $( printf '═%.0s' $(seq 1 10) )${RESET}"
    
    # Show cursor again
    echo -ne "$SHOW_CURSOR"
}

# If sourced with arguments, run the animation
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    show_animated_banner "${1:-AGENTIC SCRUM}" "${2:-AI-Driven Development Framework}"
fi