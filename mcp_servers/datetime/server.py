#!/usr/bin/env python3
"""DateTime MCP Server for AgenticScrum."""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from datetime_tools import DateTimeTools

try:
    from mcp.server import MCPServer
    from mcp.types import Tool, ToolResult
except ImportError:
    # Fallback for environments without MCP
    print("MCP library not available. Please install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


class DateTimeMCPServer(MCPServer):
    """MCP server providing datetime functionality for AgenticScrum."""
    
    def __init__(self):
        super().__init__("datetime-mcp")
        self.dt_tools = DateTimeTools()
        self._register_tools()
    
    def _register_tools(self):
        """Register all datetime tools with the MCP server."""
        
        # Current time tool
        self.register_tool(Tool(
            name="get_current_time",
            description="Get current time in specified timezone (or UTC if not specified)",
            input_schema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone name (e.g., 'US/Eastern', 'Europe/London', 'UTC')",
                        "default": "UTC"
                    }
                }
            }
        ))
        
        # Format datetime tool
        self.register_tool(Tool(
            name="format_datetime",
            description="Format datetime string in various standard formats",
            input_schema={
                "type": "object",
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "description": "ISO format timestamp or parseable date string"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["ISO8601", "RFC3339", "human", "date", "time", "date_human", "time_human", "short", "log", "filename"],
                        "description": "Output format type",
                        "default": "ISO8601"
                    }
                },
                "required": ["timestamp"]
            }
        ))
        
        # Duration calculation tool
        self.register_tool(Tool(
            name="calculate_duration",
            description="Calculate duration between two timestamps",
            input_schema={
                "type": "object",
                "properties": {
                    "start": {
                        "type": "string",
                        "description": "Start timestamp (ISO format or parseable)"
                    },
                    "end": {
                        "type": "string",
                        "description": "End timestamp (ISO format or parseable)"
                    }
                },
                "required": ["start", "end"]
            }
        ))
        
        # Add time tool
        self.register_tool(Tool(
            name="add_time",
            description="Add time periods to a timestamp",
            input_schema={
                "type": "object",
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "description": "Base timestamp (ISO format or parseable)"
                    },
                    "years": {"type": "integer", "description": "Years to add"},
                    "months": {"type": "integer", "description": "Months to add"},
                    "weeks": {"type": "integer", "description": "Weeks to add"},
                    "days": {"type": "integer", "description": "Days to add"},
                    "hours": {"type": "integer", "description": "Hours to add"},
                    "minutes": {"type": "integer", "description": "Minutes to add"},
                    "seconds": {"type": "integer", "description": "Seconds to add"}
                },
                "required": ["timestamp"]
            }
        ))
        
        # Timezone conversion tool
        self.register_tool(Tool(
            name="convert_timezone",
            description="Convert timestamp from one timezone to another",
            input_schema={
                "type": "object",
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "description": "Timestamp to convert"
                    },
                    "from_tz": {
                        "type": "string",
                        "description": "Source timezone (e.g., 'US/Eastern')"
                    },
                    "to_tz": {
                        "type": "string",
                        "description": "Target timezone (e.g., 'UTC')"
                    }
                },
                "required": ["timestamp", "from_tz", "to_tz"]
            }
        ))
        
        # Business days calculation tool
        self.register_tool(Tool(
            name="calculate_business_days",
            description="Calculate business days between dates, excluding weekends and holidays",
            input_schema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (ISO format or parseable)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (ISO format or parseable)"
                    },
                    "holidays": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of holiday dates to exclude (ISO format)",
                        "default": []
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ))
        
        # Relative time tool
        self.register_tool(Tool(
            name="get_relative_time",
            description="Convert timestamp to human-readable relative time (e.g., '2 hours ago')",
            input_schema={
                "type": "object",
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "description": "Timestamp to convert to relative time"
                    },
                    "reference": {
                        "type": "string",
                        "description": "Reference time (defaults to current time)",
                        "default": None
                    }
                },
                "required": ["timestamp"]
            }
        ))
        
        # Sprint dates calculation tool
        self.register_tool(Tool(
            name="calculate_sprint_dates",
            description="Calculate Agile sprint start/end dates with proper business day alignment",
            input_schema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Proposed start date (will be adjusted to Monday)"
                    },
                    "sprint_length_days": {
                        "type": "integer",
                        "description": "Sprint length in days",
                        "default": 14,
                        "minimum": 1,
                        "maximum": 30
                    }
                },
                "required": ["start_date"]
            }
        ))
        
        # Time until tool
        self.register_tool(Tool(
            name="get_time_until",
            description="Calculate time remaining until a target timestamp",
            input_schema={
                "type": "object",
                "properties": {
                    "target_timestamp": {
                        "type": "string",
                        "description": "Target timestamp to count down to"
                    },
                    "reference": {
                        "type": "string",
                        "description": "Reference time (defaults to current time)",
                        "default": None
                    }
                },
                "required": ["target_timestamp"]
            }
        ))
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Handle tool calls from Claude."""
        try:
            if name == "get_current_time":
                result = self.dt_tools.get_current_time(arguments.get("timezone"))
            
            elif name == "format_datetime":
                result = self.dt_tools.format_datetime(
                    arguments["timestamp"],
                    arguments.get("format", "ISO8601")
                )
            
            elif name == "calculate_duration":
                result = self.dt_tools.calculate_duration(
                    arguments["start"],
                    arguments["end"]
                )
            
            elif name == "add_time":
                timestamp = arguments.pop("timestamp")
                result = self.dt_tools.add_time(timestamp, **arguments)
            
            elif name == "convert_timezone":
                result = self.dt_tools.convert_timezone(
                    arguments["timestamp"],
                    arguments["from_tz"],
                    arguments["to_tz"]
                )
            
            elif name == "calculate_business_days":
                result = self.dt_tools.calculate_business_days(
                    arguments["start_date"],
                    arguments["end_date"],
                    arguments.get("holidays", [])
                )
            
            elif name == "get_relative_time":
                result = self.dt_tools.get_relative_time(
                    arguments["timestamp"],
                    arguments.get("reference")
                )
            
            elif name == "calculate_sprint_dates":
                result = self.dt_tools.calculate_sprint_dates(
                    arguments["start_date"],
                    arguments.get("sprint_length_days", 14)
                )
            
            elif name == "get_time_until":
                result = self.dt_tools.get_time_until(
                    arguments["target_timestamp"],
                    arguments.get("reference")
                )
            
            else:
                return ToolResult(
                    error=f"Unknown tool: {name}",
                    result=None
                )
            
            return ToolResult(result=result)
            
        except Exception as e:
            return ToolResult(
                error=f"Error in {name}: {str(e)}",
                result=None
            )


async def main():
    """Main entry point for the DateTime MCP server."""
    server = DateTimeMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())