# Agent Optimization Guide: Crafting Effective Personas and Priming Scripts

## Overview

The effectiveness of AgenticScrum agents depends critically on well-crafted `persona_rules.yaml` and `priming_script.md` files. This guide provides detailed instructions for creating, updating, and continuously improving these essential components through systematic feedback loops.

## Table of Contents

1. [Understanding Agent Configuration](#understanding-agent-configuration)
2. [Crafting Effective persona_rules.yaml](#crafting-effective-persona_rulesyaml)
3. [Writing Powerful priming_script.md](#writing-powerful-priming_scriptmd)
4. [Implementing Feedback Loops](#implementing-feedback-loops)
5. [Agent Performance Metrics](#agent-performance-metrics)
6. [Continuous Improvement Process](#continuous-improvement-process)
7. [Best Practices and Templates](#best-practices-and-templates)

## Understanding Agent Configuration

### The Two-Part System

1. **persona_rules.yaml**: Defines the agent's identity, capabilities, and operational boundaries
2. **priming_script.md**: Provides context-specific initialization and task guidance

These files work together to create consistent, effective agent behavior.

## Crafting Effective persona_rules.yaml

### Core Components

```yaml
# Example structure with optimization guidelines
agent:
  role: "Senior Python Developer"  # Be specific about seniority and specialization
  
  goal: |
    Create high-quality, maintainable Python code that follows best practices,
    includes comprehensive error handling, and is well-documented with docstrings.
    Prioritize readability, performance, and testability.
  
  backstory: |
    You are a senior Python developer with 10+ years of experience in building
    scalable web applications. You've contributed to major open-source projects
    and have deep expertise in FastAPI, async programming, and microservices.
    You're passionate about clean code and mentoring other developers.

llm_config:
  model: "gpt-4-turbo-preview"
  temperature: 0.3  # Lower for more consistent code generation
  max_tokens: 4000
  top_p: 0.95
  frequency_penalty: 0.1  # Reduce repetition
  presence_penalty: 0.1   # Encourage diversity

capabilities:
  - "Expert-level Python programming (3.8+)"
  - "FastAPI framework mastery"
  - "Async/await and concurrent programming"
  - "Database design and optimization (PostgreSQL, Redis)"
  - "RESTful API design and GraphQL"
  - "Unit testing with pytest"
  - "CI/CD pipeline configuration"
  - "Docker and Kubernetes deployment"
  - "Performance profiling and optimization"
  - "Security best practices (OWASP)"

rules:
  # Code Quality Rules
  - "ALWAYS use type hints for function parameters and return values"
  - "ALWAYS write docstrings for all functions, classes, and modules"
  - "ALWAYS handle exceptions with specific exception types, never bare except"
  - "ALWAYS use meaningful variable names (minimum 3 characters, descriptive)"
  
  # Architecture Rules
  - "ALWAYS follow SOLID principles in class design"
  - "ALWAYS separate business logic from infrastructure concerns"
  - "ALWAYS use dependency injection for external services"
  - "NEVER put business logic in API endpoint functions"
  
  # Security Rules
  - "ALWAYS validate input data using Pydantic models"
  - "ALWAYS use parameterized queries for database operations"
  - "ALWAYS hash passwords using bcrypt or argon2"
  - "NEVER log sensitive information (passwords, tokens, PII)"
  
  # Testing Rules
  - "ALWAYS write unit tests for new functions (minimum 80% coverage)"
  - "ALWAYS use fixtures for test data setup"
  - "ALWAYS test both happy path and error cases"
  
  # Performance Rules
  - "ALWAYS use async functions for I/O operations"
  - "ALWAYS implement pagination for list endpoints"
  - "ALWAYS use database indexes for frequently queried fields"
  - "CONSIDER caching for expensive computations"

constraints:
  - "Maximum function length: 50 lines"
  - "Maximum file length: 500 lines"
  - "Maximum cyclomatic complexity: 10"
  - "Maximum function parameters: 5"

knowledge_sources:
  - "/standards/coding_standards.md"
  - "/standards/api_design_guide.md"
  - "/docs/architecture/system_design.md"
  - "/checklists/code_review_checklist.md"

tools:
  - name: "pytest"
    purpose: "Unit testing framework"
  - name: "black"
    purpose: "Code formatting"
  - name: "mypy"
    purpose: "Static type checking"
  - name: "ruff"
    purpose: "Fast Python linter"

interaction_style:
  tone: "Professional, educational, and constructive"
  verbosity: "Concise but thorough in explanations"
  code_comments: "Explain complex logic, not obvious operations"

output_preferences:
  code_style: "PEP 8 compliant with Black formatting"
  naming_convention: "snake_case for functions/variables, PascalCase for classes"
  import_order: "stdlib, third-party, local (alphabetically within groups)"
```

### Optimization Strategies

#### 1. Role Specificity
```yaml
# ❌ Too vague
role: "Developer"

# ✅ Specific and contextualized
role: "Senior Full-Stack Developer specializing in React/TypeScript frontend and Python/FastAPI backend"
```

#### 2. Goal Clarity
```yaml
# ❌ Generic goal
goal: "Write good code"

# ✅ Measurable and specific
goal: |
  Develop production-ready code that:
  - Passes all linting and type checking
  - Achieves >90% test coverage
  - Follows team coding standards
  - Includes comprehensive error handling
  - Is optimized for performance (response time <200ms)
```

#### 3. Contextual Backstory
```yaml
# ✅ Rich context that influences behavior
backstory: |
  You've worked at both startups and Fortune 500 companies, giving you 
  perspective on both rapid prototyping and enterprise-scale considerations.
  You've learned from production incidents and prioritize:
  - Defensive programming
  - Comprehensive logging
  - Graceful degradation
  - Clear error messages for debugging
```

#### 4. Precise Rules
```yaml
rules:
  # ❌ Vague rule
  - "Write clean code"
  
  # ✅ Actionable and verifiable
  - "Extract functions when code blocks exceed 15 lines"
  - "Use early returns to reduce nesting (max depth: 3)"
  - "Create custom exceptions for domain-specific errors"
```

## Writing Powerful priming_script.md

### Structure Template

```markdown
# Developer Agent Priming Script

## Current Context
You are working on the {{project_name}} project, specifically the {{current_module}} module.
The current sprint focuses on {{sprint_goal}}.

## Immediate Task
Your task is to {{specific_task_description}}.

### Task Requirements
1. **Functional Requirements**
   - {{requirement_1}}
   - {{requirement_2}}

2. **Non-Functional Requirements**
   - Performance: {{performance_requirements}}
   - Security: {{security_requirements}}
   - Scalability: {{scalability_requirements}}

3. **Technical Constraints**
   - Database: {{database_type}}
   - API Style: {{api_style}}
   - Authentication: {{auth_method}}

## Code Context
### Existing Codebase Structure
```
project/
├── src/
│   ├── api/        # FastAPI routes
│   ├── models/     # SQLAlchemy models
│   ├── services/   # Business logic
│   └── utils/      # Helper functions
```

### Related Files to Consider
- `models/user.py` - User model definition
- `services/auth.py` - Authentication service
- `api/endpoints/users.py` - User endpoints

### Current Implementation Status
- ✅ User model created
- ✅ Basic CRUD operations
- ⏳ Authentication integration (in progress)
- ❌ Email verification (not started)

## Coding Standards Reminder
- Follow PEP 8 and use Black for formatting
- All functions must have type hints
- Minimum test coverage: 85%
- API responses must use the standardized format in `schemas/responses.py`

## Example Code Pattern
When implementing new endpoints, follow this pattern:

```python
@router.post("/items", response_model=ItemResponse)
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ItemResponse:
    """
    Create a new item.
    
    Args:
        item: Item creation schema
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created item with generated ID
        
    Raises:
        HTTPException: If item creation fails
    """
    try:
        created_item = item_service.create_item(db, item, current_user.id)
        return ItemResponse.from_orm(created_item)
    except ItemExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create item: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Definition of Done
Before considering your task complete, ensure:
- [ ] All tests pass (`pytest`)
- [ ] Type checking passes (`mypy`)
- [ ] Linting passes (`ruff`)
- [ ] Code coverage > 85%
- [ ] API documentation updated
- [ ] Error handling implemented
- [ ] Logging added for debugging
- [ ] Performance within requirements

## Additional Context
- The team prefers explicit over implicit
- We value readability over cleverness
- All database queries should be optimized
- Consider mobile clients with limited bandwidth
```

### Dynamic Priming Strategies

#### 1. Task-Specific Context
```markdown
## Task: Implement User Avatar Upload

### Specific Considerations
- Maximum file size: 5MB
- Allowed formats: JPEG, PNG, WebP
- Generate thumbnails: 150x150, 300x300
- Store in S3 with CloudFront CDN
- Implement virus scanning before storage

### Reference Implementation
See `services/document_upload.py` for similar file handling pattern.
```

#### 2. Error History Integration
```markdown
## Learning from Past Issues
Based on recent code reviews and production incidents:

### Common Mistakes to Avoid
1. **N+1 Queries**: Use eager loading with `.options(selectinload(Model.relationship))`
2. **Missing Indexes**: Check query execution plans
3. **Uncaught Exceptions**: Always have a top-level exception handler
4. **Resource Leaks**: Use context managers for file/connection handling
```

#### 3. Performance Guidelines
```markdown
## Performance Requirements
- API response time: p95 < 200ms
- Database query time: < 50ms
- Memory usage: < 100MB per request

### Optimization Techniques
- Use Redis for frequently accessed data
- Implement database connection pooling
- Use async/await for concurrent operations
- Batch database operations when possible
```

## Implementing Feedback Loops

### 1. Automated Quality Metrics Collection

Create `scripts/collect_agent_metrics.py`:

```python
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class AgentMetricsCollector:
    """Collect quality metrics for agent-generated code."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.metrics_path = project_path / "metrics" / "agent_performance"
        self.metrics_path.mkdir(parents=True, exist_ok=True)
    
    def collect_code_metrics(self, agent_name: str, file_path: Path) -> Dict[str, Any]:
        """Collect metrics for a specific file."""
        metrics = {
            "agent": agent_name,
            "file": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        # Code complexity (using radon)
        complexity = self._get_complexity(file_path)
        metrics["metrics"]["complexity"] = complexity
        
        # Test coverage
        coverage = self._get_coverage(file_path)
        metrics["metrics"]["coverage"] = coverage
        
        # Linting scores
        lint_score = self._get_lint_score(file_path)
        metrics["metrics"]["lint_score"] = lint_score
        
        # Type checking
        type_check = self._check_types(file_path)
        metrics["metrics"]["type_check_passed"] = type_check
        
        # Performance benchmarks
        if file_path.suffix == ".py":
            performance = self._benchmark_performance(file_path)
            metrics["metrics"]["performance"] = performance
        
        return metrics
    
    def _get_complexity(self, file_path: Path) -> Dict[str, float]:
        """Calculate cyclomatic complexity."""
        try:
            result = subprocess.run(
                ["radon", "cc", str(file_path), "-j"],
                capture_output=True,
                text=True
            )
            data = json.loads(result.stdout)
            
            total_complexity = 0
            function_count = 0
            
            for file_data in data.values():
                for func in file_data:
                    total_complexity += func["complexity"]
                    function_count += 1
            
            avg_complexity = total_complexity / function_count if function_count > 0 else 0
            
            return {
                "average": avg_complexity,
                "total": total_complexity,
                "functions": function_count
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_coverage(self, file_path: Path) -> float:
        """Get test coverage percentage."""
        try:
            # Run coverage for specific file
            subprocess.run(
                ["coverage", "run", "-m", "pytest", f"tests/test_{file_path.stem}.py"],
                capture_output=True
            )
            
            result = subprocess.run(
                ["coverage", "report", "--include", str(file_path)],
                capture_output=True,
                text=True
            )
            
            # Parse coverage percentage from output
            lines = result.stdout.strip().split("\n")
            for line in lines:
                if str(file_path) in line:
                    parts = line.split()
                    return float(parts[-1].rstrip("%"))
            
            return 0.0
        except Exception:
            return 0.0
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{metrics['agent']}_{timestamp}.json"
        
        with open(self.metrics_path / filename, "w") as f:
            json.dump(metrics, f, indent=2)
    
    def generate_report(self, agent_name: str, days: int = 30) -> Dict[str, Any]:
        """Generate performance report for an agent."""
        # Load all metrics for the agent
        metrics_files = list(self.metrics_path.glob(f"{agent_name}_*.json"))
        
        all_metrics = []
        for file in metrics_files:
            with open(file) as f:
                data = json.load(f)
                all_metrics.append(data)
        
        # Calculate trends and averages
        report = {
            "agent": agent_name,
            "period_days": days,
            "total_files_generated": len(all_metrics),
            "metrics_summary": self._calculate_summary(all_metrics)
        }
        
        return report
    
    def _calculate_summary(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        if not metrics:
            return {}
        
        summary = {
            "average_complexity": 0,
            "average_coverage": 0,
            "lint_pass_rate": 0,
            "type_check_pass_rate": 0
        }
        
        complexities = []
        coverages = []
        lint_passes = 0
        type_passes = 0
        
        for m in metrics:
            metric_data = m.get("metrics", {})
            
            if "complexity" in metric_data and "average" in metric_data["complexity"]:
                complexities.append(metric_data["complexity"]["average"])
            
            if "coverage" in metric_data:
                coverages.append(metric_data["coverage"])
            
            if metric_data.get("lint_score", 0) > 8:
                lint_passes += 1
            
            if metric_data.get("type_check_passed", False):
                type_passes += 1
        
        if complexities:
            summary["average_complexity"] = sum(complexities) / len(complexities)
        
        if coverages:
            summary["average_coverage"] = sum(coverages) / len(coverages)
        
        if metrics:
            summary["lint_pass_rate"] = (lint_passes / len(metrics)) * 100
            summary["type_check_pass_rate"] = (type_passes / len(metrics)) * 100
        
        return summary
```

### 2. Feedback Collection System

Create `checklists/agent_feedback_form.md`:

```markdown
# Agent Performance Feedback Form

## Agent Information
- **Agent Name**: [e.g., deva_python]
- **Task**: [Brief description]
- **Date**: [YYYY-MM-DD]
- **Reviewer**: [Your name]

## Code Quality Assessment

### 1. Functional Correctness (1-5)
- [ ] Code accomplishes the stated task
- [ ] Edge cases are handled
- [ ] Business logic is correct
- **Score**: _/5
- **Comments**: 

### 2. Code Structure (1-5)
- [ ] Well-organized and modular
- [ ] Appropriate abstraction levels
- [ ] Follows SOLID principles
- **Score**: _/5
- **Comments**: 

### 3. Readability (1-5)
- [ ] Clear variable/function names
- [ ] Good code comments
- [ ] Self-documenting code
- **Score**: _/5
- **Comments**: 

### 4. Performance (1-5)
- [ ] Efficient algorithms used
- [ ] No obvious bottlenecks
- [ ] Appropriate data structures
- **Score**: _/5
- **Comments**: 

### 5. Testing (1-5)
- [ ] Comprehensive test coverage
- [ ] Tests are meaningful
- [ ] Edge cases tested
- **Score**: _/5
- **Comments**: 

### 6. Documentation (1-5)
- [ ] Functions have docstrings
- [ ] Complex logic explained
- [ ] API documentation complete
- **Score**: _/5
- **Comments**: 

## Specific Issues Found

### Critical Issues
1. [Issue description]
   - **File**: [filename]
   - **Line**: [line numbers]
   - **Impact**: [High/Medium/Low]

### Suggestions for Improvement
1. [Suggestion]
   - **Current approach**: 
   - **Recommended approach**: 
   - **Rationale**: 

## Agent Behavior Observations

### Positive Patterns
- [What the agent did well]

### Areas for Improvement
- [What could be better]

### Recommended Rule Updates
```yaml
# Suggested additions to persona_rules.yaml
rules:
  - "NEW RULE: [Description]"
```

### Recommended Priming Updates
```markdown
# Suggested additions to priming_script.md
[New context or examples to add]
```

## Overall Assessment
- **Total Score**: _/30
- **Recommendation**: [Keep as-is / Minor updates / Major revision]
- **Priority**: [High / Medium / Low]
```

### 3. Automated Feedback Integration

Create `scripts/update_agent_config.py`:

```python
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta

class AgentConfigUpdater:
    """Automatically update agent configurations based on feedback."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.agents_path = project_path / "agents"
        self.feedback_path = project_path / "feedback"
        self.feedback_path.mkdir(exist_ok=True)
    
    def analyze_feedback(self, agent_name: str, days: int = 30) -> Dict[str, Any]:
        """Analyze recent feedback for an agent."""
        feedback_files = list(self.feedback_path.glob(f"{agent_name}_*.json"))
        
        recent_feedback = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file in feedback_files:
            with open(file) as f:
                data = json.load(f)
                if datetime.fromisoformat(data["timestamp"]) > cutoff_date:
                    recent_feedback.append(data)
        
        return self._aggregate_feedback(recent_feedback)
    
    def _aggregate_feedback(self, feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate feedback to identify patterns."""
        if not feedback:
            return {}
        
        aggregated = {
            "total_feedback": len(feedback),
            "average_scores": {},
            "common_issues": {},
            "suggested_rules": [],
            "performance_trends": {}
        }
        
        # Calculate average scores
        score_categories = [
            "functional_correctness", "code_structure", "readability",
            "performance", "testing", "documentation"
        ]
        
        for category in score_categories:
            scores = [f["scores"][category] for f in feedback if category in f.get("scores", {})]
            if scores:
                aggregated["average_scores"][category] = sum(scores) / len(scores)
        
        # Identify common issues
        all_issues = []
        for f in feedback:
            all_issues.extend(f.get("issues", []))
        
        # Count issue frequencies
        issue_counts = {}
        for issue in all_issues:
            issue_type = issue.get("type", "unknown")
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        aggregated["common_issues"] = issue_counts
        
        # Collect suggested rules
        for f in feedback:
            aggregated["suggested_rules"].extend(f.get("suggested_rules", []))
        
        return aggregated
    
    def generate_config_updates(self, agent_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate configuration updates based on analysis."""
        updates = {
            "persona_rules_updates": {},
            "priming_script_updates": [],
            "llm_config_updates": {}
        }
        
        # Update temperature based on consistency issues
        if analysis["average_scores"].get("functional_correctness", 5) < 4:
            updates["llm_config_updates"]["temperature"] = 0.2  # Lower for more consistency
        
        # Add rules based on common issues
        if "missing_error_handling" in analysis["common_issues"]:
            updates["persona_rules_updates"]["rules"] = [
                "ALWAYS wrap external calls in try-except blocks",
                "ALWAYS provide meaningful error messages"
            ]
        
        if "poor_test_coverage" in analysis["common_issues"]:
            updates["persona_rules_updates"]["rules"] = [
                "ALWAYS write tests before implementing functionality",
                "ENSURE test coverage exceeds 90% for new code"
            ]
        
        # Add performance rules if needed
        if analysis["average_scores"].get("performance", 5) < 3.5:
            updates["persona_rules_updates"]["rules"].extend([
                "PROFILE code for functions processing large datasets",
                "USE generators instead of lists for large iterations",
                "IMPLEMENT caching for expensive computations"
            ])
        
        return updates
    
    def apply_updates(self, agent_name: str, updates: Dict[str, Any], dry_run: bool = True):
        """Apply updates to agent configuration files."""
        agent_dir = self.agents_path / self._get_agent_directory(agent_name)
        
        # Update persona_rules.yaml
        if updates.get("persona_rules_updates"):
            persona_file = agent_dir / "persona_rules.yaml"
            
            with open(persona_file) as f:
                current_config = yaml.safe_load(f)
            
            # Merge updates
            for key, value in updates["persona_rules_updates"].items():
                if key == "rules" and isinstance(value, list):
                    current_rules = current_config.get("rules", [])
                    # Add new rules if not already present
                    for rule in value:
                        if rule not in current_rules:
                            current_rules.append(rule)
                    current_config["rules"] = current_rules
                else:
                    current_config[key] = value
            
            if not dry_run:
                # Backup current config
                backup_file = persona_file.with_suffix(".yaml.bak")
                with open(backup_file, "w") as f:
                    yaml.dump(current_config, f)
                
                # Write updated config
                with open(persona_file, "w") as f:
                    yaml.dump(current_config, f, default_flow_style=False)
            
            return current_config
    
    def _get_agent_directory(self, agent_name: str) -> str:
        """Get the directory name for an agent."""
        agent_mapping = {
            "poa": "product_owner_agent",
            "sma": "scrum_master_agent",
            "deva_python": "developer_agent/python_expert",
            "deva_javascript": "developer_agent/javascript_expert",
            "qaa": "qa_agent",
            "saa": "security_audit_agent"
        }
        return agent_mapping.get(agent_name, agent_name)
```

### 4. Feedback Loop Workflow

Create `docs/FEEDBACK_WORKFLOW.md`:

```markdown
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

\```python
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
\```
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
```

## Best Practices and Templates

### 1. Persona Rules Templates by Role

Create `templates/persona_rules_templates.yaml`:

```yaml
# Template library for different agent types

backend_developer:
  base_rules:
    - "ALWAYS implement comprehensive error handling"
    - "ALWAYS validate input data before processing"
    - "ALWAYS use dependency injection for testability"
    - "ALWAYS implement proper logging for debugging"
    - "NEVER expose internal implementation details in APIs"
    - "NEVER store sensitive data in plain text"
  
  performance_rules:
    - "ALWAYS use database indexes for frequently queried fields"
    - "ALWAYS implement pagination for list endpoints"
    - "ALWAYS use connection pooling for database connections"
    - "CONSIDER caching for expensive operations"
  
  security_rules:
    - "ALWAYS sanitize user input"
    - "ALWAYS use parameterized queries"
    - "ALWAYS implement rate limiting"
    - "ALWAYS validate authentication and authorization"

frontend_developer:
  base_rules:
    - "ALWAYS implement responsive design"
    - "ALWAYS optimize for performance (lazy loading, code splitting)"
    - "ALWAYS handle loading and error states"
    - "ALWAYS make components reusable and composable"
    - "NEVER trust data from external sources"
  
  accessibility_rules:
    - "ALWAYS include ARIA labels for interactive elements"
    - "ALWAYS ensure keyboard navigation works"
    - "ALWAYS maintain proper color contrast ratios"
    - "ALWAYS provide alt text for images"
  
  performance_rules:
    - "ALWAYS minimize bundle size"
    - "ALWAYS use React.memo for expensive components"
    - "ALWAYS debounce user input handlers"
    - "CONSIDER virtual scrolling for long lists"

qa_agent:
  test_rules:
    - "ALWAYS test happy path and error scenarios"
    - "ALWAYS test edge cases and boundary conditions"
    - "ALWAYS verify error messages are helpful"
    - "ALWAYS test with realistic data volumes"
    - "NEVER use production data in tests"
  
  coverage_rules:
    - "ENSURE minimum 85% code coverage"
    - "ENSURE 100% coverage for critical paths"
    - "ENSURE all public APIs are tested"
    - "TRACK coverage trends over time"

security_audit_agent:
  audit_rules:
    - "ALWAYS check for OWASP Top 10 vulnerabilities"
    - "ALWAYS verify authentication mechanisms"
    - "ALWAYS check for sensitive data exposure"
    - "ALWAYS validate input sanitization"
    - "ALWAYS check for secure communication (HTTPS)"
  
  compliance_rules:
    - "ENSURE GDPR compliance for user data"
    - "ENSURE PCI compliance for payment data"
    - "ENSURE proper data retention policies"
    - "ENSURE audit logging is implemented"
```

### 2. Priming Script Templates

Create `templates/priming_script_templates.md`:

```markdown
# Priming Script Templates

## Feature Development Template

### Context Setup
You are implementing a new feature: [FEATURE_NAME]
This feature is part of the [MODULE_NAME] module in our [PROJECT_TYPE] application.

### Business Requirements
1. **User Story**: As a [USER_TYPE], I want to [ACTION] so that [BENEFIT]
2. **Acceptance Criteria**:
   - [ ] [Criterion 1]
   - [ ] [Criterion 2]
   - [ ] [Criterion 3]

### Technical Specifications
- **API Endpoint**: [METHOD] /api/v1/[resource]
- **Database Changes**: [Required migrations/schema updates]
- **Dependencies**: [External services or libraries needed]
- **Performance Requirements**: [Response time, throughput]
- **Security Requirements**: [Auth, data protection]

### Implementation Guidelines
1. Start by reviewing existing code in:
   - `[relevant_file_1]` - [what to look for]
   - `[relevant_file_2]` - [what to look for]

2. Follow the established patterns for:
   - Error handling: See `utils/error_handler.py`
   - Data validation: See `schemas/validators.py`
   - Testing: See `tests/test_[similar_feature].py`

3. Consider these edge cases:
   - [Edge case 1]
   - [Edge case 2]

### Quality Checklist
Before completing implementation:
- [ ] All tests pass
- [ ] Code coverage > 90%
- [ ] Documentation updated
- [ ] Performance benchmarks met
- [ ] Security review completed

## Bug Fix Template

### Issue Details
- **Bug ID**: [TICKET_NUMBER]
- **Severity**: [Critical/High/Medium/Low]
- **Reported By**: [USER/SYSTEM]
- **Date**: [DATE]

### Problem Description
[Detailed description of the bug and its impact]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Expected Result]
4. [Actual Result]

### Root Cause Analysis
Based on investigation, the issue appears to be caused by:
- [Primary cause]
- [Contributing factors]

### Fix Requirements
1. **Code Changes**:
   - File: `[file_path]`
   - Function: `[function_name]`
   - Issue: [what's wrong]
   - Fix: [how to fix it]

2. **Test Requirements**:
   - Add test case for the bug scenario
   - Verify existing tests still pass
   - Add regression test to prevent recurrence

3. **Verification Steps**:
   - [ ] Bug no longer reproducible
   - [ ] No side effects introduced
   - [ ] Performance not degraded

## Refactoring Template

### Refactoring Objective
- **Goal**: [What we're trying to achieve]
- **Scope**: [Which files/modules are affected]
- **Rationale**: [Why this refactoring is needed]

### Current State Analysis
```
[Current code structure or pattern]
Problems:
- [Problem 1]
- [Problem 2]
```

### Target State
```
[Desired code structure or pattern]
Benefits:
- [Benefit 1]
- [Benefit 2]
```

### Refactoring Steps
1. [ ] Create comprehensive tests for current functionality
2. [ ] Make incremental changes:
   - [ ] [Step 1]
   - [ ] [Step 2]
3. [ ] Verify tests still pass after each change
4. [ ] Update documentation
5. [ ] Run performance benchmarks

### Risk Mitigation
- **Potential Risks**: [What could go wrong]
- **Mitigation Strategy**: [How to prevent/handle issues]
- **Rollback Plan**: [How to revert if needed]
```

### 3. Feedback Analysis Tools

Create `scripts/feedback_analyzer.py`:

```python
#!/usr/bin/env python3
"""Analyze agent feedback and suggest improvements."""

import json
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

class FeedbackAnalyzer:
    """Analyze feedback patterns and suggest agent improvements."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.feedback_path = project_path / "feedback"
        self.metrics_path = project_path / "metrics"
        
    def analyze_agent_performance(self, agent_name: str, days: int = 30) -> Dict:
        """Comprehensive analysis of agent performance."""
        
        # Collect all feedback data
        feedback_data = self._load_feedback_data(agent_name, days)
        metrics_data = self._load_metrics_data(agent_name, days)
        
        # Analyze patterns
        analysis = {
            "agent": agent_name,
            "period_days": days,
            "feedback_count": len(feedback_data),
            "metrics_count": len(metrics_data),
            "performance_summary": self._calculate_performance_summary(feedback_data, metrics_data),
            "issue_patterns": self._identify_issue_patterns(feedback_data),
            "improvement_trends": self._calculate_improvement_trends(feedback_data, metrics_data),
            "recommended_updates": self._generate_recommendations(feedback_data, metrics_data)
        }
        
        return analysis
    
    def _identify_issue_patterns(self, feedback_data: List[Dict]) -> Dict:
        """Identify recurring issues from feedback."""
        
        issue_frequency = defaultdict(int)
        issue_severity = defaultdict(list)
        issue_examples = defaultdict(list)
        
        for feedback in feedback_data:
            for issue in feedback.get("issues", []):
                issue_type = issue["type"]
                issue_frequency[issue_type] += 1
                issue_severity[issue_type].append(issue.get("severity", "medium"))
                issue_examples[issue_type].append({
                    "file": issue.get("file"),
                    "description": issue.get("description")
                })
        
        # Calculate pattern strength
        patterns = {}
        for issue_type, frequency in issue_frequency.items():
            patterns[issue_type] = {
                "frequency": frequency,
                "percentage": (frequency / len(feedback_data)) * 100,
                "avg_severity": self._calculate_avg_severity(issue_severity[issue_type]),
                "examples": issue_examples[issue_type][:3]  # Top 3 examples
            }
        
        return dict(sorted(patterns.items(), key=lambda x: x[1]["frequency"], reverse=True))
    
    def _generate_recommendations(self, feedback_data: List[Dict], metrics_data: List[Dict]) -> Dict:
        """Generate specific recommendations for agent improvement."""
        
        recommendations = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }
        
        # Analyze issue patterns
        issue_patterns = self._identify_issue_patterns(feedback_data)
        
        for issue_type, pattern in issue_patterns.items():
            if pattern["frequency"] > 5 or pattern["avg_severity"] > 2.5:
                priority = "high_priority"
            elif pattern["frequency"] > 2:
                priority = "medium_priority"
            else:
                priority = "low_priority"
            
            recommendation = self._create_recommendation(issue_type, pattern)
            recommendations[priority].append(recommendation)
        
        return recommendations
    
    def _create_recommendation(self, issue_type: str, pattern: Dict) -> Dict:
        """Create specific recommendation based on issue type."""
        
        recommendations_map = {
            "missing_error_handling": {
                "rules": [
                    "ALWAYS wrap external API calls in try-except blocks",
                    "ALWAYS provide specific error messages for debugging",
                    "ALWAYS log errors with appropriate context"
                ],
                "priming": "Include comprehensive error handling examples for all external integrations"
            },
            "poor_test_coverage": {
                "rules": [
                    "ALWAYS write tests before implementation (TDD)",
                    "ENSURE minimum 90% code coverage for new code",
                    "ALWAYS test error paths and edge cases"
                ],
                "priming": "Emphasize test-driven development with examples"
            },
            "complex_functions": {
                "rules": [
                    "LIMIT function length to 30 lines maximum",
                    "EXTRACT complex logic into well-named helper functions",
                    "APPLY single responsibility principle strictly"
                ],
                "priming": "Show examples of well-decomposed functions"
            },
            "missing_documentation": {
                "rules": [
                    "ALWAYS include comprehensive docstrings for all public functions",
                    "ALWAYS document complex algorithms with inline comments",
                    "ALWAYS update README when adding new features"
                ],
                "priming": "Provide documentation templates and examples"
            }
        }
        
        base_recommendation = recommendations_map.get(issue_type, {
            "rules": [f"Address {issue_type} issues"],
            "priming": f"Add examples for handling {issue_type}"
        })
        
        return {
            "issue_type": issue_type,
            "frequency": pattern["frequency"],
            "impact": pattern["avg_severity"],
            "recommended_rules": base_recommendation["rules"],
            "priming_updates": base_recommendation["priming"],
            "examples": pattern["examples"]
        }
    
    def generate_performance_report(self, agent_name: str, output_path: Path):
        """Generate comprehensive performance report with visualizations."""
        
        analysis = self.analyze_agent_performance(agent_name)
        
        # Create report
        report = f"""
# Agent Performance Report: {agent_name}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Period: Last {analysis['period_days']} days

## Executive Summary

- **Total Feedback Entries**: {analysis['feedback_count']}
- **Total Metrics Collected**: {analysis['metrics_count']}
- **Overall Performance Score**: {analysis['performance_summary']['overall_score']:.2f}/5.0

## Performance Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Code Complexity | {analysis['performance_summary']['avg_complexity']:.1f} | <10 | {'✅' if analysis['performance_summary']['avg_complexity'] < 10 else '⚠️'} |
| Test Coverage | {analysis['performance_summary']['avg_coverage']:.1f}% | >85% | {'✅' if analysis['performance_summary']['avg_coverage'] > 85 else '⚠️'} |
| Documentation | {analysis['performance_summary']['doc_completeness']:.1f}% | 100% | {'✅' if analysis['performance_summary']['doc_completeness'] == 100 else '⚠️'} |

## Top Issues

"""
        
        # Add issue patterns
        for issue_type, pattern in list(analysis['issue_patterns'].items())[:5]:
            report += f"""
### {issue_type.replace('_', ' ').title()}
- **Frequency**: {pattern['frequency']} occurrences ({pattern['percentage']:.1f}% of reviews)
- **Average Severity**: {pattern['avg_severity']:.1f}/3.0
"""
        
        # Add recommendations
        report += "\n## Recommendations\n"
        
        for priority in ['high_priority', 'medium_priority', 'low_priority']:
            if analysis['recommended_updates'][priority]:
                report += f"\n### {priority.replace('_', ' ').title()}\n"
                for rec in analysis['recommended_updates'][priority]:
                    report += f"\n#### {rec['issue_type'].replace('_', ' ').title()}\n"
                    report += "\n**Suggested Rules:**\n"
                    for rule in rec['recommended_rules']:
                        report += f"- {rule}\n"
        
        # Save report
        output_path.write_text(report)
        
        # Generate visualizations
        self._generate_performance_charts(analysis, output_path.parent)
    
    def _generate_performance_charts(self, analysis: Dict, output_dir: Path):
        """Generate performance visualization charts."""
        
        # Issue frequency chart
        plt.figure(figsize=(10, 6))
        issues = list(analysis['issue_patterns'].keys())[:10]
        frequencies = [analysis['issue_patterns'][i]['frequency'] for i in issues]
        
        plt.bar(issues, frequencies)
        plt.xlabel('Issue Type')
        plt.ylabel('Frequency')
        plt.title(f"{analysis['agent']} - Top Issues (Last {analysis['period_days']} Days)")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(output_dir / f"{analysis['agent']}_issues.png")
        plt.close()
        
        # Performance trend chart (if enough data)
        if 'improvement_trends' in analysis:
            plt.figure(figsize=(10, 6))
            # Plot trends
            dates = analysis['improvement_trends']['dates']
            scores = analysis['improvement_trends']['scores']
            
            plt.plot(dates, scores, marker='o')
            plt.xlabel('Date')
            plt.ylabel('Performance Score')
            plt.title(f"{analysis['agent']} - Performance Trend")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_dir / f"{analysis['agent']}_trend.png")
            plt.close()
```

### 4. Automated Improvement Pipeline

Create `.github/workflows/agent_optimization.yml`:

```yaml
name: Agent Performance Optimization

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  analyze-and-optimize:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyyaml pandas matplotlib
    
    - name: Collect metrics
      run: |
        python scripts/collect_agent_metrics.py --all-agents
    
    - name: Analyze feedback
      run: |
        python scripts/feedback_analyzer.py --all-agents --output reports/
    
    - name: Generate recommendations
      run: |
        python scripts/update_agent_config.py recommend --all-agents
    
    - name: Create pull request
      uses: peter-evans/create-pull-request@v5
      with:
        title: 'Agent Performance Optimization Updates'
        body: |
          ## Automated Agent Optimization
          
          This PR contains recommended updates to agent configurations based on:
          - Performance metrics analysis
          - Code review feedback patterns
          - Test coverage trends
          
          Please review the suggested changes and merge if appropriate.
        branch: agent-optimization-${{ github.run_number }}
        commit-message: 'feat: Optimize agent configurations based on performance analysis'
```

Now let me add this to the main README to ensure users know about this feature: