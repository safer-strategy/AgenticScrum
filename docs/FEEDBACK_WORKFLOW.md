# Agent Feedback Loop Workflow

## Overview
This document describes the systematic process for collecting feedback and improving agent performance through iterative updates to persona rules and priming scripts.

## Workflow Steps

### 1. Initial Baseline (Week 1)
- Deploy agents with initial configurations
- Collect baseline metrics for all agents
- Document initial performance benchmarks

### 2. Active Monitoring (Ongoing)
- Automated metrics collection for every agent-generated file
- Manual code review feedback after each sprint
- Performance tracking dashboards

### 3. Weekly Review Process

#### Monday: Metrics Analysis
```bash
# Generate weekly reports
python scripts/generate_agent_reports.py --period 7

# Review automated metrics
python scripts/analyze_metrics.py --threshold-complexity 10 --threshold-coverage 85
```

#### Wednesday: Feedback Collection
- Team code review session
- Fill out feedback forms for significant issues
- Identify patterns across multiple agents

#### Friday: Configuration Updates
1. Run feedback analyzer:
   ```bash
   python scripts/update_agent_config.py analyze --agent deva_python
   ```

2. Review suggested updates
3. Test updates in dry-run mode:
   ```bash
   python scripts/update_agent_config.py apply --agent deva_python --dry-run
   ```

4. Apply updates after team review:
   ```bash
   python scripts/update_agent_config.py apply --agent deva_python --confirm
   ```

### 4. Sprint Retrospective Integration
- Include agent performance in sprint retrospectives
- Discuss effectiveness of recent updates
- Plan improvements for next sprint

## Feedback Categories

### 1. Code Quality Feedback
- **Metric**: Cyclomatic complexity > 10
- **Action**: Add rules for function decomposition
- **Example Update**:
  ```yaml
  rules:
    - "SPLIT functions exceeding 30 lines into smaller units"
    - "EXTRACT complex conditionals into named functions"
  ```

### 2. Testing Feedback
- **Metric**: Coverage < 85%
- **Action**: Enhance testing rules and examples
- **Example Update**:
  ```yaml
  rules:
    - "WRITE test cases for all public methods"
    - "INCLUDE edge case tests for boundary conditions"
    - "TEST error handling paths explicitly"
  ```

### 3. Performance Feedback
- **Metric**: Response time > 200ms
- **Action**: Add performance optimization rules
- **Example Update**:
  ```yaml
  rules:
    - "USE database query optimization techniques"
    - "IMPLEMENT pagination for large datasets"
    - "CACHE frequently accessed computed values"
  ```

### 4. Documentation Feedback
- **Metric**: Missing docstrings
- **Action**: Strengthen documentation requirements
- **Example Update**:
  ```yaml
  rules:
    - "DOCUMENT all function parameters with types and descriptions"
    - "INCLUDE usage examples in complex function docstrings"
    - "EXPLAIN non-obvious algorithms with inline comments"
  ```

## Metrics Dashboard

### Key Performance Indicators (KPIs)
1. **Code Quality Score**: Composite of complexity, lint score, and type checking
2. **Test Coverage**: Percentage of code covered by tests
3. **Defect Rate**: Bugs found per 1000 lines of code
4. **Documentation Completeness**: Percentage of functions with docstrings
5. **Performance Score**: Percentage of code meeting performance targets

### Tracking Template
```markdown
## Agent Performance Tracking - [Agent Name]

### Week of [Date]

| Metric | Target | Actual | Trend | Action |
|--------|--------|--------|-------|--------|
| Complexity | <10 | 8.5 | ↓ | Maintain |
| Coverage | >85% | 92% | ↑ | Celebrate |
| Lint Score | >9.0 | 8.7 | → | Improve |
| Type Check | 100% | 95% | ↓ | Fix |
| Doc Complete | 100% | 88% | ↑ | Monitor |

### Issues Identified
1. [Issue]: [Description]
   - Frequency: [X times this week]
   - Impact: [High/Medium/Low]
   - Proposed Rule: [New rule to add]

### Success Stories
1. [Achievement]: [Description]
   - Keep doing: [What worked well]
```

