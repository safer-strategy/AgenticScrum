# MCP Integration Guide for AgenticScrum

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Feature Details](#feature-details)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

## Overview

Model Context Protocol (MCP) integration enhances AgenticScrum agents with:
- **Persistent Memory**: Agents learn and improve over time
- **Web Search**: Access to current information via Perplexity
- **Secure Configuration**: API keys managed safely

### Why MCP?

Claude Code's native limitations:
- ❌ No memory between sessions
- ❌ Limited web search (US-only)
- ❌ No cross-project learning
- ❌ Stateless agents

MCP-enhanced capabilities:
- ✅ Persistent agent memories
- ✅ Advanced web search globally
- ✅ Learning from past experiences
- ✅ Continuous improvement

## Prerequisites

1. **Claude Code**: Latest version installed
2. **Node.js**: v16+ for MCP servers
3. **API Keys**: Perplexity API key (optional but recommended)
4. **Operating System**: macOS, Linux, or Windows with WSL

## Quick Start

### 1. Create New Project with MCP

```bash
# Interactive setup (recommended for beginners)
./init.sh new

# Or direct CLI with MCP features
agentic-scrum-setup init \
  --project-name "MyAIProject" \
  --language python \
  --framework fastapi \
  --agents poa,sma,deva_python,qaa,saa \
  --enable-mcp \
  --enable-search
```

### 2. Configure API Keys

```bash
# Add to your shell profile
echo 'export PERPLEXITY_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc

# Verify setup
./init.sh verify-keys
```

### 3. Test MCP Integration

```bash
# Test memory server
./init.sh test-mcp memory

# Test search server (if API key configured)
./init.sh test-mcp search
```

### 4. Start Using MCP Features

Your agents now have:
- Memory that persists across sessions
- Ability to search the web for current information
- Learning capabilities that improve over time

## Feature Details

### Memory System

#### How It Works
1. Each agent has its own memory directory
2. Memories are stored in JSONL format
3. MCP server provides memory access to Claude Code
4. Agents query past experiences before making decisions

#### Memory Types
- **Code Patterns**: Reusable solutions
- **Bug Fixes**: Problem-solution pairs
- **Decisions**: Rationale and outcomes
- **Requirements**: Patterns and preferences

#### Example Memory Flow
```
User: "Implement user authentication"
  ↓
POA: Queries memory for past auth requirements
  ↓
POA: Finds JWT pattern worked well before
  ↓
POA: Creates user story with JWT recommendation
  ↓
POA: Stores new memory about this decision
```

### Search Integration

#### Perplexity Search
- More comprehensive than Claude's native search
- Works globally (not US-only)
- Cached to minimize API costs
- Rate-limited for safety

#### Search Patterns by Agent
- **POA**: Market research, competitor analysis
- **DEVA**: Library updates, best practices
- **QAA**: Testing strategies, tool comparisons
- **SAA**: Security advisories, CVE database

#### Example Search Flow
```
User: "What's the best practice for Python async?"
  ↓
DEVA: Searches "python async best practices 2024"
  ↓
DEVA: Caches results in memory
  ↓
DEVA: Implements solution based on findings
  ↓
DEVA: Stores successful pattern for future use
```

### Memory Management

#### Automatic Features
- **Relevance Scoring**: Important memories stay longer
- **Deduplication**: Prevents redundant memories
- **Pruning**: Removes outdated information

#### Manual Tools
```bash
# View memory statistics
python scripts/memory_analyze.py --report

# Backup memories
python scripts/memory_export.py --output backups/$(date +%Y%m%d).json

# Prune old memories
python scripts/memory_prune.py --strategy balanced --execute
```

## Troubleshooting

### Common Issues

#### MCP Server Not Starting
```bash
# Check Node.js version
node --version  # Should be 16+

# Reinstall MCP servers
npm install -g @itseasy21/mcp-knowledge-graph perplexity-mcp

# Check server logs
claude-code --mcp-debug
```

#### Memory Not Persisting
1. Verify `.agent-memory/` exists
2. Check file permissions
3. Ensure MCP is enabled in `.mcp.json`

#### Search Not Working
1. Verify API key is set: `echo $PERPLEXITY_API_KEY`
2. Check rate limits aren't exceeded
3. Test API key: `curl -H "Authorization: Bearer $PERPLEXITY_API_KEY" https://api.perplexity.ai/test`

### Debug Commands

```bash
# Check memory files
find .agent-memory -name "*.jsonl" -exec wc -l {} \;

# View recent memories
tail -n 5 .agent-memory/*/main.jsonl | jq .

# Test memory write
echo '{"test": "memory"}' >> .agent-memory/shared/test.jsonl

# Check MCP configuration
cat .mcp.json | jq .
```

## Best Practices

### Memory Best Practices

1. **Quality over Quantity**
   - Store meaningful patterns, not every action
   - Include context and rationale
   - Track outcomes for learning

2. **Regular Maintenance**
   - Run memory analysis monthly
   - Prune memories quarterly
   - Backup before major changes

3. **Privacy First**
   - Never store secrets or credentials
   - Sanitize customer data
   - Keep memories project-specific

### Search Best Practices

1. **Efficient Searching**
   - Use specific queries
   - Check memory cache first
   - Batch related searches

2. **Cost Management**
   - Monitor API usage
   - Use caching effectively
   - Set agent rate limits

3. **Result Validation**
   - Verify search results are current
   - Cross-reference multiple sources
   - Store validated patterns

### Integration Tips

1. **Gradual Adoption**
   - Start with memory only
   - Add search when comfortable
   - Expand agent by agent

2. **Team Workflow**
   - Share memory backups
   - Document learned patterns
   - Review agent improvements

3. **Performance Monitoring**
   - Track memory size growth
   - Monitor search API costs
   - Measure agent improvement

## Advanced Configuration

### Custom Memory Schemas

Create specialized memory types in `persona_rules.yaml`:

```yaml
memory_patterns:
  custom_types:
    deployment_outcome:
      schema:
        - environment: string
        - version: string
        - issues: array
        - resolution: string
        - downtime: number
      triggers:
        - "After deployment completes"
        - "When rollback occurs"
```

### Memory Plugins

Extend memory capabilities:

```python
# Custom memory analyzer
from scripts.memory_analyze import MemoryAnalyzer

class CustomAnalyzer(MemoryAnalyzer):
    def analyze_deployment_patterns(self):
        # Custom analysis logic
        pass
```

### Search Optimization

Configure search caching and limits:

```yaml
# In agent persona files
search_config:
  cache_ttl: 86400  # 24 hours
  max_queries_per_session: 10
  preferred_sources:
    - "official_docs"
    - "stackoverflow"
    - "github"
```

## Appendix

### Useful Links
- [MCP Specification](https://modelcontextprotocol.io)
- [Perplexity API Docs](https://docs.perplexity.ai)
- [AgenticScrum Memory Examples](https://github.com/yourusername/agentic-scrum/tree/main/examples/memory)

### Glossary
- **MCP**: Model Context Protocol
- **JSONL**: JSON Lines format (one JSON object per line)
- **Relevance Score**: Metric for memory importance
- **Memory Pruning**: Removing outdated memories
- **Search Cache**: Stored search results to avoid repeated API calls