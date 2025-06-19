# MCP Servers for AgenticScrum

This directory contains Model Context Protocol (MCP) servers used by the AgenticScrum framework.

## DateTime Server

The datetime server provides time-related functionality for AgenticScrum development:

### Features
- Get current time in any timezone
- Format timestamps in various formats
- Calculate durations between timestamps  
- Calculate sprint dates for Agile development

### Usage
The server is automatically started by Claude Code when configured in `.mcp.json`.

### Implementation
- `datetime/simple_server.py` - MCP server implementation using stdio protocol
- `datetime/datetime_tools.py` - Core datetime functionality
- `datetime/server.py` - Original server implementation (for reference)

### Requirements
- Python 3.8+
- pytz
- python-dateutil
- mcp

All requirements are installed when you set up the AgenticScrum development environment.