## Continuous Improvement Checklist

### Daily
- [ ] Review automated metrics alerts
- [ ] Flag any critical issues for immediate attention

### Weekly
- [ ] Generate and review performance reports
- [ ] Collect team feedback
- [ ] Update agent configurations based on feedback
- [ ] Test updated configurations

### Sprint (Bi-weekly)
- [ ] Comprehensive performance review
- [ ] Major configuration updates
- [ ] Update priming scripts with new patterns
- [ ] Share learnings with team

### Monthly
- [ ] Trend analysis across all agents
- [ ] Identify systemic improvements
- [ ] Update baseline benchmarks
- [ ] Plan major enhancements

## Best Practices for Feedback Integration

### 1. Incremental Updates
- Make small, focused changes
- Test each change in isolation
- Document the rationale for changes

### 2. Version Control
- Track all configuration changes in git
- Use meaningful commit messages
- Tag stable configurations

### 3. A/B Testing
- Run multiple agent configurations in parallel
- Compare performance metrics
- Adopt the best performing configurations

### 4. Knowledge Sharing
- Document successful rule patterns
- Share effective priming scripts
- Create a library of proven configurations

## Example: Complete Feedback Cycle

### Step 1: Issue Identified
```
Issue: DeveloperAgent frequently creates functions without error handling
Impact: Production errors not gracefully handled
Frequency: 15 occurrences this week
```

### Step 2: Feedback Form
```yaml
issue:
  type: "missing_error_handling"
  severity: "high"
  description: "API endpoints lack try-except blocks"
  example_file: "api/users.py"
  line_numbers: [45, 67, 89]
```

### Step 3: Rule Creation
```yaml
# Added to persona_rules.yaml
rules:
  - "ALWAYS wrap database operations in try-except blocks"
  - "ALWAYS catch specific exceptions (not bare except)"
  - "ALWAYS log errors with context for debugging"
  - "ALWAYS return meaningful error messages to users"
```

### Step 4: Priming Update
```markdown
# Added to priming_script.md
## Error Handling Pattern
Always follow this pattern for database operations:

```python
try:
    result = db.query(Model).filter(Model.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Resource not found")
    return result
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Database error occurred")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="An unexpected error occurred")
```
```

### Step 5: Validation
- Test the updated agent on similar tasks
- Verify error handling is now included
- Monitor for regression in other areas

### Step 6: Documentation
```markdown
## Configuration Update Log

### Date: 2024-01-15
**Agent**: deva_python
**Issue**: Missing error handling
**Changes**: Added 4 error handling rules
**Result**: 100% of new endpoints include proper error handling
**Status**: ✅ Successful
```

## Tools and Scripts

### 1. Feedback Collector
```bash
# Collect feedback from code review
python scripts/collect_feedback.py \
  --agent deva_python \
  --reviewer "John Doe" \
  --sprint 15
```

### 2. Metrics Analyzer
```bash
# Analyze agent performance metrics
python scripts/analyze_metrics.py \
  --agent deva_python \
  --period 30 \
  --output-format markdown
```

### 3. Config Updater
```bash
# Update agent configuration based on feedback
python scripts/update_agent_config.py \
  --agent deva_python \
  --feedback-period 14 \
  --auto-apply
```

### 4. Performance Monitor
```bash
# Real-time monitoring dashboard
python scripts/monitor_agents.py \
  --dashboard \
  --refresh-interval 300
```

## Success Metrics

### Short-term (1 month)
- 20% reduction in code review issues
- 15% improvement in test coverage
- 10% reduction in average complexity

### Medium-term (3 months)  
- 50% reduction in production bugs
- 30% improvement in development velocity
- 25% reduction in code review time

### Long-term (6 months)
- 90% first-time acceptance rate
- Self-improving agents requiring minimal manual updates
- Established patterns library for common scenarios