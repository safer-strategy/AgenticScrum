# MCP API Key Setup Guide

## Security First

This guide ensures your API keys remain secure while being accessible to MCP servers.

### Prerequisites
- Environment variable support in your shell
- Access to API keys (Perplexity, etc.)
- Claude Code installed and configured

### Setup Methods

#### Method 1: Shell Profile (Recommended)

Add API keys to your shell configuration file:

```bash
# For zsh (macOS default)
echo 'export PERPLEXITY_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'export PERPLEXITY_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Method 2: Project .env File

Create a `.env` file in your project root:

```bash
# Create .env file (already gitignored)
cat > .env << 'EOF'
# MCP Server API Keys
PERPLEXITY_API_KEY=your-perplexity-api-key-here

# Memory Configuration
MEMORY_BASE_PATH=.agent-memory
EOF
```

Then source it before running Claude Code:
```bash
source .env
claude-code
```

#### Method 3: Environment Modules (Advanced)

For teams with shared development environments:

```bash
# Create a module file
mkdir -p ~/.modules
cat > ~/.modules/agentic-scrum << 'EOF'
#%Module1.0
setenv PERPLEXITY_API_KEY "your-key-here"
setenv MEMORY_BASE_PATH ".agent-memory"
EOF

# Load the module
module load ~/.modules/agentic-scrum
```

### Verifying Your Setup

Run the verification script:

```bash
./init.sh verify-keys
```

Expected output:
```
✅ PERPLEXITY_API_KEY is set
✅ All required API keys are configured
```

### Security Best Practices

1. **Never Commit Keys**
   - The `.gitignore` is pre-configured to exclude all secret files
   - Run `git status` before committing to verify no secrets are staged

2. **Use Strong Keys**
   - Generate keys with maximum allowed length
   - Rotate keys regularly (quarterly recommended)

3. **Limit Key Permissions**
   - Create project-specific API keys when possible
   - Use read-only keys for search operations

4. **Secure Storage Options**
   - macOS: Use Keychain Access
   - Linux: Use secret-tool or pass
   - Windows: Use Windows Credential Manager

### Troubleshooting

#### Issue: "PERPLEXITY_API_KEY not found"

**Solution 1:** Check if the variable is set:
```bash
echo $PERPLEXITY_API_KEY
```

**Solution 2:** Ensure you've sourced your shell profile:
```bash
source ~/.zshrc  # or ~/.bashrc
```

#### Issue: "Invalid API key"

**Solution:** Verify your key at https://www.perplexity.ai/settings/api

#### Issue: Claude Code doesn't see environment variables

**Solution:** Launch Claude Code from the terminal where variables are set:
```bash
# Don't use GUI launcher, use terminal
claude-code
```

### Platform-Specific Notes

#### macOS
```bash
# Store in Keychain
security add-generic-password -a "$USER" -s "PERPLEXITY_API_KEY" -w "your-key-here"

# Retrieve from Keychain in .zshrc
export PERPLEXITY_API_KEY=$(security find-generic-password -a "$USER" -s "PERPLEXITY_API_KEY" -w)
```

#### Linux
```bash
# Store using secret-tool
echo -n "your-key-here" | secret-tool store --label="Perplexity API Key" service agentic-scrum key PERPLEXITY_API_KEY

# Retrieve in .bashrc
export PERPLEXITY_API_KEY=$(secret-tool lookup service agentic-scrum key PERPLEXITY_API_KEY)
```

#### Windows (PowerShell)
```powershell
# Store in Credential Manager
cmdkey /generic:PERPLEXITY_API_KEY /user:$env:USERNAME /pass:your-key-here

# Set in PowerShell profile
$env:PERPLEXITY_API_KEY = (cmdkey /list:PERPLEXITY_API_KEY | Select-String "Password").ToString().Split(":")[1].Trim()
```

### Next Steps

After setting up your API keys:

1. Run `./init.sh setup` to configure your project
2. Test MCP servers with `./init.sh test-mcp`
3. Read the [Memory Architecture Guide](MCP_MEMORY_ARCHITECTURE.md)

### Getting API Keys

- **Perplexity**: https://www.perplexity.ai/settings/api
  - Sign up for an account
  - Navigate to Settings → API
  - Generate a new API key
  - Current pricing: $5/1000 requests