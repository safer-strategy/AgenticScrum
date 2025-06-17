# AgenticScrum Memory Architecture

## Overview

The memory system transforms stateless AI agents into learning entities that improve over time. Each agent maintains its own memory space while sharing critical project knowledge through a common memory pool.

## Core Concepts

### Memory Persistence
- **Problem**: Claude Code sessions are ephemeral - all context is lost between sessions
- **Solution**: JSONL-based memory files that persist across sessions
- **Benefit**: Agents learn from past experiences and improve their performance

### Memory Types

#### Agent-Specific Memories
- **Product Owner (POA)**: Requirements, decisions, stakeholder patterns
- **Scrum Master (SMA)**: Sprint data, impediments, team dynamics  
- **Developer (DEVA)**: Code patterns, solutions, refactoring decisions
- **QA Agent (QAA)**: Test strategies, bug patterns, quality metrics
- **Security Agent (SAA)**: Vulnerabilities, mitigations, security patterns

#### Shared Memories
- **Timeline**: Project events and milestones
- **Architecture**: System design decisions
- **Learnings**: Cross-agent insights

## Memory Schema

### Base Memory Structure
```json
{
  "timestamp": "2025-01-17T10:30:00Z",
  "type": "memory_type",
  "agent": "agent_name",
  "context": "relevant context",
  "content": {
    // Type-specific fields
  },
  "outcome": "what happened",
  "tags": ["relevant", "tags"],
  "metadata": {
    "session_id": "uuid",
    "relevance_score": 1.0
  }
}
```

### Type-Specific Schemas

#### Code Pattern (DEVA)
```json
{
  "type": "code_pattern",
  "language": "python",
  "pattern": "async database connection pooling",
  "solution": "asyncpg with connection pool size 20",
  "code_snippet": "pool = await asyncpg.create_pool(...)",
  "performance": "3x throughput improvement",
  "caveats": ["requires PostgreSQL 12+"],
  "reuse_count": 5
}
```

#### Requirement Pattern (POA)
```json
{
  "type": "requirement_pattern",
  "feature_area": "authentication",
  "pattern": "multi-factor authentication",
  "decision": "implement TOTP-based 2FA",
  "rationale": "balance security and UX",
  "stakeholders": ["security_team", "product_team"],
  "outcome": "reduced unauthorized access by 95%"
}
```

#### Bug Pattern (QAA)
```json
{
  "type": "bug_pattern",
  "category": "race_condition",
  "symptoms": ["intermittent test failures", "data corruption"],
  "root_cause": "missing transaction isolation",
  "detection_method": "concurrent load testing",
  "fix_pattern": "use SELECT FOR UPDATE",
  "prevention": "add locking to all critical sections"
}
```

## Memory Lifecycle

### 1. Creation
Agents store memories during task execution:
```yaml
# In persona_rules.yaml
memory_patterns:
  store:
    triggers:
      - "After implementing a solution"
      - "When a decision is made"
      - "After fixing a bug"
    what_to_store:
      - "Solution patterns that worked"
      - "Decision rationale"
      - "Problem-solution pairs"
```

### 2. Retrieval
Agents query memories before making decisions:
```yaml
memory_patterns:
  query:
    triggers:
      - "Before implementing similar feature"
      - "When facing familiar problem"
      - "During code review"
    search_by:
      - "Tags and keywords"
      - "Similarity to current context"
      - "Time relevance"
```

### 3. Evolution
Memories are scored and updated over time:
- **Relevance Decay**: 0.95 factor per day
- **Reuse Boost**: +0.1 score per reference
- **Outcome Adjustment**: Success +0.2, Failure -0.1

### 4. Pruning
Automatic cleanup based on relevance:
- **Aggressive**: Keep only highly relevant recent memories
- **Balanced**: Standard decay with moderate retention
- **Conservative**: Preserve most memories, slow decay

## Directory Structure

