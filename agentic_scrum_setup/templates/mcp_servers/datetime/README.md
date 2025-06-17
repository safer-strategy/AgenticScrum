# DateTime MCP Service for AgenticScrum

A comprehensive datetime service that provides timezone-aware operations, duration calculations, and sprint-specific date management for AgenticScrum AI agents.

## Overview

The DateTime MCP Service is a built-in service that requires no external API keys or dependencies. It provides consistent time handling across all AgenticScrum agents and includes specialized functions for Agile development workflows.

## Features

### Core Time Operations
- **Current Time**: Get current time in any timezone
- **Time Formatting**: Convert timestamps to various formats (ISO8601, human-readable, log format, etc.)
- **Duration Calculation**: Calculate time differences with detailed breakdowns
- **Time Arithmetic**: Add/subtract time periods (days, hours, minutes, months, years)
- **Timezone Conversion**: Convert between timezones safely

### Business & Sprint Operations  
- **Business Days**: Calculate working days excluding weekends and holidays
- **Sprint Calculations**: Agile-aware sprint start/end date calculation
- **Relative Time**: Human-readable relative timestamps ("2 hours ago", "in 3 days")
- **Time Until**: Countdown to target dates with overdue detection

### Specialized Features
- **Monday Sprint Alignment**: Automatically aligns sprint starts to Mondays
- **Weekend Gap Handling**: Proper sprint scheduling around weekends
- **Holiday Support**: Configurable holiday exclusions for business day calculations
- **Performance Optimized**: Sub-100ms response times for all operations

## Available Tools

### `get_current_time`
Get current time in specified timezone or UTC.

**Parameters:**
- `timezone` (optional): Timezone name (e.g., 'US/Eastern', 'Europe/London')

**Returns:**
```json
{
  "timestamp": "2025-01-18T15:30:45Z",
  "unix": 1737216645,
  "timezone": "UTC",
  "utc_offset": "+0000",
  "components": {
    "year": 2025,
    "month": 1,
    "day": 18,
    "hour": 15,
    "minute": 30,
    "second": 45,
    "weekday": "Saturday",
    "week_number": 3
  }
}
```

### `format_datetime`
Format datetime string in various standard formats.

**Parameters:**
- `timestamp`: ISO format timestamp or parseable date string
- `format`: Output format type
  - `ISO8601` (default): Standard ISO format
  - `RFC3339`: RFC3339 format with timezone
  - `human`: "January 18, 2025 at 3:30 PM"
  - `date`: "2025-01-18"
  - `time`: "15:30:45"
  - `log`: "2025-01-18 15:30:45"
  - `filename`: "20250118_153045"

### `calculate_duration`
Calculate duration between two timestamps.

**Parameters:**
- `start`: Start timestamp
- `end`: End timestamp

**Returns:**
```json
{
  "total_seconds": 9045,
  "total_minutes": 150,
  "total_hours": 2,
  "days": 0,
  "hours": 2,
  "minutes": 30,
  "seconds": 45,
  "human_readable": "2 hours and 30 minutes",
  "is_negative": false
}
```

### `add_time`
Add time periods to a timestamp.

**Parameters:**
- `timestamp`: Base timestamp
- `years`, `months`, `weeks`, `days`, `hours`, `minutes`, `seconds`: Time to add

**Example:**
```python
# Add 2 weeks and 3 days
result = mcp.datetime.add_time(
    timestamp="2025-01-18T10:00:00Z",
    weeks=2,
    days=3
)
# Returns: "2025-02-07T10:00:00Z"
```

### `convert_timezone`
Convert timestamp from one timezone to another.

**Parameters:**
- `timestamp`: Timestamp to convert
- `from_tz`: Source timezone
- `to_tz`: Target timezone

### `calculate_business_days`
Calculate business days between dates, excluding weekends and holidays.

**Parameters:**
- `start_date`: Start date
- `end_date`: End date  
- `holidays` (optional): Array of holiday dates to exclude

**Returns:**
```json
{
  "business_days": 10,
  "total_days": 14,
  "weekend_days": 4,
  "holiday_count": 0
}
```

### `get_relative_time`
Convert timestamp to human-readable relative time.

**Parameters:**
- `timestamp`: Timestamp to convert
- `reference` (optional): Reference time (defaults to current time)

**Examples:**
- "just now"
- "5 minutes ago"  
- "2 hours ago"
- "3 days ago"
- "in 2 hours"
- "in 5 days"

### `calculate_sprint_dates`
Calculate Agile sprint start/end dates with proper business day alignment.

**Parameters:**
- `start_date`: Proposed start date
- `sprint_length_days`: Sprint length (default: 14 days)

**Returns:**
```json
{
  "sprint_start": "2025-01-20",
  "sprint_end": "2025-02-02", 
  "next_sprint_start": "2025-02-05",
  "sprint_length": 14,
  "working_days": 10
}
```

**Features:**
- Automatically moves sprint start to Monday if needed
- Ensures proper weekend gap between sprints
- Calculates actual working days in sprint

### `get_time_until`
Calculate time remaining until a target timestamp.

