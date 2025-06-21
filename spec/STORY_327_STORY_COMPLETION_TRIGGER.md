# STORY_327: Story Completion Trigger System

**Date**: 2025-06-21  
**Priority**: P1 (High)  
**Story Points**: 5  
**Assigned to**: deva_python  
**Epic**: AUTONOMOUS_QA_VALIDATION_SYSTEM  
**Sprint**: Current  

## User Story

As a system, I want to automatically detect when stories are completed so that QA validation can begin immediately.

## Background

The autonomous QA validation system needs to automatically detect when development stories are completed to trigger immediate validation. This system monitors the `spec/` directory for new or updated story files and automatically queues them for validation when they reach completion status.

## Acceptance Criteria

1. **File System Monitoring**
   - [ ] Monitor `spec/` directory for new/updated story files (.md files)
   - [ ] Detect file creation, modification, and movement events
   - [ ] Filter for story files using naming conventions (STORY_*.md)
   - [ ] Implement efficient file watching with minimal system resource usage

2. **Story Completion Detection**
   - [ ] Parse story markdown files to extract completion status
   - [ ] Identify completion indicators (e.g., "Status: Completed", "✅ Implemented")
   - [ ] Extract story metadata (ID, priority, assigned agent, completion date)
   - [ ] Validate story format and required fields

3. **Story Requirements Parsing**
   - [ ] Parse story requirements and acceptance criteria from markdown
   - [ ] Extract technical implementation details
   - [ ] Identify dependencies and prerequisites
   - [ ] Parse Definition of Done checklist items

4. **Automatic Queue Management**
   - [ ] Add completed stories to validation queue (`qa/queue/pending_validation.json`)
   - [ ] Assign unique validation IDs
   - [ ] Set appropriate priority based on story priority
   - [ ] Estimate validation duration based on story complexity

5. **Test Plan Generation**
   - [ ] Generate comprehensive test plans based on story content
   - [ ] Include acceptance criteria validation tests
   - [ ] Add regression tests for related functionality
   - [ ] Create performance and security test scenarios

6. **Integration with Background Agent System**
   - [ ] Integrate with existing background agent infrastructure
   - [ ] Trigger background QA agent when stories are queued
   - [ ] Provide story context and requirements to QA agents
   - [ ] Handle agent assignment and load balancing

## Technical Implementation Details

### File System Monitoring Architecture

```python
# story_completion_monitor.py
import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class StoryCompletionMonitor:
    """Monitors spec/ directory for completed stories and triggers QA validation."""
    
    def __init__(self, spec_dir: Path, qa_queue_dir: Path):
        self.spec_dir = spec_dir
        self.qa_queue_dir = qa_queue_dir
        self.observer = Observer()
        self.handler = StoryFileHandler(self)
        
    def start_monitoring(self):
        """Start monitoring the spec directory."""
        self.observer.schedule(self.handler, str(self.spec_dir), recursive=False)
        self.observer.start()
        logging.info(f"Started monitoring {self.spec_dir} for story completion")
    
    def stop_monitoring(self):
        """Stop monitoring the spec directory."""
        self.observer.stop()
        self.observer.join()
        logging.info("Stopped story completion monitoring")

class StoryFileHandler(FileSystemEventHandler):
    """Handles file system events for story files."""
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self.process_story_file(Path(event.src_path))
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self.process_story_file(Path(event.src_path))
```

### Story Parsing and Validation

```python
class StoryParser:
    """Parses story markdown files and extracts metadata."""
    
    def parse_story(self, story_file: Path) -> Optional[Dict]:
        """Parse a story file and return story metadata."""
        try:
            content = story_file.read_text(encoding='utf-8')
            
            story_data = {
                'file_path': str(story_file),
                'story_id': self.extract_story_id(content),
                'title': self.extract_title(content),
                'priority': self.extract_priority(content),
                'status': self.extract_status(content),
                'assigned_to': self.extract_assigned_to(content),
                'story_points': self.extract_story_points(content),
                'acceptance_criteria': self.extract_acceptance_criteria(content),
                'technical_details': self.extract_technical_details(content),
                'dependencies': self.extract_dependencies(content),
                'definition_of_done': self.extract_definition_of_done(content)
            }
            
            return story_data if self.is_story_completed(story_data) else None
            
        except Exception as e:
            logging.error(f"Error parsing story file {story_file}: {e}")
            return None
    
    def is_story_completed(self, story_data: Dict) -> bool:
        """Determine if a story is completed based on its metadata."""
        status = story_data.get('status', '').lower()
        
        # Check for completion indicators
        completion_indicators = [
            'completed',
            'implemented',
            'done',
            'finished',
            'deployed'
        ]
        
        return any(indicator in status for indicator in completion_indicators)
```

### Queue Management Integration

