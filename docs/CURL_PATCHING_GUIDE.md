# AgenticScrum Curl-Based Patching Guide

This guide covers the lightweight curl-based patching system that allows you to update AgenticScrum projects without requiring Git or full framework installation.

## Overview

The curl-based patching system provides:

- **Lightweight Updates**: Download only what you need
- **No Git Required**: Works in restricted environments
- **Safety First**: Automatic backups and rollback capability
- **Easy Distribution**: One-liner commands for common updates
- **Cross-Platform**: Works on Linux, macOS, and WSL

## Quick Start

### One-Liner Updates

For the most common updates, use these one-liner commands:

```bash
# Update init.sh with latest features
curl -fsSL https://raw.githubusercontent.com/safer-strategy/AgenticScrum/refs/heads/main/scripts/quick-init-update.sh | bash

# Add security training features
curl -fsSL https://raw.githubusercontent.com/safer-strategy/AgenticScrum/refs/heads/main/scripts/quick-security-update.sh | bash

# Add animated ASCII banner
curl -fsSL https://raw.githubusercontent.com/safer-strategy/AgenticScrum/refs/heads/main/scripts/quick-banner-update.sh | bash

# Install standalone patcher globally
curl -fsSL https://raw.githubusercontent.com/safer-strategy/AgenticScrum/refs/heads/main/scripts/quick-install-patcher.sh | bash
```

### Manual Download and Execute

For more control, download the main script first:

```bash
# Download the main patching script
curl -fsSL https://raw.githubusercontent.com/safer-strategy/AgenticScrum/refs/heads/main/download-patch-updates.sh -o patch-updater.sh
chmod +x patch-updater.sh

# Show available operations
./patch-updater.sh --help

# Apply specific updates
./patch-updater.sh init-sh-update
./patch-updater.sh security-update --dry-run
```

## Available Operations

### Core Operations

| Operation | Description | Project Context Required |
|-----------|-------------|-------------------------|
| `init-sh-update` | Update init.sh with latest framework integration | Yes |
| `animated-banner` | Add animated ASCII banner to init.sh | Yes |
| `add-animated-banner` | Alias for animated-banner | Yes |
| `mcp-config` | Update MCP configuration files | Yes |
| `security-update` | Add security training features | Yes |
| `update-security` | Alias for security-update | Yes |
| `background-agents` | Add background agent execution system | Yes |
| `add-background-agents` | Alias for background-agents | Yes |
| `core-scripts` | Download essential patching scripts | No |
| `standalone-installer` | Install agentic-patch globally | No |

### Utility Operations

| Operation | Description |
|-----------|-------------|
| `check-version` | Check current vs latest version |
| `backup-project` | Create full project backup |
| `restore-backup` | Restore from backup |
| `cleanup` | Remove temporary files and old backups |

## Command Line Options

```bash
./download-patch-updates.sh <operation> [options]

Options:
  --dry-run      Preview changes without applying them
  --force        Force apply patch even with warnings
  --help, -h     Show help and available operations
```

### Examples

```bash
# Preview what would be updated
./download-patch-updates.sh security-update --dry-run

# Force update even with warnings
./download-patch-updates.sh init-sh-update --force

# Check if updates are available
./download-patch-updates.sh check-version
```

## Safety Features

### Automatic Backups

The system automatically creates timestamped backups before making changes:

- **Backup Location**: `.agentic_patch_backup_YYYYMMDD_HHMMSS/`
- **What's Backed Up**: All files that will be modified
- **Retention**: Keeps last 5 backups, removes older ones during cleanup

### Rollback Procedure

If something goes wrong:

1. **Automatic Rollback**: Use the restore-backup operation
   ```bash
   ./download-patch-updates.sh restore-backup
   ```

2. **Manual Rollback**: Copy files from backup directory
   ```bash
   # Find your backup
   ls -la .agentic_patch_backup_*
   
   # Restore specific file
   cp .agentic_patch_backup_YYYYMMDD_HHMMSS/init.sh ./init.sh
   ```

### File Verification

Downloaded files are automatically verified for:

- **Minimum Size**: Ensures download completed
- **Content Type**: Detects HTML error pages
- **Integrity**: Basic sanity checks

## Project Context Detection

The system detects AgenticScrum projects by looking for:

- `agentic_config.yaml`
- `init.sh`
- `.mcp.json`

**Note**: Some operations work without project context (like `core-scripts` or `standalone-installer`).

## Security Considerations

### ⚠️ curl | bash Warning

When using one-liner commands, you're executing code directly from the internet. The script includes:

- **5-second delay** with security warning
- **HTTPS-only** downloads
- **SSL certificate verification**
- **Content verification** before execution

### Best Practices

1. **Review First**: Download and review scripts before execution
   ```bash
   curl -fsSL <script-url> > script.sh
   # Review script.sh
   chmod +x script.sh && ./script.sh
   ```

2. **Use Dry Run**: Preview changes first
   ```bash
   ./download-patch-updates.sh <operation> --dry-run
   ```

3. **Backup Before Major Changes**: 
   ```bash
   ./download-patch-updates.sh backup-project
   ```

4. **Verify Downloads**: The script automatically verifies file integrity

## Troubleshooting

### Common Issues

**Error: "Not in an AgenticScrum project directory"**
- Solution: Navigate to your project directory or use operations that don't require project context

**Error: "Failed to download"**
- Check internet connection
- Verify HTTPS access to GitHub
- Try again (includes automatic retry logic)

**Error: "No write permissions"**
- Run with appropriate permissions
- Check file/directory ownership

**Error: "Command not found: mapfile"**
- This affects cleanup of old backups only
- The main functionality still works
- Manually remove old `.agentic_patch_backup_*` directories

### Debug Mode

For troubleshooting, you can enable debug output:

```bash
set -x
./download-patch-updates.sh <operation>
set +x
```

### Network Issues

The script includes robust error handling for network issues:

- **Connection timeout**: 10 seconds
- **Total timeout**: 30 seconds  
- **Automatic retries**: 3 attempts with 1-second delay
- **Graceful fallback**: Clear error messages

## Advanced Usage

### Custom GitHub URL

Override the default GitHub URL if needed:

```bash
# Edit the script to change GITHUB_RAW_URL
GITHUB_RAW_URL="https://raw.githubusercontent.com/YourOrg/AgenticScrum/main"
```

### Batch Operations

Apply multiple operations in sequence:

```bash
#!/bin/bash
operations=("security-update" "background-agents" "animated-banner")

for op in "${operations[@]}"; do
    echo "Applying $op..."
    ./download-patch-updates.sh "$op"
done
```

### Integration with CI/CD

Use in automated environments:

```bash
# Non-interactive usage
export DEBIAN_FRONTEND=noninteractive

# Download and apply updates
curl -fsSL <script-url> | bash -s <operation>
```

## Files Created

The patching system creates these files in your project:

```
your-project/
├── .agentic_patch_backup_YYYYMMDD_HHMMSS/  # Backup directory
├── .last_backup                           # Points to latest backup
├── scripts/                               # Downloaded scripts
│   ├── patch-project-init.sh
│   ├── agentic-patch
│   └── animated_ascii_art.py
└── agents/                                # Security features
    └── saa/
        ├── persona_rules.yaml
        └── memory_patterns.yaml
```

## Migration from Git-Based Patching

If you're switching from the Git-based patching system:

1. **No conflicts**: Both systems can coexist
2. **Same operations**: Most operation names are compatible
3. **Backup compatibility**: Uses same backup naming convention
4. **Gradual transition**: Use curl-based for new deployments

## Version Checking

Stay up-to-date with version checking:

```bash
# Check for updates
./download-patch-updates.sh check-version

# Output shows:
# Current version: 1.0.0-beta.8
# Latest version: 1.0.0-beta.9
# ⚠️ Update available: 1.0.0-beta.8 -> 1.0.0-beta.9
```

## Contributing

To add new operations to the curl-based system:

1. **Add operation function** in `download-patch-updates.sh`
2. **Add to show_operations()** function
3. **Add to main() switch statement**
4. **Test thoroughly** with dry-run mode
5. **Document** in this guide

## Support

For issues with the curl-based patching system:

1. **Check this guide** for troubleshooting
2. **Use dry-run mode** to debug
3. **Report issues** with full error output
4. **Include system info** (OS, bash version, curl version)

---

**Remember**: Always backup your project before applying patches, especially in production environments!