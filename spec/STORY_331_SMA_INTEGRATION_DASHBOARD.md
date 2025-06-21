# STORY_331: SMA Integration and Monitoring Dashboard

**Date**: 2025-06-21  
**Priority**: P2 (Medium)  
**Story Points**: 5  
**Assigned to**: deva_python  
**Epic**: AUTONOMOUS_QA_VALIDATION_SYSTEM  
**Sprint**: Next  

## User Story

As a Scrum Master, I want real-time visibility into QA validation status so that I can monitor quality metrics and make informed decisions.

## Background

The Scrum Master Agent (SMA) needs comprehensive visibility into the autonomous QA validation system to effectively monitor quality metrics, track validation progress, and make data-driven decisions about sprint planning and team coordination. This story implements a monitoring dashboard and integration points for the SMA.

## Acceptance Criteria

1. **Real-Time QA Validation Status Display**
   - [ ] Show current validation queue status and progress
   - [ ] Display active validation sessions and their status
   - [ ] Present completed validations with pass/fail summary
   - [ ] Show validation backlog and estimated completion times
   - [ ] Provide agent utilization and performance metrics

2. **Bug Trend Analysis and Reporting**
   - [ ] Display bug discovery trends over time
   - [ ] Show bug severity distribution and patterns
   - [ ] Present bug resolution time metrics
   - [ ] Track bug recurrence and regression patterns
   - [ ] Generate weekly/monthly quality trend reports

3. **Quality Metrics Tracking Over Time**
   - [ ] Track overall quality score trends
   - [ ] Monitor code coverage evolution
   - [ ] Display performance benchmark trends
   - [ ] Show security vulnerability trends
   - [ ] Present test success rate metrics

4. **Agent Performance Monitoring**
   - [ ] Monitor QA agent productivity and efficiency
   - [ ] Track validation accuracy and false positive rates
   - [ ] Display agent workload distribution
   - [ ] Show agent specialization effectiveness
   - [ ] Monitor background agent health and uptime

5. **Sprint Planning Integration**
   - [ ] Integrate bugfix backlog with sprint planning
   - [ ] Provide quality-based story prioritization recommendations
   - [ ] Show quality impact on sprint goals
   - [ ] Display technical debt trends and recommendations
   - [ ] Generate capacity planning based on QA workload

6. **Automated Notifications and Alerts**
   - [ ] Send real-time alerts for critical bugs
   - [ ] Generate daily QA summary reports
   - [ ] Provide weekly quality trend analysis
   - [ ] Alert on quality threshold breaches
   - [ ] Notify of validation system issues

## Technical Implementation Details

### SMA Dashboard Architecture

