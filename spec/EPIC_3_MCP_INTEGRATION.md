# Epic 03: MCP Memory and Search Integration

**Epic ID:** 03  
**Epic Name:** MCP Memory and Search Integration  
**Epic Goal:** Enhance AgenticScrum agents with persistent memory and advanced search capabilities through Model Context Protocol (MCP) servers, transforming stateless agents into learning, evolving AI team members.

## Overview

This epic addresses fundamental limitations in Claude Code's native capabilities by integrating:

1. **Memory/Knowledge Graph**: Persistent agent memory across sessions
2. **Perplexity Search**: Advanced web search capabilities for real-time information
3. **Secure Configuration**: API key management without exposure

### Native Claude Code Limitations
- No persistent memory between sessions
- Limited web search (US-only, basic)
- No cross-project learning
- No pattern recognition across time

### MCP Enhancement Benefits
- Agents learn from past experiences
- Project-specific memory preservation
- Enhanced research capabilities
- Pattern recognition and reuse
- Institutional knowledge building

---

# Story 301: Secure API Key Management

**Epic:** 03 - MCP Memory and Search Integration  
**Story Points:** 2  
**Priority:** P1 (High - Security foundation required before any MCP integration)  
**Status:** ✅ Completed  
**Created:** 2025-01-16  
**Completed:** 2025-01-17  

## 📋 User Story

**As a developer**, I want to configure MCP servers with API keys securely, **so that** sensitive credentials are never exposed in version control while remaining easily accessible to the MCP servers.

**⚠️ CRITICAL REQUIREMENTS:**
- **NEVER commit API keys** to version control
- **Use environment variables** for all secrets
- **Provide clear setup documentation** for users

## 🎯 Acceptance Criteria

### Security Implementation
- [ ] **Updated .gitignore**: Add comprehensive patterns for secret files
- [ ] **Environment Variable Support**: MCP configurations use ${VAR} syntax
- [ ] **Sample Files**: Create .sample versions showing structure without keys
- [ ] **Setup Script Enhancement**: init.sh prompts for and validates API keys

### Configuration Templates
- [ ] **MCP Secrets Template**: Create .mcp-secrets.json.sample
- [ ] **Environment File Template**: Create .env.sample with required variables
- [ ] **User Instructions**: Clear documentation for API key setup

### Validation and Safety
- [ ] **Pre-commit Hook**: Add script to scan for potential API key exposure
- [ ] **Key Validation**: init.sh checks for required environment variables
- [ ] **Secure Storage Guide**: Documentation for various OS/shell configurations

## 🔧 Technical Implementation Details

### File Modification Plan

#### 1. Update .gitignore Template
**File:** `agentic_scrum_setup/templates/.gitignore.j2`
Add:
```gitignore
# API Keys and Secrets
.env
.env.local
.env.*.local
*.key
*_api_key*
.mcp-secrets.json
.secrets/
```

#### 2. Create MCP Secrets Template
**New File:** `agentic_scrum_setup/templates/claude/.mcp-secrets.json.sample`
```json
{
  "mcpServers": {
    "perplexity-mcp": {
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
        "PERPLEXITY_MODEL": "sonar"
      }
    }
  }
}
```

#### 3. Create Environment Template
**New File:** `agentic_scrum_setup/templates/.env.sample`
```bash
# MCP Server API Keys
PERPLEXITY_API_KEY=your-perplexity-api-key-here

# Memory Configuration
MEMORY_BASE_PATH=.agent-memory
```

#### 4. Update init.sh Template
**File:** `agentic_scrum_setup/templates/common/init.sh.j2`
Add API key validation function:
```bash
check_api_keys() {
    local missing_keys=()
    
    # Check for Perplexity API key if search is enabled
    if [[ -f ".mcp-secrets.json" ]] && grep -q "perplexity-mcp" .mcp-secrets.json; then
        if [[ -z "${PERPLEXITY_API_KEY}" ]]; then
            missing_keys+=("PERPLEXITY_API_KEY")
        fi
    fi
    
    if [[ ${#missing_keys[@]} -gt 0 ]]; then
        echo "Missing required API keys:"
        printf '%s\n' "${missing_keys[@]}"
        echo ""
        echo "Please set these in your environment or .env file"
        return 1
    fi
    
    return 0
}
```

