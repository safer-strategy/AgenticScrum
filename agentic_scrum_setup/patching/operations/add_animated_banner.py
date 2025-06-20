"""Add Animated Banner - Add animated ASCII art banner to init.sh."""

from pathlib import Path
from typing import Optional
from ..patcher import PatchApplication
from ..utils.init_sh_parser import InitShParser
from ..utils.init_sh_updater import InitShUpdater


# The animated banner function to add
ANIMATED_BANNER_FUNCTION = '''function show_animated_banner() {
    local text="$1"
    local subtitle="${2:-AI-Driven Development Framework}"
    
    # ANSI codes
    local CLEAR_LINE='\\033[2K'
    local CURSOR_UP='\\033[A'
    local HIDE_CURSOR='\\033[?25l'
    local SHOW_CURSOR='\\033[?25h'
    local RESET='\\033[0m'
    
    # Neon colors
    local YELLOW='\\033[93m'
    local BRIGHT_YELLOW='\\033[33;1m'
    local NEON_YELLOW='\\033[38;5;226m'
    local LIGHT_NEON='\\033[38;5;227m'
    local BRIGHT_NEON='\\033[38;5;228m'
    local EXTRA_BRIGHT='\\033[38;5;229m'
    
    # Block characters
    local FULL_BLOCK='█'
    
    # Convert text to uppercase
    text="${text^^}"
    
    # Hide cursor
    echo -ne "$HIDE_CURSOR"
    
    # Simple block text (3 lines high)
    local line1=""
    local line2=""
    local line3=""
    
    # Build block letters
    for (( i=0; i<${#text}; i++ )); do
        local char="${text:i:1}"
        case "$char" in
            A) line1+="█████  "; line2+=" ███   "; line3+="█   █  " ;;
            B) line1+="████   "; line2+="████   "; line3+="████   " ;;
            C) line1+="█████  "; line2+="█      "; line3+="█████  " ;;
            D) line1+="████   "; line2+="█   █  "; line3+="████   " ;;
            E) line1+="█████  "; line2+="███    "; line3+="█████  " ;;
            F) line1+="█████  "; line2+="███    "; line3+="█      " ;;
            G) line1+="█████  "; line2+="█  ██  "; line3+="█████  " ;;
            H) line1+="█   █  "; line2+="█████  "; line3+="█   █  " ;;
            I) line1+="█████  "; line2+="  █    "; line3+="█████  " ;;
            J) line1+="  ███  "; line2+="    █  "; line3+="████   " ;;
            K) line1+="█   █  "; line2+="███    "; line3+="█   █  " ;;
            L) line1+="█      "; line2+="█      "; line3+="█████  " ;;
            M) line1+="█   █  "; line2+="█████  "; line3+="█   █  " ;;
            N) line1+="█   █  "; line2+="██  █  "; line3+="█   █  " ;;
            O) line1+="█████  "; line2+="█   █  "; line3+="█████  " ;;
            P) line1+="████   "; line2+="████   "; line3+="█      " ;;
            Q) line1+="█████  "; line2+="█   █  "; line3+="████ █ " ;;
            R) line1+="████   "; line2+="████   "; line3+="█   █  " ;;
            S) line1+="█████  "; line2+=" ███   "; line3+="█████  " ;;
            T) line1+="█████  "; line2+="  █    "; line3+="  █    " ;;
            U) line1+="█   █  "; line2+="█   █  "; line3+="█████  " ;;
            V) line1+="█   █  "; line2+="█   █  "; line3+=" ███   " ;;
            W) line1+="█   █  "; line2+="█████  "; line3+="█   █  " ;;
            X) line1+="█   █  "; line2+=" ███   "; line3+="█   █  " ;;
            Y) line1+="█   █  "; line2+=" ███   "; line3+="  █    " ;;
            Z) line1+="█████  "; line2+=" ███   "; line3+="█████  " ;;
            " ") line1+="   "; line2+="   "; line3+="   " ;;
            "-") line1+="   "; line2+="███"; line3+="   " ;;
            *) line1+="███ "; line2+="█ █ "; line3+="███ " ;;
        esac
    done
    
    # Animation variables
    local width=${#line1}
    local lines=("$line1" "$line2" "$line3")
    
    # Print empty lines
    echo
    echo
    echo
    
    # Move cursor back up
    echo -ne "\\033[3A"
    
    # Scan effect - reveal from left to right
    for (( x=0; x<=width; x++ )); do
        for (( y=0; y<3; y++ )); do
            local line="${lines[$y]}"
            local output=""
            
            for (( i=0; i<${#line}; i++ )); do
                if (( i < x )); then
                    local char="${line:i:1}"
                    if [[ "$char" != " " ]]; then
                        output+="${NEON_YELLOW}${char}${RESET}"
                    else
                        output+=" "
                    fi
                else
                    output+=" "
                fi
            done
            
            echo -ne "\\r${CLEAR_LINE}${output}"
            if (( y < 2 )); then
                echo
            fi
        done
        
        if (( x < width )); then
            echo -ne "\\033[2A"
        fi
        
        sleep 0.015
    done
    
    # Pulse effect
    echo
    for (( pulse=0; pulse<2; pulse++ )); do
        for color in "$BRIGHT_YELLOW" "$LIGHT_NEON" "$BRIGHT_NEON" "$EXTRA_BRIGHT"; do
            echo -ne "\\033[3A"
            for line in "${lines[@]}"; do
                echo -ne "\\r${CLEAR_LINE}"
                for (( i=0; i<${#line}; i++ )); do
                    local char="${line:i:1}"
                    if [[ "$char" != " " ]]; then
                        echo -ne "${color}${char}${RESET}"
                    else
                        echo -ne " "
                    fi
                done
                echo
            done
            sleep 0.05
        done
        
        for color in "$BRIGHT_NEON" "$LIGHT_NEON" "$BRIGHT_YELLOW" "$NEON_YELLOW"; do
            echo -ne "\\033[3A"
            for line in "${lines[@]}"; do
                echo -ne "\\r${CLEAR_LINE}"
                for (( i=0; i<${#line}; i++ )); do
                    local char="${line:i:1}"
                    if [[ "$char" != " " ]]; then
                        echo -ne "${color}${char}${RESET}"
                    else
                        echo -ne " "
                    fi
                done
                echo
            done
            sleep 0.05
        done
    done
    
    # Add subtitle
    echo
    echo -e "${BRIGHT_YELLOW}════════════ ${subtitle} ════════════${RESET}"
    
    # Show cursor
    echo -ne "$SHOW_CURSOR"
}'''