```python
class ValidationQueueManager:
    """Manages the validation queue for completed stories."""
    
    def add_story_to_queue(self, story_data: Dict) -> str:
        """Add a completed story to the validation queue."""
        validation_id = self.generate_validation_id(story_data['story_id'])
        
        queue_entry = {
            'id': validation_id,
            'story_id': story_data['story_id'],
            'story_file': story_data['file_path'],
            'priority': self.map_priority(story_data['priority']),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'estimated_duration_minutes': self.estimate_duration(story_data),
            'assigned_agent': None,
            'requirements': story_data['acceptance_criteria'],
            'test_plan': self.generate_test_plan(story_data)
        }
        
        # Add to pending validation queue
        pending_queue = self.load_queue('pending_validation.json')
        pending_queue['queue'].append(queue_entry)
        self.save_queue('pending_validation.json', pending_queue)
        
        logging.info(f"Added story {story_data['story_id']} to validation queue with ID {validation_id}")
        return validation_id
```

### Test Plan Generation

```python
class TestPlanGenerator:
    """Generates comprehensive test plans for completed stories."""
    
    def generate_test_plan(self, story_data: Dict) -> Dict:
        """Generate a comprehensive test plan for a story."""
        return {
            'acceptance_criteria_tests': self.generate_acceptance_tests(story_data),
            'regression_tests': self.generate_regression_tests(story_data),
            'performance_tests': self.generate_performance_tests(story_data),
            'security_tests': self.generate_security_tests(story_data),
            'integration_tests': self.generate_integration_tests(story_data),
            'edge_case_tests': self.generate_edge_case_tests(story_data)
        }
    
    def generate_acceptance_tests(self, story_data: Dict) -> List[Dict]:
        """Generate tests for acceptance criteria."""
        tests = []
        
        for criterion in story_data.get('acceptance_criteria', []):
            test = {
                'test_type': 'acceptance_criteria',
                'description': f"Verify: {criterion}",
                'priority': 'critical',
                'automated': True,
                'expected_result': 'Acceptance criterion satisfied'
            }
            tests.append(test)
        
        return tests
```

### Background Agent Integration

The system integrates with the existing background agent infrastructure:

1. **Agent Triggering**: When stories are queued, trigger appropriate QA agents
2. **Context Passing**: Provide story context and requirements to agents
3. **Load Balancing**: Distribute validation tasks across available agents
4. **Status Monitoring**: Track validation progress and completion

## Integration Points

- **File System**: Monitor `spec/` directory using watchdog library
- **Queue System**: Integrate with QA queue management (STORY_325)
- **Background Agents**: Trigger existing background agent system
- **MCP Servers**: Use agent queue and monitoring servers
- **Story Format**: Parse existing AgenticScrum story format

## Definition of Done

- [ ] File system monitoring implemented and tested
- [ ] Story parsing and completion detection working
- [ ] Automatic queue management functional
- [ ] Test plan generation implemented
- [ ] Integration with background agent system complete
- [ ] Comprehensive logging and error handling
- [ ] Performance testing shows minimal resource usage
- [ ] Documentation complete and accurate
- [ ] Code follows existing AgenticScrum coding standards
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] All files added to git and committed

## Dependencies

- STORY_325: QA Infrastructure Setup (for queue management)
- STORY_326: Enhanced QAA Agent Configuration (for agent triggering)
- Existing background agent system
- Python watchdog library for file monitoring

## Risks

- **Risk**: High CPU usage from continuous file monitoring
  - **Mitigation**: Use efficient file watching with debouncing
- **Risk**: Story parsing errors due to format variations
  - **Mitigation**: Robust parsing with error handling and validation
- **Risk**: Queue corruption from concurrent access
  - **Mitigation**: Implement file locking and atomic operations

## Testing Strategy

1. **Unit Testing**: Test individual components (parser, queue manager, etc.)
2. **Integration Testing**: Test end-to-end story completion workflow
3. **Performance Testing**: Verify minimal resource usage during monitoring
4. **Error Handling Testing**: Test with malformed stories and edge cases
5. **Concurrent Access Testing**: Test queue management under load

## Technical Debt Considerations

- Design for extensibility to support different story formats
- Implement configurable monitoring rules and thresholds
- Consider future support for multiple specification directories
- Plan for queue backup and recovery mechanisms

## Success Metrics

- Story completion detection accuracy: >95%
- Queue processing latency: <5 seconds
- System resource usage: <5% CPU, <100MB RAM
- False positive rate: <5%
- Integration with background agents: 100% success rate

---

**Implementation Notes for deva_python**:
- Use Python watchdog library for efficient file system monitoring
- Implement robust markdown parsing with error handling
- Create atomic file operations for queue management
- Add comprehensive logging for debugging and monitoring
- Design for high availability and fault tolerance
- Test with various story formats and edge cases
- Integration with existing `scripts/` directory structure