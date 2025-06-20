# Story 324: Create Curl-Based Patch Downloader for Easy Updates

**Epic**: E009 - Patching System Robustness
**Story Points**: 3
**Priority**: P1 (Critical)
**Status**: Ready
**Sprint**: Current (Immediate Deployment)
**Assigned To**: deva_python

## Story Description

As a developer using AgenticScrum in production,
I want to download and apply patches using curl without cloning the entire repository,
So that I can quickly update my projects with the latest framework improvements.

## Problem Statement

Currently, updating AgenticScrum projects requires either:
1. Having the full framework installed locally
2. Cloning the entire repository
3. Manual file copying

This creates barriers for users who:
- Don't have Git installed
- Work in restricted environments
- Want lightweight, selective updates
- Need to patch multiple projects quickly

## Acceptance Criteria

1. **Main Download Script**
   - [ ] Create `download-patch-updates.sh` that uses curl to fetch files
   - [ ] Support multiple patch operations (core-scripts, init-sh-update, etc.)
   - [ ] Create automatic backups before applying changes
   - [ ] Provide clear progress indicators and error handling

2. **Patch Operations**
   - [ ] `core-scripts` - Download essential patching scripts
   - [ ] `patch-system` - Full patching system for framework updates
   - [ ] `init-sh-update` - Update init.sh with latest features
   - [ ] `background-agents` - Background agent system files
   - [ ] `security-update` - Security patches and SAA updates
   - [ ] `animated-banner` - Animated ASCII banner files
   - [ ] `standalone-installer` - Install agentic-patch globally

3. **One-Liner Updates**
   - [ ] Create quick curl commands for common updates
   - [ ] Ensure scripts work with `curl | bash` pattern safely
   - [ ] Add appropriate security warnings and verification

4. **Safety Features**
   - [ ] Automatic backup creation with timestamps
   - [ ] Dry-run capability to preview changes
   - [ ] Verification of downloaded files
   - [ ] Rollback instructions if issues occur

## Technical Implementation

### 1. Main Download Script Structure
```bash
#!/bin/bash
# AgenticScrum Remote Patch Downloader

GITHUB_RAW_URL="https://raw.githubusercontent.com/Anthropic/AgenticScrum/main"
BACKUP_DIR=".agentic_patch_backup_$(date +%Y%m%d_%H%M%S)"
TEMP_DIR=".agentic_patch_temp"

# Download function with error handling
download_file() {
    local remote_path="$1"
    local local_path="$2"
    curl -fsSL "${GITHUB_RAW_URL}/${remote_path}" -o "$local_path"
}

# Backup existing files
backup_file() {
    [[ -f "$1" ]] && cp "$1" "$BACKUP_DIR/$1"
}
```

### 2. Quick Update Scripts
```bash
# quick-init-update.sh
curl -fsSL $GITHUB_RAW_URL/scripts/patch-project-init.sh | bash

# quick-security-update.sh  
curl -fsSL $GITHUB_RAW_URL/scripts/apply-security-patches.sh | bash
```

### 3. Version Checking
```bash
# Check latest version
LATEST_VERSION=$(curl -fsSL $GITHUB_RAW_URL/VERSION)
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
```

## File Organization

```
/
├── download-patch-updates.sh      # Main download script
├── scripts/
│   ├── quick-init-update.sh      # One-liner init.sh updater
│   ├── quick-security-update.sh  # One-liner security updater
│   └── quick-banner-update.sh    # One-liner banner updater
└── docs/
    └── CURL_PATCHING_GUIDE.md    # Documentation
```

## Testing Requirements

1. **Download Tests**
   - Test each patch operation type
   - Verify file integrity after download
   - Test with missing/invalid URLs
   - Test backup creation

2. **Application Tests**
   - Apply patches to test projects
   - Verify idempotency
   - Test rollback procedures
   - Test in restricted environments

3. **Security Tests**
   - Verify HTTPS usage
   - Test malformed URL handling
   - Validate downloaded content
   - Test permission requirements

## Documentation

Create comprehensive guide covering:
- Available patch operations
- One-liner commands
- Backup and rollback procedures
- Troubleshooting common issues
- Security considerations

## Definition of Done

- [ ] Main download script created and tested
- [ ] All patch operations implemented
- [ ] One-liner scripts created
- [ ] Backup/restore functionality verified
- [ ] Documentation complete
- [ ] Scripts work on Linux/macOS/WSL
- [ ] No Git dependency required
- [ ] Clear error messages for all failure modes

## Dependencies

- curl (standard on most systems)
- bash
- Basic Unix tools (mkdir, cp, chmod)

## Security Considerations

- Always use HTTPS for downloads
- Verify GitHub SSL certificates
- Create backups before modifications
- Warn users about curl | bash risks
- Consider adding checksum verification

## Notes

- Critical for production deployments
- Enables air-gapped environment updates
- Reduces barrier to entry for patches
- Consider CDN distribution in future

## Implementation Priority

1. Create basic download script
2. Implement init-sh-update operation (most requested)
3. Add remaining operations
4. Create one-liner scripts
5. Document and distribute