def add_animated_banner(patcher, **kwargs) -> PatchApplication:
    """
    Add animated ASCII art banner to project init.sh.
    
    This operation:
    1. Adds the animated banner function to init.sh
    2. Replaces the static header with animated version
    3. Adds option to disable animation with --no-animation flag
    """
    project_path = Path.cwd()
    init_sh_path = project_path / "init.sh"
    
    if not init_sh_path.exists():
        print(f"❌ No init.sh found at {init_sh_path}")
        class FailResult:
            def __init__(self):
                self.success = False
                self.message = "No init.sh found"
        return FailResult()
    
    # Check if animated banner already exists
    content = init_sh_path.read_text()
    if "show_animated_banner" in content:
        print("ℹ️  Animated banner already exists in init.sh")
        class SuccessResult:
            def __init__(self):
                self.success = True
                self.message = "Animated banner already present"
        return SuccessResult()
    
    # Dry run mode
    if kwargs.get('dry_run', False):
        print("🔍 DRY RUN: Add animated banner to init.sh")
        print(f"📁 Project: {project_path}")
        print("")
        print("The following changes would be made:")
        print("  ✅ Add show_animated_banner function")
        print("  ✅ Update header function to use animation")
        print("  ✅ Add --no-animation flag support")
        print("")
        print("ℹ️  No changes applied in dry run mode")
        class DryRunResult:
            def __init__(self):
                self.success = True
                self.message = "Dry run completed"
        return DryRunResult()
    
    try:
        # Parse init.sh
        parser = InitShParser(content)
        
        # Add the animated banner function
        parser.add_function('show_animated_banner', ANIMATED_BANNER_FUNCTION.split('\n')[1:-1])
        
        # Update the header function to use animated banner
        new_header_body = [
            '# Check if animation is disabled',
            'if [[ "$1" == "--no-animation" ]]; then',
            '  # Fall back to static banner',
            '  echo -e "${C_PURPLE}${C_BOLD}"',
            '  echo "    ___    __  __   ____   _____   ____    ___    _   _ "',
            '  echo "   / __|  |  \\/  | |  _ \\  | ____| |  _ \\  / __|  | | | |"',
            '  echo "  | |     | |\\/| | | |_) | |  _|   | |_) | \\_ \\  | |_| |"',
            '  echo "  | |___  | |  | | |  __/  | |___  |  _ <  |___/  |  _  |"',
            '  echo "   \\___|  |_|  |_| |_|     |_____| |_| \\_\\ ____/  |_| |_|"',
            '  echo ""',
            '  echo -e "      >> Welcome to the ${PROJECT_NAME} Environment Manager <<"',
            '  echo -e "${C_RESET}"',
            'else',
            '  # Show animated banner',
            '  show_animated_banner "${PROJECT_NAME}"',
            'fi'
        ]
        
        # Update the header function
        if parser.function_exists('header'):
            # Get the header function info to update it properly
            header_info = parser.functions.get('header', {})
            if header_info:
                # Remove old header function content
                start_line = header_info['start']
                end_line = header_info['end']
                
                # Build the new header function
                new_header_lines = ['function header() {'] + ['  ' + line for line in new_header_body] + ['}']
                
                # Replace the old function with the new one
                parser.lines[start_line:end_line+1] = new_header_lines
                
                # Update the function tracking
                parser.functions['header'] = {
                    'start': start_line,
                    'end': start_line + len(new_header_lines) - 1,
                    'lines': new_header_lines
                }
        else:
            # If header doesn't exist, create a simpler display_banner function
            parser.add_function('display_banner', [
                'show_animated_banner "${PROJECT_NAME}"'
            ])
        
        # Write back the updated content
        init_sh_path.write_text(parser.get_content())
        
        print("✅ Successfully added animated banner to init.sh")
        print("")
        print("🎨 Usage:")
        print("  ./init.sh              # Shows animated banner")
        print("  ./init.sh --no-animation  # Shows static banner")
        
        class SuccessResult:
            def __init__(self, files_modified):
                self.success = True
                self.message = "Added animated banner to init.sh"
                self.files_modified = files_modified
        
        return SuccessResult(files_modified=[init_sh_path])
        
    except Exception as e:
        print(f"❌ Error adding animated banner: {e}")
        class ErrorResult:
            def __init__(self, error_msg):
                self.success = False
                self.message = error_msg
        
        return ErrorResult(f"Failed to add animated banner: {str(e)}")