```python
# sma_qa_dashboard.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

@dataclass
class QAMetrics:
    validation_queue_size: int
    active_validations: int
    completed_validations_today: int
    average_validation_time: float
    bugs_discovered_today: int
    bugs_resolved_today: int
    overall_quality_score: float
    agent_utilization: Dict[str, float]

@dataclass
class BugTrend:
    date: datetime
    critical_bugs: int
    high_bugs: int
    medium_bugs: int
    low_bugs: int
    total_bugs: int
    resolution_time_avg: float

class SMAQADashboard:
    """QA monitoring dashboard for the Scrum Master Agent."""
    
    def __init__(self):
        self.qa_data_collector = QADataCollector()
        self.metrics_calculator = MetricsCalculator()
        self.report_generator = ReportGenerator()
        
    async def get_current_status(self) -> Dict[str, Any]:
        """Get current QA validation system status."""
        
        # Collect current metrics
        current_metrics = await self.qa_data_collector.get_current_metrics()
        
        # Get queue status
        queue_status = await self.get_queue_status()
        
        # Get active validations
        active_validations = await self.get_active_validations()
        
        # Calculate quality indicators
        quality_indicators = await self.calculate_quality_indicators()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': current_metrics,
            'queue_status': queue_status,
            'active_validations': active_validations,
            'quality_indicators': quality_indicators,
            'agent_health': await self.get_agent_health_status()
        }
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get validation queue status."""
        pending_queue = await self.qa_data_collector.load_queue('pending_validation.json')
        active_queue = await self.qa_data_collector.load_queue('active_qa_sessions.json')
        bugfix_queue = await self.qa_data_collector.load_queue('bugfix_queue.json')
        
        return {
            'pending_validations': len(pending_queue.get('queue', [])),
            'active_validations': len(active_queue.get('active_sessions', [])),
            'bugfix_stories_queued': len(bugfix_queue.get('bugfix_stories', [])),
            'estimated_completion_time': self.calculate_estimated_completion_time(pending_queue),
            'queue_health': self.assess_queue_health(pending_queue, active_queue)
        }
    
    async def generate_bug_trend_analysis(self, days: int = 30) -> List[BugTrend]:
        """Generate bug trend analysis for the specified period."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        bug_trends = []
        current_date = start_date
        
        while current_date <= end_date:
            daily_bugs = await self.qa_data_collector.get_bugs_for_date(current_date)
            
            trend = BugTrend(
                date=current_date,
                critical_bugs=len([b for b in daily_bugs if b.severity == BugSeverity.CRITICAL]),
                high_bugs=len([b for b in daily_bugs if b.severity == BugSeverity.HIGH]),
                medium_bugs=len([b for b in daily_bugs if b.severity == BugSeverity.MEDIUM]),
                low_bugs=len([b for b in daily_bugs if b.severity == BugSeverity.LOW]),
                total_bugs=len(daily_bugs),
                resolution_time_avg=await self.calculate_avg_resolution_time(daily_bugs)
            )
            
            bug_trends.append(trend)
            current_date += timedelta(days=1)
        
        return bug_trends
```

### Quality Metrics Calculator

```python
class MetricsCalculator:
    """Calculates quality metrics and indicators."""
    
    async def calculate_overall_quality_score(self) -> float:
        """Calculate overall quality score based on multiple factors."""
        
        # Get component scores
        code_quality_score = await self.calculate_code_quality_score()
        test_coverage_score = await self.calculate_test_coverage_score()
        bug_density_score = await self.calculate_bug_density_score()
        performance_score = await self.calculate_performance_score()
        security_score = await self.calculate_security_score()
        
        # Weighted average
        weights = {
            'code_quality': 0.25,
            'test_coverage': 0.25,
            'bug_density': 0.20,
            'performance': 0.15,
            'security': 0.15
        }
        
        overall_score = (
            code_quality_score * weights['code_quality'] +
            test_coverage_score * weights['test_coverage'] +
            bug_density_score * weights['bug_density'] +
            performance_score * weights['performance'] +
            security_score * weights['security']
        )
        
        return min(100.0, max(0.0, overall_score))
    
    async def calculate_agent_productivity_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate productivity metrics for each QA agent."""
        agents = ['qaa', 'background_qa_runner']
        metrics = {}
        
        for agent in agents:
            agent_data = await self.qa_data_collector.get_agent_data(agent)
            
            metrics[agent] = {
                'validations_per_day': self.calculate_validations_per_day(agent_data),
                'average_validation_time': self.calculate_avg_validation_time(agent_data),
                'accuracy_rate': self.calculate_accuracy_rate(agent_data),
                'false_positive_rate': self.calculate_false_positive_rate(agent_data),
                'uptime_percentage': self.calculate_uptime_percentage(agent_data)
            }
        
        return metrics
```

### Report Generator

