#!/bin/bash

# Pre-commit hook to detect potential API keys and secrets
# Copy this to .git/hooks/pre-commit and make executable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Patterns to detect potential secrets
SECRET_PATTERNS=(
    # API Keys
    'api[-_]?key.*=.*["\x27][a-zA-Z0-9_\-]{20,}'
    'apikey.*=.*["\x27][a-zA-Z0-9_\-]{20,}'
    'api[-_]?secret.*=.*["\x27][a-zA-Z0-9_\-]{20,}'
    'api[-_]?token.*=.*["\x27][a-zA-Z0-9_\-]{20,}'
    
    # Specific providers
    'perplexity[-_]?api[-_]?key.*=.*["\x27]pplx-[a-zA-Z0-9]{48}'
    'anthropic[-_]?api[-_]?key.*=.*["\x27]sk-ant-[a-zA-Z0-9]{48}'
    'openai[-_]?api[-_]?key.*=.*["\x27]sk-[a-zA-Z0-9]{48}'
    
    # Generic secrets
    'password.*=.*["\x27][^"\x27]{8,}'
    'secret.*=.*["\x27][^"\x27]{8,}'
    'private[-_]?key.*=.*["\x27][^"\x27]{20,}'
    
    # AWS
    'aws_access_key_id.*=.*["\x27][A-Z0-9]{20}'
    'aws_secret_access_key.*=.*["\x27][a-zA-Z0-9/+=]{40}'
    
    # Other cloud providers
    'google[-_]?api[-_]?key.*=.*["\x27]AIza[a-zA-Z0-9\-_]{35}'
    'azure[-_]?api[-_]?key.*=.*["\x27][a-zA-Z0-9]{32}'
)

# Files to exclude from scanning
EXCLUDE_PATTERNS=(
    '*.sample'
    '*.example'
    '*.md'
    '.gitignore'
    'package-lock.json'
    'yarn.lock'
    'poetry.lock'
    'Gemfile.lock'
)

# Check if file should be excluded
should_exclude() {
    local file=$1
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            return 0
        fi
    done
    return 1
}

# Main check
echo -e "${YELLOW}Checking for potential secrets in staged files...${NC}"

found_secrets=false
files_with_secrets=()

# Get list of staged files
staged_files=$(git diff --cached --name-only)

for file in $staged_files; do
    # Skip if file is deleted
    if [ ! -f "$file" ]; then
        continue
    fi
    
    # Skip excluded files
    if should_exclude "$file"; then
        continue
    fi
    
    # Check each pattern
    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -Ei "$pattern" "$file" > /dev/null 2>&1; then
            found_secrets=true
            files_with_secrets+=("$file")
            echo -e "${RED}Potential secret found in: $file${NC}"
            grep -nEi "$pattern" "$file" | head -3
            echo ""
            break
        fi
    done
done

if [ "$found_secrets" = true ]; then
    echo -e "${RED}⚠️  COMMIT BLOCKED: Potential secrets detected!${NC}"
    echo ""
    echo "Files containing potential secrets:"
    printf '%s\n' "${files_with_secrets[@]}" | sort -u
    echo ""
    echo "To fix this:"
    echo "1. Remove the actual secret values from the files"
    echo "2. Use environment variables instead (e.g., \${PERPLEXITY_API_KEY})"
    echo "3. Add sensitive files to .gitignore"
    echo "4. If this is a false positive, you can bypass with: git commit --no-verify"
    echo ""
    exit 1
else
    echo -e "${GREEN}✓ No secrets detected in staged files${NC}"
fi

exit 0