```
.agent-memory/
├── poa/                    # Product Owner memories
│   ├── main.jsonl         # Primary memory file
│   ├── requirements.jsonl  # Requirement patterns
│   └── decisions.jsonl     # Product decisions
├── sma/                    # Scrum Master memories  
│   ├── main.jsonl
│   ├── retrospectives.jsonl
│   └── impediments.jsonl
├── deva/                   # Developer memories
│   ├── main.jsonl
│   ├── patterns.jsonl
│   └── refactors.jsonl
├── qaa/                    # QA memories
│   ├── main.jsonl
│   ├── test-strategies.jsonl
│   └── bug-patterns.jsonl
├── saa/                    # Security memories
│   ├── main.jsonl
│   ├── vulnerabilities.jsonl
│   └── mitigations.jsonl
└── shared/                 # Cross-agent knowledge
    ├── timeline.jsonl
    └── architecture.jsonl
```

## MCP Integration

### Configuration
The memory MCP server is configured in `.mcp.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@itseasy21/mcp-knowledge-graph"],
      "env": {
        "MEMORY_FILE_PATH": "${PROJECT_ROOT}/.agent-memory/${AGENT_TYPE}/main.jsonl"
      }
    }
  }
}
```

### Agent Access
Each agent accesses its own memory namespace:
- POA sees: `.agent-memory/poa/` + shared
- DEVA sees: `.agent-memory/deva/` + shared
- Etc.

## Best Practices

### 1. Memory Quality
- **Be Specific**: Include concrete details, not vague descriptions
- **Include Context**: Why was this decision made?
- **Track Outcomes**: Did the solution work? What was the impact?
- **Use Tags**: Enable cross-cutting searches

### 2. Memory Hygiene
- **Regular Pruning**: Run monthly to prevent bloat
- **Backup Important Memories**: Export critical learnings
- **Review Patterns**: Analyze what agents are learning

### 3. Privacy & Security
- **No Secrets**: Never store API keys, passwords, or PII
- **Sanitize Data**: Remove customer-specific information
- **Access Control**: Memories stay within project boundaries

## Memory Management Tools

### Export/Import
```bash
# Export all memories
python scripts/memory_export.py --output backup.json

# Export specific agent memories
python scripts/memory_export.py --agent deva --output deva_memories.json

# Import memories
python scripts/memory_import.py --input backup.json --merge
```

### Analysis
```bash
# Analyze memory patterns
python scripts/memory_analyze.py --report analysis.md

# Visualize memory growth
python scripts/memory_analyze.py --visualize charts/

# Agent-specific analysis
python scripts/memory_analyze.py --agent qaa --days 30
```

### Pruning
```bash
# Dry run to see what would be pruned
python scripts/memory_prune.py --analyze

# Balanced pruning (recommended)
python scripts/memory_prune.py --strategy balanced --execute

# Aggressive pruning for space constraints
python scripts/memory_prune.py --strategy aggressive --max-age-days 30 --execute
```

## Performance Considerations

### Memory Size
- Target: <100MB per project after 6 months
- Typical memory entry: 200-500 bytes
- Capacity: ~200k-500k memories per project

### Query Performance
- JSONL format: O(n) full scan
- Optimization: Keep active memories small
- Future: Index generation for large memory sets

### Backup Strategy
- Daily: Incremental memory export
- Weekly: Full memory backup
- Monthly: Prune and optimize

## Troubleshooting

### Common Issues

#### "Memory not persisting between sessions"
- Check: Is `.agent-memory/` directory created?
- Verify: MCP server configuration in `.mcp.json`
- Test: Manual memory write/read

#### "Agents not learning from past experiences"
- Check: Are memories being created? (`ls -la .agent-memory/*/`)
- Verify: Agent persona includes memory patterns
- Review: Memory quality and relevance

#### "Memory files growing too large"
- Run: `python scripts/memory_analyze.py --report`
- Execute: `python scripts/memory_prune.py --strategy balanced --execute`
- Consider: More aggressive pruning strategy

## Future Enhancements

### Planned Features
1. **Semantic Search**: Vector embeddings for similarity search
2. **Memory Clustering**: Automatic pattern detection
3. **Cross-Project Learning**: Shared learnings across projects
4. **Memory Versioning**: Track memory evolution
5. **Intelligent Summarization**: Compress old memories into insights

### Research Areas
- Federated learning across agent teams
- Memory importance prediction
- Automatic memory organization
- Context-aware memory retrieval