### Testing Requirements

#### Security Tests:
- [ ] Verify .gitignore prevents committing secret files
- [ ] Test environment variable substitution in MCP configs
- [ ] Validate pre-commit hook catches exposed keys
- [ ] Ensure init.sh properly validates API keys

---

# Story 302: Memory Directory Structure and MCP Configuration

**Epic:** 03 - MCP Memory and Search Integration  
**Story Points:** 3  
**Priority:** P1 (High - Core infrastructure for memory system)  
**Status:** ✅ Completed  
**Created:** 2025-01-16  
**Completed:** 2025-01-17  

## 📋 User Story

**As an AgenticScrum project**, I want a well-organized memory directory structure with MCP server configuration, **so that** each agent can maintain its own persistent memory while sharing common knowledge.

## 🎯 Acceptance Criteria

### Memory Structure
- [ ] **Project Memory Directory**: Create `.agent-memory/` in project root
- [ ] **Agent-Specific Directories**: Subdirectories for each agent type
- [ ] **Shared Memory Space**: Common directory for cross-agent knowledge
- [ ] **Memory File Format**: JSONL format for efficient append operations

### MCP Configuration
- [ ] **Memory Server Config**: Add memory MCP server to .mcp.json
- [ ] **Path Configuration**: Use project-relative paths for memory files
- [ ] **Server Initialization**: Ensure memory server starts correctly

### Project Integration
- [ ] **Setup Integration**: setup_core.py creates memory structure
- [ ] **Template Support**: Memory paths in templates use variables
- [ ] **Initialization**: Memory files created with proper schemas

## 🔧 Technical Implementation Details

### Memory Directory Structure
```
project-root/
├── .agent-memory/              # Memory root (gitignored)
│   ├── poa/                    # Product Owner memories
│   │   ├── requirements.jsonl  # Requirement patterns
│   │   └── decisions.jsonl     # Product decisions
│   ├── sma/                    # Scrum Master memories
│   │   ├── retrospectives.jsonl # Sprint retrospectives
│   │   └── impediments.jsonl   # Impediment resolutions
│   ├── deva/                   # Developer memories
│   │   ├── patterns.jsonl      # Code patterns
│   │   └── refactors.jsonl     # Refactoring decisions
│   ├── qaa/                    # QA memories
│   │   ├── test-strategies.jsonl # Testing approaches
│   │   └── bug-patterns.jsonl   # Common bug types
│   ├── saa/                    # Security memories
│   │   ├── vulnerabilities.jsonl # Security issues
│   │   └── mitigations.jsonl    # Security fixes
│   └── shared/                 # Cross-agent knowledge
│       ├── timeline.jsonl       # Project timeline
│       └── architecture.jsonl   # Architectural decisions
```

### File Modification Plan

#### 1. Update .mcp.json Template
**File:** `agentic_scrum_setup/templates/claude/.mcp.json.j2`
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@itseasy21/mcp-knowledge-graph"],
      "env": {
        "MEMORY_FILE_PATH": "${PROJECT_ROOT}/.agent-memory/{{ agent_type }}/main.jsonl"
      }
    }
  }
}
```

#### 2. Update setup_core.py
**File:** `agentic_scrum_setup/setup_core.py`
Add memory directory creation:
```python
def _create_memory_structure(self):
    """Create agent memory directory structure."""
    memory_root = self.project_path / '.agent-memory'
    
    # Agent-specific directories
    agent_dirs = ['poa', 'sma', 'deva', 'qaa', 'saa', 'shared']
    
    for agent_dir in agent_dirs:
        dir_path = memory_root / agent_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty JSONL files
        if agent_dir != 'shared':
            (dir_path / 'main.jsonl').touch()
```

---

# Story 303: Agent Memory Schemas and Patterns

**Epic:** 03 - MCP Memory and Search Integration  
**Story Points:** 3  
**Priority:** P1 (High - Defines how agents use memory)  
**Status:** ✅ Completed  
**Created:** 2025-01-16  
**Completed:** 2025-01-17  

## 📋 User Story

**As an AI agent**, I want structured memory schemas and query patterns, **so that** I can effectively store, retrieve, and learn from past experiences to improve my performance over time.

## 🎯 Acceptance Criteria

### Memory Schemas
- [ ] **POA Memory Schema**: Requirements, decisions, stakeholder feedback
- [ ] **SMA Memory Schema**: Sprint data, impediments, team dynamics
- [ ] **DEVA Memory Schema**: Code patterns, solutions, refactoring rationale
- [ ] **QAA Memory Schema**: Test strategies, bug patterns, quality metrics
- [ ] **SAA Memory Schema**: Vulnerabilities, fixes, security patterns

### Agent Persona Updates
- [ ] **Memory Instructions**: Add memory usage to each persona
- [ ] **Query Patterns**: Define when agents should query memory
- [ ] **Storage Patterns**: Define what agents should remember

### Cross-Agent Sharing
- [ ] **Shared Memory Schema**: Project timeline, decisions, learnings
- [ ] **Access Patterns**: Define when agents access shared memory
- [ ] **Conflict Resolution**: Handle conflicting memories

## 🔧 Technical Implementation Details

### Memory Schema Examples

#### POA Memory Entry
```json
{
  "timestamp": "2025-01-16T10:30:00Z",
  "type": "requirement_pattern",
  "context": "user_authentication",
  "pattern": "multi-factor authentication requested",
  "decision": "implement TOTP-based 2FA",
  "rationale": "balance between security and user experience",
  "outcome": "reduced unauthorized access by 95%",
  "tags": ["security", "authentication", "user_experience"]
}
```

#### DEVA Memory Entry
```json
{
  "timestamp": "2025-01-16T14:15:00Z",
  "type": "code_pattern",
  "language": "python",
  "pattern": "async database connection pooling",
  "solution": "asyncpg with connection pool size 20",
  "performance": "3x throughput improvement",
  "caveats": "requires PostgreSQL 12+",
  "tags": ["database", "performance", "async"]
}
```

### File Modification Plan

#### 1. Update POA Persona
**File:** `agentic_scrum_setup/templates/poa/persona_rules.yaml.j2`
Add memory section:
```yaml
memory_patterns:
  store:
    - "User story acceptance/rejection reasons"
    - "Stakeholder preference patterns"
    - "Requirement change patterns"
    - "Priority decision rationale"
  
  query:
    - "Before creating similar user stories"
    - "When prioritizing backlog items"
    - "During stakeholder discussions"
```

#### 2. Create Memory Query Functions
**New File:** `scripts/agent_memory_utils.py`
```python
class AgentMemory:
    def __init__(self, agent_type: str, project_path: str):
        self.agent_type = agent_type
        self.memory_path = Path(project_path) / '.agent-memory' / agent_type
    
    def remember(self, memory_type: str, content: dict):
        """Store a memory entry."""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': memory_type,
            **content
        }
        
    def recall(self, query: dict, limit: int = 10):
        """Retrieve relevant memories."""
        # Implementation for memory retrieval
```

---

# Story 304: Perplexity Search Integration

**Epic:** 03 - MCP Memory and Search Integration  
**Story Points:** 2  
**Priority:** P2 (Medium - Enhanced capability, not core requirement)  
**Status:** ✅ Completed  
**Created:** 2025-01-16  
**Completed:** 2025-01-17  
**Dependencies:** Story 301 (API Key Management)

## 📋 User Story

**As an AI agent**, I want access to current web information through Perplexity search, **so that** I can provide up-to-date information and discover best practices beyond my training data.

## 🎯 Acceptance Criteria

### Search Configuration
- [ ] **Perplexity MCP Setup**: Configure server in .mcp.json
- [ ] **API Key Security**: Use environment variable for API key
- [ ] **Model Selection**: Configure appropriate Perplexity model

### Agent Search Patterns
- [ ] **POA Searches**: Market research, competitor analysis
- [ ] **DEVA Searches**: Library updates, best practices
- [ ] **SAA Searches**: Security advisories, CVE database
- [ ] **Search Caching**: Store results in agent memory

### Rate Limiting
- [ ] **Usage Tracking**: Monitor API usage per agent
- [ ] **Rate Limits**: Implement per-agent rate limiting
- [ ] **Fallback Strategy**: Handle rate limit errors gracefully

## 🔧 Technical Implementation Details

### Search Use Cases by Agent

#### POA Search Patterns
```yaml
search_patterns:
  - "market analysis for {feature}"
  - "user feedback {product_category}"
  - "competitor features {domain}"