**Parameters:**
- `target_timestamp`: Target time to count down to
- `reference` (optional): Reference time (defaults to current time)

**Returns:**
```json
{
  "is_past": false,
  "total_seconds": 7200,
  "days": 0,
  "hours": 2,
  "minutes": 0,
  "human_readable": "2 hours"
}
```

## Agent Usage Patterns

### Product Owner Agent (POA)
```python
# Track user story creation
current_time = mcp.datetime.get_current_time()
story["created_at"] = current_time["timestamp"]

# Sprint planning
sprint_dates = mcp.datetime.calculate_sprint_dates(
    start_date="2025-01-20",
    sprint_length_days=14
)

# Stakeholder feedback tracking
feedback_age = mcp.datetime.calculate_duration(
    start=last_feedback_time,
    end=mcp.datetime.get_current_time()["timestamp"]
)
```

### Scrum Master Agent (SMA)
```python
# Track ceremony timing
standup_duration = mcp.datetime.calculate_duration(
    start=standup_start,
    end=standup_end
)

# Sprint progress monitoring
sprint_progress = mcp.datetime.calculate_duration(
    start=sprint_start,
    end=mcp.datetime.get_current_time()["timestamp"]
)
completion_percentage = (sprint_progress["days"] / 14) * 100

# Impediment aging
impediment_age = mcp.datetime.get_relative_time(
    timestamp=impediment_created_time
)
```

### Quality Assurance Agent (QAA)
```python
# Test execution tracking
test_start = mcp.datetime.get_current_time()["timestamp"]
run_tests()
test_duration = mcp.datetime.calculate_duration(
    start=test_start,
    end=mcp.datetime.get_current_time()["timestamp"]
)

# Bug age monitoring
bug_age = mcp.datetime.get_relative_time(
    timestamp=bug_reported_time
)

# Review deadline setting
review_deadline = mcp.datetime.add_time(
    timestamp=mcp.datetime.get_current_time()["timestamp"],
    hours=48  # 48-hour review SLA
)
```

### Security Audit Agent (SAA)
```python
# Vulnerability remediation tracking
vuln_age = mcp.datetime.calculate_duration(
    start=vulnerability_discovered_time,
    end=mcp.datetime.get_current_time()["timestamp"]
)

# Certificate expiration monitoring
cert_expiry_time = mcp.datetime.get_time_until(
    target_timestamp=certificate_expiry_date
)

# Security review scheduling
next_review = mcp.datetime.add_time(
    timestamp=mcp.datetime.get_current_time()["timestamp"],
    months=3  # Quarterly reviews
)
```

## Installation & Setup

The DateTime MCP service is automatically included in all AgenticScrum projects with MCP enabled. No manual installation or API key configuration is required.

### Requirements
- Python 3.8+
- pytz>=2024.1
- python-dateutil>=2.8.2
- mcp>=0.1.0

### Configuration

The service is automatically configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "datetime": {
      "command": "python",
      "args": ["mcp_servers/datetime/server.py"],
      "description": "Built-in datetime service for time operations"
    }
  }
}
```

## Error Handling

All datetime operations include comprehensive error handling:

- Invalid timezones return error messages with suggestions
- Malformed timestamps are caught and reported clearly
- Timezone conversion errors include source/target timezone info
- Duration calculations handle negative values appropriately

## Performance

- **Tool Invocation**: < 50ms average response time
- **Complex Calculations**: < 100ms for sprint date calculations
- **Memory Usage**: < 50MB total service footprint
- **Startup Time**: < 2 seconds server initialization

## Security

- **No External APIs**: Completely self-contained service
- **No Credentials**: No API keys or secrets required
- **Read-Only Operations**: Only reads system time, no file system access
- **Timezone Data**: Bundled with pytz library, no external downloads

## Troubleshooting

### Service Won't Start
1. Check Python version (3.8+ required)
2. Verify dependencies: `pip install -r mcp_servers/datetime/requirements.txt`
3. Check file permissions on `server.py`

### Timezone Errors
1. Use standard timezone names: `US/Eastern`, `Europe/London`, `UTC`
2. Check pytz documentation for valid timezone names
3. Use `UTC` as fallback for unknown timezones

### Performance Issues
1. Check if multiple datetime servers are running
2. Verify system time synchronization
3. Monitor memory usage during heavy calculations

## Testing

Run the test suite:

```bash
# From project root
python -m pytest agentic_scrum_setup/tests/test_datetime_tools.py -v

# Or from test directory
cd agentic_scrum_setup/tests
python test_datetime_tools.py
```

Test coverage includes:
- All core datetime operations
- Error handling scenarios
- Timezone conversion edge cases
- Sprint calculation workflows
- Business day calculations
- Integration testing scenarios

## Contributing

To extend the DateTime MCP service:

1. Add new methods to `DateTimeTools` class
2. Register tools in `DateTimeMCPServer._register_tools()`
3. Add test cases in `test_datetime_tools.py`
4. Update agent persona patterns as needed
5. Update this documentation

## License

Part of the AgenticScrum framework. See main project license.