```python
class ReportGenerator:
    """Generates QA reports for the SMA."""
    
    async def generate_daily_summary(self) -> str:
        """Generate daily QA summary report."""
        today = datetime.utcnow().date()
        
        # Collect daily data
        daily_validations = await self.qa_data_collector.get_validations_for_date(today)
        daily_bugs = await self.qa_data_collector.get_bugs_for_date(today)
        daily_resolutions = await self.qa_data_collector.get_resolutions_for_date(today)
        
        report = f"""# Daily QA Summary - {today.isoformat()}

## Validation Activity
- **Completed Validations**: {len(daily_validations)}
- **Success Rate**: {self.calculate_success_rate(daily_validations):.1%}
- **Average Validation Time**: {self.calculate_avg_time(daily_validations):.1f} minutes

## Bug Activity
- **New Bugs Discovered**: {len(daily_bugs)}
- **Critical/High Priority**: {len([b for b in daily_bugs if b.severity in [BugSeverity.CRITICAL, BugSeverity.HIGH]])}
- **Bugs Resolved**: {len(daily_resolutions)}
- **Resolution Time Avg**: {self.calculate_avg_resolution_time(daily_resolutions):.1f} hours

## Quality Indicators
- **Overall Quality Score**: {await self.metrics_calculator.calculate_overall_quality_score():.1f}/100
- **Code Coverage**: {await self.get_code_coverage():.1%}
- **Performance Score**: {await self.get_performance_score():.1f}/100

## Agent Performance
{await self.format_agent_performance()}

## Recommendations
{await self.generate_recommendations()}
"""
        return report
    
    async def generate_weekly_trend_analysis(self) -> str:
        """Generate weekly quality trend analysis."""
        week_trends = await self.dashboard.generate_bug_trend_analysis(days=7)
        
        report = f"""# Weekly Quality Trend Analysis

## Bug Discovery Trends
{self.format_bug_trends(week_trends)}

## Quality Metrics Evolution
{await self.format_quality_evolution()}

## Agent Performance Trends
{await self.format_agent_trends()}

## Action Items
{await self.generate_action_items()}
"""
        return report
```

### SMA Integration

```python
class SMAIntegration:
    """Integrates QA dashboard with SMA agent persona."""
    
    async def update_sma_persona(self):
        """Update SMA persona with QA monitoring capabilities."""
        
        # Load current SMA persona
        sma_persona_file = Path("agents/sma/persona_rules.yaml")
        
        if sma_persona_file.exists():
            persona_content = sMA_persona_file.read_text()
            
            # Add QA monitoring capabilities
            qa_capabilities = [
                "QA validation status monitoring",
                "Quality metrics analysis and reporting",
                "Bug trend analysis and prediction",
                "Agent performance monitoring",
                "Quality-based sprint planning",
                "Automated QA report generation"
            ]
            
            qa_rules = [
                "MONITOR QA validation queue and agent performance daily",
                "REVIEW quality metrics and trends weekly",
                "ESCALATE critical bugs and quality issues immediately",
                "INTEGRATE quality metrics into sprint planning decisions",
                "GENERATE daily QA summary reports",
                "TRACK technical debt and quality improvement initiatives"
            ]
            
            # Update persona with QA integration
            updated_persona = self.add_qa_capabilities(persona_content, qa_capabilities, qa_rules)
            sma_persona_file.write_text(updated_persona)
```

## Integration Points

- **SMA Agent**: Extend existing SMA persona with QA monitoring capabilities
- **QA Infrastructure**: Read from QA queue and reporting systems
- **MCP Servers**: Use agent monitoring and queue management servers
- **Background Agents**: Monitor agent health and performance
- **Reporting System**: Generate automated reports and alerts

## Definition of Done

- [ ] Real-time QA status dashboard implemented
- [ ] Bug trend analysis and reporting functional
- [ ] Quality metrics tracking operational
- [ ] Agent performance monitoring working
- [ ] Sprint planning integration complete
- [ ] Automated notifications and alerts functional
- [ ] SMA persona updated with QA capabilities
- [ ] Report generation automated
- [ ] Comprehensive error handling and logging
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Documentation complete and accurate
- [ ] Code follows existing AgenticScrum coding standards
- [ ] All files added to git and committed

## Dependencies

- STORY_325: QA Infrastructure Setup
- STORY_329: Bug Detection and Report Generation
- STORY_330: Automated Bugfix Story Creation
- Existing SMA agent persona
- MCP monitoring infrastructure

## Success Metrics

- Dashboard response time: <2 seconds
- Metrics accuracy: >95%
- Report generation time: <30 seconds
- SMA integration: 100% functional
- Alert delivery: <60 seconds for critical issues