```

#### DEVA Search Patterns
```yaml
search_patterns:
  - "{library} latest version features"
  - "{language} best practices {year}"
  - "{framework} performance optimization"
```

### File Modification Plan

#### 1. Update .mcp.json Template
**File:** `agentic_scrum_setup/templates/claude/.mcp.json.j2`
```json
{
  "mcpServers": {
    "perplexity-mcp": {
      "command": "uvx",
      "args": ["perplexity-mcp"],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
        "PERPLEXITY_MODEL": "sonar"
      }
    }
  }
}
```

#### 2. Add Search Result Caching
**File:** Update agent memory schemas to include search results
```json
{
  "type": "search_result",
  "query": "python asyncio best practices 2024",
  "source": "perplexity",
  "timestamp": "2025-01-16T10:00:00Z",
  "results": [...],
  "used_in": "task_id_123"
}
```

---

# Story 305: Memory Management Utilities

**Epic:** 03 - MCP Memory and Search Integration  
**Story Points:** 2  
**Priority:** P2 (Medium - Maintenance and optimization tools)  
**Status:** To Do  
**Created:** 2025-01-16  
**Dependencies:** Story 302, 303

## 📋 User Story

**As a project maintainer**, I want memory management utilities, **so that** I can analyze agent learning patterns, export memories for backup, and optimize memory storage over time.

## 🎯 Acceptance Criteria

### Export/Import Tools
- [ ] **Memory Export**: Script to export memories by agent/date range
- [ ] **Memory Import**: Script to import memories from backup
- [ ] **Format Support**: JSON and CSV export formats

### Analysis Tools
- [ ] **Pattern Analysis**: Identify common patterns in memories
- [ ] **Memory Statistics**: Show memory usage by agent
- [ ] **Learning Curves**: Visualize agent improvement over time

### Optimization Tools
- [ ] **Memory Pruning**: Remove outdated/redundant memories
- [ ] **Memory Compression**: Compress old memories
- [ ] **Relevance Scoring**: Score and rank memory importance

## 🔧 Technical Implementation Details

### Script Implementations

#### 1. Memory Export Script
**New File:** `scripts/memory_export.py`
```python
#!/usr/bin/env python3
"""Export agent memories for backup or analysis."""

import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta

def export_memories(project_path: str, agent: str = None, 
                   days: int = None, output_format: str = 'json'):
    """Export memories based on criteria."""
    memory_root = Path(project_path) / '.agent-memory'
    
    # Implementation details...
```

#### 2. Memory Analysis Script
**New File:** `scripts/memory_analyze.py`
```python
#!/usr/bin/env python3
"""Analyze agent memory patterns and effectiveness."""

def analyze_patterns(memory_path: Path):
    """Identify common patterns in agent memories."""
    patterns = {}
    
    # Group memories by type, tag, outcome
    # Calculate frequency and success rates
    # Return pattern analysis
```

#### 3. Memory Pruning Script
**New File:** `scripts/memory_prune.py`
```python
#!/usr/bin/env python3
"""Prune outdated or redundant memories."""

RELEVANCE_DECAY = 0.95  # Daily decay factor
MIN_RELEVANCE_SCORE = 0.1  # Minimum score to keep

def calculate_relevance(memory: dict) -> float:
    """Calculate memory relevance score."""
    age_days = (datetime.now() - memory['timestamp']).days
    base_score = memory.get('usefulness', 1.0)
    return base_score * (RELEVANCE_DECAY ** age_days)
```

---

# Story 306: Documentation and Setup Guides

**Epic:** 03 - MCP Memory and Search Integration  
**Story Points:** 2  
**Priority:** P2 (Medium - User experience and adoption)  
**Status:** To Do  
**Created:** 2025-01-16  
**Dependencies:** Stories 301-305

## 📋 User Story

**As a new user**, I want comprehensive documentation for MCP integration setup and usage, **so that** I can quickly and securely configure memory and search capabilities for my AgenticScrum project.

## 🎯 Acceptance Criteria

### Setup Documentation
- [ ] **API Key Setup Guide**: Step-by-step secure configuration
- [ ] **MCP Installation Guide**: Prerequisites and installation steps
- [ ] **Troubleshooting Guide**: Common issues and solutions

### Architecture Documentation
- [ ] **Memory Architecture**: Explain memory system design
- [ ] **Search Integration**: Document search patterns and usage
- [ ] **Best Practices**: Guidelines for effective memory use

### Integration with Existing Docs
- [ ] **README Updates**: Add MCP features section
- [ ] **Tutorial Updates**: Include memory/search examples
- [ ] **CLAUDE.md Updates**: Add MCP-specific guidance

## 🔧 Technical Implementation Details

### Documentation Structure

#### 1. API Key Setup Guide
**New File:** `docs/MCP_API_SETUP.md`
```markdown
# MCP API Key Setup Guide

## Security First

This guide ensures your API keys remain secure while being accessible to MCP servers.

### Prerequisites
- Environment variable support in your shell
- Access to API keys (Perplexity, etc.)

### Setup Methods

#### Method 1: Shell Profile (Recommended)
```bash
# Add to ~/.zshrc or ~/.bashrc
export PERPLEXITY_API_KEY="your-key-here"
```

#### Method 2: Project .env File
```bash
# Create .env in project root (gitignored)
PERPLEXITY_API_KEY=your-key-here
```
...
```

#### 2. Memory Architecture Documentation
**New File:** `docs/MCP_MEMORY_ARCHITECTURE.md`
```markdown
# AgenticScrum Memory Architecture

## Overview

The memory system transforms stateless AI agents into learning entities...

## Memory Types

### Agent-Specific Memories
- **Product Owner**: Requirements, decisions, stakeholder patterns
- **Scrum Master**: Sprint data, impediments, team dynamics
...

## Memory Lifecycle

1. **Creation**: Agents store experiences during tasks
2. **Retrieval**: Agents query relevant memories before decisions
3. **Evolution**: Memories are scored and pruned over time
...
```

### Testing Requirements

#### Documentation Tests:
- [ ] All code examples are executable
- [ ] Setup steps work on macOS/Linux/Windows
- [ ] Links to other docs are valid
- [ ] Security warnings are prominent

---

## Implementation Roadmap

### Phase 1: Security Foundation (Story 301)
- Implement secure API key management
- Create templates and samples
- Update .gitignore patterns

### Phase 2: Core Infrastructure (Stories 302-303)
- Create memory directory structure
- Implement MCP configurations
- Define agent memory schemas

### Phase 3: Enhanced Capabilities (Story 304)
- Integrate Perplexity search
- Implement search caching
- Add rate limiting

### Phase 4: Maintenance Tools (Story 305)
- Create memory management scripts
- Implement analysis tools
- Add pruning capabilities

### Phase 5: Documentation (Story 306)
- Write comprehensive guides
- Update existing documentation
- Create troubleshooting resources

## Success Metrics

1. **Security**: Zero API key exposures in commits
2. **Memory Effectiveness**: Agents show measurable improvement over time
3. **Search Utility**: Reduced time to find current information
4. **User Adoption**: 80%+ projects enable MCP features
5. **Memory Efficiency**: <100MB memory storage per project after 6 months

---

## Notes

- All API keys must be managed through environment variables
- Memory files use JSONL format for efficiency
- Search results are cached to minimize API usage
- Memory pruning runs automatically based on relevance scores
- Cross-agent memory sharing enables team learning